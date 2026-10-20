#!/usr/bin/env python3
"""Second look at the state/provincial entries the 2026-10-12 pass left unpriced (2026-10-20).

    python3 -I audit/state_park_fees/followup_2026-10-20.py [--apply]

68 state/provincial entries had no price once registry rows are counted; nearly all were tried on
2026-10-12 and their reasons are in README.md. This pass only follows leads that pass never had.
Evidence quotes: followup_evidence_2026-10-20.json.

  15392 Switzer Halfway (AB)  added after that pass; its Alberta Parks page posts $30.
  11614 Bow Willow (CA)       Anza-Borrego's own fee schedule on parks.ca.gov prices its
                              first-come campgrounds ($20; seniors 62+ $18).
  6611  Raymond Gary (OK)     not on ReserveAmerica because the park books through its own
                              ReservationKey page: $25 water/electric, $30 full hookups, the
                              same on a Saturday and in November. The page's rate text ($22/$25)
                              is older than the prices the engine charges. Its own terms (pay on
                              arrival, 3-night weekend minimum, its cancellation rule) replace
                              the state:OK row's, so `policy_ref: none`.
  6621, 6626 Beaver Dunes (OK) a City of Beaver park since Oklahoma SCR 23 (2012) approved the
                              transfer: ownership local, names follow the park's ("Beaver Dunes
                              Park"), the stale ReserveAmerica claim and its derived booking go.
                              TravelOK's $25 is undated and not the city's own, so not priced.

Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CG = os.path.join(ROOT, "campgrounds.json")
DAY = "2026-10-20"
RK = "https://v2.reservationkey.com/RGSP/"
TRAVELOK_BD = "https://www.travelok.com/listings/view.profile/id.418"
SCR23 = "https://www.legiscan.com/OK/bill/SCR23/2012"

FEES = {
    15392: ({"nightly_low": 30, "nightly_high": 30, "currency": "CAD", "surcharges": {"weekend": 0}, "checked": "2026",
             "note": "A night: unserviced $30 (4 first-come sites), May 14 to September 7. Alberta seniors get the camping fee discount. The campground's Alberta Parks page, read 2026-10-20."},
            "https://www.albertaparks.ca/parks/central/william-a-switzer-pp/information-facilities/camping/halfway/ (the 'Camping' table), read 2026-10-20"),
    11614: ({"nightly_low": 20, "nightly_high": 20, "currency": "USD", "checked": "2026",
             "note": "$20 a night for a tent or RV site; seniors 62 and over $18, State Parks Disabled Discount Pass $10. Extra vehicle $10. First come, paid at the campground. Anza-Borrego Desert State Park's fee schedule, read 2026-10-20."},
            "https://www.parks.ca.gov/anzaborrego ('Anza-Borrego Desert State Park Fee Schedule': Bow Willow Campground), read 2026-10-20"),
    6611: ({"nightly_low": 25, "nightly_high": 30, "currency": "USD", "surcharges": {"full_hookup": 5, "weekend": 0}, "checked": "2026",
            "note": "A night: water and electric (lakeside) $25; full hookups (hilltop) $30, the same on a Saturday and in November. Pets $10 a night each. Discounts for seniors and the fully disabled, applied at the office. The park's booking page (ReservationKey; nights of 2026-11-03, 2027-06-15 and 2027-06-19), read 2026-10-20."},
           f"{RK} (each RV site's nightly price for 2026-11-03, 2027-06-15 and 2027-06-19), read 2026-10-20"),
}

RAYMOND_GARY = {
    "note": "Raymond Gary SP on a 370-acre lake near Fort Towson. 10 full-hookup and 9 water/electric RV sites (rigs to ~40 ft) plus ~100 tent sites; comfort stations/showers, swim beach, group pavilions; year-round. Books through the park's own reservation page (not Oklahoma State Parks' ReserveAmerica site) with payment at the office on arrival; 3-night minimum on weekends. --Claude",
    "website": "https://www.travelok.com/state-parks/raymond-gary-state-park\n" + RK,
    "phone": "580-406-4847",
    "booking": {"reservable": True, "platform": "operator", "url": RK,
                "min_stay": [{"nights": 3, "applies": "weekend"}],
                "note": "The park's own reservation page or 580-406-4847; payment is taken at the office on arrival. 3-night minimum on weekends for RV sites. RV check-in and check-out 2 p.m. Changes and cancellations are free up to 6 days before arrival; within 5 days, one night at the standard rate is charged, held as credit for a stay within a year."},
}

BEAVER_DUNES = {
    6621: ("Pioneer Campground - Beaver Dunes Park",
           "Pioneer Campground in Beaver Dunes Park, a City of Beaver park 1 mi N of Beaver (Oklahoma State Parks transferred it to the city; the legislature approved it in 2012), adjacent to the OHV sand-dune riding area. 13 drive-in RV sites with 20/30-amp electric and water, dump station, showers, plus tent sites. Not on ReserveAmerica; call the park. TravelOK's listing (undated, read 2026-10-20) gives $25 a night. --Claude"),
    6626: ("Hackberry Bend Campground - Beaver Dunes Park",
           "Hackberry Bend Campground in Beaver Dunes Park, a City of Beaver park 1 mi N of Beaver (Oklahoma State Parks transferred it to the city; the legislature approved it in 2012), a distinct loop ~0.4 mi from Pioneer near the park's two-acre lake and the sand dunes. 7 RV sites with 20/30/50-amp electric and water plus ~10 tent sites and a primitive cabin; dump station, showers. Not on ReserveAmerica; call the park. TravelOK's listing (undated, read 2026-10-20) gives $25 a night. --Claude"),
}

if __name__ == "__main__":
    cg = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in cg}
    if by[6611].get("policy_ref") == "none":
        sys.exit("already applied")
    for i, (fees, src) in FEES.items():
        e = by[i]
        assert (e.get("fees") or {}).get("nightly_low") is None, i
        e["fees"] = fees
        e.setdefault("provenance", {})["fees"] = {"source": src, "checked": DAY, "method": "manual"}
        print(i, e["name"], fees["nightly_low"], fees["nightly_high"])
    e = by[6611]
    assert "Reservable online via ReserveAmerica" in e["note"]
    e["note"], e["website"], e["phone"] = RAYMOND_GARY["note"], RAYMOND_GARY["website"], RAYMOND_GARY["phone"]
    e["booking"] = RAYMOND_GARY["booking"]
    e["provenance"]["booking"] = {"source": f"{RK} (the page's terms and each RV site's description), read 2026-10-20", "checked": DAY, "method": "manual"}
    e["policy_ref"] = "none"
    for i, (name, note) in BEAVER_DUNES.items():
        e = by[i]
        assert e["ownership"] == "state" and "Reservable online via ReserveAmerica" in e["note"], i
        e["name"], e["note"], e["ownership"], e["phone"] = name, note, "local", "580-808-1155"
        e.pop("booking", None)
        e["provenance"].pop("booking", None)
        tag = " | 2026-10-20: ownership state -> local. Beaver Dunes is a City of Beaver park"
        if tag not in e.get("inclusion_evidence", ""):
            e["inclusion_evidence"] = e.get("inclusion_evidence", "") + tag + f" (TravelOK {TRAVELOK_BD}; transfer approved by Oklahoma SCR 23, 2012, {SCR23}); not on okstateparks.reserveamerica.com."
        print(i, "->", name, "local")
    if "--apply" in sys.argv:
        with open(CG, "w", encoding="utf-8") as f:
            json.dump(cg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
