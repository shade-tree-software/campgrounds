#!/usr/bin/env python3
"""Stitch Esri World Imagery around a federal campground and plot its real pads.

    python3 audit/sat_look.py <facility_id> [-z 17] [-o out.png]
    python3 audit/sat_look.py --at <lat> <lng> [-z 17] [-o out.png]

The waterfront gate makes a satellite look mandatory but gives it asymmetric
authority: legible imagery is decisive and overrides prose, while imagery
blinded by canopy can neither confirm nor deny, and "I couldn't see pads" is
explicitly NOT grounds to downgrade. Most federal campgrounds in the gap list
are exactly the blind case — Cowhide Cove on Lake Greeson is a wooded
peninsula where not one of its 47 pads resolves.

What breaks the deadlock is that RIDB's per-campsite catalog carries each
site's OWN coordinate. Those are the higher-authority per-site data the gate
already says to defer to when the canopy wins, so plotting them on the tile
turns an unreadable picture into a measurable one: the pads are where the dots
are, whether or not the trees let you see them.

Reading it, in the vocabulary of the gate:
  - a dot within ~a site-depth of the waterline, with open ground between,
    is the on-water case;
  - dots ranked behind a continuous treeline, a road, or a day-use strip are
    the buffer case, however close they measure;
  - dots plainly set back across open ground are `*view`.
The scale bar prints metres per pixel so the ~50 m distance bound is measured
rather than guessed. A dot is a pad, not a verdict — the buffer still has to
be read off the image.
"""

import argparse
import io
import json
import math
import os
import sys
import urllib.request

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TILE = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}")
CACHE_JSON = os.path.join("trip_data", "ridb_gap_cache.json")


def deg2num(lat, lon, z):
    n = 2.0 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def stitch(lat, lng, z, span):
    fx, fy = deg2num(lat, lng, z)
    x0, y0 = int(fx) - span, int(fy) - span
    n = span * 2 + 1
    im = Image.new("RGB", (256 * n, 256 * n))
    for dx in range(n):
        for dy in range(n):
            url = TILE.format(z=z, x=x0 + dx, y=y0 + dy)
            req = urllib.request.Request(
                url, headers={"User-Agent": "ekko-campground-curation/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                im.paste(Image.open(io.BytesIO(r.read())), (256 * dx, 256 * dy))
    return im, x0, y0


def to_px(lat, lng, z, x0, y0):
    fx, fy = deg2num(lat, lng, z)
    return (fx - x0) * 256, (fy - y0) * 256


def draw_scale(im, mpp):
    """A bar the distance bound can actually be measured against."""
    d = ImageDraw.Draw(im)
    for metres in (50, 100, 200, 500):
        px = metres / mpp
        if px >= 90:
            break
    x, y = 20, im.size[1] - 28
    d.rectangle([x - 6, y - 18, x + px + 60, y + 12], fill=(0, 0, 0))
    d.line([(x, y), (x + px, y)], fill=(255, 255, 255), width=4)
    d.line([(x, y - 7), (x, y + 7)], fill=(255, 255, 255), width=3)
    d.line([(x + px, y - 7), (x + px, y + 7)], fill=(255, 255, 255), width=3)
    d.text((x + px + 10, y - 7), f"{metres} m", fill=(255, 255, 255))


def render(lat, lng, sites, z, span, out):
    im, x0, y0 = stitch(lat, lng, z, span)
    d = ImageDraw.Draw(im)
    plotted = 0
    for s in sites or []:
        s_lat, s_lng = s.get("lat"), s.get("lng")
        if not isinstance(s_lat, (int, float)) or not isinstance(s_lng, (int, float)):
            continue
        if not (s_lat or s_lng):
            continue
        px, py = to_px(s_lat, s_lng, z, x0, y0)
        if not (0 <= px < im.size[0] and 0 <= py < im.size[1]):
            continue
        # Cyan reads against both water and summer canopy, which is the whole
        # range of ground this pass looks at.
        d.ellipse([px - 5, py - 5, px + 5, py + 5],
                  fill=(0, 255, 255), outline=(0, 0, 0), width=2)
        plotted += 1
    cx, cy = to_px(lat, lng, z, x0, y0)
    for a, b in ((-16, -6), (6, 16)):
        d.line([(cx + a, cy), (cx + b, cy)], fill=(255, 0, 0), width=3)
        d.line([(cx, cy + a), (cx, cy + b)], fill=(255, 0, 0), width=3)
    mpp = 156543.03392 * math.cos(math.radians(lat)) / (2 ** z)
    draw_scale(im, mpp)
    im.save(out)
    print(f"{out}  z={z}  {im.size[0]}x{im.size[1]}px  {mpp:.2f} m/px  "
          f"{im.size[0] * mpp:.0f} m across  {plotted} pads plotted")


def load_facility(fid):
    """One facility's campsites, from the triage cache or straight from RIDB.

    The cache lives under gitignored `trip_data/`, so it does NOT travel with
    a clone — and this tool is useless without per-site coordinates, which is
    the whole reason it exists. So a miss falls back to RIDB (one or two
    requests for one facility, against the ~45 minutes a full triage refetch
    costs) and writes the record back, which means a fresh machine can audit
    the next campground immediately instead of rebuilding 585 of them first.
    Needs RIDB_API_KEY only on the fallback path.
    """
    cache = {}
    try:
        with open(CACHE_JSON, encoding="utf-8") as fh:
            cache = json.load(fh)
    except (OSError, ValueError):
        pass
    if fid in cache and cache[fid].get("sites") is not None:
        return cache[fid]

    print(f"{fid} not in the triage cache — fetching from RIDB", flush=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ridb_gap_triage", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "ridb_gap_triage.py"))
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    raw = t._get_paced(f"facilities/{fid}", {"full": "true"})
    if raw is None:
        sys.exit(f"RIDB has no facility {fid}")
    sites, total = t.fetch_campsites(fid)
    rec = {"v": t.CACHE_VERSION, "facility": t.compact_facility(raw),
           "sites": [t.compact_site(s) for s in sites],
           "site_total": total, "site_coord": t.site_coords(sites)}
    cache[fid] = rec
    try:
        t.save_cache(cache)
    except OSError:
        pass
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facility_id", nargs="?")
    ap.add_argument("--at", nargs=2, type=float, metavar=("LAT", "LNG"))
    ap.add_argument("-z", type=int, default=17)
    ap.add_argument("--span", type=int, default=2, help="tiles each side of centre")
    ap.add_argument("-o", default="sat.png")
    args = ap.parse_args()

    sites = []
    if args.at:
        lat, lng = args.at
    else:
        if not args.facility_id:
            ap.error("give a facility id or --at LAT LNG")
        rec = load_facility(args.facility_id)
        sites = rec.get("sites") or []
        lat, lng = (rec.get("site_coord")
                    or [rec["facility"]["lat"], rec["facility"]["lng"]])
        print(f"{rec['facility']['name']} — {rec['facility']['recarea']} "
              f"({rec['facility']['org']}), {len(sites)} catalog sites")
    render(lat, lng, sites, args.z, args.span, args.o)


if __name__ == "__main__":
    main()
