#!/usr/bin/env python3
"""Patch the ocean-looking low-zoom tiles in the USB edition's satellite store.

The satellite layer is built from USGS NAIP (USGSImageryOnly), which only has
real imagery over the US. At low zoom over NON-US areas — most visibly western
Canada, which the corridor reaches as low-zoom spillover from northern-US trips
— NAIP falls back to a Blue-Marble-style global mosaic that renders as dark
ocean-blue. On the landing page (trips_map fitBounds -> ~z3-4) that shows up as
"ocean instead of land" over Canada.

This script finds the stored tiles at low zoom whose center is OUTSIDE the US
landmass and replaces them with Esri World Imagery — real global land imagery,
the SAME source the online app already uses (server.arcgisonline.com, cached by
the service worker). US tiles are left as pristine NAIP, so only the no-coverage
areas change. Esri is globally correct for both land and water, so genuine-ocean
tiles that get swept in look identical.

Default is a DRY RUN (reports what it would do). Pass --apply to write. The
replace is INSERT OR REPLACE in place, so the original NAIP ocean tile is
overwritten — that's intended (it carried no usable land imagery).

Usage:
  python3 patch-nonus-tiles.py                       # dry run against the card
  python3 patch-nonus-tiles.py --apply               # actually patch
  python3 patch-nonus-tiles.py --mbtiles /path/satellite.mbtiles --apply
  python3 patch-nonus-tiles.py --max-zoom 7 --apply  # widen the zoom band
"""
import argparse
import io
import math
import os
import sqlite3
import sys
import threading
import time
import urllib.request
import urllib.error

ESRI_URL = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}")
HEADERS = {"User-Agent": "EKKO-Trips-offline-tile-patcher/1.0 (personal RV trip app)"}
DEFAULT_MBTILES = "/media/andrew/EKKO/app/tiles/satellite.mbtiles"

# US landmass bounding boxes (lat_min, lat_max, lng_min, lng_max). A tile whose
# CENTER falls in any of these keeps its NAIP imagery; everything else at low
# zoom is repainted from Esri. Boxes are deliberately tight to the coverage so
# the actual no-NAIP areas (Canada, Mexico, open ocean) fall outside.
US_BOXES = [
    # CONUS north edge = 49.0, the 49th-parallel border west of Lake of the
    # Woods, so southern-BC coastal tiles (Vancouver ~49.28) fall outside. A
    # bbox can't trace the border exactly; erring low just repaints a few
    # border tiles from Esri, which is correct imagery there anyway.
    (24.5, 49.0, -125.0, -66.9),    # CONUS
    (51.0, 71.6, -170.0, -129.0),   # Alaska mainland
    (18.9, 22.3, -160.3, -154.8),   # Hawaii
]


def tile2lat(y, z):
    n = math.pi - 2.0 * math.pi * y / (1 << z)
    return math.degrees(math.atan(math.sinh(n)))


def tile2lon(x, z):
    return x / (1 << z) * 360.0 - 180.0


def in_us(lat, lng):
    for la0, la1, lo0, lo1 in US_BOXES:
        if la0 <= lat <= la1 and lo0 <= lng <= lo1:
            return True
    return False


def fetch_esri(z, x, y, timeout=30):
    """Fetch one Esri World Imagery tile (XYZ y). Returns bytes or None."""
    url = ESRI_URL.format(z=z, x=x, y=y)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        return data if data and len(data) > 500 else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mbtiles", default=DEFAULT_MBTILES,
                    help=f"path to satellite.mbtiles (default {DEFAULT_MBTILES})")
    ap.add_argument("--max-zoom", type=int, default=6,
                    help="only patch tiles at zoom <= this (default 6; the "
                         "landing view sits ~z3-4 and no trips reach Canada, "
                         "so higher zooms have no non-US tiles anyway)")
    ap.add_argument("--rate", type=float, default=10.0,
                    help="max Esri requests/sec (default 10)")
    ap.add_argument("--apply", action="store_true",
                    help="actually write; without it, dry-run report only")
    a = ap.parse_args()

    if not os.path.isfile(a.mbtiles):
        sys.exit(f"not found: {a.mbtiles}\n(mount the card, or pass --mbtiles)")

    con = sqlite3.connect(a.mbtiles)
    # Stored rows are TMS: tile_row = (1<<z)-1 - y_xyz  (see build-tiles.py).
    rows = con.execute(
        "SELECT zoom_level, tile_column, tile_row FROM tiles "
        "WHERE zoom_level <= ? ORDER BY zoom_level, tile_column, tile_row",
        (a.max_zoom,)).fetchall()

    targets = []   # (z, x, tms, y_xyz, clat, clon)
    for z, x, tms in rows:
        y_xyz = (1 << z) - 1 - tms
        clat = tile2lat(y_xyz + 0.5, z)
        clon = tile2lon(x + 0.5, z)
        if not in_us(clat, clon):
            targets.append((z, x, tms, y_xyz, clat, clon))

    per_z = {}
    for z, *_ in targets:
        per_z[z] = per_z.get(z, 0) + 1
    print(f"store: {a.mbtiles}")
    print(f"low-zoom tiles scanned (z<= {a.max_zoom}): {len(rows):,}")
    print(f"non-US tiles to repaint from Esri: {len(targets):,}")
    for z in sorted(per_z):
        print(f"  z{z:<2} {per_z[z]:>6,}")
    for t in targets[:10]:
        print(f"    e.g. z{t[0]} col{t[1]} row{t[2]}  center {t[4]:.2f},{t[5]:.2f}")
    if len(targets) > 10:
        print(f"    ... and {len(targets) - 10:,} more")

    if not a.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply to patch.")
        con.close()
        return

    interval = 1.0 / a.rate if a.rate > 0 else 0
    got = fail = 0
    t0 = time.time()
    next_slot = time.time()
    for i, (z, x, tms, y_xyz, clat, clon) in enumerate(targets):
        if interval:
            wait = max(0.0, next_slot - time.time())
            next_slot = max(time.time(), next_slot) + interval
            if wait:
                time.sleep(wait)
        data = fetch_esri(z, x, y_xyz)
        if data:
            con.execute("INSERT OR REPLACE INTO tiles VALUES (?,?,?,?)",
                        (z, x, tms, sqlite3.Binary(data)))
            got += 1
        else:
            fail += 1
        if got and got % 100 == 0:
            con.commit()
        if i and i % 50 == 0:
            rate = i / (time.time() - t0)
            print(f"  {i:,}/{len(targets):,}  got {got:,} fail {fail:,}  "
                  f"{rate:.0f}/s", flush=True)
    con.commit()
    con.close()
    print(f"done: repainted {got:,}, failed {fail:,}. "
          f"Restart the app; the Canada ocean tiles should now show land.")


if __name__ == "__main__":
    main()
