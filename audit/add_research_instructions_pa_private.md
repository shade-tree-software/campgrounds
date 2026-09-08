# Campground add-stage research — agent instructions (PA private re-sweep)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `star`
[RV Life user rating 0–5], `price` [0–4 $ signs], `avg_rate` [nightly USD],
`park_type`, `rvlife_lat`/`rvlife_lng` [APPROXIMATE — often km off]).

**Why this batch exists:** Pennsylvania's private stage (May–June 2026) was
detected from **Good Sam**, with RV Life used only to filter that list on
price/stars. Any independent park without a Good Sam rating was therefore never a
candidate. The same gap was found and closed for Virginia on 2026-09-07 (15 adds
from 32 candidates); this is the RV-Life-first detection PA never got: all PA
`park_type == commercial` parks with `price_level` ≤ 2 and `star_rating` ≥ 4 that
are not already in the database.

Note PA's inclusion audit is already complete (169 entries re-vetted, 11 removed),
so the existing PA entries are trustworthy — your job is purely the missing ones.

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
- cabins-only / yurt-or-glamping-only; tent-only or all walk-in/cart-in/hike-in/boat-in
- group-only / youth-camp / scout / church-retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping)
- fairground / event-lot that camps only during events
- **membership / club / sales-pitch park** — Thousand Trails, Encore, Coast-to-Coast,
  Bluegreen; **Elks / Moose / Airstream-club lodges**; timeshare "buy-in" resorts.
  This batch contains several of each; skip them and name the chain or club.
- **casino / racetrack overnight lot** — this batch contains several PA casinos.
  A casino RV *lot* is a skip even when it is free and well-reviewed. If a casino
  turns out to run a genuine separate campground with real sites, say so.
- **residential / mobile-home / seasonal-full-timer / workforce park**
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site
- a **duplicate** of another candidate in THIS batch, or of a campground already in
  the database under a different name (keep one; name the other in `skip_reason`).

**The seasonal park is the #1 risk in Pennsylvania.** PA private campgrounds skew
harder toward seasonal/"lease your site for the year" operations than any state
swept so far. A park that sells mostly seasonal sites is still a KEEP **if it
genuinely holds a real inventory of nightly transient RV sites** — but if transient
camping is a token handful, or the site map is wall-to-wall permanent trailers with
decks, sheds, skirting and add-a-rooms and a "seasonal only" or "no overnight"
policy, SKIP it. Check the operator's own rates page for a published nightly rate,
and look at satellite: uniform permanent structures on every pad = seasonal park.

When unsure between tent-only and RV-capable, dig into the operator's own site map
or booking engine. **Aggregators (snoflo, camperalerts, campscanner, thedyrt /
camping.org summaries) inflate cabin/day-use/seasonal parks into fake "RV sites" —
never confirm a keep from an aggregator alone.** Authority = the operator's own page
plus its actual booking/site list.

**A dead official domain is a strike, not an automatic skip.** Check where it
actually resolves — in the VA sweep four of sixteen adds had dead or hijacked
domains while being demonstrably live and bookable (one 301'd to an unrelated
veterinary company). If the domain is dead, confirm operation from a live booking
channel (Campspot, Hipcamp, RoverPass, Firefly, CampLife) or dated recent reviews,
point `website` at that live channel, and record the dead domain as a caveat in the
`note`.

## Ownership — RV Life tags every one of these `commercial`, but it mistags
Most will genuinely be `private`. Watch for government parks mislabeled commercial
(prior sweeps rescued dozens this way) and credit the real operator:
- **`state`** — PA DCNR state parks and state forests.
- **`local`** — county / township / borough / city parks and municipal authorities,
  including a county park run by a private concessionaire. PA has many; also watch
  for **municipal authority** recreation areas (e.g. a water/sewer authority running
  a lake campground) — those are `local`.
- **`federal`** — USACE / USFS (Allegheny NF) / NPS.
- **`private`** — everything else: commercial parks, farm campgrounds, fire-company
  and civic-club campgrounds open to the public, utility-run parks.
- **`hipcamp`** — reserve for Hipcamp-only backyard/land listings. A long-established
  commercial campground that merely *lists* on Hipcamp is `private`.

Do NOT apply the star/price gate to a park you reclassify as government-run — public
campgrounds are cheap and lightly reviewed; keep any confirmed government drive-in RV
campground and just record the RV Life star/price in the note.

### Pennsylvania reservation systems (for the `website` deep link)
- **PA State Parks (DCNR)** — verify the current portal from the park's own DCNR
  page rather than assuming; PA has used ReserveAmerica
  (`pennsylvaniastateparks.reserveamerica.com/campgroundDetails.do?contractCode=PA&parkId=<id>`)
  and has been migrating. Always link what the DCNR page itself links.
- **Federal** — `recreation.gov/camping/campgrounds/<id>`
- **Private** — the operator's own site, Campspot, CampLife, Hipcamp, RoverPass, or phone.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the highway sign, office, or town centroid. Verify on satellite. RV Life coords
  are often km off — in the VA sweep one sat 700 m away on a poultry farm and another
  put the campground out on the highway at its entrance.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — one of `private` / `state` / `local` / `federal` / `hipcamp` per above.
- **`website`** — official operator page first, then the deep reservation link
  (newline-separated, deduped by domain). URLs go HERE, not in `note`. Two exceptions
  stay as prose in the note: a NEGATIVE reservation fact ("FCFS — not reservable
  online") and a dead/suspect official domain recorded as a caveat.
- **`phone`** — the office number if on the official page; else "". Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (site count, hookup level, transient vs seasonal mix, max RV length if notable, FCFS
  vs reservable, open season) and append
  ` RV Life <star>*/<price as $ signs> ~$<avg_rate>/night (auto 9/2026). --Claude`.
  Where `avg_rate` is 0 or 1 it is a placeholder, not a real price — say so rather
  than quoting it. Do NOT copy aggregator boilerplate.
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `Operator rates page + campground map: 38 nightly W/E sites to 40 ft alongside
  a seasonal section, Campspot booking -> real transient RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing — several of these are named "Riverfront",
  "Creek", "Lake" or "Pine Creek" and that is explicitly NOT evidence).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/site-map url>",
    "water_body": "<named lake/river/creek or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  PA is landlocked — no coastal-dunes/coastal-woods overrides apply. Its water is
  rivers, creeks and reservoirs, so the open-apron and distance-bound rules govern.

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
