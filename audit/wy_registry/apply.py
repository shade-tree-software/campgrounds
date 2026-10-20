#!/usr/bin/env python3
"""Wyoming State Parks in the policy registry (2026-10-20).

    python3 -I audit/wy_registry/apply.py [--apply]

15 of WY's 18 `state` entries are Wyoming State Parks & Historic Sites, booked on
reserve.wyoming.gov (US eDirect). The row is the division's 2026 Reservation Information page;
its rules (Chapter 1, effective 11/16/2021) are linked from the Rules & Regulations page as PDFs.
The booking window differs by residency (120 days resident, 113 non-resident) and so does the
reservation fee ($4 / $8); the row records the resident figures, as each entry's price is the
resident one, and the note gives both.

Not covered (`policy_ref: none`): Game and Fish's Soda Lake WHMA (6363) and Tongue River (6369)
campgrounds, and the Wyoming State Fairgrounds RV park (6549). Every entry keeps its own price,
non-resident surcharge and day-use fee. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
RES = "https://wyoparks.wyo.gov/index.php/permits-reservations/reservations"
PERMITS = "https://wyoparks.wyo.gov/index.php/permits-reservations/permits-fees"
NONE = {6363, 6369, 6549}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "usedirect",
        "url": "https://reserve.wyoming.gov/",
        "window_opens_days": 120,
        "fcfs": "some_sites",
        "max_stay_nights": 14,
        "note": "reserve.wyoming.gov or 877-996-7275 (7 a.m.-7 p.m.). Wyoming residents book up to 120 days ahead, non-residents 113; new dates, and any site freed by a cancellation, release at 7 a.m. MT. A booking made on the first day of its window can't be changed for 18 days. Reservations are taken only in each park's season (mostly May 15-September 15); outside it every site is first come, and most parks keep some first-come sites in season too. STAY LIMIT: 14 days in any rolling 30 at one park. Check-in after 3 p.m., check-out by 11 a.m.; the account holder must occupy the site every night, and a reservation covers one vehicle. Not there by 11 a.m. the day after arrival is a no-show, cancelled without refund (a third no-show cancels the year's bookings). CANCELLING: a refund only up to two full calendar days before arrival (for a Friday arrival, by Tuesday night); never for early departure, weather or low water.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 4,
        "checked": "2026",
        "note": "Each entry carries its own price, non-resident surcharge and day-use fee. The reservation fee is $4 for Wyoming residents and $8 for non-residents; a change is $4; none of them is refunded. Wyoming resident veterans rated 50% or more service-connected disabled camp and enter free for life with the Lifetime Veteran's Pass.",
    },
    "provenance": {
        "booking": {"source": RES, "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{RES}; {PERMITS}", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:WY", "replaces an existing row" if "state:WY" in reg else "is new")
    seen = set()
    for e in cg:
        if e["id"] in NONE:
            assert e["state"] == "WY" and e["ownership"] == "state", e["id"]
            e["policy_ref"] = "none"; seen.add(e["id"])
            print("policy_ref none:", e["id"], e["name"])
    assert seen == NONE
    if "--apply" in sys.argv:
        reg["state:WY"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
