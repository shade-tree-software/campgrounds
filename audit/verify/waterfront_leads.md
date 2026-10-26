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

## Resolved 2026-10-26, West Virginia wf-wv-3 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence) - WV leads done

- Downgraded: **747 Momma Tried RV & Camping** riverfront -> not waterfront (Hipcamp's own pins put all 38 RV
  sites 100-140 m from the North Fork behind a treeline; only the 2 tent sites on 'The Island' are riverside;
  the stored riverfront contradicted --AWH 'Sites are not waterfront').
- Stand: **13367 Kennedy Park & Marina** riverview (RV rows behind the campground road; the riverside row is ~20-30
  m back across lawn and a riprap climb-down; the 'Primitive Riverfront Sites' are unplaced).

## Resolved 2026-10-26, West Virginia wf-wv-2 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Downgraded: **503 Big Rock (Monongahela NF)** riverfront -> not waterfront (rec.gov site coords: spurs north of
  FR 76, ~45-50 m from the Cranberry with the road and a wooded bank between; the stored riverfront contradicted
  --AWH 'across the road, sites are not waterfront').
- Stand: **428 Brooklyn Heights Riverfront** riverview (the dead-end road runs between the RV pads and the river);
  **232 Bluestone SP** (bench ~19 m above a slough; low confidence), **13120 Eagle's Nest**, **1201 Blue Heron
  Landing** (creek-side spots are tent sites and cabins), **457 Gauley Tailwaters** (below the dam), **456 Glade
  Creek** (canopy, no per-site source; low confidence), **463 Horseshoe** (creek meadow is day use) - not
  waterfront.
- Source: WV leaf-off imagery (services.wvgis.wvu.edu, wv_imagery_WVGISTC_leaf_off_mosaic) sees under canopy.

## Resolved 2026-10-26, West Virginia wf-wv-1 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **1227 East Fork (Monongahela NF)** riverview -> riverfront (CampLife 'River Front' RV back-ins 2-15,
  pads within ~20 m of the East Fork across open grass; re-pinned ~240 m off the Durbin rail depot).
- Downgraded: **83 Stuart RA** riverview -> not waterfront (rec.gov site coords put all 26 sites in the woods
  150-200 m from Shavers Fork; the earlier call read the day-use pavilion field).
- Stand: **266 Big Bend** and **490 Watoga - Riverside** riverfront on --AWH firsthand (the verifier proposed
  riverview at low confidence; asked in asks.md); **426 Riverside Cabins & RV** riverview (--AWH; RVs set back
  behind cabins); **1192 Great Bend** riverfront; **263 Summersville Lake Retreat** (lake ~750 m off, 100 m
  below), **498 Army Camp Rd** (--AWH) - not waterfront.

## Resolved 2026-10-26, New York wf-ny-3 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence) - NY leads done

- Upgraded: **13727 Rogers Rock** not waterfront -> lakefront (DEC map + RA photos: drive-in site 004, 30-ft RV,
  on open grass ~10 m from Lake George; most other shore sites are tent-only or across the road); **14320 Pine
  Ridge Park** riverview -> riverfront (operator map and rate sheet: 'Waterfront' RV sites along the Salmon
  River bank, open meadow to the water on 2024 0.3 m ortho); **13728 Luzerne** not waterfront -> lakeview (DEC
  map: drive-in sites 81/113/114/116 on Fourth Lake, but lidar shows a 10-15 m bank; RA photos show the lake
  below through trees).
- Stand: **14339 Niagara Shores** lakeview (RVs on the Lake Ontario bluff top); **13359 Korn's Campground** not
  waterfront (the Shawangunk Kill is in a wooded ravine 80-150 m off; ownership question in criteria_followups).

## Resolved 2026-10-26, New York wf-ny-2 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- No value changes. Stand: **21 North-South Lake** lakefront (--AWH; NE-shore pads ~12-16 m from the water);
  **1481 Brookside Beach** lakeview (RV rows atop a ~20 m shale bluff between Rt 5 and Lake Erie; re-pinned off
  the pond field; note corrected - the beach is below the bluff, not across Rt 5); **1460 North Bay** lakeview
  (the shore camp lane between); **1395 Taughannock Falls SP**, **1511 Massena International** (unnamed
  'WATERFRONT' sites; NE-edge pads ~60-70 m back across a reed meadow; low confidence), **1416 Paradox Lake**
  (nearest sites ~50+ m back; the note's '~5 waterfront sites' removed), **15466 Lake Placid KOA** (Riverside
  section ~75-85 m from the Ausable behind pines and houses), **1453 Cedar Point County Park** (re-pinned off a
  residential street onto the loops) - not waterfront.

## Resolved 2026-10-26, New York wf-ny-1 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **1516 Royal Mountain Campsites** not waterfront -> pond (ResNexus map: sites 16, 17 and the lettered
  sites between the north driveway and the pond; a trailer ~15 m from the pond across open unused lawn);
  **1505 Birch Haven** not waterfront -> riverview (front-row trailers ~40-45 m from the St. Lawrence behind a
  wooded climb-down bank; re-pinned off Rt 12E onto the park; low confidence); **1518 Rancho Pines** not
  waterfront -> riverview (Campspot draws the RV cluster beside the Schroon; one RV ~17-20 m from the water under
  canopy - the verifier's riverfront rested on a hand-scaled drawn map, held down).
- Stand: **335 Cedar Point SP** riverview (RA's 'Waterfront' tag is distance-only - sites 006-020 sit inside the
  loop across the shore drive; low confidence); **1442 Myers Park** riverfront (Salmon Creek, ~30-35 m wide);
  **1409 Limekiln Lake** lakefront; **1407 Frontier Town**, **334 Oneida Shores Park** (waterfront sites are
  tent-only) - not waterfront.

## Resolved 2026-10-26, Florida wf-fl-4 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence) - FL leads done

- Upgraded: **14870 Seminole Campground** not waterfront -> creekside (a 2021 canopy-gap frame shows west-loop RV
  pads ~5-10 m from Popash Creek, no road between; some may be park models); **14387 Panhandle RV Resort** not
  waterfront -> lakeview (west-loop pads ~20 m from the fishing pond across the loop road; the 1163 precedent).
- Stand: **168 River Junction (Withlacoochee SF)** not waterfront (--AWH; RA 'Riverfront' sites plot 30-55 m
  across wooded swamp; re-pinned ~200 m off the access road); **14434 Scott's Ferry** not waterfront (road and
  bank treeline between the RV sites and the Chipola).

## Resolved 2026-10-26, Florida wf-fl-3 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **4719 Karick Lake South (Blackwater River SF)** lakeview -> lakefront (ReserveAmerica 'Lakefront' on
  RV sites 1-13 odd; GIS of 5/7/9 ~16-22 m from shore under open-understory pines); **4728 Okaloacoochee Slough
  SF - Panther Pond** not waterfront -> pond (RV site 016, a 50-ft back-in, on an open apron ~20-25 m from the
  pond; the other 15 sites are woods); **4734 Wright Lake (Apalachicola NF)** not waterfront -> lakeview (rec.gov
  tags 15/17/18 'Lakefront' but they plot ~45-90 m back behind a tree band; low confidence).
- Downgraded: **633 Little Talbot Island SP** coastal woods -> not waterfront (A1A runs between the campground and
  the ocean; pads 40-110 m from Myrtle Creek marsh in hammock; matches --AWH 'campground is not waterfront';
  re-pinned off the beach day-use lot).
- Stand: **165 Silver Lake (Withlacoochee SF)** lakeview (--AWH partial view; sites 13/15/16 'View: Lake' ~45-55 m
  back); **14398 Sunny Shores** (a dead-end ditch, rows behind road and buildings), **14385 Wewa RV Park**
  (cypress fringe), **4823 Newport Park** (re-pinned ~150 m onto the loop; river deck reached by walkways) - not
  waterfront.

## Resolved 2026-10-26, Florida wf-fl-2 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **4770 Sportsman's Cove Resort** not waterfront -> lakefront (occupied RV sites ~5-10 m from the
  resort's boat canal into Orange Lake; operator sells 'Waterside' RV sites; the 14625 canal precedent);
  **158 Oscar Scherer SP** not waterfront -> creekside (Reserve Florida: RV sites 1-17 and 70-90 'adjacent to a
  creek'; GIS points ~20-35 m from South Creek under bank canopy).
- Stand: **743 Wickham Park** pond (bears out --AWH 'several sites are on small ponds'); **153 Rainbow Springs
  SP** (every site 280 m+ from the river), **14391 RV Village at Lake Panasoffkee** (ramp/cabin strip between),
  **4740 Ocean Pond (Osceola NF)** (cypress fringe + marsh), **14383 Pine Lake RV Park**, **15421 St. Petersburg
  / Madeira Beach KOA** (continuous mangrove belt; kayak cuts don't make on-water) - not waterfront.

## Resolved 2026-10-26, Florida wf-fl-1 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **4837 John Prince Park** lakeview -> lakefront (east-edge RV pads ~10-17 m from Lake Osborne across
  open grass; re-pinned ~400 m off the causeway); **4813 Coe Landing County Park** lakeview -> lakefront (Leon
  Co. per-site map flags sites 7, 9, 11, 13, 15, 16 Waterfront at the Lake Talquin shore; cypress shadow hides
  the shore; low confidence); **4715 Bear Lake (Blackwater River SF)** not waterfront -> lakeview (ReserveAmerica
  'Lakefront' on 11 RV sites, but the pads sit 63-83 m from the water in open pine); **170 Mutual Mine** not
  waterfront -> lakeview (site 1 'Type of View: Lake', ~40 m behind trees); **4841 Turtle Beach** not
  waterfront -> coastal woods (west-end pads ~40 m behind shore hammock + a ~20 m foredune, footpath to the
  Gulf, no lot between - the old 'beach-parking complex' reading was wrong; low confidence).
- Stand: **587 Cypress Glen** not waterfront (--AWH firsthand; its one lake-view site asked in asks.md);
  **393 St. Joseph Peninsula - Shady Pines** coastal dunes; **15417 Naples/Marco Island KOA** not waterfront
  (the creek lane is cabins, tents and boat parking).
- Tool: the verifier's FFS ReserveAmerica per-site fetcher (plain HTTP, GIS lat/lng per site) is copied to
  audit/verify/kit/ra_sites.py.

## Resolved 2026-10-26, Michigan wf-mi-15 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence) - MI done but 3900 (held)

- Upgraded: **3630 Yankee Springs - Gun Lake Modern** not waterfront -> lakefront (channel-row RVs ~10-15 m from
  Gun Lake across open grass, boats at the bank; midnrreservations tags that row Waterfront; re-pinned ~400 m
  out of the forest); **3618 Wilson SP** not waterfront -> lakeview (DNR map: sites 1-14 and 122-135 front Budd
  Lake with steps down; pads atop a ~10 m wooded bank; low confidence); **3631 Yankee Springs - Deep Lake
  Rustic** not waterfront -> lakeview (re-audited at the corrected pin; DNR per-site text 'view of the lake' on
  D46-49, D51-52, D69-72; loop ~45 m back on a 13 m bluff; low confidence).
- Stand: **3735 Weber Lake** lakeview (re-pinned ~130 m); **3654 Veterans Memorial** (re-pinned off the US-31
  bridge), **3639 W.J. Hayes SP** (re-pinned ~550 m off the day-use lot; loops ~250 m from Round Lake), **3765
  Wagner Lake** (pine band at the high-water edge; low confidence), **3608 Waterloo - Portage Lake** (DNR site
  text: 'lake is not visible') - not waterfront.

## Resolved 2026-10-26, Michigan wf-mi-14 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Stand: **3675 Trout Lake SFC** lakefront (pads ~10-22 m from the pre-drawdown shore; low confidence - the lake
  is drawn down and dam removal is recommended, see criteria_followups.md); **3722 Van Etten Lake** (re-pinned
  ~200 m off private lakefront homes) and **3657 Twin Lakes** lakeview; **14041 Tippy Dam RA** (bluff),
  **3720 Tomahawk Lake**, **3669 Upper Manistee River** (re-pinned ~350 m off the entrance road), **3721 Tomahawk
  Creek Flooding** (re-pinned ~800 m onto the east unit), **13449 Trailway** - not waterfront.

## Resolved 2026-10-26, Michigan wf-mi-13 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **4014 Shakey Lakes Park** lakeview -> lakefront (county per-site booking pages flag 'Water Frontage'
  on transient RV sites 59, 65, 66, 69-75 and P3/P4/P7-P10; imagery: peninsula-tip loop ~10-15 m from shore).
- Stand: **3678 Shupac Lake**, **3702 Silver Creek** (riverview; the river-side sites are walk-ins), **14100
  Ski-Kwe zaag'igan Lake** (re-pinned ~110 m onto the OSM pitch cluster), **3707 South Gemini Lake** (one
  clearing ~15 m from the water, not resolvable as an RV pad; low confidence), **3673 South Manistique Lake** -
  lakeview/riverview; **3719 Shoepac Lake** (pads 80-130 m back), **14036 Sunrise Lake** (lake across the road,
  on a bluff) - not waterfront.

## Resolved 2026-10-26, Michigan wf-mi-12 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **13450 Riverside Park Campground (Evart)** not waterfront -> riverfront (city per-site map: River
  Sites 4-8 on the Muskegon bank, ~20-30 m across open grass; re-pinned 150 m off the playfield); **14044 Rifle
  River RA - Ranch Rustic** not waterfront -> creekside (sites 150/152/153 ~20-30 m from the ~15 m Rifle across
  grass; midnrreservations tags 152-153 'Adjacent To: River').
- Downgraded: **3706 Ross Lake SFC** lakeview -> not waterfront (DNR: no direct lake views, steep footpaths down).
- Stand: **3731 Round Lake SFC** lakeview (canopy, loop not located; low confidence; pin left - the GNIS/OSM node
  is 120 m S, unconfirmed); **13459 Riverside RV Park (Vassar)**, **14043 Rifle River - Spruce Rustic**, **3747
  Sand Lake RA**, **14035 Schecks Place SFC** - not waterfront.
- Tip for later MI batches: midnrreservations.com/api/resourcelocation/resources?resourceLocationId=<id> returns a
  per-site 'Adjacent To' attribute (a booking tag - supporting evidence only).

## Resolved 2026-10-26, Michigan wf-mi-11 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3714 Pretty Lake SFC** lakeview -> lakefront (drive-in pads on the NE shore ~5-20 m from the water,
  a trailer on one in NAIP, <1 m above the lake); **3730 Pigeon River SFC** riverview -> creekside (a pad at the
  bend ~10-15 m from the bank, ~1.3 m above the water; the Pigeon is ~7-9 m wide, under the riverfront bar).
- Downgraded: **3737 Pine Grove SFC** riverview -> not waterfront (main clearing on a terrace ~5 m up, ~30 m back
  behind a conifer belt; low confidence).
- Stand: **3736 Pickerel Lake (Otsego) SFC**, **14033 Pigeon Bridge SFC**, **3742 Pine Lake (Huron-Manistee NF)**
  (loop's east end ~10-20 m from shore, pads canopy-hidden; low confidence), **3653 Platte River SFC**, **14034
  Rainbow Bend SFC** (re-pinned onto the drive-in loop; the riverbank clearing is the canoe group area) - not
  waterfront.

## Resolved 2026-10-26, Michigan wf-mi-10 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3794 Perch Lake (Ottawa NF)** not waterfront -> lakefront (rec.gov per-site 'Lakefront' on 9 of 20
  drive-in RV sites; plotted, 11/12/15/16/17 sit 3-16 m from shore, site 16 ~1 m above the lake on 3DEP).
- Stand: **14245 Northern Sites** riverview (RVs ~25-40 m back with the campground lane between; low
  confidence); **3718 Perch Lake SFC** lakeview (pads on an 8-12 m bank, stairs down); **3644 North Higgins Lake
  SP** (private shore strip / forest), **3744 Old Grade** (canopy, no site map; low confidence), **3738 Nichols
  Lake South** (rec.gov 'Lakefront' tag is blanket - on interior #20 too; pads 65-100 m back on a bench),
  **3745 Peterson Bridge** (Riverfront tags only on tent-only boat-in sites), **3778 Petes Lake** (re-pinned
  ~450 m off the access road; canopy, low confidence) - not waterfront.

## Resolved 2026-10-26, Michigan wf-mi-9 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3629 Metamora-Hadley RA** lakeview -> lakefront (DNR map: north-loop sites ~151-169 on the lake
  side of the loop road; RVs ~15-20 m from Lake Minnawanna across open lawn); **13456 Log Lake** not waterfront
  -> lakefront (county + Campspot maps: site 40, the 'Waterfront Electric Only Site', ~30-35 m across the park's
  own sand beach - the Fuller precedent; low confidence, lakeview if a swim beach is read as a used strip);
  **3784 Marion Lake** not waterfront -> lakeview (lakeside spurs ~20-45 m above the lake behind a conifer belt;
  FS 'lakeside spurs give views'); **3717 Natalie SFC** stays lakeview (the verifier's lakefront rested on one
  2014 leaf-off frame with no site map - held down).
- Downgraded: **3708 Ocqueoc Falls SFC** riverview -> not waterfront (pads ~25-32 m behind a continuous conifer
  belt, no sightline; low confidence).
- Stand: **3743 Minnie Pond** (sites not located; low confidence), **3769 Monocle Lake** (rec.gov sites ~70-80 m
  behind forest), **3636 Newaygo SP** (re-pinned ~480 m onto the Oak loop; atop a 20-ft embankment) - not
  waterfront.

## Resolved 2026-10-26, Michigan wf-mi-8 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3610 Lake Hudson RA** not waterfront -> lakeview (north-point sites 37/38 and the east-loop north
  spurs ~25-30 m from the lake through a continuous wooded shore band; DNR 'some sites have a lake view').
- Stand: **3689 Lake Dubonnet**, **3668 Lake Marjory** (on the SOUTH shore, not the north as DNR says),
  **3651 Leverentz Lake** (re-pinned off the access road onto the campground road), **3686 Little Lake** (one
  sandy clearing ~17-25 m from the water, no vehicle in any frame and no site map) - lakeview; **14031 Hopkins
  Creek**, **3696 Lake Ann** (~25-30 m bluff), **3763 Kneff Lake** (rec.gov sites ~50-60 m back, ~25 m up) - not
  waterfront. Hopkins Creek, Lake Ann, Dubonnet, Leverentz and Little Lake are low-confidence canopy calls.

## Resolved 2026-10-26, Michigan wf-mi-7 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3612 Fort Wilkins - West Loop** not waterfront -> lakeview (DNR map: the loop road runs between
  every lakeside site and Lake Fanny Hooe; pads ~10-25 m back, ~5 m above the lake); **14029 Goose Creek SFC**
  not waterfront -> riverview (old pin and evidence were the equestrian Trail Camp's loop; re-pinned to the
  DNR's point on the river road; DNR "all nine sites have a view of the river"; pads canopy-blind, low
  confidence).
- Stand: **3776 Flowing Well** riverview (rec.gov pads ~27-36 m back under canopy); **3694 Guernsey Lake** and
  **3660 Glidden Lake** (re-pinned off the entrance) lakeview (canopy-blind, low-confidence keeps); **3997 Grass
  Lake SFC** and **14030 High Bridge SFC** not waterfront; **3971 Haymarsh Lake** not waterfront (re-pinned off
  the entrance; the verifier's lakeview rested on a hand-drawn map over a cattail marsh, canopy-blind - held
  down).

## Resolved 2026-10-26, Michigan wf-mi-6 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3613 Fort Wilkins - East Loop** not waterfront -> lakeview (re-pinned out of the West campground
  onto the East loop; sites 1-10 ~20-25 m from Lake Fanny Hooe but ~7 m up a climb-down bank with stairs).
- Downgraded: **3682 Burton's Landing SFC** riverview -> not waterfront (campers on the camp road ~100-110 m
  behind a continuous forest band; re-pinned off the canoe landing).
- Stand: **3772 Camp 7 Lake** lakeview (rec.gov 'Lakefront' sites 022-031 sit ~55 m back up a forested slope;
  re-pinned off the day-use beach); **14215 Camp Deer Trails** (the 'Rustic waterfront' sites are not sold to
  motorhomes), **3788 Burned Dam**, **3770 Carp River** (climb-down ravine), **14578 CreationView** (pond lawn
  holds no pads), **3726 East Branch Fox River** (canopy, no site map; low confidence) - not waterfront.

## Resolved 2026-10-26, Michigan wf-mi-5 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3725 Black Creek SFC** not waterfront -> riverview (re-pinned out of the trailer park onto the
  loops; pad clearings ~30-40 m from Black Creek over an open bank ~15 m above the water; low confidence);
  **3751 Brush Lake (Huron-Manistee NF)** not waterfront -> lakeview (open grass ~25 m to a marsh fringe, water
  ~45 m; the verifier proposed lakefront at low confidence, held at the view by default-down).
- Stand: **3728 Big Eric's Bridge SFC** riverview (pitches 66-75 m back); **14025 Bray Creek SFC**, **3713 Black
  River SFC** (re-pinned onto the loop), **3797 Bob Lake** (canopy, no per-site map; low confidence), **3739
  Bowman Bridge** (re-pinned onto the rec.gov site coords; ~90 m, up the hill), **3802 Canoe Harbor** (river
  sites are walk-in only) - not waterfront.

## Resolved 2026-10-26, Michigan wf-mi-4 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **4034 Eddy Park** lakeview -> lakefront (city site-dimension PDF types lots 4-24 'Lakeside'; RVs
  ~10-20 m from Sunday Lake across open grass); **3831 Walnut Hills Family Campground** pond -> riverfront
  (river-side row ~7-13 m from the Shiawassee through a thin open fringe; nightly vs seasonal unknown).
- Downgraded: **3959 Big Bend Park** lakefront -> lakeview (re-pinned off a pine plantation ~600 m N onto the
  SE point; every RV site inside the perimeter road, units ~25-50 m back on a high bank; 13 'Water View' sites).
- Stand: **3963 Vanderbilt County Park** bayview (low confidence: ~120-160 m from a marsh arm across a brushy
  slope); **580 Woodland Park** lakeview (--AWH: a driveway separates every site); **3937 Pleasant Lake County
  Park** not waterfront (private lake-house strip between); **14023 Arbutus Lake SFC** not waterfront
  (re-pinned from the entrance onto the loop; trailer pads not resolvable, lakeshore sites tent-only; low
  confidence); **3691 Big Bear Point SFC** lakeview (pads not legible under pines).

## Resolved 2026-10-26, Michigan wf-mi-3 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **14257 Rivers Bend RV Resort** riverview -> riverfront (re-pinned off the mobile-home rows onto the
  RV peninsula; pads with docks ~10-20 m from the Menominee; transient Riverfront W&E sold); **14237 Sunset Bay
  RV Resort** not waterfront -> coastal woods (RV clearings in open shore spruce ~35-65 m from Lake Superior,
  only the campground's own lanes between; the prior 100-150 m call was contradicted at 0.22 m/px).
- Stand: **3894 Log Cabin Resort** (RVs behind the cabin row), **3862 Loomis Landing** (canopy, no per-site
  source; low confidence), **3813 Potawatomie** (lake frontage is day use), **4024 Runkle Lake Park** (site 44
  ~45 m behind the loop road), **3830 Tyler Creek** (creek-side loop is primitive sites), **14225 Vagabond
  Resort** (bay ~300 m across County 513) - all not waterfront.

## Resolved 2026-10-26, Michigan wf-mi-2 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **3808 Sunset Cove Resort** not waterfront -> lakefront (operator lot map: cove-frontage lots within
  ~10 m of Marble Lake; nightly 'Lakefront' sites sold); **3912 Wolverine Campground** not waterfront ->
  lakefront (Genesee Co site map: Lakefront sites 1-21 and 127-155 ~10-15 m from Holloway Reservoir; re-pinned
  off the day-use beach ~450 m; those sites carry a 3-night minimum, the rest don't); **3895 Big Lake
  Campground** lakeview -> lakefront (RVs ~15 m from the beach across open unused lawn); **3956 Sandy Beach
  County Park** not waterfront -> lakeview (Water View pads ~15-20 m back behind a lane and brush on a 5 m bank).
- Downgraded: **3982 Stafford County Park** lakefront -> lakeview (the shore sites 3-10 are tent-only on
  Checkfront; the Lake View electric sites sit behind the pavilion lawn).
- Stand: **407 Silver Lake SP** lakeview (--AWH: driveway between sites and lake); **3904 Bay Mills Sunrise RV
  Park** not waterfront (150-250 m back behind road and casino); **14236 Bay Ridge** bayview (pads 40-60 m up a
  brushy bluff).

## Resolved 2026-10-25, Michigan wf-mi-1 (audit/apply_waterfront_audit.py; evidence in waterfront_evidence)

- Upgraded: **4002 Beaver Lake Park** not waterfront -> lakefront (county campground map: sites 1-4, 57-58 front
  the lake; RVs ~25 m from shore across open lawn; re-pinned off the woods ~150 m SE); **4049 Hancock Recreation
  Area** not waterfront -> lakefront (pads ~12-17 m from Portage Lake behind a thin brush fringe, the city's
  waterfront sites 47, 49-55); **4016 O.B. Fuller Park** not waterfront -> lakefront (re-pinned off the M-35
  bridge onto the loop ~700 m SSE; pads ~20-30 m from Lake Michigan across open grass and the park's own beach).
- Stand: **3923 Camp Petosega** not waterfront (pads ~190 m back behind forest, road and the day-use beach);
  **3881 Chalk Hills** not waterfront (re-pinned onto the OSM campground polygon; ~100 m and 26 m above the
  flowage behind forest); **3983 Caseville County Park** lakeview (rows ~150-200 m from the bay behind the public
  beach); **3969 John Gurney Park** not waterfront (~55 m behind a continuous wooded bank).
- Held: **3900 Bond Falls Consolidated** (see its open lead).

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

- **3900 Bond Falls Consolidated (MI)** — dam screen 2026-10-21: the pin sits in the woods just **HELD wf-mi-1 (2026-10-25): two UPPCo areas ~4 km apart (West at the dam, East dispersed ~46.4067,-89.0865) - split question; West pads not legible under canopy; results in audit/verify/waterfront/wf-mi-1_held_3900.json.**
  below Bond Falls Main Dam (10 m under the flowage's pool), not at a campground; the camp loops
  are along the flowage shore somewhere south. Find the loops (UPPCo map) and re-pin before the
  lakefront call can be re-checked.
- **3532 Totogatic Park (WI)** — dam screen 2026-10-21: pin is in woods ~250 m from the Minong
  Flowage, 15 m above it; OSM's campground node is 46.14171,-91.93697. Re-pin onto the loops.
- **4353 Briarcliffe RV Resort (SC)**: operator "located on the Intracoastal Waterway", pool "overlooking the Intracoastal Waterway"; entry not waterfront (sites may be set back; check imagery).
- **15491 Myrtle Beach KOA (SC)**: KOA's booking form sells a back-in full-hookup type with "your private deck overlooking the water"; two tidal lakes connect to the Atlantic via Withers Swash; a 2026-10-15 review "patio site with a deck on the water". Entry not waterfront (2026-10-19 audit saw only an owners' waterfront type).
- **15454 Asheville East KOA (NC)**: KOA "Riverfront camping", sells "Riverside" back-in/pull-through types "parallel to the serene Swannanoa River" (B28, B29; reviewers name A1-A10); entry not waterfront.
- **4275 At The Ridge (NC)**: "Premium sites are on the river"; ResNexus River Campsites #4 and #6 full hookup "on the river" (North Fork French Broad); entry riverview.
- **4317 Cashie River Treehouses (NC)**: town's Campspot listing tags "Waterfront" and "Beach - Public Access" (on the Cashie River); entry not waterfront.
- **4326 Mayo Lake Park (NC)** (strong): former county RV page "on-water RV and tent sites" (1-28); county map shows Area 2 lining the shore; entry not waterfront.
- **245 Lake Powhatan (NC)**: FS + rec.gov "on the banks of Lake Powhatan", loops "within walking distance of the lake"; entry not waterfront (note says not on the lake).
- **32 Linville Falls (NC)** (weak): rec.gov "Linville River ... winds beside the campground"; entry not waterfront.
- Kerr Lake / Jordan Lake (NC: 104/106/108/146) ReserveAmerica "Near Water - no" on every site - a blanket attribute, ignore.
- **4306 Almond Boat & RV Park (NC)** (DOWNGRADE): operator says "It is not water front but very close to the lake"; entry lakefront.

- 4221 Jackrabbit Mountain (Lake Chatuge): entry lakeview; rec.gov says some sites "lie on the water's edge" - re-audit per site (p3-101, 2026-10-22).
- 14350 Old Fort RV Park: operator "21 Premium lots on Brevard Creek"; entry not waterfront (p3-102).
- 13205 Oyster Point: rec.gov "located on the banks of the Newport River"; entry not waterfront (p3-102).
