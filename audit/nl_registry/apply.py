#!/usr/bin/env python3
"""ParksNL (Newfoundland and Labrador provincial parks) in the policy registry (2026-10-20).

    python3 -I audit/nl_registry/apply.py [--apply]

All 13 NL `provincial` entries are ParksNL campgrounds (some run by concessionaires, all booked
on the one ParksNL Campsite Reservation Service at nlcamping.ca, a Camis/goingtocamp site, and
all on the one fee page). Sources: ParksNL's Reservations page and its 2026 Provincial Park Rules
and Regulations (sections 4, 6 and 7). The reservation service opens for the whole season in
late April rather than on a rolling window, and there is no stay limit (seasonal sites are sold),
so the row carries neither. All 13 entries lose a note-derived `platform: operator`. Every entry
keeps its own price and vehicle pass. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
RES = "https://www.parksnl.ca/reservations/"
REGS = "https://www.parksnl.ca/files/Provincial-Park-Rules-and-Regs-2026.pdf"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "goingtocamp",
        "url": "https://www.nlcamping.ca/",
        "reserve_until": {"relative_to": "arrival", "at": "20:00"},
        "fcfs": "after_cutoff",
        "note": "The ParksNL Campsite Reservation Service (nlcamping.ca, or 1-877-214-2267 from 7 a.m. to 11:30 p.m.) usually opens in the third week of April for the whole season; same-day bookings until 8 p.m. Newfoundland time. Sites are sold by the night, the week, the month or the season. Any free site can be taken at the park checkpoint without a reservation, for up to 7 nights. Check-in 3 p.m., check-out 2 p.m.; the person reserving must be 16 and one occupant must be named; six people (more for one family) and one camping unit a site. CANCELLING a stay under 8 nights: free the day before arrival or earlier; on the arrival day (until 2 p.m. the next day), one night is kept; after that, a no-show with no refund. Stays of 8 nights or more: full refund 2 days out, 75% the day before, 50% on the arrival day. Changes $6, none within 3 days of arrival on a long stay.",
    },
    "fees": {
        "currency": "CAD",
        "reservation_fee": 7,
        "checked": "2026",
        "note": "Each entry carries its own price and vehicle pass ($7 a night per vehicle, or $50 for the season at every park). The $7 reservation fee (HST included) is per booking and non-refundable; a change is $6 and cancelling in time is free. Newfoundland and Labrador residents 65 and over get 35% off campsite and vehicle fees.",
    },
    "provenance": {
        "booking": {"source": f"{RES}; {REGS} (sections 4, 6, 7)", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{RES}; {REGS}", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("provincial:NL", "replaces an existing row" if "provincial:NL" in reg else "is new")
    n = 0
    for e in cg:
        if e.get("state") == "NL" and e.get("ownership") == "provincial":
            b = e.get("booking") or {}
            if b.get("platform") == "operator":
                assert e["provenance"]["booking"]["method"] == "derived", e["id"]
                del b["platform"]; n += 1
    print("operator platform removed from", n)
    if "--apply" in sys.argv:
        reg["provincial:NL"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
