# Phase 7 verification: questions for AWH

Flags from the verifiers that need someone who has been there (or a call to the operator).
Answered items move to the bottom with the answer.

## Open

## Answered (AWH 2026-10-21)

12. **129 Green Ridge State Forest (MD)** — DNR: "Roads leading to campsites are gravel or dirt.
    Four-wheel drive may be required depending on conditions." It names no site reachable
    without 4WD and gives no RV length guidance. Conditional, so neither a plain requirement nor
    a recommendation. Drop under the 4WD rule, or keep with a caution line like Flagpole?

    **Answer (AWH 2026-10-21):** "Keep #12." Kept with a caution line quoting DNR.

10. **Dam screen: four downgrades** (audit/dam_screen/decisions_pending.json; your rule of 10-21)
    - **1900 River Road Park (MO)** lakeview -> **riverview**: below Clearwater Dam on the Black
      River (rec.gov: "lies below the dam on the Black River"); the lake is behind the embankment
      9-13 m above the loops; nearest pads ~50 m from the river across a sand bank and ramp lot.
    - **4444 Pickwick Dam Campground (TN)** lakeview -> **riverview**: below Pickwick Landing Dam
      on the Tennessee River tailwater, 8 m under Pickwick Lake's pool.
    - **2530 Mix Lake Campground (CO)** lakeview -> **not waterfront**: loops are 11 m below
      Platoro Reservoir's pool, downstream of Platoro Dam; Mix Lake is 500 m W and 37 m higher,
      behind a ridge that reaches ~3100 m.
    - **14928 Lake McCumber (CA, PG&E)** lakeview -> **not waterfront**: PG&E's sites are south of
      (below) the dam; the crest stands ~6 m above the lake and the ground falls away behind it.
    OK to apply all four?

11. **3494 James N. McNally Campground (WI)**: the RV rows sit just downstream of the low
    Hickerson Roller Mill dam that makes Memory Lake. But there's no berm to speak of: the DEM puts
    the camp and the lake surface at the same ~270 m, and the eastern rows look across ~60 m of open
    lawn to the lake. Your rule as written (downstream of the dam = no lake value) would drop the
    lakeview. I'd keep it, since nothing blocks the view. Keep, or drop to the Wood River
    channel along its north edge (creek-sized, so `creekside` only if a site is on it, else not
    waterfront)?

   **Answer (AWH 2026-10-21):** "Drop #10 keep #11" - the four downgrades applied; McNally keeps lakeview.

8. **DWR's 300-ft rule vs. your WMA entries** — DWR's statewide camping rule
   (https://dwr.virginia.gov/camping-on-wmas/): "It is unlawful to camp within 300 feet of any lake
   or facility (building, boat ramp, etc.)". That collides with four entries:
   - **123 C.F. Phelps (Kelly's Ford Bridge)** and **124 C.F. Phelps (Rogers Ford)**, both
     riverfront: DWR's map shows each parking area as the boat-ramp lot, so camping in the lot
     itself looks unlawful, and a legal spot 300 ft from the ramp is unlikely to be on the river.
   - **254 Briery Creek** (lakefront: "camping/parking areas at the lakeshore") and **236 Amelia**
     (lakefront: "one on the lake"): no legal camp spot can be within 300 ft of the lake.
   - **482 Hidden Valley** (lakefront: "Two parking/camping areas right on the lakefront"): the
     only parking DWR's page names is the boat-ramp lot on the north side of the lake.
   Did DWR tell you camping is allowed in those lots when you confirmed the permits on 10-09?
   If not: 123/124 drop (no legal place to camp at the named spot), and 254/236 come down to
   lakeview at best (or not waterfront); 482 the same, or a drop if its two areas are the ramp lot.


   **Answer (AWH 2026-10-21):** "You may drop the VA WMA sites where the parking areas are
   waterfront or near a boat ramp." Dropped 123, 124, 247, 248, 254, 482; Amelia 236 kept (its
   other lots are inland, pin on inland fields) and downgraded lakefront -> not waterfront.
9. **Flagpole Knob 403 / 404 / 405 vs the 4WD rule** — DWR's own Flagpole Knob page
   (https://dwr.virginia.gov/vbwt/sites/flagpole-knob/): "Forest Service Road 85 towards the
   Flagpole Knob summit is remote, narrow, very steep, deeply rutted, and rocky. Only experienced
   overlanding/off-roading drivers should attempt this road." Not "4WD" in words, but an agency
   telling ordinary drivers to stay off it. 404/405 sit at the summit end; 403 is 0.9 mi up the
   Briery Branch end, the roughest part. The notes already say this, and the longer Switzer
   Lake/Union Springs approach from US 33 is described (by reviewers, not an agency) as easier.
   Drop all three under the Rapidan rule, or keep them because you added them knowing the road?
   **55 Hone Quarry Ridge** is on the same road (~0.5 mi up from Briery Branch Gap) and goes with them.

   **Answer (AWH 2026-10-21):** AWH drove to the three westernmost sites (55, 402, 403) in 2WD:
   kept with a caution line (road not always maintained or promptly repaired after washouts, may
   have deteriorated). The rest (406, 404, 405) appear to need 4WD: dropped. Long Run Road: from a
   video, #4-#6 (56, 57, 58) are 2WD-accessible via Little Dry River Rd: restored with the same
   caution; #1-#3 and 521 stay dropped (unconfirmed).


7. (AWH 2026-10-21: drop both; dropped via criteria_drops.py.) **Rapidan WMA, 438 (1253 Taylor Mountain Rd) and 440 (300 Cobblestone Row)** — DWR's Rapidan page:
   roads beyond the state-maintained part "are narrow and not maintained to VDOT standards and can
   be rough. A four-wheel drive vehicle recommended" (for 438: "Continue up the dirt road to the
   management area"). A recommendation, not the requirement that excluded RI East Beach. Keep both,
   or drop them for EKKO? (The page doesn't say which tract Cobblestone Row serves.)

6. (AWH 2026-10-21: has not stayed; the older A18 description was the source, and DCR now lists A18 at a 20-ft pad / 20-ft max vehicle - not suitable for EKKO. Downgraded to not waterfront, A18 sentence replaced.) **Bear Creek Lake SP (252, VA)** — your note: "There is one waterfront RV site (A18)" (stored
   lakefront). DCR's park page now says site 18 "is a tent only water and electrical site"; the
   seven Acorn E/W sites (1, 2, 3, 15-18) take equipment "up to 20 feet long" and "offer no view of
   the water"; "The only RV sites are RV 21, 24, 25, 28, 29, 30, 32, 34, 42, 44, and 45" (Black Oak
   and Chestnut loops), and Acorn is "the only campground by the lake". Did EKKO fit A18 when you
   stayed? If DCR has since made it tent-only, the entry comes down to not waterfront and the A18
   sentence goes (your 2026 closure dates are past too).

5. (AWH 2026-10-21: the site is gone; downgraded to not waterfront, note updated.) **Black Pearl Farms (757, SC Hipcamp)** — your note: "Waterfront RV site w/canoe $45+fees"
   (stored riverfront). Hipcamp's current listing sells three RV sites named "Farm View" and
   "Blue View" (the river "a short, easy walk away"); its riverside sites are tent-only. Is the
   waterfront RV site you booked still sold? If not, riverfront comes down to not waterfront.

4. (AWH 2026-10-21: been there, EKKO fits; kept, note says so.) **Manny Gordon Recreation Area (134, Pinchot SF)** — your note describes it without a size
   caveat. ReserveAmerica lists all three sites at "Max Vehicle Length: 16 ... suitable for
   tents and pop-up trailers" (20-25 ft driveways); DCNR's page says each has "parking for one
   vehicle with travel trailer". Did EKKO fit (or would it)? If not, it's a drop under the
   trailer-length rule.


## Answered (AWH 2026-10-20)

1. **Wolf Gap WV (492)**: go with recreation.gov. Fees written as $10 (a $20 Scan & Pay
   option too); AWH's no-fee note kept verbatim with a dated --Claude line.
2. **Little Fort VA (449)**: keep, as a general campground with an OHV side.

- **3. Red Haw (AWH 2026-10-20):** rewrite it. Standing rule: clearly published information on
  the campground's or agency's own site that contradicts older --AWH text may replace it in the
  note. Done: site count 76/61 -> 51/41, cutoff 2-days-prior -> 10 pm day of arrival, FCFS cash
  option removed (DNR: 'a reservation is required'; fcfs -> never). Weekend minimums kept (not contradicted).

## 14409 Ridge Manor Campground (FL, p3-31) — keep or drop?
55+ RV and mobile-home park; "units for sale", a resident application for stays of 6+ months,
seasonal/yearly lots. Nights ARE sold (claimed RoverPass, $50-55 for June 2027 — at the gate line),
but no daily rates on sale for January 2027. Kept for now and marked mostly long-stay: test 5
(sells homes) depends on whether the park itself sells the units or residents do.
- **AWH 2026-10-21: drop.** Done.

## 4774 Kelly's RV Park (FL, p3-35) — keep or drop?
"Kelly's RV/MH Park" under Fla. Stat. 513 and 723: 72 RV sites and 20 mobile homes, monthly RV rent
with eviction rules, and "Owner reserves the right of approval or disapproval of all renters"; "a
personal vehicle is mandatory". But it posts a $40 daily rate "perfect for those passing through"
and books by phone/form with a card. Kept: the approval clause reads as a blanket park rule, not an
application for a night (test 2). Say drop if you read it the other way.
- **AWH 2026-10-21: keep.**

## 556 Periwinkle Park (Sanibel, p3-38) — keep or drop?
$65-70 a night (no gateway; nearest Everglades NP 93 km) — passes the price gate only on your
--AWH note. But it also sells ~10 lots ($45k-100k) and permanent residences ($9-10k/yr), which is
long-stay test 5 ("sells homes or lots"). Nightly camping is still sold to travellers. Kept pending you.
- **AWH 2026-10-21: keep, for its proximity to a family home** (named price-gate exception, like Fort Myers / Pine Island KOA 14882).

## 4814 Williams Landing Campground (Leon Co., Lake Talquin, p3-40) — still a campground?
Leon County's Park Index lists only a boat ramp, grill, picnic area, restroom and fountain there; its
WebTrac reservations list campgrounds at Coe Landing and Hall Landing only, and a Williams Landing
campsite search returned nothing (Coe Landing returned 20). The campsite page still mentions a
Williams Landing map and bed tax. Kept for now (website now the Park Index); drop if it's gone.
- **AWH 2026-10-21: drop.** Done.

## 4731 Big Scrub Campground (USFS Ocala NF) — off-road rule
A 46-site Forest Service campground (pull-throughs, drinking water) that rec.gov calls "perennially
popular with off-road vehicle enthusiasts", with a trailhead inside giving "riders campsite-to-trail
access" to the 47-mile Ocala Centennial Trail; most of its notices are ORV regulations. I read it as
a general campground with an OHV side (like Mack Lake ORV) and kept it. Say drop if it's a riders' camp.
- **AWH 2026-10-21: keep.**

## Fort Myers exception parks closed to short winter stays (14869 Lakes RV, 14877 Sanctuary, 14868 Orange Grove)
- **AWH 2026-10-21 rule: a peak-season long-stay minimum is OK if it applies only in peak season, lasts no more than 3 months, and the note says so.** Lakes RV (Jan-Mar) kept with a note line; Sanctuary (90-night minimum Nov through at least mid-April) and Orange Grove (sells homes; no Dec-Mar nights) dropped.

### 14869 Lakes RV — 90-night winter minimum
Online, every RV rate for a January-March arrival needs 90 nights (four winter dates checked);
single nights sell April-December ($65-120), and lakesrv.com posts winter daily prices anyway.
It calls itself an extended-stay community and sells annual sites. It's in your Fort Myers
family-proximity exception, which is a price exception; the standing-minimum rule would drop a
park whose winter is closed to short stays, but winter is when you'd be visiting. Kept; minimum
recorded in booking.min_stay. Say drop if winter-only-long-stay should exclude it.

### 14877 Sanctuary RV Resort — 90-night in-season minimum (you confirmed it 2026-10-10)
November and January arrivals sell only 90-180-night terms ("90 Night min"); single "Summer Daily"
nights ($55-63, summer/early autumn) only. Kept; minimum recorded.

### 14868 Orange Grove RV Park — sells homes, no winter nights online
Titled "55+ RV & Manufactured Homes", featured homes at $34,900 and $14,900; Campspot sells
November and April nights at $74-84 but offers no December-March nights at all (1, 7 and 31-night
queries). Outside the exception this is the Ridge Manor rule (drop). Kept pending you.

### 4822 Neals Landing (Jackson County, on Lake Seminole)
No official page says there is camping: the county lists it only as a boat ramp/landing, USACE's
Lake Seminole camping list omits it, and aggregators disagree (one review: "closed for a while").
It was added on satellite evidence. Kept; drop if you'd rather not carry it unconfirmed.
- **AWH 2026-10-21: drop.** Done.

## 809 Sullivan's Camp Cacapon (WV, private) — is RV camping an afterthought?
One full-hookup RV site ($85, over the gate; no gateway within 40 km, Shenandoah 74 km) plus a $40
self-contained "boondocking" spot in an unlevel upper parking lot with no amenities ("We do not
charge per rig"), beside glamping, tent sites, a wedding/event venue and 65-guest whole-campground
rentals. No pets; every reservation non-refundable. The $40 lot keeps it under the price gate on
paper. Kept for now; I'd lean drop.
**Answered AWH 2026-10-21: drop.** Done.

## 869 North Bend State Park vs 50 River Run (WV) — overlap — ANSWERED 2026-10-21: narrow 869 to Cokeley (done)
869 "North Bend State Park" describes both campgrounds (77 sites = River Run 49 + Cokeley 28), while 50 is River Run itself (2.6 km from 869's pin). Narrow 869 to Cokeley Campground (re-pin it there), or keep both as they are? No trips reference either.

## 509 Beckys Creek WMA (WV) — designated sites, or a parking lot? — ANSWERED 2026-10-21: wma (done)
Set to `state` on 2026-10-01 ("designated sites"), from the --AWH note "Camp in designated sites only". Phase 7 (p3-58) found nothing new. WVDNR's District 3 page says only "Camping in designated areas only", and its map shows two Hunter Access Parking lots and no campsites; stream fords can cut off the inner lot. Under the wildlife-agency rule that reads as parking-lot camping. Should it become `wma` (hidden by default), be dropped, or stay `state`?

## 515 / 516 / 499 Dolly Sods boondocking sites #1-#3 (WV) — inside the 300-ft roadside camping ban? — ANSWERED 2026-10-21: KEEP (AWH has driven past them: unpaved driveways lead to clearings away from the road)
Monongahela Forest Order 21-94 prohibits "Camping within 300 feet of Forest Road 19 and/or Forest Road 75, excluding the Red Creek Campground" in the Dolly Sods Wilderness and Scenic Area. OpenStreetMap puts all three pins on those roads (515 and 516 on FR 75, near Bear Rocks; 499 on FR 19 from the Jordan Run side), and 516's --AWH note says "roadside wooded sites". The verifier couldn't see the order's boundary map, so it's unconfirmed whether the pins fall inside the covered area, and no FS page designates these sites. Keep them, move the pins to sites you know are 300+ ft off the road, or drop them?

## 815 Harpers Ferry Campground (WV, River Riders) — 11-ft tunnel on Bakerton Rd — ANSWERED 2026-10-21: EKKO is under 10.5 ft, so it fits; keep
River Riders' booking notes warn of a "1 way narrow tunnel with 11' max height in Bakerton Rd". Is EKKO over 11 ft, and if so, is there another way in? Everything else passes: four RV site classes with 30/50A full hookups, $39.99-49.99, River View sites rated 20-25 ft.

## 1220 Sunny Glen Farms / 1223 Triple L (WV, Salem) — no posted nightly rate — ANSWERED 2026-10-21: drop both (done)
Both have a working site with a phone, Google 4.4-4.5 over 22/46 reviews, and RV Life 4*/$$, but no posted nightly rate. Sunny Glen has only a "Get a Quote" form with "City Utilities Included"; Triple L says "Daily, Weekly, and Monthly rates available!" and leads with "Nurses welcome!" / "Oil & Gas Workers Welcome". Both lean workforce. Keep, or drop on long-stay test 2 (nights not visibly for sale)?

## 517 Squirrel Gap Road Parking (WV, GW NF) — camping in a developed parking lot? — ANSWERED 2026-10-21: drop (done)
Your entry: "large paved parking lot just off of US-48". The George Washington & Jefferson NF's general-prohibitions order 08-08-00-23-3 (in force to 2028-08-30) prohibits "Camping in or within 300 feet of any developed parking area or boat ramp", and the forest's dispersed page says no camping "in the vicinity of ... trailheads". No FS page designates the lot; only Campendium/The Dyrt list it. Squirrel Gap campsite #1 (401) is ~190 m up FR 344, outside the 300-ft buffer, and the five FR 344 sites stay. Drop 517? (I'd drop it.)

## 1454 McCann Campground (Village of Greenport, NY) — mostly seasonal?
The village sells a $4,850 season and $800-865 months beside a $63 daily rate, and its 2026 map (https://villageofgreenport.gov/wp-content/uploads/2026/06/Campground_Rules_Fees_and_Map-v7-6-25-2026.pdf) labels only site 31 "TRANSIENT" among the 35 RV-field sites; nightly stays are by a request form. The map is also headed "TENTS • RVS • DRY CAMPING ONLY" (hookups now recorded as none). The long-stay five tests are written for private parks; on test 4 (1 site in 10 nightly) this one would fail if the map's labels are the count. Keep it (municipal, North Fork, rare spot) or drop? I'd lean keep with a "mostly seasonal" note line, since no page says the other 34 sites never sell nights.

## 1473 Cayuga Wine Trail Campground (Ovid, NY, Campspot) — does EKKO book as a "Van"?
Its Campspot site types: $45 "Tent or Small RV Site" (max 25 ft, shared water, no electric; RV types Pop-Up/Van/Truck Camper/Tent - no Motorhome), $60 Water/Electric (also no Motorhome), and the first type that lists Motorhome is the 30A full hookup at $65 ($68 list). No gateway within 40 km (Rochester 86 km), never stayed. If EKKO (Transit-chassis) books as a Van, the $45 site makes it pass the gate; if it must book as a Motorhome, $65 is over and it drops. Which?
  - Same question at **1518 Rancho Pines** (Chestertown, NY): Campspot's only RV type ($49) accepts Fifth-Wheel/Pop-Up/Travel Trailer/Truck Camper/Van, no Motorhome; no other type lists Motorhome at all, so it may not be bookable online in a motorhome. Kept at $49 for now.

## 497 Mower Tract Dispersed Camping (WV, Monongahela NF) — pin on a high-clearance road?
The Forest Service road layer puts the stored pin on FR 227C "Reigle Overlook", maintenance level 2 "HIGH CLEARANCE VEHICLES / Road, Not Maintained for Passenger Car"; the main road FR 227 is level 4 (passenger car). Your note says reviews report no problems for 22-25 ft trailers. Re-pin to a site on FR 227, keep as is, or drop under the high-clearance rule? (I'd re-pin if you know which sites sit on FR 227.)

## 258 Falls Lake State Recreation Area (NC) — narrow to one campground?
The entry is the whole SRA and its pin sits on no campground (0.8 km from the Hwy 50 boat ramp; Rolling View 3.1 km, Holly Point 4.0 km). Your note ("Wooded campground with multiple lakefront RV sites") fits either. Rolling View: 115 sites, 80 electric, Loop A year-round. Holly Point: 158 sites, 89 electric, closed for wastewater work until 2026-11-16. B.W. Wells and Shinleaf are hike-in/group only. Narrow this entry to Rolling View (or Holly Point) and re-pin, and add the other as its own entry? Which one did you mean?

## 146 Jordan Lake State Recreation Area (NC) — split into its campgrounds?
Same shape as 258 Falls Lake: the entry is the whole SRA and the pin (near the Visitor Center) is at none of its three family campgrounds - Crosswinds (182 sites, year-round, 50A in Areas B/C, 1.7 km), Parkers Creek (250, 2.2 km) and Poplar Point (579, the largest, 1.2 km). Your note ("Many lakefront campsites") fits all three. Split into Crosswinds + Poplar Point (+ Parkers Creek), each pinned at its own campground? I'd do all three.

## 4256 Pride RV Resort (Maggie Valley, NC) — membership resort that also sells nights
Park rules: "new sites and amenities are funded through new membership sales" (no soliciting memberships); rate sheet has member/affiliate rates (Coast to Coast, AOR/RPI/Enjoy America) and "Pride Members" discounts. It also sells public nightly sites ("Open To The Public", $65, phone booking; 3-night holiday/October minimum). The 10-14 rule excludes membership/sales-pitch parks; you kept it earlier as a GSMNP-gateway park (28 km) for price. Keep or drop? (I'd drop it as a membership park, since nightly guests are what the membership sales are pitched at.)

## 4298 Bannister RV Park (Clayton, NC) — background question on the booking form
Posts $60 nightly (Raleigh gateway 17 km) alongside weekly/monthly ("Long Term Stays", $825/month incl. electric). The only booking path is a reservation REQUEST form asking "Have you ever been convicted of a felony?" and the camper's model year. Long-stay test 2 forbids a background check, but only for a park that is long-stay in character, and the share of nightly sites isn't published. Keep (nights posted with a phone) or drop (the form is a resident screen)? I lean keep with a note line.

## 4314 Whippoorwill Campground (Beulaville, NC) — horse camp?
Its Facebook page: "Whippoorwill Campground is your horse trail destination!"; Onslow County tourism: "the Equestrians' home away from home". Only directories call it a general campground (~100 sites with water/sewer). Google 4.6/51, phone 910-915-9854; no website or rate; RV Life $$. Keep as a general campground, or drop as horse-oriented? (I'd keep it unless someone confirms non-horse campers are turned away, since horse-only is the exclusion.)

## 4229 Yates Place Camp and 4225 Sunburst Campground (NC Forest Service) — tent-only now?
- **4229 Yates Place (Uwharrie NF):** the Forest Service page calls it "an attractive destination for tent camping" and never mentions RVs; only TheDyrt/Hipcamp reviews describe parking an RV at the drive-up sites. Free, primitive, vault toilet, no water.
- **4225 Sunburst (Pisgah NF, NC-215):** FS "nine primitive campsites" with "tent pads"; rec.gov "Tents must be on the gravel"; the site catalog lists no equipment or length.
Neither page says "tents only", and both have drive-up gravel sites. Keep both (my lean: keep Sunburst, drop Yates Place unless you know RVs use it), or drop as tent campgrounds?

## 3852 Hillside Campground (Evart, MI; was "Kit's Hillside Camp & Cabins") — seasonal and for sale?
Its domain is dead and Google's website link is an unrelated spam domain; Google lists "Hillside Campground", 4.9 stars / 55 reviews, phone 231-734-2643 (presence passes, RV Life $$). But Crexi/BizQuest sale listings (undated, $1.4M) describe a 20-acre SEASONAL park with 45 sites and 5 cabins, operating about four months a year, and there is no posted nightly rate or booking engine (RV Life reviews 2019/2024 paid ~$35-40/night). If it is seasonal in character it fails long-stay test 2. Keep, or drop? (My lean: keep on the nightly-paying reviews, unless you'd rather call 231-734-2643.)

## 3984 Mason County Fairgrounds Campground (Ludington, MI) — still sold to the public?
The operator's only camping page now offers just the 2026 Western Michigan Fair week registration ($150/week, exhibitor rules); nothing on masoncountyfairgrounds.com (read 2026-10-22) says public nightly camping is sold outside fair week, though an earlier read said it was open year-round except fair week and a big horse show. RV Life 5*/$$. Run by the fair association, so now `private`. Keep pending a call (231-843-8563), or drop as fair-only?
