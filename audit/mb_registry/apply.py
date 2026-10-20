#!/usr/bin/env python3
"""Manitoba Parks in the policy registry (2026-10-20).

    python3 -I audit/mb_registry/apply.py [--apply]

All 52 MB `provincial` entries are Manitoba Parks campgrounds (none of the six commercially
operated parks Manitoba lists is in the database), so `provincial:MB` needs no policy_ref
carve-outs. Most entries already carry their own 2026 fees and vehicle permit; the row adds the
booking rules and covers the 11 entries with no fees. Manitoba has no rolling window: each
season's inventory opens on staged launch days in April, so window_opens_days stays absent and
the note says so. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REG = os.path.join(ROOT, "campground_policies.json")
CHECKED = "2026-10-20"
PUBS = "https://www.gov.mb.ca/sd/pubs/parks-protected-spaces/"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "goingtocamp",
        "url": "https://manitoba.goingtocamp.com/",
        "reserve_until": {"relative_to": "arrival", "at": "15:00"},
        "fcfs": "some_sites",
        "min_stay": [{"nights": 2, "applies": "holiday", "season": "long weekends; the stay must include the Saturday and Sunday nights"}],
        "max_stay_nights": 21,
        "note": "Manitoba Parks Reservation Service (goingtocamp), or 1-888-482-2267 (204-948-3333 in Winnipeg). There is no rolling window: 'Camping inventory becomes available for reservations in April', on staged launch days at 7 a.m. (2026: cabins, yurts and group areas April 13; Birds Hill, Winnipeg Beach and Grand Beach April 14; Whiteshell April 15; Northern and Western regions April 16; everything else April 17), and from then the whole season is bookable. Each campground's reservable dates are on Manitoba's Operating Dates list: many stop taking reservations days or weeks before they close (Beresford Lake reserves to Sept 6 but stays open to Oct 12), after which every site is first-come, and a campground with no reservation dates there takes none. 'All reservable sites can now be booked up to 3:00 p.m. on the day of arrival.' 'Although reservations are recommended, some campsites are available on a first-come, first-served basis.' MINIMUM STAY: two nights over long weekends, including the Saturday and Sunday nights (2026: Victoria Day, Terry Fox Day, Labour Day, Thanksgiving); three nights Thursday-Sunday at Birds Hill during the Winnipeg Folk Festival; and a few designated sites carry a seven-night minimum in July and August (Bakers Narrows Bay 2 sites 41-46; Birds Hill Chipping Bay 1-10 and Savannah Bay 1-10; Falcon Beach J 1-10 and Y1 1-10; St. Malo Bay 2 1-10) - every other site books for one night. MAXIMUM STAY: 21 nights on one reservation, and no one may 'occupy the same campsite for more than 21 consecutive nights'. Check-in 4 p.m., check-out 3 p.m.; a late arrival is held until 11 a.m. the next day. Six people or one family per site, one camping unit (plus a tent if space allows); quiet time 11 p.m.-9 a.m. Cancelling 4 or more days ahead costs $10 plus the reservation fee; within 3 days, the first night as well.",
    },
    "fees": {
        "currency": "CAD",
        "reservation_fee": 10,
        "entrance": {"resident": 9.5, "nonresident": 9.5, "per": "vehicle_day"},
        "checked": "2026",
        "note": "Camping fees are per entry; most carry their own 2026 rate. The $10 reservation fee is per booking and non-refundable. Every vehicle needs a provincial park vehicle permit, GST included: $9.50 a day (to midnight), $16.50 for three consecutive days, $44.50 for the year (to April 30, 2027; up to two plates on one permit); bought at manitobaelicensing.ca, a park office or a retailer, the same price for residents and visitors. Permits are not needed on the 2026 free-entry weekends (Family Fishing Weekend June 12-14, Parks Week July 13-19, Labour Day weekend September 4-7) or in February 2027, but camping fees still apply. A Manitoba permit is not valid in Riding Mountain National Park.",
    },
    "provenance": {
        "booking": {"source": "https://www.gov.mb.ca/sd/parks/prs/index.html (2026 camping season information), " + PUBS + "operating_dates.pdf (2026), " + PUBS + "parks_reservation_service.pdf, " + PUBS + "campers_guide.pdf", "checked": CHECKED, "method": "manual"},
        "fees": {"source": "https://www.gov.mb.ca/sd/parks/park-fees/index.html (2026 park vehicle permit fees), https://www.gov.mb.ca/sd/parks/prs/index.html", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    print("provincial:MB", "replaces an existing row" if "provincial:MB" in reg else "is new")
    if "--apply" in sys.argv:
        reg["provincial:MB"] = ROW
        with open(REG, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
