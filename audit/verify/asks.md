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
