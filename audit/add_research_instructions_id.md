# Campground add-stage research — agent instructions (IDAHO)

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
grass pad fine). SKIP (and say why in `skip_reason`) if it is actually:
- cabins-only / yurt-only; tent-only or all walk-in/cart-in/hike-in/boat-in/paddle-in
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping)
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park (Thousand Trails, Encore, Coast-to-Coast, etc.)
- residential / mobile-home / seasonal-full-timer / workforce park; casino lot
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site (e.g. tiny 18–20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

Idaho note: MANY of these are USFS/BLM back-country campgrounds on gravel forest
roads. A decent maintained gravel/dirt forest road is fine (drive-in). Only skip
for access if it's genuinely 4WD/high-clearance-required or the sites are all
tiny tent pads. Small primitive USFS campgrounds are legitimate keeps if a 23-ft
rig can get in and park — check the recreation.gov "Camping details" / max
vehicle length. When unsure between tent-only and RV-capable, dig into the
reservation system's per-site list or the forest's campground webpage. **Aggregators
(snoflo, camperalerts, campscanner, thedyrt/camping.org summaries) inflate cabin/
day-use parks into fake "RV sites" — never confirm a keep from an aggregator alone.**
Authority = the operator/agency page + the reservation system's actual site list.

### Idaho-specific authorities
- **Federal (most of this state):** `recreation.gov` is the workhorse for USFS,
  BLM, NPS, USACE, and Reclamation campgrounds. Idaho national forests: Boise,
  Payette, Sawtooth NF + Sawtooth NRA, Salmon-Challis, Nez Perce-Clearwater,
  Caribou-Targhee, Idaho Panhandle. NPS: Craters of the Moon NM (Lava Flow CG);
  City of Rocks National Reserve (co-managed NPS + IDPR — ownership `federal`).
  USACE: Dworshak Dam area, Lucky Peak. Reclamation/USFS reservoirs: Palisades,
  Ririe, American Falls, Lake Cascade (Cascade is a STATE park). Many small
  forest campgrounds are FCFS — say "First-come, first-served" in the note.
  Deep reservation link format: recreation.gov → `/camping/campgrounds/<id>`.
  Set `ownership: "federal"` for all of these (USFS/BLM/NPS/USACE/Reclamation).
- **State parks (IDPR):** official page `parksandrecreation.idaho.gov/parks/<slug>/`.
  Idaho State Parks reservations run through **ReserveAmerica**
  (`idahostateparks.reserveamerica.com`) — deep link
  `.../campgroundDetails.do?contractCode=ID&parkId=<id>` or the explore path.
  Verify the current system per-park (Idaho has been migrating providers). Set
  `ownership: "state"`.
- **State DNR-type (`park_type: dnr`):** Idaho Dept of Lands (IDL) recreation
  sites (e.g. Priest Lake, Payette Lake endowment-land campgrounds — some are
  IDL-run, e.g. reservable via `reserveidaho`/`idl.idaho.gov`) and Idaho Fish &
  Game (IDFG) Wildlife Management Areas / access sites. These are `ownership:
  "state"`. IDFG WMAs are often free FCFS primitive camping — verify overnight
  camping is actually allowed (some WMAs are day-use / hunt-access only → skip).
- **Local:** county parks, city parks, port districts, recreation/highway
  districts (`ownership: "local"`). Confirm the operator is genuinely local
  government. County land run by a private concessionaire is still `local`.
- **Private (commercial):** already gated to affordable/well-rated; still vet
  each — real transient RV park, not membership/seasonal/residential. Idaho has
  many "RV resort"/"hot springs resort" parks; keep if drive-in transient RV.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park office/entrance. Verify on satellite + the agency campground-map/PDF or
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
  e.g. `recreation.gov Redfish CG (Sawtooth NRA): 100+ drive-in sites, trailers to
  35 ft, reservable -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or rec.gov/ReserveAmerica url>",
    "water_body": "<named lake/river or ''>",
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
