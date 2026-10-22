# Waterfront re-audit leads from phase 7

A verifier's source (operator page or booking engine) claims water access that differs from
the stored `waterfront`. Per the curation doc's rule #7 that triggers the gate, both ways; a
booking-engine tag alone decides nothing. Work these with the full waterfront procedure.

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
