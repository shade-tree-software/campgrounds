# Campground add-stage research — agent instructions

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `star`
[RV Life user rating 0–5; 0 = unrated], `price` [0–4 $ signs], `park_type`,
`rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km], and for state-park
candidates `reservemn_placeid` / `reservemn_name` / `reservemn_lat`/`reservemn_lng`
[authoritative park coords + reservation PlaceId]).

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
- membership/club/sales-pitch park (Thousand Trails, Encore, etc.)
- residential / mobile-home / seasonal-full-timer / workforce park; casino lot
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site (e.g. 20-ft forest sites)
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

When unsure between tent-only and RV-capable, dig into the reservation system's
per-site list. **Aggregators (snoflo, camperalerts, campscanner, thedyrt/camping.org
summaries) inflate cabin/day-use parks into fake "RV sites" — never confirm a keep
from an aggregator alone.** Authority = the operator/agency page + the reservation
system's actual site-type list.

### MN-specific authorities
- State parks/SRAs: MN DNR park page `dnr.state.mn.us/state_parks/<slug>.html` (has a
  "Camping & Lodging" section + a downloadable campground map PDF) and the ReserveMN
  per-site list. When `reservemn_placeid` is given, the deep reservation link is
  `https://reservemn.usedirect.com/MinnesotaWeb/#!park/<placeid>` — include it.
- State forests: MN DNR state-forest campground pages
  `dnr.state.mn.us/state_forests/facilities/cmp<id>.html` (or search
  "<name> state forest campground mn dnr"). Most forest campgrounds are FCFS/rustic;
  many are small — **check the max RV/trailer length**: MN DNR forest campground pages
  state it, and several cap at 20–24 ft or are tent/cartin. If every site is under
  ~23 ft, SKIP (under-23ft). Some forest "campgrounds" are actually canoe/water-access
  or a single rustic site — verify drive-in.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park office/entrance. Verify on satellite + the DNR campground-map PDF.
  Prefer the ReserveMN coords as a starting point but move onto the loop if needed.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — `state` for state parks/SRAs/forests/DNR areas. If you discover a
  candidate is actually county/city/federal/private, set the correct value and note it.
- **`website`** — official park/forest page first, then the deep reservation link
  (newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office number if you find it on the official page; else "".
  Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (loops/site count, hookup level, max RV length if notable, FCFS vs reservable) and
  append ` RV Life <star>*/<price as $ signs> (auto 6/2026). --Claude`. If FCFS with no
  booking channel, say "First-come, first-served." Do NOT copy aggregator boilerplate.
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `MN DNR Itasca camping page + ReserveMN: 4 drive-in loops (Pine Ridge/Bear Paw)
  tent+elec RV sites to 60 ft -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or ReserveMN/rec.gov url>",
    "water_body": "<named lake/river or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.

## Output
Do NOT edit any repo files. Final message = ONLY a JSON array (no prose, no fences),
one object per candidate, SAME order as the batch:
```
{"decision":"add"|"skip","skip_reason":"<if skip>","name":"...","location":"lat,lng",
 "elevation_meters":<num>,"ownership":"state","website":"...","phone":"...","note":"...",
 "inclusion_evidence":"...","waterfront":"not waterfront",
 "lead":{"map_url":"...","water_body":"...","candidate_sites":"...","note":"..."}}
```
For `skip`, only `decision`, `skip_reason`, and `name` are required. Be thorough but
return strictly valid JSON.
