#!/usr/bin/env python3
"""Kentucky State Parks in the policy registry (2026-10-20).

    python3 -I audit/ky_registry/apply.py [--apply]

30 of KY's 31 `state` entries are Kentucky State Parks, which book on ReserveAmerica
(kentuckystateparks.reserveamerica.com, contract KY; every park page's Reserve link goes there).
The rule is 304 KAR 1:040 (campgrounds); the booking window, minimums and fees come from
ReserveAmerica's KY pages. The Kentucky Horse Park (1618) is run by its own commission with
its own terms, so it gets `policy_ref: none`.

27 park entries carried a note-derived `platform: "operator"`, read from "Reserve via Kentucky
State Parks"; the parks book on ReserveAmerica, so the key is removed and they inherit the row.
Every entry keeps its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
KAR = "https://apps.legislature.ky.gov/law/kar/titles/304/001/040/ (304 KAR 1:040 Section 1)"
RA = "https://kentuckystateparks.reserveamerica.com/camping/paintsville-lake-state-park/r/campgroundDetails.do?contractCode=KY&parkId=91823 (booking window and the statewide alert text; Columbus-Belmont's reads the same)"
FEES = "https://kentuckystateparks.reserveamerica.com/showPage.do?name=common&commonPath=/usa/ky/kyfeesmain.html"
FAQ = "https://parks.ky.gov/info/faqs"
HORSE_PARK = 1618

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://kentuckystateparks.reserveamerica.com/",
        "window_opens_days": 365,
        "reserve_until": {"relative_to": "arrival", "offset_hours": -24},
        "fcfs": "some_sites",
        "min_stay": [{"nights": 2, "applies": "weekend"}],
        "max_stay_nights": 14,
        "note": "Kentucky State Parks book on ReserveAmerica or by phone at (888) 4KY-PARK, up to 12 months ahead and at least a day before arrival; a campsite not reserved is first come, first served (304 KAR 1:040), and walk-ins are taken as space allows. One night is the minimum on weeknights; an arrival on Friday or Saturday must stay two, and 'longer minimum night stays are required at most campgrounds during holiday periods' (not specified, so not recorded). STAY LIMIT: 14 days, unless the park manager waives it for an emergency or business necessity. Check-in 2 p.m., check-out 1 p.m. (the regulation). Eight people and two units a site (one camper and one tent, or two tents), two vehicles; four adults and children 16 and under are in the base rate. The person reserving must be 21. Gear may not be left unattended more than 24 hours without the manager's written permission. Changes are free online or by phone up to a day before arrival. CANCELLING: 15 or more days out, the $6 reservation fee and a $10 cancellation fee are kept; 14 days or less, the first night too. On the day of arrival, call the park.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 6,
        "checked": "2026",
        "note": "Each entry carries its own price; parks post Sunday-Thursday, Friday-Saturday and holiday rates per site type. The $6 reservation fee is non-refundable; cancelling adds $10. Camping fees carry 6% sales tax, a 1% state transient tax and county taxes. Each adult past four on a site adds $5 a night, paid at the park. Guests 62 and over get 10% off with ID; no discounts on tent sites.",
    },
    "provenance": {
        "booking": {"source": f"{KAR}; {RA}; {FEES}; {FAQ}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{FEES}; {RA}; {FAQ} (senior discount)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:KY", "replaces an existing row" if "state:KY" in reg else "is new")
    n = 0
    for e in cg:
        if e.get("state") != "KY" or e.get("ownership") != "state":
            continue
        if e["id"] == HORSE_PARK:
            e["policy_ref"] = "none"; print("policy_ref none:", e["id"], e["name"])
            continue
        b = e.get("booking") or {}
        if b.get("platform") == "operator":
            assert e["provenance"]["booking"]["method"] == "derived", e["id"]
            del b["platform"]; n += 1
    print("operator platform removed from", n, "entries")
    if "--apply" in sys.argv:
        reg["state:KY"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
