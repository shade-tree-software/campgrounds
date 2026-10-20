#!/usr/bin/env python3
"""Maine State Parks (Bureau of Parks and Lands) in the policy registry (2026-10-20).

    python3 -I audit/me_registry/apply.py [--apply]

All 11 ME `state` entries are BPL state park campgrounds booked on CampWithME.com (the bureau's
own system). Sources: BPL's Reservation Tips, Cancellation/Refund Policy, Camping index and Park
Rules pages. Two things don't fit a single field and live in the note instead:
  * the 14-night limit applies only from the last Saturday in June to the third Saturday in
    August (rule 13; "No maximum stay limit during the off season"), so the row has no
    `max_stay_nights`;
  * the season opens for booking on fixed February dates, not on a rolling window.
Sebago Lake (17) also takes a 4-night minimum on reservations made during February, which goes
on the entry. Every entry keeps its own resident / non-resident price. Dry run unless --apply;
safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
BASE = "https://www.maine.gov/dacf/parks/"
TIPS = BASE + "camping/reservations/reservation_tips.shtml"
CANCEL = BASE + "camping/reservations/cancellation_refund_policy.shtml"
RULES = BASE + "park_passes_fees_rules/park_rules.shtml"
INDEX = BASE + "camping/reservations/index.shtml"
WEEKEND = {"nights": 2, "applies": "weekend", "season": "reservations made before July 1"}
SEBAGO = 17

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://www.campwithme.com/",
        "reserve_until": {"relative_to": "arrival", "offset_hours": -24},
        "fcfs": "after_cutoff",
        "min_stay": [WEEKEND],
        "note": "CampWithME.com or 800-332-1501 (207-624-9950 from outside Maine; weekdays 9-4). The season opens for booking on fixed dates in early February (Lily Bay and Sebago a few days before the rest) and reservations close for the year in mid-September; after that every site is first come until the parks close in mid-October. Book by 4 p.m. Eastern at least a day before arrival. MINIMUM: 2 nights on a Friday-Saturday stay booked before July 1; from July 1 single nights, weekends included. STAY LIMIT: 14 nights per person per park from the last Saturday in June to the third Saturday in August; no limit the rest of the season. Six people a site, one adult 18+; check-in 1-9 p.m., the camping day ends at 11 a.m.; a site may not be left more than two nights. A reserved site is held the first night, then resold at 1 p.m. on the second day with no refund. CANCELLING: before 4 p.m. on the arrival date, everything back but the processing fee; after that, the first night too. A partial cancellation can't break the minimum.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 5,
        "checked": "2026",
        "note": "Each entry carries its own resident and non-resident price (Maine residents hold a Maine driver's licence or vehicle registration). The non-refundable $5 processing fee is charged for each night reserved, not once per booking. 9% lodging tax on camping fees.",
    },
    "provenance": {
        "booking": {"source": f"{TIPS}; {CANCEL}; {INDEX}; {RULES} (rule 13)", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{TIPS}; {CANCEL}; the entries' fee notes (BPL fee schedule, read 2026-10-12)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:ME", "replaces an existing row" if "state:ME" in reg else "is new")
    for e in cg:
        if e["id"] == SEBAGO:
            assert e["name"].startswith("Sebago Lake")
            b = e.get("booking") or {}
            b["min_stay"] = [WEEKEND, {"nights": 4, "applies": "always", "season": "reservations made during February"}]
            e["booking"] = b
            e.setdefault("provenance", {})["booking"] = {"source": CANCEL + " ('Sebago Lake State Park 4 night stay for reservations made during (not for) February')", "checked": CHECKED, "method": "manual"}
            print(e["id"], e["name"], b)
    if "--apply" in sys.argv:
        reg["state:ME"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
