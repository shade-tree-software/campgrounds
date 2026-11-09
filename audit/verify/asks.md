# Phase 7 verification: questions for AWH

Flags from the verifiers that need someone who has been there (or a call to the operator).
Answered items move to the bottom with the answer.

## Open

## Answered (AWH 2026-10-26)

1. **2640 Campo City Park (CO, local, free) — keep?** (p3-158, 2026-10-26) No official source mentions overnight RV use: neither the Town of Campo nor Baca County has a page for it, and the stored website is only a town contact page. Google Maps shows only "Campo Community Center" (4.6/31), ~60 m from the pin. The free, ~3-site, water, year-round, first-come facts come from RV Life and AllStays alone, so they were cleared and the note now calls them directory-reported. No site length is published, and the note warns of low trees. The presence rule is written for private parks. Keep with that caveat, or drop until the town (719-787-2416) confirms?
   **AWH: keep it with a caveat.** Note now says no town or county page confirms overnight RV use as of 2026-10-26.

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
- **Settled 2026-10-21 (AWH, peak-season minimum rule, feedback_minimum_stay): kept** - Jan-Mar is within 3 months; PEAK-SEASON MINIMUM line and booking.min_stay are on the entry.

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
**ANSWERED 2026-10-24 (AWH): drop** — one nightly site reads as a trial spot for prospective seasonal renters, not a campground for travellers (long-stay test 4). Done.

## 1473 Cayuga Wine Trail Campground (Ovid, NY, Campspot) — does EKKO book as a "Van"?
Its Campspot site types: $45 "Tent or Small RV Site" (max 25 ft, shared water, no electric; RV types Pop-Up/Van/Truck Camper/Tent - no Motorhome), $60 Water/Electric (also no Motorhome), and the first type that lists Motorhome is the 30A full hookup at $65 ($68 list). No gateway within 40 km (Rochester 86 km), never stayed. If EKKO (Transit-chassis) books as a Van, the $45 site makes it pass the gate; if it must book as a Motorhome, $65 is over and it drops. Which?
  - Same question at **1518 Rancho Pines** (Chestertown, NY): Campspot's only RV type ($49) accepts Fifth-Wheel/Pop-Up/Travel Trailer/Truck Camper/Van, no Motorhome; no other type lists Motorhome at all, so it may not be bookable online in a motorhome. Kept at $49 for now.
**ANSWERED 2026-10-24 (AWH): EKKO books as a MOTORHOME** wherever a park offers both (AWH was turned away from a "van" site at Fort DeSoto that EKKO fit). Cayuga dropped ($65 over the gate, no gateway). Rancho Pines 1518: re-asked below (Campspot offers no motorhome type at all).

## 497 Mower Tract Dispersed Camping (WV, Monongahela NF) — pin on a high-clearance road?
The Forest Service road layer puts the stored pin on FR 227C "Reigle Overlook", maintenance level 2 "HIGH CLEARANCE VEHICLES / Road, Not Maintained for Passenger Car"; the main road FR 227 is level 4 (passenger car). Your note says reviews report no problems for 22-25 ft trailers. Re-pin to a site on FR 227, keep as is, or drop under the high-clearance rule? (I'd re-pin if you know which sites sit on FR 227.)
- **Narrowed by the 2026-10-22 rig-length rule:** the Forest Service's own road layer calls FR 227C a high-clearance road, so "keep as is" on the strength of reviews is out. That leaves re-pin to a site on FR 227, or drop.
- **AWH 2026-10-22: re-pin to FR 227 near the FR 227C junction.** Done: 38.5705,-79.9331 (on 227C, 7 m from the junction) -> 38.56995,-79.93386, on FR 227 (level 4, passenger car) 49 m south-west of the junction, per the USFS EDW road layer.

## 258 Falls Lake State Recreation Area (NC) — narrow to one campground?
The entry is the whole SRA and its pin sits on no campground (0.8 km from the Hwy 50 boat ramp; Rolling View 3.1 km, Holly Point 4.0 km). Your note ("Wooded campground with multiple lakefront RV sites") fits either. Rolling View: 115 sites, 80 electric, Loop A year-round. Holly Point: 158 sites, 89 electric, closed for wastewater work until 2026-11-16. B.W. Wells and Shinleaf are hike-in/group only. Narrow this entry to Rolling View (or Holly Point) and re-pin, and add the other as its own entry? Which one did you mean?
- **AWH 2026-10-22: split** (rule: split a park into its campgrounds that sit at separate places, ~1 km+ apart with their own entrance; only when phase 7 runs into one). Queued as a split job after p3-125.

## 146 Jordan Lake State Recreation Area (NC) — split into its campgrounds?
Same shape as 258 Falls Lake: the entry is the whole SRA and the pin (near the Visitor Center) is at none of its three family campgrounds - Crosswinds (182 sites, year-round, 50A in Areas B/C, 1.7 km), Parkers Creek (250, 2.2 km) and Poplar Point (579, the largest, 1.2 km). Your note ("Many lakefront campsites") fits all three. Split into Crosswinds + Poplar Point (+ Parkers Creek), each pinned at its own campground? I'd do all three.
- **AWH 2026-10-22: split** (rule: split a park into its campgrounds that sit at separate places, ~1 km+ apart with their own entrance; only when phase 7 runs into one). Queued as a split job after p3-125.

## 4256 Pride RV Resort (Maggie Valley, NC) — membership resort that also sells nights
Park rules: "new sites and amenities are funded through new membership sales" (no soliciting memberships); rate sheet has member/affiliate rates (Coast to Coast, AOR/RPI/Enjoy America) and "Pride Members" discounts. It also sells public nightly sites ("Open To The Public", $65, phone booking; 3-night holiday/October minimum). The 10-14 rule excludes membership/sales-pitch parks; you kept it earlier as a GSMNP-gateway park (28 km) for price. Keep or drop? (I'd drop it as a membership park, since nightly guests are what the membership sales are pitched at.)
**ANSWERED 2026-10-24 (AWH): drop as a membership park.** Done.

## 4298 Bannister RV Park (Clayton, NC) — background question on the booking form
Posts $60 nightly (Raleigh gateway 17 km) alongside weekly/monthly ("Long Term Stays", $825/month incl. electric). The only booking path is a reservation REQUEST form asking "Have you ever been convicted of a felony?" and the camper's model year. Long-stay test 2 forbids a background check, but only for a park that is long-stay in character, and the share of nightly sites isn't published. Keep (nights posted with a phone) or drop (the form is a resident screen)? I lean keep with a note line.
**ANSWERED 2026-10-24 (AWH): keep with a note if it passes everything else.** It does (Raleigh gateway 17 km, site + phone, test 4 passes by default); SCREENING note line added.

## 4314 Whippoorwill Campground (Beulaville, NC) — horse camp?
Its Facebook page: "Whippoorwill Campground is your horse trail destination!"; Onslow County tourism: "the Equestrians' home away from home". Only directories call it a general campground (~100 sites with water/sewer). Google 4.6/51, phone 910-915-9854; no website or rate; RV Life $$. Keep as a general campground, or drop as horse-oriented? (I'd keep it unless someone confirms non-horse campers are turned away, since horse-only is the exclusion.)
**ANSWERED 2026-10-24 (AWH): keep only with clear wording that horses are not co-located near the non-horse camping.** None found (its website is now a parked domain; a Google review: 'Lots of horse activities mixed in nearby'). Dropped.

## 4229 Yates Place Camp and 4225 Sunburst Campground (NC Forest Service) — tent-only now?
- **4229 Yates Place (Uwharrie NF):** the Forest Service page calls it "an attractive destination for tent camping" and never mentions RVs; only TheDyrt/Hipcamp reviews describe parking an RV at the drive-up sites. Free, primitive, vault toilet, no water.
- **4225 Sunburst (Pisgah NF, NC-215):** FS "nine primitive campsites" with "tent pads"; rec.gov "Tents must be on the gravel"; the site catalog lists no equipment or length.
Neither page says "tents only", and both have drive-up gravel sites. Keep both (my lean: keep Sunburst, drop Yates Place unless you know RVs use it), or drop as tent campgrounds?
- **Settled by the 2026-10-22 rig-length rule (docs/campground-curation.md): keep both.** Neither agency gives a length or says tents only, so the agency is silent. A dated review caveat goes in each note if a review from the last 3 years reports the reviewer's own 23-ft+ rig fitting.

## 3852 Hillside Campground (Evart, MI; was "Kit's Hillside Camp & Cabins") — seasonal and for sale?
Its domain is dead and Google's website link is an unrelated spam domain; Google lists "Hillside Campground", 4.9 stars / 55 reviews, phone 231-734-2643 (presence passes, RV Life $$). But Crexi/BizQuest sale listings (undated, $1.4M) describe a 20-acre SEASONAL park with 45 sites and 5 cabins, operating about four months a year, and there is no posted nightly rate or booking engine (RV Life reviews 2019/2024 paid ~$35-40/night). If it is seasonal in character it fails long-stay test 2. Keep, or drop? (My lean: keep on the nightly-paying reviews, unless you'd rather call 231-734-2643.)
**ANSWERED 2026-10-22 (AWH): keep** — multiple Google reviews describe stays of one night or a weekend, so it sells nights (not long-stay in character).

## 3984 Mason County Fairgrounds Campground (Ludington, MI) — still sold to the public?
The operator's only camping page now offers just the 2026 Western Michigan Fair week registration ($150/week, exhibitor rules); nothing on masoncountyfairgrounds.com (read 2026-10-22) says public nightly camping is sold outside fair week, though an earlier read said it was open year-round except fair week and a big horse show. RV Life 5*/$$. Run by the fair association, so now `private`. Keep pending a call (231-843-8563), or drop as fair-only?
**ANSWERED 2026-10-22 (AWH): drop.** Done.

## 3826 Gilmore Car Museum Campground (Hickory Corners, MI) — per-person museum admission each night
General nightly camping open to the public Apr 1 - Oct 31 with online booking (not event-only). Sites $20 (no electric) to $50 (50 A). But every guest must buy museum admission for EACH night camped: $20 per adult, $25 on car-show days (gilmorecarmuseum.org, read 2026-10-22). One adult on the cheapest site pays $40/night; two adults $60. No gateway within 40 km (Grand Rapids 62 km), no stays. Mandatory per-night fees count toward the US$50 line, so for two adults it is over. Keep, or drop? (My lean: drop — it's over for any family of two, though you do get the museum.)
**ANSWERED 2026-10-22 (AWH): drop.** Done.

## 3924 Upper Peninsula State Fair Campground (Escanaba, MI; Delta County) — every stay by application
The fairgrounds sell general nightly camping outside the fair ($40 "General Non-Fair"; 470 sites, 120 full hookup; fair week Aug 15-23 is weekly only at $300), so it is not fair-week-only like the dropped 3984 Mason County. But every reservation goes through a "Non-Fair Special Event Camping Application" that asks which event you're attending ("Other – please specify" allowed) and is confirmed by invoice "upon acceptance" — no instant booking, and no camping season stated (upstatefair.net, read 2026-10-22). Keep, or drop as event camping? (My lean: keep — public nights are sold at a posted rate.)
**ANSWERED 2026-10-22 (AWH): keep**, with a note that the application process is probably too slow for a last-minute stay. Done.

## 3858 Bird Creek RV Resort (Port Austin, MI) — "Campers must be less than 10 years old"
Huron County's listing says Bird Creek requires campers under 10 years old (no pop-ups or tents). Is EKKO under 10 years old? Otherwise it passes as an ordinary private park: Google Maps open, 4.4 / 31 reviews, phone 989-370-2366, RV Life $ tier (Facebook only, no posted rate or engine). Its long-stay character is unclear: a county EDC page calls it a "new seasonal RV resort", while a 2023 trade article says most sites are for daily camping. (My lean: keep if EKKO qualifies, drop if not.)
**ANSWERED 2026-10-22 (AWH): EKKO is a 2023 model year**, so it qualifies: keep, with the rule in the note.

## 420 Culhane Lake State Forest Campground (Luce County, MI) — "tent and small trailer use"
- **AWH 2026-10-22 (after the rig-length rule): agency boilerplate is silent, not vague** - 99 of 115 MI DNR state forest pages carry the same phrase. Kept; no qualifying review was found anyway (ParkAdvisor's 30-ft TT review is from 2020).
The DNR describes the 15 sites as "for tent and small trailer use", posts no length limit, and says nothing about County Road 500's surface (29 mi from Newberry via M-123 and CR-500). Your note ("Several sites right on the lake") is kept; no stays recorded. Does EKKO fit, or did you note it without seeing it? (My lean: keep — "small trailer" with no stated limit isn't a cap under 23 ft — unless you know the sites are short.)
**ANSWERED 2026-10-22 (AWH): keep while it has a phone (DNR 906-492-3415), with a note to call about fit.** Done.

## 1518 Rancho Pines Campground (Chestertown, NY) — no motorhome site type on Campspot
Campspot's only RV type ($49, full hookup) accepts Fifth-Wheel/Pop-Up/Travel Trailer/Truck Camper/Van and not Motorhome; no type lists Motorhome. The operator's page (still headed "2023 Season") says nothing about rig types, and lists dry ($30) and water/electric ($38) sites that aren't on Campspot. Booking online would mean booking as a Van, the Fort DeSoto risk. Keep with a "book by phone (518-494-3645) and say it's a motorhome" note, or drop? (My lean: keep with that note — nothing says motorhomes are refused, and the phone settles it.)
**ANSWERED 2026-10-24 (AWH): keep with a note.** BOOK BY PHONE note line added.

## 3931 Angel Cove Park (Branch County, MI) — mostly seasonal? (p3-127, 2026-10-25)
**ANSWERED 2026-10-25: drop** (applied via criteria_drops.py).
The county page: "The park has a continual waiting list for waterfront sites with many of the park residents returning annually to well-maintained and highly personalized lots." It posts no nightly rate, no season and no booking method (phone 517-278-8541 only); a directory reports $40/night (June 2025). Long-stay test 2 fails if the park counts as long-stay in character, but it's a county park and the count of nightly sites is unknown (the 60 pull-throughs may be the transient side). Same shape as 1454 McCann, which you dropped. Keep or drop?

## 3756 Mack Lake ORV Campground (Huron-Manistee NF, MI) — ORV staging camp or general campground? (p3-141, 2026-10-25)
**ANSWERED 2026-10-25: keep** (a lakeside family campground with ORVs barred inside it; the trailhead is a separate area).
Toward staging camp: the name; FS "The campground is primarily used by ORV trail riders", activities "OHV Camping / OHV Trail Riding"; rec.gov "With an ORV trailhead located within the campground... a popular location for ORV trail riders". Toward general campground: 41 designated lakeside family sites (24 reservable), a day-use area with buoyed swim area, picnic tables and grills, carry-in boat access; the FS lists the Mack Lake ORV Trailhead as a separate recreation area; rec.gov "ORVs may not be used within campgrounds." Your rule: OHV staging camps out, a general campground with an OHV side stays. Keep or drop?

## 4018 St. James Township Campground (Beaver Island, MI) — keep a campground reached only by car ferry? (p3-149, 2026-10-25) — ANSWERED 2026-10-26: KEEP, ferry details in the note (done)
Drive-in once on the island (17 sites, $20/$30, Firefly online booking, 8 sites take 25-28 ft). The Beaver Island Boat Co. car ferry from Charlevoix (Emerald Isle only: 13'6" height, 46-ft length, 50 tons GVW, vehicle reservation by phone required) would take EKKO. 2026 vehicle fare "over 7'6" tall, 10' long & above" $110.41+ one way ($220.82+ round trip; call with dimensions for an exact price) plus $33.50 per adult each way. Keep or drop?

## 587 Cypress Glen Campground (Withlacoochee SF, FL) — lakeview for its one lake-view site? (wf-fl-1, 2026-10-26) — ANSWERED 2026-10-26: lakeview, note says only site 47 qualifies (done)
Your note: "in a forested setting, not directly on a lake or river" (entry: not waterfront). The Florida Forest Service's ReserveAmerica page marks one of 34 sites, RV site 47, "Type of View: Lake" (the rest "Woods"); it sits ~35-45 m from Silver Lake, high above it on a bluff, under canopy. That would make the entry lakeview (still not "on the water"). I kept your not waterfront. Change to lakeview?

## 266 Big Bend (Monongahela NF, WV) and 490 Watoga SP - Riverside (WV) — keep your riverfront? (wf-wv-1, 2026-10-26) — ANSWERED 2026-10-26: riverview for both (done)
Your notes: Big Bend "sites adjacent to the water"; Watoga Riverside "several sites back up to the river". Both are riverfront on your word, and both stay riverfront unless you say otherwise. The re-audit found nothing on the record to back either one up:
- Big Bend: recreation.gov tags no site as near water, the river-loop site photos show only woods, and the Forest Service says the river is "200 feet from campground". Under the trees, the pads plot ~25-35 m from a side channel and 60-100 m from the main river.
- Watoga Riverside: the state parks' booking system tags ~24 sites "Riverview" and none "Riverfront" (the same system does use Riverfront at North Bend). A wooded bank strip ~35-45 m wide separates the south loop from the Greenbrier.
Do you remember RV pads right on the bank (keep riverfront), or should either drop to riverview?

- **2628 Trailing Edge Park, Limon CO (p3-163, 2026-10-27):** passes your five long-stay tests ($45/night quoted for a Class C, nights booked online with a 1-night minimum, 5 of 37 sites open for a November night), but the operator's own rules are written for monthly tenants (rent due on the 1st, winter skirting), and it is a gravel lot with no office, restrooms or showers. Kept. **ANSWERED AWH 2026-10-27: keep; the note says only what the park states ("nightly and monthly stays").**

- **2596 Four Seasons River Inn & RV Park, Delta CO (p3-165, 2026-10-27):** advertises "short term and seasonal lodging", but its booking engine sells only motel rooms and tent sites, no RV rate is posted (price rests on RV Life $$), and recent Google reviews (3.2/105) describe month-long stays and long-term renters. Kept for now; drop under long-stay test 2 (nights not visibly for sale), as 2595 / 3931? **ANSWERED AWH 2026-10-27: drop.**

- **2521 Coffee Pot Spring (CO, p3-174, 2026-10-28):** missing from the White River NF's campground list and 2026 operating-dates sheet; Campendium lists it as dispersed. Kept with a dated caveat. Drop it as no longer a campground, or keep until the district confirms? **ANSWERED 2026-10-28: keep with the caveat (AWH).**

- **2486 Golden Horn Designated Camping Area, Silverton CO (p3-177, 2026-10-28):** no FS page of its own. The FS says FR 585 dispersed camping is "allowed only in designated camping areas which include Anvil, Bear and Sultan" (Golden Horn not named); the San Juan Mountains Association (an FS partner) lists "Golden Horn on the left at 2.6 miles" among "4 camping areas with outhouses". One open dirt area with vault toilets, no numbered sites; FR 585 is 2WD to here. Kept for now. Keep as an agency-designated area (the outhouse and the partner listing), or drop as not named by the FS? **ANSWERED AWH 2026-10-28: keep with a caveat.** Status line added to the note.

- **13172 Lake Fork Campground (Conejos River), CO (p3-180, 2026-10-28):** the Rio Grande NF conditions page (Oct 2026 storm) says "FSR 250 between Stunner to Highway 17 has damage - 4WD is recommended" - that is the only access road. Kept with a dated caveat because it is storm damage, not the road's normal state. Drop under the 4WD rule, or keep with the caveat until the repair? **ANSWERED AWH 2026-10-28: keep with the caveat** (all four). (p3-182: the same applies to 2530 Mix Lake, also on FSR 250 below Stunner - same caveat.) (p3-188: and to 2532 Spectacle Lake and 2534 Stunner - Stunner's other approach, FR 250 between the Alamosa Guard Station and the Science Camp, is called impassable - same caveat.)

- **2487 Little Molas Lake Campground, CO (p3-180, 2026-10-28):** no FS campground page exists (not among San Juan NF's 30 listed campgrounds or its SW Colorado Campground Guide); the agency mentions only FR 584's season ("Little Molas Lake 6/1 11/30") and a trailhead parking area. Campendium (2025-09-09) describes 10 sites with gravel pads, a 43-ft fifth wheel fitting. Designated sites can't be shown from an agency source. Keep (you may know it), or drop as an undesignated dispersed area? **ANSWERED AWH 2026-10-28: drop.** Done.

- **13174 North Fruita Desert (18 Road) split? (p3-183, 2026-10-28):** the BLM campground has an Upper unit (host, loops A-D) and a Lower unit (loops E-M, ~39.308,-108.704) ~2.9 km apart on 18 Road, each with its own loops; recreation.gov sells them as one facility (274413). Under the split rule (separate places ~1 km+, own entrance) it qualifies on distance; split into Upper/Lower entries, or keep one entry pinned on the Upper unit? **ANSWERED AWH 2026-10-28: keep one entry.**

- **2343 Sleeping Elephant (CO, p3-187, 2026-10-28):** the campground page gives parking lengths of 15-30 ft and says it "will not accommodate larger RVs"; the Arapaho-Roosevelt status table lists Max Spur 20'. Kept on the 30 with a caveat in the note. Drop it if you read the table as the current figure. **RESOLVED (AWH 2026-10-28): keep** - photos show at least a few sites fit EKKO; reviews say sites are short and unlevel, so the note says to have a backup plan.

- **2574 Swinging Bridge (CO, p3-188, 2026-10-28):** the campground sits beside Browns Park's historic Swinging Bridge over the Green River - single lane, 20-ton limit, 8 ft 6 in at its narrowest. What is EKKO's width (mirror to mirror)? Kept meanwhile, with the bridge figures in the note. **RESOLVED (AWH 2026-10-28): keep** - fits with the mirrors folded (EKKO body ~7 ft 3 in, ~8 ft 1 in with mirrors out).
- **2292 / 2293 Sylvan Lake SP, Elk Run and Fisherman's Paradise (CO, p3-188, 2026-10-28):** two loops of one park; nearest sites ~70 m apart, one shared park entrance, centroids ~230 m apart. Under the split rule they would be one entry. Merge them (one id retired), or leave as two? Both pins were ~7 km off and are now fixed. **RESOLVED (AWH 2026-10-28): merged** into 2292 "Sylvan Lake State Park" (42 sites, lakefront from Fisherman's Paradise, pinned at Elk Run); 2293 retired in removals.json.

- **2572 Tom Bennett (CO, p3-189, 2026-10-28):** same shape as Sleeping Elephant but tighter: the campground page says "parking length ranges from 15 to 25 feet" and the older facility "will not accommodate larger RVs"; the ARP status table lists Max Spur 20'. Kept with the backup-plan caveat. Drop it if 25 ft at best is too tight. **ANSWERED AWH 2026-10-28: keep with the caveat.**

- **2483 Ute (CO, p3-190, 2026-10-28):** recreation.gov notice says the gravel spurs fit "an extended cab pickup truck size (approximately 20 feet in length)"; the FS page says max RV 35 ft and the site catalog lists 28-62-ft driveways. Kept with a backup-plan caveat. Drop if you trust the 20-ft notice. **ANSWERED AWH 2026-10-28: keep with the caveat.**
- **2541 Trujillo Meadows (CO, p3-190, 2026-10-28):** the FS page calls FR 118 a "4WD Forest Road" in its trail paragraph (Los Pinos trail access); the campground directions use 2.1 mi of FR 118 with no 4WD wording. Kept. Is the stretch to the campground 2WD? **ANSWERED AWH 2026-10-28: keep with a caveat.** Road line added to the note.

- **2377 Willows (CO, p3-191, 2026-10-28):** the White River NF 2026 operating-dates table lists a 20-ft maximum site; recreation.gov's catalog shows roadside pull-outs of 30-93 ft and one 25-ft pull-through, and imagery shows open gravel pull-outs (the table gives Prairie Point the same 20, so it may be a default). Kept with a backup-plan caveat; max_rig_ft stored as the agency's 20. Keep or drop? **ANSWERED AWH 2026-10-28: keep with the caveat.**

- **208 Beartown State Forest (MA, p3-194, 2026-10-28):** your entry ("Limited number of RV spots"). ReserveAmerica now sells only one site EKKO fits: 001, the 25-ft universal-access site, which DCR asks you to book only if someone needs it or it is the last one left (003 and 004 are rated 20 ft; the rest are tent-only). Otter River was dropped for the same shape. Keep or drop? **ANSWERED AWH 2026-10-28: drop.** Done.

- **2629 Travel Port (CO, p3-169), 15565 Navajo (Tiffany) separate entry (add-co-1), 14881 Sun Retreats Estero Bay (FL):** asked in chat 2026-10-28. **ANSWERED AWH 2026-10-28:** Travel Port dropped; Navajo (Tiffany) stays separate; Estero Bay kept.

- **14374 Bear Branch RV Park (Twin City GA, p3-195, 2026-10-29):** no website, booking engine or Facebook page (old domain dead); presence rests on Google Maps alone (open, 4.8 from 39 reviews, phone 478-494-0094) and price on RV Life $$. Two Google reviews describe living there for months while working nearby; others describe overnight stays. Kept. Drop it as long-stay in character (no nightly rate posted = test 2)? **ANSWERED AWH 2026-10-29: keep, just barely.**

- **182 Cat Head Creek RV Park (Townsend GA, p3-198, 2026-10-29):** your entry (the note was only "RVLife 9.4/10 --AWH", now dropped as the rating field holds it). Recent RV Life reviews say "mostly permanent residence" (5/2025) and "a lot of full timers" (2/2026). The operator's site lists 24 sites and phone reservations but posts no rate; campers paid $50-55 in 2025-26 (right at the $50 line); no gateway within 40 km. That fails long-stay test 2 (no posted nightly rate or engine). Kept for now because it is yours. Drop? **ANSWERED AWH 2026-10-29: drop.** Done.
- **4601 Currahee RV Park (Toccoa GA, p3-198, 2026-10-29):** Facebook only (no website, no engine); "several long term folks" (7/2026), "a lot of full timers" (2/2025); campers paid $25-35 in 2026. Same shape as Bear Branch, which you kept just barely, but without Bear Branch's RV Life $$. Kept for now. Drop under test 2, or keep like Bear Branch? **ANSWERED AWH 2026-10-29: drop.** Done.

- **737 Duckett Mill (Hall County, Lake Lanier, p3-199, 2026-10-29):** your note says "Many of the 88 sites have 180-degree lake views", word for word the same as Bolding Mill's; the county's map lists 97 water/electric sites plus 14 primitive (111). Change 88 to 97 in your note, or leave it? (The site count on file is now the 97.) **ANSWERED AWH 2026-10-29: update it.** Done (88 -> 97 in the --AWH note).

- **4641 Scenic Mountain RV Park, Milledgeville (p3-203, 2026-10-29):** its website is down (scenicmountainrv.com doesn't answer). Kept: it's a Good Sam Park in the GS directory with phone 478-454-1013, and RV Life $$. One 2025 guest review says $60 (over $50 even at GS 10% off = $54; no gateway within 40 km). Keep, or drop until the site comes back / a call confirms the rate? **ANSWERED (AWH 2026-10-29): the site is live at scenicmountainrvresort.com (the stored domain was the wrong one) and Google reviews run to two weeks ago. Rates page: $50 back-in, $60 pull-through, 10% Good Sam/military off - passes on the back-in sites. Kept; website, fees, booking updated.**
- **4696 Sprewell Bluff River Ridge, Upson County (p3-203):** the stored pin is in woods south of the Flint with no pads visible; site lengths aren't posted and booking (Firefly) is behind a captcha. Kept as is (6 county RV sites, 30/50 A). Do you know where the RV sites sit, or that a 23-ft rig fits? **ANSWERED (AWH 2026-10-29): campground at 32.871252,-84.473533; Firefly quote for Jul 2027: six RV sites (1, 2, 3, 10, 11, 12), 42-80 ft, $45, 30/50 A + water. Re-pinned (~2.2 km), sites/fees/hookups set from the quote.**

- **4615 Inland Harbor RV Park, Darien (p3-206, 2026-10-30):** posts no rate ("CALL FOR ... RATES", cash or check, phone booking). Four 2026 RV Life motorhome reports say $55 (over $50, no gateway: Savannah 84 km); RV Life tier $$. Kept for now - keep, or drop on the camper reports? **ANSWERED (AWH 2026-10-30): drop. Dropped.**
- **4618 Jellystone Park Cochran (p3-206):** Campspot's 2027 rates are $51.45 Tuesday / $56.70 Saturday on every RV type (fall 2026 nights $49.50; the operator's page still says $45). Not a Good Sam Park, no gateway (Atlanta 183 km). Kept for now - $1.45 over on a 2027 weeknight; keep or drop? **ANSWERED (AWH 2026-10-30): drop. Dropped.**

- **4645 Spence Field Campground, Moultrie (p3-208, 2026-10-30):** the City of Moultrie runs it on the Sunbelt Ag Expo grounds ($35 30 A / $40 50 A since 10/2025). Every source is Expo-oriented - a Visitor/Exhibitor reservation form, an Expo holiday minimum, the Expo's lodging page. If it only rents around events it is out like Jim R. Miller Park. Kept for now; a call to 229-890-5425 would settle it. Keep or drop? **ANSWERED (AWH 2026-10-30): drop. Dropped.**
- **4697 Tally Valley County Park, Tallapoosa (p3-208):** neither Haralson County's recreation page nor the City of Tallapoosa's parks page mentions it; the only source is an undated n-georgia.com directory listing ($16 + tax, Apr 15-Dec 1, 770-574-2076); the Google Maps place has no phone or reviews and the campground can't be found on imagery. Kept for now (a dead web presence isn't proof it's gone) - drop, or keep pending a call? **ANSWERED (AWH 2026-10-30): drop. Dropped.**
- **4648 Sugar Mill RV Park, Thomasville (p3-208):** Good Sam Park, $40 nightly posted (passes). The operator serves "individual travelers ... as well as the seasonal and permanent residents"; the rules page is written for residents of "home lots" with park-model homes (blocked, anchored, skirted) and lets a resident "sell his or her home and leave it in the park" to a manager-approved buyer. The park itself advertises no homes for sale, and no count of homes vs RV sites exists. Kept for now - does it fail test 5 (home community)? **ANSWERED (AWH 2026-10-30): drop, for very poor Google reviews. Dropped.**

- **13201 Andrews Cove Campground, near Helen (p3-209, 2026-10-30):** recreation.gov lists no RV/motorhome equipment at any of its 10 sites. Trailers are permitted only at sites 3 and 9 (24 ft, though site 3's driveway reads 14 ft) and site 10 (16 ft); the other seven take tents, cars and pickup campers. So EKKO fits about one site and couldn't book it as a motorhome. Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): drop. Dropped.**

- **753 Blackwater Ranch, St. Marys River (p3-210, 2026-10-30):** your note ("Private primitive kayak-friendly sites right on the Saint Marys River.  --AWH"). The cheapest RV-allowed site is $44.84 from the host but $52.79 with Hipcamp's mandatory service fee ($54.58 with tax) - over $50; nearest gateway Jacksonville at 46 km (just past 40). RVs allowed (sites to 25/30 ft, a 34-ft hookup site); a May 2026 reviewer warns the gravel drive out of the gate is steep. Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): keep.**
- **4550 Bussey Point Campground, Thurmond Lake (p3-210):** recreation.gov permits only "Pop up" equipment on all 14 sites - no RV, motorhome or trailer, and no driveway lengths. Same shape as Andrews Cove. Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): drop. Dropped.**

- **4561 Lake Conasauga Campground (p3-211, 2026-10-30):** recreation.gov permits an RV (motorhome) only up to 21 ft, on 20 of 29 sites (trailers to 25 ft on 18); the FS page says "RV maximum length 24 feet". EKKO books as a 23-ft motorhome, so the catalog says no and the FS page says yes. Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): keep, with a tight-fit warning (rec.gov's campsite photos look closer to the FS 24 ft). Done.** **AWH 2026-11-02: flag sites within 2 ft of EKKO as tight on the Availability page. Done.**
- **4567 Low Gap Campground, near Helen (p3-211):** recreation.gov lists no RV/motorhome type at any of its 13 sites (trailers to 24 ft at four sites, 26 ft at one); unlike Andrews Cove, the Forest Service page says "the recommended size of a RV is 28 ft". Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): keep.**
- **755 Pragma Farms (p3-211):** your note ("Single full-hookup RV site on a 4-acre pond.  $60+fees/night.  --AWH"). The Hipcamp listing's access is set to "4WD recommended" (EKKO isn't 4WD; no trip here), and the price is $54-60 from the host, $63.83-69.83 with Hipcamp's fee - over $50, no gateway (Jacksonville 175 km). Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): drop. Dropped.**
- **13373 James Dykes Memorial Park (Dykes Landing), Bleckley County (p3-211):** a 2022 county ordinance allows free first-come camping (7 days in any 31) on an open gravel boat landing on the Ocmulgee - no marked sites, water or toilets. County-designated, but it's the landing lot itself. Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): keep with a caveat. Done.**

- **13203 Upper Chattahoochee River Campground, near Helen (p3-212, 2026-10-30):** recreation.gov lists no RV/motorhome type. Trailers are capped at 10 ft on most sites (14-16 ft on three), and only sites 15-16 - parallel pull-offs with 39-41 ft driveways - take a trailer of any length; sites 9-11 are tent/car only. The FS page gives no RV length. Closer to Andrews Cove (dropped) than Low Gap (kept). Kept for now - keep or drop? **ANSWERED (AWH 2026-10-30): keep, with a caveat that only two sites fit. Done.**

- **Bonefish Bay Resort, Marathon (Keys re-screen, 2026-10-30):** real and open (Google 4.3/333, phone 305-289-0565 matches its site), with 17 full-hookup RV sites, but no posted RV rate ("Call for Motel Room & RV Site Rates and Reservations"; its online engine sells only cabins). RV Life rates it $$$$. The presence rule accepts "an RV Life $ or $$" in place of a published rate, a limit that came with the price gate, which the Keys zone lifts. Does $$$/$$$$ count as the price indicator in the Keys? Recorded as a skip (no rate) for now; yes would make it an add, and the same for any later Keys park in that position. **ANSWERED (AWH 2026-10-30): yes, RV Life $$$/$$$$ counts as a price in the Florida Keys.**

- **Sugarloaf Key RV Resort & Cottages, Summerland Key (Keys re-screen, 2026-10-30):** the same park as Sun Outdoors Sugarloaf Key (ex-Lazy Lakes, 311 Johnson Rd), but Blue Water took it off the Sun Outdoors brand on 2025-04-15 and runs it independently; no source says whether Sun keeps a stake (its rules page is still a copy of Sun's). Added as not-Sun, since the skip is on brand. 7-night minimum for Dec 1 - Mar 31 check-ins, kept as time-of-year (Quartzsite precedent). $217.80 in season incl. $15 resort fee; lakefront on a 7-acre saltwater pond; Google 4.5/482. Drop it if you count a former Sun park as Sun. **ANSWERED AWH 2026-10-30: "Sugarloaf can stay" - kept (15583); a park that has left the Sun brand is not skipped as Sun.**

- **1249 Jackson County Fairgrounds, Wellston OH (p3-213, 2026-10-30):** the fair board's site ((740) 384-6587) publishes only fair camping - July 1-20, $550 for 19 nights, spots leased yearly with a waiting list - plus a "Halloween Campout". Nothing sources the note's $25/night, FCFS or year-round; one Campendium review (April 2024) reports full-hookup field sites at $15/$20, so some ordinary nights may exist, but no operator page says so. Same shape as Elbert County Fairgrounds (held). Keep with a caveat, or drop? **Dropped 2026-10-31 (AWH: a fairground stays only with a published rate).**
- **14295 Freedom Valley Campground, New London OH (p3-213, 2026-10-30):** passes the gates ($40 weekday / $50 weekend for 2, plus a $15 season membership charged once; Google 4.7/211), but its About page "invites men over 21 to join our diverse group of Seasonals" and its rules say "Absolutely no nudity in non-designated areas" - likely a men's clothing-optional campground, like Cedar Hills WI (skipped 2026-10-21). Bookings are by request form, closed for the season when read. Keep or drop? **Dropped 2026-10-31 under AWH's standing calls.**

- **1300 River Bend Family Campground, Caledonia OH (p3-214, 2026-10-30):** at the line on price ($50.00 weeknights on ResNexus, $55 Fri-Sat; Google 4.4/278; no gateway), but mostly seasonal: of 231 RV sites only the 16 water/electric sites (91W-106W) are sold by the night (7%); the other 215 are seasonal full-hookup lots. With its ~25 nightly primitive tent sites it is 41 of ~256 (16%). Every RV night is a 2-night minimum. Does long-stay test 4 (1 site in 10 nightly) count RV sites only (drop) or all sites (keep)? **ANSWERED AWH 2026-10-30: "River Bend Family Campground tent sites can count toward the nightly number" - kept (41 of ~256, 16%).**
- **15471 Shelby / Mansfield KOA (p3-214, 2026-10-30):** kept for now: the cheapest motorhome site is $49 on May and September 2027 weeknights but $66 on a June 2027 weeknight - over US$50 all summer. No gateway within 40 km, not a GS Park, Google 4.5/470. The gate has used the cheapest real RV night, which passes; say if a summer price over the line should drop it. **ANSWERED AWH 2026-10-30: "Shelby keep it".**

- **1231 Ross County Fairgrounds (OH, p3-218):** the fair's site says the campgrounds are 'available for rental throughout the year' at $30 a night (motion of May 1, 2024), but publishes no hookups and no way for a non-fair camper to book; hookups and ~200-site count come from directories only. Same family as Elbert County and Jackson County. Keep with a caveat, or drop? A call to 740-775-5083 would settle it. Meanwhile kept. **ANSWERED AWH 2026-10-31: keep** (a published rate + phone is enough for a fairground). Under the same rule: 1249 Jackson publishes only the $550 fair lease, 2647 Elbert reads CLOSED on every rate - neither has a nightly rate; re-asked. **ANSWERED AWH 2026-10-31: 1249 Jackson dropped; 2647 Elbert kept, marked temporarily closed.**
- **1240 Piedmont (OH, p3-218):** joins 1228 Atwood Lake: reserve.mwcd.org needs a human captcha pass for per-site rates, lengths and season. **Piedmont done 2026-10-31 from AWH's saved pages: 27 reservable sites, $39/$49 confirmed, lakefront -> not waterfront. Atwood 2026-10-31 from AWH's saved grid: 332 reservable, 294 take 23 ft, $27-99 confirmed. Lakefront kept: AWH read the map view and Area F (sites 604-702, all reservable, $27-43) is definitely waterfront. Closed.**

- **1274 Adventure Bound Pleasant View (OH, p3-219):** $44 midweek shows beside $85 on the same row, so it may be a promotion. If so the real night is $78-85 and it fails the price gate (no gateway, not a GS Park, Google 3.7/386). Kept for now. **AWH 2026-10-31: rates start at $79; dropped.**
- **14292 Bluegrass (OH, p3-219):** has an 'Extended-Stay RV Sites for Traveling Workers' page; nightly rates posted ($50, GS member $45), nightly share unknown. Kept; worth a look against the workforce exclusion. **AWH 2026-10-31: stays.**
- **597 South Bass (OH, p3-219):** island campground reached by Miller Ferry at about $124 round trip with two adults, on top of the site. Kept. **Settled by the Beaver Island ruling (AWH 2026-10-26: keep, ferry details in the note) - the note carries the Miller Ferry details.**

- **1299 Clinton Lake (OH, p3-220):** no posted rate, no booking engine; looks long-stay ('close-knit community', monthly and seasonal rates listed by others, packed settled rows, third-generation campers). If long-stay it fails test 2, and RV Life $$ doesn't stand in. Google 4.6/175; a call to 419-585-3331 would settle it. **AWH 2026-10-31: dropped, reviews so-so.**
- **14297 Hickory Lakes (OH, p3-220):** $45 posted, but rules are written for seasonal owners (shed limits, 2014-or-newer) with ~150 packed units; nightly share may be under 1 in 10. Kept for now. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**
- **1244 Friendship Park (OH, p3-220):** its page also lists Sam Kerr RV Campground ($35, 30/50A, sewer; call for availability), not located. Can't tell which cluster the pin is on, so split undecided. Kept as one entry. **AWH 2026-11-02: cannot find Sam Kerr either. One entry stays.**

- **1266 Kenisee (OH, p3-221):** 300 sites; only ~12-25 appear sold nightly (4-8%, no published count), 'settle for a season', sells RVs set up on site, reviews mention long-term residents. $50 posted, Google 4.6/188. Test 4 looks failed; a call to 440-466-2320 would settle it. Kept for now. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **1292 Shady Trails (OH, p3-222):** stored 'mostly seasonal' has no source; no operator page or booking site; only rate is Good Sam's undated 'From $35'. Google 4.5/79 reads like overnight use ('a couple nights', 'every weekend'). Kept for now as an ordinary park; on test 2 it would go. 937-393-5618. **AWH 2026-11-01: dropped, reviews suggest mostly seasonal with many permanent campers.**

- **1014 Malabar Farm (OH, p3-223):** ODNR: 'outfitted for equestrian camping', '15 sites designated for equestrian camping'; ReserveOhio site 001 says 'available to all campers', pads 43-60 ft, campers report 36-ft trailers. Horse camps are out, general campgrounds with horse sites are in; this is a horse camp that admits others. Recommend drop. Kept for now. **AWH 2026-11-01: dropped, no separate horse and general areas found.**

- **1313 Timashamie (OH, p3-223):** no posted rate, no engine; operator leads with 'SEASONAL SITES ARE AVAILABLE!', tightly packed lots; a 2023 camper paid $35 a night. If long-stay it fails test 2. Google 4.4/125. Kept for now; 330-525-7054 would settle it. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **1241 Village Green (OH, p3-223):** public $45 daily, but a 2025 camper says 'mainly populated with seasonal campers', some with moss on them; share unposted, test 4 unmeasured. Kept for now; 440-224-0310. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **14306 Walnut Creek (OH, p3-223):** a 7/2026 motorhome review (4 of 10, 'Will not return') opens with a warning about the road in, Blacksmith Hill, and RV Life's API cuts the text there. Read it before taking EKKO; EKKO is not 4WD. Other 2025-26 reviews, incl. a motorhome, raise nothing readable. Kept. **AWH 2026-11-01: dropped, reviews indicate mostly full-time residents.**

- **1242 Sally Buffalo (OH, p3-224):** village park, no published rate (only ~$450/month, WOSU 2015); WOSU describes oilfield workers with no two-week cap, a 2007 review says 3 of 4 areas are permanent; imagery shows three packed lots. Village page doesn't say it takes ordinary nights. Google 4.4/468. Evidence is old; recommend drop unless 740-942-3213 says nightly. Kept for now. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **14318 Big Bear Lake (OH, p3-225):** $40 posted, Google 4.7/187, but lease-based: numbered lease sites 1-335 with 'one camp site for the year', members sell campers and improvements on their lots, leaf-off shows packed trailers. Overnight blocks look like ~25-35 sites, near or under 1 in 10 by a rough map count. Recommend drop. Kept for now. **Dropped 2026-10-31 under AWH's standing calls.**

- **13345 Charles Mill (OH, p3-225):** Eagle Point (electric with spigots, sites 400-612) and Main Camp (mostly full hookup) have own entrances either side of the causeway, ~800 m across the water, ~1 km by road: right at the split line. Per-area rates sit behind the captcha. Left as one entry; pages saved from a browser would allow a split. **AWH 2026-11-02: saved the booking calendar: sites 400-612 $30-56, the rest $30-87; the engine doesn't name the areas. Split queued (split-9).**

- **14307 Sandy Springs (OH, p3-226):** site is behind a bot check, so nothing was re-read. Stored $45 is an October rate, riverview $50, riverside $65; a summer rate over $50 wouldn't show. Google 4.9/207. A look at sandyspringscampground.com rates, or a saved page, would settle the gate and the riverside row. Kept for now. **AWH 2026-11-01: keep.**

- **1373 AOK (IN, p3-226):** Google 3.7/219, well below RV Life 5*, and the only readable snippet says 'some maybe full time residents'. $35, daily/weekly/monthly. You judge reviews by what they say and most were blocked; drop if they read poorly. Kept for now. **AWH 2026-11-01: dropped, under 4 stars and borderline long-stay.**

- **13346 Seneca Lake (OH, p3-226):** Marina Point (199 full-hookup sites, own gatehouse on SR 313, 1.3 km across the water) would be its own entry if it sells nights. Stored text says seasonal-only from a search excerpt; imagery fits; engine is behind the captcha. Left out. **AWH 2026-11-02: nothing called Marina Point on the engine, which lists the park as Senecaville Lake. Stays left out.**

- **1371 Covered Bridge (IN, p3-228):** Google 3.9/61, mixed: small close sites, shower stalls without locks, 'need a mow', also 'peaceful, clean', 'inexpensive'. Rates page 404s; last posted 2021 $32 W/E, RV Life $$ avg $32. Kept; your call on the reviews. **Dropped 2026-10-31 under AWH's standing calls.**

- **1318 Elkhart County Fairgrounds (IN, p3-228):** run by the Elkhart County 4H Fair association; no page says county-run. Stored local unconfirmed. About 3 months blacked out in 2026. Kept under the fairground rule. **AWH 2026-11-02: unknown, leave as is.**

- **1086 Hardy Lake (IN, p3-228):** Wooster's on-water sites are $14 primitive, 'primarily to serve fishermen'; Shale Bluff is the main campground above the water. Does the entry's rating follow Wooster? **Resolved 2026-11-01 (wf-in-1): lakefront on site 155.**

- **1380 Robinson's Whitewater (IN, p3-230):** temporarily closed after the August 2026 flood, no reopening date. Owner's listing says 'daily, weekly, seasonal and permanent camping', a June 2026 camper says 'a lot of people live at the campground', imagery shows settled units; no posted rate, no engine. Long-stay test 2 fails if that is its character. Google 4.6/273, warm. Recommend drop; kept for now. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **15432 Richmond KOA (IN, p3-230):** passes at $45.89 only on 30-amp back-ins KOA calls 'Perfect for pop-ups', offered to a 23-ft motorhome search. Next is $54.11, then $67+; no gateway. Google 4.6/628. Kept for now. **AWH 2026-11-02: an engine-offered site counts. Kept at $45.89.**

- **1363 Old Mill Run (IN, p3-230):** $46.73, about 1 night site in 7. Newest review: '90% of the sites are used by what looks like full time residents... looks like a run down mobile home park'. Others warm; Google 4.5/280. Kept for now. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **1367 Walnut Ridge (IN, p3-231):** $50 at the line ($55 for 50-amp), Google 4.3/129. About 113 of 160 sites priced as seasonal (~29% left, by subtraction). Reviews: 'Mostly permanent sites. We were put right next to maintenance building', 'We will never return', 'Many of the sites appear to be long term guests'. Sits beside an RV dealership. Recommend drop; kept for now. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **1370 White Oaks (IN, p3-231):** $50 weekdays at the line, Google 4.5/179. Operator says bathhouses are in rough shape, laundry closed; a review says cold water only. Kept for now. **Dropped 2026-10-31 under AWH's standing calls.**

- **1369 Amishville (IN, p3-232):** no operator site (amishville.com parked), no operator rate, Good Sam 'from $31' undated. Recent reviews: 'very few full hook-up sites that aren't occupied by people living there full time'; 'monthly payers who live there'; 'Never, ever staying here again'. Google 4.3/259. If long-stay, test 2 fails. Recommend drop; kept for now. **Dropped 2026-10-31 under AWH's standing call (on the fence, mostly seasonal and iffy).**

- **1320 Johnson County Fairgrounds (IN, p3-233):** run by a member Fair Association; no filing found and nothing says who holds the grounds. Stored local left, same question as 1318 Elkhart. $30 passes either way. **AWH 2026-11-02: unknown, leave as is.**

- **1341 Lake Waveland (IN, p3-233):** pin moved to the loops in wf-in-3 (2026-11-01), value not waterfront; still no operator rate (camper report $30, undated). A call to 765-435-2073 would settle both. Kept. **AWH 2026-11-02: drop. Dropped.**

## 174 Blythe Island Regional Park (GA): your not waterfront, or lakeview? (wf-ga-1, 2026-11-01) — ANSWERED 2026-11-01: lakeview; RVs seen along the lakeshore in photos from across the lake (done)
Stored not waterfront rests on your note ("some sites may hav a water view, but this is not confirmed"). The county prices sites 1-13 as "Lakeview" at $45 against $42 for the wooded sites. Canopy hides the sites on imagery, so nothing confirms or refutes it. Recommend lakeview if you recall a view at the low-numbered sites; otherwise it stays.

## 4623 Lake Tobesofkee Claystone (GA): does the campground's own loop road block lakefront? (wf-ga-2, 2026-11-01) — ANSWERED 2026-11-01: yes; lakeview stays, rule added to the curation doc (done)
Sites 40-45 are sold as "RV WF"; the nearest is ~45-50 m from shore across the loop road and an open slope. Stored lakeview stays under the road-between rule. It would read lakefront only if a low-traffic loop road does not count.

## 725 Paulk Park (GA): does your lakefront stand under the new loop-road rule? (wf-ga-5, 2026-11-01) — ANSWERED 2026-11-01: AWH says lakeview, loop road; applied
Your note says "25 lakeside RV sites on a 10-acre lake", so the stored lakefront stays. On imagery the pull-through rows run ~40-65 m (east ends) to ~100 m (west ends) from shore across open lawn and the campground's loop road. Under your 2026-11-01 rule that would read lakeview, but you have been there and I have not.

## 597 South Bass Island (OH): does lakeview stand? (wf-oh-2, 2026-11-01) — ANSWERED 2026-11-01: lakeview, filtered view in reserveohio photos
Your note says RV sites "are set back a ways from the water", so I left lakeview alone. On leaf-off imagery the closest RV pads, 126 and 129, are ~40-50 m from shore through trees, the electric block 100-250 m back in woods, with no open sightline found. It reads not waterfront unless you remember a view.

## 15364 Leafy Oaks (OH): does a campground's own swim beach count as day use? (wf-oh-2, 2026-11-01) — ANSWERED 2026-11-01: own swim beach is day use; not waterfront stays
Operator-sold "Waterfront" sites 311-323 back onto a ~0.6 ha swim pond across ~15 m of grass and a roped sand beach. Left not waterfront under the no-day-use rule. If the campers' own beach doesn't block, those sites earn pond.

## 567 West Branch (OH): does your not waterfront stand? (wf-oh-3, 2026-11-01) — ANSWERED 2026-11-01: lakeview, filtered view in reserveohio photos; applied
Your note says wooded loops, not on the shoreline, so the value stays. On the ODNR map and leaf-off imagery, lake-side pads read about 20-35 m through thin woods with no road between (a rough scale reading). Say if you remember any lake-side sites worth lakefront.

## Also open, 2026-11-01 (raised in chat, logged here)
- **1294 Shadow Lake (OH):** packed with parked rigs, nightly share unpublished, $45, Google 4.7/87; kept. **AWH 2026-11-01: keep.**
- **15591 Maple Grove (OH):** reviewers say "space is tight", nobody reports a 23-ft rig, no limit posted; kept under the posted-limit rule. **AWH 2026-11-01: keep; overhead imagery and Google review photos show room for EKKO.**
- **13347 Clendening / 1238 Pleasant Hill (OH):** reserve.mwcd.org captcha; saved pages would settle 93-99 nightly (lakefront) and Pleasant Hill's per-site tags. **AWH 2026-11-02 rule: both stay lakeview unless a page turns up.**
- **4671 Broad River / 14379 Clay Hill (GA):** Firefly "RV Site - Water Access" units behind reCAPTCHA; Broad River's fees also open. **AWH 2026-11-02 rule: both stay not waterfront unless a page turns up.**
- **4561 Lake Conasauga:** Availability page hides all sites on rec.gov's 21-ft motorhome limit; recommend leaving it, alternative is a "tight" flag within 2 ft. **Done 2026-11-02 (AWH): `TIGHT_MIN_FT` = 21 shows those sites as tight.**
- **3900 Bond Falls (MI):** two areas ~4 km apart, pin below the dam; split? Held until answered. **AWH 2026-11-02: Google reviews suggest EKKO fits both campgrounds. Split queued (split-10).**
- **`header-icon-bar`:** merged branch only AWH can delete. **2026-11-08: no such branch locally or on GitHub; closed.**

- **2658 Molas Lake (CO), wf-co-4:** the town's site PDF calls P32 "waterfront... RVs up to 23 ft" under a header saying "under 23 ft", and says over 23 ft belongs in the view sites. If EKKO fits P32 it's lakefront (pad ~17 m over open shore); held at lakeview. **AWH 2026-11-02 rule: unsure goes down without asking. Stays lakeview.**
- **2469 Cement Creek (CO), wf-co-7:** Campendium: "nothing larger than 20ish feet" (2022), a 25-ft trailer fit one site (2021), Loop 2 cars and vans only; no posted limit. Kept, tight; note now says so. Drop if that's too thin for EKKO. **AWH 2026-11-02: unclear pad size = keep with a caveat. Kept; caveat in the note.**
- **2388 Elk Wallow (CO), wf-co-8:** Campendium and a Dyrt review (10/2020) give a 22-ft max vehicle; allstays says 30 ft. No agency figure read. Kept unless an agency source caps it. **AWH 2026-11-02: unclear pad size = keep with a caveat. Kept; caveat in the note.**
- **2357 Blue River (CO), wf-co-16:** rec.gov says "tents and smaller trailers"; catalog driveways 10-20 ft on the river sites, only 009 lists 23 ft+, while imagery shows spurs ~15-20 m long. Kept, value held at riverview. Drop if the catalog lengths are right. **AWH 2026-11-02: unclear pad size = keep with a caveat. Kept; caveat in the note.**
- **2590 Drake (CO), wf-co-17:** private, no website (domain parked), no rate, Google 3.9/98, listed for sale in 2026, nightly vs seasonal row unknown. Fails the price-and-presence test on what's on file; kept 10-26 with a caveat. Recommend drop. **Superseded: it passed the private gate (RV Life $$, Google presence), but AWH's 2026-11-02 under-4-stars rule drops it at Google 3.9/98. Dropped.**

- **4185 Big Eddy (ME, p3-237):** bigeddy.chewonki.org refuses scripted requests (Cloudflare). Saved pages (rates, site map) would settle the rate, the RV sites and riverfront vs riverview. Stored riverfront left in the meantime. Search excerpts of its pages say maximum trailer 30 ft and no water or sewer at sites, and a Campendium camper paid $40 in Aug 2024, not stored because the operator has a page. **AWH 2026-11-02: sent the map and booking page. Settled: rate, nightly RV sites, riverfront kept.**
- **657 Seawall (ME, p3-239):** stored `coastal woods` came from your note, which says the sites "are not waterfront". Route 102A and the picnic area lie between the sites and the shore, so your highway rule points to `not waterfront`. Change it? **AWH 2026-11-02: stays `coastal woods`; only a local road between is probably OK (Seawall, Blackwoods yes, Dunewood no). Rule softened in the curation doc.**

- **3243 Lil' Bit of Country RV Park (IA, p3-271):** the website's amenity checklist includes a '55-plus' tag; no policy text, booking page or review repeats an age rule, and RoverPass sells single nights to anyone. Kept with no note line. Is a stray '55-plus' tag enough to treat it as age-restricted? **AWH 2026-11-04: 55-plus is never a drop on its own. Kept, with a note line naming the tag.**

- **13541 Smidt Campground, Titonka (IA, p3-275):** stored as city-run, but nothing read shows the city runs it (own Gmail, Facebook and Google phone; the city just lists it). No operator posts a nightly rate; one 2020 review says almost everyone was there for work at $500 a month, open through winter. Fall imagery shows ~15-20 units on ~80 pads. Google 4.8/47. Kept as local. If it is private, it has no posted price and leans workforce: drop? **AWH 2026-11-04: drop if private. Private (taxed parcel 16-09-202-008, sold 2018, per ATTOM). Dropped.**

- **2721 North Shore, Lake McConaughy SRA (NE, p3-278):** camping is on the open beach, reached only by sand two-tracks through the dunes. No page I could read says whether a 2WD motorhome can get in or warns about getting stuck (outdoornebraska.gov, visitkeithcounty.com and ilovelakemac.com all blocked automated reads), so it is kept with no flag. Have you driven Lake Mac's beaches, or should beach-only camping on sand be treated like a 4WD recommendation and dropped? **AWH 2026-11-04: driving on sand or open beach is not safe for EKKO. Dropped, with 2724 Omaha Beach, 2735 Sandy Beach, 2713 Martin Bay, 7151 Padre North Beach, 11321 Lone Rock, 11679 Oceano Dunes, 11415 SB Cove, 7110 Cedar Canyon, 7655 Magnolia Beach.**

- **14516 Deer Ridge (IA, p3-268):** mostly seasonal; held because AWH had kept it. **AWH 2026-11-04: drop. Dropped.**
- **Sand rule, still open (2026-11-04):** 2725 Otter Creek (Lake McConaughy: 10 Basic sites in a 'sandy-beach camping area'), 6101 Confederate (MT, Canyon Ferry: north side is beach camping, south side sites suit smaller RVs), 10135 Cisco Beach (UT, Bear Lake: ~59 primitive sites strung along the beach). Each needs a read of what the sites sit on before a drop. **2026-11-07: not a question for AWH any more** - under the 2026-11-05 clarification (bare open beach = drop, maintained packed surface = keep) these are my reads to make and report.
- **2678 Bridgeport SRA (NE, p3-284), sand rule:** five sandpit lakes; imagery shows no developed loop or pads, camping strung along sand tracks around the lakes, and open sand at the waterline in the main shore areas (NGPC's magazine: 'The Beaches of Bridgeport'). The official description is Cloudflare-blocked; reviews say RVs camp there (sites far apart) and none mentions getting stuck. Kept, lakefront, until a read of the tracks settles it. (2026-11-05: under AWH's clarification the question is whether those tracks are maintained packed roads to packed sites, or bare beach.) **2026-11-07: my read to make and report, as with 6101/10135.**

- **Merritt Reservoir sand driveways (p3-287, 2026-11-05):** ReserveAmerica lists 'Driveway Surface: Sand' for every site at 2716 Boardman Creek and 2717 Cedar Bay (and Willow Cove, most of Beed's Landing). They are developed numbered loops with electric pedestals, and NGPC's photos show packed sand-gravel pads and loop roads - not beach camping. Does a packed-sand pad and loop count as driving on sand for EKKO? Kept for now; Willow Cove (9 sites, not in the DB) held on the answer. **AWH 2026-11-05: packed gravel/sand pads via a maintained packed gravel/sand road are fine; the concern is the bare sand of an open beach. Kept; Willow Cove released to vet.**

- **Rosebud Casino RV Park (2876, SD, p3-288, 2026-11-05):** the RV park has no Google listing of its own; the casino's listing is 3.8 over 864 reviews (gaming, hotel, restaurant). I kept it, reading that as the casino's rating rather than the park's. RV Life 7.75 over only 8. Drop it on the casino's rating? **AWH 2026-11-07: drop - done.**

- **Tuxedo Park, Crete (2841, p3-290, 2026-11-05):** the city page says the main entrance crosses a '3 ton bridge'. A new concrete bridge opened in 2021, so the posting may be out of date, and there is a back entrance off Idaho Road. Kept, with a note line sending EKKO in the back way. OK, or drop? **AWH 2026-11-07: keep.**

- **Battle Creek Municipal Park (2772, p3-292, 2026-11-05):** the city's parks page doesn't mention camping, and a Cowboy Trail site says 'two campsites' against our ~18 electric sites; only a tourism stub lists it. Kept for now. Drop, or keep until someone rings City Hall (402-675-2165)? **AWH 2026-11-07: keep with a caveat - caveat line added.**

- **Otter Creek, Lake McConaughy (2725) - sand rule update (p3-294, 2026-11-05):** the '10 Basic sites' don't exist: ReserveAmerica has no Otter Creek loop and NGPC's site inventory maps none there (the old note probably mixed it up with Sandy Beach Campground at Lemoyne). What is there: open sand beach south of the ramp road (driving onto sand) and a dirt-and-grass clearing under cottonwoods north of the creek with ~5 trailers, which no source names as designated sites. I'd drop it under the sand rule. Drop? **Dropped 2026-11-05 under AWH's clarification (only camping is bare open beach).**

- **Miller Creek, Lewis and Clark SRA (15612, lead, 2026-11-05):** added as Basic camping (NGPC's 2026 guide lists it; 2022 imagery shows a trailer in a pull-off), but the brochure icon says 'Non Reservable Tent Camping', a 2021 reviewer advises a small rig or tent (rough dirt road from the west, mud after rain) and a 2026 Google reviewer calls it tent-only. Kept with the fit caveat in the note. Keep, or drop as tent-only? **AWH 2026-11-07: drop - done.**

- **Jayhawker RV Park, La Harpe KS (14543, p3-300, 2026-11-06):** sells daily, weekly and monthly stays with an 11 a.m. check-out, Google 4.1/65, but its rules page is written for residents (mail via a P.O. box, deliveries held at the office, proof of liability insurance, 'lessee' throughout). Kept. Drop as mostly residential? **AWH 2026-11-06: keep.**

- **Lake Afton Park (2156, Sedgwick County KS, p3-309, 2026-11-06):** the county park rules say 'Operating a vehicle more than 1-1/2 tons is prohibited unless operated by request of the county'. Read literally that bars every motorhome (EKKO is ~5 tons), so it probably targets trucks on park roads; the park sells RV permits with hookups. Kept. Treat it as a truck rule, or drop? **AWH 2026-11-07: keep - read as the truck rating class (medium/heavy trucks), not vehicle weight; no note line.**

- **El Dorado SP Boulder Bluff (13955, p3-310, 2026-11-06):** the Equestrian Loop's 22 water/electric 50 A sites each have a corral, but campitks sells them as 'RV Site,Tent Site,Trailer Site' and no page says horse-only. Kept and counted (as with 15624 Tuttle Creek South Randolph). If it's a horse camp, the entry becomes the 21 primitive Pintail sites with no hookups. Keep, or treat as horse camp? **AWH 2026-11-07: drop - horse camps are out unless the horse area is separate from the campground. Done.**

- **Camelot RV Campground (2038, Poplar Bluff MO, private, p3-317, 2026-11-07):** posts $56 a night, no gateway within 40 km and not a Good Sam Park, so the price gate would drop it. But the operator itself gives 20% off ($45) to Good Sam, FMCA, AARP and Escapees members, seniors, military, veterans and first responders. Kept for now. Does an operator's own member discount lift the gate the way a Good Sam Park's 10% does, or drop it? **AWH 2026-11-07: keep it.**

- **Unionville City RV Park (1952, MO, p3-316, 2026-11-07):** the town's website lapsed to casino spam, so nothing online describes the park any more; the only trace is a Campendium phone (660-947-2438) next to the city office's 660-947-2437. Kept as a town park (public land is exempt from the presence rule). Keep, or drop with no page left? **AWH 2026-11-07: keep with a caveat - caveat line added.**

- **The Last Resort RV Park (2070, Warsaw MO, private, p3-319, 2026-11-07):** mostly an annual park ($220/month plus electric, by application) with about 16 of ~130 sites sold by the night at $45 ($65 holiday weekends) on its own engine; 'No Full Time Living'. Passes all five long-stay tests narrowly; Google 4.9 from 12 reviews; occupancy couldn't be checked. Kept for now. Keep, or drop as mostly seasonal? **AWH 2026-11-07: keep.**

- **Pomme de Terre State Park - Hermitage (1847, MO, p3-320, 2026-11-07):** Loop 400 basic sites H409-H412 sit 35-45 m from the lake over open sandy shore, ~4-5 m above normal pool, with no road between. Stored lakeview. Upgrade to lakefront? **AWH 2026-11-07: lakefront, as long as that shore is not a dedicated day-use beach (it isn't; the swim beach is elsewhere) - set.**

- **Mellon Acres Event Center RV Park (1961, Lawson MO, private, p3-320, 2026-11-07):** a wedding/event estate that lists 21 full-hookup RV lots; its RV page blocked the verifier, Google lists it as a wedding venue (4.8, 97 reviews) and no recent review mentions an RV stay; RV Life $$ (~$39). Kept for now. Keep, or drop as not really selling ordinary nights? **AWH 2026-11-07: drop - done.**

- **Show-Me Rest RV Park (1960, Butler MO, private, p3-321, 2026-11-07):** no website (Hipcamp page 'coming soon'), no posted rate (RV Life $$, avg ~$28), Google 4.7 from 108. One review mentions a work crew staying 'for the next few months'; winter imagery shows ~12 rigs in 19 sites. Kept. Keep, or drop as long-stay in character (it would then fail the posted-rate test)? **AWH 2026-11-07: drop - done.**

- **Red Cedar RV Park (1965, Bolivar MO, private, with a motel, p3-321, 2026-11-07):** no operator website; the only listing is an unclaimed RoverPass page (now cleared); camper-reported $28 a night (Campendium), RV Life $$ / 4.5 from 37, Google 4.3 from 137, phone answers. Kept under the camper-reported-rate rule. Keep? **AWH 2026-11-07: drop - done.**

- **Soggy Bottom Campground (14558, Cameron MO, private, p3-321, 2026-11-07):** operator site is live (23 full-hookup sites, phones), but rates are quoted by email and a mandatory gate fee is unpriced; only RV Life's $$ tier indicates price; Google 4.6 from 118. Kept. Keep, or drop for no posted price? **AWH 2026-11-07: drop - done.**

- **Bass' River Resort (1997, Steelville MO, private, p3-322, 2026-11-07):** priced per person: two adults on the cheapest hookup site pay $51 before tax ($14.50-20.50 per adult + $22 per hookup site), $1 over the US$50 gate; nearest gateway St. Louis at 111 km; not a Good Sam Park, and no posted member discount. Google 4.6 from 1,494, RV Life 4.0 from 13. Kept for now, pending the price-cap question (2026-11-07: whether to retire the cap and restore the 307 price-only drops). If the cap stays, the Google tiebreaker is close (4.6, not 4.7+). **AWH 2026-11-07: price cap stays as-is (no restore). Dropped - $1 over, 4.6 under the tiebreaker, loud-area quiet hours 2:30-6 am.**

- **Bayview Campers Park (2077, Hannibal MO, private, p3-323, 2026-11-07):** no posted nightly rate and no booking engine, phone only; reads as mostly seasonal ('Camp With Us for the "Rest" of Your Life!', set-up units with decks, sheds and private docks; reviews talk about summer seasons). A recent reviewer's two tries to book two weeks went unanswered (new 2025 owners say the phone line was down). Google 4.3 from 56 under its new name, Berry's Lakeview Campers Park. Kept for now. Drop as mostly seasonal with no posted price (as with Show-Me Rest / Soggy Bottom)? **AWH 2026-11-07: drop - done.**

- **Bevier RV Center (1992, MO, private, p3-323, 2026-11-07):** posts no rate ('Call our office'); its ResNexus booking engine exists but walls bots, so it went unread; RV Life $$ (avg $34), Google 4.3 from 303. Kept under the booking-page-is-both-indicators rule. Keep? **AWH 2026-11-07: keep.**

- **Blue Mountain Campground (1986, Branson MO, p3-323, 2026-11-07):** the stored website and its $69/$79 rates were a different Blue Mountain Campground (Catskills NY) - both cleared. No operator site exists; set the website to the park's Facebook page (Google's link) and phone 417-338-2114. Good Sam Park, Branson gateway 12 km, so no price gate. (FYI, no decision needed.)

## Re-check of every older ask (2026-11-08)
Nothing here is open. The last three items that were mine to do are done: 6101 Confederate
(beach side out under the sand rule; kept on the developed loop, lakefront -> lakeview), 10135 Cisco
Beach (units sit on a strip behind the beach on a dirt track, kept) and 2678 Bridgeport (graded
sand-dirt roads around the lakes, kept). The splits it queued (258, 146, split-9 Charles Mill,
split-10 Bond Falls) were done 2026-10-22 / 11-02.

## New asks (p3-326, 2026-11-08)
- **Ozark Country Campground (2028, Branson MO, private, p3-326):** kept. $60 a night passes only on the Branson gateway (7 km); Google 4.3 from 227, RV Life 4.5 from 140. But it leans long-stay: the operator runs "a long term section… open all the time", a reviewer puts ~50 of ~100 sites as residents, and the office email is @workforcehousingllc.com. The website is stale (footer ©2015) and carries a hidden spam link. Keep or drop?
- **Powell's Creekside Haven (2043, MO, private, p3-326):** still temporarily_closed. The operator banner "TEMPORARILY CLOSED FOR MAJOR RENOVATION" has been up since at least 2025-04 (Wayback), with no reopening date; the site's pages were last edited 2024-09; the cabins are listed on Airbnb. Google shows no closed label. Kept as temporarily closed with a caveat (standing rule); drop it if two years means gone.
- **Answered (AWH 2026-11-08):** 2043 Powell's Creekside Haven dropped (private, closed ~2 years); 2028 Ozark Country dropped.

## New asks (p3-333, 2026-11-09)
- **Castor River CA (13813, MO MDC):** the pinned camp is a gravel loop with ~6 back-in pads and tables at the multi-use trailhead off Route Y. MDC's map labels a camping symbol there 'Horse Camping Area (Trail Head)' (a second symbol ~250 m NE may be a separate loop). No MDC page restricts camping to riders and the area page lists general 'Designated Camping Sites'. Kept; drop if it is a horse camp? (Trace Creek Camping Area, split to 15639, is unaffected.)
- **Coldwater Access (14006, MO MDC):** no mapped site, lot or GIS point; brochure: 'Primitive camping is permitted along interior roads'. The only road is a single-lane dirt track across an old field, no gravel pad, may be muddy after rain. Kept with a caveat (Archangel/Bonnots Mill precedent); drop if a pad is required? Cedar Bluff Access (13980) is similar but has a ~15 x 25 m gravel pull-off lot.
- **Cobb Ridge Recreation Area (1922, Mark Twain NF):** kept as a general campground with an OHV side (45 sites, showers, host, trailheads are separate day-use areas), but the Forest Service says most visitors come for the Chadwick motorcycle/ATV trails. Drop as OHV-dominated?
- **Parking-lot camping at MDC areas (p3-334):** dropped 13897 Cross Timbers Access, where MDC allows camping only 'in the Northeast corner of the parking lot' (a boat-ramp lot - like Bird's Blue Hole). Kept 13874 Dark Hollow Natural Area and 13763 Charlie Heath, whose brochures say 'Camping is allowed on or adjacent to all graveled area parking lots' and whose area pages list 'Designated Camping Sites' with an MDC GIS camping point beside each lot. Drop those too?
- **Answered (AWH 2026-11-09):** 13813 Castor River dropped (no obvious distinction between the horse camp and the general camp; Trace Creek 15639 stays); 14006 Coldwater kept, no pad required, caveat added; 1922 Cobb Ridge kept with a caveat (riders, engine noise).
- **Answered (AWH 2026-11-09):** 13874 Dark Hollow and 13763 Charlie Heath kept - lot-adjacent camping stays where MDC marks designated camping points; a camping allowance inside a ramp/parking lot (Cross Timbers, Bird's Blue Hole) is still a drop.
- **I-49 RV Park (14586, Archie MO, private, p3-340):** one night on the cheapest site a 23-ft rig fits is $48.93 on most dates but $51.50 on November dates (dynamic pricing; the $39 'Standard' rate needs 7 nights). On a November weeknight ~60% of ~137 RV sites were taken, most likely extended stays; the park markets monthly stays to travel nurses and construction/pipeline crews, and its rules read residential (heated hose by Nov 1, skirting approval). It still sells a big nightly block (44 open nightly sites that night, 103 in June), so it passes the 1-in-10 test easily. Google 4.2 (184), highway noise mentioned. Kept for now - keep, or drop as mostly long-term + borderline price?
