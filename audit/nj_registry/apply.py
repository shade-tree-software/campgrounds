#!/usr/bin/env python3
"""New Jersey State Park Service in the policy registry (2026-10-20).

    python3 -I audit/nj_registry/apply.py [--apply]

All 15 NJ `state` entries are State Park Service campgrounds booked on NJ Outdoors (the state's
own system on njportal.com). dep.nj.gov sits behind an Incapsula bot wall, so the row comes from
the rules themselves, N.J.A.C. 7:2 (via the Cornell LII copy): 6.7 (11 months ahead, 2-night
minimum, 14-night maximum, same-night bookings by phone 8-4, at most two non-consecutive
reservations at once), 6.8 (24 hours' notice for a refund) and 17.2 (cancellation fee; resident
62+ / totally disabled discount). No reservation fee is set by rule, and none was read off NJ
Outdoors, so `reservation_fee` stays absent (unknown).

Every entry already carries its own booking note and the 2-night minimum (AWH-confirmed on NJ
Outdoors 2026-10-10); those stay, and win over the row's note. The row adds the window and the
stay limit. Every entry keeps its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
LII = "https://www.law.cornell.edu/regulations/new-jersey/"
SRC = f"N.J.A.C. 7:2-6.7, 7:2-6.8 and 7:2-17.2 ({LII}N-J-A-C-7-2-6-7, -6-8, -17-2)"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://www.njportal.com/DEP/NJOutdoors",
        "window_opens_days": 335,
        "min_stay": [{"nights": 2, "applies": "always"}],
        "max_stay_nights": 14,
        "note": "NJ Outdoors, the state's own booking site, up to 11 months ahead (N.J.A.C. 7:2-6.7). A campsite is reserved for at least 2 consecutive nights and at most 14; a same-night booking is taken by phone, 8 a.m.-4 p.m. A person or family may hold at most two non-consecutive camping reservations at once. CANCELLING (7:2-6.8, 17.2): a refund needs at least 24 hours' notice, less a cancellation fee of $40 or two nights, whichever is less ($50 or two nights for non-residents).",
    },
    "fees": {
        "currency": "USD",
        "checked": "2026",
        "note": "Each entry carries its own resident and non-resident price. Cancelling costs $40 or two nights, whichever is less ($50 for non-residents). New Jersey residents 62 and over, or totally disabled, get $2 a night off family campsites.",
    },
    "provenance": {
        "booking": {"source": SRC, "checked": CHECKED, "method": "manual"},
        "fees": {"source": SRC, "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    print("state:NJ", "replaces an existing row" if "state:NJ" in reg else "is new")
    if "--apply" in sys.argv:
        reg["state:NJ"] = ROW
        with open(REG, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
