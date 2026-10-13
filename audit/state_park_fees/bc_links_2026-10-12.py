"""Two BC booking links that point at another park: python3 -I bc_links_2026-10-12.py [--apply]

- Whiteswan Lake Provincial Park - Packrat Point Campground (8474) linked Swan Lake Provincial Park's map
  (resourceLocationId -2147483524, the one 8559 Swan Lake links); Whiteswan Lake is -2147483508 and its Packrat Point
  Campground map -2147483239 (camping.bcparks.ca /api/maps, read 2026-10-12).
- Summit Lake Campground (Stone Mountain Provincial Park) (8551) linked Summit Lake Provincial Park near Nakusp
  (-2147483525, 'Summit Lake - Nakusp', the one 8464 links); Stone Mountain is not on the booking site (its Summit Lake
  campground is first come, first served), so the link is removed and the park page stays."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
FIX = {
    8474: ("resourceLocationId=-2147483524&mapId=-2147483393", "resourceLocationId=-2147483508&mapId=-2147483239"),
    8551: ("\nhttps://camping.bcparks.ca/create-booking/results?resourceLocationId=-2147483525&mapId=-2147483395"
           "&bookingCategoryId=0", ""),
}
n = 0
for i, (old, new) in FIX.items():
    w = by[i].get("website") or ""
    if old not in w:
        print(i, "already fixed")
        continue
    by[i]["website"] = w.replace(old, new)
    n += 1
    print(i, by[i]["name"], "->", by[i]["website"].replace("\n", " | "))
if "--apply" in sys.argv and n:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    print("written")
