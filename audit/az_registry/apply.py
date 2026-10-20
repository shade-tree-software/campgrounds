#!/usr/bin/env python3
"""Arizona State Parks & Trails in the policy registry (2026-10-20).

    python3 -I audit/az_registry/apply.py [--apply]

All 15 AZ `state` entries are Arizona State Parks & Trails campgrounds, booked on the agency's own
system at azstateparks.com/reserve (run by Tyler Technologies, hence `operator`). The row is the
agency's Reservation and Cancellation Policies page. Every entry keeps its own seasonal price.
Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CHECKED = "2026-10-20"
POL = "https://azstateparks.com/reservation-policies"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://azstateparks.com/reserve/",
        "window_opens_days": 365,
        "reserve_until": {"relative_to": "arrival", "offset_hours": -24},
        "min_stay": [{"nights": 2, "applies": "weekend", "season": "peak season"}],
        "max_stay_nights": 14,
        "note": "Arizona State Parks' own booking site or 877-697-2757: up to 365 days ahead and at least one day before arrival. MINIMUM: 2 nights on peak-season weekends. STAY LIMIT: 14 nights in any 30 per park, per household (the park manager may extend). Up to five sites per household per stay. Check-in 2 p.m., check-out noon; ten people (six adults) and one vehicle a site, extra vehicles $15 a night. A camper not there by noon the day after the first night forfeits everything and the site goes to walk-ins. Two free changes; a third means cancelling and rebooking. CANCELLING (by phone, 8 a.m.-5 p.m.): a $20 fee always, plus the $3.60 reservation fee; after 2 p.m. the day before check-in, one night as well.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 3.6,
        "checked": "2026",
        "note": "Each entry carries its own price, which varies by site and season and includes park entry. The $3.60 reservation fee is per site and non-refundable (it goes to Tyler Technologies, which runs the booking system); every cancellation costs $20. An extra vehicle is $15 a night.",
    },
    "provenance": {
        "booking": {"source": POL, "checked": CHECKED, "method": "manual"},
        "fees": {"source": POL, "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    print("state:AZ", "replaces an existing row" if "state:AZ" in reg else "is new")
    if "--apply" in sys.argv:
        reg["state:AZ"] = ROW
        with open(REG, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
