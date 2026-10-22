# Criteria follow-ups from phase 7

Entries a verifier found may fail the inclusion criteria. I decide these (standing rules let
me drop and report); each needs the research named before a verdict.

## Montana (mt-N batches)
- **6156 Silos, Canyon Ferry (MT)** (mt-4): ownership private -> federal (Reclamation land under a concession). Reclamation is re-bidding the concession (usbr.gov/gp/mtao/canyonferry), so operator, website (thesilosmt.camp) and Campspot booking may change for 2027.
- **6085 Ruby Creek (MT, BLM)** (mt-4): BLM page now thin; the derived 50-ft max, water, toilets and FCFS can't be confirmed. Not on rec.gov.
- **6232 Summit, Marias Pass (MT)** (mt-4): Helena-Lewis and Clark NF, not Flathead (website fixed); derived reservable/rec.gov cleared (no listing); FCFS and the 35-ft max unstated.
- **6127 Lewis & Clark RV Park (MT, private)** (mt-3): for sale ('Due to health issues, we have made the unfortunate decision to sell our RV Park. We will still be opening in March for 2026', operator site Wayback 2026-03-06). The live site refused connections from the cloud on 2026-10-22 (read fine 2026-10-16). Re-check it operates in 2027. $40-45 incl. tax, under the gate.
- **6234 North Shore (MT, USFS Kootenai)** (mt-3): inherited federal booking row (reservable on rec.gov) looks wrong: not on rec.gov and the FS page offers no reservations; probably FCFS, unstated.
- **278 Many Glacier (MT, NPS)** (mt-3): fits, but only 13 of 109 sites take up to 35 ft (most driveways 'will not accommodate towed units over 21 feet'); book one of those. NPS 109 sites vs rec.gov catalog 103.
- **6251 Lid Creek (MT, USFS)** (mt-3): rec.gov 'The West Side Reservoir Road is narrow with many switchbacks. Not suitable for larger RV's.' Paved; kept for a 23-ft rig.
- **6227 Grizzly (MT, USFS Lolo)** (mt-2): DROPPED 2026-10-22 (criteria_drops.py). FS page: 'Trailers, motorhomes and tow vehicles not recommended due to the narrow and rough road.'
- **6226 Grasshopper (MT, USFS)** (mt-2): set temporarily_closed from the FS banner 'Closed due to Sand Creek and Bobcat Lakes Fires' (page updated 2026-08-28); the forest's alerts list no closure order, so it may have lifted. Re-check and lift.
- **6095 Fish Creek State Park (MT)** (mt-2): the campground is really Big Pine Fishing Access Site inside the park (https://myfwp.mt.gov/fishMT/fas/39754101); Forks FAS also in the park, unchecked. 'Primitive Campsite', 23-ft trailer limit, 'Difficult Accessibility'. Name/website/FCFS unresolved.
- **6096 Horse Prairie (MT, Reclamation)** (mt-2): Reclamation never mentions drive-in sites, length, FCFS or stay limit; inclusion_evidence leans on The Dyrt; website's rec.gov link is the reservoir gateway, not a campground.
- **6218 Dunn Creek (MT, USACE)** (mt-2): renamed from 'Dunn Creek Flats' to rec.gov's name. Derived year_round unstated (rec.gov rate seasons Apr 1-Nov 30); inclusion_evidence's 'free year-round' is out of date ($10 peak, reservation-only). USACE pages 403 from the cloud session.
- **6082 Galena Gulch (MT, BLM)** (mt-2): derived year_round unstated; BLM gives only the fee period Apr 1-Nov 30.
- **6228 Hood Creek (MT, USFS)** (mt-2): concessionaire ExplorUS on rec.gov vs Rocky Mountain Recreation Company on the FS page.
- **6122 Bolster Dam Campgrounds (MT, City of Plentywood)** (mt-1): no official page at all (plentywood.org is a history page); every fact and the phone 406-765-1700 rest on aggregators; sizes disagree (18 sites vs 10 power/water + 3 dry, 2018 review). Local, so not a presence drop; needs a city source.
- **6094 Clark Canyon, Lewis & Clark (MT, Reclamation)** (mt-1): the inherited federal booking row (reservable on rec.gov, 180-day window) looks wrong: Reclamation describes a self-pay station and rec.gov gateway 131 is not reservable and lists no Lewis & Clark facility. No official fee, site count or season; the note's ~$30 is reviews only; a 2022 review says the lower tier fits ~22 ft.
- **6219 Afterbay (MT, NPS Bighorn Canyon)** (mt-1): reservations by phone through Yellowtail Market, contact email crow-nsn.gov (run by/for the Crow Nation?); NPS's park fee program suspended 2018, so the inherited senior/access discount is doubtful.

- **14312 James Creek RV Resort (PA)** — $50 base rests only on our own note; RJourney blocks
  plain HTTP and showed no rates with the park closed. Re-quote when 2027 booking opens.
- **525 Grindstone (VA, USFS)** — closed for 2026 (no reopening date). `booking.reservable: true`
  came from note prose, but every rec.gov rate season since 2022 is "First-come, First-served"
  with walk-in prices. Re-check booking when it reopens; the USFS page currently 404s.
- **940 Tall Pines / Chesapeake Bay KOA (VA)** — possibly mostly seasonal, on secondary evidence
  only: a 2026-10-10 camper review on koa.com says "the cg is almost all seasonal/fulltime. There
  is one section remaining that is transient." The family has stayed (--AWH). Needs the operator's
  own word (site map / call) before any verdict.
- **474 Big Bend boondocking sites (VA, GW NF)** — the forest's dispersed rules say "Dispersed
  camping is not allowed in the vicinity of developed recreation areas such as campgrounds,
  picnic areas, or trailheads" (fs.usda.gov/r08/gwj/recreation/camping-cabins); the spot is a
  former picnic area that is now an overlook, and the site details rest on TMBtent/boondocking
  listings. Needs the ranger district's word (540-432-0187) on overnighting there.
- **255 Bath County Recreational Campground** — kept by AWH 2026-10-11 as an FCFS utility area with
  no posted fee; p3-20 found no official site count, size limit or rate either (DWR: "Primitive
  Camping Only", "a small fee"). Stands on AWH's call.
- **476 Crooked Creek WMA** — one of its two parking areas is "near the old concession building";
  DWR's 300-ft rule (building/boat ramp) may bar camping there. The East Fork lot is unaffected.
- **763 Burton Family Farm (Hipcamp)** — kept: sites 1, 3 and 10 are 2WD; Hipcamp marks 6, 8, 9
  "four-wheel drive recommended" (note says so). Not the access road, so not the Rapidan case.
- **478 Hog Camp Gap** — GWJ rules bar dispersed camping "in the vicinity of developed recreation
  areas such as ... trailheads"; the FS Mount Pleasant trailhead parking is ~0.25 mi past the gap.
  No FS page bars the clearing by name; widely used. Kept.
- **8 Fauquier Horse & Campground (Hipcamp)** — listing contradicts itself on hookups (overview:
  "hookups for water and electricity"; lakeside site text: 4 x 30A + 8 x 50A; amenity flags: no
  electric, no water). Left as AWH's note had it (no hookups). Host question.
- **447 McClintic Point** — every site listed at 21 ft, and the FS says "All equipment must fit on
  the space provided"; under the ~23-ft floor. Kept on AWH's own note ("will probably handle a few
  feet more"). Its two pages disagree on drinking water (rec.gov seasonal; FS none).
- **1108 Jamison Mill** — ownership federal -> local (Franklin County runs it on Corps land; same
  as Glen Lyn). Now county-reservable; the old FCFS/USACE claims were wrong.
- **239 Oronoco** — Modern Campground (2023-10-01) reported a GWNF proposal to make it a $14 fee
  campground with water and marked sites; no official page says whether it was adopted. If it
  was, the $0 fee and dispersed rules are stale. Inclusion rests on Campendium alone. Call the
  Glenwood-Pedlar district (540-291-2188).
- **472 The Pines / 237 Walnut Flats** — FS says only "small recreation vehicles can be
  accommodated", no length; 23-ft fit unconfirmed.
- **759 Seven Islands (Hipcamp)** — $54 base, over the $50 gate; AWH added it, so kept.
  **761 Private Paradise** is $46.75 only under a 15% discount (list $55).
- **MD non-resident camping fee** — Elk Neck's DNR camping page: "non-Maryland residents will be
  charged an additional $1 fee per night" (now `fees.nonresident` on 659). 21 other MD parks'
  fee notes say "no out-of-state camping surcharge" (the 10-12 pass); no other park page read so
  far says either way. Check the booking site's price for a non-resident before changing them.
- **650 Point Lookout** — booking site's reservable dates: Hoffman's/Malone Apr 1 - Oct 31, Tulip
  to Nov 29 (2026); the manual season says no closing date posted. Booking site lists 71 sites
  in three loops (Conoy, under restoration, absent): check whether "bayfront" rests on Conoy.
- **129 Green Ridge SF** — sites near the Potomac / Fifteen Mile Creek (DNR) but the entry is
  pinned at HQ, not waterfront; a forest-wide entry. Plus asks #12 (4WD).
- **975 Island Resort** — $85 base, kept on the gateway rule (Ocean City 17 km). Seasonal share
  unknown: "We have booked all seasonal sites for the 2025 camping season", monthly $1,600.
- **437 Weston / 235 White Oak Mountain (VA WMA)** — neither pin is at a parking lot (437: DWR's
  lot is at the end of the WCS access road; 235 has 16 lots). Neither has water/ramp at the pin.
  437 is now named Weston Wildlife Conservation Site (DWR's name).
- **Price gate, p3-26:** 977 Lake Somerset ($60) and 972 Bar Harbor ($85-95) carry --AWH notes
  (exception); 970 Sun Outdoors Ocean City ($91-328, a Sun brand the sweeps skip) is in Ocean City
  (gateway). All kept.
- **63 New Germany** — 24 of 28 RV sites list a 20-ft max; four list 30 ft. The one electric site
  (#34) is the host's, so electric is unset while the manual fees carry an electric +$9.
- **825/829 Pocomoke** — booking site's park-wide rates ($19.50 / $25.50) match neither area's
  DNR figures; the entries keep DNR's.
- **MD non-resident fee, more evidence (p3-27):** the booking site's rate tables for Cedarville,
  Martinak and Hollofield run exactly $1 above DNR's published base ($19.50/$25.50 vs
  $18.50/$24.50), footnoted "do not reflect ... surcharges (holiday/weekend/residency)";
  Swallow Falls matches DNR. Still unresolved for the 21 "no out-of-state surcharge" notes.
- **Seasons (manual, from booking site, p3-27):** 830 Cedarville "Open through Oct 25 2026",
  Hickory Loop Apr 3 - Oct 31 2026; 424 Martinak Mar 27 - Nov 1 2026, Mar 26 - Oct 31 2027.
- **828 Swallow Falls** — only ~a dozen of 65 sites take over 20 ft; the electric sites are 20 ft
  (tent/pop-up only). EKKO's choices: non-electric 25-35 ft, or full hookup 40/42A.
- **1149 Cosca** — electric outlets under repair (WebTrac notice, 2026-10-21).
- **Price gate, p3-27:** 974 Bayshore ($80), 981 Roaring Point ($63+ for 30A) carry --AWH notes;
  15441 DC/Capitol KOA ($78) is 25 km from Baltimore (gateway). All kept. Bayshore may be
  mostly seasonal (waiting list), no split published.
- **827 Susquehanna** — DNR's 2022 camp sheet: "Out-of-State Residents, add $1 /night" (third MD
  park pointing at the $1 non-resident fee); also a Golden Age Pass discount Sun-Thu.
- **Potomac-Garrett SF (43, 41, 42, 44)** — DNR says nothing on road condition or unit length;
  inclusion rests on AWH's firsthand notes. 43: Lostland Run Road closed at Campsite 22 (bridge).
- **1150 Watkins** — "we do not offer RV camping ... Class B and Class C camper vans are
  permitted": EKKO qualifies. Open Thu noon - Mon 11 am only.
- **ADD lead: Jonathan Dickinson SP, Pine Grove campground** — 90 sites, full hookups, 40 ft
  (Reserve Florida loop PG, facility 81); no entry (373 is the River Campground). Vet + add.
- **586 Gamble Rogers** — beachside loop (half the sites, the basis of the coastal-dunes call)
  closed since 2026-06-23 for a project, no reopening date; riverside open. In the note.
- **14432 Grape Hammock / 14424 Lakeport** — long-stay parks kept on the five tests (nightly rate
  posted with phone; no counts; homes not sold). Grape Hammock's nightly sites are rustic, RV fit
  unstated. Lakeport $50 base at the line.
- **4749 Lake Victor** — only link was an unclaimed RoverPass listing (removed); stands on Google
  (33 reviews, phone) + RV Life $$. Note's hookups/24 sites/pool unconfirmed.
- **386 Burns Lake (NPS Big Cypress)** — rec.gov: "primarily used by hunters and off-road vehicle
  users", has an ORV parking lot/backcountry access, no ORV use in the campground. Kept as a general
  NPS campground with an OHV side (cf. Wolf Den Run 87, an ORV park, dropped). 14 sites (rec.gov) vs 15 (NPS).
- **4720 Coldwater Equestrian** — the "closed until further notice due to Hurricane Isaias tree
  damage" banner is CURRENT, not 2020: Isaias is a live October 2026 storm (2026 reuses the 2020
  name list; Escambia County declared an emergency, evacuations in effect 2026-10-21). Status set
  temporarily closed 2026-10-21.
- **4729 Dinner Island Hammock Camp** — FWC: "campers or small RVs", no length; 23-ft fit unstated.
- **4746 Fisheating Creek Outpost** — ownership private -> state (policy_ref none): a Cape Leisure
  concession in FWC's Fisheating Creek WMA "for" FWC, by analogy with concessions on federal land.
  So the private $50 gate no longer applies ($43 + a $5/person entry fee). Standing 2-night minimum
  recorded (engine refuses 1 night on ordinary Tuesdays).
- **4818 Escambia County Equestrian Center** — 75 RV sites are "part of our event facility", events
  have priority (24 h vacate notice), marketed as a "horse motel"; no rates posted; whether a
  no-horse, no-event RVer can book is unstated. Call 850-941-6042.
- **4730 Dinner Island Kowechobe Camp** — FWC: inundated sites, best Nov-Apr; the note's "may
  require 4x4 in summer" is not FWC's (no agency 4WD statement), left in the note.
- **4848 Donald MacDonald** — county calls them "Electric sites"; derived water: true unconfirmed.
- **679 Flamingo** — concessioner booking; inherited federal 180-day window shows but doesn't apply.
- **4721 High Bluff (Lake Talquin SF)** — ReserveAmerica site details list "30/50" electric + water
  on 14 of 19 sites, against the campground alert and FDACS ("no electricity or water"); recorded none.
- **4794 Johnston Springs** — $65 (GS $58.50), kept on the Walt Disney World gateway (28 km); rate
  table undated (2022 footer); sells monthly-annual stays and park models (owners background-checked).
- **370 John Pennekamp** — park: most sites take 40 ft; booking site lists up to 62 ft; max_rig_ft unset.
- **4820 Lake Stone (Escambia Co.)** — human-checked fees $18-20.25: $20.25 is the non-resident
  rate, residents a flat $18 -> could be 18/18 + nonresident surcharge $2.25/night (manual, not
  overwritten). County table "set as of April 1, 2021".
- **4741 Long Pine Key / 679 Flamingo** — concessioner-booked (flamingoeverglades.com); the inherited
  federal 180-day window displays but doesn't apply. Consider a policy_ref for the Everglades concession.
- **388 Midway** — NPS page shows "Page In-Progress"; rec.gov is the only website for now.
- **HURRICANE ISAIAS (Oct 2026) storm closures — RE-CHECK SOON.** Set temporarily_closed 2026-10-21:
  197 Topsail Hill (FSP banner "Effective Oct. 21, 2026 ... closed due to Hurricane Isaias") and 4720
  Coldwater. Other panhandle parks verified before 10-21 may also be closed but are not marked;
  lift both statuses once the parks reopen. Also 4855 Easterlin Park temporarily_closed through
  2026-10-31 for road repaving (not the storm) — re-check after 11-01. And 163 Highlands Hammock:
  family campground closed for renovation since 2026-04-03 (youth camp only), no reopening date.
- **4744 The Glades / 4767 The Hideaway** — dropped, but their water leads stood: Glades "along the
  Caloosahatchee River", Hideaway sells "waterfront sites" on a spring-fed pond.
- **4836 Otter Springs (local)** — ottersprings.com dead (hosting error; empty on 2026-10-15 too), no
  county/operator page; open/closed unverifiable online. Call 352-463-0800. Not dropped (a local park;
  a dead website is not a closure).
- **4728 Panther Pond** — only 1 of 16 sites takes an RV (016, "RV up to 50ft", soil pad, Wildcow
  Grade limerock road). 4727/4728: FDACS "Keri Tower Road is closed" since 2024-11-22; whether either
  camp uses it is unstated.
- **14383 Pine Lake RV Park** — rules: "NO FEMA Campers, RVs without holding tanks ... School buses,
  Vans are permitted"; "RVs older than 10 years must be inspected". EKKO is a van-chassis Class C:
  probably fine (the rule reads as camper vans), unconfirmed. Good Sam derived false -> true (operator).
- **4844 Torry Island (Belle Glade)** — the city's pages were down (CivicPlus outage) on 2026-10-21, so
  no Isaias check was possible; re-check belleglade.gov/torry.
- **14398 Sunny Shores** — kept: $50 + tax (at the line), 55+ except travelling nurses/military/police,
  36 RV sites vs 8 MH spaces, nothing for sale; markets to snowbirds and annuals.
- **4731 Big Scrub (USFS Ocala)** — kept as a general campground with an OHV side (46 sites, the
  Mack Lake ORV reading), but rec.gov calls it "perennially popular with off-road vehicle enthusiasts"
  with a trailhead giving riders campsite-to-trail access to the Ocala Centennial Trail. AWH 2026-10-21: keep.
- **4710 Gilchrist Blue Springs** — Reserve Florida sells 36 units with sewer; park page says 23
  campsites, 30 amp. Sewer cleared; call 386-454-1369. Construction banner since 2025-10-29 (no water
  activities, port-o-lets); camping still sold.
- **4856 Pahokee** — city rates page offline 2026-10-21 (host security takedown); re-check the rate.
- **13382 Blue Spring (Econfina, NWFWMD)** — CampLife needs a free login to see availability; kept
  under the 2026-10-14 softening (the District publishes the price, free, and a phone). No site
  lengths published; 23-ft fit unconfirmed.
- **14436 Blackbird's Hideaway** — rigs over 10 years old need photos emailed for approval; Campspot
  $25/$35 vs the policies page's $45-65 (soft-opening?) - re-check.
- **633 Little Talbot** — only 4 sites take 23 ft (#013, #014, #016, #021, 30 ft).
- **4859 Clay County Fairgrounds RV Park** — current county pages present the 48 hookups only for
  event renters; Hipcamp listing off since 2026-10-10; only the FY26/27 fee schedule (read
  2026-10-11, now 403) and the old note show nights for travellers. Call 904-284-6378 x2.
- **13377 Dead River Landing** — CampLife's RV type omits "motorhome" (District page says RVs OK);
  2.3-mile graded dirt road floods in moderate floods.
- **4801 Florida Sand Music Ranch** — festival venue + year-round camping on non-festival days; the
  Visit page's directions are template text for a different place (address 85 Myers Rd, Brooksville).
- **4736 Hickory Landing** — rec.gov Scan & Pay $10 (from 2026-10-01) vs the forest page's $3;
  recorded $10, both in fees.note.
- **4726 Livingston Creek (Lake Wales Ridge SF)** — hunt-season camp: open September-April,
  "reservable during scouting and hunting dates"; season recorded, kept.
- **14869 Lakes RV** — 90-night online minimum for January-March arrivals; asked AWH.
- **4822 Neals Landing (Jackson Co.)** — no official page says camping exists: the county lists it
  only under boat ramps and landings; USACE's Lake Seminole camping list omits it; aggregators
  split (AllStays 10 sites; a review says "closed for a while"). Inclusion rested on satellite only.
  AWH 2026-10-21: dropped.
- **4737 Mack Landing** — FS page $3/vehicle vs rec.gov Scan & Pay $10 (2026-10-01..12-31); left $3
  (human read). Hickory Landing 4736 went to $10 on the same evidence - DONE 2026-10-21: 4737 and
  4738 Whitehead Landing set to rec.gov's $10 too (rec.gov is the newer channel), $3 kept in fees.note.
- **385 Mitchell Landing (NPS Big Cypress)** — only sites 8 and 10 list a length, 14 ft; 23-ft fit
  unproven.
- **168 River Junction** — closes when Sumter County is under a tropical storm/hurricane warning.
- **14870 Seminole Campground (Fort Myers exception)** — winter priced only by the month
  ($1,500-1,800, "depending on month"); the page names no winter months and a deposit is needed only
  for stays "of a month or longer", so no clear minimum. Kept; check the winter window against the
  3-month peak-season rule if it's ever quoted.
- **14881 Sun Retreats Estero Bay** — Campspot now $103-115 (Nov) / $113-132 (Jan) vs the manual
  2026-10-13 figures; one nights sell in winter. Fort Myers exception.
- **877 Panther SF (WV)** — the park page allows one night Sun-Thu, but book.wvstateparks.com sold
  no 1-night stay on any 2027 date tested (8 weeknights + a Sunday) while selling 2 nights; only the
  page's weekend minimum recorded. Call 304-938-2252. Panther is now on the booking site (supplier
  11067662) - the state:WV registry note and audit/state_park_fees/README.md say it isn't.
- **504 Cranberry** — rec.gov 2026 $15 single / $30 double vs the FS page's $10/$20 (undated).
- **1227 East Fork** — $50 base at the line, plus a $6 per-stay reservation fee (kept; booking fees
  aren't counted, as with Tall Timbers' $3).
- **14250 Camp Holly** — only 5 RV sites, also sells seasonal sites; weekday $30-45, peak Saturday $55.
- **514 Camp Run** — "primitive 1950s style camping", no site lengths; 23-ft fit unconfirmed.

- **1206 Elk River Camp and RV (WV)**: the homepage carries an injected block of ~900 spam domains under the park content (read 2026-10-21). Its only rate ("$15.00 to $35.00 Per Night") is undated. The reservation phone is a Colorado number, 303-807-5209 (added).
- **427 Five River (WV)**: "$30 to $55 per night" is undated (the page itself is current). Bonfire is behind a captcha.
- **526 Canaan Valley (WV)**: wvstateparks.com says spring through fall, but the resort runs the comfort station year-round (water off October-April) and CampLife sells January nights. Season not written. Concession on CampLife, so policy_ref is now "none" (CampLife sells one Saturday night).
- **720 Briar Point (WV)**: booked by phone through Stonewall Resort, not book.wvstateparks.com, so policy_ref is now "none" (the 14-night max no longer inherits).
- **984 Chief Logan (WV)**: "spring through summer", with no closing date published; the 26 sites, 40-ft limit and water/sewer rest on a deleted park page.

- **425 Just Plane Adventures (WV)**: takes monthly renters (winter $600/month, Nov-Apr, 2-month commitment); on ResNexus for 2026-10-21 only 3 of 34 full-hookup sites were bookable. It sells nights at a posted $40-49, so it was kept, but the monthly share is worth a look.
- **455 Rifrafters (WV)**: no site lengths published (an old note said the back-in sites suit 22-ft rigs). The Firefly booking form asks for RV length, so a browser check could settle the 23-ft fit.
- **869 North Bend (WV)**: River Run's 23 non-electric sites are $24.99, but nothing says whether they fit an RV, so the base was left at $44.99.
- **873 Moncove Lake (WV)**: the park's lodging page gives 304-722-3450 in the November-camping sentence (copied into the manual season.note), while its contact block gives 304-772-3450. The first is probably a typo.
- **1196 Grand Vue Park (WV)**: a mandatory $10 per RV guest per day for pool and mini-golf (waived at 4+ nights); CampLife quotes $59.75 for a Tuesday. A local park, so no price gate.

## Resolved 2026-10-21
- **p3-54 (WV):** 12 verified, no drops. Phones added (547 Sutton Lake office, 425), website added (1196). 455 Rifrafters electric 30 -> 50 and year-round; 14254 River Expeditions season April to mid-October.
- **p3-53 (WV):** drop 1200 Big Earl's (site down, Cloudflare 522, no rate) and 1204 Camp Morning Wood (no website, no rate), both on the presence rule. Phones added (487, 491, 526, 720, 1206) and fixed (874). Aggregator/CampLife links taken out of 491 and 630. 630 Coopers Rock base $31.99 -> $41.99 (the $31.99 Rhododendron sites are tent/hammock only). 526 Canaan Valley fees $63-69 (new).
- **p3-52 (first WV):** drop 13122 Hidden Hollow (workforce park, approval for short stays) and 1209
  Lakeview (Facebook only). 504 Cranberry is first-come only. 14251 Kick Back low $28 -> $35 (the
  $28 sites suit tents); 878 Seneca low $22.99 (April-August). 809 Sullivan's: asked AWH.
- **p3-51:** drop 14880 Swan Lake (sells homes) and 14399 Tall Timbers ($50.41 with mandatory
  fees). 14435 Twin Palms at exactly $50 kept, operator site added. 15341 KICCO: the District books
  "Campsite - Town of KICCO (RV/Trailer)", settling the tent-only doubt.
- **p3-50:** drop 14433 Orange Blossom (park model for sale). 4823 Newport Park now reservable on
  Rec1. 168 name spelling fixed. 14868 Orange Grove and 14877 Sanctuary: asked AWH (sells homes /
  in-season 90-night minimum) - both in the Fort Myers exception.
- **p3-49:** drop 14871 Gulf Waters (RVs must be 26 ft or longer; the Fort Myers exception is a price
  exception). 4821 renamed Hutch Gibson Park & Campground (Hamilton Co., so the Escambia
  surcharge follow-up stays with 4820 only). 14876 Imperial Bonita: 55+ (second occupant 45+)
  co-op, nightly rates posted, passes.
- **p3-48:** no drops. The four Fort Myers-exception parks (14875, 14872, 14873, 14882) pass the
  long-stay tests (single nights sold); 369 Gate to the Keys live on Hipcamp, $76, Everglades 8 km.
- **p3-47:** no drops. 4742 Bear Island temporarily_closed -> open (NPS Open, rec.gov booking Nov
  2026; the Hilux Fire claim was the note's). 4734 Wright Lake and 4731 Big Scrub highs dropped (the
  $30 sites are host/management). 167 renamed Bennett Field Campground. 4796 Avalon kept on the
  St. Petersburg gateway (20 km; no per-person fee - the skipped Avalon was WV).
- **p3-46 drops:** 4812 Travel World (Facebook only), 4762 Unhitched Leisure Lakes ($55, no gateway),
  14421 Villa Margaret (55+ permanent-resident park, call for rates). 4846 Lithia Springs is
  reservable on WebTrac (the "FCFS, no reservations" note was wrong); 4829 Withlacoochee River Park
  moved from CivicRec to WebTrac, 50-amp.
- **p3-45 drops:** 14388 Sun Retreats Crystal River ($67.50, no gateway), 14389 Sun Retreats Homosassa
  River ($70, 28-night winter minimum). Kept on gateways: 15420 Orlando SW KOA (WDW 19 km), 15421
  St. Pete KOA (14 km). 4786 St. Johns River at $50.00. 4740 Ocean Pond base $12 -> $20 (the $12
  loop is tents/pop-ups/vans only).
- **p3-44 drops:** 14420 Lettuce Lake ($70, no gateway, 55+ selling units), 14423 Moss Landing ($70,
  55+ manufactured-home community), 4810 Lynch's Landing (dead site, aggregators only). Kept: 4800
  Little Flamingo ($55, Tampa 35 km). 4702 Manatee Springs dump station closed since 2026-01-14
  (in its note); 741 Long Point: Scout Island bridge closed (Hurricane Milton). 4854 Markham: no laundry.
- **p3-43 drops:** 4808 International RV Park ($65-90, no gateway, seasonal 55+), 4795 LeLynn (no
  operator site), 4803 Lake Toho (RV & mobile-home park selling homes and lots, call for rates).
  Renamed: 169 Hog Island Campground, 14391 RV Village at Lake Panasoffkee (no posted rate, RV Life $$).
  169's sites take 25 ft (EKKO fits); 282 Juniper Springs soft minimums recorded.
- **p3-42 drops:** 4809 Floridian (dead site, aggregators only), 4799 Fiddlers Green ($50 + a
  mandatory $3 utility fee, no gateway), 14408 Florilow Oaks (55+ singles park, lots for sale).
  Kept: 14416 Fiesta Grove (St. Petersburg gateway 22 km; daily nights on BookMySites; newest
  rates 2024-25), 4787 Georgetown Marina ($50 incl. tax), 4761 Drifters ($46.77 = $52.62 less 12.5% tax).
- **p3-41 drops:** 14403 Breezy Oaks ($57.56, no gateway), 4780 Arrowhead (website hijacked by a
  gambling spam page), 4763 Cedar Lakes (Facebook only), 4802 Cedars Lake (dead site, unclaimed
  RoverPass only). Kept at/under the line: 14411 7 Oaks $50, 4784 Chiefland $50, 4793 Cody's $45
  summer ($55 Oct-Mar). 4722 Cash Creek: FFS 65+/military/disabled discounts, no amount stated.
- **p3-40 drops:** 4767 The Hideaway ($57, no gateway), 4744 The Glades (annual residents, park
  models for sale, call for rates), 4789 Tampa South (call for rates, residents/tenants).
- **p3-39 drops:** 4755 Sunset Isle (monthly/long-term only since 2022), 4768 Strawberry Fields ($60,
  no gateway, primarily 55+). Kept: 727 Suwannee River Bend ($60+tax, no gateway) on its --AWH note;
  14404 Seven Springs ($60, Tampa gateway 37 km; 55+, marked).
  Site counts disagree: 4711 Santos 23/25/24, 4700 Stephen Foster 45 vs 39 on Reserve Florida.
  382 St. Lucie South: rec.gov rule militaryDiscount=1, meaning unclear, not written.
- **p3-38 drop:** 14386 Pellicer Creek ("mainly a long-term park", background checks on all
  occupants). Rodman 154 fees $19 -> $29 (the $12 base was the tent rate). Rodman / Ross Prairie
  (Cross Florida Greenway) are on floridastateparks.org + Reserve Florida: state:FL fits.
  153 Rainbow Springs: a day-use reservation program for all visitors since 2026-04-29.
- **p3-37 drops:** 14407 Morningside RV Estates ($72.95, no gateway, mostly seasonal 55+), 14418 Oak
  Grove RV Resort (rules admit only rigs 24 ft+; no posted rate). Notes: 151 Gold Head's Turkey Oak
  loop closed for renovation since 2026-03; 4725 Myakka's park-wide drinking-water outage since 2025-10-28.
- **p3-36 drop:** 4771 Lake Waldena Resort (Campspot $55-60, no gateway; as Countryside).
- **p3-34 drop:** 4758 Gulf Breeze RV Park ($69, no gateway; nearly full on weekdays, 2-night engine).
- **p3-33 drop:** 14395 Countryside RV Park ($55 on Campspot, no gateway; 55+ mostly seasonal).
  Clearwater/Lake Tarpon KOA 15415 ($72) kept: Tampa gateway 33 km.
- **p3-32 drops:** 14394 Woods-n-Water Trails (55+ community with a Homes for Sale page),
  14422 Woody's (no posted rate, daily stays "call for details", a Ch. 723 mobile-home community).
  Kept at the $50 line: 4772 Astor Landing (undated rate page). 4819 Wilderness Landing's $0 and
  14-night max cleared (camper reports only).
- **p3-31 drops:** 4804 Lazy Dazy (no price indicator; stored fees were other parks'), 4806 Masonic
  ($60), 14425 Oak Haven ($70, 55+ home community), 4811 Scottish Traveler ($85). Kept: 15422
  Sugarloaf KOA (Key West gateway). 383 renamed Ortona South Campground; 393 renamed to its
  Shady Pines campground.
- **p3-30 drops:** 4797 Hammondell (sells mobile homes and lots, primarily 55+), 4751 In The Garden
  (Facebook only, 10 Google reviews).
- **p3-29 drops (Florida):** 14397 Arrow Family ($65, no gateway), 14414 Cross Creek ($71, no
  gateway, maybe 55+), 14431 Buckhead Ridge (annual leases, no nights for sale), 4766 Buddy's
  Lakeside (no live presence), 4724 Escribano Point (FWC: "Camping: Prohibited" 2026-27).
  Kept: 14428 Cypress Isle (Google 4.6/29 + phone meets the presence rule).
- **FL registry row** confirmed from floridastateparks.org/reservation-information (browser):
  caveat removed, fcfs always, method manual. Four FFS entries (166, 169, 170, 587) now
  policy_ref none like the other 17 state-forest/FWC entries.
- **64 St. John's Rock / 87 Wolf Den Run** — DROPPED under the off-road rule (ORV-trail campsites;
  Maryland's ORV state park). Reported to AWH for a possible reversal.
- **436 Thompson Lake Parking Area** — DWR 300-ft rule: satellite 2026-10-21 puts the pin in
  woods ~250 m east of the lake, nowhere near the ramp; no problem.
- **Long Run Road #1-#6 (520, 519, 522, 56, 57, 58)** — DROPPED under the 4WD rule: DWR's FR 72
  page says the road "is recommended only for 4-wheel drive vehicles with high clearance".
  **521 Western-Facing Campsite** (0.5 mi up FR 72C off FR 72) dropped on the same page.
- **13090 Lonesome Pine RV Park (VA)** dropped (criteria_drops.py): no website, Facebook behind a
  login, Google 16 reviews, no rate (RV Life's $ is a ~$1 placeholder).
- **15518 Richmond North / Kings Dominion KOA** kept: base $35 (November weeknight); weekends and
  season run $71-150, and it is 34 km from Richmond (gateway).
- **1131 Parkview RV Park** kept: static 2022 site with no rates, phone; RV Life $$ is the price indicator.
- **13095 Jubilee Park and Horse Show Grounds (VA)** dropped (criteria_drops.py): login-walled
  Facebook only, no operator rate, Google listing (43 reviews) has no phone.
- **894 Chincoteague Bay RV Resort** kept: base $59 ($49 + $10 resort fee) is over the gate but it
  sits 4 km from Chincoteague/Assateague (gateway). Campspot's record still points at a Sun Outdoors
  URL, which now lands on Sun's Virginia index without it (Sun lists only Jellystone Chincoteague);
  the operator site is "Blue Water" - a past Sun affiliation, not a current Sun park.
- **1140 Glen Maury Park** rates ($70 W/E, $55 tent, 2026 page) are high for a city park and rest on
  one page; earlier city/news pages said $35-40. Kept as posted.

- Dropped (audit/verify/criteria_drops.py, logged in removals.json): **1168 Lake Bonin** (long-stay
  test 2: "focus on seasonal sites", daily rates only by call/email, nothing posted, no booking
  site), **13118 Valleyview Farm** (domain parked, booking host gone, no Google listing at the
  pin), **1164 Frey's** (Facebook only; Google listing has no phone; no posted rate - AWH's
  2026-10-11 drop class), **1188 Woodhaven Acres** (site has no phone/rates/booking; Google 5 reviews).
- Kept: **4375 King's RV Park** (own site kingsrvcampground.com found via Google: $35 nightly,
  phone; website added, fees corrected - the $45 was King's Campground in Dillsburg PA),
  **1181 Shady Rest** (Google open, 139 reviews, phone 570-222-2365 added), **13113 Sunvalley**
  (Google open, 69 reviews, phone matches), **1136 Cavitts Creek** (local; Google 237 reviews,
  phone 276-988-7250 confirmed), **14277 Fire Pit** and **14278 Pine Lane** (both pass the five
  long-stay tests: 2026 nightly rates posted + phone, no standing minimum, no site count; Fire
  Pit's note now says it is mostly seasonal), **1104 Breaks** (the park page does not say its
  $27 primitive sites are tent-only; Firefly is behind reCAPTCHA, so the stored base stands).
- **14267 Harts Content** kept: a live ParkWith booking page sells RV sites (price + presence);
  fees.checked corrected 2026 -> 2023 (the table is titled "2023 Rates").
- **14274 Ledgedale** kept: posted nightly RV rate + phone, the waitlist is for SEASONAL sites
  only; the rate page is undated and its holiday dates fit 2022, so fees.checked -> 2022 and
  inclusion_evidence corrected. Re-check for a current rate when the 2027 season is posted.
- **1147 Washington County Park** closed: it is a LOCAL park (county park authority), and the
  long-stay five tests apply to private parks only.
- **13087 Amelia Family Campground** kept: the verifier found the operator site stale (newest post
  2020, no rates); Google listing active, 159 reviews, phone 804-561-3011 matches - the same state
  AWH kept it in on 2026-10-14 (own site + phone + RV Life $$).

### p3-55 / p3-56 (WV, 2026-10-21)
- **13121 Gheny Nook dropped** (long-stay test 2; see criteria_drops.py).
- **426 Riverside Cabins** kept: the only rate ($40/$45) is on an undated page last modified 2023-08-04, with no booking channel (phone/email/Facebook). It carries an --AWH note and RV Life rates it 4.5. Re-check for a dated rate.
- **1218 Saylwinds**: the operator says it "has been listed for sale" (2026 season note), but it is still taking reservations. Re-check next season.
- **875 Summersville Lake SP** overrides the state:WV 2-night weekend minimum: the booking site sold one-night Fri/Sat stays and the park page states no minimum.
- **1197 Kitty Wilson**: rates only on a 2018 page (local, no gate). **1193 Krodel Park**: no official web page found (town park).
- **14248 Lazy K's / 14252 Lost River / 1226 Lake Stephens**: monthly sites alongside nightly ones; nights are sold to anyone, so the long-stay test passes. Lost River's base is exactly $50.00, at the gate, not over it.

### p3-57 / p3-58 (WV, 2026-10-21)
- **1199 Beaver Lakes** kept: no operator site (dead Wix domain, Facebook unreadable) and Google has 23 reviews, but a live instant-book Hipcamp listing with a posted rate is its booking page (price + presence). The phone is now Google's 304-618-7399; it was 304-619-6654.
- **1205 Creekside Camping** kept: working site (2019) with a phone, and Google 4.6 over 58 reviews; no posted rate (RV Life $$ only), and nothing suggests a long-stay park. A call would confirm nightly sales.
- **13120 Eagle's Nest** kept: $50.00 base, at the gate, not over it. It sells a $850/month "Full Time Resident" product and a weekend season alongside posted nightly sites; nights are for sale, and there are no homes or lots for sale.
- **232 Bluestone SP**: the inherited state:WV booking row looks wrong. book.wvstateparks.com sells only picnic shelters there, and the camping page drops the reservation/minimum sentences, so it is probably first-come or by phone during the dam work. Call 304-466-2805, then override the row. Not priced.
- **715 Beech Fork (registry lead)**: the booking site sold one-night Fridays 9 and 23 days out but refused them 30+ days out and on every 2027 Friday, so the 2-night weekend minimum is waived somewhere inside 24-29 days. Confirm at another park before the state:WV row gets a waiver.
- **876 Cabwaylingo**: the base is $39.99 (electric, the only sites tagged for RVs). If the 13 untagged non-electric sites fit 23 ft, the base would be $19.99.
- **120 Blue Bend**: a concession since spring 2026 (Sunshine Valley Land Management, secondary evidence); recreation.gov still says not commercially managed.
- **500 Abes Run** kept (--AWH firsthand): no FS page exists and the FS designates no sites; FR 51 is dirt.
- **84 Bear Heaven** kept: "a small primitive campground" with no stated vehicle length; the inclusion audit found one site listed at ~30 ft.
- **817 Mountain Lake**: the FAQ says "we do not offer full hook-up sites", but the booking page sells 50A/water/sewer sites in area 2. The booking page was recorded.
- **216 Tygart Lake**: the lodging page says "10 full hookups"; the camping page says 50A + water, "Full hookup sites are not available". The camping page was recorded. Only 10 sites take RVs.
- **117 Seneca Shadows**: the FS says a 6-month window, rec.gov rules say 11; 180 days recorded.

### p3-60 (WV, 2026-10-21)
- **746 Fourth Moon Camp** kept: $60 (+ Hipcamp fee) is over the gate, but it carries an --AWH note, which is a specific exception.
- **502 Cranberry River sites 6-19**: fees $0 -> $10/$20 (rec.gov first-come-season fee). Road: Forest Order 09-21-02-26-05 closes the southern FR 76 approach from Richwood Sept 8-Nov 20, 2026; the sites are reachable from the north via FR 101 / CR 46/2.
- **118 Day Run**: FR 86 closures shift through Nov 30, 2026 (Forest Order 09-21-02-26-04); reachable from Dyer.
- **499 Dolly Sods #3**: FR 19 is closed from the Laneville gate to FR 75 from 2026-06-22 (alert runs to 2027-06-15); the site seems to be on the open Jordan Run side.
- **14062 Cedar Branch**: the WV DNR District 4 page says "On the WMA: Camping is not permitted" for Bluestone Lake WMA, but DNR's own map labels "Cedar Branch Campground" and Summers County sells it at $15. Probably stale boilerplate.
- **14054 Chief Cornstalk / 14055 Conaway Run / 14062 / 59 Gandy Creek**: no page states a rig size for the primitive sites (14062 was already accepted by AWH 2026-10-11).
- **402 Flagpole Road**: the phone is not set (the North River RD numbers have been reported down since 12/10/25).
- **59 Gandy Creek**: the vault toilet has been closed since 2026-08-11.

### p3-59 (WV, 2026-10-21)
- **1221 The Dock dropped** (presence rule; see criteria_drops.py).
- **1216 Robert Newlon Airpark**: robertnewlon.com is hijacked (slot-casino spam / redirect chain), so the website is now its Facebook page (from Google Maps). Presence passes on Google (4.4 over 148 reviews). Its hookups/sites/facilities are derived and appear on no operator page (likely RV Life/Campendium); clear them if they turn out to be aggregator-only.
- **1219 Starry Fields**: workforce-leaning ("Close to local employers"; reviews are 1-2 month work stays), but posted nightly rates and Firefly booking pass test 2.
- **14249 Smokey Bottom**: $50 base for four, at the gate, not over it. Monthly/seasonal sites sit beside nightly ones.
- **1225 State Fairgrounds**: the $45 rate's page header still reads 2021 (Bonfire booking has a reCAPTCHA). Ownership private (501(c)(3)) confirmed.
- **1195 Brooke Hills Park**: CampLife lists no sites, says "2 night minimum" to every one-night request and "No sites available" to two-night searches, so it may book by phone only (304-737-1236).
- **815 Harpers Ferry Campground**: mixed-use outfitter base (zipline, guest boat launch, trains 24/7); monthly leases Nov-Mar with a background check. Tunnel height is an ask.

### p3-61 (WV, 2026-10-21)
- **14056 Bluestone Old Mill**: still temporarily_closed for the Bluestone Dam work ("will reopen once construction is completed", no date); "not suggested for larger RVs and campers". Re-check later.
- **462 Buffalo Gap Retreat** kept (--AWH note): only 2 of 24 sites take RVs (creekside, no hookups, under 30 ft; site 30's RV parks in the parking area); $50 from Hipcamp, at the gate, not over it.
- **513 Gladwin Dispersed** kept (--AWH firsthand): no agency page names it (website is now the Monongahela's general camping page, replacing thedyrt); a 2021 aggregator review says the low-water bridge to the far-side site washed out.
- **Canaan Loop Road #1-#4, #7, #8**: the FS designates no numbered sites; FS says only "exercise caution, especially when in a low-clearance vehicle" (not a 4WD recommendation). Aggregators say the full loop may need 4x4. The north end is private land. Booking values rest on a newspaper reprint (method reported).
- **483 Brandywine Lake**: "Not suitable for large RVs" (no length); the North River RD phone was reported down, so it's not set.
- **1039 Guyandotte**: 21 of 86 sites are long-term (16-night minimum); 65 are normal nightly. The season rests on note prose.

### p3-63 (WV, 2026-10-21)
- **496 Red Run Falls**: ~1.1 km from Stonecoal 511 on the same FR 209 corridor. If it is one of Stonecoal's numbered sites, AWH's 2026 fee-change photo ($15 single) applies and the recorded $0 (2023 notice) is stale. No FS page says which sites the fee covers.
- **494 / 496 / 510 / 13221 / 13222 Shavers Fork dispersed**: no FS page designates any of them (the 2023 Greenbrier developed-dispersed list names only Stonecoal); websites set to the Monongahela camping page (496: the FR 209 reopening release). FS road layer rates FR 481/47/49/233/209 at each pin maintenance level 3, "suitable for passenger cars". 494's pin is on FR 481 "Fish for Fun", not FR 27 (AWH's note already hedges); its hookups/sites/facilities still rest on thedyrt (method reported).
- **112 Short Mountain**: DNR lists 74 primitive tent/trailer campsites, so ownership wma -> state (agency-designated sites) and renamed "Short Mountain WMA Campsites".
- **501**: renamed "Seneca State Forest Campground (Seven Mile)"; no official page uses "Seven Mile".
- **14051 / 14053 / 112 / 13221 / 13222**: no page states a rig size. 14063 Shanklin's Ferry: same DNR "Camping is not permitted" boilerplate conflict as Cedar Branch 14062.

### p3-62 (WV/MT/NJ, 2026-10-21)
- **61 Red Creek**: FS page says "Restrooms are not available" (recorded no toilets; may be stale if a vault toilet exists). FR 19 closed Laneville gate to FR 75 since 2026-06-22, no end date; FS directions use the Jordan Run/Hopeville end. Forest Order 21-94's 300-ft roadside ban excludes the campground. Thedyrt link removed.
- **744 Smalltown**: rates undated (©2021 footer; $45/$285 weekly/$700 monthly), under the gate anyway; management may refuse units older than 15 years.
- **Glacier gateway parks 15377 / 15370 / 15378 / 15395**: over $50, kept under the Glacier NP gateway exception (bases $76 / $73.45 / $63.60 / $96). Heart of Glacier charges a $50 non-refundable booking fee per stay. St. Mary KOA is owned by the Blackfeet Nation (Siyeh Corp.); left `private`, as First Nations parks are in BC.
- **6299 Avalanche**: Going-to-the-Sun vehicle limit (21 ft / 8 ft) between Sun Point and Avalanche; a 23-ft rig comes from West Glacier only.
- **14057 Bertha**: same DNR "Camping is not permitted" boilerplate conflict as 14062/14063; no closure for the dam work found.
- **503 Big Rock / 119 Bishop Knob**: first-come only, overriding the inherited rec.gov reservable row. FR 76 (Richwood side) closed 2026-09-08..11-20; both reachable from Dyer via FR 101.
- **463 Horseshoe**: no FS page (expected URL 404s); rec.gov only. Note says "along a remote section of the Cheat River" (-AWH) where rec.gov says "along Horseshoe Run" (the run joins the Cheat nearby). Phone set to the district office 304-478-2481 (staffed season: 304-801-3262).

### p3-64 (WV, 2026-10-21)
- **528 Summit Lake**: fee $10 -> $15 from the Monongahela's Dec 2025 fee release (effective 2026-01-01); the campground page (2026-06-02) still says $10.
- **62 Spruce Knob Lake**: rec.gov $18/$32/$15 vs FS page $16/$28/$13 (rec.gov recorded); rec.gov lists vault toilets + solar drinking water, FS page says neither (water left unset). Concession: American Land & Leisure.
- **511 Stonecoal**: no FS page numbers the sites; "15" rests on elkinsrandolphwv.com. Whether Red Run Falls 496 is a Stonecoal site (and so $15) is still open. Discount flags stored false with no source.
- **116 Tea Creek**: FR 86 construction closure (to 2026-11-30) is a road closure; the campground stays open (reach from Dyer).
- **60 Swallow Rock**: no agency page uses the name (FS mentions Swallow Rock only as a CR 29 bridge); website now the Gandy Creek dispersed-area alert.
- **Squirrel Gap 397-401**: GW&J NF Lee RD; FR 344 level 3 gravel, open to vehicles 04/01-01/15. No FS page names the sites; no rig size anywhere.
- **14050 Teter Creek**: DNR lists 20 tent/trailer sites only; directions corrected (CR 9 from WV 92 at Meadowville).
- **Monongahela 2026 opening dates** (fs.usda.gov/r09/monongahela/recreation) recorded only as season.note, year_round false.

### p3-65 (WV/SC, 2026-10-21)
- **750 The Trout Camp** (--AWH, hipcamp): host says "15 tent sites and annual RV sites"; only RV #5-#8 of ~11-12 riverside RV sites book nightly on Hipcamp (7-night max, 7-9 bookings each). Nightly sale is real, so test 2 passes; the rest of the row looks annual. $60 price is AWH's call (his note).
- **114 / 115 Williams River**: FR 86 construction closure (Forest Order 09-21-02-26-04, to 2026-11-30) spans 114's pin; the FR 86 approach WV 150 -> FR 216 (115) closed since 2026-07-20. Road closure, not a status.
- **4351 Betty's RV Park**: Facebook-only, passes presence on Google Maps (4.6 over 56, phone 803-924-4135). No posted nightly rate (RV Life $ tier + one 2026? camper report $30); derived hookups/sites/booking cleared (directory-only).
- **740 Coneross**: no Corps page states a season (district page CDN-blocked).
- **91 Hawe Creek**: closed for the season 2026-09-13 (Corps release), no reopening date; 3-night holiday-weekend minimum.
- **13369 Virginia Point**: rates only by phone (camp host 304-690-5211).

### p3-66 (SC, 2026-10-21)
- **4353 Briarcliffe** kept: "a membership park that is also open to the public" ($3,500 membership + dues), but guests book nightly by phone ($75-90, gateway: Myrtle Beach 17 km lifts the price half; $8/night electric fee may be extra). Site count 289 (note prose) vs operator "over 146 sites" - left. Good Sam now true.
- **4352 Turtle Creek** kept: no posted nightly rate (phone booking, "call us for monthly prices"), but RV Life 5*/$$ and Passport America nightly sale satisfy price + presence.
- **646 Buck Hall**: open only "until the end of shrimp baiting season in November" 2026, then the whole area closes for a major renovation (no contract, no timeline). Set temporarily_closed once it starts.
- **622 Camp Pedro** (--AWH): no rate readable (innRoad behind Cloudflare Turnstile); RV Life $$$.
- **4379 Chau Ram**: county fee page $20 res/$30 non-res vs reservations page $25 all-in (res $5 off); fee page kept. experienceoconee.com now behind Cloudflare.
- **4354 Cherokee**: $49.95 regular (undated, ©2018), just under the gate.

### p3-67 (SC, 2026-10-21)
- **4357 Edmund RV Park** kept: unclaimed RoverPass link removed (no operator site; edmundrvpark.com parked); presence on Google Maps (4.0 over 139, phone); price only RV Life $$; long-stay mix uncheckable. Derived values that rested on RoverPass cleared.
- **702 Hamilton Branch**: sites 115-165, The Nest (140/141) and H1-H6 still closed for cleanup (booking site, 2026-10-21) - partial, no status.
- **93 Modoc**: closed for the season 2026-09-13 (Corps release), no reopening date.
- **4382 Lynches River**: "Each site can accommodate RVs from 60 to 157 feet" read as site lengths, not a minimum rig length (sites note).
- **96 Lake Wateree**: lakefront count 23 (park page) vs 15 (booking site, AWH note).

### p3-68 (SC, 2026-10-21)
- **4369 Broad River DROPPED** (criteria_drops.py): approval required to stay overnight (long-stay test 2), workforce marketing, ~$51.94/night with Campspot's per-night % fees, no exception.
- **4362 Bass Lake**: operator rates page (undated) $55.04-71.40 + tax vs Campspot's live $45.50 quote (2026-10-13); the dated booking-channel quote kept. Re-check next season; over the gate if the operator page is current (no gateway, not GS).
- **4359 Tanager Woods**: rigs "no more than 15 years old" (also 744 Smalltown); standing 2-night minimum; courts Charleston-area workers with weekly/monthly rates but posts a nightly rate with no application.
- **733 South Cove**: county fee page vs reservations page disagree (as Chau Ram); county 86 sites vs ReserveAmerica 56 RV + 11 tent.
- **4366 Aiken RV Park**: aikenrvpark.com redirects to a cabinetry company; Campspot is the only operator channel.
- **15490 Mount Pleasant KOA**: $84.99+, Charleston gateway (17 km).

### p3-69 (SC, 2026-10-21)
- **4370 Mr. Z's** kept: workforce signals (6 mi from Michelin/US Foods plants; monthly $750, "Maximum stay 3 years for Monthly", monthly rigs under 10 years old) but a posted $50 nightly rate (at the gate), no application, rules say "temporary stays by transient guests". Passes test 2.
- **4373 Saluda River / 4365 Sweetwater Lake / 4364 Swamp Fox / 4368 Sandy Oak**: no operator rate; presence on Google Maps (200 / 166 / 356 reviews) or the operator site (Sandy Oak); price from camper reports (Saluda $40 2024-01, Sweetwater $40 2024-12) or RV Life $$. Directory-only values cleared. Swamp Fox's domain is parked and its RoverPass unclaimed (no website). Sweetwater advertises "Long term and short term".
- **4381 High Falls**: county fee page vs reservations page disagree (as Chau Ram / South Cove); 2-night waterfront minimum in booking.note.
- **592 Lake Aire** $62.30-77 and **15491 Myrtle Beach KOA** $68.94: over the gate, Charleston / Myrtle Beach gateways.
- **4363 Jolly Acres**: syrrrun.com is its own site; rate undated (© 2013), under the gate.

### p3-70 (SC, 2026-10-21)
- **4367 Tuck in the Wood**: no posted nightly rate (only "Monthly 'snowbird' rates ... call"); RV Life $$ + website/phone pass price + presence. "NO Reservations Required" but a reservations phone.
- **4361 The Barnyard**: $65.40, over the gate, Congaree NP gateway (35 km); Good Sam member rate $58.86.
- **606 Campbell's Lake** (--AWH): scfc.gov states no road or vehicle limit; aerial shows a car on a sand clearing via an unpaved sand track. 23-ft fit rests on AWH.
- **97 Sedalia**: FS fee box $7/$14 vs its own text + rec.gov 2026-27 $5/$10 ($5 kept). Loop 2 (sites 6-12) opens only for deer (Aug 28-Jan 3) and April turkey seasons.
- **4350 Elmwood**: site count and 40-ft max cleared (camper report only).

### p3-71 (SC, 2026-10-21)
- **13978 H. Cooper Black**: policy_ref "none" removed - it is an SC State Parks area booking on their site under the state:SC rules (13-month window, 2-night minimum), not an SCDNR site; open to any RV camper. Max rig 91 ft comes from the reservation site's park filter.
- **610 Hunter Pond / 611 Lee Pond**: SCFC states no road surface or vehicle length (sites off TT 110 Rd); inclusion rests on "drive-in campsite".
- **4385 Mill Creek (Sumter County)**: rates ($20/$25) come from an undated 2014 renovation write-up; no 2024+ date. Call 803-436-2248.
- **4344 Oconee**: winter closures Dec-Mar "contact the park"; year_round cleared. reserve.southcarolinaparks.com's park filter `maxrv` sometimes disagrees with park pages (Poinsett 60 vs 40) - park page wins.

### p3-72 (SC/NY, 2026-10-21)
- **607/608/609 Sugarloaf SL 1A/1B/2**: SCFC calls all 20 forest campsites "primitive" and states no road or vehicle limit; 23-ft fit rests on AWH's notes.
- **751 Twilight** (--AWH, hipcamp): host sets Site 2 (lakeside, full hookups) to FOUR_WHEEL_DRIVE_RECOMMENDED; Site 1 (36 ft, "upper lot in the woods") is 2WD. AWH's note ("Site 2 ... in the woods") may describe Site 1. Not a drop: Site 1 is reachable in 2WD.
- **1443 Chautauqua Fairgrounds**: only "several sites" year-round; booking by mailed contract/application to the Fair Office (no online/phone path stated). Nightly rates posted ($25-45).
- **1505 Birch Haven**: mostly seasonal but passes the five tests on what is published (daily $40 + phone, no application/minimum, 8 lease spaces of 80). Rate page Last-Modified 2021, so no fee recorded.
- **1509 Cherry Hill**: operator page "$52 per night (no hook-ups)" for 2+2 (undated) vs Campspot $40 for 2 adults (Oct 2026, dated) - kept under the gate; Buffalo gateway 41 km (just outside). Re-check when summer 2027 opens.
- **1478 Camp Elmbois**: sewer cleared (electric + water + dump only); 2-night Jul-Aug weekend / 3-night holiday minimums.

### p3-73 (NY, 2026-10-21)
- dec.ny.gov and parks.ny.gov answer 403 to plain HTTP; DEC's 2026 campground summary PDF (dec.ny.gov/sites/default/files/2025-04/summerreccampgroundsummary.pdf) gives each DEC campground's sites, minimum, phone and season. ralist.py (session scratch p3-73) parses ReserveAmerica site lists.
- **291 Hither Hills**: peak season (mid-Jun to mid-Sep) is 7-night reservations only (PEAK-SEASON MINIMUM line; ≤3 months, AWH 10-21 rule).
- **1454 McCann**: asks.md (mostly seasonal; now dry camping only).
- **1497 Lizzie's**: lizziescampground.com is a HugeDomains for-sale page; presence on Google Maps (4.3 over 35, phone 607-548-4044); price only RV Life $$ (AAA lists $30-55).
- **1506 Riverside Acres**: rates undated (site build Feb 2025); motor home $40/$45.
- **1389 Eel Weir**: park says 38 sites, ReserveAmerica sells 27.
- **1390 Sacandaga / 345 Scaroon Manor**: season closes set 09-05 (DEC 2026 summary + RA 2027).

### p3-74 (NY, 2026-10-21)
- **1495 Waterfalls Campsite DROPPED** (presence: Squarespace site expired, Google 5 reviews).
- **1517 Treasure Isle**: "WE ARE AN ALL SEASONAL PARK WITH A LIMITED AMOUNT OF OVERNIGHT SITES"; nightly $50 posted, no count of overnight sites (test 4: no count = pass). Phone corrected.
- **1476 Top-A-Rise** $50 and **1517** $50: at the gate, not over.
- **1513 Adirondack Gateway**: no posted rate ("Call for Reservations"); RV Life $$ + site/phone. Actually at Cold Brook (Herkimer Co.).
- **1504 Black River Bay**: also sells a "Trailer Site, No electric, No water, $15 per night"; base left at $45 (W/E) - unclear whether the dry site takes a motorhome.
- **1403 Bear Spring Mountain**: DEC 37 sites vs RA description 41 vs RA list 33.
- p3-72's rap.py misses RA labels with a double space; fixed copy rap2.py (session scratch p3-74). parks.ny.gov unreadable (Cloudflare) - OPRHP entries rest on ReserveAmerica.

### p3-75 (NY, 2026-10-21)
- **1485 Creekview DROPPED** (presence: placeholder site, 9 Google reviews, no rate anywhere).
- **1473 Cayuga Wine Trail**: asks.md (Van vs Motorhome site types decide the gate).
- **1477 Elkdale**: sells weeks/months/seasons, "We also welcome construction workers for long term camping"; $50 nightly (undated) at the gate; no nightly-vs-seasonal count (test 4 passes on no count).
- **1475 Country Hills**: daily/weekly/monthly/seasonal + rallies; online nightly booking, no application; rate page headed 2025, $43 + $2.50/night online fee.
- **1396 Fillmore Glen**: 2027 bridge construction limits sites 27-60 to vehicles of 9 tons or less (EKKO passes).
- **1438 Chemung**: ReserveAmerica link replaced with the county's working one. **1410 Caroga Lake** closes 09-05.
- ralist2.py (session scratch p3-75) returns every campsite at parks that also have cabins.

### p3-76 (NY, 2026-10-21)
- **1448 Indian Island DROPPED** (non-resident Green Key bookings carry a 4-night minimum; $200 VIP key the only way around). Registry row local:suffolk-county-ny now has no entries; its premium_site 4 is the Flagship Park surcharge (Premier +$22 / Tier I +$11 / Tier II +$5 per the 2026 schedule) - fix if a Suffolk park is ever re-added.
- **1407 Frontier Town**: RVs not confined to the horse loop (13-site Stagecoach RV/Trailer Loop + Prairie Junction); sites 77; phone changed to DEC's 518-532-9051.
- **327 Gilbert Lake**: non-electric Deer Run sites (77-79, 90-135) open Jun 11 - Sep 5, 2027; manual season note doesn't say so.
- **317 Grass Point**: park text says 20 A on all 20 electric sites; RA list labels 8 at 30 A and 4 at 50 A; recorded 20.
- **328 Glimmerglass**: no park phone found (RA alternate 315-492-1756 only).
- **1464 Hickories Park**: hookups corrected to 50 A/water/sewer; FCFS, cash or check.
- rap2.py can hang; wrap it in `timeout`. go.sh (session scratch p3-76) pulls park page + phones + site list.

### p3-77 (NY, 2026-10-21)
- **1468 Lake Placid VFD Campground**: ownership local -> private (run by Lake Placid Volunteer Fire Department, Inc., a nonprofit, not a government). No operator page (lakeplacidfd.com never mentions it); presence rests on Campendium/RV Life/The Dyrt listings + Aug 2026 camper reviews; camper-reported $40. Reviews call it "a small RV parking lot" with hookups, no fire pits/tables - kept as an RV park.
- **1520 Jellybeans** $50 at the gate; **15465 Lake George KOA** $80-90 under the Lake George gateway (14 km).
- **214 Letchworth**: phased loop closures summer 2026 - spring 2027 for new shower buildings (loops 100/200 open); dated note, no status.
- **1405 Long Point**: only 5 of 74 sites "Near Water" - note's "most sites on/near the water" dropped.
- **1409 Limekiln Lake** closes 09-05. ralist4.py (session scratch p3-77) handles site labels with spaces.

### p3-78 (NY, 2026-10-21)
- **1446 Smith Point DROPPED** (Suffolk non-resident Green Key 4-night minimum, as 1448).
- **15469 Sodus Point KOA**: $49 Fisherman's Row "perfect for a small Class B Motor Home, Pop-Up, or Small Travel Trailer" - KOA's form offered it for a 23-ft motorhome; if not, base $70 over the gate (Rochester 50 km).
- **15467 Niagara Falls KOA**: $60 under the Niagara Falls gateway (11 km).
- **1516 Royal Mountain**: ~30 of ~50 seasonal; ResNexus sells 11 RV sites nightly - passes. Rates page "2025".
- **1518 Rancho Pines**: operator page still 2023; Campspot $49 kept (motorhome question in asks.md).
- **310 Robert Moses / 143 Sampson**: no parks.ny.gov page on the entry (Cloudflare kept the path unread).
- **21 North-South Lake**: 126 of 203 sites listed at 20 ft.
- pdfget.py (session scratch p3-78) fetches a Cloudflare-blocked PDF from inside a browser page.

### p3-80 (NY, 2026-10-21)
- **1481 Brookside Beach**: no nightly rate posted anywhere; banner pushes 2026 seasonal sites; says it offers "overnight and seasonal sites". Presence via site + RV Life $$. Confirm a transient rate by phone (716-326-3096) if it matters.
- **1474 Camp Bell**: $45 base is the 20-amp class ("designed for Tents and Small RVs"), which Staylist offers to a 23-ft Class C; 30-amp is $58 (over). Kept at $45, as Sodus Point KOA. No sewer at sites.
- **1524 Cedar Creek**: sewer false -> true; $35/$40 (2024-03); seasonals $1,250 beside nightly - passes.
- **466 Fahnestock**: RA name is "Clarence Fahnestock State Park"; no park phone on RA; 2026 bathhouse closure no longer posted.
- Missing parks.ny.gov / dec.ny.gov pages on 336, 363, 349, 466 (both sites 403 to scripts; Wayback unreachable from here) - add when readable.
- Short listed lengths: 1402 Woodland Valley (11 of 67 at 30 ft), 336 Burnham Point (8 of 44 over 20 ft), 1414 Cayuga Lake (158 of 247 at 20 ft), 466 Fahnestock (13 of 66 at 25-30 ft).

### p3-79 (NY, 2026-10-21)
- **1486 Southern Shores DROPPED** (no live presence: both domains dead, RoverPass unclaimed, no Google listing confirmed as this park).
- **1522 Stysh's Brown Barn DROPPED** (no posted nightly price or booking engine; camper-reported $25 not usable while the operator has a site).
- **1401 Taconic Copake Falls**: 17 sites take 25 ft - EKKO fits; 85 sites.
- **1398 Sugar Hill**: general first-come area (horse stalls at the trailhead, not a horse camp); restroom/water outage noted; phone -> DEC Region 8 Bath office 607-622-8282.
- **1514 Thornbush Acres**: $40 + metered electric $0.30/kWh - under the gate.
- **1395 Taughannock**: RA contact gives 607-539-4078; stored 607-387-6739 kept (the park's long-standing number).
- **1466 Winding Hills**: website moved to orangecountyny.gov (old domain 301s there); FCFS except four holiday weekends by phone.

### p3-82 (NY, 2026-10-21)
- **1499 Niagara Hartland DROPPED** (Campspot $60 every RV type, no gateway within 40 km).
- **1470 Little Wolf**: stored phone 518-359-3328 on no official page; town page gives Town Hall 518-359-9261 and 518-359-3341; tupperlake.com 518-817-6019. Left as is.
- **1460 North Bay**: 31 daily / 33 seasonal / 8 tent - passes test 4; rates undated.
- **15468 Lewiston KOA** $65-73 under the Niagara Falls gateway (15 km).
- Short listed lengths: 1412 Max V. Shaul (6 of 30 at 25+ ft), 1416 Paradox Lake (13 of 55 at 30+ ft).
- **350 Nicks Lake**: no dec.ny.gov page on the entry (403 to scripts).

### p3-81 (NY, 2026-10-21)
- **1503 J & J Campground**: only web page is an undated subpage of vintagebirds.com (a Wanderlodge FMCA chapter site) naming the owners and phone; $28-30 undated. Kept (operator page + phone, far under the gate).
- **14336 Lake Champlain RV Resort**: "Only 9 Seasonal Spaces Left!" banner; $45 daily posted, no minimum - passes. Footer lists it under Investorade Community Holdings with seven other parks.
- **1471 Ilion Marina**: 14 sites rent seasonal/monthly/weekly/daily; no seasonal count.
- **1449 General Clinton**: military + Passport America get $30 instead of $60.
- **15466 Lake Placid KOA** $65-102 under the Lake Placid gateway (17 km).
- **354 Lake Durant** closes 09-05; 38 of 62 sites listed at 20 ft.
- Missing parks.ny.gov / dec.ny.gov pages on 319, 312, 332, 354 (403 to scripts). rl.sh (session scratch p3-81) runs the site-list parser over a park's loops.

### p3-84 (NY, 2026-10-21)
- **Suffolk County correction**: the county Campground Rules give non-residents walk-ups ("Check-in for available walk-up sites will begin at 8:00 am", non-resident rates without a Green Key); the Green Key 4-night minimum binds only reservations made with the $50 non-resident key. Reservations are 2 nights minimum, 4 if they take in Thu-Sun May 15 - Oct 15; 7-night max. **Indian Island 1448 RESTORED** (pre-p3-76 entry + its p3-76 result, then the county booking block from 1451). **Smith Point 1446 stays dropped**: its own page says "Reservations are required for all the sites in the campground", so no walk-up. Blydenburgh 1452, Cathedral Pines 1451, Cedar Point 1453 kept with the same block. Site occupancy is one household. The county's reservation system is being replaced ("coming soon").
- **1453 Cedar Point**: LOW CLEARANCE BRIDGE under 10 ft on Stephen Hands Path - EKKO (~10.5 ft) must take the posted RV route (in the note).
- **1418 Beaver Pond**: only 7 of 129 sites take 23 ft (D 2/4/6, E 3/4/20, F 3, all 30-ft back-ins); no pets.
- **1417 Mills Norrie**: only the 6 electric sites are 30 ft (rest 20 ft); phone -> in-season campground 845-889-4909 (office 845-889-4646).
- **1419** renamed "Piseco Lake Campground (Little Sand Point Loop)" (RA/DEC publish one Piseco Lake Campground with two loops; Point Comfort has the two 40-ft sites).
- **1440 Montour Falls**: website moved to villageofmontourfalls.gov; daily/weekly/monthly/seasonal, phone/form only.
- **1452** season: county camping page still says all close Nov 1, 2025; park page Apr 1 - Nov 11 recorded. Phone corrected.
- Missing dec.ny.gov / parks.ny.gov pages on 355, 348, 364, 338. **355/1419** close 09-05.

### p3-83 (NY, 2026-10-21)
- **1502 Streamside DROPPED** ($54 any site 2027, no gateway). **1507 Shady Shores DROPPED** (new operator Unhitched RV; no 1-night stay offered, no nightly price).
- **1472 Wayne County Fairgrounds**: ownership local -> private (run by the Wayne County Fair association, office 315-597-5372); camping stays open through fair week; page warns "this is a fairgrounds and not a recreational camping site" with "no trailer pads" - kept.
- **1510 Schroon River Escape** $70-90 under the Lake George gateway (14 km); phone corrected (Schroon River RV Resort, LLC).
- **1459 Webster Park**: county pricing sheet PDF gone; out-of-county +$10 unconfirmed.
- **1461 St. Johnsville**: phone -> marina 838-289-4506 (also Campspot's).
- Short listed lengths: 346 Putnam Pond (16 of 61 drive-in at 30 ft), 1411 Stony Brook.

### p3-86 (NY, 2026-10-21)
- **1455 Morningside Park DROPPED** (2023 town fee sheet: "Fallsburg residents only").
- **1463 East Sidney Lake Park**: under-documented - eastsidneylake.org stale (2018 season); website -> town page + USACE page, phone -> town 607-829-6433 (USACE/RIDB list 607-829-6006); may be mostly seasonal (2018 site sold monthly/seasonal). Kept with a caveat; worth a call.
- **1458 Cook Park**: rate sheet leads with seasonal/monthly/weekly; $50 nightly posted; no nightly count.
- **1436 Blueberry Patch**: "under 24 feet" - EKKO fits at 23 ft.
- **1426 Beaverkill**: RA name "Beaverkill (John and Patricia Adams Campground at)". 1426/1427/365 close 09-05.
- Short listed lengths: 1427 Brown Tract Pond (48 of 88 at 20 ft), 365 Buck Pond (73 of 111 at 20 ft).

### p3-85 (NY, 2026-10-21)
- **1421 Cherry Plain DROPPED** (every site 15 ft).
- **1435 Camp Gateway (Floyd Bennett Field)**: status temporarily_closed (NPS 2026-09-30 "remain closed at this time"; no rec.gov availability since 2023; migrant shelter 2023-25). Kept with the caveat; may be closed for good - re-check spring 2027. Fees only from rec.gov's 2019/2020 table. Phone -> park line 718-354-4606; NPS page added.
- **1423 Hearthstone Point**: max_rig 40 -> 30 (RA's longest listed site); DEC page unreadable.
- **356 Eighth Lake**: opens Jun 28 in 2027 only (infrastructure work).
- **1450 Southaven**: kept under the Suffolk walk-up rule (no reservation-only statement); phone -> 631-852-1391.
- **1444 Greenwood**: all 50 sites sold nightly beside a $1,800 seasonal rate.
- Short listed lengths: 1420 Newtown Battlefield (6 of 18 take 23 ft), 1425 Sharp Bridge (10 of 39).
- 1422/20/1425 close 09-05.

### p3-87 (NY, 2026-10-21)
- **13359 Korn's**: town ownership weakly supported (2016 Senate release on the Town Board buying it; operator site never names the town; RA lists it under its private contract). $75/night for 4; if private it would fail the gate (Newark 90 km). Left local.
- **1431 Hunts Pond SF**: May-Sep sites need a DEC permit (phone/email, bookable from Apr 1); first-come Oct-Apr; a bare "ANY vehicle is prohibited." line on DEC's page has no context. Phone -> Lands and Forests 607-371-7268.
- **13729 Moose River Plains**: "Tents or small campers" only, no length stated; Payne Brook bridge failure closes the eastern road segment and sites 1-20 (enter from Inlet). Kept.
- **14339 Niagara Shores**: $42 dry site; hookup sites $51-65 (no gateway; Niagara Falls 43 km) - base passes on the dry site.
- **14320 Pine Ridge**: $30 base is a "Waterfront - No Hookups" site; if tent-only, base $38.
- **13358 Onoville**: ~2/3 seasonal (sold out to returning campers); transient sites book online at a daily rate - passes.
- 1433/13727 close 09-05; 1433 only 5 of 24 drive-in sites at 30 ft.

### p3-88 (NY/NC, 2026-10-21) - NY finished
- **14324 Tamarack DROPPED** (12 nightly of ~200 sites; test 4).
- **13361 Sheridan Bay (town)**: no posted nightly rate (only aggregators: Campendium $40, Jul 2026); nights by phone through the caretaker beside weekly/seasonal. Long-stay tests are for private parks - kept.
- **1462 St. Regis Falls**: website is "Town of Waverly (UNOFFICIAL)"; C1-C11 nightly, C12-C29 seasonal; "$34.00" unitless.
- **638 Cape Point**: temporarily_closed (NPS alert 2026-10-21, post-storm); winter closure from Nov 28 anyway. Inclusion evidence's "25 ft max" is the two-vehicle limit; NPS gives 40 ft.
- **4243 Cotton Patch Goldmine**: website's camping page is injected with UK van-insurance spam; the only "up to 50 feet" sits inside it, so sites.max_rig_ft removed. Rates undated (Last-Modified 2026-07-22).
- **241 Black Mountain**: Isaias closure (Oct 9-13) over; selling nights through Oct 30.
- **23 Balsam Mountain**: 14 RV sites at 24 ft; reservation only.
- Methods: WebFetch reads dec.ny.gov; NPS campgrounds/alerts JSON at developer.nps.gov/api/v1 with api_key=DEMO_KEY; rgsum.py / cat.py (session scratch p3-88) summarise rec.gov rates and the RIDB catalog.

### p3-89 (NC, 2026-10-21)
- **DROPPED (no nightly price / no booking engine):** 4241 Country Woods, 4253 Ho-Hum (both unclaimed RoverPass only), 4244 Goodwin's (monthly workforce), 4240 Jordan Dam ("call for rates").
- **4250 Nantahala Ridge**: entry had mixed in Nantahala RV Resort & Campground (Campspot, 1.7 km west, 828-736-1812, nantahalarvresort.com). Website -> nrcamp.com (ResNexus); Campspot fees, booking and the derived Good Sam false removed. **LEAD**: Nantahala RV Resort & Campground has no entry - vet and add.
- **103 County Line (Kerr Lake)**: RA says holiday minimum drops to 1 night within 14 days; state:NC row says 7 - check the row. Phone added.
- **4247 Double L Farms**: books on its own Hipcamp listing ($42); shares the farm with a mobile-home community, 12 of 26 sites nightly - passes.
- **14344 Farm Pond**: markets monthly/Fort Bragg commuters; $40 nightly posted (copyright 2024); share nightly unknown.
- **4238 Highlands Riverbend**: rate unread (ResNexus captcha); GSMNP 39 km.
- **4233 Hominy Valley** $50, **4245 JCO** "from $50": at the gate.
- No Helene closure notices found in western NC.
