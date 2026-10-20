#!/usr/bin/env python3
"""Nevada State Parks in the policy registry (2026-10-20).

    python3 -I audit/nv_registry/apply.py [--apply]

The row is Nevada State Parks' reservations page (ReserveNevada) plus NAC 407.080, the
camping rule: 14 days in any 30, unless the park's own section sets less. Six parks' sections do
(7 days in 30): Cave Lake (407.225), Dayton (407.240), Fort Churchill (407.270), Kershaw-Ryan
(407.285), Spring Valley (407.340) and Washoe Lake (407.370). Their entries get
`max_stay_nights: 7`, the booking group's provenance becoming manual and naming both sources.
Dave Deacon Campground (11202) is NDOW's, not a state park: `policy_ref: none`. Every entry keeps
its own price, hookup charge and non-resident surcharge.

ReserveNevada's own catalog (nevadardr.usedirect.com rdr/search/grid, each unit's
AllowWebBooking, read 2026-10-20) contradicted six note-derived bookings: every individual site at
Beaver Dam (30), Cave Lake's Elk Flat (16) and Lake View (18), Rye Patch (61), and Valley of Fire's
Arch Rock (29) and Atlatl Rock (44) is web-bookable, and 20 of Fort Churchill's 21 are, though its
note said "not reservable". Those take `{reservable: true}` (the row's after-cutoff first-come
rule applying) and their notes are corrected. Kershaw-Ryan's primitive sites and Lahontan's
dispersed areas really are unbookable, so their `some_sites` stands; so does Big Horn's
`reservable: false` (0 of 16 bookable). Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
RES = "https://parks.nv.gov/about/reservations"
NAC = "https://www.leg.state.nv.us/NAC/NAC-407.html"
NONE = {11202}
CATALOG = "ReserveNevada unit catalog (https://nevadardr.usedirect.com/NevadaRDR/rdr/search/grid, AllowWebBooking per unit)"
FIX = {
    11192: [("Individual sites first-come, first-served (group site reservable).",
             "All 30 sites in Campgrounds A and B are reservable on ReserveNevada; first come, first served from November 1.")],
    11195: [("Individual sites first-come, first-served; group area reservable.", "All 18 sites reservable on ReserveNevada.")],
    11197: [("Individual sites first-come, first-served; group area reservable.", "All 16 sites reservable on ReserveNevada.")],
    11201: [("Reservable online; many sites first-come, first-served.",
             "All 61 sites in the Lower and Upper campgrounds are reservable on ReserveNevada.")],
    11204: [("first-come, first-served with reservations available for the park via ReserveNevada.",
             "all 29 sites reservable on ReserveNevada.")],
    11205: [],
    11209: [("Samuel Buckland Campground has 20 first-come, first-served sites", "Samuel Buckland Campground has 20 reservable sites"),
            (" First-come, first-served -- not reservable.", "")],
}
SEVEN = {11195: "407.225", 11197: "407.225", 11194: "407.240", 11209: "407.270",
         11193: "407.285", 11208: "407.340", 11203: "407.370"}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "operator",
        "url": "https://www.reservenevada.com/",
        "window_opens_days": 335,
        "reserve_until": {"relative_to": "arrival", "offset_hours": -72},
        "fcfs": "after_cutoff",
        "max_stay_nights": 14,
        "note": "ReserveNevada (Nevada State Parks' own system since September 2023): 'Visitors may make reservations from 3 days to 11 months in advance', the window rolling at 8 a.m. Pacific. A reservable site not reserved is sold first come, one night at a time; first-come campers may extend with park staff. No minimum stay. STAY LIMIT (NAC 407.080): 14 days in any 30, less where a park's own rule says so; 14 days in 30 in the Western region bars camping at any Western-region park for the rest of the period. Check-in 2 p.m., check-out 11 a.m.; two vehicles or eight people a site; a site may not be left empty overnight without the supervisor's permission. A reserved site is held until check-in time the day after arrival, then cancelled without refund unless the park was told. CHANGES AND CANCELLING (up to 3 days before arrival): a change costs $5 more than a month out and $10 within a month; a cancellation is free (bar the $5 fee) more than a month out, $10 within a month, and $10 plus one night within 3 days. No refunds for weather, smoke, bugs, fire bans or early departure.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 5,
        "checked": "2026",
        "note": "Each entry carries its own price, hookup charge and non-resident surcharge. The $5 transaction fee is per reservation and non-refundable. Disabled-placard holders and active military and veterans get $1 off the daily entrance fee; no camping discount is published.",
    },
    "provenance": {
        "booking": {"source": f"{RES}; {NAC} (NAC 407.080)", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{RES}; https://parks.nv.gov/fees/discounts-special-fees", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:NV", "replaces an existing row" if "state:NV" in reg else "is new")
    seen = set()
    for e in cg:
        if e["id"] in NONE:
            assert e["state"] == "NV" and e["ownership"] == "state", e["id"]
            e["policy_ref"] = "none"; seen.add(e["id"])
            print("policy_ref none:", e["id"], e["name"])
        if e["id"] in FIX:
            for old, new in FIX[e["id"]]:
                if old in e["note"]:
                    e["note"] = e["note"].replace(old, new)
                else:
                    assert old not in e["note"] and (not new or new in e["note"]), (e["id"], old)
            e["booking"] = {"reservable": True}
            seen.add(e["id"])
        if e["id"] in SEVEN:
            assert e["state"] == "NV", e["id"]
            e["booking"]["max_stay_nights"] = 7
            seen.add(e["id"])
        if e["id"] in FIX or e["id"] in SEVEN:
            prev = e["provenance"]["booking"]
            src = prev["source"] if prev["method"] == "manual" else f"note prose (checked {prev['checked']})"
            if e["id"] in FIX and "ReserveNevada unit catalog" not in src:
                src = f"{CATALOG}"
            if e["id"] in SEVEN and "NAC " not in src:
                src += f"; max_stay_nights: {NAC} (NAC {SEVEN[e['id']]}, 7 days in 30)"
            e["provenance"]["booking"] = {"source": src, "checked": CHECKED, "method": "manual"}
            print("booking:", e["id"], e["name"], e["booking"])
    assert seen == NONE | set(SEVEN) | set(FIX)
    if "--apply" in sys.argv:
        reg["state:NV"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
