#!/usr/bin/env python3
"""Mississippi State Parks in the policy registry (2026-10-20).

    python3 -I audit/ms_registry/apply.py [--apply]

The row is 40 Miss. Admin. Code Part 6, Rule 1.2 (rev. 2023), which beats the parks' own
pages where they differ (Tishomingo's says 12 months; the rule says 13). Bookings run on
reserve.mdwfp.com, a Camis site (the goingtocamp engine); its /api/resourceLocation catalog
lists all 20 MDWFP parks with campgrounds.

Not covered by the row (`policy_ref: none`): MDWFP's State Fishing Lakes, a separate permit
program ($18/day, first come or by phone, none on the reservation site); Grand Gulf Military
Monument Park (its own commission); John W. Starr Memorial Forest RV Park (Mississippi State
University).

Corrections made while reading:
  * Natchez, Buccaneer and Wall Doxey said "ReserveAmerica"; Holmes County, LeFleur's Bluff and
    Legion said "operator". All note-derived; MDWFP left ReserveAmerica, and every park now
    inherits the reservation site from the row.
  * Golden Memorial (5002): MDWFP's park page: "managed as a day use park only." Marked closed
    with a dated caveat; dropping it is an ask (audit/registry_asks_2026-10-20.md).
  * Holmes County (5004): gone from MDWFP's park list (its page 404s) and from the booking
    catalog; listed as closed for renovations with its lakes closed. Marked closed; also an ask.
Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
RULE = "https://mdwfp.com/sites/default/files/2024-04/40-miss-admin-code-part-6-rule-12-rules-and-regulations-for-state-parks-rev-3-2023-final-april.pdf (40 Miss. Admin. Code Part 6, Rule 1.2, sections A, C, F, G)"
CATALOG = "https://reserve.mdwfp.com/api/resourceLocation"
NONE = {4999, 5008, 5009, 5010, 5011, 5014, 5015, 5016, 5017, 5018, 5019, 5026, 5075,  # State Fishing Lakes
        5003,   # Grand Gulf Military Monument Park
        13445}  # John W. Starr Memorial Forest RV Park (MSU)
DROP_PLATFORM = {4997, 4998, 5030, 5004, 5020, 5021}
NOTE_FIXES = {
    4997: ("Reservable online via ReserveAmerica.", "Reservable online through MDWFP's reservation site."),
    4998: ("Reservable online via ReserveAmerica.", "Reservable online through MDWFP's reservation site."),
    5030: ("Reservable online via ReserveAmerica (MS state parks).", "Reservable online through MDWFP's reservation site."),
    5021: ("Reservable online (MDWFP reservation system) or by phone up to 12 months ahead.",
           "Reservable online through MDWFP's reservation site or by phone."),
    5002: ("Day entrance $2/person.",
           "Day entrance $2/person. CAVEAT 2026-10-20: MDWFP's park page now says the park \"is managed as a day use park only\", with questions to Roosevelt State Park (601-732-6316); no overnight camping."),
    5004: ("Reservable online via the MS State Parks system.",
           "CAVEAT 2026-10-20: the park is gone from MDWFP's list of state parks (its page returns not-found) and from the state reservation site, and is listed as closed for renovations with its lakes closed to fishing; call (662) 653-3351 before relying on it."),
}
STATUS = {
    5002: {"operating": "temporarily_closed", "note": "MDWFP manages it as a day-use park only; no overnight camping (2026-10-20)"},
    5004: {"operating": "temporarily_closed", "note": "closed for renovations; off MDWFP's park list and reservation site (2026-10-20)"},
}
STATUS_SRC = {
    5002: "https://www.mdwfp.com/parks-destinations/park/golden-memorial-state-park",
    5004: f"https://www.mdwfp.com/parks-destinations (no Holmes County); {CATALOG} (absent)",
}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "goingtocamp",
        "url": "https://reserve.mdwfp.com/",
        "window_opens_days": 395,
        "fcfs": "some_sites",
        "min_stay": [
            {"nights": 2, "applies": "weekend", "season": "May 15 - Aug 15"},
            {"nights": 3, "applies": "holiday", "season": "Memorial Day, Independence Day, Labor Day, and special events"},
            {"nights": 2, "applies": "holiday", "season": "Thanksgiving, Christmas, New Year's, Easter"},
        ],
        "max_stay_nights": 14,
        "note": "MDWFP's own reservation site (reserve.mdwfp.com, a Camis system), the call center (1-800-GO-PARKS) or the park office 8 a.m.-5 p.m. 'Reservations are not required but are highly recommended especially during the peak season (May 15 through August 15)'; they are taken for 1-14 days, up to 13 months ahead, paid in full at booking. Primitive sites are not reservable. MINIMUMS: May 15-August 15, 2 nights on weekends and none on weeknights; 3 nights for Memorial Day, Independence Day, Labor Day and special events (special events carry 3 all year); 2 for Thanksgiving, Christmas, New Year's and Easter. A reserved site is released at 11 a.m. the morning after the arrival date unless the park has been told of a late arrival. STAY LIMIT: 14 days on a campsite; some parks rent designated sites by the month, up to 90 days. Check-in 4 p.m., check-out 2 p.m. Eight people and one camping unit a site (a second tent with the manager's approval, at the primitive rate); renters must be 21 or older, and the reservation holder must stay for the whole visit. CANCELLING: 7 or more days out, refunded minus the $8 reservation fee; 6 days or less, half the reservation is forfeited; within 3 days or a no-show, nothing back. Date or site changes are free up to 7 days out ($8 inside that), none within 3 days.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 8,
        "checked": "2026",
        "note": "Each entry carries its own price. The $8 reservation fee is non-refundable; changing the dates or site inside the 7-day window costs another $8. Park entrance is $2 a person (5 and under free) on the park pages; an RV site's rental covers fishing and the boat launch for the people registered on it, and their visitors pay entrance.",
    },
    "provenance": {
        "booking": {"source": f"{RULE}; {CATALOG}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{RULE}; https://www.mdwfp.com/parks-destinations/park/tishomingo-state-park (entrance fee)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:MS", "replaces an existing row" if "state:MS" in reg else "is new")
    seen = set()
    for e in cg:
        i = e["id"]
        if i in NONE:
            assert e["state"] == "MS" and e["ownership"] == "state", i
            e["policy_ref"] = "none"; seen.add(i)
            print("policy_ref none:", i, e["name"])
        if i in DROP_PLATFORM and (e.get("booking") or {}).get("platform"):
            assert e["provenance"]["booking"]["method"] == "derived", i
            print("own platform removed:", i, e["name"], e["booking"].pop("platform"))
        if i in NOTE_FIXES:
            old, new = NOTE_FIXES[i]
            if old in e["note"]:
                e["note"] = e["note"].replace(old, new); print("note fixed:", i)
        if i in STATUS:
            e["status"] = STATUS[i]
            e.setdefault("provenance", {})["status"] = {"source": STATUS_SRC[i], "checked": CHECKED, "method": "manual"}
            print("status closed:", i, e["name"])
    assert seen == NONE, NONE - seen
    if "--apply" in sys.argv:
        reg["state:MS"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
