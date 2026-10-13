"""Arizona State Parks findings, read 2026-10-12 (texts in az_fee_pages_2026-10-12.txt).

    python3 -I az_build.py OUT

Arizona State Parks' fee schedule page (azstateparks.com/fee-schedule) lists each park's camping fees ('Camping Fees at
parks where camping is available range from $25-$50 per night'; 'Additional vehicles are charged $15.00 per night';
'there $3.60 non-refundable reservation fee per site'); each park's camping page says which sites take RVs. Camping
includes the park's day use ('Campground fee includes the use of all of the park's day-use recreation areas', Homolovi;
'Campers arriving before 12 noon on the day of arrival will be charged the park entrance fee'), so no entrance is
recorded. There is no resident rate and no weekend rate for camping (Lake Havasu's and Patagonia Lake's weekend prices are
day-use entrance). The booking engine (azstateparks.com/reserve) sits behind reCAPTCHA and a bot checker, so it was not
read. Each entry: base = the cheapest camping fee for a site a 23-ft rig can use (tent-only loops, boat-in, equestrian,
group and overflow-only areas left out); hookup sites as add-ons on it ('hook-ups' are water and electric, some with
sewer); reservation fee $3.60."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
FEES = "https://azstateparks.com/fee-schedule"
# entry -> (park page, low, high, add-ons, note)
PARK = {
    11583: ("homolovi/camping-and-rvs/rv-and-tent-camping", 30, 30, {"electric": 5},
            "Non-electric sites $30 a night April 15 to November 14 and $25 the rest of the year; electric $35 March 15 "
            "to November 14 and $40 the rest of the year (the fee schedule's seasons). Most sites have water and 30-amp "
            "electric (pull-throughs 30/50); 9 are non-electric; back-in and pull-through sites take large rigs."),
    11584: ("catalina/camping-and-rvs/rv-and-tent-camping", 50, 50, {},
            "Campgrounds A and B: every site has 20/30/50-amp electric and water, $50 a night. Ringtail Campground "
            "(overflow, no hookups) is $25, open January 1 to March 31 only."),
    11585: ("dead-horse/camping-and-cabins/camping-at-dead-horse-ranch", 50, 50, {},
            "Electric sites (30/50-amp, water) $50 a night; the $25 non-electric sites are the Blackhawk Loop, 'reserved "
            "exclusively for tents. RVs, including campers and vans, are not permitted.'"),
    11586: ("kartchner/camping-and-cabins/rv-tent-camping", 50, 50, {},
            "'All campsites at Kartchner are $50/night and feature electric hookups and water.'"),
    11587: ("lost-dutchman/camping-and-cabins/rv-and-tent-camping", 35, 35, {"electric": 15},
            "68 sites with 50/30/20-amp electric and water, $50 a night; the rest are non-hookup sites 'on paved roads for "
            "tents or RVs', $35. Rustic hike-in sites $25."),
    11588: ("picacho/camping-and-rvs/camping", 50, 50, {},
            "78 electric sites for RVs or tents, '$50 per night/per vehicle'; '$25 rustic camping (October - April 15)'."),
    11589: ("fool-hollow/camping-and-rvs/camping-at-fool-hollow-lake", 50, 50, {},
            "62 electric RV sites (30-amp, some 50; water at all sites, sewer in the Mallard and Redhead loops), $50 a "
            "night; oversized sites $75. The $25 non-hookup sites are tent only ('RVs are not allowed')."),
    11590: ("cattail-cove/camping-and-rvs/rv-and-tent-camping", 50, 50, {},
            "Every site has electric and water (the upper campground's 78 have full hookups), $50 a night. Two-night "
            "minimum for Friday-Saturday April 1 to September 30; three nights on Memorial Day, Labor Day and Columbus "
            "Day weekends."),
    11591: ("lake-havasu/camping-and-cabins/lake-havasu-camping", 40, 50, {},
            "Campground sites (50-amp electric and water) 'standard $50 a night'; an RV campsite in the cabin loop $40 "
            "(dump station included); overflow $25. Three-night minimum on Memorial Day, Labor Day and Columbus Day "
            "weekends."),
    11592: ("patagonia-lake/camping-and-cabins/rv-tent-camping", 50, 50, {},
            "Electric and water sites $50 a night; the 2 non-electric sites ($25) are 22 ft long for campers and "
            "trailers; boat-in sites $25."),
    11593: ("roper-lake/camping-and-cabins/campsites", 25, 25, {"electric": 25},
            "Non-electric sites $25 a night, water only $30, electric $50; most hookup sites take vehicles to 45 ft, "
            "back-in only; the Gila campground has 5 non-electric sites."),
    11594: ("buckskin/camping-and-rvs/rv-and-tent-camping", 50, 50, {},
            "84 sites with water and 20/30/50-amp electric, some with sewer, $50 a night; non-electric riverfront sites "
            "(for tents, first come, first served) $35."),
    11595: ("lyman-lake/camping-and-cabins/rv-tent-camping", 25, 25, {"electric": 25},
            "38 hookup sites (13 with sewer) $50 a night, 18 non-hookup sites $25; no limit on RV length. 'There is "
            "currently no drinking water at the park.'"),
    11596: ("river-island/camping-and-rvs/rv-tent-camping", 50, 50, {},
            "29 RV sites (up to 65 ft, 50/30/20-amp electric and water) and 8 beachfront sites (20-amp, water, for tents "
            "and campers to 24 ft), $50 a night. Two-night minimum for Friday-Saturday April 1 to September 30."),
    11597: ("alamo-lake/camping-and-cabins/rv-and-tent-camping", 25, 25, {"electric": 15, "full_hookup": 25},
            "Dry and basic sites (Campgrounds A, D and E) $25 a night, water and electric (Campground C) $40, full "
            "hookups (Campground F) $50; Campground B mixes them, $25-40."),
}
out = []
for eid, (page, lo, hi, sur, what) in sorted(PARK.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    text = (what + " Plus the $3.60 reservation fee; a second vehicle is $15 a night. Park entry included. Arizona "
                   f"State Parks' fee schedule and the park's camping page, read {D}.")
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": lo, "nightly_high": hi, "currency": "USD", "reservation_fee": 3.6,
        "surcharges": {"weekend": 0, **sur}, "checked": "2026", "note": text},
        "source": f"{FEES} (the park's camping fees, $3.60 reservation fee) + https://azstateparks.com/{page} (site "
                  f"types), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "AZ findings")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f["nightly_high"], f["surcharges"])
