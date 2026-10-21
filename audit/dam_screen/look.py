#!/usr/bin/env python3
"""Side-by-side review frame for one dam-screen flag: satellite | terrain.

    python3 -I audit/dam_screen/look.py <id> [--d 0.006] [--at lat,lng] [--pool M] [-o out.png]

Left: Esri World Imagery. Right: the AWS terrain tiles at z14 as a hillshade, with the flagged
dam's pool level painted blue (within 0.5 m), ground more than 3 m BELOW the pool tinted red,
and ground within 3 m of it left plain. The red cross is the entry's pin, the yellow ring the
NID dam, cyan dots recreation.gov's own campsite coordinates (RIDB, cached by audit/sat_look.py). Reading it: a pin in red ground across the dam from the blue is the below-the-dam
case; a pin beside blue at the same level is on the lake whatever the screen said.
--pool overrides the pool level (when the screen picked the wrong lake), --at the centre.
"""
import io, json, math, os, re, sys, urllib.request

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import screen  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
SIZE = 700


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    eid = int(sys.argv[1])
    flags = {r["id"]: r for r in json.load(open(os.path.join(HERE, "flags.json")))}
    cg = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
    e, r = cg[eid], flags.get(eid)
    la, lo = map(float, e["location"].split(","))
    cla, clo = map(float, arg("--at").split(",")) if arg("--at") else (la, lo)
    d = float(arg("--d", "0.006"))
    sys.path.insert(0, os.path.join(HERE))
    import tiers
    b = None
    if r:
        cands = [x for x in r["dams"] if tiers.tier(e, x)] or [r["best"]]
        b = cands[0]
    pool = float(arg("--pool")) if arg("--pool") else (b or {}).get("pool")
    dx = d / math.cos(math.radians(cla))
    bbox = (clo - dx, cla - d, clo + dx, cla + d)
    url = ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
           f"bbox={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}&bboxSR=4326&imageSR=4326&size={SIZE},{SIZE}&format=jpg&f=image")
    sat = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())).convert("RGB")
    # terrain resampled onto the same lat/lng grid
    screen.Z = 14
    e_arr, (ox, oy), mpp = screen.window([(bbox[3], bbox[0]), (bbox[1], bbox[2])], 50)
    lats = np.linspace(bbox[3], bbox[1], SIZE)
    lngs = np.linspace(bbox[0], bbox[2], SIZE)
    n = 2 ** 14 * 256
    px = ((lngs + 180) / 360 * n - ox).astype(int).clip(0, e_arr.shape[1] - 1)
    s = np.sin(np.radians(lats))
    py = ((0.5 - np.log((1 + s) / (1 - s)) / (4 * np.pi)) * n - oy).astype(int).clip(0, e_arr.shape[0] - 1)
    el = e_arr[np.ix_(py, px)]
    gy, gx = np.gradient(el)
    shade = np.clip(0.6 + (gx - gy) * 0.08, 0.15, 1.0)
    rgb = np.stack([shade * 200] * 3, -1)
    if pool is not None:
        lake = np.abs(el - pool) <= 0.5
        low = el < pool - 3
        rgb[lake] = [40, 110, 230]
        rgb[low] = rgb[low] * [1.0, 0.55, 0.55] + [60, 0, 0]
    ter = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))

    def to_xy(lat, lng):
        return (lng - bbox[0]) / (bbox[2] - bbox[0]) * SIZE, (bbox[3] - lat) / (bbox[3] - bbox[1]) * SIZE

    sites = []
    m = re.search(r"recreation\.gov/camping/campgrounds/(\d+)", e.get("website") or "")
    cache = os.path.join(ROOT, "trip_data", "ridb_gap_cache.json")
    if m and os.path.exists(cache):
        f = json.load(open(cache)).get(m.group(1)) or {}
        sites = [(s["lat"], s["lng"]) for s in f.get("sites") or [] if s.get("lat")]
    for im in (sat, ter):
        g = ImageDraw.Draw(im)
        for sl, sg in sites:
            x, y = to_xy(sl, sg)
            g.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(0, 230, 255), outline=(0, 0, 0))
        x, y = to_xy(la, lo)
        g.line((x - 12, y, x + 12, y), fill=(255, 0, 0), width=3)
        g.line((x, y - 12, x, y + 12), fill=(255, 0, 0), width=3)
        if b and b.get("dam"):
            dams = json.load(open(os.path.join(HERE, "nid_cache.json")))
            for dm in dams:
                if dm.get("NAME") == b["dam"] and abs(dm["LATITUDE"] - la) < 0.06 and abs(dm["LONGITUDE"] - lo) < 0.08:
                    x2, y2 = to_xy(dm["LATITUDE"], dm["LONGITUDE"])
                    g.ellipse((x2 - 10, y2 - 10, x2 + 10, y2 + 10), outline=(255, 220, 0), width=3)
        km = (bbox[2] - bbox[0]) * 111.32 * math.cos(math.radians(cla))
        L = 500 if km > 2 else 200 if km > 0.8 else 100
        bar = SIZE / km * L / 1000
        g.rectangle((10, SIZE - 22, 10 + bar, SIZE - 16), fill=(255, 255, 255))
        g.text((14 + bar, SIZE - 26), f"{L} m", fill=(255, 255, 255))
    out = Image.new("RGB", (SIZE * 2 + 10, SIZE + 40), (0, 0, 0))
    out.paste(sat, (0, 40))
    out.paste(ter, (SIZE + 10, 40))
    cx, cy = (min(SIZE - 1, max(0, int(v))) for v in to_xy(la, lo))
    camp = float(el[cy, cx])
    title = (f"{eid} {e['name']} [{e['waterfront']}]  pin {camp:.1f} m  pool {pool} m  "
             f"dam {b.get('dam') if b else '-'} {b.get('dam_m') if b else ''} m")
    ImageDraw.Draw(out).text((8, 12), title, fill=(255, 255, 255))
    path = arg("-o", f"dam_{eid}.png")
    out.save(path)
    print(path, "|", title)


if __name__ == "__main__":
    main()
