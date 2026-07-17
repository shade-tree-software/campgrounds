# Campground add-stage research — agent instructions (NEVADA)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `star`
[RV Life user rating 0–5; 0 = unrated], `price` [0–4 $ signs], `park_type`,
`rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km], sometimes `former_name`,
`site_count`).

The RV ("EKKO") is 23 ft. Decide keep/skip per the inclusion criteria, then for
each KEEP produce a full record. Load `WebFetch` + `WebSearch` via ToolSearch
(`select:WebFetch,WebSearch`) and use them freely. Satellite look (curl GET works):
`curl -s "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=<lng-d>,<lat-d>,<lng+d>,<lat+d>&bboxSR=4326&size=1000,1000&format=jpg&f=image" -o /tmp/r_<id>.jpg`
with d=0.0035, then **Read** the jpg. Keep size ≤ 1000,1000.

## Inclusion criteria (SKIP if it fails)
KEEP only a real, currently-operating, **drive-in RV campground usable by a 23-ft
rig** (at least some drive-in sites fit 23 ft; reachable by a normal vehicle —
decent dirt/gravel OK, hardcore 4WD-only disqualifies; hookups NOT required,
grass/gravel/paved pad fine). SKIP (and say why in `skip_reason`) if it is actually:
- cabins-only / yurt-only; tent-only or all walk-in/cart-in/hike-in/boat-in/paddle-in
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping); a trailhead or overlook with no campground
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park (Thousand Trails, Encore, Coast-to-Coast, etc.)
- residential / mobile-home / seasonal-full-timer / workforce park; **casino/racetrack
  overnight lot** (a real casino-adjacent RV *park* with defined sites + amenities may be
  borderline — vet it as a transient RV park; a bare overnight parking lot is a SKIP)
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site (e.g. tiny 16–20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

Nevada note: this is a mostly-empty, arid, federal-land state (~63% BLM, plus the vast
Humboldt-Toiyabe NF). MANY candidates are BLM / USFS / NPS campgrounds on gravel or
desert/forest roads — a decent maintained gravel/dirt road is fine (drive-in). Only skip
for access if it's genuinely 4WD/high-clearance-required or the sites are all tiny tent
pads. Some sites are **boat-in only** (a few Lake Mead/Lake Mohave coves) — SKIP those.
Nevada also has a heavy concentration of **snowbird / 55+ / long-term residential RV
resorts** around Las Vegas, Pahrump, Laughlin, Mesquite, and Reno — vet the private
bucket hard for genuinely-transient operation. **Aggregators (snoflo, camperalerts,
campscanner, thedyrt/camping.org summaries) inflate cabin/day-use parks into fake "RV
sites" — never confirm a keep from an aggregator alone.** Authority = the operator/agency
page + the reservation system's actual site list.

### Nevada-specific authorities & ownership
- **State parks (Nevada Division of State Parks):** `parks.nv.gov`. Reservations run through
  the state portal **reservenevada.gov** (some parks are FCFS). Big camping state parks:
  Valley of Fire, Cathedral Gorge, Echo Canyon, Spring Valley, Cave Lake, Ward Charcoal
  Ovens, Berlin-Ichthyosaur, Wild Horse, South Fork, Rye Patch, Lahontan, Washoe Lake,
  Fort Churchill, Kershaw-Ryan, Beaver Dam, Big Bend of the Colorado, Dayton, Sand Harbor/
  Lake Tahoe NSRA (mostly day-use — verify overnight). Set `ownership: "state"`. NOTE: Rye
  Patch & Lahontan sit on Reclamation dams but are STATE-park-operated → `state` (credit the
  operator, not the dam owner).
- **BLM (FEDERAL) — this is what `park_type: dnr` USUALLY means in Nevada.** Nevada is ~63%
  BLM; most BLM camping is dispersed/primitive but there are developed campgrounds: Red Rock
  Canyon NCA (Red Rock CG), Sloan Canyon, Fort Sage, some along the Colorado/Truckee, and
  various district sites. `blm.gov/visit/<slug>`; a few reservable on recreation.gov, many
  FCFS. Set `ownership: "federal"`. **VERIFY the operator per entry** — a `dnr`-tagged site
  that turns out to be a Nevada Division of State Parks or NDOW (Nevada Dept. of Wildlife)
  area is `state`; a county-run site is `local`.
- **NDOW (Nevada Dept. of Wildlife) WMAs / fishing accesses = STATE** (`ndow.org`) — a few
  offer drive-in camping (e.g. reservoirs/WMAs). `park_type: dnr` occasionally means this,
  not BLM — verify. Set `ownership: "state"`.
- **USFS (federal, `park_type: usfs`/`national`):** the **Humboldt-Toiyabe NF** is the
  largest NF in the lower 48 and blankets Nevada's mountain ranges — Ruby Mountains (Angel
  Lake, Angel Creek, Thomas Canyon), Jarbidge, Santa Rosa (Lye Creek), Spring Mountains /
  Mount Charleston (Kyle Canyon: Fletcher View, Hilltop; Lee Canyon: McWilliams, Dolomite),
  Ely district (Ward Mountain, Berry Creek, Cave Lake area), and the Lake Tahoe Basin
  (Nevada side: Nevada Beach). Most drive-in campgrounds are on recreation.gov (deep link →
  `/camping/campgrounds/<id>`); some FCFS. Set `ownership: "federal"`. Watch the under-23-ft
  skip rate — many small high-elevation range sites cap at 16–22 ft.
- **NPS (federal, `park_type: national`):** **Great Basin NP** (Lower Lehman, Upper Lehman,
  Wheeler Peak [check RV length — often too small], Baker Creek, Grey Cliffs); **Lake Mead
  NRA** (Boulder Beach, Las Vegas Bay, Callville Bay, Echo Bay, Cottonwood Cove — Lake
  Mohave; Katherine Landing is AZ); **Death Valley NP** (Nevada has only a sliver — most
  campgrounds are CA-side). Set `ownership: "federal"`.
- **USFWS (federal):** a few refuges (e.g. Ruby Lake NWR) — most have no developed campground;
  confirm before keeping. Set `ownership: "federal"`.
- **Local:** county / city / regional parks AND municipal utility parks. Nevada local camping
  is thin: Washoe County (Davis Creek, Bower's Mansion), Clark County, and municipal RV parks
  (Boulder City, Ely, Elko, Winnemucca, Wells, Caliente, Hawthorne, Battle Mountain, etc.).
  County fairgrounds that run a year-round public RV park count (skip event-only lots). Confirm
  the operator is genuinely local government; county land run by a private concessionaire is
  still `local`.
- **Tribal:** Nevada has many reservations. Tribal-operated campgrounds (Pyramid Lake Paiute,
  Walker River Paiute, Duck Valley, Moapa, etc.) are `ownership: "private"` per convention.
  Pyramid Lake camping is tribal-permit beach camping — keep only if it's genuine drive-in RV
  camping (much of it is drive-on-beach dispersed; vet access).
- **Private (commercial):** already gated to affordable/well-rated ($/$$, ≥4★); still vet each
  — real transient RV park, NOT membership/seasonal/residential/55+/casino-lot. The Vegas
  valley, Pahrump, Laughlin, Mesquite, Reno/Sparks, Carson City, and the I-80 corridor
  (Winnemucca/Battle Mountain/Elko/Wells/West Wendover) have many; keep if drive-in transient
  RV and it clears the inclusion criteria. Many Vegas/Pahrump "resorts" are 55+ or long-term —
  read reviews/site policy and SKIP the residential ones.

### Max-RV-length rule (Nevada mountain sites can be small)
If the reservation system / agency page gives a max vehicle/RV length and it is **≤21 ft
at every site**, SKIP (note the cap in `skip_reason`). 22 ft is a borderline keep. If
firsthand reviews clearly show 28–30-ft rigs fitting despite a low listed max, you may keep
(say so in `inclusion_evidence`). If no length is published, judge from satellite/photos —
if the pull-ins visibly fit a 23-ft rig, keep.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park office/entrance/trailhead. Verify on satellite + the agency campground-map/PDF
  or recreation.gov photos. RV Life coords are often off by km; move onto the loop.
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
  e.g. `recreation.gov Thomas Canyon CG (Humboldt-Toiyabe NF, Ruby Mtns): 40 drive-in sites,
  RVs to 40 ft, reservable -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or rec.gov url>",
    "water_body": "<named lake/river/reservoir/ocean or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  NEVADA is LANDLOCKED — no ocean, no coastal dunes/woods. The big waters are Lake Tahoe
  (`lakefront`/`lakeview`: Nevada Beach, Zephyr Cove), Lake Mead & Lake Mohave (Colorado
  River reservoirs: Boulder Beach, Echo Bay, Callville Bay, Cottonwood Cove), Pyramid Lake
  (tribal), Walker Lake, Lahontan/Rye Patch/Wild Horse/South Fork/Cave Lake reservoirs, and
  the Colorado (Laughlin/Big Bend), Truckee, Carson, Humboldt rivers (`riverfront`/`riverview`).
  Flag the water body + any shoreline site observation so the audit can weigh it. Do NOT
  assign a coastal-dunes value — Nevada's lakes lack genuine shore-dune fields.

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
