#!/usr/bin/env python3
"""Alabama State Parks in the policy registry (2026-10-20).

    python3 -I audit/al_registry/apply.py [--apply]

The row is the camping reservation policy on Alabama State Parks' own reservation site
(reserve.alapark.com), the same block at every park on it. It covers the 19 parks that book
there. Not covered (`policy_ref: none`):
  * parks booked only by phone, with their own fees and discounts: Chickasaw (4868; its
    page: "For Campground Reservations call 334-643-3448", $3 transaction fee) and Paul M.
    Grist (4876; "For reservations call Paul Grist State Park office", run with Dallas County);
  * "state" parks run by their own commissions or other bodies: Historic Blakeley (4862),
    Brierfield Ironworks (4864), Tannehill Ironworks (4879), St. Stephens (13385), Moundville
    (4937, University of Alabama Museums), and DeKalb County Public Lake (4923, an ADCNR
    fisheries lake).
Chickasaw's booking becomes {reservable, platform: phone} from its page. Every entry keeps its
own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
SITE = "https://reserve.alapark.com/desoto/campsites (Camping Reservation Policies, Cancellation & No-Show Policies, Reservation Discounts; the same block at every park on the site)"
NONE = {4868, 4876, 4862, 4864, 4879, 13385, 4937, 4923}
CHICKASAW = 4868
CHICKASAW_SRC = "https://www.alapark.com/parks/chickasaw-state-park/camping ('For Campground Reservations call 334-643-3448')"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://reserve.alapark.com/",
        "window_opens_days": 365,
        "max_stay_nights": 14,
        "note": "Alabama State Parks' own reservation site, or the park office. 'Advanced reservations may be made up to one year in advance.' STAY LIMIT: 14 nights (31 from November 1 to March 31 at select parks), applying to the camping group and the unit alike. Check-in 2 p.m., check-out 11 a.m.; the person reserving must be 18. One wheeled camper and one tent (or two tents) a site, 8 people. A reserved site not occupied by noon the day after the first night is forfeited with all fees unless the park is told; a camper gone three consecutive days forfeits the rest. CANCELLING: up to 72 hours before midnight of the arrival date, everything back but the $5.25 fee; after that, all fees and taxes are kept (for any nights cancelled).",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 5.25,
        "checked": "2026",
        "note": "Each entry carries its own price; rates vary by site and night. The $5.25 reservation fee is non-refundable, per site. 15% off nightly camping, with ID at check-in, for guests 62 and over, veterans and active-duty military, guests with disabilities (ADA), and State of Alabama employees.",
    },
    "provenance": {
        "booking": {"source": SITE, "checked": CHECKED, "method": "manual"},
        "fees": {"source": SITE, "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:AL", "replaces an existing row" if "state:AL" in reg else "is new")
    seen = set()
    for e in cg:
        if e["id"] in NONE:
            assert e["state"] == "AL" and e["ownership"] == "state", e["id"]
            e["policy_ref"] = "none"; seen.add(e["id"])
            print("policy_ref none:", e["id"], e["name"])
        if e["id"] == CHICKASAW:
            e["booking"] = {"reservable": True, "platform": "phone"}
            e.setdefault("provenance", {})["booking"] = {"source": CHICKASAW_SRC, "checked": CHECKED, "method": "manual"}
    assert seen == NONE
    if "--apply" in sys.argv:
        reg["state:AL"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
