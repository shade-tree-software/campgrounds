#!/usr/bin/env python3
"""New Mexico State Parks in the policy registry (2026-10-20).

    python3 -I audit/nm_registry/apply.py [--apply]

All 38 NM `state` entries are New Mexico State Parks (EMNRD), booked on ReserveAmerica.
The rule is 19.5.2.12 NMAC as amended 7/1/2025, which beats the website where they differ
(reference_agency_policy_research). Its stay limit is seasonal: 7 days in any 20 from May 1
to September 30, 14 in any 20 the rest of the year. The row records 7, the limit in the
camping season, and the note gives both.

Rockhound (7933) and Lea Lake (7931) carried a note-derived `max_stay_nights: 14`, which is
only the winter half of the rule and would have overridden the summer 7. The script removes
those two keys and the "14-day limit" from both notes, so the entries inherit the full rule.
Hyde Memorial (7960) carried a note-derived `fcfs: always` ("Electric RV sites are first-come,
first-served"); ReserveAmerica lists 37 of its campsites as bookable, the electric RV area included,
so its booking becomes the row's ReserveAmerica record and the note says so.

Every entry keeps its own price and non-resident surcharge. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
NMAC = "https://www.srca.nm.gov/parts/title19/19.005.0002.pdf (19.5.2.12-13 NMAC) and the 7/1/2025 amendment, https://www.srca.nm.gov/wp-content/uploads/2025/06/19.5.2amend.html"
CAMPING = "https://www.emnrd.nm.gov/spd/camping/"
NOTE_FIXES = {
    7931: ("first-come, first-served (14-day limit). --Claude", "first-come, first-served. --Claude"),
    7933: ("first-come, first-served; 14-day limit. --Claude", "first-come, first-served. --Claude"),
    7960: ("Electric RV sites are first-come, first-served. --Claude",
           "ReserveAmerica lists 37 of the campsites as bookable, the electric RV area included (read 2026-10-20). --Claude"),
}
HYDE_RA = "https://newmexicostateparks.reserveamerica.com/camping/hyde-memorial/r/campgroundDetails.do?contractCode=NM&parkId=430013"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://newmexicostateparks.reserveamerica.com/",
        "window_opens_days": 180,
        "fcfs": "some_sites",
        "max_stay_nights": 7,
        "note": "New Mexico State Parks book on ReserveAmerica: 'Most campgrounds have a certain number of campsites that can be reserved in advance online. Campsites can be reserved 6 months in advance.' The rest are first come, first served, and nobody may hold a site for someone else. At the campground a green 'Vacant' sign means the site is free for one night; red 'Occupied' or 'Reserved' means it is taken. STAY LIMIT (19.5.2.12 NMAC): from May 1 through September 30, 7 days in any 20-day period; from October 1 through April 30, 14 days in any 20; the director may extend, shorten or waive either. Camping gear must leave the park at the limit. A reserved site not occupied, and not called about, by 8 a.m. the day after the arrival date is released with no refund (it was 4 p.m. before the 7/1/2025 amendment). The park may require the whole stay paid in advance for weekends, holidays and special events.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 3.5,
        "checked": "2026",
        "note": "Each entry carries its own price and non-resident surcharge. Since January 1, 2025 the schedule differs by residency, per vehicle per night: primitive $10 resident / $15 non-resident; developed $15/$20; with electric $20/$30; with sewer $20/$25; electric and sewer $25/$35 (water hookups $5 more where a site has them). A site's hookup fee is owed whether or not it is used. ReserveAmerica adds $3.50 a night, at most $10 a reservation, and $5 to cancel; neither goes to the parks. Annual camping permit holders pay only the hookup fees ($5-20 a day), and a park may accept the permit at reservable sites if posted.",
    },
    "provenance": {
        "booking": {"source": f"{NMAC}; {CAMPING}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{CAMPING} (Reserve America Fees, Camping Fees); 19.5.2 NMAC", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:NM", "replaces an existing row" if "state:NM" in reg else "is new")
    for e in cg:
        if e["id"] in NOTE_FIXES:
            old, new = NOTE_FIXES[e["id"]]
            if old in e["note"]:
                e["note"] = e["note"].replace(old, new)
                print("note fixed:", e["id"])
            if e["id"] == 7960 and (e.get("booking") or {}).get("fcfs") == "always":
                assert e["provenance"]["booking"]["method"] == "derived"
                e["booking"] = {"reservable": True, "platform": "reserveamerica"}
                e["provenance"]["booking"] = {"source": HYDE_RA, "checked": CHECKED, "method": "manual"}
                print("Hyde booking corrected")
            b = e.get("booking") or {}
            if b.pop("max_stay_nights", None) is not None:
                assert e["provenance"]["booking"]["method"] == "derived", e["id"]
                print("own max_stay_nights removed:", e["id"], e["name"])
    if "--apply" in sys.argv:
        reg["state:NM"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
