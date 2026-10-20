#!/usr/bin/env python3
"""Parks NB (New Brunswick provincial parks) in the policy registry (2026-10-20).

    python3 -I audit/nb_registry/apply.py [--apply]

All 9 NB `provincial` entries are Parks NB campgrounds booked on reservations.parcsnbparks.ca (a
Camis/goingtocamp site). The row is Parks NB's published policies (About Us, Policy #4:
Reservation Policy). No booking window or general stay limit is published there, so the row
carries neither. Two entries lose a note-derived `platform: operator`. Every entry keeps its own
price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
POL = "https://www.parcsnbparks.ca/en/about-us#policies"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "goingtocamp",
        "url": "https://reservations.parcsnbparks.ca/",
        "reserve_until": {"relative_to": "arrival", "at": "20:00"},
        "fcfs": "some_sites",
        "note": "reservations.parcsnbparks.ca, 1-800-561-0123, or at the park in season, until 8 p.m. Atlantic on the arrival day. At least 95% of each campground's sites are reservable; the rest are first come, on site, for up to 7 nights. Check-in 2 p.m., check-out noon; the booking is in the name of someone staying on the site, 16 or older (19 to supervise younger campers); six people (more for families) and one RV or tent a site. A reservation is held until noon the day after arrival, then cancelled as a no-show and charged in full. CHANGES $8 (extending a stay is free); a new arrival date after 11:59 p.m. two days before arrival costs one night. CANCELLING: until 11:59 p.m. two days before arrival, an $8 fee; after that, one night (no $8 fee).",
    },
    "fees": {
        "currency": "CAD",
        "reservation_fee": 10,
        "checked": "2026",
        "note": "Each entry carries its own price, plus 15% HST. The $10 reservation fee is per reservation and non-refundable; a change or a timely cancellation is $8.",
    },
    "provenance": {
        "booking": {"source": f"{POL} (Policy #4: Reservation Policy)", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{POL} (Policy #4)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("provincial:NB", "replaces an existing row" if "provincial:NB" in reg else "is new")
    n = 0
    for e in cg:
        if e.get("state") == "NB" and e.get("ownership") == "provincial":
            b = e.get("booking") or {}
            if b.get("platform") == "operator":
                assert e["provenance"]["booking"]["method"] == "derived", e["id"]
                del b["platform"]; n += 1
    print("operator platform removed from", n)
    if "--apply" in sys.argv:
        reg["provincial:NB"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
