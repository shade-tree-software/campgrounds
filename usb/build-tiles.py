#!/usr/bin/env python3
"""Build the offline map-tile store for the EKKO USB standalone edition.

Computes the TRIP CORRIDOR — trip GPS tracks + trip-visited stays/events + home,
buffered by +/-1 tile, enumerated z0..16 — and fetches USGS/USDA NAIP public-domain
satellite tiles into <tiles>/satellite.mbtiles. Low zooms are inherently broad
(few tiles blanket the region); high zooms stay tight to the actual routes.

Resumable + incremental: tiles already in the MBTiles are skipped, so a killed run
just re-run continues. Satellite is public-domain NAIP (legal to fetch a corridor);
the street layer is built separately (vector .pmtiles, see build-street.sh).

Usage:
  python3 build-tiles.py --repo <app_dir> --out <tiles_dir> [--dry-run] [--max-zoom 16]
  python3 build-tiles.py --dry-run          # report the corridor tile count, fetch nothing

See usb/TILE-PIPELINE-DESIGN.md.
"""
import argparse
import concurrent.futures
import glob
import gzip
import json
import math
import os
import sqlite3
import sys
import threading
import time
import urllib.request
import urllib.error

NAIP_URL = ("https://basemap.nationalmap.gov/arcgis/rest/services/"
            "USGSImageryOnly/MapServer/tile/{z}/{y}/{x}")
HEADERS = {"User-Agent": "EKKO-Trips-offline-tile-builder/1.0 (personal RV trip app)"}


def deg2tile(lat, lng, z):
    n = 1 << z
    x = int((lng + 180.0) / 360.0 * n)
    lat_r = math.radians(max(-85.05, min(85.05, lat)))
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return min(max(x, 0), n - 1), min(max(y, 0), n - 1)


def corridor_points(repo):
    """All (lat,lng) the offline maps must cover: trip tracks + trip-visited
    stays/events + home. NOT the whole campground DB (that would cover the
    continent)."""
    pts = []

    def add(lat, lng):
        try:
            lat = float(lat); lng = float(lng)
            if -90 < lat < 90 and -180 < lng < 180:
                pts.append((lat, lng))
        except (TypeError, ValueError):
            pass

    # 1. trip GPS tracks (dense — trace every route)
    for f in glob.glob(os.path.join(repo, "trip_data/track_cache/*.json*")):
        try:
            raw = gzip.open(f).read() if f.endswith(".gz") else open(f, "rb").read()
            d = json.loads(raw)
            arr = d if isinstance(d, list) else d.get("points", [])
            for p in arr:
                add(p.get("lat"), p.get("lon", p.get("lng")))
        except Exception:
            pass

    # 2. trip-visited stays/events (covers trips lacking a GPS track)
    # Both location files: family entries live in the gitignored
    # trip_data/family.json, and an event's `family_id` resolves through this
    # same map — skipping it would leave relatives' towns off the offline map.
    cg = {}
    for loc_file in ("campgrounds.json", "trip_data/family.json"):
        try:
            for e in json.load(open(os.path.join(repo, loc_file))):
                loc = e.get("driveway_location") or e.get("location")
                if loc and "," in loc:
                    a, b = loc.split(","); cg[e["id"]] = (a, b)
        except Exception:
            pass
    try:
        trips = json.load(open(os.path.join(repo, "trip_data/trips.json")))
    except Exception:
        trips = []
    for t in trips:
        for s in t.get("stays", []):
            if s.get("campsite_location") and "," in s["campsite_location"]:
                a, b = s["campsite_location"].split(","); add(a, b)
            elif s.get("campground_id") in cg:
                add(*cg[s["campground_id"]])
        for ev in t.get("events", []):
            if ev.get("location") and "," in ev["location"]:
                a, b = ev["location"].split(","); add(a, b)
            elif ev.get("family_id") in cg:
                add(*cg[ev["family_id"]])

    # 3. home
    try:
        h = json.load(open(os.path.join(repo, "home.json")))
        add(h.get("home_lat"), h.get("home_long"))
    except Exception:
        pass

    return pts


def corridor_tiles(pts, min_z, max_z, buffer_tiles):
    """Set of (z,x,y) covering the corridor, +/-buffer at each zoom."""
    tiles = set()
    for z in range(min_z, max_z + 1):
        n = 1 << z
        seen = set()
        for lat, lng in pts:
            seen.add(deg2tile(lat, lng, z))
        for (x, y) in seen:
            for dx in range(-buffer_tiles, buffer_tiles + 1):
                for dy in range(-buffer_tiles, buffer_tiles + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < n:
                        tiles.add((z, nx, ny))
    return tiles


def tile2lon(x, z):
    return x / (1 << z) * 360.0 - 180.0


def tile2lat(y, z):
    n = math.pi - 2.0 * math.pi * y / (1 << z)
    return math.degrees(math.atan(math.sinh(n)))


def emit_poly(pts, path, z, buffer_tiles):
    """Write an Osmosis .poly corridor polygon for osmconvert clipping. The
    corridor tiles at zoom z are dissolved into per-row run rectangles to keep
    the polygon-section count low (osmconvert slows on thousands of sections)."""
    rows = {}   # y -> set of x
    n = 1 << z
    for lat, lng in pts:
        x, y = deg2tile(lat, lng, z)
        for dx in range(-buffer_tiles, buffer_tiles + 1):
            for dy in range(-buffer_tiles, buffer_tiles + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n:
                    rows.setdefault(ny, set()).add(nx)
    rects = []
    for y, xs in rows.items():
        xs = sorted(xs)
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is None or x != prev + 1:
                rects.append((start, prev, y))   # inclusive x run at row y
                start = x
            prev = x
    with open(path, "w") as f:
        f.write("corridor\n")
        for i, (xs, xe, y) in enumerate(rects):
            west, east = tile2lon(xs, z), tile2lon(xe + 1, z)
            north, south = tile2lat(y, z), tile2lat(y + 1, z)
            f.write(f"section{i}\n")
            for lon, lat in [(west, south), (east, south), (east, north),
                             (west, north), (west, south)]:
                f.write(f"   {lon:.6f}   {lat:.6f}\n")
            f.write("END\n")
        f.write("END\n")
    return len(rects)


def open_mbtiles(path, layer_name, fmt):
    new = not os.path.isfile(path)
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("CREATE TABLE IF NOT EXISTS tiles "
                "(zoom_level INT, tile_column INT, tile_row INT, tile_data BLOB)")
    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS tile_idx "
                "ON tiles (zoom_level, tile_column, tile_row)")
    con.execute("CREATE TABLE IF NOT EXISTS metadata (name TEXT, value TEXT)")
    if new:
        for k, v in [("name", layer_name), ("type", "baselayer"),
                     ("version", "1.0"), ("format", fmt)]:
            con.execute("INSERT INTO metadata VALUES (?,?)", (k, v))
    con.commit()
    return con


def have_tile(con, z, x, y_tms):
    return con.execute("SELECT 1 FROM tiles WHERE zoom_level=? AND tile_column=? "
                       "AND tile_row=?", (z, x, y_tms)).fetchone() is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ),
                    help="app dir containing trip_data/, campgrounds.json, home.json")
    ap.add_argument("--out", default=None, help="tiles output dir (default <repo>/tiles)")
    ap.add_argument("--min-zoom", type=int, default=0)
    ap.add_argument("--max-zoom", type=int, default=16)
    ap.add_argument("--buffer", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true", help="report the corridor tile count, fetch nothing")
    ap.add_argument("--emit-poly", default=None, help="write an Osmosis .poly corridor to this path and exit (for osmconvert street clipping)")
    ap.add_argument("--poly-zoom", type=int, default=10, help="tile zoom for the .poly corridor (coarser = wider street context)")
    ap.add_argument("--rate", type=float, default=20.0, help="max NAIP requests/sec (a real ceiling, shared across workers)")
    ap.add_argument("--workers", type=int, default=8, help="parallel fetch threads (overlaps NAIP's ~0.3s latency so --rate is actually reached)")
    ap.add_argument("--no-repaint-nonus", action="store_true", help="skip the post-build Esri repaint of low-zoom non-US tiles (NAIP serves an ocean-blue global mosaic outside the US; the repaint fixes the western-Canada 'ocean instead of land' artifact — see usb/patch-nonus-tiles.py)")
    a = ap.parse_args()

    repo = os.path.abspath(a.repo)
    out = a.out or os.path.join(repo, "tiles")
    pts = corridor_points(repo)
    print(f"corridor points: {len(pts):,}")
    if a.emit_poly:
        nrect = emit_poly(pts, a.emit_poly, a.poly_zoom, a.buffer)
        print(f"wrote {a.emit_poly}: {nrect:,} polygon sections (z{a.poly_zoom} corridor)")
        return
    tiles = corridor_tiles(pts, a.min_zoom, a.max_zoom, a.buffer)
    per_z = {}
    for (z, _, _) in tiles:
        per_z[z] = per_z.get(z, 0) + 1
    print(f"corridor tiles z{a.min_zoom}-{a.max_zoom} (+/-{a.buffer}): {len(tiles):,}")
    for z in sorted(per_z):
        print(f"  z{z:<2} {per_z[z]:>8,}")
    est_gb = len(tiles) * 20_000 / 1e9
    print(f"est. size @ ~20 KB/tile: ~{est_gb:.1f} GB")
    if a.dry_run:
        print("dry-run: nothing fetched.")
        return

    os.makedirs(out, exist_ok=True)
    con = open_mbtiles(os.path.join(out, "satellite.mbtiles"), "EKKO NAIP satellite", "jpg")
    ordered = sorted(tiles)  # low zoom first
    todo = [(z, x, y) for (z, x, y) in ordered if not have_tile(con, z, x, (1 << z) - 1 - y)]
    print(f"to fetch: {len(todo):,} (skipping {len(tiles) - len(todo):,} already present)")

    # Fetch on a small thread pool. Serially, throughput is bound by NAIP's
    # ~0.3 s round-trip, not by --rate: a 20/s cap actually delivered ~3/s
    # (17 h for the corridor). Workers overlap that latency; the shared rate
    # limiter below still enforces --rate as a real ceiling, so this is faster
    # without being less polite. sqlite writes stay on the main thread (the
    # connection isn't shared), workers only do HTTP.
    interval = 1.0 / a.rate if a.rate > 0 else 0
    got = fail = 0
    t0 = time.time()
    rate_lock = threading.Lock()
    next_slot = [time.time()]

    def fetch(tile):
        z, x, y = tile
        if interval:                       # global rate ceiling, shared by all workers
            with rate_lock:
                now = time.time()
                wait = max(0.0, next_slot[0] - now)
                next_slot[0] = max(now, next_slot[0]) + interval
            if wait:
                time.sleep(wait)
        url = NAIP_URL.format(z=z, x=x, y=y)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return tile, r.read()
        except Exception:
            return tile, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        for i, ((z, x, y), data) in enumerate(pool.map(fetch, todo)):
            if data and len(data) > 500:   # skip empty/placeholder responses
                con.execute("INSERT OR REPLACE INTO tiles VALUES (?,?,?,?)",
                            (z, x, (1 << z) - 1 - y, sqlite3.Binary(data)))
                got += 1
            else:
                fail += 1
            if got % 500 == 0 and got:
                con.commit()
            if i % 1000 == 0 and i:
                rate = i / (time.time() - t0)
                eta = (len(todo) - i) / rate / 60 if rate else 0
                print(f"  {i:,}/{len(todo):,}  got {got:,} fail {fail:,}  "
                      f"{rate:.0f}/s  ETA {eta:.0f} min", flush=True)
    con.commit()

    # Repaint the low-zoom non-US tiles from Esri. NAIP has no imagery outside
    # the US and serves an ocean-blue global mosaic there, so corridor tiles
    # that spill across the border (western Canada, from northern-US trips)
    # render as "ocean instead of land" at the fitBounds landing zoom. This
    # runs on every build so a rebuilt store stays corrected. Best-effort:
    # needs Esri reachable, so it's skipped/soft-failed on a NAIP-only run.
    if not a.no_repaint_nonus and got:
        import importlib.util
        _p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "patch-nonus-tiles.py")  # hyphenated, load by path
        _spec = importlib.util.spec_from_file_location("patch_nonus_tiles", _p)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        repaint_nonus_tiles = _mod.repaint_nonus_tiles
        print("repainting low-zoom non-US tiles from Esri (fixes the "
              "western-Canada ocean artifact)...")
        try:
            n, rgot, rfail = repaint_nonus_tiles(con, apply=True, verbose=True)
            print(f"  repaint: {rgot:,}/{n:,} tiles from Esri "
                  f"({rfail:,} failed)")
        except Exception as e:
            print(f"  repaint skipped ({e}); run usb/patch-nonus-tiles.py "
                  f"later if the Canada tiles show ocean")

    con.close()
    print(f"done: fetched {got:,}, failed/empty {fail:,}. satellite.mbtiles in {out}")


if __name__ == "__main__":
    main()
