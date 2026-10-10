#!/usr/bin/env python3
"""Esri World Imagery around a candidate's sites, each site a numbered red dot.

    python3 audit/pa_sf_dispersed/sat.py <first_site_id> OUT.jpg [half_width_m=150]

Frames the candidate's sites (the bbox of all of them, at least 2*half_width
across) so the waterfront call reads every pad against the stream, not just
the pin. A scale bar in the corner gives metres.
"""
import io, json, math, os, sys, time, urllib.request

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 900


def merc(lat, lng):
    return lng * 20037508.34 / 180, math.log(math.tan(math.radians(90 + lat) / 2)) * 6378137


def main():
    sid, out = sys.argv[1], sys.argv[2]
    hw = float(sys.argv[3]) if len(sys.argv) > 3 else 150
    c = next(c for c in json.load(open(os.path.join(HERE, "candidates.json"))) if c["site_ids"][0] == sid)
    lls = c["site_lls"]
    clat = (min(l[0] for l in lls) + max(l[0] for l in lls)) / 2
    clng = (min(l[1] for l in lls) + max(l[1] for l in lls)) / 2
    k = math.cos(math.radians(clat))
    span = max(hw, max(abs(l[0] - clat) * 110540 for l in lls) + 60,
               max(abs(l[1] - clng) * 111320 * k for l in lls) + 60)
    # Web Mercator box, square in ground metres (mercator metres = ground / cos(lat)),
    # so the export keeps exactly this extent and the dots land where they should.
    cx, cy = merc(clat, clng)
    h = span / k
    u = ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
         f"bbox={cx - h},{cy - h},{cx + h},{cy + h}&bboxSR=3857&imageSR=3857"
         f"&size={SIZE},{SIZE}&format=jpg&f=image")
    for attempt in range(5):
        try:
            data = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}),
                                          timeout=60).read()
            break
        except Exception:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    im = Image.open(io.BytesIO(data)).convert("RGB")
    d = ImageDraw.Draw(im)
    for i, (la, lo) in enumerate(lls):
        px, py = merc(la, lo)
        x = (px - (cx - h)) / (2 * h) * SIZE
        y = ((cy + h) - py) / (2 * h) * SIZE
        d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(255, 0, 0), width=3)
        d.text((x + 9, y - 6), c["labels"][i][:12], fill=(255, 255, 0))
    mpp = 2 * span / SIZE
    bar = 50 / mpp
    d.rectangle((20, SIZE - 30, 20 + bar, SIZE - 24), fill=(255, 255, 255))
    d.text((20, SIZE - 45), f"50 m  ({mpp:.2f} m/px)", fill=(255, 255, 255))
    im.save(out)
    print(out, c["name"], f"water {c.get('water_m')} m {c.get('water')}")


if __name__ == "__main__":
    main()
