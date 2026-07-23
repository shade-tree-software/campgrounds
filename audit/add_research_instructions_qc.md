# Campground add-stage research — agent instructions (QUEBEC)

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

**Quebec is francophone** — most official pages are in French. SEPAQ and Parks
Canada have English versions (`/en/` paths or `language_id=1`); municipal sites
are often French-only — read them anyway (place/camping vocabulary: *camping
aménagé* = serviced/drive-in sites, *camping semi-aménagé* = partial services,
*camping rustique* = primitive drive-in or walk-in [check which], *prêt-à-camper*
/ *tente Huttopia* / *chalet* = ready-to-camp/cabin [NOT an RV site], *sans
service* = no hookups, *accès* = access, *réservation* = reservation, *premier
arrivé premier servi* = first-come-first-served).

## Inclusion criteria (SKIP if it fails)
KEEP only a real, currently-operating, **drive-in RV campground usable by a 23-ft
rig** (at least some drive-in sites fit 23 ft; reachable by a normal vehicle —
decent dirt/gravel OK, hardcore 4WD-only disqualifies; hookups NOT required,
grass pad fine). SKIP (and say why in `skip_reason`) if it is actually:
- cabins-only / chalet-only / prêt-à-camper / Huttopia-tent / yurt-only; tent-only
  or all walk-in/cart-in/hike-in/boat-in/canoe-in/paddle-in
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping); a beach/*halte* with no campground
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park (Thousand Trails, Encore, etc.)
- residential / mobile-home / seasonal-full-timer / workforce park; casino lot
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site
- a **duplicate** of another candidate in THIS batch or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

When unsure between tent-only and RV-capable, dig into the reservation system's
per-site list. **Aggregators (snoflo, camperalerts, campscanner, thedyrt/camping.org
summaries) inflate cabin/day-use parks into fake "RV sites" — never confirm a keep
from an aggregator alone.** Authority = the operator/agency page + the reservation
system's actual site-type list.

### Quebec-specific authorities & ownership
- **SEPAQ provincial parks & wildlife reserves (`ownership: provincial`)** — Quebec
  confusingly calls its PROVINCIAL parks *"parc national"*; they are SEPAQ (Société
  des établissements de plein air du Québec), NOT federal. Official pages:
  `sepaq.com/pq/<slug>` (parcs nationaux) and `sepaq.com/rf/<slug>` (réserves
  fauniques). Reservation/camping: `sepaq.com/en/reservation/camping/<full-slug>`.
  SEPAQ publishes per-campground/sector maps (great `lead` map_url). **Réserve
  faunique** camps are often rustic drive-to lakeside sites on gravel roads —
  confirm drive-in + RV-fitting (some réserve sites are canoe-in/boat-in remote;
  skip those). A parc national frequently has SEVERAL distinct drive-in
  campgrounds at different lakes/sectors — those are legitimately separate entries
  (e.g. Mont-Tremblant's Lac Provost / Lac Lajoie / Lac-Chat are all real).
- **Parks Canada (`ownership: federal`)** — only true national parks (La Mauricie,
  Forillon, Mingan). Pages `parks.canada.ca`; reservation `reservation.pc.gc.ca`
  (goingtocamp SPA). Anything labelled "…Reserve/Réserve faunique" is SEPAQ
  **provincial**, not federal, despite an RV Life `canadian` mistag.
- **Municipal / regional (`ownership: local`)** — *Camping Municipal de X*, *Camping
  régional de X* (MRC/regional-county), town/city-run parks, and municipal
  nonprofit outdoor centres (*Centre de plein air*, *Parc de l'Île X*). Do NOT
  apply a star/price gate to local — public municipal campgrounds are cheap and
  lightly reviewed; keep any confirmed local-government drive-in RV campground and
  just record the RV Life star/price in the note. Reservations via the town site
  or a booking platform (Sépaq/Camping-Québec/Bonjour Québec/each town). *Camping
  Manic-2* (Baie-Comeau) is at a **Hydro-Québec** dam — if Hydro-Québec-run treat
  as `private` (utility-run) per the utility rule; if the town runs it, `local`.
- **Private (`ownership: private`)** — commercial parks. Vet per inclusion (real
  transient RV park, not seasonal/residential/membership; dead-website strike).
- **ZEC** (zone d'exploitation contrôlée) — community nonprofit-managed Crown land;
  if one surfaces with a real drive-in RV campground, `ownership: local` and note it.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park office/entrance. Verify on satellite + the SEPAQ/Parks-Canada
  campground-map PDF. RV Life coords are often km off.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — one of `provincial` / `federal` / `local` / `private` per above.
- **`website`** — official park/municipal page first, then the deep reservation link
  (newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office number if on the official page; else "". Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (sectors/loops/site count, hookup level, max RV length if notable, FCFS vs
  reservable) and append ` RV Life <star>*/<price as $ signs> (auto 6/2026). --Claude`.
  If FCFS with no booking channel, say "First-come, first-served." Do NOT copy
  aggregator boilerplate. Keep names/accents intact (UTF-8).
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `SEPAQ Mont-Tremblant camping map + reservation site: Lac Provost sector has
  drive-in serviced + rustic RV sites -> real RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or reservation-map url>",
    "water_body": "<named lake/river/sea or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  Quebec is coastal on the Gulf of St. Lawrence / Gaspé / North Shore / Îles-de-la-
  Madeleine — the coastal-dunes / coastal-woods overrides can apply there; note it
  in the lead if the site sits behind a real shore dune field or shore forest.

## Output
Do NOT edit any repo files. Final message = ONLY a JSON array (no prose, no fences),
one object per candidate, SAME order as the batch:
```
{"decision":"add"|"skip","skip_reason":"<if skip>","name":"...","location":"lat,lng",
 "elevation_meters":<num>,"ownership":"provincial","website":"...","phone":"...","note":"...",
 "inclusion_evidence":"...","waterfront":"not waterfront",
 "lead":{"map_url":"...","water_body":"...","candidate_sites":"...","note":"..."}}
```
For `skip`, only `decision`, `skip_reason`, and `name` are required. Be thorough but
return strictly valid JSON.
