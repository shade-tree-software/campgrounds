# Waterfront re-audit leads from phase 7

A verifier's source (operator page or booking engine) claims water access that differs from
the stored `waterfront`. Per the curation doc's rule #7 that triggers the gate, both ways; a
booking-engine tag alone decides nothing. Work these with the full waterfront procedure.

## Open leads carried over from the Montana section

- **806 Loraine Campground, Harold Parker SF (MA)** — stored "not waterfront" (--AWH). ReserveAmerica
  tags 14 sites in loop "Sites 59-90" Waterfront; RV-capable STANDARD sites 61, 63, 69, 71, 75,
  77, 81, 83, 87 (25-40 ft). Still open: the stored pin (42.6056,-71.1003) is in empty woods and
  Google's "Lorraine Park Campground" pin (42.6106,-71.0907) shows no loop either; mass.gov and
  the RA catalog both refuse plain HTTP. Needs the DCR campground map. AWH's call stands meanwhile.
- **1140 Glen Maury Park (VA, City of Buena Vista)** — stored riverview. The city's camping page
  (2026 kiosk map) names lower-campground RV areas "Riverside" (sites 104-115) and "Water's Edge"
  on the Maury River. Names alone prove nothing; needs the map + satellite for pads at the bank.
- **13086 Riverside Campground (VA, Holston)** — stored not waterfront. Operator: "2,000 feet of
  scenic river frontage along the North Fork Holston River", fishing "right from your campsite",
  tent/pop-up sites "most situated right on the river". The question is whether any of the 94
  full-hookup RV sites front the river; needs the site map + satellite.
- **236 Amelia WMA (VA)** — stored lakefront (--AWH: "one [parking area] on the lake"). DWR's
  statewide rule (https://dwr.virginia.gov/camping-on-wmas/): "It is unlawful to camp within 300
  feet of any lake or facility (building, boat ramp, etc.)" - so no legal camp spot is within the
  ~50 m on-water bound; at best lakeview from 90 m+ if the view is open.
- **530 Bark Camp (VA, USFS)** — stored not waterfront (--AWH: trees likely block the view). USFS:
  "situated beside a 45-acre lake" with a shoreline trail; needs the site map + satellite.
- **255 Bath County Recreational Campground (VA, Dominion)** — stored lakeview; DWR says "Seasonal
  lakeside camping" at the recreation ponds.

## Resolved 2026-10-24, 6125 Beaver Creek Park split (AWH; audit/verify/splits/6125.json)

- **6125** is now **Shambo (Beaver Creek Park)**, not waterfront, re-pinned off the RV dump lot (the old pin)
  onto the Shambo-Doney-Hagener sites; new **15559 Springs Campground** (south end, not waterfront, canopy) and
  **15560 Beaver Creek Reservoir** (lakefront: NAIP, open unused grass 15-20 m from the beach, at pool level,
  dam at the NW corner). Excluded: Bearpaw Lake FAS (FWP 20-ft trailer limit), reservable group sites, Camp
  Kiwanis, Boy Scout Camp, picnic memorials, and the scattered northern-half pull-offs (no loops or rigs seen).

## Resolved 2026-10-24, Montana wf-mt-6 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **6286 Sheridan** not waterfront -> creekside (rec.gov RV sites 08/09, 30/33 ft, tagged Riverfront;
  spur ~20 m from Rock Creek); **6284 Sage Creek** not waterfront -> creekside (legible satellite: pads ~15-23 m
  from Sage Creek across open meadow; access route already in the note, kept by AWH 10-22).
- Stand: **6280 North Dickey Lake** not waterfront (FS site map: no site at the shore; re-pinned from the access
  road onto the loop); **6258 Reservoir Lake** lakeview (pads 40-50 m back behind open pines); **14172 Willow
  Creek Reservoir** lakefront (open grass ~10-15 m from high water; dam 1.5 km E, not below it).

## Resolved 2026-10-24, Montana wf-mt-5 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **14138 Lichen Cliff FAS** riverview -> creekside (FWP photo + satellite: pullout ~7-10 m from Little
  Prickly Pear Creek, thin shrub fringe only).
- Downgraded: **6315 Chisholm** lakeview -> not waterfront (no rec.gov water tags; west arc ~33-40 m inside
  continuous dense conifer, main pool 300 m+ away; low confidence).
- Stand (drawdown leads: measured to high water, per the gate): **14121 Eureka Reservoir**, **14143 Martinsdale
  Reservoir**, **14148 Newlan Creek Reservoir** lakefront; **6103 Painted Rocks SP** lakeview (nearest pad
  25-32 m behind scattered pines, open area by the water is ramp parking); **6310 Boulder Creek** riverview
  (low; fire closure already recorded in mt-20).
- Held: 6125 Beaver Creek Park (see its lead above).

## Resolved 2026-10-24, Montana wf-mt-4 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **6239 Murray Bay** not waterfront -> lakefront (rec.gov sites 02-06, 08, 11, 12 tagged Lakefront,
  33-60 ft; spurs ~13-27 m from Hungry Horse's full-pool edge); **6233 Holland Lake** lakeview -> lakefront (FS
  Bay Loop map: south-spur RV sites 018/020/021 end ~15-20 m from the lake, no road between; rec.gov carries no
  water tags at all; canopy-blind, low confidence).
- Stand: **6211 Big Larch**, **6173 Rainbow Point**, **6065 Wayfarers (Flathead Lake SP)** not waterfront (pads
  100-190 m back behind forest/road); **6214 Pete Creek** not waterfront (canopy-blind, no per-site source; low);
  **6245 Beaver Creek (Spotted Bear)** riverview (FS "<100 ft", resolvable pads 50-70 m back in old growth; low);
  **6097 Coal Banks Landing** riverview (nearest tables across the used boat-ramp apron).

## Resolved 2026-10-24, Montana wf-mt-3 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **6062 Logan SP** lakeview -> lakefront (ReserveAmerica per-site "Shore" on RV sites A013-A015/A017;
  pads ~40-50 m from Middle Thompson Lake across open unused meadow; low confidence, loop labels read off FWP's
  schematic); **6059 West Shore Unit (Flathead Lake SP)** not waterfront -> lakeview (ReserveAmerica per-site
  "Water View" on all 12 RV sites; canopy-blind, low confidence).
- Stand: **15376 Rocky Mountain Hi**, **15452 Yellowstone Park / Mountainside KOA**, **6126 Riverfront RV Park**
  (old evidence misplaced the river; it runs along the SE edge, still behind the loop road) not waterfront;
  **14597 River Edge Resort** riverview (tent sites hold the bank); **6220 Big Beaver** riverfront, re-pinned
  off the road onto the Boulder River pads; **6225 Eagle Creek** not waterfront, re-pinned from the entrance
  junction onto the loops.

## Resolved 2026-10-24, Montana wf-mt-2 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **6189 Emery Bay** not waterfront -> lakefront (rec.gov sites 2-6 tagged Lakefront; site 6 ~10-15 m
  from Hungry Horse's high-water edge); **15386 Lake Five Resort** not waterfront -> lakefront (operator ResNexus
  site map: Lake Sites 1-12 between road and shore, spurs ~10-15 m from the water; reverses the 10-19 call);
  **6150 Parkside** riverview -> creekside (rec.gov 12 RV sites tagged Riverfront, ~25-30 m from Rock Creek
  under open canopy; creekside to match Basin on the same creek); **6162 Seeley Lake** not waterfront ->
  lakeview (rec.gov SLS27-29 tagged Lakefront but pads ~50-60 m back behind the day-use beach; SLS29 open
  ground with the lake visible; low confidence); **6137 Merry Widow** not waterfront -> riverview (operator
  sketch map puts sites 14-28 along the Boulder; ~35-45 m across a gravel flat that carries the footbridge
  path, sightline open; low confidence).
- Stand: **6241 Snowbank** riverview (no per-site water tags; creek behind a riparian band), **6216 Rombo** and
  **6144 Camp Sula** not waterfront (pads 30-70 m back behind continuous riparian trees; operator prose only).

## Resolved 2026-10-22, Montana wf-mt-1 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **6076 Big Arm** lakeview -> lakefront (ReserveAmerica per-site "Proximity to Water: Shore" on
  A004-A016/B001-B016, pads ~25-50 m from the beach's high-water edge in open pines; low confidence, no per-site
  map exists); **6086 Moose Creek Flat** not waterfront -> riverfront (satellite: pads 05-09 ~15-25 m from the
  Gallatin across open meadow; 01-04 stay screened); **6201 Langohr** riverview -> creekside (sites 06/07
  ~10-15 m from Hyalite Creek); **6212 Lake Alva** not waterfront -> lakefront (rec.gov LSS4-LSS6 tagged
  Lakefront, canopy case; re-pinned west of Hwy 83).
- Downgraded: **6251 Lid Creek** lakeview -> not waterfront (pads 55-75 m inside continuous forest).
- Stand: **6203 Greenough Lake** (rec.gov tags 7 Riverfront, but legible conifer stand between pads and Rock
  Creek; re-pinned off the entrance bridge), **6196 Lolo Creek** (re-pinned onto the loops), **6198 Many Pines**
  (re-pinned west of US-89).

## Resolved 2026-10-21 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **861 Hyner Run** not waterfront -> creekside (DCNR map + RA per-site tags, canopy case);
  **128 Promised Land** lakeview -> lakefront (FHU site 136 only; note says so); **14272 Penn's
  Creek** not waterfront -> creekside (z19 satellite: pads ~15 m from the bank); **647 Douthat**
  not waterfront -> lakeview (DCR Lakeside site map + satellite: 19 sites across the loop road from
  the north shore; pin moved onto that loop; --AWH note kept, dated --Claude line added).
- Downgraded: **252 Bear Creek Lake SP** lakefront -> not waterfront (AWH: A18 is 20 ft, not EKKO; RV loops away from the lake);
  **757 Black Pearl Farms** riverfront -> not waterfront (AWH: the waterfront RV
  site is gone; RV sites are Farm View/Blue View, riverside sites tent-only); **1184 Stony Mountain** lakefront -> not waterfront (operator: the one lake site is a
  tent site; transient loops 100+ m back; pin moved onto the loops; low confidence - a site map
  could reverse it); **1048 Milton Loop** riverview -> not waterfront (continuous tree band);
  **590 Jekyll Island** coastal woods -> not waterfront (operator: "There are no waterfront
  campsites"; salt marsh and the beach road lie between, not the campground's own forest).
- Stand, evidence refreshed: 863 Sizerville, 78 Kooser, 619 Keystone (--AWH), 14316 Riverbank,
  13088 River Run, 1186 Whispering Winds, 1173 Moyer's Grove, 14277 Fire Pit (the creek claims
  are canopy-hidden with no per-site source, so they stay down).
- Closed, existing evidence stands: 860 Fowlers Hollow, 835 Hills Creek, 862 Lyman Run,
  127 Tobyhanna, 558 Laurel Hill.
- **924 Cape Charles KOA** (p3-16): KOA's page says "waterfront RV camping"; the --AWH firsthand
  note ("partial bay view, but none are directly on the beach") keeps bayview.
## Open leads, all states (appended during phase 7; work these with audit/verify/kit/mkwfbatch.py)

- **3900 Bond Falls Consolidated (MI)** — dam screen 2026-10-21: the pin sits in the woods just
  below Bond Falls Main Dam (10 m under the flowage's pool), not at a campground; the camp loops
  are along the flowage shore somewhere south. Find the loops (UPPCo map) and re-pin before the
  lakefront call can be re-checked.
- **3532 Totogatic Park (WI)** — dam screen 2026-10-21: pin is in woods ~250 m from the Minong
  Flowage, 15 m above it; OSM's campground node is 46.14171,-91.93697. Re-pin onto the loops.
- **247 Hog Island WMA, Carlisle Tract** — bayfront. DWR's 300-ft rule names boat ramps; the
  tract's ramp is its one named facility, so a camping area at the ramp lot would be unlawful.
  Same question as asks #8 for the rest of AWH's beach camping areas.
- **587 Cypress Glen (Withlacoochee SF)** — FDACS: "several sites having a view of the water"
  (Silver Lake); entry is not waterfront. Lakeview tier may apply to some sites.
- **170 Mutual Mine (FFS)** — FDACS: sites "in a horseshoe formation next to a ... rain-filled lake
  that was formerly a mine pit"; ReserveAmerica "Type of View: Lake". Entry not waterfront.
- **393 St. Joseph Peninsula (Shady Pines)** — coastal dunes rested on AWH's note about two dune
  campgrounds; only Shady Pines remains (Gulf Breeze gone). Check Shady Pines sits behind the dunes.
- **4841 Turtle Beach (Sarasota Co.)** — county: "premier beachfront campground", "direct beach
  access"; entry not waterfront.
- **4715 Bear Lake (Blackwater River SF)** — booking site: 11 of 31 RV sites "Proximity to Water:
  Lakefront"; entry not waterfront.
- **4813 Coe Landing (Leon Co.)** — county booking site marks six sites "Waterfront"; entry lakeview.
- **4837 John Prince Park (Palm Beach Co.)** — county: "51 sites located on beautiful Lake Osborne",
  lakefront-site rules; entry lakeview.
- **15417 Naples / Marco Island KOA** — KOA: "surrounded by the beautiful Rookery Bay", sites
  "backed by trees and mangroves", boat ramp, creek fishing; entry not waterfront.
- **158 Oscar Scherer SP** — Reserve Florida: sites 1-17 and 70-90 "adjacent to a creek"; park page
  "several campsites along the creek"; entry not waterfront.
- **153 Rainbow Springs SP** (weak) — campground "located along the Rainbow River", but the swim
  area/launch is "a substantial walk from campsites".
- **4770 Sportsman's Cove (Orange Lake)** — operator sells "Waterside" sites ($50-55) and a
  "waterfront" cabin; entry not waterfront.
- **743 Wickham Park (Brevard Co.)** — county rate rules: "there are no water access or water view
  sites at Wickham Park"; entry pond (AWH: "Several sites are on small ponds"). Contrary, downward.
- **14391 RV Village at Lake Panasoffkee** — operator: "Situated on the southern banks of Lake
  Panasoffkee", "FISHING DOCK/BOAT SLIPS ON SITE"; entry not waterfront.
- **4740 Ocean Pond (USFS)** — rec.gov: "on the north shore of Ocean Pond", "multiple campsites provide
  lakeside access"; entry not waterfront.
- **14383 Pine Lake RV Park** — operator: "along the shimmering waters of Pine Lake"; entry not waterfront.
- **15421 St. Pete / Madeira Beach KOA** — "Kayak Access" sites through the mangroves, "Along Bayou"
  sites with bayou views; entry not waterfront.
- **165 Silver Lake (Withlacoochee SF)** — booking page "On the shore of Silver Lake"; entry lakeview
  (AWH note supports lakeview).
- **4728 Panther Pond** (weak) — its one RV site, 016, "Type of View: Lake".
- **14398 Sunny Shores MH & RV** — "Our canal opens straight onto 5,000-acre, spring-fed Lake
  Panasoffkee", fishing dock; entry not waterfront.
- **14385 Wewa RV Park** — "The back of Wewa RV Park borders pristine Stone Mill Creek"; entry not waterfront.
- **4734 Wright Lake (USFS)** — "along one portion of the lakeshore", "views of the lake"; entry not waterfront.
- **633 Little Talbot Island SP** — entry coastal woods, but the --AWH note says "campground is not
  waterfront"; park page: sites a half-mile from the beach, "tidal creeks border the western edge",
  several RV sites "can get wet during ... high tides".
- **4719 Karick Lake South (Blackwater River SF)** — ReserveAmerica marks 7 of 14 sites "Proximity to
  Water: Lakefront" (siteIds 1202-1214 even); entry lakeview.
- **4823 Newport Park (Wakulla Co.)** — "nestled along the St. Marks River"; entry not waterfront (a
  "short nature path" to the deck suggests the sites sit back).
- **168 River Junction (Withlacoochee SF)** — ReserveAmerica marks sites 001, 014, 016 "Near Water";
  entry and the --AWH note say not waterfront.
- **14387 Panhandle RV Resort** (minor) — "Two Fishing Ponds ... right on the property".
- **14870 Seminole Campground** — "47 creek side campsites" on Pop Ash Creek; entry not waterfront.
- **14434 Scott's Ferry** (weak) — "Located on the Chipola River with boat launch"; entry not waterfront.
- **266 Big Bend (USFS, WV)** — entry riverfront on the --AWH note ("sites adjacent to the water");
  rec.gov and the FS page say "The river is located 200 feet from campground".
- **1227 East Fork (WV)** — operator: "waterside" sites, "primitive waterfront sites", a river that
  "runs the length of the campground"; entry riverview.
- **426 Riverside Cabins & RV Park (WV)**: operator says "RV Sites – On the bank of the Potomac River"; entry is riverview, and the --AWH note says the RV sites are set back from the river.
- **490 Riverside, Watoga SP (WV)** (weak): the booking site tags ~20 sites "Riverview" and none "Riverfront"; entry is riverfront (--AWH firsthand).
- **263 Summersville Lake Retreat (WV)**: FAQ "We overlook Summersville Lake and have a fantastic view of the lake but we do not have direct access"; premium sites "stare out on Summersville Lake". Entry is not waterfront, so a view tier may be earned.
- **498 Army Camp, NPS (WV)**: NPS says the sites are "along the banks of the New River at one of its many horseshoe bends"; entry is not waterfront (--AWH says the sites are not waterfront).
- **1192 Great Bend (WV)**: the city says it's "Nestled along the Sandy Creek close to where it flows into the Ohio River"; entry riverfront, so the water at the sites may be the creek.
- **83 Stuart Recreation Area (WV)**: rec.gov says "perched along a bend on the Shavers Fork River" and "along the banks"; entry riverview.
- **428 Brooklyn Heights Riverfront (WV)**: operator names RV6-RV10 "Primitive Riverfront RV site" (the river is across a narrow dead-end road); RV1 is "about 50 feet from the Dry Fork River"; entry riverview.
- **232 Bluestone SP (WV)**: camping page calls it "the perfect lakeside retreat camping spot" and the note says "lakeside campsites"; entry not waterfront. Old Mill and East Shore are closed for dam work, and Meador is the RV campground.
- **13120 Eagle's Nest (WV)**: operator offers "permanent waterfront lodging", "Family Campground Near Water" with swimming and fishing in Patterson Creek; entry not waterfront.
- **1201 Blue Heron Landing (WV)** (weak): "camp, and kayak right on Mill Creek with direct access on-site", but the rate page puts the tent sites, not the RV lots, along the creek.
- **457 Gauley Tailwaters (WV, NPS)**: the entry's own note says "with sites directly along the river"; NPS says only "located just below Summersville Dam" (below a dam: river value only, from the river itself). Entry not waterfront.
- **456 Glade Creek, NPS (WV)**: the note says "sites directly adjacent to the creek" and NPS says "near the banks of the New River and the Glade Creek Trailhead"; entry not waterfront.
- **503 Big Rock (WV)**: entry riverfront, but its own --AWH note says "Sites are not waterfront"; rec.gov says "adjacent to the Cranberry River". Re-audit (likely a downgrade).
- **463 Horseshoe (WV)** (weak): rec.gov "relaxing beside the creek" (Horseshoe Run, a snorkel site); entry not waterfront.
- **4353 Briarcliffe RV Resort (SC)**: operator "located on the Intracoastal Waterway", pool "overlooking the Intracoastal Waterway"; entry not waterfront (sites may be set back; check imagery).
- **15491 Myrtle Beach KOA (SC)**: KOA's booking form sells a back-in full-hookup type with "your private deck overlooking the water"; two tidal lakes connect to the Atlantic via Withers Swash; a 2026-10-15 review "patio site with a deck on the water". Entry not waterfront (2026-10-19 audit saw only an owners' waterfront type).
- **1505 Birch Haven (NY)**: operator claims "a majestic view of the St. Lawrence shipping channel"; entry not waterfront (a view tier may be earned).
- **335 Cedar Point SP (NY)** (weak): ReserveAmerica tags 13 sites "Near Water" (003-011, 014, 016, 018, 020) - its generic icon; entry riverview, note says one 20-ft riverfront site.
- **1407 Frontier Town (NY)** (weak): ReserveAmerica puts the 91-acre facility "on the shores of the Schroon River"; entry not waterfront. Property-level claim.
- **1442 Myers Park (NY)**: on Cayuga Lake ("extensive Cayuga Lake frontage", Campspot "Waterfront") but entry says `riverfront` - type looks wrong.
- **1409 Limekiln Lake (NY)** (weak, contrary): ReserveAmerica tags all 263 sites "Near Water - no"; entry lakefront. DEC pages 403.
- **334 Oneida Shores (NY)** (contrary operator claim): county page "over 50 shaded lake view campsites" and "Basic & Waterfront Site" (tents only); entry not waterfront.
- **1518 Rancho Pines (NY)**: Campspot feature "Waterfront"; along the Schroon River with a canoe launch; entry not waterfront.
- **1516 Royal Mountain (NY)** (weak): site 16 "by the pond" (stocked fishing pond).
- **21 North-South Lake (NY)** (weak, contrary): RA marks all 203 sites "Near Water - no"; entry lakefront, --AWH "Some campsites are on the lake" supports it.
- **1481 Brookside Beach (NY)** (contrary operator claim): "A peaceful campground located directly on Lake Erie", "sunsets right from your campsite"; entry lakeview, note says the beach is across Rt 5.
- **1395 Taughannock Falls (NY)** (weak): RA description "Campsites and cabins overlook Cayuga Lake"; entry not waterfront; RA tags every site "Near Water - no".
- **1511 Massena International Kampground (NY)**: 2026 rate sheet sells "WATER, ELEC. & SEWER (WATERFRONT)" sites at $50; entry not waterfront.
- **1460 North Bay Campground (NY)**: city page "A peaceful lakefront setting" with "waterfront sites"; entry lakeview.
- **1416 Paradox Lake (NY)**: RA "located on the shore of Dark Bay, which is on Paradox Lake"; note counts ~5 waterfront sites; entry not waterfront.
- **15466 Lake Placid / Whiteface KOA (NY)** (weak): KOA sells "Riverside" site types "near the beautiful Ausable River"; entry not waterfront - look at the Riverside sites on imagery.
- **1453 Cedar Point County Park (NY)** (weak): "commanding views of Gardiner's Bay" (park + glamping tents, not the family sites); entry not waterfront.
- **13359 Korn's (NY)**: "39 acres of wooded land on the Shawangunk Kill River"; entry not waterfront.
- **14339 Niagara Shores (NY)**: lakeview RV sites "Most ... currently located waters edge with panoramic views of Lake Ontario"; entry lakeview.
- **14320 Pine Ridge (NY)**: sells "Deluxe Waterfront" and "Waterfront - No Hookups" sites on the river through the park; entry riverview.
- **13728 Luzerne (NY)** (weak): RA "partially surrounds Fourth Lake"; entry not waterfront.
- **13727 Rogers Rock (NY)** (weak): west shore of Lake George with a sand beach; entry not waterfront.
- **15454 Asheville East KOA (NC)**: KOA "Riverfront camping", sells "Riverside" back-in/pull-through types "parallel to the serene Swannanoa River" (B28, B29; reviewers name A1-A10); entry not waterfront.
- **4275 At The Ridge (NC)**: "Premium sites are on the river"; ResNexus River Campsites #4 and #6 full hookup "on the river" (North Fork French Broad); entry riverview.
- **13367 Kennedy Park & Marina (WV)**: operator lists "Primitive: Riverfront Sites" on the Ohio; entry riverview (primitive sites may not take a 23-ft rig).
- **747 Momma Tried (WV)** (weak): Hipcamp tent spots "by the river", "riverfront access"; entry field says riverfront while AWH's note says sites are not waterfront - the two stored statements disagree.
- **4317 Cashie River Treehouses (NC)**: town's Campspot listing tags "Waterfront" and "Beach - Public Access" (on the Cashie River); entry not waterfront.
- **4326 Mayo Lake Park (NC)** (strong): former county RV page "on-water RV and tent sites" (1-28); county map shows Area 2 lining the shore; entry not waterfront.
- **245 Lake Powhatan (NC)**: FS + rec.gov "on the banks of Lake Powhatan", loops "within walking distance of the lake"; entry not waterfront (note says not on the lake).
- **32 Linville Falls (NC)** (weak): rec.gov "Linville River ... winds beside the campground"; entry not waterfront.
- Kerr Lake / Jordan Lake (NC: 104/106/108/146) ReserveAmerica "Near Water - no" on every site - a blanket attribute, ignore.
- **4306 Almond Boat & RV Park (NC)** (DOWNGRADE): operator says "It is not water front but very close to the lake"; entry lakefront.

- 4221 Jackrabbit Mountain (Lake Chatuge): entry lakeview; rec.gov says some sites "lie on the water's edge" - re-audit per site (p3-101, 2026-10-22).
- 14350 Old Fort RV Park: operator "21 Premium lots on Brevard Creek"; entry not waterfront (p3-102).
- 13205 Oyster Point: rec.gov "located on the banks of the Newport River"; entry not waterfront (p3-102).
- 4002 Beaver Lake Park (Alpena Co): county "On the shores of beautiful Beaver Lake"; Campspot sells "Waterfront RV Site" types; entry not waterfront (p3-103).
- 3923 Camp Petosega: county "on the shores of Pickerel Lake"; entry not waterfront (p3-104).
- 3881 Chalk Hills: operator "Riverview - not riverfront"; entry not waterfront - a river view value may apply (p3-104).
- 3983 Caseville County Park: county sells 'Full Hookup Lakefront' sites ($78), seasonal sites 'some are even lake front on Lake Huron'; entry lakeview (p3-109).
- 4049 Hancock Recreation Area: city's BookMySites sells '50 Amp Waterfront' (52-55, 'view of the water right from your own camper') and '30 Amp Waterfront' (47, 49-51) on Portage Lake; entry not waterfront (p3-111).
- 3969 John Gurney Park (Hart): operator 'sits along the East Shore of Hart Lake', 'Overlooking Hart Lake', beach + boat launch; entry not waterfront (p3-112).
- 4016 O.B. Fuller Park (Delta Co): county 'on the shores of Bark River and Lake Michigan', 'a lakeside camping area'; Campspot sells 7 'Lake Front' + 4 'Lake View' sites; entry not waterfront (p3-113).
- 3956 Sandy Beach County Park (Newaygo): county sells 'Full-hookup, Pull-thru, Water View' sites on Hardy Dam Pond; entry not waterfront (p3-114).
- 3982 Stafford County Park (Huron Co): county's best RV sites are "Electric Only Lakeview" ("Lake view sites, electric only" on the map); only rustic sites 3-10 sit on the shore; entry lakefront - may be a downgrade (p3-114/115).
- 407 Silver Lake SP: DNR "sites 1-13 are on Silver Lake", booking site tags 4 sites "Adjacent To: Waterfront"; entry lakeview, which AWH's firsthand note supports (driveway between sites and lake) - likely stays (p3-115).
- 3808 Sunset Cove Resort (Marble Lake): operator sells "Lakefront" full-hookup nightly sites ($50); entry not waterfront (p3-116).
- 3912 Wolverine Campground (Genesee Co): county sells "Lakefront" sites ($52/$57) and advertises "lake-front camping"; entry not waterfront (p3-116).
- 3904 Bay Mills Sunrise RV Park: operator "overlooks the Back Bay of Lake Superior" (Waiska Bay); entry not waterfront (p3-117).
- 14236 Bay Ridge RV Park: operator "sits on over 400' of waterfront" with boat docking; entry bayview (p3-117).
- 3895 Big Lake Campground (Curtis): operator "located right on Big Manistique Lake ... beautiful shallow waterfront" (2013 blog); entry lakeview (p3-117).
- 3894 Log Cabin Resort (Curtis): operator "on Big Manistique Lake", beach, marina, slips, "the oldest log cabin on the waterfront"; campsites' relation to shore unstated; entry not waterfront (p3-121).
- 3862 Loomis Landing: operator "on the Backwaters of Tippy Dam", record walleye "caught right here in front of Loomis Landing"; entry not waterfront (p3-121).
- 3813 Potawatomie Campground (Union City): operator "We are located on Fox Lake", sandy beach, fishing dock; entry not waterfront (p3-123).
- 14257 Rivers Bend RV Resort (Iron Mountain): operator sells "Riverfront water & electric" sites, Firefly "Waterfront Premium" class, site 99 on the river with a dock; entry riverview (p3-123).
- 4024 Runkle Lake Park (Crystal Falls): operator "lakeside camping", beach and pier; entry not waterfront (p3-123).
- 14237 Sunset Bay RV Resort (Ahmeek): operator "Spots along the water go quickly once summer hits"; entry not waterfront on satellite (sites 100-150 m back behind a treeline) (p3-124).
- 3830 Tyler Creek (Alto): operator "set along a beautiful Pure Michigan trout stream", primitive sites along the Tyler Creek Trout Trail; map draws rustic loop 1-27 beside the creek; entry not waterfront (p3-125).
- 14225 Vagabond Resort (Little Bay de Noc): operator advertises Bay De Noc sunsets and a fishing dock; entry not waterfront (p3-125).
- 3963 Vanderbilt County Park: county "located along the Saginaw Bay Shoreline"; entry bayview (p3-125).
- 3831 Walnut Hills: operator "the Shiawassee River runs right alongside the park", kayak launch from the park; entry pond (p3-125).
- 580 Woodland Park (Grand Marais): township's Campspot sells 'Lakefront Campsite' (22) and 'Prime Lakefront Campsite' (5) types; entry lakeview, and the --AWH note says all sites are separated from the lake by a driveway (p3-126).
- 4034 Eddy Park (Wakefield): city's site-dimension sheet types RV lots 4-24 'Lakeside' (Sunday Lake); entry lakeview (p3-126).
- 3959 Big Bend Park (Big Prairie Twp, Hardy Dam Pond): engine sells 13 "Water View Back-in" sites, the other 107 "Standard"; entry lakefront - a view label suggests a downgrade; re-run the gate (p3-127).
- 3937 Pleasant Lake County Park (Jackson Co): county "Positioned on the lake shore" with a sandy swim beach; entry not waterfront (p3-128).
- 14023 Arbutus Lake SFC: DNR "sits along the northwest shore of Arbutus Lake #4"; entry not waterfront (p3-128).
- 3691 Big Bear Point SFC: DNR "sits on the north shore of Big Bear Lake", carry-in access "directly at some campsites"; entry lakeview (p3-130).
- 3725 Black Creek SFC: DNR "on the banks of Black Creek", sites "nestled along Black Creek", 12 sites "accessible from the water"; entry not waterfront (p3-130).
- 3728 Big Eric's Bridge SFC (weak): DNR "located along the Huron River"; entry riverview (p3-130).
- 14025 Bray Creek SFC: DNR "situated along the banks of the Baldwin River", confluence "adjacent to the campground"; entry not waterfront (river reached by stairs from the day-use area) (p3-131).
- 3713 Black River SFC (weak): DNR "quick access to the Black River", carry-in access; entry not waterfront (p3-131).
- 3797 Bob Lake (Ottawa NF) (weak): FS "Many of the sites are situated near the lake"; entry not waterfront (p3-131).
- 3739 Bowman Bridge (weak): rec.gov "situated along the Pere Marquette National Scenic River", but FS puts it "up the hill from Bowman Bridge Boat Landing"; entry not waterfront (p3-131).
- 3751 Brush Lake (Huron-Manistee NF): FS "located on the shores of Brush Lake", carry-in launch in the campground; entry not waterfront (p3-132).
- 3802 Canoe Harbor SFC: DNR "located along the south branch of the Au Sable River", carry-in access in the campground, four sites reachable from the river; entry not waterfront (p3-132).
- 3772 Camp 7 Lake (Hiawatha NF): rec.gov says some sites "are right on the lake"; entry lakeview (p3-132).
- 14215 Camp Deer Trails (Harrison): operator sells "Rustic Lakefront Campsites" and "a half mile of lakefront access"; entry not waterfront. The lakefront type is NOT offered to motorhomes on Campspot, so only the RV-bookable types count. Also check the pin: Campspot's record is 44.084285,-84.748482, ~1 km ESE of the stored 44.08717,-84.76024 (p3-132).
- 3682 Burton's Landing SFC (weak): DNR "riverside campground rests on the banks of the Au Sable River"; entry riverview (p3-132).
- 3788 Burned Dam (Ottawa NF) (weak): FS gives river access on the Middle Branch Ontonagon "from the Burned Dam Campground"; entry not waterfront (p3-132).
- 3770 Carp River (Hiawatha NF) (weak): FS "adjacent to the Carp Wild and Scenic River", stairs down the bank; entry not waterfront (p3-132).
- 14578 CreationView (weak): operator "Waterfront Views ... Nature Lake and Otto's Pond", "Scenic waterfront areas"; CampLife's Water-front amenity is on the cabin type only; entry not waterfront (p3-133).
- 3726 East Branch of Fox River SFC: DNR "located on the East Branch of the Fox River and King's Pond", fishing pier; entry not waterfront (p3-134).
- 3613 Fort Wilkins East Loop: RE-PIN FIRST - the stored 47.4662,-87.8680 is inside the West campground; the East campground is ~0.7 km east (OSM centre 47.4661,-87.8585, own road off US-41). Then: DNR campground map puts sites 1-10 on the Lake Fanny Hooe shore with "STAIRS TO LAKE" and observation decks; entry not waterfront (p3-135).
- 3612 Fort Wilkins West Loop: DNR campground map draws 50-amp pull-throughs 142-158 and sites 161-179 along the Lake Fanny Hooe shore; entry not waterfront (p3-135).
- 3776 Flowing Well (Hiawatha NF): rec.gov + FS "Some sites are situated along the bank, overlooking the slow-moving river"; entry riverview (p3-135).
- 14029 Goose Creek SFC: DNR "sits on the shore of the Upper Manistee River", all nine sites "have a view of the river"; entry not waterfront (p3-136).
- 3997 Grass Lake SFC: DNR "Located on Grass Lake Flooding", ramp + Betsie River carry-in "on site"; entry not waterfront (p3-136).
- 3971 Haymarsh Lake (Mecosta Co): county sells "Rustic Waterfront Camping", campground "perched on the edge of Haymarsh Lake"; entry not waterfront (p3-136).
- 3694 Guernsey Lake SFC: DNR "nestled on Guernsey Lake's north shore"; entry lakeview (p3-136).
- 3660 Glidden Lake SFC: DNR "on Glidden Lake's eastern shore"; entry lakeview (p3-136).
- 14030 High Bridge SFC: DNR "lies along the Two Hearted River", "is located on the Two Hearted River"; entry not waterfront (p3-137).
- 14031 Hopkins Creek SFC: DNR "Nestled along the creek's edge", "located along the Hopkins Creek"; entry not waterfront (p3-137).
- 3696 Lake Ann SFC: DNR "on the peaceful shores of Lake Ann", "located on Lake Ann" (boat launch); entry not waterfront (p3-139).
- 3689 Lake Dubonnet SFC: DNR 50 sites "along the tranquil shores of Lake Dubonnet"; entry lakeview (p3-139).
- 3668 Lake Marjory SFC: DNR "sits on the north shore of Lake Marjory"; entry lakeview (p3-139).
- 3763 Kneff Lake (Huron NF): rec.gov "centered around the 20-acre Kneff Lake"; entry not waterfront (weak, p3-139).
- 3610 Lake Hudson RA: DNR "located near the lake, and some sites have a lake view"; entry not waterfront (weak, p3-139).
- 3651 Leverentz Lake SFC: DNR "sits on the shores of Little and Big Leverentz Lakes"; entry lakeview (p3-140).
- 3686 Little Lake SFC: DNR "situated on the east side of Little Lake", "a small beach area centrally located in the campground"; entry lakeview (p3-140).
- 13456 Log Lake (Kalkaska Co): Campspot sells a "Waterfront Electric Only Site" (site 40), county posts a $45 "Waterfront" rate; entry not waterfront (p3-140).
- 3784 Marion Lake (Ottawa NF): FS "lakeside spurs provide grand views of the south and west shores"; entry not waterfront (p3-141).
- 3629 Metamora-Hadley RA: DNR "The north loop offers some campsites on the water"; entry lakeview (p3-141).
