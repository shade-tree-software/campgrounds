# Campground add-stage research — agent instructions (UTAH)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `star`
[RV Life user rating 0–5; 0 = unrated], `price` [0–4 $ signs], `park_type`,
`rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km]).

The RV ("EKKO") is 23 ft. Decide keep/skip per the inclusion criteria, then for
each KEEP produce a full record. Load `WebFetch` + `WebSearch` via ToolSearch
(`select:WebFetch,WebSearch`) and use them freely. Satellite look (curl GET works):
`curl -s "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=<lng-d>,<lat-d>,<lng+d>,<lat+d>&bboxSR=4326&size=1000,1000&format=jpg&f=image" -o /tmp/r_<id>.jpg`
with d=0.0035, then **Read** the jpg. Keep size ≤ 1000,1000.

## Inclusion criteria (SKIP if it fails)
KEEP only a real, currently-operating, **drive-in RV campground usable by a 23-ft
rig** (at least some drive-in sites fit 23 ft; reachable by a normal vehicle —
decent dirt/gravel OK, hardcore 4WD-only disqualifies; hookups NOT required,
grass/gravel/slickrock pad fine). SKIP (and say why in `skip_reason`) if it is actually:
- cabins-only / yurt-only; tent-only or all walk-in/cart-in/hike-in/boat-in/paddle-in
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping); a trailhead or overlook with no campground
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park (Thousand Trails, Encore, Coast-to-Coast, etc.)
- residential / mobile-home / seasonal-full-timer / workforce park; casino lot
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site (e.g. tiny 18–20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

Utah note: MANY of these are USFS/BLM/NPS back-country campgrounds on gravel or
slickrock roads. A decent maintained gravel/dirt road is fine (drive-in). Only skip
for access if it's genuinely 4WD/high-clearance-required (e.g. some Maze/Needles
backcountry, Lockhart Basin, some La Sal/Henry Mtn spur roads) or the sites are all
tiny tent pads. Small primitive BLM/USFS campgrounds are legitimate keeps if a 23-ft
rig can get in and park — check the recreation.gov "Camping details" / max vehicle
length. Utah has many **dispersed camping areas / rec areas** in the RV Life data;
add a drive-in dispersed area only if it's an established, named, drive-in site (not
a random pin on a road). **Aggregators (snoflo, camperalerts, campscanner,
thedyrt/camping.org summaries) inflate cabin/day-use parks into fake "RV sites" —
never confirm a keep from an aggregator alone.** Authority = the operator/agency
page + the reservation system's actual site list.

### Utah-specific authorities
- **Federal (most of this state):** `recreation.gov` is the workhorse for USFS,
  BLM, NPS, and Reclamation campgrounds. Utah national forests: Uinta-Wasatch-Cache,
  Ashley, Dixie, Fishlake, Manti-La Sal. NPS: Zion (Watchman/South/Lava Point),
  Bryce Canyon (North/Sunset), Capitol Reef (Fruita + primitive Cedar Mesa/Cathedral
  Valley), Arches (Devils Garden), Canyonlands (Squaw Flat/Needles, Willow Flat/Island
  in the Sky), Natural Bridges NM, Hovenweep NM, Cedar Breaks NM (Point Supreme),
  Dinosaur NM (UT side: Green River, Split Mountain). **Glen Canyon NRA** (Bullfrog,
  Halls Crossing, Lone Rock — Lake Powell; NPS land, concessionaire-run, ownership
  `federal`). **Flaming Gorge NRA** (Ashley NF, USFS-operated → `federal`).
  Deep reservation link format: recreation.gov → `/camping/campgrounds/<id>`.
  Set `ownership: "federal"` for all USFS/BLM/NPS/Reclamation.
- **BLM (`park_type: dnr` in Utah — Utah has NO state-DNR campgrounds; `dnr` = BLM):**
  BLM is enormous in Utah. Moab river corridors — Colorado River SR-128 (Goose Island,
  Big Bend, Hittle Bottom, Dewey Bridge, Hal Canyon, Oak Grove, Upper/Lower Drinks
  Canyon, Grandstaff) and Potash Rd SR-279 (Kings Bottom, Williams Bottom, Jaycee Park,
  Gold Bar) — plus Sand Flats Recreation Area, Ken's Lake, Canyon Rims Rec Area
  (Windwhistle, Hatch Point), Little Sahara Rec Area (Oasis, White Sands, Jericho —
  OHV area but developed drive-in campgrounds, keep), Calf Creek Rec Area (within
  Grand Staircase-Escalante NM), Red Cliffs (near Leeds), Simpson Springs (Pony
  Express Trail), Baker Dam, Starr Springs/Lonesome Beaver/McMillan Springs (Henry
  Mtns). Many are reservable on recreation.gov; others FCFS ("First-come,
  first-served" in the note). Grand Staircase-Escalante NM and Bears Ears NM are
  BLM-managed → `federal`. Set `ownership: "federal"`.
- **State parks (Utah State Parks / Div. of State Parks):** official page
  `stateparks.utah.gov/parks/<slug>/`. Reservations run through **ReserveAmerica**
  (`utahstateparks.reserveamerica.com`) — deep link
  `.../campgroundDetails.do?contractCode=UT&parkId=<id>` (verify per-park; Utah has
  been migrating providers, so confirm the live booking link). Set `ownership:
  "state"`. Utah state parks with reservoirs (Sand Hollow, Quail Creek, Jordanelle,
  Deer Creek, Bear Lake, Willard Bay, Yuba, Otter Creek, Scofield, Steinaker, Red
  Fleet, East Canyon, Rockport, Starvation, Millsite, Palisade, Hyrum) are common.
  **Dead Horse Point SP** already has its Kayenta CG in the DB (id 281) — add only the
  **Wingate** campground if distinct, else skip as dup. **Minersville** appears as both
  a "State Park" and county-tagged: Minersville Lake Park is operated by **Beaver
  County** → `ownership: "local"` (verify).
- **Local:** county/city parks, water-conservancy or recreation districts
  (`ownership: "local"`). Confirm the operator is genuinely local government. County
  land run by a private concessionaire is still `local`.
- **Private (commercial):** already gated to affordable/well-rated; still vet each —
  real transient RV park, not membership/seasonal/residential. Utah has many
  "RV resort" parks near the parks (Moab, St George, Kanab, Bryce); keep if drive-in
  transient RV and it clears the inclusion criteria.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park office/entrance/trailhead. Verify on satellite + the agency campground-map/PDF or
  recreation.gov photos. RV Life coords are often off by km; move onto the loop.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — per the authorities above (federal / state / local / private).
- **`website`** — official park/forest page first, then the deep reservation link
  (newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office/ranger-district number if on the official page; else "".
  Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (loops/site count, hookup level, max RV length if notable, FCFS vs reservable) and
  append ` RV Life <star>*/<price as $ signs> (auto 7/2026). --Claude`. If FCFS with no
  booking channel, say "First-come, first-served." Do NOT copy aggregator boilerplate.
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `recreation.gov Devils Garden CG (Arches NP): 51 drive-in sites, RVs to 40 ft,
  reservable -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or rec.gov/ReserveAmerica url>",
    "water_body": "<named lake/river/reservoir or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.

## Output
Do NOT edit any repo files. Final message = ONLY a JSON array (no prose, no fences),
one object per candidate, SAME order as the batch:
```
{"decision":"add"|"skip","skip_reason":"<if skip>","name":"...","location":"lat,lng",
 "elevation_meters":<num>,"ownership":"federal","website":"...","phone":"...","note":"...",
 "inclusion_evidence":"...","waterfront":"not waterfront",
 "lead":{"map_url":"...","water_body":"...","candidate_sites":"...","note":"..."}}
```
For `skip`, only `decision`, `skip_reason`, and `name` are required. Be thorough but
return strictly valid JSON.
