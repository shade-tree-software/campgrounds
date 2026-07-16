# Campground add-stage research — agent instructions (OREGON)

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
- residential / mobile-home / seasonal-full-timer / workforce park; casino lot
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site (e.g. tiny 16–20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

Oregon note: MANY of these are USFS / BLM / NPS back-country campgrounds on gravel
or forest roads. A decent maintained gravel/dirt road is fine (drive-in). Only skip
for access if it's genuinely 4WD/high-clearance-required or the sites are all tiny
tent pads. Some Oregon campgrounds are **boat-in or hike-in only** (Waldo Lake's
far sites, some Cascade lakes, coastal hike-ins) — SKIP those. **Aggregators
(snoflo, camperalerts, campscanner, thedyrt/camping.org summaries) inflate cabin/
day-use parks into fake "RV sites" — never confirm a keep from an aggregator alone.**
Authority = the operator/agency page + the reservation system's actual site list.

### Oregon-specific authorities & ownership
- **State parks (Oregon State Parks / OPRD):** `stateparks.oregon.gov`. Reservations run
  through **ReserveAmerica** (`oregonstateparks.reserveamerica.com`,
  `.../campgroundDetails.do?contractCode=OR&parkId=<id>`). Big camping state parks:
  Cape Lookout (ALREADY in DB — skip as dup), Fort Stevens, Beverly Beach, South Beach,
  Nehalem Bay, Cape Blanco, Bullards Beach, Sunset Bay, Honeyman, Tumalo, LaPine, Detroit
  Lake, Champoeg, Silver Falls, Wallowa Lake, Emigrant Springs, Farewell Bend, Cove
  Palisades, Prineville Reservoir, Valley of the Rogue, etc. Set `ownership: "state"`.
- **Oregon Dept. of Forestry (STATE forests, also `ownership: "state"`):** Tillamook
  State Forest & Clatsop State Forest campgrounds (Dovre, Fan Creek, Elk Creek, Gales
  Creek, Browns Camp[OHV], Jones Creek, Keenig Creek, Diamond Mill, Nehalem Falls,
  Northrup Creek) and Santiam State Forest. `oregon.gov/odf`. FCFS or reservable via
  the forest's own system — verify. **These are STATE, not federal, even though RV Life
  may tag them `dnr`.**
- **BLM (FEDERAL) — this is what `park_type: dnr` USUALLY means in Oregon.** Oregon has
  a HUGE BLM recreation inventory, especially the Roseburg/Glide district (North Umpqua:
  Susan Creek, Millpond, Cavitt Creek Falls, Wolf Creek, Scaredman, Rock Creek, Lone Pine,
  Tyee, Eagle View), the Steens Mountain / Frenchglen area (Page Springs, Fish Lake, South
  Steens, Jackman Park), Leslie Gulch, Gerber Reservoir, Chukar Park, Chickahominy
  Reservoir, Loon Lake, Sixes River, Edson Creek, Coos Bay district, Lakeview district
  (Can Springs, Sunstone), Prineville district (Chimney Rock, Trout Creek, Macks Canyon).
  `blm.gov/visit/<slug>`; some reservable on recreation.gov, many FCFS. Set
  `ownership: "federal"`. **VERIFY the operator per entry** — a `dnr`-tagged site that
  turns out to be an Oregon Dept. of Forestry state-forest camp is `state`; a county-run
  site is `local`.
- **USFS (federal, `park_type: usfs`/`national`):** Oregon's national forests are vast —
  Mt. Hood, Willamette, Deschutes, Umpqua, Rogue River-Siskiyou, Fremont-Winema,
  Ochoco, Malheur, Wallowa-Whitman, Umatilla, Siuslaw NFs. Most drive-in campgrounds are
  on recreation.gov (deep link → `/camping/campgrounds/<id>`); some FCFS. Set
  `ownership: "federal"`. Watch the under-23-ft skip rate — many small Cascade-lake and
  wilderness-edge sites cap at 16–22 ft; skip if the max RV length disqualifies (see below).
- **NPS (federal, `park_type: national`):** Crater Lake NP (Mazama Village, Lost Creek—
  tent-only, skip), Oregon Caves NM (no campground), John Day Fossil Beds (no campground),
  Lake Roosevelt is WA. Set `ownership: "federal"`.
- **USACE (federal, `park_type: coe`):** Willamette Valley reservoirs (Detroit is state;
  but Cottage Grove Lake, Dorena Lake, Fall Creek, Lookout Point, Fern Ridge, Blue River,
  Hills Creek, Dexter) and Columbia/Willamette projects. Many reservable on recreation.gov.
  Credit the actual operator — some COE reservoirs are run by Oregon State Parks or a
  county (then state/local). Set `ownership: "federal"` only if COE-operated.
- **Reclamation (federal):** a few reservoir campgrounds (e.g. Prineville is a STATE
  park on a Reclamation dam → state). Credit the operator, not the dam owner.
- **Local:** county / city / port / regional / metro parks AND **People's Utility District
  (PUD) parks**. Oregon county parks are extensive (Lane, Douglas, Josephine, Jackson,
  Deschutes, Klamath, Coos, Tillamook, Clackamas, Hood River, Wasco, Union, Baker,
  Wallowa county parks). Port districts (Port of Newport, Port of Garibaldi) and city
  parks (e.g. municipal RV parks). PUDs/municipal utilities are units of local government
  → `ownership: "local"`. Confirm the operator is genuinely local government. County land
  run by a private concessionaire is still `local`.
- **Private (commercial):** already gated to affordable/well-rated ($/$$, ≥4★); still
  vet each — real transient RV park, not membership/seasonal/residential/casino. Coastal
  Oregon (US-101), the Columbia Gorge, Bend/Sisters, and the Cascade lakes have many;
  keep if drive-in transient RV and it clears the inclusion criteria.

### Max-RV-length rule (Oregon has many small forest sites)
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
  e.g. `recreation.gov Susan Creek CG (BLM Roseburg): 31 drive-in sites, RVs to 35 ft,
  reservable -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or rec.gov url>",
    "water_body": "<named lake/river/reservoir/ocean or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  OREGON COASTAL note for the lead: the Pacific coast (US-101) has genuine dune fields
  (Oregon Dunes NRA: Honeyman, Jessie Honeyman, Umpqua, Windy Cove, Carter Lake, Tahkenitch,
  Eel Creek; Fort Stevens; Bullards Beach) and shore forest — flag `water_body: "Pacific
  Ocean"` and any dune/beach observation so the audit can weigh `coastal dunes`/`coastal
  woods`. Cascade lakes/reservoirs are `lakefront`/`lakeview` candidates; the many rivers
  (Deschutes, Umpqua, Rogue, McKenzie, Metolius, John Day) are `riverfront`/`riverview`.

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
