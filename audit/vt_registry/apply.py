#!/usr/bin/env python3
"""Vermont State Parks in the policy registry (2026-10-20).

    python3 -I audit/vt_registry/apply.py [--apply]

All 29 VT `state` entries are Vermont State Parks (Dept. of Forests, Parks and Recreation),
booked on ReserveAmerica (vtstateparks-visit.com, contract VT). Rules from the division's
Reservations page (the policy in force since February 11, 2026) and its Camping page;
fees from Fees and Passes. Every entry keeps its own price and non-resident surcharge.
The parks have no hookups. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CHECKED = "2026-10-20"
RES = "https://vtstateparks.com/reservations.html"
CAMP = "https://vtstateparks.com/camping.html"
FEES = "https://vtstateparks.com/fees.html"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://vtstateparks-visit.com/",
        "window_opens_days": 335,
        "reserve_until": {"relative_to": "arrival", "at": "14:00"},
        "min_stay": [{"nights": 2, "applies": "always", "waived_if": {"booking_within_days": 7}}],
        "max_stay_nights": 21,
        "note": "Vermont State Parks book on ReserveAmerica, by phone at 1-888-409-7579 (weekdays 9-4) or at the park in season. Dates open daily on a rolling 11-month window at 9 a.m.; same-day bookings until 2 p.m. on the arrival day. Full payment at booking. A reservation made more than 7 days ahead needs 2 nights; inside 7 days one night is fine on any day (remote sites at Waterbury Reservoir, Osmore Pond and Kettle Pond always need 2). A booking made on the day its dates open can't be changed or cancelled for 22 days. Without a reservation you may camp if a site is open, but none are held for walk-ins. STAY LIMIT: 21 nights on most sites; 14 on prime sites at Little River and Ricker Pond and on Knight and Woods Islands; 7 for Molly's Falls Pond, Waterbury Reservoir remote sites, Burton Island waterfront lean-tos, cabins and cottages. After the limit, wait 7 days before booking another site in the same park. Check-in 2-9 p.m., check-out 11 a.m.; 8 people and 2 vehicles a site. A camper who hasn't checked in or called by 2 p.m. on the third day loses the site, without refund. CANCELLING: 10 or more days out, everything back but the $8 fee; 3-9 days, the fee and one night are kept; 0-2 days, no refund. Free date or park changes three or more days out if the number of nights and sites stays the same.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 8,
        "checked": "2026",
        "note": "Each entry carries its own price and non-resident rate (in effect since July 1, 2025). Site prices cover 4 people; each extra person is $8 a night (8 at most), each pet $3 a night. The $8 reservation fee is per site and non-refundable. Visitors to a campsite register and pay day-use admission ($5 adult, $2 child 4-13). Vermont residents 62 and over and honorably discharged veterans can get the $2 Green Mountain Passport (lifetime free day use, not camping).",
    },
    "provenance": {
        "booking": {"source": f"{RES}; {CAMP}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{FEES}; {CAMP}", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    print("state:VT", "replaces an existing row" if "state:VT" in reg else "is new")
    if "--apply" in sys.argv:
        reg["state:VT"] = ROW
        with open(REG, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
