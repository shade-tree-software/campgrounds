"""Cross-checks RV Life is known to need: OSM camp/caravan sites and the RIDB
federal catalog, inside the study area, with no database entry."""
import json, os, sys, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import private_gap_list as pg  # noqa: E402
from area import inside, nearest, BOXES  # noqa: E402

db = pg.entries()
out = []

def report(src, name, lat, lng, extra):
    if not inside((lat, lng)):
        return
    ok, why = pg.held(name or "", lat, lng, db)
    if ok:
        return
    a, k = nearest((lat, lng))
    out.append({"src": src, "name": name, "lat": lat, "lng": lng, "anchor": a,
                "km": round(k, 1), "why": why, **extra})

for s, w, n, e in BOXES:
    q = f"""[out:json][timeout:120];
(nwr["tourism"~"^(camp_site|caravan_site)$"]({s},{w},{n},{e}););
out center tags;"""
    for ep in ("https://overpass-api.de/api/interpreter",
               "https://overpass.private.coffee/api/interpreter"):
        try:
            req = urllib.request.Request(ep, data=urllib.parse.urlencode({"data": q}).encode(),
                                         headers={"User-Agent": "ekko-campgrounds/1.0"})
            data = json.load(urllib.request.urlopen(req, timeout=180))
            break
        except Exception as ex:
            print("overpass", ep, ex, file=sys.stderr)
    else:
        raise SystemExit("overpass unavailable")
    for el in data["elements"]:
        t = el.get("tags", {})
        c = el.get("center") or el
        if not t.get("name") or t.get("backcountry") == "yes" or t.get("camp_site") == "basic" and t.get("access") == "private":
            continue
        report("osm", t["name"], c["lat"], c["lon"],
               {"tags": {k: t[k] for k in ("tourism", "operator", "website", "caravans",
                                           "motorhome", "tents", "fee", "access",
                                           "backcountry", "camp_site", "capacity") if k in t},
                "osm": f'{el["type"]}/{el["id"]}'})
    time.sleep(2)

key = os.environ["RIDB_API_KEY"]
for lat, lng in ((48.6, -113.8), (48.4, -114.2), (51.3, -115.8), (52.6, -117.7)):
    url = ("https://ridb.recreation.gov/api/v1/facilities?" + urllib.parse.urlencode(
        {"latitude": lat, "longitude": lng, "radius": 75, "activity": "", "limit": 50,
         "offset": 0}))
    off = 0
    while True:
        req = urllib.request.Request(url.replace("offset=0", f"offset={off}"), headers={"apikey": key})
        data = json.load(urllib.request.urlopen(req, timeout=60))
        for f in data["RECDATA"]:
            if "camp" not in (f.get("FacilityTypeDescription") or "").lower():
                continue
            report("ridb", f["FacilityName"], f["FacilityLatitude"], f["FacilityLongitude"],
                   {"ridb": f["FacilityID"], "reservable": f.get("Reservable")})
        off += 50
        if off >= data["METADATA"]["RESULTS"]["TOTAL_COUNT"]:
            break
        time.sleep(0.3)

seen, uniq = set(), []
for r in sorted(out, key=lambda r: (r["anchor"], r["km"])):
    k = (r["src"], r["name"], round(r["lat"], 3))
    if k in seen: continue
    seen.add(k); uniq.append(r)
json.dump(uniq, open(os.path.join(HERE, "osm_ridb.json"), "w"), indent=1, ensure_ascii=False)
for r in uniq:
    print(f'{r["src"]:4} {r["anchor"][:14]:14} {r["km"]:5} | {r["name"][:45]:45} | {json.dumps(r.get("tags") or r.get("ridb"))[:150]}')
print(len(uniq))
