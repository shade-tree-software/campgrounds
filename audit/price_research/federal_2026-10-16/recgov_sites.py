#!/usr/bin/env python3
"""Per-campsite rates for the rec.gov facilities recgov_rates.py could not price (2026-10-16).

    python3 -I recgov_sites.py --fetch CACHE.json      # 1.2 s per facility
    python3 -I recgov_sites.py --show CACHE.json       # one line per facility, read by hand

`/api/search/campsites?fq=asset_id:<id>` lists every site with its `type`, `permitted_equipment`
and `rates` (seasons, each with an end_date and per-attribute per_night). A site counts when
its type is not group/cabin/shelter/equestrian/management/boat/hike and it permits an RV,
trailer or camper van, or lists no equipment at all (rec.gov's 'TENT ONLY' label is reported, not trusted: Mortimer 33
permits RVs and AWH has stayed there). Seasons ending today or later count; else the latest
year's. Prices are printed per type so a double or premium site can be told apart by hand.
"""
import json, os, re, sys, time, urllib.request
from collections import defaultdict
from datetime import date
ROOT = __file__.rsplit("/audit/", 1)[0]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/140"}
DROP = re.compile(r"GROUP|CABIN|SHELTER|EQUEST|HORSE|MANAGEMENT|BOAT|HIKE|YURT|LOOKOUT|PICNIC|DAY USE|PARKING", re.I)
RVISH = {"RV", "Trailer", "Caravan/Camper Van", "Pickup Camper", "Fifth Wheel", "Pop up"}
TODAY = date.today().isoformat()


def fetch(path, ids=None):
    here = os.path.dirname(os.path.abspath(__file__))
    search = ids or json.load(open(here + "/search.json"))
    cache = json.load(open(path)) if os.path.exists(path) else {}
    for fid in search:
        if fid in cache:
            continue
        sites, start = [], 0
        while True:
            u = f"https://www.recreation.gov/api/search/campsites?fq=asset_id%3A{fid}&size=100&start={start}"
            try:
                d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
            except Exception as e:
                print("ERR", fid, e); break
            sites += d.get("campsites") or []
            start += 100
            if start >= (d.get("total") or 0):
                break
            time.sleep(1.2)
        cache[fid] = [{"name": s.get("name"), "type": s.get("type"), "loop": s.get("loop"),
                       "equip": [e.get("equipment_name") for e in s.get("permitted_equipment") or []],
                       "rates": [{"start": r.get("start_date"), "end": r.get("end_date"),
                                  "night": sorted({(v.get("single_amount_fees") or {}).get("per_night")
                                                   for a, v in (r.get("rate_map") or {}).items()
                                                   if a in {p.get("attribute") for p in r.get("prices") or []}} - {None})}
                                 for r in s.get("rates") or []]} for s in sites]
        json.dump(cache, open(path, "w"))
        time.sleep(1.2)
    print(len(cache))


def summary(sites):
    by = defaultdict(set); n = 0; years = set()
    for s in sites:
        if DROP.search(s["type"] or ""):
            continue
        if s["equip"] and not RVISH & set(s["equip"]):   # none listed = unknown, kept
            continue
        n += 1
        cur = [r for r in s["rates"] if (r["end"] or "")[:10] >= TODAY]
        if not cur and s["rates"]:
            last = max((r["end"] or "")[:4] for r in s["rates"])
            cur = [r for r in s["rates"] if (r["end"] or "")[:4] == last]
        for r in cur:
            years.add((r["end"] or "")[:4])
            by[s["type"]].update(r["night"])
    return n, dict(by), sorted(years)


if __name__ == "__main__":
    if sys.argv[1] == "--fetch":
        fetch(sys.argv[2], sys.argv[3].split(",") if len(sys.argv) > 3 else None)   # optional id list
    else:
        cache = json.load(open(sys.argv[2]))
        search = json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/search.json"))
        for fid, sites in cache.items():
            n, by, yrs = summary(sites)
            print(fid, ((search.get(fid) or {}).get("name") or "")[:34], f"{n}/{len(sites)} rv sites",
                  yrs, {k: sorted(v) for k, v in by.items()})
