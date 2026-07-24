# Campground add-stage research — agent instructions (CANADA private top-up: ON/BC/AB/SK/MB)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `prov`,
`star` [RV Life user rating 0–5], `price` [0–4 $ signs], `avg_rate` [nightly rate
in **CAD**], `park_type`, `rvlife_lat`/`rvlife_lng` [APPROXIMATE — often km off]).

**Why this batch exists:** RV Life's `$` price tags are NOT currency-adjusted — the
$/$$/$$$ cutoffs ($20/$40/$70) are applied to the raw nominal rate, which for
Canadian parks is CAD. These parks were tagged `$$$` and wrongly excluded from the
earlier ON/BC/AB/SK/MB sweeps even though their CAD rate converts to ≤ ~$40 USD.
They are the affordable tier, not the expensive one. Do NOT skip a candidate merely
because RV Life shows `$$$` — the price gate is already satisfied by the CAD rate.

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
- cabins-only / cottage-resort-only / yurt-or-glamping-only; tent-only or all
  walk-in/cart-in/hike-in/boat-in/canoe-in
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping)
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park (Thousand Trails, Encore, Coast-to-Coast, etc.)
- **residential / mobile-home / seasonal-full-timer / workforce park; casino lot**
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site
- a **duplicate** of another candidate in THIS batch, or of a campground under a
  different name (keep one; name the other in `skip_reason`).

**The seasonal-park trap is the #1 risk in this bucket.** Canadian private parks
skew heavily toward seasonal/"lease your site for the summer" operations. A park
that sells mostly seasonal sites is still a KEEP **if it genuinely holds a real
inventory of nightly transient RV sites** — but if transient camping is a token
handful of spots, or the site map is wall-to-wall seasonal trailers with a "no
overnight" or "seasonal only" policy, SKIP it. Check the operator's own rates page
for a nightly/transient rate, and look at satellite: decks, sheds, skirting, and
permanent add-a-rooms on every pad = seasonal park.

When unsure between tent-only and RV-capable, dig into the operator's own site map
or booking engine. **Aggregators (snoflo, camperalerts, campscanner, thedyrt /
camping.org summaries) inflate cabin/day-use/seasonal parks into fake "RV sites" —
never confirm a keep from an aggregator alone.** Authority = the operator's own
page + its actual booking/site list.

## Ownership — RV Life tags every one of these `commercial`, but it mistags
Most will genuinely be `private`. Watch for government parks mislabeled commercial
(prior sweeps rescued dozens this way) and credit the real operator:
- **`provincial`** — Ontario Parks, BC Parks & Recreation Sites and Trails BC
  (RSTBC), Alberta Parks (incl. contractor-operated Alberta Parks land),
  Saskatchewan Provincial Parks, Manitoba Provincial Parks. Also BC Hydro rec sites.
- **`local`** — municipal / town / city / village campgrounds, regional districts
  (BC), counties & municipal districts (AB), **Saskatchewan "Regional Parks" (these
  are LOCAL, not provincial — a standing SK rule)**, Ontario **Conservation
  Authorities** (Grand River CA, Otonabee, Kawartha, Long Point, etc. = LOCAL), and
  municipally-run marina/beach campgrounds.
- **`federal`** — Parks Canada only (national parks/historic sites).
- **`private`** — everything else: commercial parks, First Nations–run campgrounds,
  utility-run parks (a utility campground is private), forestry-company sites.

Do NOT apply a star/price gate to a park you reclassify as government-run — public
campgrounds are cheap and lightly reviewed; keep any confirmed government drive-in
RV campground and just record the RV Life star/price in the note.

### Reservation systems by province (for the `website` deep link)
- **ON** — Ontario Parks: `reservations.ontarioparks.ca` (goingtocamp SPA).
  Conservation Authorities book on their own sites or Let's Camp / goingtocamp.
- **BC** — BC Parks: `camping.bcparks.ca` (goingtocamp). RSTBC sites are mostly FCFS.
- **AB** — Alberta Parks: `reserve.albertaparks.ca` (ReserveAmerica, contractCode
  ABPP; Queue-it fronted — a plain fetch may bounce, that's expected).
- **SK** — Saskatchewan Parks: ReserveAmerica contractCode SKPP.
- **MB** — Manitoba Parks: `manitobaelicensing.ca` / goingtocamp.
- Private parks: their own site, Campspot, Let's Camp, or phone.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the highway sign, office, or town centroid. Verify on satellite. RV Life coords
  are often km off.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — one of `private` / `provincial` / `local` / `federal` per above.
- **`website`** — official operator page first, then the deep reservation link
  (newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office number if on the official page; else "". Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (site count, hookup level, transient vs seasonal mix, max RV length if notable,
  FCFS vs reservable, open season) and append
  ` RV Life <star>*/<price as $ signs> CAD ~$<avg_rate>/night (auto 7/2026). --Claude`.
  Recording the CAD rate matters — it is the evidence this park clears the gate.
  If FCFS with no booking channel, say "First-come, first-served." Do NOT copy
  aggregator boilerplate. Keep names/accents intact (UTF-8).
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `Operator site rates page + campground map: 60 nightly serviced pull-thrus to
  40 ft alongside seasonal section -> real transient RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing — many of these are named "…Lakefront"
  or "…Beach Resort" and that is explicitly NOT evidence).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/site-map url>",
    "water_body": "<named lake/river/sea or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  BC is Pacific-coastal and ON/MB sit on the Great Lakes / Lake Winnipeg, so the
  coastal-woods and coastal-dunes overrides can apply — note it in the lead if the
  sites sit behind a real undeveloped shore dune field or shore forest.

## Output
Do NOT edit any repo files. Final message = ONLY a JSON array (no prose, no fences),
one object per candidate, SAME order as the batch:
```
{"decision":"add"|"skip","skip_reason":"<if skip>","name":"...","location":"lat,lng",
 "elevation_meters":<num>,"ownership":"private","website":"...","phone":"...","note":"...",
 "inclusion_evidence":"...","waterfront":"not waterfront",
 "lead":{"map_url":"...","water_body":"...","candidate_sites":"...","note":"..."}}
```
For `skip`, only `decision`, `skip_reason`, and `name` are required. Be thorough but
return strictly valid JSON.
