#!/usr/bin/env python3
"""Find the rec.gov campground facility for unpriced federal entries by name + position
(2026-10-16): entries whose link is a group facility, an FS page saying "see Recreation.gov",
or an NPS page whose fee is drawn by script.

    python3 -I recgov_byname.py OUT.json

Queries /api/search with the entry's name (parenthetical dropped), keeps campground-type
results within 2 km of the entry's pin, and stores the nearest with its price_range and
site-use facts. Read by hand; per-site rates then come from recgov_sites.py.
"""
import json, math, os, re, sys, time, urllib.parse, urllib.request
ROOT = __file__.rsplit("/audit/", 1)[0]
sys.path.insert(0, ROOT)
import campground_schema as cs
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/140"}
reg = json.load(open(ROOT + "/campground_policies.json"))


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


out = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
for e in json.load(open(ROOT + "/campgrounds.json")):
    if e.get("kind") != "campground" or e.get("ownership") != "federal" or e.get("country", "US") != "US":
        continue
    if e["state"] in {"ON", "BC", "AB", "SK", "MB", "QC", "NB", "NS", "PE", "NL"}:
        continue
    v = (cs.resolve(e, reg).get("fees") or {}).get("values", {})
    if "nightly_low" in v or "nightly_high" in v or str(e["id"]) in out:
        continue
    lat, lng = map(float, e["location"].split(","))
    q = re.sub(r"\(.*?\)", " ", e["name"]).strip()
    u = "https://www.recreation.gov/api/search?" + urllib.parse.urlencode(
        {"q": q, "fq": "entity_type:campground", "size": 20, "lat": lat, "lng": lng, "radius": 25})
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
    except Exception as ex:
        print("ERR", e["id"], ex); time.sleep(2); continue
    best = None
    for x in d.get("results", []):
        try:
            dist = km(lat, lng, float(x["latitude"]), float(x["longitude"]))
        except Exception:
            continue
        if dist <= 2 and (best is None or dist < best[0]):
            best = (dist, x)
    row = {"name": e["name"], "state": e["state"], "website": e.get("website")}
    if best:
        x = best[1]
        row.update(km=round(best[0], 2), entity_id=x.get("entity_id"), rg_name=x.get("name"),
                   price_range=x.get("price_range"), reservable=x.get("reservable"),
                   use=x.get("campsite_type_of_use"), equipment=x.get("campsite_equipment_name"),
                   count=x.get("campsites_count"), org=x.get("org_name"))
    out[str(e["id"])] = row
    json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
    time.sleep(1.2)
print(len(out), sum(1 for r in out.values() if r.get("entity_id")))
