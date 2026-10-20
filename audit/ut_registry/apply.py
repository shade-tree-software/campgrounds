#!/usr/bin/env python3
"""Utah State Parks in the policy registry (2026-10-20).

    python3 -I audit/ut_registry/apply.py [--apply]

All 45 UT `state` entries are Utah State Parks. Booking rules come from the division's Park
Rules page (rules-and-faq), which is where its reservation policies now live. Every entry
carries its own price; the Bear Lake entries carry their own non-resident difference, which is
a Bear Lake rate, not a system rule, so the row has none. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CHECKED = "2026-10-20"
RULES = "https://stateparks.utah.gov/rules-and-faq/"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://utahstateparks.reserveamerica.com/",
        "window_opens_days": 120,
        "reserve_until": {"relative_to": "arrival", "offset_hours": -48},
        "fcfs": "after_cutoff",
        "max_stay_nights": 14,
        "note": "Utah State Parks on ReserveAmerica, or 800-322-3770 (8 a.m.-5 p.m. Mountain, Monday-Friday). 'Individual campsites are available for reservation on a four-month rolling basis. For example, on January 10 individual sites are available for reservation through May 10' (window_opens_days carries 120), and 'you can book a maximum of 13 days beyond the last date of the reservation window'. 'For reservations less than two days in advance, please contact the park directly' - the online system stops two days out and the park takes walk-ups for whatever is left, hence after_cutoff. STAY LIMIT: 'generally limited to 14 days within any 30-day period', extendable by the park manager; a park may set less, and its entry says so (Palisade: 5 nights). No minimum stay is published. Check-in 3-10 p.m. (2 p.m. at Sand Hollow); check-out 2 p.m., noon at Wasatch Mountain, Bear Lake, Dead Horse Point, Goblin Valley, Huntington, Jordanelle, Millsite, Palisade, Quail Creek, Hyrum, Sand Hollow, Scofield and Utahraptor. A site not occupied by 10 a.m. the day after arrival is a no-show. Cancelling four or more days ahead costs an $8 cancellation fee on top of the $8 reservation fee; closer in, one night as well.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 8,
        "checked": "2026",
        "note": "Each entry carries its own price (Utah State Parks' fee page and the booking site). 'All reservations are charged an $8 reservation fee', non-refundable. Camping covers one vehicle's park entry; an extra vehicle pays the park's extra-vehicle fee. Bear Lake charges non-Utah residents $5 a night more; that is on its entries, not a system rule.",
    },
    "provenance": {
        "booking": {"source": RULES + " (Campsite Reservations, Length of Stay, Check-in/Check-out, Cancellations)", "checked": CHECKED, "method": "manual"},
        "fees": {"source": RULES + "; Utah State Parks' fee page and booking site, read 2026-10-12", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    print("state:UT", "replaces an existing row" if "state:UT" in reg else "is new")
    if "--apply" in sys.argv:
        reg["state:UT"] = ROW
        with open(REG, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
