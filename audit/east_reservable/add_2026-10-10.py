#!/usr/bin/env python3
"""Eastern reservable designated-site gap (AWH 2026-10-10): the three that qualify.

Surveyed after the PA state-forest pass (audit/pa_sf_dispersed/): which other eastern
agencies book individually designated primitive sites online?
- NY DEC: Stoney Pond State Forest is the one property on ReserveAmerica (17 sites);
  the other DEC primitive sites are first-come (Hunts Pond, Sugar Hill already in).
- SFWMD (FL): RV/travel-trailer camping only at DuPuis, Istokpoga (already in),
  Town of KICCO, and two equestrian camps (out: horse camps).
- SWFWMD: primitive sites are tent + personal vehicle only; trailers only at
  equestrian camps -> none qualify.  SJRWMD: RVs/trailers prohibited.
- SRWMD: individual drive-in camping only at Goose Pasture, not reservable.
- MD state forests: already in (Savage River's reservable areas included).
- OH state forests: reservations only at a horse camp and park-and-pack sites.

    python3 audit/east_reservable/add_2026-10-10.py [--dry-run]
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

D = "2026-10-10"
RA_SP = "https://newyorkstateparks.reserveamerica.com/campsiteDetails.do?contractCode=NY&parkId=2424"
SFWMD_FAQ = "https://www.sfwmd.gov/sites/default/files/SUL_FAQs_1-30-20.pdf"
SUL = "https://www.sfwmd.gov/community-residents/recreation/sul"

ENTRIES = [
 dict(
  entry={"name": "Stoney Pond State Forest Camping Area (sites 10, 12-15)", "location": "42.8813,-75.7170",
   "elevation_meters": 496.0, "state": "NY", "ownership": "state",
   "waterfront": "not waterfront",
   "waterfront_evidence": "DEC Stoney Pond Campground map + Esri satellite 2026-10-10: the 30-ft sites (12-15 on the west spur north of Stoney Pond Rd, 10 south of it) sit in a white-pine plantation roughly 300+ m from the pond's south shore; sites 3-5 near the pond are 20-ft only. Under canopy, default down",
   "inclusion_evidence": f"ReserveAmerica campsiteDetails (NY parkId 2424, read {D}): 17 sites; sites 010, 012, 013, 014, 015 Drive-In, Back-In, Max Vehicle Length 30 ft (001-009 are 20 ft, 011 unstated, 016-017 Hike-In) -> a 23-ft trailer fits 5 sites. DEC property page: 17 designated sites by permit, reserved online only (ReserveAmerica / NY State Parks) May 1-Sep 30, first-come Oct 1-Apr 30; 'one camping trailer ... plus two vehicles per site'; free",
   "website": "https://dec.ny.gov/places/stoney-pond-state-forest\nhttps://newyorkstateparks.reserveamerica.com/campgroundDetails.do?contractCode=NY&parkId=2424",
   "phone": "800-456-2267",
   "note": "NY DEC designated campsites in a white-pine plantation at the south end of Stoney Pond, near Nelson (Madison Co). Only sites 10 and 12-15 take a vehicle up to 30 ft (the other drive-in sites are 20 ft). Free, but May 1-Sep 30 each site must be reserved online on ReserveAmerica (no phone or office bookings); first-come Oct-Apr. Fire rings, two portable toilets in season, no potable water, no hookups; 14 nights per calendar year. --Claude",
   "policy_ref": "none"},
  groups={"fees": {"nightly_low": 0, "nightly_high": 0, "currency": "USD", "note": "Free; May 1-Sep 30 a free reservation on ReserveAmerica is the camping permit."},
          "booking": {"reservable": True, "platform": "reserveamerica", "note": "Reservation required May 1-Sep 30 (online only, opens April 1); first-come, first-served Oct 1-Apr 30."},
          "hookups": {"electric": 0, "water": False, "sewer": False},
          "facilities": {"potable_water": False},
          "sites": {"count": 5, "max_rig_ft": 30, "pull_through": False}},
  prov={"fees": {"source": "https://dec.ny.gov/places/stoney-pond-state-forest ('Fee: Free'); DEC 2021-04-01 press release (camping free, no reservation fee)", "checked": D},
        "booking": {"source": "https://dec.ny.gov/places/stoney-pond-state-forest (permit May 1-Sep 30 via NY State Parks / ReserveAmerica only)", "checked": D},
        "hookups": {"source": "https://dec.ny.gov/places/stoney-pond-state-forest (fire ring per site, no potable water, portable toilets)", "checked": D},
        "facilities": {"source": "https://dec.ny.gov/places/stoney-pond-state-forest ('There is no potable water')", "checked": D},
        "sites": {"source": RA_SP + " (Max Vehicle Length, Driveway Entry Back-In)", "checked": D}}),
 dict(
  entry={"name": "DuPuis Campground (non-equestrian RV area, SFWMD)", "location": "27.00485,-80.55932",
   "elevation_meters": 11.0, "state": "FL", "ownership": "local",
   "waterfront": "not waterfront",
   "waterfront_evidence": "Esri satellite 2026-10-10: gravel campground loops with parked RVs/trailers in open pine/oak; the only water nearby is a small excavated retention pond south-east of the loops, not a frontage. Default down",
   "inclusion_evidence": f"SFWMD DuPuis Management Area page (read {D}): activities include 'Camping (RV/Travel Trailer)'; the DuPuis Equestrian Campground 'has been separated into two campgrounds; equestrian and non-equestrian' - non-equestrian campers use the second area; Gate 3 is 'equestrian and trailer camping'. SFWMD SUL FAQ (2020): RV/travel-trailer camping allowed here, no length limit, no hookups, the District's only dump station (registered campers). Booked with a free Special Use License online",
   "website": "https://www.sfwmd.gov/recreation-site/dupuis-management-area\n" + SUL,
   "phone": "866-433-6312",
   "note": "South Florida Water Management District campground at the DuPuis Management Area off SR-76 (Kanner Hwy) near Indiantown, Gate 3. The former equestrian campground is now split: campers without horses use the non-equestrian half. RVs and travel trailers of any length; no hookups, but a dump station for registered campers (the District's only one). Free, with a required free Special Use License reserved online in advance (gate combination on the license); 8 nights per visit, 30 per year District-wide. Generators until 11 pm. --Claude",
   "policy_ref": "none"},
  groups={"fees": {"nightly_low": 0, "nightly_high": 0, "currency": "USD", "note": "Free; a free Special Use License (online reservation) is required."},
          "booking": {"reservable": True, "platform": "operator", "fcfs": "never", "max_stay_nights": 8},
          "hookups": {"electric": 0, "water": False, "sewer": False},
          "facilities": {"dump": True}},
  prov={"fees": {"source": SUL + " ('Special Use Licenses can be obtained at no cost')", "checked": D},
        "booking": {"source": SFWMD_FAQ + " (up to 8 consecutive days per permit, 30 per year)", "checked": D},
        "hookups": {"source": SFWMD_FAQ + " ('There are no campsites that have any electric or water hook ups')", "checked": D},
        "facilities": {"source": SFWMD_FAQ + " ('The DuPuis Equestrian Campground is the only dump station ... available to only those registered ... overnight campers')", "checked": D}}),
 dict(
  entry={"name": "Town of KICCO Campsite (SFWMD, Kissimmee River)", "location": "27.6687,-81.1446",
   "elevation_meters": 18.0, "state": "FL", "ownership": "local",
   "waterfront": "riverfront",
   "waterfront_evidence": "Esri satellite 2026-10-10 (110 m and 250 m crops): an open grass clearing runs straight to the bank of the restored Kissimmee River oxbow (~40 m of open water), with an RV parked about 20 m from the water and no treeline between - open apron to the river. The FDEP Kissimmee River blueway guide places the campsite 'on river right along original river channel'",
   "inclusion_evidence": f"SFWMD SUL FAQ (2020): RV/travel-trailer camping allowed at 'the Town of KICCO Campsite', no length limit, no hookups; SFWMD camping-area layer (LR_CAMPING) types it RV/TRAVEL TRAILER, ALL ACCESS, SUL REQUIRED. Satellite shows RVs parked in the clearing. Caveat: the current SFWMD KICCO page tags only 'Camping (Tent)' (read {D})",
   "website": "https://www.sfwmd.gov/recreation-site/kicco-and-blanket-bay-slough\n" + SUL,
   "phone": "866-433-6312",
   "note": "Largest of the five primitive campsites in SFWMD's KICCO Wildlife Management Area, on the Kissimmee River off River Ranch Blvd, south of SR-60 between Lake Wales and Yeehaw Junction. Open grass clearing on the old river channel; picnic tables and fire rings, no hookups or water. Free, with a required free Special Use License reserved online (gate combination on the license); 8 nights per visit. Horses are also allowed here. The District's 2020 FAQ lists it for RVs/travel trailers (no length limit) but its current KICCO web page tags only tent camping - confirm when booking. --Claude",
   "policy_ref": "none"},
  groups={"fees": {"nightly_low": 0, "nightly_high": 0, "currency": "USD", "note": "Free; a free Special Use License (online reservation) is required."},
          "booking": {"reservable": True, "platform": "operator", "fcfs": "never", "max_stay_nights": 8},
          "hookups": {"electric": 0, "water": False, "sewer": False}},
  prov={"fees": {"source": SUL + " ('Special Use Licenses can be obtained at no cost')", "checked": D},
        "booking": {"source": SFWMD_FAQ + " (up to 8 consecutive days per permit)", "checked": D},
        "hookups": {"source": SFWMD_FAQ + " ('There are no campsites that have any electric or water hook ups')", "checked": D}}),
]

def main():
    dry = "--dry-run" in sys.argv
    path = os.path.join(ROOT, "campgrounds.json"); rows = json.load(open(path))
    fam = os.path.join(ROOT, "trip_data", "family.json")
    nid = max(r["id"] for r in rows + (json.load(open(fam)) if os.path.exists(fam) else [])) + 1
    added = []
    for x in ENTRIES:
        e = {"id": nid, "kind": "campground", **x["entry"]}
        cs.apply_update(e, {**x["groups"], cs.PROVENANCE: x["prov"]})
        cs.validate_row(e, e["name"]); added.append(e); nid += 1
    print(len(added), "entries, ids", added[0]["id"], "-", added[-1]["id"])
    if dry: return
    with open(path + ".tmp", "w") as fh:
        json.dump(rows + added, fh, indent=2, ensure_ascii=False); fh.write("\n")
    os.replace(path + ".tmp", path)

if __name__ == "__main__":
    main()
