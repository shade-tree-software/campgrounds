#!/usr/bin/env python3
"""Which rec.gov-linked entries fit nothing longer than ~23 ft, per RIDB's campsite catalog.

    python3 -I audit/trailer_length_2026-10-20/ridb_scan.py [--all]

Free: reads only trip_data/ridb_campsites.json (built by recgov_hookups.py --fetch).
Uses recgov_hookups.rv_sites for "a site an RV family could book" (host sites, tent-only
equipment lists, group and walk-to sites out). A site's length is its Max Vehicle Length,
else its Driveway Length; a site with neither, or a value under 10 (placeholders), is
unknown and can never make a campground fail. A candidate is a facility with at least
MIN_CATALOG_SITES RV sites, every one of them with a known length, all under 23 ft.
"""
import json, os, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from recgov_hookups import rv_sites, load_cache, MIN_CATALOG_SITES
from recgov_calendar import facility_ids

FIT_FT = 23


def site_len(s):
    a = s.get("attrs") or {}
    for k in ("Max Vehicle Length", "Driveway Length"):
        try:
            v = float(a.get(k) or "")
        except ValueError:
            continue
        if v >= 10:
            return v
    return None


def scan(rows, cache):
    links = facility_ids(rows)
    by = {r["id"]: r for r in rows}
    out = []
    for cid, fid in links.items():
        rec = cache.get(fid)
        if not rec:
            continue
        rv = rv_sites(rec["sites"])
        lens = [site_len(s) for s in rv]
        known = [l for l in lens if l is not None]
        out.append({"id": cid, "fid": fid, "entry": by[cid], "rv": len(rv), "known": len(known),
                    "max": max(known) if known else None,
                    "fits": sum(1 for l in known if l >= FIT_FT)})
    return out


if __name__ == "__main__":
    rows = json.load(open("campgrounds.json", encoding="utf-8"))
    res = scan(rows, load_cache())
    c = Counter()
    for r in res:
        if r["rv"] < MIN_CATALOG_SITES:
            c["under 3 RV sites"] += 1
        elif r["known"] < r["rv"]:
            c["some site length unknown"] += 1 if r["fits"] == 0 else 0
            c["fits (some known >= 23)"] += 1 if r["fits"] else 0
        elif r["fits"]:
            c["fits"] += 1
        else:
            c["CANDIDATE: every site < 23 ft"] += 1
    print(len(res), "linked + fetched"); [print(f"  {v:5} {k}") for k, v in c.most_common()]
    for r in sorted(res, key=lambda r: (r["entry"]["state"], r["id"])):
        cand = r["rv"] >= MIN_CATALOG_SITES and r["known"] == r["rv"] and not r["fits"]
        near = r["rv"] >= 1 and r["fits"] == 0 and r["known"] > 0
        if cand or ("--all" in sys.argv and near):
            e = r["entry"]
            print(f"{'*' if cand else ' '} {r['id']:5} {e['state']} {e['ownership']:8} rv={r['rv']:3} known={r['known']:3} max={r['max']} fid={r['fid']} {e['name']}")
