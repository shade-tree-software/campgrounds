#!/usr/bin/env python3
"""New Hampshire State Parks in the policy registry (2026-10-20).

    python3 -I audit/nh_registry/apply.py [--apply]

All 18 NH `state` entries are NH State Parks campgrounds, booked through ReserveAmerica. Sources:
NH State Parks' Camping Policies page (which quotes the rule, Ncr 732.03) and its Camping
Reservations & Fees page. The policies page gives the reservation fee as $7.00 and, further down,
as $6.50; the fees page says $7.00, so $7 it is.

Greenfield (4101) and Pawtuckaway (4102) lose a note-derived `platform: operator` (both book on
ReserveAmerica) and Lake Francis (4114) a derived `max_stay_nights: 14` the row now carries. Every
entry keeps its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
POL = "https://www.nhstateparks.org/find-camping-lodging/camping-policies"
FEES = "https://www.nhstateparks.org/fees-reservations/camping-rates-reservations"
DROP = {4101: "platform", 4102: "platform", 4114: "max_stay_nights"}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://newhampshirestateparks.reserveamerica.com/",
        "window_opens_days": 335,
        "min_stay": [{"nights": 3, "applies": "always", "season": "reservations made before April 1 for that season (from April 1, 1 night)"}],
        "max_stay_nights": 14,
        "note": "ReserveAmerica, online or 1-877-647-2757, up to 11 months ahead; sites open at 8 a.m. weekdays and 9 a.m. weekends on the 11-month mark. MINIMUM: 3 nights for any reservation made before April 1 of its season (so for every booking of next season); from April 1, 1 night. STAY LIMIT (Ncr 732.03): 14 consecutive days, extendable by up to 14 more when the campground is under 60% full; at Hampton Beach and Ellacoya RV parks 14 days consecutive or cumulative between Memorial Day and Labor Day weekends, never extended. Check-in 1-8 p.m., check-out 11 a.m.; only the named holder can check in, and a name change counts as a cancellation. The rate covers two adults and up to four children (at most four adults, six people). Changes by phone until the day before, $2.15. CANCELLING: 10 or more days out, everything back but the reservation fee; 4-9 days, less the fee and one night; 0-3 days, no refund. No refunds for weather or mosquitoes.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 7,
        "checked": "2026",
        "note": "Each entry carries its own price. The $7 reservation fee is non-refundable; a change costs $2.15. Each extra adult $10 a night, each extra child $5. New Hampshire residents 65 and over get $5 a night off the site fee as primary occupant (not on holidays or holiday-weekend minimums, and not at Hampton Beach RV, Ellacoya RV, Cannon RV or the Coleman lodges). Visitors pay the day-use fee.",
    },
    "provenance": {
        "booking": {"source": f"{POL} (quoting Ncr 732.03); {FEES}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{FEES}; {POL}", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:NH", "replaces an existing row" if "state:NH" in reg else "is new")
    for e in cg:
        if e["id"] in DROP:
            assert e["state"] == "NH" and e["provenance"]["booking"]["method"] == "derived", e["id"]
            v = e["booking"].pop(DROP[e["id"]], None)
            print("drop", DROP[e["id"]], v, e["id"], e["name"])
    if "--apply" in sys.argv:
        reg["state:NH"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
