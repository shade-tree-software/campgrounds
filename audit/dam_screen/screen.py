#!/usr/bin/env python3
"""Screen lake-labelled campgrounds for the below-the-dam case (AWH 2026-10-21).

    python3 -I audit/dam_screen/screen.py [--limit N] [--ids 1,2,3]

AWH: a campground behind a dam's berm or below the lake's elevation gets no lake value, and
overhead imagery hides both. This finds the US `lakefront`/`lakeview` entries with a dam from
the National Inventory of Dams (fetch_nid.py) close enough to matter, and compares elevations on
the AWS terrain tiles (Terrarium PNGs, US 3DEP at ~10 m, hydro-flattened so a lake is one flat
value). It only FLAGS; every flag is for a person to look at.

For each entry and each dam (NID_HEIGHT >= 6 ft) within 2 km + half the dam's length (capped at
5 km):
  pool  P = the most common elevation among FLAT pixels within the dam's radius - on a
            hydro-flattened DEM the reservoir is the biggest flat surface;
  camp  C = the elevation at the pin;
  water W = the elevation of the flat water nearest the pin (within 500 m) - the water the
            campground actually sits beside.
Flags: below_pool (C < P - 3 m), other_water (W < P - 3 m: the nearest water is not the pool,
e.g. the tailwater) and downstream (the pin is on the far side of the dam from the pool's flat
pixels). `strong` = below_pool plus one of the others. An entry whose pool can't be found is
listed as `no_pool`.

Writes audit/dam_screen/flags.json (every entry screened, with its numbers) and prints a
summary. Tiles are cached in audit/dam_screen/tiles/ (gitignored). No API key, no browser.
"""
import io, json, math, os, sys, time, urllib.request
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TILES = os.path.join(HERE, "tiles")
OUT = os.path.join(HERE, "flags.json")
Z = 13
TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
CANADA = {"ON", "BC", "AB", "SK", "MB", "QC", "NB", "NS", "PE", "NL"}
LAKE_VALUES = ("lakefront", "lakeview")
MIN_DAM_FT = 6
BELOW_M = 3.0
WATER_NEAR_M = 500
MIN_WATER_PX = 40          # a flat value needs this many pixels in the window to count as water


def hav(a, b, c, d):
    p = math.radians
    x = math.sin(p(c - a) / 2) ** 2 + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(x))


def to_px(lat, lng):
    n = 2 ** Z * 256
    s = math.sin(math.radians(lat))
    return (lng + 180) / 360 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def tile(x, y):
    path = os.path.join(TILES, f"{Z}_{x}_{y}.png")
    if not os.path.exists(path):
        os.makedirs(TILES, exist_ok=True)
        for attempt in range(4):
            try:
                req = urllib.request.Request(TILE_URL.format(z=Z, x=x, y=y), headers={"User-Agent": "Mozilla/5.0"})
                data = urllib.request.urlopen(req, timeout=60).read()
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        with open(path + ".tmp", "wb") as f:
            f.write(data)
        os.replace(path + ".tmp", path)
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def window(points, radius_m):
    """Elevation mosaic covering every (lat, lng) in points padded by radius_m; returns the
    array, its top-left global pixel and the metres per pixel."""
    lat0 = points[0][0]
    mpp = 156543.03392 * math.cos(math.radians(lat0)) / 2 ** Z
    pad = radius_m / mpp
    px = [to_px(*p) for p in points]
    x0, x1 = min(p[0] for p in px) - pad, max(p[0] for p in px) + pad
    y0, y1 = min(p[1] for p in px) - pad, max(p[1] for p in px) + pad
    tx0, tx1, ty0, ty1 = int(x0 // 256), int(x1 // 256), int(y0 // 256), int(y1 // 256)
    rows = [np.hstack([tile(tx, ty) for tx in range(tx0, tx1 + 1)]) for ty in range(ty0, ty1 + 1)]
    return np.vstack(rows), (tx0 * 256, ty0 * 256), mpp


def flat_mask(e):
    """Pixels equal to a horizontal AND a vertical neighbour: a hydro-flattened water surface."""
    hd = np.abs(np.diff(e, axis=1)) < 0.02
    vd = np.abs(np.diff(e, axis=0)) < 0.02
    h = np.zeros(e.shape, bool)
    v = np.zeros(e.shape, bool)
    h[:, :-1] |= hd
    h[:, 1:] |= hd
    v[:-1, :] |= vd
    v[1:, :] |= vd
    return h & v


def screen_pair(cg_ll, dam, cache):
    dll = (dam["LATITUDE"], dam["LONGITUDE"])
    L = (dam.get("DAM_LENGTH") or 0) * 0.3048
    r = min(max(1500, L / 2 + 800), 4000)
    e, (ox, oy), mpp = window([dll, cg_ll], max(r, WATER_NEAR_M) + 100)
    flat = flat_mask(e)
    yy, xx = np.mgrid[0:e.shape[0], 0:e.shape[1]]
    dx_, dy_ = to_px(*dll)
    ddist = np.hypot(xx + ox - dx_, yy + oy - dy_) * mpp
    vals = np.round(e[flat & (ddist <= r)], 1)
    if vals.size < MIN_WATER_PX:
        return {"dam": dam.get("NAME"), "nidid": dam.get("NIDID"), "pool": None}
    cnt = Counter(vals.tolist())
    pool, pool_px = cnt.most_common(1)[0]
    cx_, cy_ = to_px(*cg_ll)
    ix, iy = int(round(cx_ - ox)), int(round(cy_ - oy))
    camp = float(e[iy, ix])
    # nearest flat water to the pin: a value common enough in the window to be a water surface
    allcnt = Counter(np.round(e[flat], 1).tolist())
    water_vals = {v for v, c in allcnt.items() if c >= MIN_WATER_PX}
    wmask = flat & np.isin(np.round(e, 1), list(water_vals))
    cdist = np.hypot(xx - ix, yy - iy) * mpp
    near = wmask & (cdist <= WATER_NEAR_M)
    if near.any():
        k = np.argmin(np.where(near, cdist, np.inf))
        water = float(np.round(e.flat[k], 1))
        water_m = float(cdist.flat[k])
        water_px = int(allcnt.get(water, 0))
    else:
        water = water_m = water_px = None
    # which side of the dam: pool pixels' centroid vs the pin, both seen from the dam
    pm = flat & (np.round(e, 1) == pool) & (ddist <= r)
    pcx, pcy = xx[pm].mean() + ox - dx_, yy[pm].mean() + oy - dy_
    vx, vy = cx_ - dx_, cy_ - dy_
    dot = (pcx * vx + pcy * vy) / (math.hypot(pcx, pcy) * math.hypot(vx, vy) + 1e-9)
    dist_dam = hav(*cg_ll, *dll)
    f = {"below_pool": bool(camp < pool - BELOW_M),
         "other_water": bool(water is not None and water < pool - BELOW_M),
         "downstream": bool(dot < -0.3 and dist_dam <= r)}
    return {"dam": dam.get("NAME"), "nidid": dam.get("NIDID"), "dam_ft": dam.get("NID_HEIGHT"),
            "river": dam.get("RIVER_OR_STREAM"), "dam_len_ft": dam.get("DAM_LENGTH"),
            "dam_m": round(dist_dam), "pool": pool, "pool_px": pool_px, "camp": round(camp, 1),
            "water": water, "water_m": None if water_m is None else round(water_m), "water_px": water_px,
            "side": round(dot, 2),
            **f, "strong": f["below_pool"] and (f["other_water"] or f["downstream"])}


def main():
    cg = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
    ents = [e for e in cg if e.get("waterfront") in LAKE_VALUES and e["state"] not in CANADA]
    if "--ids" in sys.argv:
        want = {int(i) for i in sys.argv[sys.argv.index("--ids") + 1].split(",")}
        ents = [e for e in ents if e["id"] in want] + [e for e in cg if e["id"] in want and e not in ents]
    dams = json.load(open(os.path.join(HERE, "nid_cache.json")))
    grid = defaultdict(list)
    for d in dams:
        if (d.get("NID_HEIGHT") or 0) >= MIN_DAM_FT:
            grid[(int(math.floor(d["LATITUDE"] * 10)), int(math.floor(d["LONGITUDE"] * 10)))].append(d)
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    out, done = [], 0
    for e in ents:
        la, lo = map(float, e["location"].split(","))
        near = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for d in grid[(int(math.floor(la * 10)) + i, int(math.floor(lo * 10)) + j)]:
                    L = (d.get("DAM_LENGTH") or 0) * 0.3048
                    dist = hav(la, lo, d["LATITUDE"], d["LONGITUDE"])
                    if dist <= min(2000 + L / 2, 5000):
                        near.append((dist, d))
        if not near:
            continue
        near.sort(key=lambda t: t[0])
        rows = []
        for _, d in near[:3]:
            try:
                rows.append(screen_pair((la, lo), d, None))
            except Exception as ex:
                rows.append({"dam": d.get("NAME"), "nidid": d.get("NIDID"), "error": str(ex)})
        best = max(rows, key=lambda r: (r.get("strong", False), r.get("below_pool", False),
                                        r.get("other_water", False) or r.get("downstream", False)))
        out.append({"id": e["id"], "state": e["state"], "name": e["name"], "waterfront": e["waterfront"],
                    "ownership": e.get("ownership"), "location": e["location"], "best": best, "dams": rows})
        done += 1
        if done % 50 == 0:
            print(done, "screened", flush=True)
            json.dump(out, open(OUT, "w"), indent=1)
        if limit and done >= limit:
            break
    json.dump(out, open(OUT, "w"), indent=1)
    cat = Counter()
    for r in out:
        b = r["best"]
        cat["strong" if b.get("strong") else "below_pool" if b.get("below_pool") else
            "other_water" if b.get("other_water") else "downstream" if b.get("downstream") else
            "no_pool" if b.get("pool") is None and "error" not in b else "error" if "error" in b else "clear"] += 1
    print(len(out), "entries screened:", dict(cat))


if __name__ == "__main__":
    main()
