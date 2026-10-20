#!/usr/bin/env python3
"""Montana Fish, Wildlife & Parks in the policy registry (2026-10-20).

    python3 -I audit/mt_registry/apply.py [--apply]

Montana's 99 `state` entries are one agency, FWP: 24 state parks and 75 fishing access sites
(FAS). One row, `state:MT`, reached by ownership+state, carries what binds both - the 7-night
stay limit of FWP's public use rules - and the state parks' booking system. The FAS entries
already say `reservable: false, fcfs: always` themselves, which drops the row's platform,
window, cutoff and reservation fee there (`campground_schema._moot_agency_keys`). Every entry
carries its own 2026 price, so the row has no nightly figures; non-resident rates and the
entrance fee are in the note rather than fields, because a non-resident's camping rate at a
state park already includes the day's entrance, and as fields they would also print under the
FAS, where neither applies. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REG = os.path.join(ROOT, "campground_policies.json")
CHECKED = "2026-10-20"
FEES_PAGE = "https://fwp.mt.gov/stateparks/fees-and-general-information"
RULES_PAGE = "https://fwp.mt.gov/conservation/wildlife-management-areas/public-use-rules"
CAMP_PAGE = "https://fwp.mt.gov/activities/camp"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://montanastateparks.reserveamerica.com/",
        "window_opens_days": 90,
        "reserve_until": {"relative_to": "arrival", "offset_hours": -24},
        "fcfs": "after_cutoff",
        "max_stay_nights": 7,
        "note": "Montana State Parks (FWP) on ReserveAmerica, or 855-922-6768. Reservations are taken only for stays from the third Friday in May through the third Sunday in September; the rest of the year every site is first-come. 'Reservations for individual campsites ... are available up to 3 months in advance of arrival' (window_opens_days carries 90) and 'no later than one day prior to your arrival' ('There is a 1-day minimum window'); a multi-night stay booked on the first day of the window is frozen for 12 days. 'On the date of arrival, if a site is not reserved it becomes a first come first served for that night', and some parks also hold designated walk-up sites, shown as 'walk-up' on the booking map - those parks' entries say so. 20 of the 55 state parks take reservations; the fishing access sites take none (each FAS entry says first-come itself). STAY LIMIT, both: FWP's public use rules (ARM, printed on its public-use-rules page) prohibit camping 'for a period of longer than 7 nights during any consecutive 30-day period, beginning with the first night occupied unless otherwise posted by the department', and the state parks' camping policies say the same ('Campers may stay no longer than 7 nights in any thirty-day period'). No minimum stay is published on either page. Check-in 2 p.m., check-out 1 p.m. (campsites; cabins and yurts 3 p.m./noon); quiet hours 10 p.m.-7 a.m.; 8 people, one camping unit and two extra tents per site. Changes $10 (extending a stay is free); cancelling costs $10 before check-in time, plus the first night after it, and the reservation fee is never refunded; a reservation not claimed by check-in time the day after arrival is a no-show and forfeits everything.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 10,
        "checked": "2026",
        "note": "Each entry carries its own 2026 camping fee. STATE PARKS: 'Campsite fees range from $4-$34 per night, depending on season and available amenities'; the $10 reservation fee is per site, online or by phone, and non-refundable. Non-residents pay $10-12 a night more, which buys the day's entrance - the $50 annual Nonresident Entrance Pass or the $35 7-day pass (sold at the parks) takes that $10-12 off the camping fee instead. Day-use entrance without camping: residents free if they paid the $9 state parks fee with their vehicle registration (otherwise the non-resident fee applies), non-residents $8 a vehicle. Montana residents 62 and over, with a disability, or with veteran status get 50% off camping fees (not electric fees). FWP proposed in June 2026 to raise state-park camping fees no earlier than 2027. FISHING ACCESS SITES: no reservation and no entrance fee, but everyone 12 or older needs FWP's annual Conservation License to use one ($8 resident, $4 youth 12-17 and seniors 62+, $10 non-resident; license year from March 1; it comes with any Montana fishing license). Where camping is charged, FWP's 2026 FAS use fee table sets it statewide: $12 a night with a Montana fishing license, $18 without, $5/$7.50 for Montana residents 62 or over, disabled or veterans. Sites with no camping fee cost only the Conservation License, which those entries price for two people.",
    },
    "provenance": {
        "booking": {"source": f"{FEES_PAGE} (Campsite Reservation Policies, General Camping Policies, FAQs), {CAMP_PAGE}, {RULES_PAGE}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{FEES_PAGE}; https://fwp.mt.gov/binaries/content/assets/fwp/fish/fas/2026-fas-fee-table_adopted.pdf (2026 FAS use fee table); https://fwp.mt.gov/buyandapply/conservation-license", "checked": CHECKED, "method": "manual"},
    },
}

reg = json.load(open(REG, encoding="utf-8"))
old = reg.get("state:MT")
print("state:MT", "replaces an existing row" if old else "is new")
print(json.dumps(ROW, indent=1, ensure_ascii=False)[:1500])
if "--apply" in sys.argv:
    reg["state:MT"] = ROW
    with open(REG, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("written")
