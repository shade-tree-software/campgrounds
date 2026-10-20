#!/usr/bin/env python3
"""Tennessee State Parks in the policy registry (2026-10-20).

    python3 -I audit/tn_registry/apply.py [--apply]

39 of TN's 42 `state` entries are Tennessee State Parks, booked on the division's own system
(reserve.tnstateparks.com). Notchy Creek, Toqua and Lotterdale Cove are the Tellico Lake
campgrounds, run outside the state park system on Campspot with their own terms, so they get
`policy_ref: none`. Every park entry carries its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
POLICIES = "https://tnstateparks.com/about/policies"
PARK = "https://reserve.tnstateparks.com/tims-ford/camping/ (the camping policy block every park's reservation page carries; Cove Lake's reads the same)"
NOT_TNSP = {4447: "Notchy Creek", 13393: "Toqua", 13394: "Lotterdale Cove"}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://reserve.tnstateparks.com/",
        "window_opens_days": 365,
        "max_stay_nights": 14,
        "note": "Tennessee State Parks' own reservation system (reserve.tnstateparks.com), or 888-867-2757. 'Reservations for campsites may be made up to one year prior to arrival date', with the whole stay, tax and the reservation fee paid at booking. The booking help on every park's page says 'Most campsites require a minimum of a 2-night stay' without saying which sites or dates, so no minimum is recorded; a one-night stay may be refused. STAY LIMIT: 'Maximum stay for camping is 14 days (28 days December 1 to February 28/29). After the maximum stay, members of the camping party must vacate the park for 3 consecutive camping nights prior to returning.' Six people per site; quiet hours 10 p.m.-6 a.m.; check-in 4 p.m., check-out noon (as printed at Tims Ford and Cove Lake). Campers no longer check in with the attendant unless a discount is applied; the site tag carries the reservation. CANCELLING: two or more days before arrival, everything back except the $5 fee; one day before, the first night, tax and the fee are forfeited; on the day, the first two nights (all of a one-night stay).",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 5,
        "checked": "2026",
        "note": "Each entry carries its own price; Tennessee State Parks price by site, season and night, higher on weekends and busy dates, plus state and local tax. The $5 'Advanced Reservation Fee' is per campsite and non-refundable. No entrance fee. Discounts (one per site, never on premium sites): seniors 62 and over, resident or not, per the division's rate schedule when the senior owns the camper; active-duty U.S. military 25-50% (booked within 30 days of arrival); disabled visitors 25-50%; Tennessee resident veterans 50% December 1-February 28/29 and one free night on Veterans Day, and 50% year-round with a 100% service-connected disability (booked within 30 days).",
    },
    "provenance": {
        "booking": {"source": f"{POLICIES} (Camping, Camping Cancellations); {PARK}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{POLICIES} (Senior Citizen Discounts, ADA Discount, Tennessee Veterans Discounts); {PARK}", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:TN", "replaces an existing row" if "state:TN" in reg else "is new")
    for e in cg:
        if e["id"] in NOT_TNSP:
            assert e["state"] == "TN" and e["ownership"] == "state", e["id"]
            print("policy_ref none:", e["id"], e["name"])
            e["policy_ref"] = "none"
    if "--apply" in sys.argv:
        reg["state:TN"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
