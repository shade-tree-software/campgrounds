#!/usr/bin/env python3
"""rec.gov search-index facts for the rec.gov-linked entries recgov_rates.py could not price (2026-10-16).

    python3 -I recgov_search.py OUT.json

recgov_rates.py reads the facility's rate table; for ~100 facilities its current seasons
hold only group/shelter/tent types or nothing (FCFS 'POI-style' listings). The search
index (`/api/search?fq=entity_id:<id>`) carries `price_range` - what rec.gov's own
listing shows - plus equipment and site-use lists. Read by hand in build_recgov.py.
"""
import json, os, sys, time, urllib.request
ROOT = __file__.rsplit("/audit/", 1)[0]
sys.path.insert(0, ROOT + "/audit/price_research")
import recgov_rates as R
found = {f["id"] for f in json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/recgov_findings.json"))}
out = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
for r, fid in R.targets():
    if r["id"] in found or fid in out:
        continue
    u = f"https://www.recreation.gov/api/search?fq=entity_id%3A{fid}&size=2"
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": R.UA}), timeout=30))
    except Exception as e:
        print("ERR", fid, e); continue
    res = [x for x in d.get("results", []) if x.get("entity_id") == fid]
    keep = ("name", "price_range", "reservable", "campsite_type_of_use", "campsite_equipment_name",
            "campsite_reserve_type", "campsites_count", "campsite_max_vehicle_length", "notices", "org_name", "parent_name")
    out[fid] = {k: res[0].get(k) for k in keep} if res else None
    json.dump(out, open(sys.argv[1], "w"), indent=1)
    time.sleep(1.2)
print(len(out))
