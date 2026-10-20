#!/usr/bin/env python3
"""Nova Scotia Parks in the policy registry (2026-10-20).

    python3 -I audit/ns_registry/apply.py [--apply]

All 19 NS `provincial` entries are Nova Scotia Parks camping parks booked on
novascotia.goingtocamp.com (Camis). Sources: Nova Scotia Parks' Make a Reservation page, its 2026
Camping Fees list and its Rules & Regulations summary of the Parks Act regulations. The fee list
is the price authority ($8.95 reservation, $6.95 to cancel or change); the reservation page rounds
them to $9 and $7. The season opens for booking all at once each spring rather than on a rolling
window, so the row carries no `window_opens_days`.

Twelve entries carried a note-derived `platform: operator` and Whycocomagh a derived
`fcfs: some_sites` read from "walk-ups accepted" (a vacant site goes to whoever arrives; no site is
held back from booking). Both are removed so the row's goingtocamp platform applies. Every entry
keeps its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
RES = "https://parks.novascotia.ca/make-reservation"
FEES = "https://parks.novascotia.ca/camping-fees"
RULES = "https://parks.novascotia.ca/rules-regulations"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "goingtocamp",
        "url": "https://novascotia.goingtocamp.com/",
        "max_stay_nights": 14,
        "note": "Nova Scotia Parks book on novascotia.goingtocamp.com or 1-888-544-3434 (519-826-5301 from outside North America); the season opens for booking all at once in spring, and the site offers cancellation alerts and a flexible-dates search up to four months out. A vacant site can be taken on arrival: at the park office at full-service parks, or by the yellow phone at the kiosk at self-registration parks (no reservation fee for a stay that starts that day). STAY LIMIT: a camping permit runs up to 14 nights on one site and lapses if the site is empty 48 hours. Check-in 2 p.m., check-out 1 p.m.; the permit holder is 19 or older and staying on the site, and a reservation can't be handed to someone else at arrival. Six people (more if one family) and one vehicle a permit. Arriving after midnight, camp one night on any vacant site and register at 9 a.m. CANCELLING: up to 2 p.m. on the arrival date, everything back but the reservation and cancellation fees.",
    },
    "fees": {
        "currency": "CAD",
        "reservation_fee": 8.95,
        "checked": "2026",
        "note": "Each entry carries its own price (taxes included). The $8.95 reservation fee is per reservation and non-refundable; cancelling or changing costs $6.95. An extra vehicle is $8.25 a night. Seniors 65 and over and veterans (3 years' honourable service) get $2.35 a night off.",
    },
    "provenance": {
        "booking": {"source": f"{RES}; {RULES}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{FEES} (2026 prices)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("provincial:NS", "replaces an existing row" if "provincial:NS" in reg else "is new")
    n = 0
    for e in cg:
        if e.get("state") == "NS" and e.get("ownership") == "provincial":
            b = e.get("booking") or {}
            for k in ("platform", "fcfs"):
                if k in b:
                    assert e["provenance"]["booking"]["method"] == "derived", e["id"]
                    print("drop", k, b[k], e["id"], e["name"]); del b[k]; n += 1
    print(n, "derived values removed")
    if "--apply" in sys.argv:
        reg["provincial:NS"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
