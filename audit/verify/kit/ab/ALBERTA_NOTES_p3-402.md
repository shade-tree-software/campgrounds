# p3-402 Alberta notes (2026-11-11)

Lessons: Alberta Parks pages hide old text in HTML comments (Parks Canada Wabasso) - never use it. FCDA/West Fraser phone-booked PRAs (Watson Creek, Whitehorse Creek) are policy_ref none candidates. Shop site lists ('Near Water' tag, max length) settle waterfront leads and max_rig_ft. Esri sat2.sh 500s: crop existing imagery with PIL. status.operating takes 'open'|'temporarily_closed', not a boolean; a partial closure goes in sites.note.

## 15660
Kneehill County page + Let's Camp (read 2026-11-11): 5 unserviced stalls, C$25 incl. GST, Let's Camp booking, 14-night max confirmed; added dump station and max rig 40 ft (per-site 30-40 ft). Closed for the season; 2027 bookings open Feb/Mar 2027. Phone and pin confirmed.

- PHONE: stored 403-443-0380 = Let's Camp's 'phoneNumber' '1 (403) 443-0380' for this camp (email parkhost@kneehillcounty.com); the county page and the Let's Camp bio give the county office 403-443-5541 'for assistance and details' (already in booking.note). Either is defensible; no change needed.
- SEASON (not written): the Let's Camp bio says 'RESERVATIONS FOR THE 2027 SEASON (MAY-SEPTEMBER) WILL OPEN FEBRUARY/MARCH 2027', and still carries old dates 'Friday May 16th - Sunday September 14th' / bookings 'Tuesday February 25th' (those weekdays are 2025's). No current season dates published, so no season group written.
- WEBSITE: both stored URLs answer 200 and are this campground.
- PIN (51.79415,-113.60623): on imagery it sits on the small treed lane east of the arena, ~23 m from Let's Camp's point 51.79432,-113.60604. OK.
- WATERFRONT: not waterfront confirmed (village lot, no water).

## 8981
Alberta Parks page (May 7, 2026) + Town of Swan Hills page: C$20 FCFS confirmed; sites 20 (derived) -> 18; season May 15 - Sep 15; vault toilets, non-potable pump; phone 780-333-4477; OHV access from campsites = drop candidate; pin OK.

- CRITERIA / OHV (drop candidate): the agency's own page says 'There are OHV trails nearby, which registered campers can access from their campsites.' and lists a 'Loading Ramp'. Riding from the campsite to the trails is OHV use in the campground, the same pattern as Waiparous/Fallen Timber South ('travel to OHV trails from their campsites'). The Town of Swan Hills camping page does not mention OHVs for this site.
- PHONE (stored empty): page 'Information: 780-333-4477' (= Town of Swan Hills office, PH 780-333-4477 on the town site). Page names 'Leaseholder: Town of Swan Hills'; the town's 2024 camping page instead says 'Managed by Blue Ridge Lumber, Operated by Top Height Forestry.' No Facility Operator line. NO seniors line on this page.
- POLICY ROW: first-come only, so the provincial:AB shop/window/fee keys do not arise (not inherited here). Leased to the town; fees are posted on the Alberta Parks page, so no policy_ref change is needed unless the reviewer wants one for the leasehold.
- WEBSITE: stored = the park root (https://www.albertaparks.ca/parks/central/trapper-lea-s-cabin-pra/). Give the camping page https://www.albertaparks.ca/parks/central/trapper-lea-s-cabin-pra/information-facilities/camping/trapper-lea-s-cabin/ (200, this campground) and, optionally, https://www.townofswanhills.com/community/adventure/camping/ (200; the 'Trapper Lea's Recreation Area' block).
- PIN (54.52327,-115.09393): on imagery it is the grass clearing at the entrance off Hwy 33; the campground lane runs ~150 m NE into the trees from it; the page's directions point is 54.523275,-115.093272 (~45 m). OK.
- WATERFRONT: not waterfront confirmed (no water body near the clearing on imagery).
- NOTE: dropped 'picnic tables' and 'hand-pump water' as facility repeats; reworded the OHV line to the agency's wording; added the leaseholder.

## 9013
Alberta Parks page (Jun 5, 2026) + Jul 2026 tear sheet: 49 unserviced FCFS sites at C$25 confirmed, season May 14 - Sep 28 (manual) agrees; no potable water; phone 780-538-5350; seniors line present; not waterfront confirmed; pin OK.

- PHONE (stored empty): page 'Information: 780-538-5350' (tear sheet: 'Campground Information Phone: 780-538-5350'). No Facility Operator line. SENIORS LINE PRESENT.
- WEBSITE: stored = park root + https://reservation.albertaparks.ca (that host no longer resolves - p3-394 - and this campground is first-come anyway). Give the camping page https://www.albertaparks.ca/parks/north/twin-lakes-pra/information-facilities/camping/twin-lakes/ (200, this campground) and drop the reservation link.
- SEASON: page 'Season: May 14 - Sep 28' and the advisory 'The last night of camping at Twin Lakes Provincial Campground is September 27. The campground closes for the season on September 28.' agree with the stored manual season; not rewritten.
- SITE COUNT: the page says 49, but the July 2026 tear sheet numbers only sites 1-39. Kept 49 (the page's table); the reviewer may prefer 39.
- WATERFRONT: not waterfront confirmed. On imagery the loops sit in continuous spruce; the westernmost spurs (tear sheet sites 19-20) are ~45-60 m from East Twin Lake's shore with unbroken forest between; only the day-use/boat launch at the north end touches the water.
- PIN (57.44720,-117.52560): in the middle of the loops on imagery; the page's directions point 57.446335,-117.526507 is ~110 m SW. OK.
- NOTE: dropped 'no potable water (bring your own)' (facilities.potable_water).

## 15656
Town of Vulcan camping page (read 2026-11-11): free first 3 consecutive nights in six months, C$20 a night from the 4th, 14-night max, no reservations, water and sewage disposal - all as stored (manual, 2026-11-10). Phone 403-485-2417 and pin confirmed. Nothing new.

- CONFIRMED: town page 'Vulcan Municipal Campground (Free Campground 1st Avenue South) | By the Arena | Corner of Highway 534 & 1st Ave South | No Reservations | Water and sewage disposal available | Maximum length of stay without a fee is Three (3) consecutive nights in a six month period | 4th day and every day after - $20.00 per night and; - shall not exceed Fourteen (14) consecutive days'; contact '321 - 2nd Street South 403-485-2417'. Website answers 200 and is this campground (Policy PU-06 PDF linked from it, file path dated 2025-12).
- PIN (50.39767,-113.25608): on imagery it sits on the treed stall area east of the arena lot at Hwy 534 and 1st Ave S. OK.
- WATERFRONT: not waterfront confirmed (town lot).
- LEAD (already in DB): the town's other campground, Virginia Mitchell Memorial Park (32 full-service 30-amp sites, C$35, FCFS, May 1 - Sep 30), is on the same page; the database already holds 'Virginia Mitchell Memorial Park'.

## 15390
Parks Canada Jasper camping page (modified 2026-10-14; read 2026-11-11): 'Wabasso Campground and Whirlpool Group Campground will remain closed for the 2026 camping season'; the Wabasso row reads 'Closed until further notice.' Stored status (manual) agrees; no reopening date. Every other Wabasso detail on the page is inside HTML comments, so nothing new written. Pin OK.

- STATUS (manual, agrees): visible page text 'Wabasso Campground and Whirlpool Group Campground will remain closed for the 2026 camping season.' and 'Wabasso | Closed until further notice.' No 2027 reopening is announced. The stored status note's 'contractor use only' is not on this page (it came from the add-stage interim-housing page); not re-read.
- HIDDEN TEXT (not used): the page source keeps the old Wabasso blocks inside <!-- --> comments: 'Sites: 231', 'Electrical only campsites only are equipped with 15 and 30 amp service', and two different fit lines, 'Best suited for tenting, and motorhomes and trailers under 27 feet' and 'Best suited for tents as well as motorhomes and trailers under 35 feet'. Not displayed, so not written (stored sites.count 230 is derived from note prose). When it reopens, re-read the fit line: a 23-ft rig passes either version.
- PHONE (stored empty): the camping page gives only the Parks Canada Reservation Service, 1-877-737-3783 (519-826-5391 outside North America); no campground line. Jasper contact-page URLs tried (/info/contact, /info/coordonnees-contact) answered 404.
- WEBSITE: stored Jasper camping page answers 200 and covers Wabasso. OK.
- PIN (52.7655,-117.9880): on imagery it is in the middle of the fishbone loops between Hwy 93A and the Athabasca River. The page's map point POINT(-117.98745, 52.76195) is ~400 m SSE near the entry road. Stored pin is better. OK.
- WATERFRONT (stored not waterfront): kept. The NE loops' spur ends come within ~25-50 m of the Athabasca's bank, but a riverside trail and a conifer belt run between (imagery hazy, post-fire). At most a riverview lead for the NE-most spurs; with the campground closed and no site photos, it stays down.
- OWNERSHIP: federal (Parks Canada) correct.

## 8945
AP page (updated Jun 5, 2026) + Red Rock Sawmills page: 53 unserviced at C$40, FCFS, May 1 - Oct 14, vault toilets, non-potable pump; confirmed. OHV drop candidate (ride-out from sites). Creekside recommended down to not waterfront. Pin OK.

- OHV DROP CANDIDATE (agency + operator own wording): Alberta Parks: 'Registered campers may off-load and travel to OHV trails from their campsites.' Red Rock Sawmills: 'Off-Highway Vehicle Access: Designated OHV trails nearby (please respect trail use guidelines). You can exit right from your campsite.' It is in the Ghost Public Land Use Zone (an OHV land-use zone; the stored note already said 'OHV staging allowed'). Meets 'adjacent to an OHV trail system / ride-out from sites'.
- WATERFRONT (stored creekside): RECOMMEND DOWN to not waterfront. The operator's site map (Loop Area 1 north of the road, Loop Area 2 south) puts the creek along Loop Area 1's north/east side. On imagery the nearest pads (east side of Loop Area 1, ~51.3660,-114.9850) sit ~30-45 m from the wetted channel but behind a continuous conifer belt on the bank top; the open gravel bar is on the far (east) side. Site numbers on the sign-photo map are not legible enough to place. Lead only: AP and operator both say 'Several campsites are located just steps from the water' (marketing; forbidden as sole basis).
- SITE COUNT: AP 53 unserviced; operator 'Total Campground Sites: 55' (may count the group camp, https://www.redrocksawmill.com/waiparous-creek, 12-15 units, $220 for the first 5). Wrote 53.
- SEASON: AP May 1 - Oct 14; operator's campgrounds page 'generally open April 29 - October 14'. Wrote the AP dates.
- PHONE 587-830-2198: AP 'Information' line and the operator's contact phone. OK. No seniors-discount line on the AP page.
- WEBSITE: stored AP camping page 200, is this campground. Operator page https://www.redrocksawmill.com/waiparous 200. OK.
- PIN (51.36550,-114.98800): inside Loop Area 2 west of the trunk road; AP directions point 51.365836,-114.990125 ~170 m W. OK.
- POLICY: AP lists it, but booking is FCFS with the operator; nothing booked on the shop, so provincial:AB's window/fee rows are moot. No policy_ref change needed.

## 8982
AP page (Apr 21, 2026) + July 2025 tear sheet: 20 unserviced FCFS sites at C$30, season May 14 - Sep 28, vault toilets confirmed; 2026 drinking-water advisory keeps potable_water false. Seniors line present. Not waterfront confirmed; pin OK.

- PHONE (stored empty): page 'Information: 780-538-5350' (tear sheet: Grande Prairie District Office 780-538-5350). No Facility Operator line. SENIORS LINE PRESENT.
- WEBSITE: stored = park root + shop link parkId 330244, which is the Waskahigan Group Use listing, not the FCFS campground. Give the camping page https://www.albertaparks.ca/parks/north/waskahigan-river-pra/information-facilities/camping/waskahigan-river/ (200, this campground) and drop the shop link (or keep it only as the group site).
- WATER: page body says 'Potable water is available.' but the Drinking Water Advisory (effective May 14, 2026, until further notice) says it is not. Kept potable_water false with the advisory dated in facilities.note; re-check in 2027.
- WATERFRONT: not waterfront confirmed. The tear sheet puts sites 1-20 on a loop just north of Hwy 43, with the Little Smoky River ~150-200 m W/NW reached by a trail; imagery shows continuous mixed forest between the loop and the river. The page's 'nice little riverside campground' is marketing; the old note's 'Riverside' is removed.
- PIN (54.74519,-117.15996): on the camping loop; AP directions point 54.745104,-117.160065 ~10 m. OK.
- NOTE: dropped 'bring your own water' (facilities hold it) and 'Riverside'; added 'No firewood for sale' ('Firewood is not available').

## 15003
Lions page (2026 season) + county page: 40 unserviced sites in two areas, C$25 + C$15 reservation fee via Campspot, May 8 - Oct 31 2026, outhouses, non-potable water; riverview kept. Campspot 4.5 (115), Google 4.4 (36). Name covers only the south area.

- RATINGS (club-run): Campspot campspotRating 4.5 from 115 ratings; Google Maps 4.4 (36 reviews) (gm.py returned a results list whose first place carried 4.4/36 and the Lions website, at 51.5394,-114.6105, the north area). Both above 4.0. Not a drop.
- NAME / SCOPE: the entry is 'Water Valley Campground - South', but the operator and county describe ONE campground of 40 sites in two areas (north: sites 1-21 with registration/office at the north gate, 30033 Range Road 52; south: day use + sites 26-39c, south gate 30027 Range Road 52), one booking page and one fee. The areas are ~300-400 m apart across the river, under the ~1 km split threshold. No North entry exists in the DB. Recommend renaming to 'Water Valley Campground' (sites.count 40 written for the whole campground).
- PHONE (stored empty): the Lions pages give only email watervalleycamp@cremonalions.ca; Campspot park record phoneNumber 403-996-0300. Suggest 403-996-0300 (Campspot's operator-entered number; not on the Lions site).
- WEBSITE: stored http://cremonalions.ca/Water%20Valley%20Campground/ answers 200 and is this campground. Booking page https://www.campspot.com/book/watervalleylionscampground (Campspot park 4851 'Water Valley Campground', CAD). No 2027 availability yet (reservations open March 31).
- OWNERSHIP: local correct (county page: 'owned by Mountain View County and operated by the Lions Club of Cremona').
- WATERFRONT (stored riverview): kept. Lead only (never upgraded): on imagery the east end of the south area's spur (operator map sites 36-39c; clearing ~51.5363,-114.6087) opens onto a grassy point bar inside the river bend, roughly 30-40 m from the water with no tree screen; the river there is ~15-20 m wide, so an on-water value would be creekside, not riverfront. Site numbers placed from the stylised operator map only, not confirmed on the ground. The north loop (sites 1-21) sits behind trees above the bank.
- PIN (51.5368,-114.6106): in the south area between the two Range Road 52 bridges, ~40 m from Campspot's point (51.53644,-114.610393). OK for the south area; if renamed to cover both, still acceptable (Google's point 51.5394,-114.6105 is the north area ~290 m N).
- MAX RIG: not stated anywhere read; Campspot had no site list for 2027 dates. Occupancy rules allow 'one camping accommodation unit of any kind'. Not written.
- OHV: Guests page prohibits riding an off-highway vehicle in the campground. No OHV issue.
- POLICY: policy_refs local:AB, local; booking on Campspot with its own $15 fee - nothing to change.

## 8921
AP page (Apr 17, 2026) + West Fraser page: 38 unserviced sites (6 walk-in tent), C$20 (seniors C$15) + C$10 reservation fee, 15 reservable by phone with FCDA / 24 FCFS, Apr 24 - Oct 11, pump water not potable. Booking corrected from FCFS-only. Riverfront recommended down. policy_ref none candidate.

- POLICY_REF NONE CANDIDATE: booked by phone with the Fox Creek Development Association (780-865-2154), C$10 reservation fee, not on shop.albertaparks.ca; the provincial:AB row's 90-day window and C$12 fee do not apply. I wrote reservation_fee 10 and platform phone; the window would still inherit 90 unless policy_ref is set to none.
- WATERFRONT (stored riverfront): RECOMMEND DOWN to not waterfront. On imagery the campground road runs ~600 m W-E along the south side of the McLeod River's floodplain (from ~53.0743,-117.2713 to the east-end curve at ~53.0752,-117.2665); the closest stretch (north side of the road, ~53.0752,-117.2670 to -117.2655) is ~35-45 m from the main channel's south bank, but through a continuous dense conifer belt with no open apron; the west part sits behind a wet meadow ~150-200 m from the river. No site numbers placed (no site map found). Lead: AP says 'a few next to the McLeod River'; operator 'located adjacent to the McLeod River' (marketing; not enough).
- SITES: AP 38; WF '38 Campsites' but also '15 ... for reservations and 24 on a first-come, first-served basis' (=39) and 'six walk-in tenting only sites'. Wrote 38.
- ROAD (operator wording, not a drop trigger): 'The road is accessible by two-wheel drive, but there can be snow on the campground road well into the first two weeks of May.' Kept as a caveat in the note.
- PHONE 780-865-2154: AP 'Information' line = FCDA reservations line on the WF page. Stored phone empty; suggest 780-865-2154. SENIORS LINE PRESENT on AP page; WF gives $15 seniors' rate.
- WEBSITE: stored park root + WF page. Give the camping page https://www.albertaparks.ca/parks/central/watson-creek-pra/information-facilities/camping/watson-creek/ (200) and keep https://www.westfraser.com/responsibility/recreation/frma/campgrounds/watson-creek (200, this campground).
- PIN (53.07480,-117.26600): on the campground road's east-end curve, inside the campground; AP directions point 53.074403,-117.271286 is ~355 m W, mid-campground. Within the campground, so not moved; the reviewer may prefer ~53.0746,-117.2690 as the centre.
- FIREWOOD: AP 'No charge firewood available at campground.'

## 8922
AP page (Aug 6, 2026) + shop site list: 20 sites (19 RV + 1 tent-only), 25-100 ft, five pull-throughs, C$28, reservable on the shop, May 8 - Sep 19, vault toilets, pump not potable. Season and count corrected. Google 4.4 (58). Pin across the road from the campground.

- SEASON: derived 05-01..09-30 'Approximate' -> AP 'Season: May 8 - Sep 19'. Shop status line for parkId 330152: 'Closed through Thu May 06 2027' (whole Brazeau Reservoir listing).
- SITES: derived 18 -> 20 (AP table; shop lists 01-20, site 18 tent only).
- OHV (stays): AP 'OHV trails are located nearby, but they are prohibited in the campground.' General campground with an OHV side, no OHV use in the campground.
- PHONE (stored empty): AP 'Information: 1-855-721-3975' (Facility Operator Westward Bound Campgrounds); Google lists the same number. Suggest 1-855-721-3975. SENIORS LINE PRESENT.
- WEBSITE: stored = park root + shop link. Give the camping page https://www.albertaparks.ca/parks/central/brazeau-reservoir-pra/information-facilities/camping/west-canal/ (200, this campground); keep the shop link https://shop.albertaparks.ca/camping/brazeau-reservoir-provincial-recreation-area/r/campgroundDetails.do?contractCode=ABPP&parkId=330152 (200). westwardbound.ca/west-canal-campground.htm answered 404.
- PIN (52.95261,-115.52833): on a gravel lot NORTH of the reservoir road. AP directions point 52.950938,-115.527559 and Google's place 52.951311,-115.5273425 are both SOUTH of the road on the treed strip between road and reservoir, ~160-190 m from the stored pin. Under 250 m but across the road; suggest moving to 52.95120,-115.52740. Esri imagery there shows only unbroken forest (no loop visible; imagery may predate the loop or canopy hides it).
- WATERFRONT (stored not waterfront): kept. Lead: the shop tags sites 01 and 02 'Near Water'; AP says 'located near the waterfront and is well treed'. The treed strip south of the road is ~100-150 m deep to the reservoir and imagery shows no loop or open apron, so no site could be placed.
- GOOGLE: West Canal Campground 4.4 (58) (agency campground; for reference).

## 8923
AP page (May 13, 2026; advisory Nov 5, 2026) + West Fraser page: sites 1-7 permanently closed (rockfall), 10 general + 9 equestrian left, C$20 + C$10 reservation fee by phone with FCDA (5 reservable/5 FCFS general), May 1 - Oct 31, pump not potable. Creekside confirmed. policy_ref none candidate.

- STATUS: partial closure, agency wording: 'Due to rockfall hazards identified in parts of Whitehorse Creek Campground, campsites 1-7 are permanently closed.' (effective May 11, 2026, until further notice; updated Nov 5, 2026). Not written as a status (the campground is open); recorded in sites.note.
- SITES: derived 17 -> 10 general (sites 8-17); the 9 equestrian sites are 'only for parties with horses', so they are in sites.note, not the count. AP table says 19 (10 + 9).
- ACCESS WORDING (operator, mention only, not a listed trigger): West Fraser: 'follow this road, through a tunnel, to the campground'. No clearance is posted on either page; 'The road is accessible by two-wheel drive.' Not researched further per the brief.
- POLICY_REF NONE CANDIDATE: reserved by phone with Fox Creek Development Association (780-865-2154), C$10 fee; not on shop.albertaparks.ca. NO SENIORS LINE on the AP page.
- PHONE 780-865-2154 (AP Information = FCDA reservations). Stored phone empty; suggest it.
- WEBSITE: stored park root + https://www.westfraser.com/responsibility/recreation/frma/campgrounds/whitehorse-creek. Give the camping page https://www.albertaparks.ca/parks/central/whitehorse-creek-pra/information-facilities/camping/whitehorse-creek/ (200) and the WF page https://www.westfraser.com/responsibility/recreation/frma/campgrounds/whitehorse-creek-campground (200, this campground; check the stored WF URL redirects there).
- WATERFRONT (stored creekside): confirmed. On imagery the loop's south arc and the gravel turnaround at its SE corner (~52.9846,-117.3438) sit ~25-50 m from Whitehorse Creek's channel across an open grass meadow with no tree screen; the creek is a braided gravel channel ~15-25 m wide (creek-sized). The closed sites 1-7 appear to be the west strip under the scree slope, also near the creek; the confirmation rests on the loop, not on them. Site numbers not legible (no site map found).
- PIN (52.9841,-117.3450): on the meadow between the loop and the creek; AP directions point 52.984389,-117.344076 ~70 m E. OK.
- OHV: WF 'There are no off-highway vehicles (quads) allowed in this campground or Park (unless on trailers).' No issue.

## 9006
AP page (Jul 15, 2026) + shop list + Mar 2026 tear sheet: 53 sites (33 power 15/30 A at C$38, 20 unserviced at C$30), reservable on the shop, May 14 - Sep 8, vault toilets; derived showers cleared (showers are at Ross Lake). Lakeview kept. Pin OK.

- SHOWERS: derived true cleared (null). The page lists no showers; the only Shower Building named is at Ross Lake Campground (Fall Construction notice), and the tear sheet's shower icon sits in the Ross Lake area.
- DUMP: not written. The amenity list includes 'Sewage Disposal' but the text says the campground 'is a short drive from the sanitary dump station' (tear sheet: dump station on the road between the lakes). Reviewer may set dump false.
- SEASON: derived 05-15..09-15 'Approximate' -> page 'Season: May 14 - Sep 8'. Shop status for parkId 330132 (the whole park listing): 'Closed through Wed May 19 2027'.
- PHONE (stored empty): page 'Information: 780-594-7856' (tear sheet: Cold Lake Area Office). The Ross Lake Campground Booth (seasonal) 780-943-2482 is for Ross Lake. Suggest 780-594-7856. SENIORS LINE PRESENT. Accessible site B-31 is in Ross Lake Loop B, not this campground.
- WEBSITE: stored = park root + shop link. Give the camping page https://www.albertaparks.ca/parks/north/whitney-lakes-pp/information-facilities/camping/whitney-lake/ (200) and keep the shop link https://shop.albertaparks.ca/camping/whitney-lakes-provincial-park/r/campgroundDetails.do?contractCode=ABPP&parkId=330132 (200).
- WATERFRONT (stored lakeview): kept. Lead only (never upgraded): tear sheet sites 41-46 at the north end of the west strip sit ~50-70 m from the Whitney Lake beach over sparse, open ground on imagery (leaf-off; may be screened in summer); spur ends of sites 49-53 are ~25-40 m from a marshy lagoon west of the strip whose connection to the lake is unclear. Shop tags no Whitney Lake site 'Near Water'. No site confirmed at the water's edge.
- PIN (53.82850,-110.54700): on the fishbone loop of sites 1-27; AP directions point 53.829954,-110.548769 is the beach/day-use ~200 m NW. OK.
- FIT: sites 23 and 24 are 21 ft on the shop; every other site 30-61 ft. No criteria issue.

