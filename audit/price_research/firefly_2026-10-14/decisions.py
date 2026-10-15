"""Per-entry decisions of the Firefly pass (2026-10-14), read by firefly_apply.py. Keys as in
../roverpass_ops_2026-10-14/decisions.py (act price|drop|keep, fees, src, phone, name, note, booking, min_stay,
disc, add_web/drop_web, why/rule, ie). Read from pages.jsonl (ops_read.py) with ../roverpass_ops_2026-10-14/ops_view.py.
"""
D = {}


def d(i, **kw):
    assert i not in D, i
    D[i] = kw


# ---- batch 1 ----
d(455, act="price", phone="304-574-1065",
  fees=(45, 55, "RV sites $45 a night with water and electric, $50 with full hookups and $55 for a premium full "
                "hookup, for two people before tax ($15 each extra adult). Read 2026-10-14."),
  src=("https://rifrafters.com/campsites-cabins/rates/", ["DAILY Rates: per 2 people", "(taxes not included)",
       "$55.00", "Premium Sites", "$45.00", "per night hookup (water and electric)"]),
  note_add="2026 rate page: RV sites $45-55 a night for two, before tax. --Claude")
d(691, act="price",
  fees=(35, 70, "RV-usable sites $35-40 rustic, $50 with 50-amp, $60 full hookup and $70 full-hookup pull-through, "
                "per site for four adults ($8 each extra adult). Read 2026-10-14."),
  src=("https://youghlakecampground.com/camping", ["Lakeside Rustic Sites $35", "Lakeside 50 AMP Sites $50",
       "Full Hookup Pull Through $70", "Listed price is per site per night for 4 adults or family."]),
  min_stay=[{"nights": 2, "applies": "weekend"}, {"nights": 3, "applies": "holiday"}],
  booking_src=("https://app.fireflyreservations.com/Reserve/Property/YoughLakeCampground",
               ["Weekends require a minimum 2 night stay. Holiday weekends require a minimum 3 night stay."]),
  note_add="Weekends need 2 nights and holiday weekends 3 (2026). --Claude")
d(1158, act="price", phone="717-987-3244",
  fees=(40, 52, "RV sites $40 with electric and water, $49 with 30-amp electric and water, $52 with full hookups "
                "($7 more for 50-amp), for a family of two adults and three children. Read 2026-10-14."),
  src=("https://www.historicmillandcamping.com/index5255.html?id=9", ["$40", "Electric and Water", "$49",
       "30 amp Electric and Water", "$52", "Electric, Water, and Sewer", "+50 AMP available for additional $7 per day"]))
d(1219, act="price", phone="412-330-1146",
  fees=(22, 36, "Nightly $22-36 from April 15, 2026 (weekly $135-195, monthly $550-580). Read 2026-10-14."),
  src=("https://starryfieldsrvpark.com/rv-sites/", ["New rates starting on April 15th, 2026 will be as follows:",
       "Nightly:$22 – $36"]))
d(1230, act="price",
  fees=(35, 45, "Nightly $35 with water and electric or electric only, $45 with full hookups (30 or 50 amp). "
                "Read 2026-10-14."),
  src=("https://mercercountyohiofair.com/camping/", ["Nightly Rates", "Full Hookup 50 or 30 Amp: $45*",
       "Water & Electric or Electric only: $35*"]))
# ---- batch 2 ----
d(1245, act="price",
  fees=(40, 60, "Full-hookup sites $40 a night April through October, $60 November through March. Read 2026-10-14."),
  src=("https://www.galliacountyfair.org/campgrounds", ["Nightly Rate", "April 1st thru October 31", "$40",
       "November 1 to March 31", "$60"]))
d(1248, act="keep", why="county agricultural society grounds; its camping page posts no rate and its Firefly page "
  "shows none without a search (local parks need no posted rate)")
d(1293, act="price",
  fees=(50, None, "RV sites from $50 a night ($300 a week). Read 2026-10-14."),
  src=("https://atwoodlakecountrycampground.com/rates/", ["RV Sites", "Starting at", "$50 /night"]))
d(1320, act="price",
  fees=(30, 30, "$30 a day plus sales tax, water and electric or full hookup; no camping the week before or during "
                  "the county fair. Read 2026-10-14."),
  src=("https://www.jocofairin.com/camping", ["Daily Camping Rate: $30* per day - Water Electric and Full Hookup "
       "Available", "*Plus applicable sales tax"]))
d(1323, act="keep", phone="812-292-2003",
  drop_web="https://www.madison-in.gov/department/division.php?structureid=145",
  why="city campground; the city's page is gone (404) and the Firefly page, which names the camp cell 812-292-2003 "
      "and a season of April 1 to November 8, posts no rate")
d(1326, act="keep", why="county park; its rates page gives rules and a $5 reservation fee but no site rate")
d(1346, act="price",
  fees=(28, 36, "Class B (water and electric) $28 Sunday-Wednesday and $32 Thursday-Saturday and holidays; Class A "
                "(full hookup, 30 or 50 amp) $31 and $36. Primitive Class C sites $23-28. Read 2026-10-14."),
  src=("https://www.warrickcountyparks.com/pricing", ["Class A (water, 50 or 30 amp electric & Sewer) $36.00",
       "Class B (water & electric) $32.00", "Class A (water, 50 or 30 amp electric & sewer) $31.00",
       "Class B (water & electric) $28.00"]))
d(1483, act="drop", rule="OVER",
  why="over the price limit: standard RV sites $65-80 a night (gazebo RV sites $80-95), no gateway within 40 km "
      "(Rochester 75 km)")
# ---- batch 3 ----
d(1603, act="price",
  fees=(36, None, "Full-hookup RV sites from $36 a night, year-round. Read 2026-10-14."),
  src=("https://ohkentuckyrvpark.com/rates", ["RV Sites", "Starting at $36 per night"]))
d(1964, act="price",
  fees=(40, None, "Standard full-hookup RV site from $40 a night ($255 a week). Read 2026-10-14."),
  src=("https://lanternlightsrvpark.com/rates/", ["Standard RV Site", "Starting at", "$40 /night"]))
d(2000, act="price", phone="573-979-4921",
  add_web="https://www.camplife.com/campground/Cypress+Creek+RV+Park",
  drop_web="https://app.fireflyreservations.com/Reserve/Property/CypressCreekRVPark",
  fees=(35, 35, "$35 a night before sales tax and the booking fee ($210 a week, $500 a month). Read 2026-10-14."),
  src=("https://cypresscreekrv.com/", ["Click here to book your stay: https://www.camplife.com/campground/Cypress+Creek+RV+Park",
       "Daily – $35.00 *", "*does not include sales tax and booking fee"]),
  ie="its own site now books through CampLife, so the Firefly link gave way to that one")
d(2227, act="drop", rule="OVER", border=True,
  why="over the price limit: full-hookup pull-throughs $52.80 a night (50 amp; $48 with a Good Sam, veteran or AARP "
      "discount), no gateway within 40 km")
d(3028, act="price",
  fees=(20, 30, "$20 a night electric only (20, 30 or 50 amp), $25 with water, $30 full hookup; primitive $10. "
                "Read 2026-10-14."),
  src=("https://www.boonecountyfairia.com/campgrounds.html", ["Electric Only (we have 20, 30 or 50 amps available)",
       "$20 /night", "Electric & Water", "$25/night", "Full Hookups (Electric, Water & Sewer)", "$30/night"]))
d(3397, act="price",
  fees=(35, 50, "RV sites $35 (20-amp, no water) to $50 (lakeside 50-amp pull-through with water), for up to six "
                "people, before tax. Read 2026-10-14."),
  src=("https://hiles-pinelakecampground.com/rates", ["LAKESIDE SITE - PULL THRU - 50/30 AMP & WATER $50.00",
       "REGULAR SITE - BACK IN 30/20 AMP & WATER $42.00", "RV/TENT SITE - 20 AMP, NO WATER $35.00",
       "- prices include up to 6 people on the site, and use of boat launch."]))
d(4006, act="keep", why="village park; neither its page nor its Firefly page posts a rate")
d(4023, act="keep", why="city RV park; neither its page nor its Firefly page posts a rate")
# ---- batch 4 ----
d(4024, act="price",
  drop_web="https://app.fireflyreservations.com/reserve/property/runklelakecampground",
  add_web="https://app.fireflyreservations.com/Reserve/Property/RunkleLakeCamping",
  fees=(30, 45, "$30 a night with 20-amp electric, $32 with 30/50-amp electric, $45 full hookup; tent sites $25. "
                "Read 2026-10-14."),
  src=("https://runklelakecamping.com/rates.htm", ["Full Hookup Camper Sites", "30 & 50 amp", "$45 daily",
       "Electric-Only Sites", "$32 daily", "20 amp", "$30 daily"]),
  ie="its old Firefly link answers 'Property not found'; the park's own site links the current one")
d(4086, act="price",
  fees=(54, 60, "May 15 to October 15: $54 with water and electric, $60 full hookup. Read 2026-10-14."),
  src=("https://www.burlingtonvt.gov/964/North-Beach-Campground", ["Rates for May 15 through October 15:",
       "Full Hook-up Site: $60", "Water and Electric: $54"]))
d(4145, act="drop", rule="OVER",
  why="over the price limit: camper sites $65 a night with full hookups ($70 on holiday weekends; its $45 sites with "
      "water and electric are tent sites), no gateway within 40 km")
d(4845, act="price",
  fees=(25, 28, "Electric sites (30/50 amp) $25 a night plus tax, premium lakeside electric $28; primitive $20. "
                "Read 2026-10-14."),
  src=("https://www.hardeecountyfl.gov/departments-services/parks-recreation/hardee-lakes/", ["Nightly Cost",
       "Electric (30A & 50A)", "$25 plus tax", "Premium Lakeside Electric (30A & 50A)", "$28 plus tax"]))
d(4849, act="price",
  fees=(25, 45, "Sites with electric $25 a night plus tax, with electric and sewer $45; no-hookup sites $20. "
                "Read 2026-10-14."),
  src=("https://www.hardeecountyfl.gov/departments-services/parks-recreation/pioneer-park/", ["Camp Sites with Electric",
       "$25 plus tax", "Camp Sites with Electric & Sewer", "$45.00 plus tax"]))
d(4850, act="keep", why="county park; its page gives only the $2 day-use fee, and its Firefly kiosk shows no rate")
d(4858, act="price",
  fees=(45, 60, "RV sites with electric: interior $45 a night plus tax May-October and $50 November-April; "
                "waterfront $50 and $60. Read 2026-10-14."),
  src=("https://www.martin.fl.us/rv-sites", ["Waterfront RV Site Rates with Electric:",
       "Nov. 1 – April 30: $60.00 plus tax per night", "Interior RV Site Rates with Electric:",
       "May 1 – Oct. 31: $45.00 plus tax per night"]))
d(5623, act="keep", phone="218-546-5021",
  min_stay=[{"nights": 2, "applies": "weekend"}, {"nights": 2, "applies": "holiday"}],
  booking_src=("https://www.cityofcrosby.com/?SEC=A006F880-19E1-4EA5-8A60-07AA22B91DD2",
               ["There is a 2-night camping minimum on both Memorial Day and Labor Day Holiday weekends.",
                "There is a 2-night camping minimum on all weekends."]),
  why="city campground; its page gives the 2026 season (May 8 to October 11) and the reservation line but no rate")
# ---- batch 5 ----
CC = ("https://www.cameroncountytx.gov/wp-content/uploads/2026/09/REVISIONS-PARK-SPACE-AGREEMENT-9-24-26.pdf")
d(6614, act="price",
  fees=(30, 30, "$30 a night ($175 a week); fees can change for special events. Read 2026-10-14."),
  src=("https://www.muskogeeparks.org/facilities___rentals/hatbox_event_center/rv_park.php",
       ["Cost per RV site*: $30 Per Night Fee", "$175 Weekly Rate (7 consecutive days)"]))
d(6747, act="keep", why="its Firefly page is an active booking site selling RV sites by the night (#5); the rate "
  "sits behind Firefly's captcha, and RV Life rates it $$")
d(6783, act="keep", why="its Firefly page is an active booking site selling RV sites by the night (#5); the rate "
  "sits behind Firefly's captcha, and RV Life rates it $$")
d(6789, act="keep",
  why="a long-stay RV and mobile-home park that passes the long-stay rule: its Firefly page sells RV sites by the "
      "night, and on satellite (2026-10-14) its RV loop of about 20 pads outnumbers the ~10 mobile homes",
  note="Mostly long-stay: a shaded country RV and mobile-home park on E 92nd St near Stillwater, with an RV loop of "
       "about 20 full-hookup pads (20/30/50 amp) beside ~10 mobile homes. Takes nightly guests through its online "
       "booking; showers and laundry. --Claude")
d(6824, act="keep", drop_web="https://rusticrvranch.com/",
  why="its own domain no longer resolves, but its Firefly page is an active booking site selling RV sites by the "
      "night (#5); the rate sits behind Firefly's captcha, and RV Life rates it $$")
d(7197, act="price",
  fees=(30, 30, "Full hookup (no cable) $30 a day, $450 a month plus utilities; tents $20. Read 2026-10-14."),
  src=(CC, ["ADOLPH THOMAE PARK SPACE FEE SCHEDULE:", "Full Hook-Up W/O Cable:", "Daily $30.00"]))
d(7200, act="price",
  fees=(62, 88, "Standard full-hookup sites $62 a day off-peak (April-May, September-November), $75 in winter "
                "(December-March) and $88 in summer (June-August). Read 2026-10-14."),
  src=(CC, ["Andy Bowie County Park RV Fee Schedule", "Standard Daily $75.00 $88.00 $62.00",
            "***Off Peak- April 1st – May 31st and September 1st thru November 30th"]),
  note="Cameron County beach park on the Gulf at the north end of South Padre Island (across from the Convention "
       "Center); one of the few public RV camping options on the island. Full-hookup RV sites, restrooms, showers, "
       "beach access. Reservable online or by phone. --Claude")
d(7248, act="price", phone="956-761-5494",
  fees=(55, 107, "Partial hookup $55-81 and full hookup $62-107 a day by season (off-peak April-May and "
                 "September-November, winter December-March, summer June-August). Read 2026-10-14."),
  src=(CC, ["Isla Blanca County Park RV Fee Schedule", "Partial Hook-Up Daily $68.00 $81.00 $55.00",
            "Premium Daily $94.00 $107.00 $81.00"]),
  note="Cameron County's largest park at the south tip of South Padre Island: ~600 full-hookup RV sites in several "
       "loops with Gulf beach and Laguna Madre access, boat launch and lighted boardwalk. The ~577 sites inside the "
       "gate have been closed since late 2025 for a ~$12M utility rebuild that has run past its year; in October "
       "2026 the county's booking page lists 43 RV sites outside the gate as open (24 full hookup, 19 water and "
       "electric). Verify before booking. --Claude")
# ---- batch 6 ----
FFK = "its Firefly page is an active booking site selling RV sites by the night (#5); the rate sits behind Firefly's captcha"
d(7313, act="price", rf=5,
  fees=(30, 30, "RV sites $30 a night for four people, two weeks at most, plus a $5 reservation fee and a $5 gate "
                "entry fee. Read 2026-10-14."),
  src=("https://riohondo.us/spotted-sea-trout-park", ["RV Sites", "$30.00 per night 2 weeks max",
       "Reservation Fee", "$5.00", "Entry Fee", "$5.00"]))
d(7561, act="price",
  drop_web="https://app.fireflyreservations.com/reserveexternal/reserveamerica/95e9f0f2-98c7-4c9f-aee9-d4a6221d4033",
  add_web="https://app.fireflyreservations.com/Reserve/Property/HiddenPinesRVPark",
  fees=(35, 35, "Full-hookup RV sites $35 a day, every size ($200 a week). Read 2026-10-14."),
  src=("https://www.hiddenpines-rv.com/sites-rates/", ["DAILY", "$35", "Weekly", "$200"]))
d(7695, act="price",
  fees=(45, 45, "RV lots $45 a day all inclusive (electric, water, septic, WiFi, laundry, showers). Read 2026-10-14."),
  src=("https://www.palmsrvliving.com/home/amenities-xb32f", ["RV LOT RATES", "DAILY ALL INCLUSIVE", "$45.00 per day"]),
  why="a long-stay park (it leads with a first-month special) that passes the long-stay rule: a nightly rate and "
      "phone on its own site, no minimum for a daily stay, no home sales")
d(7715, act="price",
  fees=(49, 55, "Back-in standard sites (60 x 23 ft, 30/50 amp) from $49 a day, back-in pond sites from $55. "
                "Read 2026-10-14."),
  src=("https://porterstrongrvresort.com/rates/", ["BACK-IN STANDARD", "Rates starting At:", "$49", "Daily",
       "BACK-IN POND SITE", "$55", "Nightly"]))
d(7723, act="keep", drop_web="https://www.myquailridgervpark.com/",
  why=f"its own domain answers 404, but {FFK}, and RV Life rates it $$")
d(7796, act="keep", why=f"its own site renders nothing without JavaScript; {FFK}, and RV Life rates it $$")
d(8600, act="keep", why="district campground; its camping page and 2026 policies give rules and a $5 processing fee "
  "but no site rate")
d(10137, act="keep", why=f"its own site posts no rate; {FFK}, and RV Life rates it $$")
# ---- batch 7 ----
d(10505, act="price",
  fees=(30, 35, "South full-hookup sites $35 a night, north electric/water sites $30; dry tent camping $20. "
                "Read 2026-10-14."),
  src=("https://www.okanogancounty.gov/419/RV-Park", ["Camping Fees", "South RV Site (full hookup): $35 per night",
       "North RV Site (electric/water): $30 per night"]))
d(11456, act="keep", why="county park; its page gives the 114 RV sites and the office phone but no rate, and its "
  "Firefly guest portal shows none")
d(11568, act="drop", rule="LONGSTAY",
  why="fails long-stay test 5: its own site sells mobile homes ('Mobile Homes for Sale or Rent') in a 55+ home "
      "community beside the RV sites, and it posts no nightly rate")
d(11732, act="keep",
  min_stay=[{"nights": 4, "applies": "holiday"}],
  booking_src=("https://app.fireflyreservations.com/reserve/property/CalistogaRVPark",
               ["If you are booking for an event weekend, 4 nights are required, if you are booking for Labor Day "
                "weekend, 4 nights are required."]),
  why="city RV park; neither the city page nor the Firefly page posts a rate. Firefly requires 4 nights on Labor Day "
      "and event weekends")
d(11801, act="price",
  fees=(50, 50, "Full-hookup sites $50 a night per space. Read 2026-10-14."),
  src=("https://www.atthegrounds.com/facilities/rv-park/", ["Full hookups are available at every site",
       "$50 per night per space"]))
d(13091, act="price",
  fees=(40, 45, "Full hookup $40 a day with 30 amp, $45 with 50 amp (limited), for two adults; $5 per extra adult. "
                "Read 2026-10-14."),
  src=("https://campclinch.com/rates", ["Daily E/W/S 30 Amp Full Hookup $40", "50 Amp $45 (limited availability)"]))
d(13110, act="keep", why=f"its rates page lists site types but no prices ('FOR HOLIDAY RATES PLEASE CALL'); {FFK}, "
  "and RV Life rates it $$")
d(13130, act="keep", border=True,
  why=f"its own site posts no rate and RV Life rates it $$$, but Badlands NP is a gateway 27 km away, so the price "
      f"limit does not apply; {FFK}")
d(14201, act="price",
  fees=(48, 58, "2026 (May 8 - October 11): 50-amp water/electric $48 back-in and $50 pull-through, full hookup $53 "
                "back-in and $58 pull-through, for two adults. Read 2026-10-14."),
  src=("https://starlightcampground.com/rates-reservations.html", ["2026 Campsite & Rental Rates",
       "Water and Electric 50 amp, Back In", "$48.00", "Full Hook-Up 50 amp W/E/S, Pull-Thru", "$58.00"]))
d(14552, act="keep",
  why="it leads with monthly rates ($750) but passes the long-stay rule: its Firefly page sells RV sites by the night "
      "(the page takes a one-night deposit), no minimum, no home sales; Branson is a gateway 3 km away, and RV Life "
      "rates it $$")
