#!/usr/bin/env python3
"""Arkansas State Parks in the policy registry (2026-10-20).

    python3 -I audit/ar_registry/apply.py [--apply]

All 30 AR `state` entries are Arkansas State Parks, booked on the division's own system
(reserve.arkansasstateparks.com). The rule is 22 CAR § 50-108(e); the reservation site's camping
policy block (identical at every park) adds the check-in time, the cancellation terms and the
discounts. The site says the nightly quote excludes "taxes or the reservation fee" but never
states the fee, so `reservation_fee` stays unknown. arkansasstateparks.com's old policy and FAQ
pages now 404 (the site moved under arkansas.com). Every entry keeps its own price.
Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CHECKED = "2026-10-20"
CAR = "https://codeofarrules.arkansas.gov/Rules/Rule?levelType=section&titleID=22&chapterID=195&subChapterID=240&partID=813&subPartID=6651&sectionID=43230 (22 CAR § 50-108)"
SITE = "https://reserve.arkansasstateparks.com/lake-catherine/camping/ (Camping Reservation Policies, the same block on every park)"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://reserve.arkansasstateparks.com/",
        "window_opens_days": 365,
        "min_stay": [
            {"nights": 2, "applies": "weekend"},
            {"nights": 3, "applies": "holiday", "season": "three-day holiday weekends (Memorial Day, Fourth of July when it makes one, Labor Day)"},
        ],
        "max_stay_nights": 14,
        "note": "Arkansas State Parks' own reservation site or 1-888-287-2757, up to 12 months before arrival. By rule every campsite is reservable, a specific site included; a site not reserved is rented at the park office, and an after-hours arrival takes an open site and registers by 10 a.m. A single night is fine Sunday-Thursday; a weekend takes Friday and Saturday, and a one-night Friday or Saturday is not considered until a week out (holiday weekends excepted). Three-day holiday weekends take 3 nights. Up to 20% of a park's high-demand sites carry 3 nights on weekends (Thursday-Saturday) and 4 on holiday weekends, released on Fridays if unreserved. STAY LIMIT: 14 nights in any 30-day period at one park; the superintendent may grant 7-day extensions April-October when the campground isn't full, and longer ones November-March. Check-in and check-out are both 3 p.m. A reserved site is held until 10 a.m. the morning after the arrival date. Eight people and one camping unit a site (an RV and one tent, or two tents); an adult must register and stay for the whole period. CANCELLING: the deposit (the first night at the full rate, plus tax) is never refunded, and no refund is made for leaving early from a holiday weekend; moving the arrival date means a new reservation and a lost deposit, though nights can be added at either end.",
    },
    "fees": {
        "currency": "USD",
        "checked": "2026",
        "note": "Each entry carries its own price; nightly rates vary by site, date and demand, plus tax and a reservation fee whose amount the site doesn't state. The non-refundable deposit is the first night's full rate plus tax, and the balance is paid on arrival. Discounts, with proof at check-in: Arkansas residents 62 and over pay half Sunday-Thursday and 25% less on weekends and holidays; out-of-state 62 and over pay 25% less Sunday-Thursday only; U.S. citizens with a 100% total and permanent disability pay half year-round.",
    },
    "provenance": {
        "booking": {"source": f"{CAR}; {SITE}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{SITE}; {CAR}", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    print("state:AR", "replaces an existing row" if "state:AR" in reg else "is new")
    if "--apply" in sys.argv:
        reg["state:AR"] = ROW
        with open(REG, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
