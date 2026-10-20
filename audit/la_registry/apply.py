#!/usr/bin/env python3
"""Louisiana State Parks in the policy registry (2026-10-20).

    python3 -I audit/la_registry/apply.py [--apply]

21 of LA's 26 `state` entries are Louisiana State Parks (Office of State Parks), booked on
the Go Outdoors Louisiana reservation system (reservations.gooutdoorslouisiana.com, run by
Brandt Information Services). The row is that system's published policy page.
lastateparks.com refuses scripted reads (403), so its fee page wasn't re-read; the $4.50
reservation fee is what every entry already records from the 2026-10-12 read of the park
pages and booking site.

Not covered (`policy_ref: none`): the Sabine River Authority parks (Cypress Bend 674, Oak
Ridge 6883, Pleasure Point 6884, San Miguel 6924), which have their own minimums and fees, and
LDAF's Indian Creek Recreation Area (6870), booked on ResNexus. Every entry keeps its own
price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
POL = "https://reservations.gooutdoorslouisiana.com/Policies.aspx"
NONE = {674, 6883, 6884, 6924, 6870}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://reservations.gooutdoorslouisiana.com/",
        "window_opens_days": 395,
        "max_stay_nights": 15,
        "note": "Louisiana State Parks book on the Go Outdoors Louisiana system: 'Reservations can be created up to 13 months in advance online, and changed and cancelled by calling 1-833-609-0686.' The person reserving must be 21. STAY LIMIT: 15 consecutive days on any site, then 7 consecutive days away before using it again. Campsite check-in 2 p.m., check-out 1 p.m.; keep the registration receipt. Occupancy is set per site. CANCELLING: a reservation made 10-13 months before arrival costs one night to cancel; inside the 9-month window, $10 at 15 or more days out and one night within 14 days.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 4.5,
        "checked": "2026",
        "note": "Each entry carries its own price; rates rise with demand within each site type's range, plus tax. The $4.50 reservation fee is per booking. America the Beautiful Senior and Access pass holders get 50% off camping if their home state's parks honour the pass.",
    },
    "provenance": {
        "booking": {"source": POL, "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{POL}; the entries' own fee notes (Louisiana State Parks' park pages and booking site, read 2026-10-12)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:LA", "replaces an existing row" if "state:LA" in reg else "is new")
    seen = set()
    for e in cg:
        if e["id"] in NONE:
            assert e["state"] == "LA" and e["ownership"] == "state", e["id"]
            e["policy_ref"] = "none"; seen.add(e["id"])
            print("policy_ref none:", e["id"], e["name"])
    assert seen == NONE
    if "--apply" in sys.argv:
        reg["state:LA"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
