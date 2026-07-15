# Campground add-stage research — agent instructions (WASHINGTON)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `star`
[RV Life user rating 0–5; 0 = unrated], `price` [0–4 $ signs], `park_type`,
`rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km], sometimes `note_hint`).

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
- **largest drive-in sites cap under ~23 ft** at every site (e.g. tiny 18–20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

Washington note: MANY of these are USFS/NPS/state back-country campgrounds on gravel
or forest roads. A decent maintained gravel/dirt road is fine (drive-in). Only skip
for access if it's genuinely 4WD/high-clearance-required or the sites are all tiny
tent pads. Some famous WA campgrounds are **boat-in or hike-in only** — Stehekin
(Lake Chelan NRA), Ross Lake boat-in camps, most Olympic coast beach camps, San Juan
marine-park camps — SKIP those. **Aggregators (snoflo, camperalerts, campscanner,
thedyrt/camping.org summaries) inflate cabin/day-use parks into fake "RV sites" —
never confirm a keep from an aggregator alone.** Authority = the operator/agency
page + the reservation system's actual site list.

### Washington-specific authorities
- **NPS (federal):** `recreation.gov` is the workhorse.
  - **Olympic NP** — Kalaloch is ALREADY in the DB (skip it as dup); others: Hoh,
    Mora, Sol Duc, Fairholme, Heart O' the Hills, Staircase, Ozette, Deer Park,
    Graves Creek, Queets, South Beach, Dosewallips (road washed out — verify open).
  - **Mount Rainier NP** — Cougar Rock, Ohanapecosh, White River (Sunshine Point/
    Longmire closed — verify).
  - **North Cascades NP complex / Ross Lake NRA** — Newhalem Creek, Colonial Creek,
    Goodell Creek, Gorge Lake. (Lake Chelan NRA Stehekin = boat/hike-in → skip.)
  - **Lake Roosevelt NRA** (NPS-run, Columbia/Grand Coulee) — Spring Canyon, Keller
    Ferry, Fort Spokane, Porcupine Bay, Evans, Kettle Falls, Gifford, Hunters, Hawk
    Creek, Kettle River, Marcus Island, Napoleon Bridge, etc.
  - Set `ownership: "federal"`. Deep link recreation.gov → `/camping/campgrounds/<id>`.
- **USFS (federal):** Olympic NF, Mt Baker-Snoqualmie NF, Okanogan-Wenatchee NF
  (Wenatchee/Chelan/Entiat/Methow/Naches districts), Gifford Pinchot NF, Colville NF.
  Huge number of drive-in campgrounds; most on recreation.gov, some FCFS. Set
  `ownership: "federal"`.
- **USACE (federal, `park_type: coe`):** Snake River dams (Ice Harbor, Lower
  Monumental, Little Goose, Lower Granite) and Columbia (McNary/Lake Wallula:
  Charbonneau, Fishhook, Hood Park), Mud Mountain Dam, Howard A. Hanson. Many free/
  FCFS; some reservable on recreation.gov. Set `ownership: "federal"`.
- **Reclamation (federal):** a few; but note **Banks Lake (Steamboat Rock SP)** and
  Lake Chelan reservoirs are run by WA State Parks → `state`, not federal. Credit the
  actual operator, not the dam owner.
- **State parks (WA State Parks):** official page
  `parks.wa.gov/find-parks/state-parks/<slug>`. Reservations run through
  **washington.goingtocamp.com** (Aspira/goingtocamp SPA — no clean US-eDirect API;
  use the park's goingtocamp landing URL if you can, else the parks.wa.gov page + a
  bare `https://washington.goingtocamp.com`). Deception Pass is ALREADY in the DB
  (skip as dup). Big camping state parks: Steamboat Rock, Sun Lakes-Dry Falls, Fort
  Worden, Cape Disappointment, Grayland Beach, Ocean City, Twin Harbors, Pacific
  Beach, Twanoh, Belfair, Lake Chelan, Moran (Orcas), Fields Spring, Riverside,
  Lincoln Rock, Wenatchee Confluence, Potholes, Kanaskat-Palmer, etc. Set
  `ownership: "state"`.
- **WA DNR (`park_type: dnr` → almost always state):** Washington Dept. of Natural
  Resources campgrounds (recreation on state trust land). Official page
  `dnr.wa.gov/Rec<slug>` / the "Recreation" section. These are **FCFS, free, Discover
  Pass required** (no reservation system) — say "First-come, first-served (Discover
  Pass required)" in the note. e.g. Middle Waddell, Margaret McKenny, Sherman Valley,
  Fall Creek, Tahuya-area, Yacolt Burn (Rock Creek, Cold Creek), Mount Si NRCA. Set
  `ownership: "state"`. (Rare BLM in eastern WA = federal — verify if the operator is
  clearly BLM, e.g. Juniper Dunes.)
- **Local:** county/city parks AND **Public Utility District (PUD) parks** — Chelan
  County PUD, Douglas County PUD, Grant County PUD run big Columbia-River campgrounds
  (Beebe Bridge, Daroga, Lincoln Rock[state], Entiat, Chelan Falls, Crescent Bar,
  Sun Lakes-area) — WA PUDs are units of local government → `ownership: "local"`.
  County/city/port/regional/metro parks → `local`. Confirm the operator is genuinely
  local government. County land run by a private concessionaire is still `local`.
- **Private (commercial):** already gated to affordable/well-rated ($/$$, ≥4★); still
  vet each — real transient RV park, not membership/seasonal/residential. Coastal WA
  (Long Beach Peninsula, Ocean Shores) and the Cascades/San Juans have many; keep if
  drive-in transient RV and it clears the inclusion criteria.

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
  e.g. `recreation.gov Ohanapecosh CG (Mt Rainier NP): 188 drive-in sites, RVs to 32 ft,
  reservable -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or rec.gov/goingtocamp url>",
    "water_body": "<named lake/river/reservoir/ocean/sound or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  WA COASTAL note for the lead: the Pacific coast (Long Beach Peninsula: Grayland
  Beach, Cape Disappointment, Ocean City, Pacific Beach) has genuine dune fields and
  shore forest — flag `water_body: "Pacific Ocean"` and any dune/beach observation so
  the audit can weigh `coastal dunes`/`coastal woods`. Puget Sound / Salish Sea sites
  are saltwater (`bayfront`/`bayview` candidates).

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
