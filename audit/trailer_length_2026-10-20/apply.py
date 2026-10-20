#!/usr/bin/env python3
"""DB-wide trailer-length pass, first half: entries whose every RV site is rated under 23 ft.

    python3 -I audit/trailer_length_2026-10-20/apply.py [--apply]

Rule (AWH 2026-10-20, memory feedback-trailer-length-limits): a posted trailer limit applies
to a motorhome too unless the source says otherwise, so a campground none of whose public RV
sites is rated for 23 ft fails the minimum site length. I may drop and report.

How the drops were found (scripts beside this one):
  ridb_scan.py      - every rec.gov-linked entry against trip_data/ridb_campsites.json;
                      24 had no RV site listed at >= 23 ft.
  fetch_equipment.py- the site attribute "Max Vehicle Length" is a flat 20 at whole Corps
                      facilities (Lake Ouachita, New Hogan) whose per-equipment MaxLength
                      (what rec.gov prints as "RV up to N ft") runs 30-70 ft, so the
                      candidates were re-read with equipment lengths (equipment.json).
                      That cleared 8.
  agency pages      - a subagent read each remaining campground's FS/BLM page and rec.gov
                      description (2026-10-20). None states 23 ft or more; three confirm
                      the short limit. Horseshoe CO stays on rec.gov's "fits RVs up to 25
                      feet"; Crab Flats stays on one FCFS site listing motorhomes to 26 ft.
Held for AWH, not here: the 22-ft class (Christopher Creek among them) and Umtanum WA,
whose only short figure is the uniform site attribute (its spurs measure 35-69 ft).

Each removal is logged to removals.json beside this script (same format as
audit/drops_2026-10-20/removals.json). Dry run unless --apply; safe to rerun.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CG = os.path.join(ROOT, "campgrounds.json")
LOG = os.path.join(HERE, "removals.json")
DAY = "2026-10-20"
WHY = "every RV site rated under 23 ft (AWH 2026-10-20: a trailer limit applies to a motorhome too)"
CAT = "recreation.gov campsite catalog (RIDB facility {}), read {}: "

DROPS = {
    13701: (232774, "3 RV sites, all 20 ft. FS page: 'Max Trailer Length : 20ft, small trailers or RVs, no turnaround'."),
    10905: (272093, "only 3 RV sites (15-16 ft), the other 13 tent-only. FS page: 'Vehicles 16 ft. max.'"),
    9996: (231936, "27 RV sites at 18-20 ft. FS page: 'It is not possible for trailers/RVs longer than 20 ft to safely manuever into the sites ... You will be turned away.'"),
    12054: (273379, "5 sites, all 16 ft. FS page and rec.gov give no other length."),
    12197: (234116, "16 RV sites, all 20 ft. FS page and rec.gov give no other length."),
    12249: (233404, "42 sites at 14-21 ft (trailer). FS page and rec.gov give no other length."),
    3780: (234620, "10 sites, all 20 ft. FS page and rec.gov give no other length."),
    10044: (10047895, "5 RV sites, all 20 ft; rec.gov: 'Max Vehicle Length includes tow vehicle'. FS page gives no other length."),
    10057: (10046989, "4 sites at 17-20 ft; rec.gov: 'Max Vehicle Length includes tow vehicle'. FS page gives no other length."),
    13214: (256347, "18 sites, all 20 ft (spurs longer). rec.gov: 'tent and limited RV camping'; FS page gives no length."),
    10396: (10344735, "6 sites, max vehicle 20 ft and driveways 20 ft. BLM page gives no other length."),
    6412: (231927, "4 single sites, all 20 ft. FS page: 'designed for tent camping or small trailers'."),
    13215: (10040547, "drive-in sites at 12-20 ft. rec.gov: 'drive-in sites that accomodate small RVs'."),
}

# Kept, with the note and max_rig_ft corrected to what rec.gov says (the old figures were
# driveway or host-site lengths).
FIXES = {
    12304: {
        "old": "RVs/trailers to ~31-32 ft (recreation.gov site data)",
        "new": "trailers to 21 ft on every site per recreation.gov; only first-come site 014 also lists motorhomes, to 26 ft, so a 23-ft rig fits that one site",
        "max_rig_ft": 26,
        "source": "recreation.gov campsite catalog (RIDB 232386), per-site permitted equipment lengths",
    },
    2413: {
        "old": "18 sites, sites to ~40 ft.",
        "new": "18 sites; recreation.gov says the campground 'fits RVs up to 25 feet', though its per-site catalog rates the RV sites at 14-20 ft.",
        "max_rig_ft": 25,
        "source": "recreation.gov facility description (RIDB 233724): 'fits RVs up to 25 feet in length'",
    },
}

if __name__ == "__main__":
    cg = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in cg}
    sys.path.insert(0, ROOT)
    import trips
    log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
    logged = {r["id"] for r in log}
    gone = []
    for i, (fid, ev) in DROPS.items():
        e = by.get(i)
        if e is None:
            assert i in logged, i
            continue
        assert not trips.campground_references(i), i
        assert "--AWH" not in (e.get("note") or ""), i
        gone.append(i)
        log.append({"id": i, "state": e["state"], "name": e["name"], "ownership": e["ownership"],
                    "location": e["location"], "reason": WHY,
                    "evidence": CAT.format(fid, DAY) + ev, "checked": DAY})
        print(f"  drop {i} {e['state']} {e['name']}")
    fixed = 0
    for i, f in FIXES.items():
        e = by[i]
        if f["old"] not in e["note"]:
            continue
        e["note"] = e["note"].replace(f["old"], f["new"])
        e.setdefault("sites", {})["max_rig_ft"] = f["max_rig_ft"]
        e.setdefault("provenance", {})["sites"] = {"source": f["source"], "checked": DAY}
        fixed += 1
        print(f"  fix  {i} {e['state']} {e['name']}")
    print(len(gone), "to drop,", fixed, "to fix")
    if "--apply" in sys.argv and (gone or fixed):
        cg = [e for e in cg if e["id"] not in gone]
        with open(CG, "w", encoding="utf-8") as fh:
            json.dump(cg, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        with open(LOG, "w", encoding="utf-8") as fh:
            json.dump(log, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        print("written")
