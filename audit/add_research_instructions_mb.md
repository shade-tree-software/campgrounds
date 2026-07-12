# MB Campground add-stage research — agent instructions

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records for **Manitoba, Canada**. Your batch file
(path in your prompt) is a JSON array of candidate objects from RV Life (fields:
`cg_name`, `city`, `star` [RV Life user rating 0–5; 0 = unrated], `price` [0–4 $
signs], `park_type`, `ownership_hint` [best-guess bucket — CONFIRM & override per
entry], `rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km]).

The RV ("EKKO") is 23 ft. Decide keep/skip per the inclusion criteria, then for
each KEEP produce a full record. Load `WebFetch` + `WebSearch` via ToolSearch
(`select:WebFetch,WebSearch`) and use them freely. Satellite look (curl GET works):
`curl -s "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=<lng-d>,<lat-d>,<lng+d>,<lat+d>&bboxSR=4326&size=1000,1000&format=jpg&f=image" -o /tmp/r_<name>.jpg`
with d=0.0035, then **Read** the jpg. Keep size ≤ 1000,1000.

## Inclusion criteria (SKIP if it fails)
KEEP only a real, currently-operating, **drive-in RV campground usable by a 23-ft
rig** (at least some drive-in sites fit 23 ft; reachable by a normal vehicle —
decent dirt/gravel OK, hardcore 4WD-only disqualifies; hookups NOT required,
grass pad fine). SKIP (say why in `skip_reason`) if it is actually:
- cabins-only / yurt-only; tent-only or all walk-in/cart-in/hike-in/boat-in/paddle-in
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping)
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park; seasonal-lease / full-timer / residential /
  mobile-home / workforce park; casino lot
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

When unsure tent-only vs RV-capable, dig into the reservation system's per-site
list. **Aggregators (snoflo, camperalerts, campscanner, thedyrt/camping.org
summaries) inflate cabin/day-use parks into fake "RV sites" — never confirm a keep
from an aggregator alone.** Authority = the operator/agency page + the reservation
system's actual site-type list.

## MB-specific authorities & ownership
- **Manitoba Provincial Parks** (`ownership: "provincial"`): official pages at
  `https://www.gov.mb.ca/nrnd/parks/` (Manitoba Parks) / `manitobaparks.com`;
  reserve via **goingtocamp** — host `manitoba.goingtocamp.com`. Deep link
  (Platform A SPA): `https://manitoba.goingtocamp.com/create-booking/results?resourceLocationId=<parkId>&mapId=<campgroundId>&bookingCategoryId=0`
  (resourceLocationId=park, mapId=campground/loop; both are large NEGATIVE ints
  from the goingtocamp API — if you can't resolve mapId, at minimum include the
  `manitoba.goingtocamp.com` booking site + the official Manitoba Parks page).
  Big parks (Whiteshell, Duck Mountain, Nopiming, Grass River, Turtle Mountain,
  Clearwater Lake) have MANY named-lake campgrounds — each distinct loop is its
  own entry; confirm drive-in RV access (some northern/rustic ones are boat/tent).
  NOTE: Manitoba has NO SK-style "Regional Park" class — provincial parks are
  provincial. But watch for a town/municipal campground RV Life mis-tagged
  `provincial` (e.g. "Gilbert Plains Campground") -> set `local`.
- **Federal** (`ownership: "federal"`): Parks Canada only — **Riding Mountain
  National Park** (Wasagaming + Lake Audy/Moon/Deep Lake). Official pages
  `https://parks.canada.ca/...`; reserve via goingtocamp `reservation.pc.gc.ca`.
  Keep only drive-in frontcountry loops (some are rustic/backcountry).
- **Local** (`ownership: "local"`): municipal / town / village / RM / Lions /
  Kinsmen town campgrounds, municipal beach/rec-area campgrounds. Don't apply the
  ≥4★/≤$$ gate to public/local-gov entries (they're cheap & lightly reviewed).
- **Private** (`ownership: "private"`): commercial. Apply the gate (keep only
  ≥4★ AND ≤$$, non-membership) then vet per inclusion criteria; First Nations-run
  commercial campgrounds fold into `private`.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park office/entrance. Verify on satellite + any official campground map.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — one of federal/provincial/local/private, CONFIRMED (override the hint).
- **`website`** — official park page first, then the deep reservation link
  (newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office number from the official page; else "". Never fabricate.
- **`note`** — concise, every claim sourced. Include camping basics you confirmed
  (loops/site count, hookup level, max RV length if notable, FCFS vs reservable) and
  append ` RV Life <star>*/<price as $ signs> (auto 7/2026). --Claude`. If FCFS with
  no booking channel, say "First-come, first-served." No aggregator boilerplate.
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `Manitoba Parks Whiteshell/Nutimik page + goingtocamp: 3 elec loops, RV sites to 45 ft -> real drive-in RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit decides).
- **`lead`** — head start for the later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or reservation url>",
    "water_body": "<named lake/river or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from map/satellite, or ''>"}`.

## Output
Do NOT edit any repo files. Final message = ONLY a JSON array (no prose, no fences),
one object per candidate, SAME order as the batch:
```
{"decision":"add"|"skip","skip_reason":"<if skip>","name":"...","location":"lat,lng",
 "elevation_meters":<num>,"ownership":"...","website":"...","phone":"...","note":"...",
 "inclusion_evidence":"...","waterfront":"not waterfront",
 "lead":{"map_url":"...","water_body":"...","candidate_sites":"...","note":"..."}}
```
For `skip`, only `decision`, `skip_reason`, and `name` are required. Be thorough but
return strictly valid JSON.
