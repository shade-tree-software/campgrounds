#!/usr/bin/env python3
"""Oklahoma State Parks in the policy registry (2026-10-20).

    python3 -I audit/ok_registry/apply.py [--apply]

All 51 OK `state` entries are Oklahoma State Parks (Oklahoma Tourism and Recreation
Department), booked on okstateparks.reserveamerica.com. Booking rules come from the
Administrative Code (OAC 725:30-12-5), which the standing rule puts above the website; fees
from TravelOK's reservation guidelines and the 2026-10-12 booking-site price research, which
found no reservation fee although the rule allows one. No stay limit was found in the code or
on TravelOK, so max_stay_nights is absent. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CHECKED = "2026-10-20"
OAC = "https://www.law.cornell.edu/regulations/oklahoma/OAC-725-30-12-5"
GUIDE = "https://www.travelok.com/state-parks/reservation-guidelines"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://okstateparks.reserveamerica.com/",
        "window_opens_days": 335,
        "fcfs": "never",
        "min_stay": [
            {"nights": 2, "applies": "weekend"},
            {"nights": 3, "applies": "holiday", "season": "any multi-day period around a state holiday (Memorial Day, 4th of July and Labor Day named)"},
        ],
        "note": "Oklahoma State Parks on ReserveAmerica (okstateparks.reserveamerica.com, linked from travelok.com/state-parks). OAC 725:30-12-5: 'Individual camping reservations are accepted up to eleven (11) months in advance' (window_opens_days carries 335). 'All sites must be reserved prior to occupancy. No sites within the parks system are available on a first-come basis', and TravelOK repeats 'Online reservations must be made for all RV and tent campsites'; a few entries name tent areas a park still runs first-come. MINIMUM STAY: 'The minimum reservation shall be for two (2) nights on weekends and three (3) nights on holiday periods'; 'at the discretion of the Manager, single night reservations may be accepted less than thirty (30) days prior to arrival' - a discretion, not a waiver, so it is not recorded as one. No stay limit is published. Holiday reservations (Memorial Day, 4th of July, Labor Day) need the whole stay paid up front; otherwise the full stay is charged as a deposit at booking anyway. Check-in 5 p.m., check-out 2 p.m.; a confirmed reservation is held until 10 a.m. the day after arrival. Cancel at least five days before arrival for a full refund, or forfeit the first night. Reselling a reservation (Airbnb and the like) is illegal under 74 O.S. 2217.",
    },
    "fees": {
        "currency": "USD",
        "checked": "2026",
        "note": "Each entry carries its own 2026 price from the booking site; Oklahoma publishes no rate table. No reservation fee was charged on the 2026 booking site (the rule permits a portal and a reservation fee); a 3% service fee applies to card payments, plus tax. 'One parking pass to this state park is included with a completed reservation'; other vehicles need their own pass for the stay. Seniors 62 and over and active or former military get 10% off the campsite base rate; 100% disabled visitors get 50% off it (utilities not discounted). A $75 card hold is taken at check-in.",
    },
    "provenance": {
        "booking": {"source": f"{OAC} (OAC 725:30-12-5); https://www.travelok.com/state-parks/campsites; {GUIDE}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{GUIDE}; audit/state_park_fees/ok_build.py (booking-site rates, read 2026-10-12)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    print("state:OK", "replaces an existing row" if "state:OK" in reg else "is new")
    if "--apply" in sys.argv:
        reg["state:OK"] = ROW
        with open(REG, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
