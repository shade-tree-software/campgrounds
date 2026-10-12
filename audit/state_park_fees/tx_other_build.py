"""Texas entries run by state agencies other than TPWD, each from its operator's own page or booking site, read
2026-10-12 (page text in tx_other_pages_2026-10-12.json; the two Lake Fayette parks from Campspot's availability for
Tue 2027-06-15 and Sat 2027-06-19).

    python3 -I tx_other_build.py OUT

- LCRA parks (lcraparks.com park pages): each site type's 'Starting at $N' a night, and 'Entrance Fees: Adults - $5;
  Seniors (65 and older), Military and Disabled - $2' a day. The six primitive parks' drive-up sites take tents or
  self-contained RVs (no hookups).
- Lake Fayette's Park Prairie and Oak Thicket (LCRA parks run by Vista Recreation): Campspot.
- Texas Historical Commission: Fort Griffin's and Mission Dolores' campground pages.
- Lavaca-Navidad River Authority (Brackenridge and Texana): the complex's camping rates page; 'All reservations will
  incur a $3.50 reservation fee'.
- Trinity River Authority (Wolf Creek): its park fees page, entrance '$5 per person/per night (ages 13 & older)'.
- Guadalupe-Blanco River Authority (Lake Wood): its park page, 'RV'S, TRAILERS, CAMPERS AND POP-UPS: $35.00 per vehicle
  per camping day', '$40.00 per day for vehicles using 50 AMP service'."""
import json, sys
D = "2026-10-12"
LCRA_ENT = {"resident": 5, "nonresident": 5, "per": "person_day"}
LCRA_NOTE = (" Plus the LCRA entrance fee, $5 a day per adult ($2 for seniors 65+, military and disabled visitors). "
             f"LCRA's park page ('Starting at'), read {D}.")


def lcra(eid, name, slug, low, text, high=None, sur=None):
    fees = {"nightly_low": low, "currency": "USD", "entrance": LCRA_ENT, "checked": "2026", "note": text + LCRA_NOTE}
    if high is not None:
        fees["nightly_high"] = high
    if sur:
        fees["surcharges"] = sur
    return {"id": eid, "name": name, "fees": fees,
            "source": f"https://lcraparks.com/parks/{slug} (site types 'Starting at', entrance fees), read {D}"}


PRIM = "Primitive drive-up campsites (tents or self-contained RVs, no hookups) from $25 a night"
out = [
    lcra(7021, "Camp Creek Park", "camp-creek-park", 25, PRIM + "; six deluxe campsites from $49."),
    lcra(7024, "Cedar Point Recreation Area", "cedar-point-recreation-area", 25, PRIM + "."),
    lcra(7043, "Grelle Recreation Area", "grelle-recreation-area", 25, PRIM + "; one large campsite (16 people) from $35."),
    lcra(7084, "Shaffer Bend Recreation Area", "shaffer-bend-recreation-area", 25, PRIM + "; one large campsite from $35."),
    lcra(7088, "Turkey Bend Recreation Area", "turkey-bend-recreation-area", 25, PRIM + "."),
    lcra(7282, "Muleshoe Bend Recreation Area", "muleshoe-bend-recreation-area", 25, PRIM + "; six large campsites from $35."),
    lcra(7145, "Matagorda Bay Nature Park", "matagorda-bay-nature-park", 45,
         "Full-hookup RV sites from $45 a night, pull-through full-hookup sites from $50, waterfront sites from $58.",
         sur={"premium_site": 13}),
    lcra(7400, "Black Rock Park", "black-rock-park", 40,
         "Full-hookup RV campsites from $40 a night (the park's other campsites from $25 have no hookups)."),
    lcra(7606, "Lake Bastrop North Shore Park", "lake-bastrop-north-shore-park", 40, "RV sites from $40 a night."),
    lcra(7811, "Lake Bastrop South Shore Park", "lake-bastrop-south-shore-park", 35,
         "RV sites with water and electric from $35 a night, full hookups from $40.", sur={"full_hookup": 5}),
    {"id": 7135, "name": "Lake Fayette Park Prairie Park", "fees": {
        "nightly_low": 38, "nightly_high": 38, "currency": "USD", "surcharges": {"premium_site": 20, "weekend": 3},
        "checked": "2026",
        "note": ("Non-waterfront water-and-electric RV sites (to 45 ft) $38 a night, $41 on a Saturday; waterfront full-hookup "
                 "sites (to 40 ft) $58 / $63. Day use is $7 a person 13 and older ($4 seniors). Run for LCRA by Vista "
                 f"Recreation; its Campspot booking (June 2027 nights), read {D}.")},
     "source": ("https://www.campspot.com/book/parkprairiepark (availability for 2027-06-15 and 2027-06-19) + "
                f"https://vista-rec.com/parks/texas/lcra/lake-fayette-prairie-park/ (day-use fees), read {D}")},
    {"id": 7609, "name": "Lake Fayette Oak Thicket Park", "fees": {
        "nightly_low": 34.5, "nightly_high": 34.5, "currency": "USD", "surcharges": {"premium_site": 9, "weekend": 0},
        "checked": "2026",
        "note": ("Water-and-electric RV sites $34.50 a night (20/30/50-amp sites to 45 ft), waterfront sites $43.50, the "
                 f"same on a Saturday. Run for LCRA by Vista Recreation; its Campspot booking (June 2027 nights), read {D}.")},
     "source": f"https://www.campspot.com/book/oak-thicket-park (availability for 2027-06-15 and 2027-06-19), read {D}"},
    {"id": 7035, "name": "Fort Griffin State Historic Site", "fees": {
        "nightly_low": 15, "nightly_high": 15, "currency": "USD", "surcharges": {"full_hookup": 7}, "checked": "2026",
        "note": ("'Water/Electric (sites 1-13, 15-20): $15 per night'; 'Water/Electric/Sewer (sites 21-28): $22 per night'; "
                 "tent sites $12. 'Campsite fees are in addition to the daily entrance fees.' Reservations by phone "
                 f"(325-762-3592) or email. Texas Historical Commission's campground page, read {D}.")},
     "source": f"https://thc.texas.gov/state-historic-sites/fort-griffin/fort-griffin-campgrounds, read {D}"},
    {"id": 7668, "name": "Mission Dolores RV Park & Campground", "fees": {
        "nightly_low": 24, "nightly_high": 24, "currency": "USD", "checked": "2026",
        "note": ("'Water/Electric/Sewer: $24 per night'; 'All sites are full hook-up (50 amp), paved, back-in sites'; first "
                 f"come, first served. Texas Historical Commission's campground page, read {D}.")},
     "source": f"https://thc.texas.gov/state-historic-sites/mission-dolores/mission-dolores-campgrounds, read {D}"},
]
LNRA = ("Partial hookups (water and electric) $40 a night, full hookups $45; weekly $240 / $270. 'All reservations will "
        "incur a $3.50 reservation fee'; a card payment adds 2.7% + 15 cents. Lavaca-Navidad River Authority's camping "
        f"rates for the Brackenridge Recreation Complex, read {D}.")
for eid, name in ((7409, "Brackenridge Park & Campground"), (7087, "Texana Park and Campground")):
    out.append({"id": eid, "name": name, "fees": {
        "nightly_low": 40, "nightly_high": 40, "currency": "USD", "reservation_fee": 3.5, "surcharges": {"full_hookup": 5},
        "checked": "2026", "note": LNRA},
        "source": f"https://www.brackenridgepark.com/p/accommodations/camping-rates, read {D}"})
out.append({"id": 7343, "name": "Wolf Creek Park (Lake Livingston)", "fees": {
    "nightly_low": 25, "nightly_high": 25, "currency": "USD",
    "entrance": {"resident": 5, "nonresident": 5, "per": "person_day"}, "surcharges": {"premium_site": 10},
    "checked": "2026",
    "note": ("'RV site $25 nightly', 'Waterfront RV site $35 nightly'; 'Entrance Fee $5 per person/per night (ages 13 & "
             "older)'; a site includes two vehicles ($5 a night for another). Trinity River Authority's park fees page, "
             f"read {D}.")},
    "source": f"https://www.trinityra.org/recreation/park_fees.php, read {D}"})
out.append({"id": 7615, "name": "Lake Wood Recreation Area", "fees": {
    "nightly_low": 35, "nightly_high": 35, "currency": "USD", "surcharges": {"premium_site": 5}, "checked": "2026",
    "note": ("'RV'S, TRAILERS, CAMPERS AND POP-UPS: $35.00 per vehicle per camping day'; '$40.00 per day for vehicles "
             "using 50 AMP service'; tent sites $25; a second vehicle $15 a day. Guadalupe-Blanco River Authority's park "
             f"page, read {D}.")},
    "source": f"https://www.gbra.org/recreation/lake-wood-park/ (Park Fees), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "findings")
