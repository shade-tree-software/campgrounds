#!/usr/bin/env python3
"""Connecticut State Parks in the policy registry (2026-10-20).

    python3 -I audit/ct_registry/apply.py [--apply]

All 15 CT `state` entries are DEEP State Parks and Forests campgrounds, booked on ReserveAmerica.
The row is DEEP's camping page (ctparks.com/camping: reservation window, length of stay,
cancellations, campground rules). DEEP names its own exceptions, and they go on the entries
(booking provenance becoming manual and citing the same page):
  * 21 consecutive days instead of 14 at Hammonasset Beach (212) and Rocky Neck (4051);
  * reservations close 48 hours before arrival, not one day, at Macedonia Brook (4058) and
    Mashamoquet Brook's two campgrounds (4060, 4061), and Macedonia's 2-night minimum is never
    waived for a late booking;
  * no walk-ins at Devil's Hopyard (4052), Pachaug's Green Falls (4053) and Mount Misery (4054),
    Mashamoquet (4060, 4061) and Macedonia (4058).
Every entry keeps its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
CAMP = "https://ctparks.com/camping"
NO_WALKIN = {"fcfs": "never"}
CLOSE48 = {"reserve_until": {"relative_to": "arrival", "offset_hours": -48}}
OVR = {
    212: {"max_stay_nights": 21},
    4051: {"max_stay_nights": 21},
    4052: NO_WALKIN, 4053: NO_WALKIN, 4054: NO_WALKIN,
    4058: {**NO_WALKIN, **CLOSE48, "min_stay": [{"nights": 2, "applies": "always"}]},
    4060: {**NO_WALKIN, **CLOSE48},
    4061: {**NO_WALKIN, **CLOSE48},
}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://connecticutstateparks.reserveamerica.com/",
        "window_opens_days": 335,
        "reserve_until": {"relative_to": "arrival", "offset_hours": -24},
        "fcfs": "after_cutoff",
        "min_stay": [{"nights": 2, "applies": "always", "waived_if": {"booking_within_days": 3}}],
        "max_stay_nights": 14,
        "note": "ReserveAmerica, online or 1-877-668-2267, 11 months ahead and up to the day before arrival (48 hours before at Macedonia Brook and Mashamoquet Brook). MINIMUM: 2 nights, except that a reservation made 1-3 days before arrival may be one night (never at Macedonia Brook). STAY LIMIT: 14 consecutive days inland, 21 at Hammonasset Beach and Rocky Neck; between stays the whole party and its equipment leave the campground for 5 days, so an RV can't be left for back-to-back reservations. An unreserved site may be taken as a walk-in ($3 walk-in fee) except at Devil's Hopyard, Pachaug's Mount Misery and Green Falls, Mashamoquet Brook (with Wolf Den) and Macedonia Brook. Check-in 1 p.m., check-out noon; two vehicles a site; the primary occupant, who can't be changed, must be at check-in and be 18. Changes before check-in, $9; none within two days of arrival. CANCELLING (through ReserveAmerica only): more than 7 days out, everything back but the $9 reservation fee; 2-7 days, less the fee and one night; under 2 days, no refund. A $9 cancellation fee also comes off every refund.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 9,
        "checked": "2026",
        "note": "Each entry carries its own resident and non-resident price. The $9 reservation fee is per reservation; changing or cancelling costs another $9. A walk-in pays a $3 walk-in fee.",
    },
    "provenance": {
        "booking": {"source": CAMP, "checked": CHECKED, "method": "manual"},
        "fees": {"source": CAMP, "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:CT", "replaces an existing row" if "state:CT" in reg else "is new")
    seen = set()
    for e in cg:
        if e["id"] in OVR:
            assert e["state"] == "CT" and e["ownership"] == "state", e["id"]
            b = e.get("booking") or {}
            b.update(json.loads(json.dumps(OVR[e["id"]])))
            e["booking"] = b
            e.setdefault("provenance", {})["booking"] = {"source": CAMP, "checked": CHECKED, "method": "manual"}
            seen.add(e["id"]); print(e["id"], e["name"], b)
    assert seen == set(OVR)
    if "--apply" in sys.argv:
        reg["state:CT"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
