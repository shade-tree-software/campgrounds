"""Good Sam re-check of the private sweeps' price skips (AWH 2026-10-15: "re-check earlier private-campground
rejections that might now pass with good sam"). screen.py + screen_geo.py list the skips made on price at parks
in the Good Sam directory; each was re-read 2026-10-15 and tested at its cheapest RV-site rate less 10% (or the
park's own Good Sam rate) against US$50 / C$69. Six pass and are added here (ids 15361-15366); the rest stay
skipped, with a verdict row saying why. python3 -I apply.py [--apply]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

D = "2026-10-15"
GS = "Good Sam campground directory (trip_data/goodsam_parks.json, isGsPark)"
GATE = "AWH 2026-10-14: a Good Sam Park may pass the price gate on its 10% discount"


def rv(stars, tier):
    return {"stars": stars, "price_tier": tier, "checked": "2026-10", "source": "rvlife"}


NEW = [
 dict(id=15361, vname="Victoria Coleto Lake RV Resort", vst="tx", name="Victoria Coleto Lake RV Resort",
      location="28.71433,-97.17805", elevation_meters=36, state="TX", waterfront="not waterfront",
      waterfront_evidence=f"satellite at 28.7143,-97.1781 ({D}): gravel loops of RV pads in open pasture east of Coleto "
                          "Park Rd; no water at or beside any site (the fishing pond and Coleto Creek Reservoir are not "
                          "at the pads)",
      inclusion_evidence=f"Operator coletolakervresort.com + its Newbook engine ({D}): full-hookup back-in and "
                         "pull-through RV sites sold by the night ('Standard' $48 back-in, $53 pull-through), cabins, "
                         "tent sites; Google 4.5 over 179 reviews; RV Life 4* $$. Was skipped 2026-10-04 at $53 (the "
                         "pull-through price); the back-in rate passes the gate outright, and it is a Good Sam Park",
      website="https://www.coletolakervresort.com/", phone="361-582-0222",
      note="RV resort at 500 Coleto Park Rd, about 12 miles SW of Victoria near Coleto Creek Reservoir: full-hookup "
           "back-in and pull-through sites, cabins and tent sites; pool, ten private bathhouses, playground, "
           "clubhouse, fenced dog park, WiFi, laundry, nature trails, a catch-and-release fishing pond, and an "
           "on-site café Wednesday to Saturday evenings. Weekend and long-term guests. Books online. --Claude",
      rating=rv(4, 2), hookups={"water": True, "sewer": True},
      fees=dict(lo=48, hi=53, note=f"Full-hookup back-in sites $48 a night, pull-throughs $53; weekly works out to "
                                   f"$40.71-42.86 a night. Read {D}."),
      src=f"https://coletolakervresort.com/book-online/ (Newbook categories 1 and 4: 'Standard $48.00 / night' back-in, "
          f"'$53.00 / night' pull-through), read {D}"),
 dict(id=15362, vname="Elk Ridge Campground", vst="wa", name="Elk Ridge Campground",
      location="46.87050,-120.97190", elevation_meters=649, state="WA", waterfront="riverview",
      waterfront_evidence=f"satellite at 46.8705,-120.9719 ({D}): pads under pines between WA-410 and the Naches "
                          "River (~40-50 m wide here); the lowest pads sit ~40 m from the water behind a strip of "
                          "riparian trees and a gravel bar, canopy-blind, so default-down to riverview",
      inclusion_evidence="Held 2026-10-05 (20 water/electric RV sites on the Naches River, ResNexus); AWH read the rate "
                         "2026-10-05: all sites $51.76 before tax. Google 4.8 over 317 reviews, phone 509-658-2093; "
                         f"Good Sam Park. Re-check {D}: passes at $46.58 with the Good Sam discount ({GATE})",
      website="http://elkridgecampground.com/", phone="509-658-2093",
      note="Small campground on WA-410 along the Naches River, about 16 miles NW of Naches toward Chinook Pass: 20 "
           "water/electric RV sites among the pines, plus tent sites. Books through ResNexus. --Claude",
      rating=None, hookups={"water": True},
      fees=dict(lo=51.76, hi=51.76, note="All sites $51.76 a night before tax ($56 with it), read by AWH from the "
                                         "booking engine 2026-10-05; $46.58 with the 10% Good Sam discount."),
      src="AWH 2026-10-05 (ResNexus engine linked from elkridgecampground.com): all sites $51.76 before tax, $4.24 tax"),
 dict(id=15363, vname="Camping Bas Saint-Laurent", vst="qc", name="Camping Bas-Saint-Laurent",
      location="48.15810,-69.01107", elevation_meters=126, state="QC", waterfront="lakeview",
      waterfront_evidence=f"satellite at 48.1573,-69.0121 ({D}): the row of RV pads west of Chemin du Lac Sud sits "
                          "15-25 m from Lac Saint-Mathieu, but a continuous shrub/tree strip and a fence run along "
                          "the bank; the beach is a separate day area to the north; the loops east of the road are "
                          "inland -> lakeview",
      inclusion_evidence="Operator campingbsl.com: deluxe and regular pull-through/back-in RV sites with 5 services, "
                         "tent sites, ready-to-camp cabins, plus seasonal sites; booking engine reservationpleinair.ca "
                         "quoted Tue 13 Jul 2027 (read 2026-10-08): cheapest RV hookup site C$71 (pull-through), "
                         "back-ins C$73; Google 4.1 over 383 reviews; RV Life 4.5*. Skipped 2026-10-08 as over C$69; "
                         f"re-check {D}: a Good Sam Park, C$63.90 with the discount ({GATE})",
      website="https://campingbsl.com/", phone="418-738-2034",
      note="Large campground on Lac Saint-Mathieu at Saint-Mathieu-de-Rioux, south of Trois-Pistoles: deluxe and "
           "regular RV sites (mostly pull-through, five services), tent sites, cabins and chalets, and a big seasonal "
           "section. Pool, mini golf, playgrounds, beach and lake access, activities all season. --Claude",
      rating=rv(4.5, 3), hookups={"water": True, "sewer": True},
      fees=dict(lo=71, hi=73, cur="CAD", note="Full-hookup RV sites C$71 a night (pull-through) or C$73 (back-in) on "
                                              "a July 2027 weeknight, plus tax; C$63.90 with the 10% Good Sam discount. "
                                              "Read 2026-10-08."),
      src="reservationpleinair.ca booking engine linked from campingbsl.com, quote for Tue 13 Jul 2027, 2 adults "
          "(H/I pull-thru C$71, back-ins C$73), read 2026-10-08"),
 dict(id=15364, vname="Leafy Oaks Campground", vst="oh", name="Leafy Oaks Campground",
      location="41.22390,-83.02500", elevation_meters=236, state="OH", waterfront="not waterfront",
      waterfront_evidence=f"satellite at 41.2232,-83.0248 ({D}): RV pads ring a small swimming pond, but its whole "
                          "rim is a sand swim beach with a rope line (a used strip, not an open apron); a creek runs "
                          "through woods east of the sites. The engine's 'Waterfront Back-in Full Hookup' type was "
                          "not confirmed at the pads -> not waterfront",
      inclusion_evidence=f"CampLife engine 808 linked from leafyoaks.com (read {D}): back-in electric/water sites "
                         "$51.50-57.50, waterfront back-in full hookup $57.50, full-hookup pull-throughs $62.50 a night "
                         "(Saturday 17 Oct 2026); season April-October; plus seasonal sites. Google 4.3 over 243 "
                         "reviews; RV Life 4.5*. Was skipped 2026-10-01 on RV Life $$$; Good Sam Park, $46.35 with the "
                         f"discount ({GATE})",
      website="https://www.leafyoaks.com/\nhttps://www.camplife.com/808/reservation/step1", phone="567-230-6499",
      note="Family campground at 6955 OH-101 near Clyde, in Seneca County: back-in water/electric sites, full-hookup pull-throughs and back-ins, buddy sites, "
           "tent sites, cabins and rental campers, plus seasonal sites. Swimming pond with a sand beach, fishing, "
           "camp store, live music on summer weekends. Open April to October. --Claude",
      rating=rv(4.5, 3), hookups={"electric": 50, "water": True, "sewer": True},
      fees=dict(lo=51.5, hi=62.5, note=f"RV sites $51.50-57.50 a night with water and electric, $57.50 for a waterfront "
                                       f"back-in full hookup, $62.50 for a full-hookup pull-through (a Saturday in "
                                       f"October 2026); $46.35 and up with the 10% Good Sam discount. Read {D}."),
      src=f"https://www.camplife.com/808/reservation/step1 (CampLife API, 1-night quotes for 2026-10-17; "
          f"leafyoaks.jsonl), read {D}"),
 dict(id=15365, vname="Pioneer Campground", vst="pa", name="Pioneer Campground",
      location="41.40120,-76.50950", elevation_meters=615, state="PA", waterfront="not waterfront",
      waterfront_evidence=f"satellite at 41.4005,-76.5070 ({D}): wooded sites along lanes on a ridge off Pioneer "
                          "Trail; no water at or near any site",
      inclusion_evidence="Operator pioneercampground.com, 2026 rate sheet (rates33 image, read "
                         f"{D}): water/30-amp sites $48-55 a night, water/50-amp $51-58, a full-hookup site $53-60, "
                         "electric-only $38-45, plus cabins and cottages; 10% off for Good Sam/AAA/military. Google 4.6 "
                         "over 220 reviews; RV Life 5*. Was skipped 2026-10-01 on RV Life $$$; the posted rates pass "
                         "outright",
      website="https://pioneercampground.com/nsite/", phone="570-946-9971",
      note="Wooded family campground at 307 Pioneer Trail, Muncy Valley, near Eagles Mere and Worlds End State Park: "
           "water/electric (30 or 50 amp) and electric-only sites, one full-hookup site, tent and primitive sites, "
           "rustic cabins and furnished cottages. Store, laundry, activity center, pavilion, ball field, hiking trail, "
           "dump station. Monthly and seasonal sites by phone. --Claude",
      rating=rv(5, 3), hookups={"electric": 50, "water": True},
      fees=dict(lo=38, hi=60, note=f"2026 rates for two adults: water/30-amp sites $48 off-season, $50 weeknights and "
                                   f"$55 weekends in peak season (May 4 to Oct 17); water/50-amp $51-58; the one "
                                   f"full-hookup site $53-60; electric-only $38-45. 10% off with Good Sam, AAA or "
                                   f"military (not on holiday dates). Read {D}."),
      src=f"https://pioneercampground.com/nsite/wp-content/uploads/2026/03/rates33-1024x672.jpg (2026 rate sheet on "
          f"the RV & Tent Sites page), read {D}"),
 dict(id=15366, vname="Timberline West RV Campground", vst="ia", name="Timberline West RV Campground",
      location="41.57850,-93.87200", elevation_meters=297, state="IA", waterfront="pond",
      waterfront_evidence=f"satellite at 41.5798,-93.8729 ({D}): the north loop's back-in RV pads end ~20-30 m from a "
                          "small pond across open, unused mown lawn (a reed fringe at the edge, no path, road or day "
                          "use between); the main loops south and east are inland",
      inclusion_evidence=f"Campspot engine timberlineiowa (read {D}): 43 full-hookup and 42 water/electric RV sites "
                         "(20/30/50 amp, up to 70 ft), $54 water/electric and $59 full hookup a night all year, plus "
                         "cabins and tent sites; Google 4.5 over 793 reviews; RV Life 4.5* $$$ (avg $53). Was skipped "
                         f"2026-10-02 on RV Life $$$; Good Sam Park, $48.60 with the discount ({GATE})",
      website="https://timberlineiowa.com/\nhttps://www.campspot.com/book/timberlineiowa", phone="515-987-1714",
      note="Large RV campground at 31635 SE Ashworth Rd, Waukee, just west of Des Moines: full-hookup and "
           "water/electric sites (20/30/50 amp, pull-throughs), furnished cabins and tent sites; open all year. "
           "Sister park Timberline East is at Newton. --Claude",
      rating=rv(4.5, 3), hookups={"electric": 50, "water": True, "sewer": True},
      fees=dict(lo=54, hi=59, rf=3,
                note=f"Water/electric sites $54 a night and full hookups $59, the same in October, January and June; "
                     f"$48.60 and $53.10 with the 10% Good Sam discount. Booking online adds a 4% card fee and a $3 "
                     f"convenience fee per stay. Read {D}."),
      src=f"https://www.campspot.com/book/timberlineiowa (Campspot API, park types 1904/1909, Tue/Sat pairs 2026-10 to "
          f"2027-06; 2 nights $108 + $4.32 card fee + $3.00 convenience fee, so that fee is per stay; "
          f"timberline.jsonl), read {D}"),
]

SKIPS = {
 ("az", "Las Colinas RV Park"): "55+ community that sells homes (annual and 6-month residents): fails the long-stay test 5; $55 a day passes only with the Good Sam 10%",
 ("az", "Sundance 1 RV Resort"): "55+ community with park-model and manufactured-home sales (711 sites): fails long-stay test 5; $53 off-season ($73.46 winter)",
 ("az", "Rock Springs RV Resort"): "not a Good Sam Park (the name match was wrong); standard back-in from $55 stays over the gate",
 ("ia", "Three Fingers Campground"): "not a Good Sam Park; $45 a night but only 9 transient sites among ~140 (131 seasonal): fails the 1-in-10 test",
 ("pa", "Waterside Campground"): "Good Sam Park, but the standard RV site is $59.95 a day on its Newbook engine ($53.96 with 10% off); mostly seasonal",
 ("oh", "Berlin RV Park and Campground"): "its posted Good Sam / senior / veteran rate is $62 a night (water and electric)",
 ("oh", "Sauder Village Campground"): "not a Good Sam Park; 'rates range from $41 to $64' with no site breakdown - left as skipped",
}


def main():
    path = os.path.join(ROOT, "campgrounds.json")
    db = json.load(open(path, encoding="utf-8"))
    fam = json.load(open(os.path.join(ROOT, "trip_data/family.json"), encoding="utf-8"))
    top = max(r["id"] for r in db + fam)
    assert top == 15360, top
    for n in NEW:
        f = n["fees"]
        e = {"id": n["id"], "kind": "campground", "name": n["name"], "location": n["location"],
             "elevation_meters": n["elevation_meters"], "state": n["state"], "ownership": "private",
             "waterfront": n["waterfront"], "waterfront_evidence": n["waterfront_evidence"],
             "inclusion_evidence": n["inclusion_evidence"], "website": n["website"], "phone": n["phone"],
             "note": n["note"]}
        if n["rating"]:
            e["rating"] = n["rating"]
        upd = {"hookups": n["hookups"], "booking": {"reservable": True},
               "fees": {"nightly_low": f["lo"], "nightly_high": f["hi"], "currency": f.get("cur", "USD"),
                        "checked": "2026", "note": f["note"], **({"reservation_fee": f["rf"]} if "rf" in f else {})},
               "discounts": {"good_sam": True},
               cs.PROVENANCE: {"hookups": {"source": "operator site / booking engine", "checked": D, "method": "manual"},
                               "booking": {"source": "operator site / booking engine", "checked": D, "method": "manual"},
                               "fees": {"source": n["src"], "checked": D},
                               "discounts": {"source": GS, "checked": D, "method": "derived"}}}
        cs.apply_update(e, upd)
        cs.validate_row(e, f"id {e['id']}")
        db.append(e)
        print(e["id"], e["name"], e["waterfront"], json.dumps(e["fees"])[:90])
    if "--apply" not in sys.argv:
        return
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(db, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    rows = {}
    for n in NEW:
        rows.setdefault(n["vst"], []).append({"name": n["vname"], "decision": "add", "kind_of_no": "",
                                              "why": f"Good Sam re-check {D}: added as id {n['id']}", "decided": D})
    for (st, name), why in SKIPS.items():
        rows.setdefault(st, []).append({"name": name, "decision": "skip", "kind_of_no": "price",
                                        "why": f"Good Sam re-check {D}: {why}", "decided": D})
    for st, rs in rows.items():
        with open(os.path.join(ROOT, f"audit/{st}_private/verdicts.jsonl"), "a", encoding="utf-8") as fh:
            for r in rs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("written")


if __name__ == "__main__":
    main()
