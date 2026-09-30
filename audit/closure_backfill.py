#!/usr/bin/env python3
"""Backfill `status.operating = temporarily_closed` from closure notes (2026-09-30).

    python3 audit/closure_backfill.py            # dry run: what would change
    python3 audit/closure_backfill.py --apply    # write campgrounds.json

The map greys out temporarily closed campgrounds and can hide them (AWH
2026-09-30), but until now a closure lived only in `note` prose: 269 notes
matched a closure pattern and the map could see none of them. Every one of those
notes was read by hand; the table below is the result. Only a closure still in
effect on 2026-09-30 is recorded. Deliberately NOT recorded:

  * seasonal closings ("closed in winter", "closes Nov 1") - that is `season`;
  * a partial closure (one loop, the showers, the dump station, a boat launch)
    while the campground itself operates;
  * "reopened ..." history;
  * a closure whose stated end date has already passed - those are RECHECK below,
    because the note is stale either way and a person should look.

Provenance is `derived` from the note, dated today: the claim is only as fresh as
the note it came from, and the popup / manage form show where it came from.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CG = os.path.join(os.path.dirname(HERE), "campgrounds.json")
CHECKED = "2026-09-30"

# id: (reopens or None, reason) - reason is a short paraphrase of the note.
CLOSED = {
    56: (None, "access gate closed (Little Dry River / Long Run Rd), June 2026"),
    57: (None, "access gate closed (Little Dry River / Long Run Rd), June 2026"),
    58: (None, "access gate closed (Little Dry River / Long Run Rd), June 2026"),
    519: (None, "bottom gate on Long Run Rd closed June 2026"),
    520: (None, "bottom gate on Long Run Rd closed June 2026"),
    521: (None, "bottom gate on Long Run Rd closed June 2026"),
    522: (None, "bottom gate on Long Run Rd closed June 2026"),
    480: ("2027", "closed for 2026 after Hurricane Helene"),
    525: (None, "closed in 2026 for maintenance"),
    1107: (None, "closed for roadway/site resurfacing"),
    1547: ("2027", "closed for the 2026 season for renovations"),
    1554: ("Jan 2027", "flood-damage repairs through 12/31/2026"),
    1555: ("~Mar 2027", "major renovation"),
    2306: ("2027", "closed from mid-Aug 2026 for sewer work"),
    2959: (None, "closed for construction in 2026"),
    4161: (None, "closed from July 31, 2026 for bathhouse construction"),
    4391: ("spring 2027", "campground closing fall 2026 for infrastructure renovation"),
    4742: (None, "closed spring 2026 after the Hilux Fire"),
    5026: (None, "closed 2026 for storm/debris cleanup after Winter Storm Fern"),
    5087: (None, "closed for water-service interruption / construction (USFS)"),
    5845: ("~summer 2027", "closed after Sept 8, 2026 for water-main repairs"),
    6176: ("2027", "closed for the 2026 season for construction"),
    6210: (None, "closed for the 2026 season after storm damage"),
    6293: ("2027", "closed for the 2026 season for improvements"),
    6893: (None, "camping closed 2026 (USFS; day use open)"),
    6904: (None, "hurricane-damage closure (USFS)"),
    7248: ("~late 2026", "RV campground closed for electric/wastewater upgrade"),
    7965: ("Nov 2026", "closed for campground renovations through Oct 31, 2026"),
    8220: ("2027", "closed for the 2026 season for major improvements"),
    8826: (None, "closed for flood recovery since June 2026"),
    8904: (None, "closed until further notice after wildfire damage (2026)"),
    8948: (None, "park closed after the July 8, 2026 tornado"),
    9184: ("2027", "closed for the 2026 season for wildfire-damage restoration"),
    9556: (None, "closed mid-2026 for hazard-tree removal"),
    9558: ("~Nov 2026", "closed for reconstruction"),
    9563: ("~late 2026", "closed for reconstruction"),
    9578: (None, "closed 2026 for hazard-tree removal"),
    9598: (None, "closed for the Rainbow-Amanita forest health project"),
    9647: (None, "closed for the 2026 season after fire"),
    9660: (None, "closed after 2024 windstorm damage; restoration underway"),
    9882: (None, "closed for the 2026 season after the Forsyth Fire and flooding"),
    9898: (None, "Forest Service closure order, mid-2026"),
    9933: (None, "closed for the 2026 season for construction"),
    10214: (None, "closed for the 2026 season for windstorm cleanup"),
    10218: ("2027", "closed 2025-2026 for rehabilitation"),
    10280: (None, "closed since late 2025 after the Pomas Fire and road damage"),
    10283: (None, "entrance bridge washed out; closed until repaired"),
    10301: (None, "closed for the Hawk Creek Road project"),
    10326: (None, "closed until further notice (Sourdough Fire debris-flow hazard)"),
    10331: (None, "closed for the 2026 season (Suiattle River Rd flood damage)"),
    10612: (None, "full closure from Aug 2026 for culvert replacement"),
    10666: (None, "inside the 2026 Anthony Fire closure area"),
    10710: (None, "closed for danger-tree treatment"),
    10711: (None, "closed for danger-tree treatment"),
    10753: (None, "closed until further notice for hazard-tree mitigation"),
    10811: (None, "closed for hazardous-tree removal"),
    10869: (None, "closed until further notice for hazard-tree mitigation"),
    10991: (None, "closed July 2026 for the Anthony Fire"),
    11215: (None, "closed for renovations (USFS, 2026)"),
    11268: (None, "closed for the 2026 season after the Davis Fire"),
    11340: ("Oct 2026", "closed for improvements through Oct 1, 2026"),
    11354: (None, "closed for repair; no 2026-27 winter reservations"),
    11620: (None, "closed since the Jan 2025 Hughes Fire"),
    11955: (None, "closed for the 2026 season for hazard trees"),
    11981: (None, "closed for hazard-tree removal"),
    12236: (None, "closed until further notice for hazard-tree removal"),
    13167: (None, "all campgrounds closed until further notice (infrastructure damage)"),
    13168: (None, "closure notice; no sites bookable"),
    13192: (None, "closed for Upper Clackamas redesign; no reopening date"),
    13194: (None, "closed since the 2020 Riverside Fire; redesign in progress"),
    13249: (None, "closed for the 2026 season (Suiattle River Rd washed out)"),
    13251: (None, "inaccessible (Index-Galena Rd / FR 65 closures)"),
    13261: (None, "closed until facilities are rebuilt"),
    13274: ("mid-2027", "closed since 2024 (water supply)"),
    13290: (None, "closed by a road washout after the 2026 Little Giant Fire"),
    13314: (None, "closed for the 2026 season (hazardous trees)"),
    13370: (None, "closed after Hurricane Helene"),
    13397: (None, "closed for the 2026 season"),
    13624: (None, "closed until further notice as of Sept 2026"),
    13658: ("2027", "closed for the 2026 season for improvements"),
    13717: (None, "closed for renovations"),
    13718: ("2027", "closed through 2026 for renovation"),
    13720: (None, "closed for renovations"),
    13721: ("early 2027", "closed for structural renovations"),
    13722: ("late 2026", "closed for renovation"),
    13723: ("late 2026", "closed for renovation"),
    13724: (None, "closed for bathhouse and campground renovations"),
    13726: ("late 2026", "closed for renovations since July 2025"),
    13730: ("2027", "closed for all of 2026 for construction"),
    13967: ("summer 2027", "closed; county/TID joint powers authority to reopen it"),
    14036: (None, "no potable water; repairs underway"),
    14037: ("Oct 2026", "closed for entrance/headquarters rebuilding"),
    14056: (None, "closed 2026 for Bluestone Dam construction"),
    14074: (None, "closed for the 2026 season"),
    14075: (None, "closed since Sept 2025 after the Tacoma Creek Fire"),
    14092: (None, "Loomis State Forest closed for the Sinlahekin Fire"),
    14093: (None, "Loomis State Forest closed for the Sinlahekin Fire"),
}

# Past-dated or hedged closures: the note is stale, a person should look.
RECHECK = {
    149: "note: closed throughout 2025 (waterline project)",
    275: "note: expected to reopen June 2026",
    1534: "note: target reopen mid-March 2026",
    1545: "note: reopening ~spring 2026",
    1807: "note: family sites closed for bathhouse construction as of 2025",
    3269: "note: closed ~Feb-early Aug 2026",
    3270: "note: closed ~Feb-early Aug 2026",
    3385: "note: closed for the 2025 season",
    3606: "note: expected to reopen ~end of July 2026",
    3613: "note: anticipated reopening ~July 4, 2026",
    3642: "note: targeted reopen ~mid-May 2026",
    3645: "note: anticipated reopen ~Aug 1, 2026",
    3646: "note: anticipated reopen ~Sept 1, 2026",
    4131: "note: expected reopen mid-2026",
    5050: "note: 'may be' closed for parkway road construction",
    5579: "note: reopening ~July 1, 2026",
    7160: "note: reopening expected by summer 2026",
    9958: "note: a 2026 construction closure window",
    10411: "note: closed Jun 5-Sep 15, 2026",
    10818: "note: closure order expired end of 2025",
    12231: "note: subject to a forest-order closure",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    text = open(CG, encoding="utf-8").read()
    rows = json.loads(text)
    by_id = {e["id"]: e for e in rows}
    missing = [i for i in CLOSED if i not in by_id]
    if missing:
        raise SystemExit(f"ids not in campgrounds.json: {missing}")
    changed = 0
    for i, (reopens, reason) in CLOSED.items():
        e = by_id[i]
        status = e.get("status") or {}
        if status.get("operating") and status.get("operating") != "temporarily_closed":
            print(f"  skip {i} {e['name']}: status already {status['operating']}")
            continue
        new = {"operating": "temporarily_closed", "note": reason}
        if reopens:
            new["reopens"] = reopens
        if status == new:
            continue
        e["status"] = new
        e.setdefault("provenance", {})["status"] = {
            "source": "note prose", "checked": CHECKED, "method": "derived"}
        changed += 1
        print(f"  {i:>6} {e['state']} {e['name'][:44]:<44} {reopens or '-':<12} {reason[:50]}")
    print(f"{changed} entries {'written' if args.apply else 'would change'}; "
          f"{len(RECHECK)} flagged for a re-check (not written)")
    if args.apply and changed:
        out = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
        tmp = CG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(out)
        os.replace(tmp, CG)
        json.loads(open(CG, encoding="utf-8").read())
    return 0


if __name__ == "__main__":
    sys.exit(main())
