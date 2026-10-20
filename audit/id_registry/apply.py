#!/usr/bin/env python3
"""Idaho State Parks in the policy registry (2026-10-20).

    python3 -I audit/id_registry/apply.py [--apply]

All 25 ID `state` entries are Idaho Department of Parks and Recreation campgrounds (Smoky
Mountain at Castle Rocks SP included; its website is the NPS City of Rocks page, but IDPR runs
it). The rule is IDAPA 26.01.20 (sections 250-276), which beats IDPR's own pages where they
differ: the camping page says both "14 nights in a 30-day period" and "15 days in any 30-day
period", and lists a "$9 Reservation Fee" beside a "$10 non-refundable Transaction Fee"; the rule
says 15 days in 30 and a $10 reservation service charge per site. IDPR's reservation system
moved off ReserveAmerica to its own (getoutside.idaho.gov), so nine entries lose a note-derived
`platform: reserveamerica`, and their notes say who books them. Every entry keeps its own price, non-resident surcharge and entrance
fee. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
IDAPA = "https://adminrules.idaho.gov/rules/current/26/260120.pdf (IDAPA 26.01.20, sections 250, 256, 276)"
RES = "https://parksandrecreation.idaho.gov/reservations/"
CAMP = "https://parksandrecreation.idaho.gov/camping/"

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://getoutside.idaho.gov/",
        "window_opens_days": 274,
        "max_stay_nights": 15,
        "note": "IDPR's own reservation system (getoutside.idaho.gov) or 1-888-922-6743, on a rolling 9-month window, same-day bookings included. A multi-night stay booked on the first day of the window whose departure runs past it is frozen for 18 days (no changes or cancelling). STAY LIMIT (IDAPA 26.01.20.250): 15 days in any 30 consecutive days, reserved or first come; the operations administrator may set shorter or longer limits for an area. Check-in 2 p.m., check-out 1 p.m. (park time). Eight people and one RV plus up to two tents a site; one vehicle is included, others pay the $7 entrance fee. A reserved site is held until check-out time the day after arrival, then cancelled with all fees forfeited. CANCELLING (IDAPA 26.01.20.276): $10 a site before check-in time on the arrival day; after it, the first night. The reservation charge is never refunded. Changing dates so no night overlaps is a cancellation and rebooking.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 10,
        "checked": "2026",
        "note": "Each entry carries its own price, non-resident surcharge and $7 motor vehicle entrance fee; IDPR prices sites by demand within statewide ranges. The $10 reservation service charge is per site and non-refundable, and is waived for a camper with a current Idaho RV registration sticker; paying by card adds 3%. Discounts: 62 and over, 50% off Monday-Thursday stays (not holidays) at select parks; Idaho veterans rated 100% permanently and totally disabled get free entrance and one free campsite per stay.",
    },
    "provenance": {
        "booking": {"source": f"{IDAPA}; {RES}; {CAMP}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{IDAPA}; {CAMP}", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:ID", "replaces an existing row" if "state:ID" in reg else "is new")
    n = 0
    for e in cg:
        if e.get("state") == "ID" and e.get("ownership") == "state":
            b = e.get("booking") or {}
            if b.get("platform") == "reserveamerica":
                assert e["provenance"]["booking"]["method"] == "derived", e["id"]
                del b["platform"]; n += 1
            for old, new in (("Reservable through Idaho State Parks (ReserveAmerica)", "Reservable through Idaho State Parks"),
                             ("Reservable via ReserveAmerica", "Reservable through Idaho State Parks")):
                e["note"] = e["note"].replace(old, new)
            assert "ReserveAmerica" not in e["note"], e["id"]
    print("reserveamerica platform removed from", n, "entries")
    if "--apply" in sys.argv:
        reg["state:ID"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
