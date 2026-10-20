#!/usr/bin/env python3
"""Entries removed on AWH's answers to audit/registry_asks_2026-10-20.md (2026-10-20).

    python3 -I audit/drops_2026-10-20/apply.py [--apply]

Each removal is logged to removals.json beside this script, in the format of
audit/minimum_stay_removals_2026-10-01.json. No trip references any of them (checked with
trips.campground_references before writing). Dry run unless --apply; safe to rerun.

Montana fishing access sites: FishMT posts "Vehicle Length: Trailer Length is N ft" per site.
AWH: absent anything saying otherwise, a trailer limit applies to a motorhome too, so a 20-ft
limit fails the ~23-ft minimum site length. Every FAS in the database was read; those posting
20 ft go, those posting 25 ft or more or no limit stay.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CG = os.path.join(ROOT, "campgrounds.json")
LOG = os.path.join(HERE, "removals.json")
DAY = "2026-10-20"
FISHMT = "https://myfwp.mt.gov/fishMT/fas/{}"

ASKS = {
    9363: ("not a public campground (AWH, ask #2)",
           "Not on Manitoba Parks' 2026 operating dates, its goingtocamp catalog or the Whiteshell campground maps; the pin shows a small loop of cabins and trailers 2 km W of Falcon Beach Campground. Probably an RV Life phantom or a private camp."),
    5002: ("day use only (AWH, ask #4)",
           "mdwfp.com Golden Memorial State Park page, read 2026-10-20: the park 'is managed as a day use park only'; The Dyrt and Campendium agree."),
    5004: ("closed, gone from the state's park list (AWH, ask #5)",
           "Gone from MDWFP's list of state parks (page 404s) and the reservation catalog; eRegulations lists it closed for renovations; Campendium says permanently closed."),
    6617: ("tent-only (AWH, ask #7)",
           "travelok.com Grand Lake State Park - Little Blue / Disney Area, read 2026-10-20: '30 primitive tent camping spots', only tent sites listed; nothing on ReserveAmerica."),
    6621: ("beside the OHV dune-riding area (AWH, ask #8: keep Hackberry Bend 6626 only)",
           "Pioneer Campground, Beaver Dunes Park (City of Beaver): 'direct access to the dunes' where off-road vehicles ride; out of scope under the 2026-10-02 off-road rule."),
    13827: ("walk-in tent camping by permit (AWH, ask #9)",
            "MDC Busiek State Forest and Wildlife Area page, read 2026-10-20: 'eight primitive, walk-in tent campsites. Camping is permitted ONLY with a permit.'"),
    13903: ("permit-only, and the area regulations prohibit camping (AWH, ask #10)",
            "MDC Little Indian Creek Conservation Area page, read 2026-10-20: 'Camping is allowed by permit only and requested 10 days in advance', while its area regulations say 'Camping is prohibited.'"),
}

# id: FishMT facility id, for every FAS whose page reads "Trailer Length is 20ft." (2026-10-20).
MT_20FT = {
    14105: "39753822", 14106: "39754401", 14107: "39753810", 14108: "39753828", 14111: "39753836",
    14112: "39753838", 14114: "39753840", 14115: "39754309", 14122: "39754383", 14123: "39754407",
    14126: "39754315", 14127: "39753842", 14128: "39754325", 14130: "39753844", 14134: "39753406",
    14136: "39753848", 14137: "39754381", 14140: "39753860", 14142: "39753862", 14146: "39753864",
    14147: "39754391", 14149: "39753690", 14151: "39753854", 14152: "39753866", 14158: "39754327",
    14159: "39753808", 14160: "39754581", 14161: "39754621", 14162: "39754405", 14165: "39754387",
    14166: "39753876", 14168: "39753404", 14169: "39753858", 14170: "39753878",
}

if __name__ == "__main__":
    cg = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in cg}
    drops = {i: v for i, v in ASKS.items()}
    for i, fid in MT_20FT.items():
        drops[i] = ("20-ft trailer limit, under EKKO's 23 ft (AWH 2026-10-20: a trailer limit applies to a motorhome too)",
                    f"{FISHMT.format(fid)}, read 2026-10-20: 'Vehicle Length: Trailer Length is 20ft.'")
    sys.path.insert(0, ROOT)
    import trips
    log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
    logged = {r["id"] for r in log}
    gone = []
    for i, (reason, evidence) in drops.items():
        e = by.get(i)
        if e is None:
            assert i in logged, i
            continue
        assert not trips.campground_references(i), i
        gone.append(i)
        log.append({"id": i, "state": e["state"], "name": e["name"], "ownership": e["ownership"],
                    "location": e["location"], "reason": reason, "evidence": evidence, "checked": DAY})
        print(f"  drop {i} {e['state']} {e['name']}: {reason}")
    print(len(gone), "to drop")
    if "--apply" in sys.argv and gone:
        cg = [e for e in cg if e["id"] not in gone]
        with open(CG, "w", encoding="utf-8") as f:
            json.dump(cg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        with open(LOG, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("written")
