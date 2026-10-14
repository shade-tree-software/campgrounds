"""Per-entry decisions of the RoverPass pass (#8f, 2026-10-14), read by roverpass_ops_apply.py.

Each entry was read in ops_view.py's digest of its own pages (ops_read.py), with the page's full text where the
digest wasn't enough. d(id, ...) records one decision:
  act    price | drop | hold | keep
  fees   (low, high, fee note[, currency[, checked]]) - checked "2026" unless given, note ends "Read 2026-10-14."
  src    (url, [verbatim quotes]) for provenance.fees, or a plain string used as the source verbatim (a camper
         report: locals only, AWH 2026-10-11); src2 a second source appended to it
  rf     fees.reservation_fee, a flat fee once per stay (as the Campspot pass records it)
  phone  the park's published number, when it differs from ours or ours is blank (AWH 2026-10-14 #6)
  name   the name the park publishes now (AWH 2026-10-14 #8)
  note   the rewritten note (a note that named RoverPass, or carried a rate or claim the park's own pages
         don't support, is rewritten whole; --AWH text is kept); note_add a line appended instead
  booking   keys merged into the booking group (None deletes one), with booking_src - (url, [quotes]) or a plain
         string - as its provenance; only a note-derived booking group is replaced, never a person's
  booking_note  booking.note;  min_stay  booking.min_stay rules, with src giving the page
  disc   ({key: value}, (url, [quotes])) - discounts the park's own pages state
  add_web / drop_web   a URL (or a list of them) added to or removed from website
  keep_rp  a town or county park keeps its RoverPass link (no page of its own, AWH 2026-10-01)
  why    the drop reason; rule: LIVE (no live web presence, #5), OVER (over the price limit, no gateway),
         SEASONAL (no nightly RV site offered), EVENT (event or rally grounds only), MEMBERSHIP (members only),
         NORV (its own site offers no RV sites; precedent Red Pine Lodge, AWH 2026-10-11), CLOSED (Google Maps
         marks it permanently closed and no live site says otherwise)
  amend  a LIVE drop the 2026-10-01 amendment had kept (a Google Maps listing with a phone and reviews in place
         of a website, docs/campground-curation.md); #5 supersedes it, and these go in their own commit
  hold   b  = live site and phone but no published rate and no booking site (question (b) to AWH)
         2  = long-stay or seasonal park with nightly sites (AWH's #2 criteria, pending)
  ie     a line for inclusion_evidence;  border  a call close enough to the line to name in the report to AWH
Every RoverPass link on an entry this pass touches is unclaimed (roverpass_tier_2026-10-14.jsonl) and is removed,
except on a town or county park with no page of its own (AWH 2026-10-01).
"""
D = {}


def d(i, **kw):
    assert i not in D, i
    D[i] = kw


R = "read 2026-10-14"
# ---- batch 1 ----
d(1749, act="hold", hold="b",
  note="Private 38-site full-hookup campground at 721 E Carroll St, Herrin, behind the city park; 19 pull-throughs "
       "handle any size RV, 20/30/50 amp, dump station, LP, laundry, storm shelter, 7 cabins. Small stocked pond is "
       "an amenity, not RV-site-adjacent (waterfront none). Its website gives no rates and takes no bookings; call "
       "618-942-2069. --Claude")
d(1984, act="hold", hold="2b", name="Trumans Eagles Nest",
  note="Year-round RV park at 11086 Hwy 7, Clinton, minutes from the Bucksaw and Long Shoal marinas on Truman Lake "
       "(not on the water). Large full-hookup pads with room to build a carport, aimed at campers who leave their "
       "rigs year-round, plus some nightly spots. Its website gives no rates and takes no bookings; call "
       "660-477-3336. --Claude")
d(1989, act="price", phone="417-533-5628",
  fees=(45, 55, "Overnight RV Park $45 a night on weekdays and $55 on weekends from Memorial Day, for up to six "
                "people ($10 for each extra person). The page gives no year. Read 2026-10-14."),
  src=("https://www.hvoutfitters.com/pricing", ["Overnight RV Park", "Weekday $45", "Weekend $55 (Starting Memorial Day)",
                                               "Includes first 6 people"]),
  note="Outfitter's RV park on the Niangua River next to Bennett Spring SP (open Mar-Oct) with 100+ riverside sites "
       "incl. 40-ft concrete full-hookup pads. Reservable online or by phone. --Claude")
d(3379, act="hold", hold="2b",
  note="Resort on Pokegama Lake (Chetek chain), 2535 8 1/2 Ave, with seasonal RV sites, seven cabins, a bar, boat "
       "fuel and pontoon and kayak rentals; open mid-April to early October. ~170 sites (142 full-hookup, 28 W/E; "
       "20/30/50 amp) per RV Life. Its website lists seasonal camping and cabin rates only, no nightly RV rate; call "
       "715-924-3680. --Claude")
d(3494, act="keep",
  note="Village of Grantsburg campground at 300 W Olson Dr, beside the Wood River and Memory Lake Park. 38 "
       "full-hookup sites (water/sewer/electric and Wi-Fi; cable/phone via Grantsburg Telcom for a fee), modern "
       "bathhouse; rigs up to ~60 ft. The village's second campground, McNally West (400 W Olson Dr, 30 sites from "
       "full hookup to primitive), opened in September 2025. Reservations by calling the Village Office "
       "(715-463-2405); the village's page said 2026 rates were coming soon (read 2026-10-14). --Claude")
d(4050, act="price", phone="906-369-5450",
  fees=(20, 35, "Water and 30-amp electric $32 a night, water and 50-amp electric $35, rustic sites $20; the 7th "
                "night is free (not during July 4th week). The page gives no year. Read 2026-10-14."),
  src=("http://www.lakelinden.net/campground.html",
       ["RATES: Sites with water and 30-amp electric are $32 per night , the 7th night is free. (Weekly $192)",
        "Sites with water and 50-amp electric are $35 per night and the 7th night is free. (Weekly $210) (not during "
        "July 4th week)", "Rustic sites are $20 per night and the 7th night is free. (Weekly $120)"]),
  note="Village of Lake Linden campground on Torch Lake (401 Calumet St), est. 1980. 27 sites with water and 30/50A "
       "electric plus rustic tent/no-hookup sites; flush toilets, showers, dump station, swimming beach, boat ramp, "
       "disc golf. Longest rig reported 45 ft though larger sites can be tight per reviews; a 23-ft rig fits. "
       "Reservable on the village's page; changes by phone (906-369-5450) in season. --Claude")
d(4065, act="price",
  fees=(50, 60, "2026 rates: water & electric sites $50 a night in April to mid-May, September and October and $60 in "
                "June-August; holiday weekends $215 for three nights or $80 a night. Tent sites (no hook-ups) "
                "$40-47. Read 2026-10-14."),
  src=("http://www.campcirclec.com/index.php", ["Our 2026 Rates", "Water & Electric Sites", "$50.00/Night",
                                               "$60.00/Night", "$215.00 (3 night minimum)",
                                               "$80.00/Night (if not 3 nights)"]))
d(4067, act="drop", rule="OVER",
  why="over the price limit: RV sites $63 a night on the park's rates page (chamberlainlakecampground.com/rates); "
      "nearest gateway Hartford and Providence, 56 km")
# ---- batch 2 ----
d(4092, act="hold", hold="b",
  note="Private campground on 59 acres at 3628 Route 5 S, Ascutney (I-91 exit 8, then 2 mi south). ~100 sites incl. "
       "large pull-throughs with full hookups and 50 amp; heated pool, store, rec room, laundry. Open May 1-Oct 25. "
       "Mix of seasonal RVs/trailers and nightly transient sites. Near the Connecticut River and Mount Ascutney but "
       "set back west of the river across Route 5/rail line. Its website gives no rates and takes no bookings; call "
       "802-674-2812. --Claude")
d(4093, act="price",
  fees=(50, 50, "RV sites (water and 30-amp electric) $50 a night, tent sites $40; 3-night minimum on holiday "
                "weekends. The page gives no year. Read 2026-10-14."),
  src=("https://www.countryvillagecampground.com/rates-campground-map/",
       ["$50.00 (3-night minimum for holiday weekends)", "RV sites include water and 30 amp electric."]),
  min_stay=[{"nights": 3, "applies": "holiday"}], booking_note="3-night minimum on holiday weekends.",
  note="Small private wooded campground at 40 US Route 7, Leicester. 41 sites; RV sites have water and 30-amp "
       "electric; pool, laundry, showers, dump station. Open May 1-Oct 14. Nightly plus weekly/monthly rates; reserve "
       "by phone (no online booking shown). Not on water - nearest lakes/river within ~5 miles. --Claude")
d(4136, act="drop", rule="OVER",
  why="over the price limit: RV sites $55 a night on the park's rates page (saddlebackcampground.com/site-rates); "
      "nearest gateway Boston, 92 km")
d(4142, act="price",
  fees=(47, 47, "Full hook-up sites (20/30/50 amp) $47 a night; partial-hookup sites (electric and water) for tents, "
                "vans and pop-ups $30. The page gives no year. Read 2026-10-14."),
  src=("http://www.riverbend-nh.com/", ["Full Hook-up Sites", "$47 per night $280. per week", "tents, vans & pop-ups",
                                       "$30 per night $200. per week"]),
  note="Family-owned campground on the Bearcamp River, 11 Jackman Pond Rd, South Tamworth; ~27-35 sites, a mix of "
       "seasonal and nightly. Full hookups (water/sewer, 20/30/50-amp) on pull-thrus and back-ins, plus "
       "partial-hookup sites for tents, vans and pop-ups; max RV ~45-60 ft. Pool, playground, store, bathhouse, "
       "riverwalk. Open ~mid-May to mid-Oct. Book by phone. --Claude")
d(4233, act="price",
  fees=(50, 50, "Standard rate $50 a night; long-term rates by phone. The page gives no year. Read 2026-10-14."),
  src=("https://hominyvalleyrvpark.com/rates", ["Standard Rate - $50.00 daily", "(Call for Long Term Rates)"]))
d(4242, act="price",
  fees=(30, 45, "Water, sewer and 30-amp electric $45 a night, water/electric/sewer $40, water and electric $30; "
                "pay for 6 nights and the 7th is free; extra adults $5. The page gives no year. Read 2026-10-14."),
  src=("https://brysoncitycampground.com/campsites/", ["Water / 30 AMP / Sewer", "$45 per night",
                                                      "Water / Electric / Sewer", "$40 per night", "Water / Electric",
                                                      "$30 per night"]))
d(4256, act="price",
  fees=(65, 78, "2026 rate sheet: public RV sites $65 a night in rows A-F and H, $70 with a concrete patio, $78 in "
                "row G (2-night minimum); holidays and October $70-83 with a 3-night minimum; $2 more Thursday to "
                "Saturday. Read 2026-10-14."),
  src=("https://pridervresort.com/wp-content/uploads/2026/05/2026-Pride-RV-Resort-Rates.pdf",
       ["2026 PRIDE RV RESORT RATE SHEET", "Rows A-F & H $65 $1,820", "Row G all w/concrete patio (2 night min) $78",
        "PUBLIC RV SITES - HOLIDAY & OCTOBER RATES", "Holiday is a 3 night minimium"]),
  min_stay=[{"nights": 3, "applies": "holiday"}],
  booking_note="3-night minimum on holidays and through October; row G needs 2 nights (2026 rate sheet).",
  note_add="MINIMUM STAY: 3 nights on holidays and in October (2026 rate sheet, read 2026-10-14). --Claude",
  ie="AWH 2026-10-14: over the $50 price limit ($65 a night on its 2026 rate sheet) but kept as a gateway park, 28 km "
     "from Great Smoky Mountains NP")
d(4265, act="price",
  fees=(50, 65, "Rates effective January 1, 2025, still posted: $65 a night on the river, $50 off it, for two people "
                "(water, sewer and Wi-Fi included). Read 2026-10-14.", "USD", "2025"),
  src=("https://campnc.com/events-rates/", ["Rates (Effective January 1, 2025)", "On River", "Off River", "$65.00",
                                           "$50.00", "All listed rates are for two registered people in one camping "
                                           "unit per site. The fee also covers the costs of water, sewer, and wifi."]))
# ---- batch 3 ----
d(4266, act="drop", rule="OVER",
  why="over the price limit: full hook-up sites $53-63 a night on the park's rates page (thepinesrvpark.com/rates; "
      "its $35 electric-and-water sites are 'Usually for Tents and Pop-Ups'); nearest gateway Great Smoky Mountains "
      "NP, 43 km")
d(4289, act="price",
  fees=(50, 50, "Full hook-up sites (30/50 amp) $50 a night for two adults and two children, $5 per extra person; "
                "tent sites with power and water also $50. The page gives no year. Read 2026-10-14."),
  src=("https://www.foothillsfamilycampground.com/rates/", ["Full Hook-up", "$50/day | $300/week",
                                                           "pricing for 2 adults, 2 children Add $5/person/night for "
                                                           "extra"]))
d(4303, act="price",
  fees=(35, 50, "Rates effective 4/1/2024, still posted: electric-and-water campsites $45 a night, full hook-up $50, "
                "tent sites $40; $10 less from October 1 to March 31. Read 2026-10-14.", "USD", "2024"),
  src=("https://sandypointresortcampground.com/", ["Effective 4/1/2024", "CAMPSITE [electric and water]", "$45.00",
                                                  "CAMPSITE [full hook-up]", "$50.00",
                                                  "Off Season rates (oct. 1st – March 31st) Deduct $10 from daily "
                                                  "rate"]),
  disc=({"military": True}, ("https://sandypointresortcampground.com/",
                             ["15% Discount for Active Duty Military on overnight camping"])))
d(4313, act="hold", hold="b",
  note="Mountain RV park at 7868 Hwy 64 E, Hayesville, on Shooting Creek near Lake Chatuge. Full-hookup sites with "
       "30/50-amp and Wi-Fi, primitive camping, and units for rent or sale; summer and year-round camping. Its website "
       "gives no rates ('Call for great prices!') and takes no bookings; call 828-389-8232. --Claude")
d(4492, act="keep")
d(4624, act="hold", hold="2b",
  note="Full-hookup RV park just off I-75 Exit 306 (881 Poplar Springs Rd, Adairsville). ~24 gravel pull-thru/back-in "
       "sites, 50-amp, 42-ft max; laundry, cable TV. Its website gives only a monthly rate ($550 plus electric); call "
       "706-506-3273 for nightly stays and reservations. Honors Passport America (first 5 nights). --Claude")
d(4629, act="price",
  fees=(47, 47, "RV sites $47 a night, 7th night free. The page gives no year. Read 2026-10-14."),
  src=("https://www.parkwoodrv.com/rvsites.php", ["RV Site Rates", "Nightly", "$47", "7th night free!"]),
  note="Big-rig-friendly transient RV park on US-301 S south of Statesboro. ~50 sites, 30x100 pull-thru, full hookups "
       "(50/30/20 amp, water, sewer), pool, laundry, paved roads. Nightly, weekly and monthly; reservable on its "
       "website. Cottages monthly. --Claude")
# pending: read in the browser (page needs JavaScript or a booking widget) / check the Google listing
TODO = {2637: "browser", 3390: "browser", 4652: "browser", 4295: "google: website has rates but no phone"}
# ---- batch 4 ----
d(4655, act="hold", hold="2b",
  note="Riverside campground on the Chestatee River at 142 Turners Campsite Rd, Cleveland, with RV storage, an onsite "
       "manager and 24/7 access; full hookups (50-amp, water, sewer), big-rig friendly (vehicles up to ~60 ft); "
       "tubing and trout fishing on the river. Seasonal leases and short stays. Its website gives no rates ('Call For "
       "Prices') and takes no bookings; call 706-670-3351. --Claude")
d(4789, act="hold", hold="b")
d(4790, act="hold", hold="2b")
d(5102, act="hold", hold="2b",
  note="Small family RV park on the Luxapalila River in north Columbus, off Military Rd (315 Sand Rd), run with "
       "Country Living RV Park in SW Columbus. Full hookups (30/50A), waterfront lots, boat landing, river fishing, "
       "trail; tent sites too. Its website offers monthly rates but gives none, and no nightly rate; call "
       "662-242-0786. --Claude")
d(5266, act="price", phone="501-778-6050",
  fees=(50, 50, "Full hook-up sites (30 and 50 amp) $50 a night; weekly $280, monthly $550. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://www.jbsrvpark.com/", ["DAILY RATES", "Full Hook-up: 30 AMP & 50 AMP - $50.00"]),
  note="Privately owned RV park at 8601 J B Baxley Rd, Benton, off I-30 exit 106 (between Little Rock and Hot "
       "Springs). Open all year; all pull-through full-hookup sites (30/50 amp), showers, laundry, dump station; also "
       "adults-only long-term/permanent sites and a small lake on the property. --Claude")
d(5320, act="price", phone="479-667-4066",
  fees=(49, 49, "Electric sites (tent or RV) $49 a night for four people, $12 for each extra person; primitive sites "
                "$12 a person. Prices may vary during concerts and events. The page gives no year. Read 2026-10-14."),
  src=("https://byrdsadventurecenter.com/rvs-camping/", ["Camping Rates (Tent or RV)",
                                                        "Electric Site – $49 for 4 people per night / $12 for each "
                                                        "additional person per night",
                                                        "Primitive Site – $12 per person per night"]))
d(5321, act="price",
  fees=(39, 39, "RV sites with water and electric (50/30 amp and 110) $39 a night for two guests, $8 per extra guest; "
                "primitive sites $10 a guest. The page gives no year. Read 2026-10-14."),
  src=("https://www.mulberrymountainlodge.com/rv-park/",
       ["RV Sites with Electric & Water Hookups (50amp, 30amp, & 110 at each site)",
        "$39.00 per night for up to (2) guests"]))
TODO.update({4660: "browser: site is a script app", 5261: "google: the winery's website never mentions an RV park",
             5317: "google: its website is Caddo River Access RV Park in Glenwood, a different park"})
# ---- batch 5 ----
d(5540, act="price",
  fees=(39, 42, "Water and electric sites $39 a night with 30 amp, $42 with 50 amp, plus tax, for up to 2 adults and 4 "
                "children ($5 per extra person); tent sites $25; no sewer at short-term sites. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://kozyoakskamp.com/pricing-information.html", ["$39 plus tax 30 amp/water/ Free Dump Station",
                                                            "$42 plus tax 50 amp/water/Free Dump Station",
                                                            "No septic at short term sites."]))
d(5545, act="hold", hold="b")
d(5548, act="price",
  fees=(35, 45, "2026 rates: full hook-up sites $45 a night, electric only $35, rustic tent sites $25; online "
                "reservations only, 14-night maximum. Read 2026-10-14."),
  src=("https://www.hutchinsonprce.com/campground/",
       ["2026 Rates:", "Full Hook-up (water, sewer, electrical): $45/night (sites 2-14: Campground host will occupy "
        "site 1.)", "Electric Only: $35/night (sites 15-24)", "On line reservations only"]))
d(5549, act="price",
  fees=(37, 40, "Its rates page is dated 2019 and still posted: electric/water/dock sites $37 a night, "
                "electric/water/sewer/dock $40, for 1-4 people ($5 per extra person). Read 2026-10-14.", "USD", "2019"),
  src=("http://www.leechlakecampground.com/rates/", ["New Leech Lake Campground Camping & Lodging Rates – 2019",
                                                    "Elec./Water/Dock", "Elec./Water/Sewer/Dock",
                                                    "Rates based per sleeping unit"]))
d(5554, act="price",
  fees=(35, 35, "$35 a night including electric; weekly $200, monthly $500. The page gives no year. Read 2026-10-14."),
  src=("https://www.owensplacervpark.com/reservations.html", ["Overnight Rate: $35.00", "Weekly Rate: $200.00"]),
  note="Small private RV park in the Chippewa NF at Marcell; 22 sites, 12 full-hookup pull-throughs, big-rig friendly "
       "to 40 ft. Open seasonally; reservations by phone or the website's contact form. Across the highway from "
       "Marcell town park. --Claude")
d(5557, act="price", phone="507-665-2297",
  fees=(38, 43, "Water/electric sites (30/50 amp) $38 a night, full hookup $43, tents $36; four people per site, $3 "
                "per extra person; 7th night free. The page gives no year. Read 2026-10-14."),
  src=("https://www.pvcamping.com/rates.php", ["Water/Electric", "$38.00 per night", "Full Hookup", "$43.00 per night",
                                              "Limit four people and one RV or tent per site"]))
d(5562, act="price",
  fees=(39.95, 49.95, "Two-person daily rates: RV sites with 30-amp electric and water $39.95, with sewer too $49.95; "
                      "tent sites $32; 3% card fee. The page gives no year. Read 2026-10-14."),
  src=("https://www.prairielakecamp.com/rates", ["Two Person Daily Rates:", "30 amp Electric & Water: $39.95",
                                                "30 amp Electric, Water, & Sewer: $49.95"]))
d(5565, act="hold", hold="b",
  note="Wooded 22-acre RV park at 1000 Park Place Dr, Moose Lake, next to the state park and on the Soo Line/Willard "
       "Munger trails; full-hookup and water/electric sites, back-ins and drive-throughs, hot showers, laundry, dump, "
       "game room, small wildlife pond. Its website, last updated for the 2022 season, gives no rates and takes no "
       "bookings; call 218-485-0341. --Claude")
TODO.update({5344: "google: county page for a county park", 5345: "google: county page for a county park"})
# ---- batch 6 ----
d(5589, act="price",
  fees=(15, 40, "2026 campsite fees: primitive sites $15 a night, electric $25, electric and water $35, full "
                "connections $40, plus taxes and fees; holiday rates $5 more. Read 2026-10-14."),
  src=("https://www.madeliamn.com/recreation/camping/",
       ["2026 Campsite Fees:", "Primitive site – $15.00 (additional $15.00 per tent) + taxes and fees",
        "Electrical hook ups – $25.00 + taxes and fees", "Electrical and water – $35.00 + taxes and fees",
        "Full connections – $40.00 + taxes and fees"]))
d(5620, act="price", add_web="https://www.campspot.com/book/DeLagoon-Campground",
  fees=(25, 60, "Water and electric RV sites $50 a night, full hook-up $60, tent sites with water and electric $25; "
                "in October and April every site is $25. Reservations online only, 7-night maximum. The page gives "
                "no year. Read 2026-10-14."),
  src=("https://www.fergusfallsmn.gov/campground", ["RV site – partial hook-up", "$50.00/day", "RV site – full hook-up",
                                                   "$60.00/day", "Off-Season Rates (October and April)"]),
  note="City of Fergus Falls park campground on Pebble Lake, rebuilt in 2025 to 42 RV sites (10 full-hookup, 32 "
       "water+electric) plus 8 tent sites, new bathhouse and dump, boat landing. Reservations online only (Campspot), "
       "7-night maximum. --Claude")
d(5798, act="drop", rule="OVER",
  why="over the price limit: 'Our regular camping price is $60' on the park's camping page (hills-rv.com/camping, "
      "which adds 'we accept ALL discounts if paying cash or check. Average cost is $30 to $35'); nearest gateway "
      "Badlands NP, 278 km")
d(5799, act="price", phone="605-787-7898",
  fees=(47, 58, "RV rates for two people: 30-amp electric and water $47 a night, 50-amp $53, full hookups $52-58; $4 "
                "per extra person. Sturgis Rally week: full hookups need 9 days, booked by phone. The page gives no "
                "year. Read 2026-10-14."),
  src=("https://threeflagsrvpark.com/rates.html", ["RV Rates are For Two People:",
                                                  "RV 30 amp Electric and Water - $47.00 per nigh t",
                                                  "RV 50 amp Electric/Water/Sewer - $58.00 per night"]),
  note="Private RV park at Black Hawk off I-90, ~5 mi NW of Rapid City. 41 full-hookup pull-through sites up to ~80-90 "
       "ft, big-rig friendly, dump station, WiFi/cable. Open ~Apr 1-Oct 15; oriented to guests 40+ (with "
       "exceptions). Reserve by phone (605-787-7898). --Claude")
d(5805, act="price",
  fees=(50, 70, "RV sites: standard rate $50-70 a night. The page gives no year. Read 2026-10-14."),
  src=("https://steelwheelcampground.com/book-now/rv-and-campgrounds/", ["Standard Rate", "$50-70"]))
d(5806, act="hold", hold="b", phone="605-929-6007",
  note="Family-owned RV park on US-18 near I-29 at Lennox, ~20 mi SW of Sioux Falls, open year-round; 36 "
       "big-rig-friendly full-hookup sites (30/50-amp), many pull-through, with dump station, restrooms/showers, "
       "laundry, playground, propane. Check-in at the adjoining Cenex/travel plaza. Daily and monthly sites; its "
       "website gives no rates and takes no bookings, call 605-929-6007. --Claude")
d(5810, act="price",
  fees=(40, 50, "RV sites with full hookups (30 and 50 amp) $40-50 a night for up to 2 adults; tent sites $25; $5 per "
                "extra person. The page gives no year. Read 2026-10-14."),
  src=("http://www.echovalleypark.com/", ["& 50 Amp) $40.00-$50.00 night for up to 2 adults"]))
d(5813, act="price", phone="605-692-2708",
  fees=(30, 30, "Camper pads (electric) $30 a night plus tax; tents off the pads $15. Reservations online "
                "(brookingsrec.activityreg.com); two-week maximum. The page gives no year. Read 2026-10-14."),
  src=("https://www.cityofbrookings-sd.gov/311/Sexauer-Park-Campground",
       ["Camper pad: $30 per night plus tax", "Tents not on a camping pad: $15 per night plus tax"]),
  note="City of Brookings municipal campground at 121 W 10th St (entrance on Western Ave), the only campground in town, "
       "with Six Mile Creek through it. 18 paved pads (5 pull-through) with electric plus a tent area, dump station, "
       "showers, playground. Reservable online; two-week maximum stay. --Claude")
d(5821, act="price", phone="605-845-7104",
  fees=(21, 35, "RV sites (50-amp electric with water access) $21 a night or $400 a month, double RV sites $35, elders "
                "(55+) $18; vehicles $15 a day; holiday rates on the Memorial Day, Father's Day, July 4th and Labor "
                "Day weekends. The page gives no year. Read 2026-10-14."),
  src=("https://grandrivercasino.com/lodging/", ["RV Site: $21/day or $400/mo", "Elder (55 and over) Site: $18/night",
                                                "Double RV Site: $35/day or $475/mo", "Vehicle: $15/day"]))
d(5827, act="price",
  fees=(35, 35, "$35 a night for 1-6 nights, taxes included; weekly $210, monthly $425. The page gives no year. Read "
                "2026-10-14."),
  src=("http://www.watertownsdproperties.com/campground-reservations.html",
       ["$35 - Nightly rate (1-6 nights)", "These prices INCLUDE all applicable taxes"]))
D[5821]["note"] = ("RV park at the Standing Rock Sioux Tribe's Grand River Casino & Resort, 4 mi west of Mobridge on US-12 on "
                   "Lake Oahe; ~81 RV sites with 50-amp electric and water access, plus cabins, dump station, two boat "
                   "ramps, fish-cleaning station, convenience store. Seasonal (spring-fall); reservations by phone "
                   "(605-845-7104). --Claude")
D[5827]["note"] = ("Small private full-hookup RV campground (formerly Watertown Mobile Estates) in SE Watertown; ~15 paved "
                   "big-rig-friendly full-hookup sites, many pull-through, WiFi, laundry, dump station (restrooms, no "
                   "showers). Nightly reservations on its website; open ~Apr-mid-Nov. --Claude")
# ---- batch 7 ----
# add_web / drop_web: a URL to add to or remove from `website` (besides the RoverPass link every touched entry loses).
d(5892, act="keep", phone="701-567-4363",
  note="City of Hettinger campground in Mirror Lake Park, at the south edge of town on Mirror Lake; 26 sites with "
       "water and electric, big-rig friendly, free hot showers, single-hole dump station. No rates posted online (a "
       "camper reported paying $20 a night with electric in October 2023); call the city office, 701-567-4363. "
       "--Claude")
d(5943, act="hold", hold="2b", phone="701-739-9934",
  note="Family-owned resort on the west bay of Devils Lake (Minnewaukan Flats), 6660 ND-19 near Minnewaukan, with a "
       "private boat ramp. Its website now markets only cabins and vacation homes (from $150 a night) and does not "
       "mention RV sites; RV Life listed full-hookup sites for short-term and seasonal stays. Reservations by phone, "
       "701-739-9934. --Claude")
d(6764, act="price", hold="2",
  fees=(40, 40, "Full-hookup sites $40 a day, $175 a week, $500 a month (including $150 of electric) for 2 adults and "
                "2 children. The page gives no year. Read 2026-10-14."),
  src=("https://horseshoeacresrv.com/", ["Our Rates", "Daily $40.00", "Weekly $175.00"]))
d(6920, act="price",
  fees=(75, 75, "North and West RV lots, 30 or 50 amp: $75 a night or $1,000 a month (30 nights); card only, paid when "
                "booking. The page gives no year. Read 2026-10-14."),
  src=("https://www.lamardixonexpocenter.com/facilities/rv-park/", ["North RV Lot", "30 amp", "$75 Nightly",
                                                                   "$1000 Monthly"]),
  booking={"reservable": True, "platform": "operator"},
  booking_src=("https://www.lamardixonexpocenter.com/facilities/rv-park/north-rv-lot/",
               ["Payments are due at the time of reservation", "Check Facility Availability", "Reservation Date",
                "We are NOT a long-term facility."]),
  booking_note="Reservations through the availability form on the RV park page; check-in and check-out at the front "
               "desk, Monday to Friday only.",
  note="Ascension Parish-owned expo center at 9039 S St Landry Ave, Gonzales, with two RV lots (North and West, ~300 "
       "sites): 30/50-amp electric, water and sewer, two restroom/shower buildings, WiFi, pads to ~65 ft, fishing pond "
       "and walking track. Open year-round but not a long-term facility; RVs only, no tents. Request a reservation on "
       "the website's availability form; check-in and check-out at the front desk, Monday to Friday only. Busy during "
       "events. --Claude")
d(7219, act="keep", phone="806-675-2301",
  note="Small City of Crosbyton RV park with 8 sites (30-amp electric and water, some sewer) at US-82 and Aspen St, "
       "beside the city park playground and municipal pool; mostly level pads, big-rig friendly, highway noise. The "
       "city's page gives no rates; campers report the first two nights free, then $10 a night to a five-night "
       "maximum, paid at an honor box. First come, first served; City Hall 806-675-2301. --Claude")
TODO.update({5832: "google: now Hidden Lake Campground & Resort; only site is the old Larive Lake yola page",
             5834: "google: no operator site (Facebook only)", 5950: "browser: ashley-nd.com/tourism (sgcaptcha)",
             6757: "browser: where MAKE RESERVATIONS goes on the RV page", 6953: "browser: script-rendered site"})
# ---- batch 8 ----
# rule EVENT: RV hookups offered only as a service to events held at the site (the fairground/rally event-only case)
d(7242, act="drop", rule="EVENT",
  why="event-only: the county event center's own site lists 'RV Hook Ups (30/50 amp + water) $30/night' among the "
      "services 'to help enhance your event' and offers no public camping anywhere; its RoverPass listing is unclaimed")
d(7363, act="price",
  fees=(50, 50, "Daily $50 including electricity, city water/sewer and WiFi, for two people ($2 per extra person); "
                "weekly $190 and monthly $375 plus electricity. Weekend and holiday stays need 2 nights. The page "
                "gives no year. Read 2026-10-14."),
  src=("https://anglersrvretreat.com/rates/", ["Daily", "$50", "Includes Electricity, City Water/Sewer & Wifi",
                                              "Weekend and Holiday Rates require a 2 night minimum please."]),
  min_stay=[{"nights": 2, "applies": "weekend"}, {"nights": 2, "applies": "holiday"}],
  booking_note="2-night minimum on weekends and holidays; reservations by phone.",
  note="Family-owned (est. 2009) RV park under 1 mi from downtown Rockport; full-hookup sites with WiFi, open "
       "year-round, popular with winter guests. Reservations by phone; 2-night minimum on weekends and holidays. "
       "Gulf-coast fishing area near Aransas/Little Bay. --Claude")
d(7370, act="price",
  fees=(50, 55, "One night $50-55, one week $150-165, one month $420-470 plus electric; water and sewer included; $5 a "
                "day per extra adult. Reserve by calling the office. The page gives no year. Read 2026-10-14."),
  src=("https://www.austinbayougolf.com/rv-park", ["1 Night", "$50.00 - $55.00", "Water and sewer is included in price",
                                                  "For availability or to reserve a site please call the office."]),
  note="RV park at a 9-hole golf course, 2111 County Road 33 near Danbury (Brazoria County). Full-hookup pull-through "
       "big-rig sites (30/50-amp), game room, showers, coin laundry, WiFi; a row of RV sites sits beside an on-site "
       "pond with fishing piers (catch and release). Reserve by calling the office, 979-922-1234. --Claude")
d(7385, act="drop", rule="OVER",
  why="over the price limit: 30/50-amp sites 'Daily – $55' on its RV Lots page (bayoubendrvresort.com/rv-lots); "
      "downtown Houston is 44 km away, just outside the 40 km gateway radius")
d(7387, act="price",
  fees=(35, 35, "$35 a night, everything included (electric, water, sewer and wireless internet), for 2 people ($5 per "
                "extra person); weekly $180, monthly $400. The page gives no year. Read 2026-10-14."),
  src=("http://bcranchrvpark.com/rates.htm", ["Daily", "$35.00", "(Everything included*)",
                                             "Rates are for 2 people. Extra people are $5 per night per person."]),
  note="Small owner-run full-hookup RV park at 45560 Hwy 118 N, ~2 mi north of Alpine in the high desert; 30/50-amp "
       "pull-through sites fitting big rigs (to ~70 ft), cable and WiFi. Self-contained RVs only: no tent camping and "
       "guests use their own toilet and shower. Open year-round; office 9-5 daily, late arrivals welcome. --Claude")
d(7404, act="price",
  fees=(40, 45, "Daily rates for two people including electric, water and sewer: 30 amp $40, 50 amp $45; tent sites "
                "$30; weekly $240-260; monthly $375 plus electric. The page gives no year. Read 2026-10-14."),
  src=("https://www.bluebirdrvparktexas.com/rates", ["Daily: 30 amp = $40 per day", "Daily: 50 amp = $45 per day"]))
d(7438, act="price", hold="2",
  fees=(45, 45, "Daily $45 with 30/50-amp service, electricity included; weekly $190; monthly $450 plus electricity. "
                "The page gives no year. Read 2026-10-14."),
  src=("https://casarvpark.net/information", ["Daily 30/50 AMP Service $45*", "*Daily/Weekly rates include electricity",
                                             "We love long-term guests."]),
  note="RV park at 1103 Bob Smith Rd, Baytown (off I-10), minutes from the Baytown, La Porte and Pasadena "
       "petrochemical plants; aimed at long-term guests and working people (mailboxes provided) but rents by the day. "
       "Full-hookup concrete pads with 30/50-amp, free cable TV and WiFi, laundry, restrooms. Reservations by phone, "
       "281-420-0559. --Claude")
TODO.update({7417: "browser: Leisure Interactive booking engine renders its rates in script",
             7430: "google: the church camp's site never mentions RV sites; RoverPass unclaimed",
             7437: "google: website is a default Plesk page"})
# ---- batch 9 ----
d(7446, act="price",
  fees=(40, 50, "Daily rates for two people, including water, sewer, WiFi and trash: back-ins $40 a night, "
                "pull-throughs $50; $5 off the daily rate for the military. Weekly $185-240, monthly from $450 plus "
                "electric. The page gives no year. Read 2026-10-14."),
  src=("https://www.cicadaspringsrvpark.com/rates", ["DAILY RATES:", "Back Ins = $40/night", "Pull Thrus = $50/night"]),
  disc=({"military": True}, ("https://www.cicadaspringsrvpark.com/rates", ["MILITARY DISCOUNT AVAILABLE:",
                                                                          "$5.00 off the Daily Rate"])),
  note="Large in-town RV park in Killeen (founded 2010): 180 full-hookup sites (50/30/20 amp), 62 covered, 19 "
       "pull-throughs, rigs to 60 ft; WiFi and laundry, beside the city's paved hike/bike trail, playground and dog "
       "park, ~3.5 mi from Fort Cavazos. Daily, weekly and monthly; reservations up to two months ahead with a "
       "deposit. --Claude")
d(7452, act="hold", hold="b",
  note="Private RV resort at 1031 N Hood St, Rockport, with 51 full-hookup sites (30/50 amp, big-rig access) plus a "
       "two-bedroom rental cabin; pool, clubhouse, WiFi, pets OK; open year-round. Near Rockport Beach and Aransas "
       "Bay. Its website gives no rates and takes no bookings; call 361-729-5633. --Claude")
d(7474, act="keep",
  why="active booking site: its reservations page links Firefly (daily concrete and gravel sites); price left to the "
      "Firefly pass. Aledo is 25 km from downtown Fort Worth, a gateway if it prices over $50")
d(7491, act="hold", hold="2b",
  note="RV resort at 7100 S I-35E, Denton; 176 large shaded pull-through sites with water and 30-amp electric "
       "(premium sites add 50-amp and sewer), heated pool and spa, rec hall, camp store, playground, 6-acre sports "
       "field. Primarily a monthly park, though daily or weekly stays can be reserved; no rates posted, call "
       "940-497-3353. --Claude")
d(7509, act="price",
  fees=(48, 48, "$48 a night for 30 and 50 amp service, all utilities paid, for 2 people ($5 per extra person a day); "
                "weekly $225. The page gives no year. Read 2026-10-14."),
  src=("https://www.eastviewrvranch.com/rates.html", ["Daily Rates*", "$48.00 per night for 30 & 50 AMP service"]))
d(7516, act="price", hold="2",
  fees=(40, 40, "Nightly $40 (availability limited), weekly $150, monthly $400 including electric; free WiFi. The page "
                "gives no year. Read 2026-10-14."),
  src=("https://fairwayrv.com/", ["RV Site Rental Prices", "Nightly: $40 (availability limited)"]),
  note="Private 40-site RV park beside Woodland Hills Golf Course, 5393 S US-59, Nacogdoches; large full-hookup sites "
       "(20/30/50-amp), pull-throughs, max site ~70 ft, private shower stalls, laundry, dog park, free WiFi. Aimed at "
       "long-stay guests (retirees, students, workers); a few nightly sites, availability limited. --Claude")
d(7517, act="hold", hold="2b",
  note="Private Hill Country RV park NW of Bandera, its sites set into a hillside above the Hicks Creek valley; 75 "
       "full-hookup sites (72 pull-thru, 30/50-amp), pool, rec hall, dog park, hiking trails. Many sites are rented "
       "to leave an RV in place as a second home; no rates posted, call 830-589-2276. --Claude")
d(7536, act="price",
  fees=(30, 30, "Nightly $30 with electricity included, for two adults and a child under 1 ($3 per extra person); "
                "weekly $130 and monthly $350 plus electricity. The page gives no year. Read 2026-10-14."),
  src=("https://www.gatewayrvpark.com/RatesandRule.html", ["Regular Rates", "Nightly: $30.00",
                                                          "Electricity Included."]))
TODO.update({7439: "browser: FareHarbor flows 987703/987930 for current camping rates (else the July 2021 flyer, "
                   "$40-50)",
             7521: "browser: does its HotelKey engine sell RV sites, and at what price"})
# ---- batch 10 ----
# WF: entries whose own pages claim a waterfront different from ours, for the #7 re-audit at the end of the pass
WF = {}
d(7551, act="price",
  fees=(30, 30, "30 and 50 amp sites $30 a night, $175 a week, $350 a month plus electricity (13 cents a kWh). The "
                "page gives no year. Read 2026-10-14."),
  src=("https://harlowesrv.com/", ["30 AMP", "Nightly $30", "50 AMP"]))
d(7553, act="price", add_web="https://secure.rec1.com/TX/tom-green-county-tx/catalog",
  fees=(25, 25, "Utility hookups at Harper Park $25 (county rules amended August 19, 2025); reservations are required, "
                "through the county's online reservation system, and overnight camping is limited to 3 nights. Read "
                "2026-10-14.", "USD", "2025"),
  src=("https://www.tomgreencountytx.gov/upload/page/0157/docs/RULESANDREGULATIONSFORTGC%20PARKS%20-%20Amended%202025_.pdf",
       ["Reservations are required for Harper Park. The user fees are listed in the table below.",
        "Harper – Utility Hookups", "$25", "overnight camping is limited to three (3) nights"]),
  booking_note="Reservations required, through Tom Green County's online reservation system (rec1); 3-night maximum.")
d(7557, act="price", hold="2",
  fees=(45, 45, "Daily $45 ($35 for veterans with ID), weekly $155, monthly $500 (covered sites $650); water, sewer, "
                "electricity and fiber internet included. The page gives no year. Read 2026-10-14."),
  src=("https://heartlandrvpark.net/", ["We offer Daily, Weekly, Monthly Rates", "Daily", "$45",
                                       "$35 for Veterans (ID required)"]),
  disc=({"military": True}, ("https://heartlandrvpark.net/", ["$35 for Veterans (ID required)"])),
  note="RV park at 3366 SH-19 in Huntsville, near Sam Houston NF and Lake Livingston. 64 large pull-thru + 9 back-in "
       "full-hookup sites (30/50-amp), cable, fiber internet, laundry, dog park. Marketed mainly by the month, with "
       "daily and weekly rates too. --Claude")
d(7560, act="price", hold="2",
  fees=(42, 42, "Its rates page is headed 2019 and still posted: daily $42 including electric for 2 people ($5 per "
                "extra guest), weekly $220, monthly $330-370 plus electric; tent campers at the same rates. Read "
                "2026-10-14.", "USD", "2019"),
  src=("https://www.hiddenoaksrvresort.com/info.html", ["2019 RATES", "DAILY", "$42.00 includes Electric"]),
  note="RV resort at 221 Palmetto St in Lamar, across the Copano Bay causeway from Rockport and under a mile from Goose "
       "Island State Park, among live oaks; 60 extra-large full-hookup sites (~40 x 80 ft, room for a boat), "
       "clubhouse, laundry, WiFi; two public boat ramps within two blocks. Daily, weekly, monthly, seasonal and "
       "permanent rates; call 361-790-8581. --Claude")
d(7562, act="price",
  fees=(50, 50, "Daily $50, weekly $200, monthly $500-525 plus electric; water, sewer, garbage, two guests and two cars "
                "included, $5 per extra guest a day; cash, check or money order. The page gives no year. Read "
                "2026-10-14."),
  src=("https://www.hiddenviewrvpark.com/rates", ["Daily", "$50/ day", "Payment options: Cash, Check, or Money Order."]),
  note="Family-owned RV park (since 2003) at 1235 FM 471 N near Castroville, along the Medina River west of San "
       "Antonio. ~100 spacious full-hookup sites (30/50-amp), pull-thru big-rig access. Daily, weekly and monthly; "
       "cash, check or money order. --Claude")
d(7566, act="price",
  fees=(50, 50, "RV sites (full hookups, 20/30/50 amp, WiFi) $50 a night with a two-night minimum, $250 a week, $450 a "
                "month, all inclusive; tent camping $40. Reservations need a one-night deposit, non-refundable. The "
                "page gives no year. Read 2026-10-14."),
  src=("https://rvtexasresort.com/rates-1", ["Daily Rate | $50.00", "Minimum: Two or more nights",
                                            "Prices are all inclusive."]),
  min_stay=[{"nights": 2, "applies": "always"}],
  booking_note="2-night minimum for RV sites; a one-night deposit, non-refundable.",
  note="Hill Country resort at 17740 SH-16 N, Medina, with Medina River access. 52 full-hookup RV sites (20/30/50 amp, "
       "WiFi) plus cabins and a large event center; pool, rec center, dog park, nature trails. Reservations need a "
       "one-night deposit. MINIMUM STAY: 2 nights for RV sites (rates page, read 2026-10-14). --Claude")
d(7567, act="price", phone="979-716-9474",
  fees=(35, 35, "Daily $35, weekly $150, monthly $450, with free WiFi and utilities. The page gives no year. Read "
                "2026-10-14."),
  src=("https://texw23.wixstudio.com/hillshadervpark", ["RATES", "Daily - $35", "(Short Term and Long Term)"]),
  note="Small family-run RV park at 336 County Rd 90B outside Gonzales, established 2000, owners on site. Full "
       "hookups, 30/50-amp, 70-ft pull-throughs, 200+ shade trees, laundry, restrooms and showers, small bait shop; "
       "daily, weekly and monthly. Reservations by phone (979-716-9474) or email. --Claude")
d(7574, act="price",
  fees=(45, 55, "RV sites with water, electric and sewer, 30 or 50 amp: water-view $45 a night ($425 a month), "
                "water-front $55 ($500 a month). Call to book. The page gives no year. Read 2026-10-14."),
  src=("https://hollyparkmarina.com/rates/", ["RV CAMPING", "RV 30amp (Water-View)", "$45.00",
                                             "RV 30amp (Water-Front)", "$55.00"]))
WF[7574] = "its rates page sells 'Water-Front' RV sites ($55) as well as 'Water-View' ($45); ours is lakeview"
d(7613, act="drop", rule="OVER",
  why="over the price limit: RV sites 'Daily Rate: $74.43' including all fees and taxes "
      "(lakepointervresort.com/ways-to-stay/rv-spots); nearest gateway San Antonio, 57 km")
d(7616, act="price", hold="2",
  fees=(45, 75, "Daily RV sites: standard $45 a night, deluxe $60, premium $75; weekly $250-350; monthly $399-650 plus "
                "electric. The page gives no year. Read 2026-10-14."),
  src=("https://lakelandrvranch.com/daily-rv-site-rates", ["Daily RV/Camp Site Rates", "Standard- $45.00 Per Night",
                                                          "Premium $75.00 Per Night"]),
  note="Private 21-acre RV ranch near Farmersville, across the road from Lake Lavon; ~85 full-hookup 30/50-amp "
       "back-in and pull-through RV sites plus tent sites, on-site fishing pond, clubhouse and farm animals. Daily, "
       "weekly and monthly (marketed mostly by the month); book online or by phone. --Claude")
# ---- batch 11 ----
d(7636, act="price", name="Lochness RV Park", phone="936-890-5400",
  fees=(50, 60, "Lake-view spaces $50 a day, $200 a week, $575 a month; lakefront $60 a day, $225 a week, $650 a month. "
                "The page gives no year. Read 2026-10-14."),
  src=("https://lakeconroestorages.com/lochness-rv-park-reservation-request/",
       ["Lake view $50d/$200wk/$575mo Lake front $60d/$225wk/$650mo"]),
  note="RV park in a secluded cove on the north side of Lake Conroe, 14560 Calvary Rd, Willis, run by Lake Conroe "
       "Storages: 12-by-40-ft RV spaces with power (rigs must be under 40 ft), lake-view and lakefront, private boat "
       "ramp, restrooms, showers, picnic area. Daily, weekly and monthly; reserve by phone or the website's request "
       "form. --Claude")
d(7658, act="drop", rule="SEASONAL",
  why="long-stay only: its own rates page lists a single monthly rate ('Monthly' '$500' '(plus electric @ "
      "$0.06/kWh)', theoaksofmagnoliarvpark.com/rates) and no nightly or weekly sites; the nightly rate in our note "
      "came from an unclaimed RoverPass listing")
d(7666, act="drop", rule="OVER",
  why="over the price limit: 'Nightly: $52' is its cheapest site (millercreekrvpark.com/rv-sites); nearest gateway "
      "Austin, 64 km")
d(7678, act="keep", phone="254-897-2321",
  why="active booking site: its Book Now buttons open ResNexus; price left for the browser step",
  note="Historic 1925 park at 1019 NE Barnard St, Glen Rose (National Register), billed as the oldest RV park in "
       "Texas; 120 full-hookup RV spaces plus 20 electric tent sites, cabins and casitas, a large spring-fed "
       "swimming pool, event hall, park store, free WiFi. Near Dinosaur Valley SP. Book online or call "
       "254-897-2321. --Claude")
d(7684, act="price", hold="2",
  fees=(45, 65, "Daily rates including electricity, by lot size: $45, $55 and $65 (extra-large); weekly $250-300; "
                "monthly $425-465 plus electricity. The page gives no year. Read 2026-10-14."),
  src=("https://oleanderacres.com/rv-rates/", ["Daily (includes electricity)", "$45", "$55", "$65"]),
  note="Year-round RV resort in the Rio Grande Valley (Mission, S Conway Ave); 300 full-hookup sites (30/50-amp) plus "
       "park-model rentals and mobile homes, all ages, big-rig friendly, WiFi. A Winter Texan park, sold mostly by "
       "the month and season, but it takes daily and weekly stays; book online or by phone. --Claude")
d(7694, act="price",
  fees=(35, 35, "RV sites $35 a day, $175 a week, for up to 4 people ($5 per extra person); monthly on request plus "
                "electric. The page gives no year. Read 2026-10-14."),
  src=("http://palestinervpark.com/rates.htm", ["RATES FOR RV Site", "Daily - $35.00", "Weekly - $175.00"]),
  note="Small gated, heavily wooded RV park ~3 mi southeast of downtown Palestine, East Texas. 25 full-hookup sites "
       "with 20/30/50-amp; several wide level big-rig pull-thrus 70-90 ft long; laundry and bathhouse; cabins and a "
       "tiny house for rent. --Claude")
d(7701, act="price", phone="830-391-7011",
  fees=(45, 45, "Daily $45 with electric included; weekly $225; monthly $500 plus electric. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://pecanspringsrvpark.com/rates/", ["Prices:", "Daily $45 electric included"]),
  note="Country RV resort ~0.5 mi off SH-181 near Floresville, ~15 min SE of San Antonio (1956 Sutherland Springs "
       "Rd); 54 big-rig-friendly concrete full-hookup pads (30/50-amp, city water and sewer), WiFi, 24-hr laundry. "
       "Daily, weekly and monthly; call 830-391-7011. --Claude")
TODO.update({7669: "browser: morganshady.com is a script-rendered Wix site", 7678: "browser: ResNexus rates",
             7691: "google: its only site still says 'Closed Temporarily Due to Covid-19'",
             7698: "browser: rates sit in a Wix Table Master widget; Winter Texan park (hold 2 at least)"})
# ---- batch 12 ----
# fees high None = a "from" price: only nightly_low is written (the 5301 precedent)
d(7706, act="price", hold="2", name="Piney Ridge RV Park",
  fees=(40, 40, "$40 a night, every night; monthly from $450 for a basic site to $595 with carport and hobby building. "
                "The page gives no year. Read 2026-10-14."),
  src=("https://www.pineyridgervpark.com/rates-and-availability", ["Our daily rates are $40", "per night, every night."]),
  note="Gated, wooded adults-only RV park (no children) on US-69 S about 4 mi south of Tyler, aimed at retirees, "
       "students and working professionals; full hookups (30/50-amp, cable, fiber WiFi), big-rig pull-throughs, "
       "monthly sites with carports; opened 2012. Book online or by phone. --Claude")
d(7713, act="price",
  fees=(50, 65, "Interior lots $50 a day, $200 a week, $450-550 a month plus electric; waterfront lots $65 a day, $275 a "
                "week, $600-700 a month plus electric. The page gives no year. Read 2026-10-14."),
  src=("https://www.portisabelmarinaandrvpark.com/rv-lots-and-rates", ["Waterfront Lots", "$65.00 per day",
                                                                      "Interior Lots", "$50.00 per day"]),
  note="Marina RV park on the Port Isabel channel at 706 Hwy 100, with a small dock and boat ramp; interior and "
       "waterfront lots with water/sewer, cable, laundry, bathhouse. Daily, weekly and monthly; reservations by "
       "phone. --Claude")
d(7721, act="price", phone="432-426-3201",
  fees=(30, None, "RV sites with water, sewer and 30/50-amp electric from $30 a night, or by the month. The page gives no "
                  "year. Read 2026-10-14."),
  src=("https://www.prude-ranch.com/reservations", ["RV CAMPING", "Book a single night (from $30) or stay for a full "
                                                                  "month with water, sewer hookups, and electricity "
                                                                  "(30 & 50 amp)."]),
  note="Historic Davis Mountains ranch (est. 1897) at ~5,000 ft near Fort Davis and McDonald Observatory, 201 Prude "
       "Guest Ranch Rd. ~40 RV sites with full hookups (30/50-amp), pull-throughs, big-rig friendly, dump station, "
       "pool. General RV camping by the night or month at a working horse ranch that also runs a summer youth camp "
       "and group retreats; trail rides and cabins. Book online or call 432-426-3201. --Claude")
d(7724, act="price", phone="830-278-8182",
  fees=(40, 40, "Daily rate $40; discounts for military and veterans, Good Sam and Escapees. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://www.quailspringsrvpark.com/rates-amenities", ["Daily Rates: $40"]),
  disc=({"military": True, "good_sam": True}, ("https://www.quailspringsrvpark.com/rates-amenities",
                                               ["We Offer Discounts for Military/Veterans, Good Sam and Escapees"])),
  note="Adult-only RV park at 2727 E Main St (US-90) in Uvalde; full-hookup sites among mature oaks with an on-site "
       "pond; daily, weekly and monthly. Discounts for military and veterans, Good Sam and Escapees. --Claude")
d(7766, act="price",
  fees=(35, 35, "Standard full-hookup sites $35 a day, $170 a week, $370-510 a month (electric over an allowance at "
                "$0.13/kWh). The page gives no year. Read 2026-10-14."),
  src=("http://www.rvparkofvictoria.com/rates.htm", ["Sites—Standard Full Hookups", "Daily—$35"]))
d(7767, act="price",
  fees=(50, None, "Full-hookup RV sites from $50 a night ($295 a week); long-term sites from $550 a month. The page "
                  "gives no year. Read 2026-10-14."),
  src=("https://rvranch.com/rates/", ["Standard Back-In", "Starting at", "$50 /night", "$295/week"]))
d(7769, act="price",
  fees=(30, 30, "Nightly $30, monthly $600. One-night stays book online; longer stays by email or phone. The page gives "
                "no year. Read 2026-10-14."),
  src=("https://saddlebackmountainrv.com/", ["Nightly rate is $30.00. Monthly rate is $600.00.",
                                            "To reserve an overnight stay, please use the on-line booking option."]),
  note="Private I-10 stopover ~5 mi east of Balmorhea (near the Balmorhea springs). 46 pull-through full-hookup sites, "
       "RO water and ice; on-site Saddleback Steakhouse & Circle Bar Saloon. One-night stays book online, longer "
       "stays by phone. Desert setting, some highway noise. --Claude")
d(7776, act="price",
  fees=(37, 48, "Daily rates including electricity, for 2 adults and 2 children: standard sites $37, premium $48; weekly "
                "$185-240; monthly $400-500 plus electricity. Holiday weekends $50-60 a day with a 3-day minimum. The "
                "page gives no year. Read 2026-10-14."),
  src=("https://www.sargentshoresrv.com/", ["Current Rates:", "$37 per day on a Standard Site (includes electricity)",
                                           "$48 per day on a Premium Site (includes electricity)",
                                           "3 day minimum charge for 2 adults and 2 children 12 years old"]),
  min_stay=[{"nights": 3, "applies": "holiday"}], booking_note="3-day minimum on holiday weekends.",
  note="Small waterfront RV park in Sargent: 18 full-hookup sites (30/50-amp, dual water) on a man-made canal, ~2 min "
       "from the Intracoastal Waterway and Sargent Beach; lighted fishing dock, boat access, pool. Daily, weekly and "
       "monthly; 3-day minimum on holiday weekends. --Claude")
TODO.update({7722: "google: its site is a GoDaddy shell with a 'Residents Only' page, no rates or phone",
             7742: "google: its site now lists only cabins and guesthomes, no RV sites",
             5943: "google: its site lists only cabins and homes - does it still rent RV sites (decision held 2b)"})
# ---- batch 13 ----
d(7777, act="price", phone="903-656-2272",
  fees=(40, 40, "Full-hookup RV sites $40 a day; weekly and monthly rates by phone. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://scenicviewmarina.com/", ["25 Sites ~ Full Hook-Ups", "Big Rig Friendly ~ 20/30/50 Amp", "Daily $40"]),
  booking_note="Reservations by phone only (903-656-2272).",
  note="Mom-and-pop motel, marina and RV park on Lone Star Lake (Ellison Creek Reservoir) near Lake O' the Pines in "
       "Lone Star, run since the 1940s; 25 full-hookup RV sites (20/30/50-amp, big-rig friendly) plus motel rooms and "
       "a cabin, a large boat dock, fishing dock and boat rentals. Daily, weekly and monthly; reservations by phone "
       "only. --Claude")
WF[7777] = ("operator: 'bringing your own camper and hooking up right on the shore front!' and 'over 100 yards of "
            "shoreline' (scenicviewmarina.com); ours is not waterfront")
d(7781, act="drop", rule="SEASONAL",
  why="long-stay only: its own site lists only monthly rates ('MONTHLY RATES:' 'Weekend periodic use reservation "
      "$399.99 + electric' 'Fulltime use reservation $449.99 + electric', seaportvillagervpark.com) and no nightly "
      "sites or booking; our 'reservable online' came from an unclaimed RoverPass listing")
d(7784, act="price", name="Serendipity Bay RV Resort and Marina",
  fees=(50, 60, "2024 rates, still posted, electric included, for a family of 4: standard back-in $50, waterfront "
                "back-in $52, deluxe pull-through $55, deluxe waterfront $60 a day; weekly $250-300 and monthly "
                "$425-525 plus electric. 2-night minimum on holidays. Read 2026-10-14.", "USD", "2024"),
  src=("https://www.serendipitybayresort.com/rv-sites/rv-site-rates",
       ["2024 rates", "Daily Rates include Electric", "Standard Back-IN", "Daily : $50", "waterfront back-in",
        "Daily : $52", "Daily : $60", "Holidays require a 2 night minimum reservation"]),
  min_stay=[{"nights": 2, "applies": "holiday"}], booking_note="2-night minimum on holidays.")
d(7801, act="price",
  fees=(46, 51, "RV sites $46 a day with 30-amp, $51 with 50-amp, for 2 people ($8 each extra, children 10 and under "
                "free); weekly $265-285; monthly $460-480 plus electric. The page gives no year. Read 2026-10-14."),
  src=("http://www.skylineranchrvpark.com/features-rates.html",
       ["RV Site Rates", "Daily", "$46.00", "30 amp", "$51.00", "50 amp"]))
d(7807, act="price", add_web="https://parkwith.us/camps/sonnys-rv-park",
  fees=(30, 30, "RV sites $30 a day for 2 people, $175 a week, $350 a month plus electric. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://www.sonnysrvpark.com/rates", ["Daily 30.00", "Weekly 175.00", "Rates based on 2 person occupancy"]),
  note="Quiet country RV park at 8816 N Hwy 77, Lexington; full-hookup sites (30/50 amp, water, sewer), pull-throughs "
       "with big-rig access, bathhouse, laundry, clubhouse, WiFi; open year-round, popular with Winter Texans. Book "
       "online (Park With Us) or by phone; near Somerville Lake. --Claude")
d(7810, act="price",
  fees=(35, 39, "Full-hookup RV sites $35 a day for 2 people with 30-amp, $4 more for 50-amp ($2 each extra person); "
                "weekly $210 and monthly $375, both plus electric; primitive tent sites $20. The rates page shows them "
                "as images and gives no year. Read 2026-10-14."),
  src=("https://www.southfortyrvpark.com/rates.html",
       ["Daily Rates - Full Hook-up RV Site: Electric, Water, and Sewer", "$35 - (2 people / 30 amps)",
        "50 Amp Service – $4 per night"]),
  note="Wooded RV park and campground on SH-77 ~6 mi south of Giddings, part of the Ross family's South Forty Longhorn "
       "Ranch. Full-hookup pull-through sites (30/50 amp, water, sewer), primitive tent sites, pool, laundry, rec "
       "room, WiFi; small decorative pond and waterfall on the grounds. Daily, weekly and monthly; reservations by "
       "phone. --Claude")
d(7827, act="price", hold="2", phone="903-707-0660",
  add_web="https://app.fireflyreservations.com/reserve/property/StillMeadowRVPark",
  fees=(40, 40, "Nightly $40, weekly $100, monthly $300 plus electric. The page gives no year. Read 2026-10-14."),
  src=("https://www.stillmeadowrvparktx.com/rates", ["Monthly", "$300 + elec.", "Weekly", "$100", "Nightly", "$40"]))
d(7830, act="price",
  fees=(58, 61, "Daily $58 with 30-amp, $61 with 50-amp, double occupancy; weekly $310-330; monthly $630-675 plus "
                "metered electric. The page gives no year. Read 2026-10-14."),
  src=("https://stonecreekrvpark.com/rates/", ["Daily", "30 amp service", "$58.00", "50 amp service", "$61.00",
                                              "All rates are based on double occupancy"]),
  ie="AWH 2026-10-14: over the $50 price limit ($58 a night on its rates page) but kept as a gateway park, 31 km "
     "from downtown San Antonio")
d(7856, act="price", hold="2",
  fees=(40, 40, "RV lots $40 a day with 30/50-amp electric, water and sewer, plus a $200 deposit; $300 a month plus "
                "electricity. Every stay needs photos of the trailer and a background check before approval. The page "
                "gives no year. Read 2026-10-14."),
  src=("https://thehideawayrvpark.com/rentalrates/",
       ["RV Daily Lot Fee", "Deposit $200", "Must have pictures of all sides of travel trailer to make sure there are "
                                            "no add-ons before approval to moving in. With a background check."]),
  note="Small 18-site RV-only park off Hwy 36 in Gatesville (351 Cattle Dr) with full hookups (30/50-amp), laundry, "
       "showers, WiFi; also efficiency apartments. Daily and monthly lots, but every stay needs a $200 deposit, photos "
       "of the trailer and a background check before approval; call 254-865-6678. --Claude")
d(7860, act="drop", rule="OVER",
  why="over the price limit: 'Regular Site Daily $55 starting rate' (thepalmsrvpark.com/rates); no gateway within 40 "
      "km (Corpus Christi is under 1M; nearest gateway San Antonio, 211 km)")
# ---- batch 14 ----
# on a hold, why = what makes it a long-stay / residential park (for the #2 criteria mapping)
d(7865, act="price",
  fees=(25, 25, "RV sites $25 a day plus metered electric, $175 a week plus metered electric, posted as a 'Limited Time "
                "Offer!' starting June 1st; monthly $375 ($475 covered) plus metered electric. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://www.t2rvpark.com/accomodations/", ["Daily", "$25 + metered electric", "Starting June 1st",
                                                  "Limited Time Offer!"]),
  note="41-site full-hookup RV park (20/30/50-amp, back-in and pull-thru, 40-60 ft) at the end of TX-185 in the "
       "coastal fishing town of Port O'Connor (1402 Harrison Ave); shaded sites with decks, clubhouse, air-conditioned "
       "restrooms and showers, fish-cleaning station, WiFi; also bunk huts, a cabin and tiny homes. Daily, weekly and "
       "monthly; request a reservation online or by phone. --Claude")
d(7867, act="price", hold="2",
  why="monthly grass, paved and covered RV sites plus manufactured home sites, with a resident referral program",
  fees=(40, 40, "Daily $40 with electric included (10% off for Good Sam or TACO members), $198 a week; monthly $435-600 "
                "with utilities. The page gives no year. Read 2026-10-14."),
  src=("https://thompsonlakervresort.com/rates/", ["Daily Rates", "$40.00 per night", "10% off the daily rate",
                                                  "For Good Sam or TACO members"]),
  disc=({"good_sam": True}, ("https://thompsonlakervresort.com/rates/", ["10% off the daily rate",
                                                                        "For Good Sam or TACO members"])))
d(7871, act="hold", hold="2b", phone="832-841-4074",
  why="aimed at full-time RVers (mailboxes; reviews call it convenient 'to just about every need of a full time "
      "RV'er'); no rates and a 'GET QUOTE' form only",
  note="Small quiet family-owned full-hookup RV park (est. 2014) at 19615 FM 2920, 6 mi W of Tomball, NW of Houston; "
       "all sites 30/50-amp with water, sewer and WiFi, spaces 40 ft center to center, laundromat, four restrooms "
       "with showers, dog park. No rates posted; quotes by phone or the website's form. --Claude")
d(7893, act="price", hold="2",
  why="pitched as a place to spend the winter ('stay a day or a lifetime'); monthly sites with in-unit washers",
  fees=(35, 35, "2025 rates, effective January 1, 2025: $35 a day, $215 a week, $325 a month plus electricity, for 2 "
                "people ($1 a day each extra). Read 2026-10-14.", "USD", "2025"),
  src=("http://www.valleygatewayrvpark.com/id5.html", ["2025 Rates", "Daily $ 35.00", "Effective",
                                                      "January 1, 2025"]),
  note="Family-owned RV park (since 1984) on US-281 16 mi N of Edinburg, 1 mi S of Linn-San Manuel; 46 acres with "
       "large lots, 96 pull-through full-hookup (15/30/50-amp) big-rig sites, rec room, WiFi, restrooms and showers, "
       "nature trail. A winter-visitor park that also takes overnight travelers; reserve by phone. --Claude")
d(7929, act="price", hold="2", phone="806-935-4940",
  why="mixed mobile-home and RV park ('a few years, a few months or just a few hours')",
  fees=(40, 40, "Overnight $40, weekly $200, monthly $400 plus electricity. The page gives no year. Read 2026-10-14."),
  src=("https://www.yerbysrvpark.com/rates/", ["Overnight Rate", "$40.00", "Weekly Rate", "$200.00"]),
  note="Family-owned in-town RV park (since 1985) on S Meredith Ave in Dumas, on the US-287 panhandle overnight-stop "
       "corridor, next to McDade Park; 75 full-hookup spaces (30/50 amp) with concrete patios and driveways, laundry, "
       "WiFi (no on-site restrooms or showers). Mixed mobile-home and RV park that takes overnighters; reservations "
       "by phone, 806-935-4940. --Claude")
d(8048, act="keep", phone="575-517-6145",
  add_web=["https://www.socorronm.gov/attractions/city-socorro-sports-complex/",
           "https://reserve4.resnexus.com/resnexus/reservations/lodging/76EC960F-2655-42ED-AC24-1FE5BFF86334"],
  drop_web="https://www.socorronm.gov/city-services/public-parks/",
  why="town park with its own page and an active ResNexus booking site ('Book RV Sites & Horse Stalls'); price left "
      "for the browser step",
  note="City of Socorro municipal RV park at the Rodeo & Sports Complex off I-25 exit 147 (Rodeo Rd), beside the "
       "soccer fields and a 2-mile walking trail; 50 spaces with 30/50-amp, water, sewer and WiFi on graded gravel. "
       "Year-round; book online or call the complex, 575-517-6145. --Claude")
d(8132, act="price",
  fees=(42, 42, "Rate sheet posted on the site in January 2026: daily $42 plus tax with electric included; weekly $220 "
                "plus tax; monthly $375, six months $1,625 and yearly $2,550, all plus electric. For 2 people ($8 a day "
                "each extra). Read 2026-10-14."),
  src=("https://apachervcamp.com/wp-content/uploads/2026/01/Document_2026-01-01_105446rates.jpg",
       ["RATES", "Daily", "$42.00 + tax", "(Includes Electric)"]),
  note="Private RV park on Hwy 12 at mile marker 16, ~9 mi N of Reserve in Gila NF country (Cruzville); large 40x60 "
       "full-hookup lots with 30/50-amp, pull-throughs plus tent sites, showers, laundry, propane, big-rig friendly. "
       "Daily to yearly; reservations by phone. --Claude")
d(8133, act="price", phone="575-377-0533",
  fees=(45, 45, "Full-hookup sites for any size RV $45 a night, $265 a week, $650 a month plus electric. The page gives "
                "no year. Read 2026-10-14."),
  src=("https://angelnestrvretreat.com/", ["All sites have Full Hook-ups for any size RV at $45/nightly $265/weekly "
                                          "$650/monthly+electric"]),
  note="Private RV retreat ~1 mi S of Eagle Nest village on Hwy 64 (28418 US-64) at ~8,240 ft, set back from Eagle "
       "Nest Lake; 61 full-hookup sites for any size RV plus cabins, modern restrooms and showers, laundry, rec room. "
       "Reservations by phone. --Claude")
WF[8133] = ("operator: 'Family-friendly RV park with mountain and lake views' (angelnestrvretreat.com); ours is not "
            "waterfront (evidence: lake not within the 700 m frame)")
TODO.update({7909: "google: weebly page only (address and phone); note says rebranded 'Western Edition RV Community'",
             8048: "browser: ResNexus RV site rate (keep regardless; town park)",
             8148: "browser: Rezstream rates for 'Sipapu RV Camping 1-3' (hookup) and sites A-D (RVs, no hookups)"})
# ---- batch 15 ----
d(9821, act="price",
  fees=(37, 60, "Off season (September 16-May 14): sections A and B $37 a day, premium section C $42. Summer (May "
                "15-September 15): A and B $50 a day plus tax, C $60 plus tax. Tents $15. Good Sam members 10% off. "
                "The page gives no year. Read 2026-10-14."),
  src=("https://www.shobangaming.com/stay/rv-park/", ["RV Spaces in ‘A’ & ‘B’ Sections: $37/day",
                                                     "RV Spaces in ‘A’ & ‘B’ Sections: $50/day, plus tax",
                                                     "Premium RV Spaces in ‘C’ Section: $60/day, plus tax",
                                                     "Good Sam Club Rates – 10% Discount"]),
  disc=({"good_sam": True}, ("https://www.shobangaming.com/stay/rv-park/", ["Good Sam Club Rates – 10% Discount"])))
d(9847, act="price", phone="208-230-9152",
  fees=(40, 40, "Daily $40 for 2 adults ($3 each extra adult); weekly $250 (7 nights, 2 free); monthly $585; tent "
                "sites $10-20. The page gives no year. Read 2026-10-14."),
  src=("https://trailsidebicyclervpark.com/rv-park", ["Daily", "2 Adults", "$3 Each Additional Adult $40"]),
  note="Private RV park at 407 S Hornet Creek St, Council, on the 85-mi Weiser River Trail rail-trail (formerly Weiser "
       "River Trail RV Park); ~30 full-hookup sites (30/50-amp) with pull-throughs for big rigs, tent sites, dump "
       "station, showers, laundry; owner offers bike shuttles. Daily, weekly and monthly; call 208-230-9152. --Claude")
d(10158, act="price",
  fees=(40, 60, "RV sites $40 a day with water and electric, $60 with full hookups (Passport America half price the "
                "first night); weekly $240-280; tent sites $20-40. Public camping May 1 to September 30. The page gives "
                "no year. Read 2026-10-14."),
  src=("https://camplutherwoodutah.org/rates", ["Recreational Vehicle Camping", "Without Full Hookup $40",
                                               "With Full Hookup $60"]),
  note="Lutheran non-profit camp ~2 mi east of Long Valley Junction (US-89/SR-14) down a maintained gravel road, "
       "between Zion and Bryce; open to the public for nightly RV and tent camping May 1 to September 30. Large grassy "
       "RV spaces with water and 50-amp electric or full hookups, clubhouse and commercial kitchen, communal fire pit, "
       "restrooms and showers, cabins and bunkhouses. Reservations by phone, 800-205-4887. --Claude")
d(10563, act="drop", rule="MEMBERSHIP",
  why="membership resort: one of KM Resorts' 8 Washington membership campgrounds ('Put your family fun on repeat with "
      "a KM Resorts membership', kmresorts.com); its page posts no public rate and routes non-members to the sales "
      "line (1-800-867-4193 - Non-Members). Curation rule: no membership parks, even ones that take overnighters")
d(11517, act="drop", rule="OVER",
  why="over the price limit: 'Nightly : $55, Weekly : $350' (paysonrvpark.com; 10% off for military on daily stays "
      "only); no gateway within 40 km (Phoenix 106 km)")
d(13094, act="price",
  fees=(62, 77, "2025 rates, still posted, for 2 adults and 3 children: water and electric $62 a day, standard full "
                "hookup $68, premium full hookup $71 (lakefront $77); weekly, monthly and seasonal rates too. 3-night "
                "minimum on holiday weekends, paid in advance. Read 2026-10-14.", "USD", "2025"),
  src=("https://stoneycreekresort.net/camping-rates", ["2025 Camping Rules and Rates", "Water and Electric",
                                                      "$62.00 per Day $372.00 per Week", "Lake Front: $77.00 per Day",
                                                      "*All Holiday Weekends: 3 Day Min."]),
  min_stay=[{"nights": 3, "applies": "holiday"}], booking_note="3-night minimum on holiday weekends, paid in advance.",
  disc=({"military": True}, ("https://stoneycreekresort.net/camping-rates",
                             ["Police, Military, Fire Rescue, Scouts", "and Special Needs Groups - 15%"])),
  ie="AWH 2026-10-14: over the $50 price limit ($62 a night on its 2025 rate sheet) but kept as a gateway park, 23 km "
     "from Shenandoah NP",
  note="Large independent resort on 200+ acres beside its own Stoney Creek Lake near Greenville, ~23 km from "
       "Shenandoah NP. The operator's campground map numbers RV sites 1-198 on the lake level and 199-341 on the "
       "upper property: water/electric, standard full-hookup and premium (lake-view and lakefront) sites, plus tent "
       "sites T1-T12, bunkhouses and cabins. Nightly, weekly, monthly and seasonal stays; reservations by phone, "
       "check-in at the general store. Off-season storage runs Nov 1-Mar 31, so camping runs roughly April through "
       "October. Pool, mini golf, clubhouse and grill, camp store, laundry, swim beach. --Claude")
d(11520, act="hold", hold="2", phone="928-710-0180",
  why="now a Dwell RV long-term community ('Perfect for year round living', monthly from $500); whether ResNexus "
      "still sells nights decides between hold 2 and a SEASONAL drop")
TODO.update({11115: "browser: medfordoaks.com renders nothing without JS",
             11269: "browser: campgroundreservations.com rates (phone 775-725-3300 to add)",
             11308: "browser: JackRabbit rates; note names Roverpass",
             11314: "browser: camping.com (Leisure Interactive) rates; note names Roverpass and an RV Life line",
             11520: "browser: does Dwell's ResNexus sell nights? yes = price + hold 2, no = drop SEASONAL"})
# ---- missed in batch order ----
d(1998, act="price",
  fees=(45, 45, "Full-hookup RV sites $45 a day for 2 guests ($5 each extra), $250 a week, $650 a month; primitive tent "
                "sites $20. The page gives no year. Read 2026-10-14."),
  src=("http://cherokeelakescampground.com/services-rates/", ["RV Site Daily: $45.00 (includes two guests)",
                                                             "RV Site Weekly: $250.00 (includes two guests)"]))


def u(i, **kw):
    """Update a decision recorded before its browser step; a None value deletes that key."""
    D.setdefault(i, {})
    for k, v in kw.items():
        if v is None:
            D[i].pop(k, None)
        else:
            D[i][k] = v
    TODO.pop(i, None)


# ---- browser step (the driver, one page at a time) ----
# border = an over-the-limit drop or a gateway call close enough to the line to name in the report to AWH
u(7678, act="price", why=None,
  fees=(45, 55, "Standard RV sites $45 a night (30-amp pull-through, 50-amp back-in and pull-through), deluxe $55, "
                "tent sites $30, on a 2-night search for October 15-17, 2026. Read 2026-10-14."),
  src=("https://resnexus.com/resnexus/reservations/book/C2FE9E7E-9C13-4DC0-9E00-4D795B9DA54F",
       ["Standard 30 Pull Thru", "Standard Rate", "$45.00 / night"]),
  add_web="https://resnexus.com/resnexus/reservations/book/C2FE9E7E-9C13-4DC0-9E00-4D795B9DA54F")
u(8048, act="price", why=None,
  fees=(40, 40, "All 25 RV sites $40 a night on a 1-night search for October 14-15, 2026. Read 2026-10-14."),
  src=("https://resnexus.com/resnexus/reservations/book/76EC960F-2655-42ED-AC24-1FE5BFF86334",
       ["A-01 Alamo Lane", "Standard Rate", "$40.00 / night"]))
D.pop(11520)
TODO.pop(11520)
d(11520, act="drop", rule="SEASONAL",
  why="now a Dwell RV long-term community: its own site offers only 'Monthly Stays' from $500 ('Perfect for year "
      "round living'), and the Virgin River Communities ResNexus engine it shares lists no nightly site for it under "
      "the Short-Term filter (only '05.2 Desert Springs - Nightly $44.00 / night')")
d(7417, act="hold", hold="b",
  note="Rural full-hookup RV park at 678 Old Sayers Rd off US-290 near Elgin, ~25 min east of Austin/I-35; open "
       "year-round. Circular layout around a central bathhouse, 50-amp sites, water hookups, dump station, laundry, "
       "WiFi. Its website gives no rates and takes no bookings; reservations by phone (512-581-8033 or 512-294-8354), "
       "cash or check only. --Claude")
d(11314, act="hold", hold="b",
  note="Year-round RV park at 807 N Humboldt Ave, Wells, between the Humboldt and Ruby Mountains: ~38 sites with "
       "30/50-amp full hookups and cable TV, pull-throughs for big rigs, tent sites, dump station, WiFi, laundry and "
       "bathhouse. Its website gives no rates and takes no bookings; call 775-752-3525. --Claude")
d(11308, act="hold", hold="2b",
  why="billed as 'A Neighborhood in a Resort Type Setting', with extra storage; its 'Rates & Reservations' link goes to "
      "a dead JackRabbit page, so whether nights are sold is unconfirmed",
  note="Pahrump RV park at 901 West St, billed as 'A Neighborhood in a Resort Type Setting': ~40 sites with asphalt "
       "pads and 30/50-amp full hookups behind automated security gates, pool, clubhouse, BBQ area, propane station, "
       "extra storage. Its website gives no rates and its reservations link is dead; call 775-727-9996. --Claude")
d(11269, act="price", phone="775-725-3300",
  fees=(36, 38, "Back-in full hookup (30/50-amp) from $36 a night, pull-through full hookup from $38, on a 2-night "
                "search for October 20-22, 2026 with a 23-ft travel trailer. Read 2026-10-14."),
  src=("https://reserve.campgroundreservations.com/search_sites?gs_campground_id=201301384",
       ["Back-In FHU 30,50A", "From US$36.00 / night", "Pull Through 30,50 Only", "From US$38.00 / night"]),
  add_web="https://reserve.campgroundreservations.com/search_sites?gs_campground_id=201301384")
d(8148, act="drop", rule="OVER",
  why="over the price limit: its 3 RV spaces are $65 a night ('RV Hookup 1 ... $65.00 / night', rezStream, 2-night "
      "search for October 15-17, 2026; electric only in winter, summer dates not yet bookable); the $30 riverside "
      "campsites are tent sites where 'Some trailers may also dry camp'; no gateway within 40 km (Santa Fe 63 km)",
  border="Taos is ~28 km away but isn't on the gateway list; some trailers may dry camp in the $30 tent sites")
d(7439, act="price",
  fees=(40, 50, "Power-only sites from $40 a night, power and water from $45, full hookup from $50; tent sites from "
                "$35. Read 2026-10-14."),
  src=("https://fareharbor.com/embeds/book/cascadecaverns/items/?flow=987930&full-items=yes",
       ["Power Only Sites", "From $40 – 200", "Power & Water Site", "From $45 – 540", "Full Hookup Camp Site",
        "From $50 – 600"]),
  note="226 Cascade Caverns Rd, Boerne, on a 103-acre Hill Country property with on-site cavern tours. 95 sites (46 "
       "full-hookup, plus electric-water and electric-only), 20 pull-throughs, 30/50-amp, big-rig access to 60 ft; "
       "showers, laundry, nature trails. Stays of a night to a month (power-only sites up to two weeks), booked "
       "online. --Claude")
d(7521, act="hold", hold="b",
  note="Motel-plus-RV-park at 2201 TX-17 at the north edge of Fort Davis in the Davis Mountains, a mile from Fort "
       "Davis National Historic Site and ~20 min from McDonald Observatory. Pull-through and back-in full-hookup RV "
       "sites, restrooms with hot showers, laundry, WiFi, picnic tables, pets welcome. Its online booking engine "
       "sells motel rooms only and its RV page gives no rates; call 432-426-2112. --Claude")
d(7669, act="hold", hold="b",
  note="RV and tent campground on the South Llano River in Junction, shaded by pecan trees: full-hookup RV sites, "
       "shaded tent sites, river access for swimming, kayaking and fishing, restrooms, picnic areas, WiFi, a party "
       "barn. Its website gives no rates and takes no bookings; call 325-215-2055. --Claude")
d(7698, act="drop", rule="OVER",
  why="over the price limit: the cheapest daily rate is the interior sites' $52 ('Interior Regular $52.00', $58 "
      "June-August; daily rates include electricity), Winter Texan park; no gateway within 40 km",
  border="South Padre Island is 5 km away but isn't on the gateway list; $52 is $2 over")
d(11115, act="price",
  fees=(30, 35, "Water-and-electric sites $30 a night, full hookup $35, tents $20, for up to 4 people ($3 each "
                "extra), on the park's own rates page as last archived November 10, 2024 (the current site sits "
                "behind a captcha). Read 2026-10-14.", "USD", "2024"),
  src=("https://web.archive.org/web/20241110045305/http://medfordoaks.com/Rates.htm",
       ["Daily, weekly and monthly rates are offered.", "Sites w/water & elec", "$30", "Full hook-ups", "$35"]),
  note="27-acre RV park and campground at 7049 Hwy 140, Eagle Point, ~11 mi NE of Medford, under oak trees. Mostly "
       "pull-through full-hookup sites, big-rig friendly; seasonal pool, catch-and-release fishing pond, rec room, "
       "group picnic area, store, laundry and showers; also cabins and tent sites. Daily, weekly and monthly rates; "
       "the first night is charged when you reserve. --Claude")
d(2637, act="price", phone="303-697-6159",
  fees=(40, 40, "Campsites $40 a night ($6 off with an annual park pass), April 1 to October 31; group site $120, yurt "
                "$55, cabin $65. Read 2026-10-14."),
  src=("https://www.lakewoodco.gov/Local-Government/Departments/Community-Resources/Parks-Forestry-and-Open-Space/"
       "A-to-Z-Park-List/Bear-Creek-Lake-Park/Camping", ["Camping fees", "$40 per night",
                                                        "$34 per night for annual park pass holders"]),
  add_web="https://www.lakewoodco.gov/Local-Government/Departments/Community-Resources/Parks-Forestry-and-Open-Space/"
          "A-to-Z-Park-List/Bear-Creek-Lake-Park/Camping",
  drop_web="https://www.lakewoodco.gov/Local-Government/Departments/Community-Resources/Parks-Forestry-and-Open-Space/"
           "A-to-Z-Park-List/Bear-Creek-Lake-Park/Camping/Bear-Creek-Lake-Park-Campground",
  note="City of Lakewood campground in Bear Creek Lake Park, 15600 W Morrison Rd, ~15 mi from downtown Denver. 47 sites "
       "with 20/30/50-amp electric, a fire ring and picnic table (up to six people), shared water-fill station and "
       "spigots, dump station, restrooms and coin showers; also 3 cabins, 2 yurts and a group site. Open April 1 to "
       "October 31, booked online through Lakewood. The campground sits north of and set back from Bear Creek "
       "Lake. --Claude")
d(3390, act="hold", hold="b",
  note="Campground at 388 S Railroad St, Gays Mills, along the Kickapoo River in apple country: 60 shaded or wooded "
       "RV sites with electric hookups and many tent sites (85 sites in all, water included), fire pits, pool; "
       "canoeing and fishing. Also hosts weddings, reunions and the Stump Dodger Bash music festival. The lower "
       "Kickapoo floods in spring and early summer. Its website gives no rates and its Book Now button goes to a "
       "contact page; call 608-735-4929. --Claude")
d(4652, act="drop", rule="OVER",
  why="over the price limit: all 10 RV sites $65 a night ('RV Site - 1 . $65.00', Checkfront, 1-night search for "
      "October 27-28, 2026); no gateway within 40 km (Great Smoky Mountains NP 111 km, Atlanta 114 km)")
d(4660, act="drop", rule="OVER",
  why="over the price limit: 'Daily Rate - $55' for 30-amp full-hookup pull-throughs and $60 for 50-amp, plus tax "
      "(walkaboutcamp.com); no gateway within 40 km",
  border="Jacksonville is 57 km away; the ferry to Cumberland Island National Seashore is ~25 km")
d(5950, act="keep",
  add_web="https://www.ndtourism.com/ashley/places-stay/campgrounds-rv-parks/lake-hoskins-rv-park-campground",
  why="town park with its own pages (the city's tourism page and its ND Tourism listing, phone 701-288-5141)",
  note="Ashley Park District campground on Lake Hoskins, ~3 mi west of Ashley: primitive and modern sites with "
       "water and electric hookups, dump station, boat ramp and dock, fish-cleaning station, picnic shelters, "
       "playground, restrooms with showers. No rates or booking published; call 701-288-5141. --Claude")
d(6757, act="hold", hold="b", phone="877-725-2670",
  note="Otoe-Missouria tribal casino resort's RV park at 12875 N Hwy 77, Newkirk: full-hookup sites (30/50-amp "
       "water, electric, sewer) with easy in/out access near the casino, hotel and waterpark; no tents, no "
       "generators. Daily, weekly and monthly rates, not posted; its online booking engine sells hotel rooms only. "
       "Reservations by phone, 877-725-2670. --Claude")
d(6953, act="drop", rule="OVER",
  why="over the price limit: full hookups '57/Night' including WiFi, taxes and fees (hiddentreasurerv.com), about "
      "$52 before Louisiana's ~10% sales tax; ~80% of guests are traveling nurses and other monthly stays; no "
      "gateway within 40 km",
  border="$57 includes tax; before tax it is about $51-52")
for _i in (7417, 11314, 11308, 11269, 8148, 7439, 7521, 7669, 7698, 11115, 2637, 3390, 4652, 4660, 5950, 6757, 6953):
    TODO.pop(_i)
# ---- sites curl could not read (403/429/timeouts), read in the browser ----
d(3925, act="price",
  fees=(30, 40, "Electric-only sites $30 a day, water and electric $35, full hookup $40; tent sites $20; weekly and "
                "monthly rates too. The page gives no year. Read 2026-10-14."),
  src=("https://www.gladstonemi.gov/parks-and-recreation/page/gladstone-bay-campground",
       ["Camping Fees", "Electric $30.00", "Water & Electric $35.00", "Full $40.00"]),
  add_web="https://secure.rec1.com/MI/city-of-gladstone-mi/catalog/index?filter=c2VhcmNoPSZsb2NhdGlvbiU1QjQ2OTQzJTVEPTEmcmVudGFsJTVCZnJvbSU1RD0mcmVudGFsJTVCdG8lNUQ9JjU1NGZjNTk4Y2ZhNzVlMDU4ZWI2ZGNiZmJkZjE3MWU1PTRmOTFlMjRhNzU0ZTk4MWM3N2JlNzFhMzg4ZmNkMDZm",
  note="City of Gladstone campground at 37 Michigan Ave on Little Bay de Noc (Lake Michigan), 65 sites: full-hookup "
       "(50-amp), water-and-electric, electric-only and tent sites; 1,500-ft sandy beach with deck, boardwalk and bike "
       "path, dump station, WiFi, playground, restrooms and showers. Mix of transient and seasonal campers; RVs to "
       "60 ft. Reservations by phone (906-428-1211) or online through the city. --Claude")
d(5812, act="price",
  fees=(30, 45, "Full hookups $40 a day (30 or 50-amp), $45 for a one-night stay; electric-only $30; seasonal and "
                "monthly rates too. Open April to November. The page gives no year. Read 2026-10-14."),
  src=("https://countrycabinsrvpark.com/rv-sites.php", ["Full Hook-ups 30 AMP $40/day", "Full Hook-ups 50 AMP $40/day",
                                                       "Electric Only $30/day",
                                                       "RV Full Hookups - One day only $45/day"]),
  note="Seasonal (April-November) RV park and cabins at 2909 Country Dr, east of Mobridge near Lake Oahe: 26 RV sites "
       "(14 full-hookup 30/50-amp, 7 full-hookup 30-amp, 5 electric-only) with pull-throughs and parking for a boat, "
       "tent sites, 11 cabins and a cottage, a bathhouse of private rooms, laundry, clubhouse, wild-game cleaning room "
       "and freezer space; also pull-through areas for horse trailers. No online booking; call 605-845-2267. --Claude")
d(5815, act="price",
  fees=(40, 40, "Daily $40 for two adults ($5 a night for each extra person 12 and over), weekly $250, monthly $900, "
                "electricity included; $75 a night during the Sturgis Rally; primitive tent camping $25. Cash or check "
                "only. The page gives no year. Read 2026-10-14."),
  src=("https://lazyjdrvpark.com/rates/", ["Daily-$40", "Weekly $250", "Rates during Sturgis Rally", "Daily-$75"]),
  note="Quiet semi-rural RV park near Piedmont, 8 mi from downtown Rapid City, open May 1 to October 1. 22 full-hookup "
       "sites (20/30/50-amp) with 150-ft pull-throughs on level gravel; showers and laundry, no playground. Drive-ups "
       "welcome; cash or check only. Call 605-787-7036 for availability. --Claude")
d(7717, act="drop", rule="OVER",
  why="over the price limit: 'Nightly Back-In Site: Starting at $55', pull-through $60 (Osprey Communities' FAQ for "
      "the park); an Osprey RV park beside its manufactured-home community, 'a mix of full-time and long-term "
      "residents'; no gateway within 40 km")


# ---- AWH #8f, 2026-10-14: the remaining entries (operator sites, live probe, Google Maps) ----
# Google Maps was read through the driver (google_all.json, pass record google_maps_2026-10-14.jsonl); the live probe
# of every URL on record and every URL Google names is liveprobe_2026-10-14.json (+ its retries).
d(1287, act="price", phone="567-382-8495",
  fees=(40, 40, "RV sites $40 a night, $175 a week, $575 a month, $1,950 a season; no tents. The page gives no year. "
                "Read 2026-10-14."),
  src=("https://timberwoodscampground.com/", ["Under new ownership!", "$40.00 per night", "$175.00 weekly",
                                              "$575.00 monthly", "$1950.00 seasonal", "No tents"]),
  add_web="https://timberwoodscampground.com/",
  note="Campground at 10856 Liberty-Union Road, Van Wert, under new ownership: about 158 full-hookup sites "
       "(30/50-amp) for RVs up to 60 ft, pull-throughs among them; pool, pond, mini golf, playground, laundry and "
       "Wi-Fi for a fee; no tent camping. Open April to October. Nightly, weekly, monthly and seasonal rates; book "
       "from the website or call 567-382-8495. --Claude")
d(4476, act="price",
  fees=(40, 40, "RV sites (30 or 50 amp, with water) $40 a night for 2 adults, $10 for each extra person 13 and older; "
                "$240 a week. First come, first served, cash only. The page gives no year. Read 2026-10-14."),
  src=("https://crazyhorsecanoe.com/rv-park-waynesboro-tn", ["RV site — 30 or 50 amp", "$40 / night",
                                                             "$10 each additional person 13 and older", "RV weekly",
                                                             "$240 / week"]),
  booking={"reservable": False, "fcfs": "always", "platform": None},
  booking_src=("https://crazyhorsecanoe.com/rv-park-waynesboro-tn",
               ["Do campsites need to be reserved?", "No. All camping is first come, first served"]),
  add_web="https://crazyhorsecanoe.com/rv-park-waynesboro-tn",
  note="The original Buffalo River outfitter, family-run for 35 years at Bell Bridge on Hwy 13 just north of "
       "Waynesboro. Its North and South campgrounds have 30/50-amp electric-and-water RV sites along over a mile of "
       "river frontage (a few septic sites for monthly stays), free showers and restrooms, a camp store, and canoe "
       "and kayak floats. Open April to October. First come, first served with no reservations; cash only, paid at "
       "the gate or to a camping assistant; the gates are never locked; no generators. Office and South Campground at "
       "2505 Waynesboro Hwy, North Campground at 2501. --Claude")
d(1281, act="price",
  fees=(45, 50, "Sites with water and 30-amp electric $45 a day, with 50-amp $50, for a family of four ($1 a day for "
                "each extra child; air conditioning $2 a day). The page gives no year. Read 2026-10-14."),
  src=("https://cherokeeparkcampground.com/rates.html", ["Rates are based on a family of four.",
                                                         "With 30 Amp Electric & Water $45.00",
                                                         "With 50 Amp Electric & Water $50.00",
                                                         "Air Conditioning - Daily $2.00"]),
  add_web="https://cherokeeparkcampground.com/",
  note="Family campground at 3064 SR 43, Mogadore (Brimfield Township, Portage County), between US-224 and I-76: 120 "
       "sites with water and 30/50-amp electric, pull-throughs, dump station, on small private lakes and ponds less "
       "than a mile from Mogadore Reservoir. Daily, weekly, monthly and seasonal rates; a $40 non-refundable deposit "
       "holds a site. Call 330-673-1964. --Claude")
u(4295, act="price", phone="828-702-1973",
  fees=(50, 50, "Full-hookup sites $50 a night, $250 a week, $800 a month. The page gives no year. Read 2026-10-14."),
  src=("https://www.stonyforkrv.com/rate", ["STONY FORK RV RATES:", "Nightly $50.00", "WEEKLY $250.00",
                                            "MONTHLY $800.00"]),
  note="Small RV park on the O'Kelley farm at 2149 Pisgah Hwy, Candler, at the foot of Mt. Pisgah and the Blue Ridge "
       "Parkway, about 15 miles from downtown Asheville: 10 level full-hookup sites (30 or 50 amp) that take most "
       "any size RV; dump station, laundry, WiFi, pets welcome. Nightly, weekly and monthly rates. The website "
       "gives only an email address. The phone is from its Google Maps listing, and Pisgah View RV Park next door "
       "(2138 Pisgah Hwy) lists the same number on RoverPass. --Claude")
d(4297, act="price",
  fees=(45, 55, "Full-hookup RV sites $45 a night with 30 amp and $55 with 50 amp; pop-ups (no sewer) $40, tent sites "
                "$30-35; stay 6 nights and the 7th is free; cards carry a 2.7% charge. The 2026 season ends November 1. "
                "Read 2026-10-14."),
  src=("https://rosecreekfamilycampground.com/", ["30 amp (full hook up) $45/Night", "50 amp (full hook up) $55/Night",
                                                  "Pop-ups (no sewer hookup) $40/Night",
                                                  "Last day of the 2026 season is November 1st"]),
  booking={"reservable": True, "platform": "phone", "max_stay_nights": 30},
  booking_src=("https://rosecreekfamilycampground.com/",
               ["We do not book reservations online", "You must make reservations ahead of time due to limited "
                "availability.", "Maximum stay in a camper/RV is 30 days, no exceptions."]))
d(4480, act="price", name="Grandview RV Park and Cabins",
  fees=(35, 45, "Full-hookup RV sites $35 a night with 30 amp and $45 with 50 amp, plus 5% tax; $180 or $270 a week; "
                "primitive tent sites $15. The page gives no year. Read 2026-10-14."),
  src=("https://www.grandviewrvpark-cabins.com/", ["$35.00+$1.75tax/30 amp full hook up",
                                                   "$45.00+$2.25tax/50 amp full hook up"]),
  booking={"reservable": True, "platform": "operator"},
  booking_src=("https://www.grandviewrvpark-cabins.com/", ["Enter your information below to make a reservation.",
                                                           "We will contact you on the availability via email."]),
  add_web="https://www.grandviewrvpark-cabins.com/", drop_web="https://grandviewtn.tripod.com/GrandView",
  note="Family-run RV park and cabins at 2406 Gap Road, Altamont, on the Cumberland Plateau: 17 pull-through "
       "full-hookup sites (30/50-amp), four themed cabins and the 'Everglades' cabin on posts, primitive tent sites "
       "with a shower house, and a pond stocked with sunfish and bass; the office is open around the clock for "
       "laundry and ice. Reservations through the form on its website or by phone (931-692-3484). --Claude")
d(7488, act="price",
  fees=(35, 35, "Full-hookup sites $35 a night, $245 a week, $450 a month (metered electricity on monthly stays). The "
                "page gives no year. Read 2026-10-14."),
  src=("https://rvparkwacotx.com/stay-with-us", ["NIGHTLY RATE", "$35 / night", "WEEKLY RATE", "$245 / week",
                                                 "MONTHLY RATE", "$450 / month"]),
  booking={"reservable": True, "platform": None},
  booking_src=("https://rvparkwacotx.com/stay-with-us", ["Book a nightly or weekly stay online",
                                                         "Deposit required — call us at 254-848-8048 for details"]),
  booking_note="Its Book Now buttons lead to a RoverPass listing that no longer exists (2026-10-14); call "
               "254-848-8048 to reserve.",
  add_web="https://rvparkwacotx.com/", drop_web="https://rvparkswacotx.com/",
  note="Small locally run RV park at 610 Lady Bird Road off Hwy 6 in Waco, near Lake Waco and Magnolia Market: 25+ "
       "full-hookup sites (water, electric, sewer; WiFi included) and a dog park, by the night, week or month "
       "(metered electricity on monthly stays). Its Book Now buttons lead to a RoverPass listing that no longer "
       "exists; call 254-848-8048 to reserve. --Claude")
d(7661, act="price", name="Melody Lane Christian Renewal Center", phone="956-580-3101",
  fees=(22, 22, "RV sites $22 a night for stays under a week, $130 a week, $260 a month plus electricity. The page "
                "gives no year. Read 2026-10-14."),
  src=("https://melodylane.org/winter-texans", ["Nightly", "$22 per night", "If you are staying less than a week.",
                                                "$130/7 days", "$260 plus electric"]),
  booking={"reservable": True, "platform": "phone"},
  booking_src=("https://melodylane.org/winter-texans",
               ["Please contact us by phone for reservations at (956)580-3101 or email at office@melodylane.org"]),
  add_web="https://melodylane.org/winter-texans",
  note="Christian ministry retreat center at 2525 W Veterans Blvd, Palmview, in the Rio Grande Valley, that takes "
       "Winter Texans and other RVers ('Ministry focused, come join us'): about 96 big-rig full-hookup sites "
       "(30/50-amp, sewer, WiFi) beside its housing and meeting rooms. Nightly, weekly and monthly rates; "
       "reservations by phone (956-580-3101) or email. --Claude")
u(5832, act="price", name="Hidden Lake Campground and Resort", phone="605-745-4042",
  fees=(38, 42, "Back-in sites for RVs 35 ft and under $38 a night, pull-throughs for RVs over 35 ft $42, for 2 adults "
                "on a 1-night search for October 14-15, 2026. Read 2026-10-14."),
  src=("https://resnexus.com/resnexus/reservations/book/958E9C40-3E2C-4B09-A5C8-4AE23D166D70",
       ["14 Back in Site - RVs 35' and Under", "Standard Rate", "$38.00 / night", "01 Pull Thru Site - RVs over 35'",
        "$42.00 / night"]),
  booking={"reservable": True, "platform": "operator"},
  booking_src="https://campathiddenlake.com/ ('Now Open Year-Round — Book Your Stay'; its 'BOOK NOW' opens the park's "
              "ResNexus booking page), read 2026-10-14",
  disc=({"military": True}, ("https://resnexus.com/resnexus/reservations/book/958E9C40-3E2C-4B09-A5C8-4AE23D166D70",
                             ["Military/Veteran", "Thank you for your service! A military ID is required",
                              "5% discount"])),
  add_web=["https://campathiddenlake.com/",
           "https://resnexus.com/resnexus/reservations/book/958E9C40-3E2C-4B09-A5C8-4AE23D166D70"],
  drop_web="http://www.larivelakecampground.yolasite.com/",
  note="Family campground and resort at 27291 Evans Street, Hot Springs, on the old Larive Lake, a private "
       "spring-fed lake for fishing, kayaking, swimming and floating; now open year-round. Full-hookup RV sites with "
       "fire pits and picnic tables (back-ins for RVs up to 35 ft, pull-throughs for longer rigs), ten cabins, "
       "restrooms and showers, laundry and a playground; close to Wind Cave National Park and Custer State Park. "
       "Booked online; Campers Card members get 10% off. --Claude")
d(6994, act="price", name="RV Park Place", phone="337-348-1232",
  fees=(40, 40, "Full-hookup sites (30/50-amp, water, sewer) $40 a night on a 1-night search for October 20-21, 2026 "
                "with a travel trailer. Read 2026-10-14."),
  src=("https://parkwith.us/camps/rv-park-place-llc", ["RV Park Place LLC", "Site 101", "30/50A", "Water", "Sewage",
                                                       "$40.00 / night"]),
  booking={"reservable": True, "platform": "operator"},
  booking_src="https://parkwith.us/camps/rv-park-place-llc (the park's ParkWithUs booking page, 'RV Park Place LLC', "
              "prices per site and 'Select Site'), read 2026-10-14",
  add_web="https://parkwith.us/camps/rv-park-place-llc",
  note="Full-hookup RV park at 1381 Pitkin Rd, Leesville, about 1.5 mi from Fort Johnson's south gate (it was Quality "
       "RV Park): 58 gravel sites with 20/30/50-amp, water and sewer, a bathhouse and laundry, and a Dollar General "
       "next door; short and long stays, booked online through ParkWithUs. --Claude")
d(4494, act="price", phone="423-225-2566", rf=2,
  fees=(50, 61, "All sites pull-through full hookup (20/30/50-amp): $50 a night Sunday to Thursday and $55 Friday and "
                "Saturday, deluxe $56 and $61, plus tax; $300 a week, $600 a month plus electricity. Plus the park's $2 "
                "booking fee once per stay when booked online; Campspot adds its own booking fee at checkout. The page "
                "gives no year. Read 2026-10-14."),
  src=("https://mountainglenrvpark.com/accommodations", ["RV Daily Sunday-Thursday $50.00 plus tax",
                                                         "RV Daily Friday-Saturday $55.00 plus tax",
                                                         "RV Deluxe Daily Sunday-Thursday $56.00 plus tax",
                                                         "RV Deluxe Daily Friday-Saturday $61.00 plus tax",
                                                         "All sites are pull-thru full hookup sites"]),
  src2="https://www.campspot.com/book/mountainglenrvpark (Campspot's quote for October 20, 2026: the site $50.00, "
       "the park's 'Booking Fee' $2.00 once per stay, Campspot's 'Booking Fee' $3.00), read 2026-10-14",
  booking={"reservable": True, "platform": "campspot"},
  booking_src="https://mountainglenrvpark.com/accommodations ('RESERVE YOUR SPOT NOW!' opens the park's Campspot "
              "booking page, https://www.campspot.com/book/mountainglenrvpark), read 2026-10-14",
  disc=({"military": True}, ("https://mountainglenrvpark.com/accommodations",
                             ["Discount for Military. Restrictions apply.", "we will apply up to 10% discount"])),
  add_web=["https://mountainglenrvpark.com/", "https://www.campspot.com/book/mountainglenrvpark"],
  drop_web="https://mountainglen.com/",
  note="Private RV park at 6182 Brockdell Rd, Pikeville, on the Cumberland Plateau: standard and deluxe pull-through "
       "full-hookup sites (20/30/50-amp) plus tent and glamping sites; year-round, by the day, week or month. Booked "
       "online through Campspot or by call or text (423-225-2566). Come in by Hwy 111, Old Hwy 111 and Brockdell "
       "Road: the park warns that the routes from Hwy 28 and Hwy 27 over College Station Mountain have hairpin "
       "turns RVs cannot clear. --Claude",
  border="exactly $50 on weeknights ($55 Friday-Saturday), plus a $2 booking fee once per stay when booked online")
d(2851, act="price",
  fees=(30, 40, "Electric-only sites $30 a day; full-service sites $40 in peak season and $35 off-peak; tent sites "
                "$20. The page gives no year. Read 2026-10-14."),
  src=("https://stores.cabelas.com/us/ne/sidney/115-cabela-drive.html",
       ["CAMPGROUND RATES", "Electric Only Site $30 per day/$30 per day", "Full-service Site $40 per day/$35 per day"]),
  booking={"reservable": False, "fcfs": "always"},
  booking_src=("https://stores.cabelas.com/us/ne/sidney/115-cabela-drive.html",
               ["No reservation necessary – this is a first come first serve campground."]),
  disc=({"good_sam": True}, ("https://stores.cabelas.com/us/ne/sidney/115-cabela-drive.html",
                             ["AAA, AARP and Good Sam Club members receive a 10% discount."])),
  add_web="https://stores.cabelas.com/us/ne/sidney/115-cabela-drive.html",
  note="First-come, first-served RV park and campground beside the original Cabela's store at One Angler's Lane, "
       "Sidney, open year-round, with Walmart and restaurants in walking distance: 31 full-service sites (30 or 50 "
       "amp, water and sewer), electric-only sites (8 pull-throughs and 14 back-ins) and 6 tent sites; big rigs fit. "
       "Showers, laundry, Wi-Fi, playground, dump station. No reservations; call 308-254-7889 for availability. "
       "Cabela's and Bass Pro CLUB members get 20% off. --Claude")
d(5628, act="price", name="Everett Park", phone="517-247-8857",
  fees=(25, 25, "Electric sites $25 a night. The page gives no year. Read 2026-10-14."),
  src=("https://www.foxlakeconservation.com/everett-park.html", ["There 30 electrical campsites available",
                                                                 "Cost - $25 per night"]),
  booking={"reservable": False, "fcfs": "always", "platform": None},
  booking_src=("https://www.foxlakeconservation.com/everett-park.html", ["We are a first come campground."]),
  add_web="https://www.foxlakeconservation.com/everett-park.html",
  note="Everett Park, a Martin County park on the southeast corner of Fox Lake near Sherburn, run by the Fox Lake "
       "Conservation League: 30 sites with 30-amp electric, water fill, showers, a dump station, and boat access with "
       "docks. First come, first served; holiday weekends fill early. Open May 1 to September 30. The caretaker's "
       "number is 517-247-8857. --Claude")
d(6954, act="price",
  fees=(35, 35, "A Campendium reviewer paid $35 a night in June 2025. No operator rate page (the park posts on "
                "Facebook only); confirm by phone."),
  src="https://www.campendium.com/nibletts-bluff-park (Last Nightly Rate $35, reported 2025-06-04; read 2026-10-14)",
  note="Public park run by a Ward 7 (Calcasieu Parish) commission at the historic Niblett's Bluff site on "
       "the Old River (Sabine) near Vinton, 3409 Niblett Bluff Rd: RV sites with full hookups (30/50-amp), tent "
       "areas, a boat launch and playground, open year-round. Reservations by phone, 337-589-7117. --Claude  "
       "CAMPER-REPORTED RATE: $35 a night in June 2025 (Campendium review); the commission posts no rate "
       "(2026-10-14). --Claude")
d(7297, act="price", phone="806-244-5511", keep_rp=True,
  fees=(15, 15, "A Campendium reviewer paid $15 a night in July 2025. No operator rate page; confirm by phone."),
  src="https://www.campendium.com/rita-blanca-lake-park (Last Nightly Rate $15, reported 2025-07-22; read 2026-10-14)",
  note="City of Dalhart campground in Lake Rita Blanca Park south of town, behind the rodeo grounds: about 8 gravel "
       "full-hookup pads (30/50-amp), dump station, playground; self-service pay. Big rigs fit, but the sites are "
       "mostly back-in. Call Dalhart City Hall, 806-244-5511. --Claude  CAMPER-REPORTED RATE: $15 a night in July "
       "2025 (Campendium review); the city posts no rate (2026-10-14). --Claude")
WF[4295] = "operator: 'Creekside spaces' (stonyforkrv.com home page); ours is not waterfront"
WF[4476] = ("operator: '30 & 50 amp riverfront RV sites with water' and 'Riverfront sites on the Buffalo River' "
            "(crazyhorsecanoe.com/rv-park-waynesboro-tn); ours is riverview")

# hold: live site and phone, no published rate and no booking site (b), or a long-stay park as well (2b)
d(7507, act="hold", hold="b", add_web="http://easttexasrvpark.com/",
  note="Private RV park at 2935 Highway 69 South, Greenville, about 45 mi northeast of Dallas and a short drive from "
       "Lake Tawakoni: 35 full-hookup sites (20/30/50-amp, water, sewer), pull-throughs to 60 ft for short stays and "
       "back-ins for long-term guests ('Stay with us for a day or lifetime!'); restrooms and showers, dump station, "
       "cable TV, WiFi, propane, laundry, dog run. Its website gives no rates and takes no bookings; call "
       "903-454-8900. --Claude")
d(13087, act="hold", hold="b", add_web="https://ameliafamilybluegrass.com/",
  note="80-space campground at 9720 Military Rd, Amelia Court House, about 25 miles southwest of Richmond, home of "
       "the Hutchinson family's Amelia Family Bluegrass festivals and open for ordinary camping year-round: 30 and "
       "50-amp service, 50 full-hookup and 20 electric-only sites, 50 pull-throughs (14 by 65 ft), tent camping; "
       "pool, pond, playground, restrooms and showers, laundry. Its website gives no rates and takes no bookings; "
       "call 804-561-3011. --Claude")
d(11540, act="hold", hold="b", phone="928-422-3549", add_web="http://www.route66seligmanarizona.com/attractions/",
  note="Small transient RV park behind the Historic Route 66 General Store (22940 W Hwy 66, Seligman) on old US-66: "
       "full-hookup pull-through and back-in sites (30/50-amp, water, sewer) with free WiFi and big-rig access; a "
       "roadside stop between I-40 and the Grand Canyon. Its website gives no rates and takes no bookings; call the "
       "General Store, 928-422-3549. --Claude")
u(7909, act="hold", hold="b", name="Westend RV Park",
  note="Family-owned RV park at 375 Garner Adell Rd in rural Weatherford: about 75 full-hookup sites (30/50-amp, "
       "bills paid), pull-through and back-in, by the day, week or month; a small pond on site. Its website gives no "
       "rates and takes no bookings; call 940-682-4694. --Claude")
d(4792, act="hold", hold="2b", add_web="https://rvmhp.com/park/ponderosa-rv-park/",
  drop_web="http://www.ponderosaparkflorida.com/",
  note="All-ages RV park at 1983 Fortune Road off Hwy 192, Kissimmee, opposite Osceola Heritage Park and minutes from "
       "Walt Disney World: 200 paved sites with concrete patios and 20/30/50-amp full hookups, pull-throughs for big "
       "rigs (45 ft max), heated pool, laundry, WiFi, RV storage; cable and phone for long-term residents, stays of "
       "a day to six months. Its website takes reservation requests (a form asking for a card) but gives no rates; "
       "call 407-847-6002. --Claude")
d(1996, act="hold", hold="b", phone="573-265-3796", add_web="http://www.meramecspringscountrystore.com/4622.html",
  note="Country store and full-hookup RV park at 20458 Hwy 8, St. James, about 5.6 miles southeast of I-44 Exit 195: "
       "49 full-hookup sites (50-amp, RVs to 50 ft), swimming pool, canoe, raft and kayak floats, near trout fishing; "
       "open year-round. Its website gives no rates and takes no bookings; call 573-265-3796. --Claude")
d(6847, act="hold", hold="b", add_web="https://washitavalley.tasoffice.com/rates",
  disc=({"military": True}, ("https://washitavalley.tasoffice.com/rates",
                             ["Active military personnel stay free, up to two nights, through the Tents-For-Troops "
                              "program."])),
  note="Private RV park on Old Hwy 81 about 4 mi south of Chickasha off I-44: full-hookup pull-through sites "
       "(30/50-amp, water, sewer), WiFi, dump station, a self-pay station at the entrance; nightly, weekly and monthly "
       "guests. Dry in-country location (the ponds next door are a sewage lagoon, not a water body). Its website "
       "gives no rates and takes no bookings; call 405-689-0050. --Claude")
d(14429, act="hold", hold="2b", add_web="https://k-parkswfl.com/",
  note="Small RV park on Henderson Creek at 1366 Henderson Creek Dr, east of Naples, a short drive from the Marco "
       "Island and Naples beaches: full hookups, waterfront lots with private docks and Gulf access, pets welcome "
       "('Call today - immediate availability'). Its website gives no rates and takes no bookings; call "
       "239-248-3198. --Claude")
d(7703, act="hold", hold="b", phone="979-332-9939", add_web="https://www.pinchersrestaurants.com/rv-park",
  note="Small in-town full-hookup RV park on concrete pads behind Pinchers restaurant at 2006 Divide St, El Campo: "
       "level 50-amp sites with water and sewer, laundry, showers and restrooms; open year-round. Its website gives "
       "no rates and takes no bookings; call 979-332-9939 (the number on its Google Maps listing). --Claude")
d(5098, act="hold", hold="b", add_web="https://diamondlakerv.com/",
  drop_web="https://www.facebook.com/diamondlakervpark/",
  booking={"platform": None, "reservable": None},
  note="Family-owned RV park on Hwy 49 at Perkinston, near De Soto National Forest and 30 minutes from the Gulf "
       "Coast: full-hookup sites with concrete patios and 30/50-amp service, a lake and two ponds stocked with "
       "catfish, bass and bream (two boardwalks and a pier), about 16 to 22 full-hookup big-rig sites "
       "(pull-throughs, rigs to 74 ft), rec room with kitchenette, pavilion, fire pit, dog run, "
       "propane, WiFi, satellite TV, laundry and shower house; also mobile homes and cabins for rent. Daily, weekly "
       "and monthly rates, not posted; call Troy, 228-234-5253. --Claude")
WF[14429] = ("operator: 'We provide full hook ups and have waterfront lots & private docks' (k-parkswfl.com); ours is "
             "not waterfront")

# keep: town and county parks; the RoverPass link stays where the park has no page of its own (AWH 2026-10-01)
d(3063, act="keep", keep_rp=True,
  note="City of Ackley park (101 acres, six fishing ponds): about 120 sites, about 90 with 30-amp electric and about "
       "30 full hookups, 8 pull-throughs, big rigs welcome; dump station, shower house. Open about April to October; "
       "some sites go seasonal or monthly, but it runs as a transient campground. Call ahead to reserve, "
       "641-485-1623. --Claude")
d(7198, act="keep", keep_rp=True,
  note="City of Iraan park: a small city-run RV area (about 10 full-hookup 50-amp sites) with pool, playground, "
       "tables and grills, and a dump station. Call the city, 432-639-2301. --Claude")
d(7239, act="keep", keep_rp=True)
u(5344, act="keep", keep_rp=True, drop_web="https://www.arkansas.com/huttig/outdoor-recreation/grand-marais-campground",
  why="the arkansas.com page now redirects to a generic page (its newer address answers 404), so the link goes; the "
      "county has no page of its own, so the RoverPass link stays")
u(5345, act="keep", keep_rp=True, drop_web="https://www.arkansas.com/lake-village/accommodations/chicot-county-rv-park",
  why="the arkansas.com page now redirects to a generic page, and the county's own page lists only its offices, so "
      "the RoverPass link stays",
  note="Chicot County park on 65 wooded acres along Lake Chicot (819 Lakehall Rd, Lake Village): 98 sites, about 31 "
       "full hookups and 67 with electric, 30/50-amp; dump station, laundry, showers, playground. Call "
       "870-265-3500. --Claude")
d(5060, act="keep", keep_rp=True,
  note="Neshoba County park (owned by the Board of Supervisors, run by the Philadelphia-Neshoba County Park "
       "Commission) on Burnside Lake, a Pearl River oxbow about 5 mi northeast of Philadelphia on Hwy 15: 22 improved "
       "sites with water and 30/50-amp electric (RVs to 40 ft), bathhouse; boat ramp, fishing pier, pavilions, ball "
       "fields, nature trail, suspension bridge. The county's page covers the park but not its campsites or rates. "
       "--Claude")

# over the price limit, no gateway
d(7719, act="drop", rule="OVER",
  why="over the price limit: 'Daily: $60' for one or two people (priddymeadowrvpark.com); nearest gateway Austin, "
      "47 km",
  border="Austin is 47 km away, 7 km past the line")

# drops: no live web presence (#5), permanently closed, or no RV sites
d(3391, act='drop', rule='LIVE', amend=True, why="no live web presence: happyoursrvwisconsin.com doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our address with a phone and 39 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(3414, act='drop', rule='LIVE', amend=True, why="no live web presence: moonlitetrailscampgroundllc.camp.zone doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 25 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(4095, act='drop', rule='LIVE', amend=True, why="no live web presence: gfrcg09.com doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 36 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(7689, act='drop', rule='LIVE', amend=True, why="no live web presence: outwestcampground.com doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 76 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(7597, act='drop', rule='LIVE', why="no live web presence: kellycreeklanding.com and wrightpatmanlake.com don't resolve; its RoverPass listing is unclaimed")
d(3898, act='drop', rule='LIVE', why="no live web presence: its page on a real-estate agency's site (michiganlakeshorerealestate.net) times out; its RoverPass listing is unclaimed")
d(7548, act='drop', rule='LIVE', why='no live web presence: happycamperrvresort.com shows nothing but its own name over http and fails over https; its RoverPass listing is unclaimed')
d(7895, act='drop', rule='LIVE', why='no live web presence: vinsonrvparkandboatstorage.com is now a parked page (502 Bad Gateway earlier the same day); its RoverPass listing is unclaimed')
d(7611, act='drop', rule='LIVE', why='no live web presence: lakeliferv.com answers 402 Payment Required (hosting unpaid); its RoverPass listing is unclaimed')
d(5100, act='drop', rule='LIVE', amend=True, why='no live web presence: froglevelrv.com answers 500 with a WordPress critical-error page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 57 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7429, act='drop', rule='LIVE', why="no live web presence: camppecanbayou.com doesn't resolve; Facebook only; its RoverPass listing is claimed but takes no bookings")
d(9813, act='drop', rule='LIVE', amend=True, why="no live web presence: 1000springsresort.com is a parked redirect page (ParkLogic) and 1000-springs-resort.site, the site on its Google listing, doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 1,231 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
u(7437, act='drop', rule='LIVE', amend=True, why='no live web presence: cappyscovervpark.com is a default Plesk server page; its RoverPass listing is unclaimed; Google Maps lists it at our address with a phone and 47 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7828, act='drop', rule='LIVE', amend=True, why='no live web presence: stinsonrvparkandstorage.com answers 404 and stinsonrv.com, the site on its Google listing, redirects to a slot-gambling page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 33 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
u(7722, act='drop', rule='LIVE', amend=True, why="no live web presence: quailcrossingwaco.com is a template shell with a 'Residents Only' page and no rates or phone; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 77 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
u(7691, act='drop', rule='LIVE', why="no live web presence: its only site, overlandcampground.wordpress.com, still says 'Closed Temporarily Due to Covid-19', and Google Maps marks it temporarily closed; its RoverPass listing is unclaimed")
d(4659, act='drop', rule='LIVE', why="no live web presence: usryrvpark.com doesn't resolve; the Google result is Boss's RV park (bosssrv.com), 8.4 km away; its RoverPass listing is unclaimed")
d(7697, act='drop', rule='LIVE', why="no live web presence: paradiservoftx.com doesn't resolve; the Google result is Paradise Acres RV Resort in Dayton, 83 km away; its RoverPass listing is unclaimed")
u(5317, act='drop', rule='LIVE', why='no live web presence: caddoriveraccessrv.com, the site we linked, is Caddo River Access RV Park in Glenwood, a different park; its RoverPass listing is unclaimed')
d(3376, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only (the page of its bar and grill); its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 120 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(1271, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; bayshorefamilycamping.com now redirects to spam; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 180 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4278, act='drop', rule='LIVE', amend=True, why='no live web presence: hawkinscreekcampground.com is for sale and its Google listing links only a Good Sam page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 214 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7692, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; oxfordranchcamp.com is now a cleaning-services site in Yonkers, NY; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 237 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5089, act='drop', rule='LIVE', amend=True, why="no live web presence: only a Visit Meridian tourism page (the RV park is private, beside the city's Bonita Lakes Park); its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 398 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(5544, act='drop', rule='LIVE', amend=True, why='no live web presence: only a Visit Lake City tourism page and Facebook; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 85 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(6771, act='drop', rule='LIVE', amend=True, why='no live web presence: only a TravelOK tourism listing; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 95 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(6826, act='drop', rule='LIVE', amend=True, why='no live web presence: only a TravelOK tourism listing and Facebook; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 51 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
u(5834, act='drop', rule='LIVE', amend=True, why='no live web presence: only a Camp South Dakota directory page; its business.site page answers 404; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 130 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(1261, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our address with a phone and 313 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5326, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is gone; Google Maps lists it at our pin with a phone and 29 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(8141, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is gone; Google Maps lists it at our pin with a phone and 60 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(9866, act='drop', rule='LIVE', why='no live web presence: no website or Google Maps listing with a phone found; its RoverPass listing is unclaimed')
d(10176, act='drop', rule='LIVE', why='no live web presence: no website or Google Maps listing found; its RoverPass listing is unclaimed')
d(1290, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; twinvalleycampground.com is a parked page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 65 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(1308, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 72 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(1965, act='drop', rule='LIVE', amend=True, why='no live web presence: redcedarrv.com shows nothing but its own name; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 135 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(1999, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 42 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(2033, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 36 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(2040, act='drop', rule='LIVE', why='no live web presence: no website found; its RoverPass listing is unclaimed')
d(2853, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 147 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(3821, act='drop', rule='LIVE', amend=True, why="no live web presence: wildwoodcampgroundjonesville.com doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 99 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(3823, act='drop', rule='LIVE', amend=True, why='no live web presence: only a Pure Michigan tourism listing; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 215 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4241, act='drop', rule='LIVE', amend=True, why='no live web presence: countrywoodsrvpark.com is up for auction at GoDaddy; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 40 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4253, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 48 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4267, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 139 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4270, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our address with a phone and 41 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4300, act='drop', rule='LIVE', amend=True, why='no live web presence: only a Passport America listing; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 61 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4357, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 138 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4364, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 356 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4606, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 188 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4635, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 101 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(4749, act='drop', rule='LIVE', amend=True, why="no live web presence: lakevictorrv.com doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 33 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(4802, act='drop', rule='LIVE', amend=True, why="no live web presence: cedarslakervpark.com doesn't resolve; Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 88 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(5101, act='drop', rule='LIVE', amend=True, why="no live web presence: haasciendaranch.net doesn't resolve; Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 100 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(5256, act='drop', rule='LIVE', amend=True, why='no live web presence: only an Arkansas Tourism listing; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 80 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5264, act='drop', rule='LIVE', why='no live web presence: no website or Google Maps listing found; its RoverPass listing is unclaimed')
d(5267, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our address with a phone and 126 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5268, act='drop', rule='LIVE', amend=True, why='no live web presence: only a go-arkansas.com directory page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 62 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5332, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 107 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5566, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 44 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5803, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 175 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5808, act='drop', rule='LIVE', amend=True, why='no live web presence: its Camp South Dakota page is blank; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 114 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(5828, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 34 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(6167, act='drop', rule='LIVE', amend=True, why='no live web presence: the site on its Google listing is a spam domain (padsus.cfd); its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 38 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(6554, act='drop', rule='LIVE', why='no live web presence: no website found; its RoverPass listing is unclaimed')
d(6558, act='drop', rule='LIVE', why='no live web presence: no website found; the nearest Google result is a public access area 3.3 km away; its RoverPass listing is unclaimed')
d(6564, act='drop', rule='LIVE', why='no live web presence: no website or Google Maps listing found; its RoverPass listing is unclaimed')
d(6825, act='drop', rule='LIVE', why="no live web presence: rollingmeadowsrv.com doesn't resolve; its RoverPass listing is unclaimed")
d(6978, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found (Google Maps now names the place Tiger Town RV Park); its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 38 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(6993, act='drop', rule='LIVE', why='no live web presence: no website or Google Maps listing found; its RoverPass listing is unclaimed')
d(7322, act='drop', rule='LIVE', why='no live web presence: no website found; its RoverPass listing is unclaimed')
d(7348, act='drop', rule='LIVE', why='no live web presence: no website found; its RoverPass listing is unclaimed')
d(7368, act='drop', rule='LIVE', why='no live web presence: no website found; its RoverPass listing is unclaimed')
d(7372, act='drop', rule='LIVE', amend=True, why="no live web presence: azlewestrvpark.com doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 85 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(7384, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 65 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7423, act='drop', rule='LIVE', why='no live web presence: no website or Google Maps listing found; its RoverPass listing is unclaimed')
d(7480, act='drop', rule='LIVE', amend=True, why='no live web presence: crystalcanalrv.com is for sale; Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 69 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7482, act='drop', rule='LIVE', why="no live web presence: dandlrvpark.com doesn't resolve; its RoverPass listing is unclaimed")
d(7490, act='drop', rule='LIVE', why='no live web presence: its Google listing links only a Campendium page; its RoverPass listing is unclaimed')
d(7523, act='drop', rule='LIVE', why='no live web presence: no website found; its RoverPass listing is unclaimed')
d(7550, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 25 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7565, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 69 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7581, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 45 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7586, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 107 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7643, act='drop', rule='LIVE', amend=True, why='no live web presence: lonesomedovervparkandcamp.com is a parked page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 44 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7645, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 166 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7647, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 67 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7650, act='drop', rule='LIVE', amend=True, why='no live web presence: its business.site page answers 404; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 39 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7679, act='drop', rule='LIVE', amend=True, why="no live web presence: oakridgervresort.com doesn't resolve; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 46 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(7720, act='drop', rule='LIVE', why='no live web presence: Facebook only; its RoverPass listing is unclaimed')
d(7727, act='drop', rule='LIVE', why='no live web presence: no website found; the campingfriend.com directory page times out; its RoverPass listing is unclaimed')
d(7746, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 137 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7791, act='drop', rule='LIVE', amend=True, why='no live web presence: shadyoaksrvparkandcampground.com is for sale; Facebook only; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 84 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(7817, act='drop', rule='LIVE', why='no live web presence: Facebook only; its RoverPass listing is unclaimed')
d(7917, act='drop', rule='LIVE', amend=True, why='no live web presence: only a camping.com directory page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 76 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(8101, act='drop', rule='LIVE', amend=True, why='no live web presence: only a Sierra County tourism listing; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 118 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(8106, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 151 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(9842, act='drop', rule='LIVE', why="no live web presence: countryjunctionrv.com doesn't resolve; its RoverPass listing is unclaimed")
d(9865, act='drop', rule='LIVE', why='no live web presence: no website or Google Maps listing found; its RoverPass listing is unclaimed')
d(10180, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 27 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(10540, act='drop', rule='LIVE', why='no live web presence: thelastresortrvpark.com is a parked page; its RoverPass listing is unclaimed')
d(10564, act='drop', rule='LIVE', amend=True, why='no live web presence: Facebook only (wildroservpark.com belongs to a park in Kalispell, MT); its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 148 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(10578, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 65 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(11156, act='drop', rule='LIVE', amend=True, why='no live web presence: sawyerslandingnewport.com redirects to a spam page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 234 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(11277, act='drop', rule='LIVE', amend=True, why='no live web presence: only a Travel Nevada listing; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 54 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(11295, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 102 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(11581, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 114 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(12444, act='drop', rule='LIVE', amend=True, why='no live web presence: only a Visit Mendocino listing; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 98 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(12468, act='drop', rule='LIVE', amend=True, why='no live web presence: no website found; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 59 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not')
d(1963, act='drop', rule='LIVE', why='no live web presence: its old page (eureka-net.com/mikes) redirects to the Eureka Springs visitor site, and the Google result is a different business (The Hideaways on Rickety Ridge, 5.7 km away); its RoverPass listing is unclaimed')
d(6989, act='drop', rule='LIVE', why='no live web presence: no website found; the Google result is Willow Ranch RV Park, 8.5 km away; its RoverPass listing is unclaimed')
d(9871, act='drop', rule='LIVE', why='no live web presence: no website found; the Google result is Ideal Acres RV, 15 km away; its RoverPass listing is unclaimed')
d(6938, act='drop', rule='LIVE', amend=True, why="no live web presence: TA's own page for its Greenwood travel center doesn't mention an RV park, and the Google listing links only a Good Sam page; its RoverPass listing is unclaimed; Google Maps lists it at our pin with a phone and 135 reviews, which the 2026-10-01 amendment accepted in place of a website and #5 does not")
d(7925, act='drop', rule='CLOSED', why='permanently closed: Google Maps marks it permanently closed and woodwardranch.com answers 404; its RoverPass listing is unclaimed')
d(2009, act='drop', rule='CLOSED', why='permanently closed: Google Maps marks it permanently closed and redbeardsranch.com answers 403 or loops on redirects; its RoverPass listing is unclaimed')
d(1968, act='drop', rule='CLOSED', why="permanently closed: Google Maps marks it permanently closed and fortniangua.com doesn't resolve; its RoverPass listing is unclaimed")
d(5561, act='drop', rule='CLOSED', why='permanently closed: Google Maps marks it permanently closed; no website found; its RoverPass listing is unclaimed')
u(7742, act='drop', rule='NORV', why="no RV sites: riverrimresort.com now rents only cabins and guesthomes ('Frio River Cabins in Concan')")
u(7430, act='drop', rule='NORV', why="no RV sites: the church camp's own sites (sionito.org, sionitoyouthcamp.com) offer group and family lodging and never mention RV sites")
u(5261, act='drop', rule='NORV', why="no RV sites: the winery's website and sitemap have no RV page, and its old /rvpark.html answers 400")
u(5943, act='drop', rule='NORV', why='no RV sites: its website now markets only cabins and vacation homes (from $150 a night) and never mentions RV sites', hold=None, phone=None, note=None)

assert not TODO, sorted(TODO)
