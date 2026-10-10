#!/usr/bin/env python3
"""Which reservable PA state forest campsites are missing from campgrounds.json.

    python3 audit/pa_sf_dispersed/gap.py [ra_sites.jsonl]

Matches each ReserveAmerica site to a PA entry by coordinate (<= 250 m; 1.5 km for a recreation-area campground's sites) or by
siteId appearing in the entry's website / inclusion_evidence. Prints the
unmatched sites with what the inclusion gate needs (access, max vehicle length,
category, status), and writes gap.json beside this script.
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def num(s):
    m = re.search(r"-?\d+(\.\d+)?", s or "")
    return float(m.group(0)) if m else None


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ra_sites.jsonl")
    sites = [json.loads(l) for l in open(src)]
    pa = [r for r in json.load(open(os.path.join(ROOT, "campgrounds.json")))
          if r.get("state") == "PA" and r.get("kind") == "campground"]
    ents = []
    for r in pa:
        la, lo = map(float, r["location"].split(","))
        blob = " ".join(str(r.get(k) or "") for k in ("website", "inclusion_evidence", "note", "name"))
        ents.append((r, (la, lo), blob))
    gap, matched = [], []
    for s in sites:
        la, lo = num(s.get("GIS Details Latitude")), num(s.get("GIS Details Longitude"))
        if la is None:
            la, lo = num(s.get("Facility Latitude /GPS")), num(s.get("Facility Longitude / GPS"))
        s["_ll"] = (la, lo) if la else None
        # siteId=N in a URL, "siteId N" / "siteId A, B, N" in evidence, /N/campsite-booking
        hit = next(((r["id"], "siteId") for r, ll, blob in ents
                    if re.search(rf"siteId[= ](?:\d+, )*{s['site_id']}\b|site ?{s['site_id']}\b|/{s['site_id']}/campsite",
                                 blob)),
                   None)
        if not hit and s["_ll"]:
            # A recreation-area campground (Moon Lake, Manny Gordon) is one entry for
            # all its sites, which spread farther than a roadside pad's pin error.
            rad = 1.5 if "Recreation Area" in (s.get("Site, Loop") or "") else 0.25
            d, rid = min((km(s["_ll"], ll), r["id"]) for r, ll, blob in ents)
            if d <= rad:
                hit = (rid, f"{d * 1000:.0f} m")
        (matched if hit else gap).append((s, hit))
    print(f"{len(sites)} RA sites; {len(matched)} matched to an entry; {len(gap)} not in the database")
    by_entry = {}
    for s, hit in matched:
        by_entry.setdefault(hit[0], []).append(s.get("Site, Loop", s["site_id"]))
    print("entries matching more than one site:",
          {k: v for k, v in by_entry.items() if len(v) > 1})
    rows = []
    for s, _ in gap:
        rows.append({k: s.get(k) for k in ("forest", "park_id", "site_id", "Site, Loop", "Type", "Site Access",
                                            "Max Vehicle Length", "Driveway Surface", "Looking For Category",
                                            "Status", "Type of Use")} | {"ll": s["_ll"]})
    json.dump(rows, open(os.path.join(HERE, "gap.json"), "w"), indent=1, ensure_ascii=False)
    for r in rows:
        print(f"{r['forest']:13} {r['site_id']:>6} {str(r['Site, Loop'])[:38]:38} {str(r['Type'])[:14]:14} "
              f"{str(r['Site Access'])[:10]:10} len={r['Max Vehicle Length']} {str(r['Looking For Category'])[:40]}")


if __name__ == "__main__":
    main()
