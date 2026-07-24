# Campground add-stage research — agent instructions (ATLANTIC CANADA: NB/NS/PE/NL)

You are researching candidate campgrounds for a personal RV-trip database and
returning ready-to-append records. Your batch file (path in your prompt) is a
JSON array of candidate objects from RV Life (fields: `cg_name`, `city`, `prov`
[NB/NS/PE/NL], `star` [RV Life user rating 0–5; 0 = unrated], `price` [0–4 $
signs], `avg_rate` [nightly rate in **CAD**], `park_type`,
`rvlife_lat`/`rvlife_lng` [APPROXIMATE — often off by km]).

The RV ("EKKO") is 23 ft. Decide keep/skip per the inclusion criteria, then for
each KEEP produce a full record. Load `WebFetch` + `WebSearch` via ToolSearch
(`select:WebFetch,WebSearch`) and use them freely. Satellite look (curl GET works):
`curl -s "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=<lng-d>,<lat-d>,<lng+d>,<lat+d>&bboxSR=4326&size=1000,1000&format=jpg&f=image" -o /tmp/r_<id>.jpg`
with d=0.0035, then **Read** the jpg. Keep size ≤ 1000,1000.

Atlantic Canada is mostly anglophone, but **northern/eastern New Brunswick is
Acadian francophone** — some official pages are French (*camping* vocab: *terrain
de camping* = campground, *emplacement* = site, *avec/sans services* =
with/without hookups, *rustique* = primitive, *chalet* = cabin [NOT an RV site],
*prêt-à-camper* = ready-to-camp/glamping [NOT an RV site], *premier arrivé premier
servi* = FCFS). Read them anyway.

## Inclusion criteria (SKIP if it fails)
KEEP only a real, currently-operating, **drive-in RV campground usable by a 23-ft
rig** (at least some drive-in sites fit 23 ft; reachable by a normal vehicle —
decent dirt/gravel OK, hardcore 4WD-only disqualifies; hookups NOT required,
grass pad fine). SKIP (and say why in `skip_reason`) if it is actually:
- cabins-only / chalet-only / cottage-resort / prêt-à-camper / yurt-or-glamping-only;
  tent-only or all walk-in/cart-in/hike-in/boat-in/canoe-in
- group-only / youth-camp / scout / retreat only
- **equestrian-only horse camp** (a general campground that merely offers horse sites is OK)
- day-use only (no overnight camping); a beach/day-park with no campground
- fairground/event-lot that camps only during events
- membership/club/sales-pitch park (Thousand Trails, Encore, Coast-to-Coast, etc.)
- **residential / mobile-home / seasonal-full-timer / workforce park; casino lot**
- closed / defunct / no evidence it currently operates (dead site + thin reviews = strike)
- **largest drive-in sites cap under ~23 ft** at every site
- a **duplicate** of another candidate in THIS batch, or a clearly different name for
  the same campground (keep one; name the other in `skip_reason`).

**The seasonal-park trap:** Atlantic private parks skew heavily toward seasonal
("lease your site for the summer") operations. A park that sells mostly seasonal
sites is still a KEEP **if it genuinely holds a real inventory of nightly transient
RV sites** — but if transient camping is a token handful, or the site map is
wall-to-wall seasonal trailers with a "seasonal only" policy, SKIP it. Check the
operator's own rates page for a nightly/overnight rate, and look at satellite:
decks, sheds, skirting, add-a-rooms on every pad = seasonal park.

When unsure between tent-only and RV-capable, dig into the operator/agency page or
the reservation system's per-site list. **Aggregators (snoflo, camperalerts,
campscanner, thedyrt/camping.org summaries) inflate cabin/day-use/seasonal parks
into fake "RV sites" — never confirm a keep from an aggregator alone.** Authority =
the operator/agency page + the reservation system's actual site-type list.

## Atlantic authorities & ownership
RV Life mistags government parks as `commercial` and sometimes tags Parks Canada as
`canadian`/`national`. Credit the REAL operator:
- **`provincial`** — the four provincial park systems:
  - **NB** — *Parks NB / Parcs NB* (e.g. Mactaquac, Parlee Beach, Mount Carleton,
    Sugarloaf, Murray Beach, de la République, Val Comeau). Reservations:
    `nbparks.ca` / `parcsnbparks.ca` (goingtocamp).
  - **NS** — *Nova Scotia Provincial Parks* (`parks.novascotia.ca`); reservations
    `novascotia.goingtocamp.ca` (goingtocamp SPA).
  - **PE** — *PEI Provincial Parks* (`www.princeedwardisland.ca/en/topic/provincial-parks`);
    reservations via the PEI parks reservation portal.
  - **NL** — *Newfoundland & Labrador Provincial Parks* (`gov.nl.ca` parks;
    reservations `nlcamping.ca`). **NL nuance:** most NL provincial parks are run by
    **private concessionaires under licence on provincial park land** — the land and
    designation are provincial, so ownership is **`provincial`**, not private (note
    the concessionaire in the note if you like). NL also has many *unserviced
    municipal/community* parks (see local).
- **`federal`** — **Parks Canada national parks/sites ONLY**: Fundy & Kouchibouguac
  (NB); Kejimkujik & Cape Breton Highlands (NS); PEI National Park (Cavendish/
  Stanhope/Robinsons Island); Gros Morne & Terra Nova (NL). Pages `parks.canada.ca`;
  reservation `reservation.pc.gc.ca` (goingtocamp). A single national park often has
  SEVERAL distinct drive-in campgrounds — those are legitimately separate entries.
- **`local`** — municipal / town / city / village campgrounds, and community-run
  or service-club (Lions/Kinsmen) parks on municipal land. Do NOT apply a star/price
  gate to local — public campgrounds are cheap and lightly reviewed; keep any
  confirmed local-government drive-in RV campground and just record the RV Life
  star/price in the note.
- **`private`** — everything else: commercial parks, **First Nations / Mi'kmaq /
  Wolastoqey-run** campgrounds (First-Nations-run = private), KOAs, utility-run parks.

Do NOT apply a star/price gate to a park you reclassify as government-run.

**Why the private batch exists (CAD pricing):** RV Life's `$` price tags are NOT
currency-adjusted — the $/$$/$$$ cutoffs ($20/$40/$70) are applied to the raw
nominal rate, which for Canadian parks is CAD, so Canadian parks are over-tiered
~1 level. The private candidates were gated on the CAD-converted rate (≤ ~$55 CAD ≈
$40 USD) AND ≥4★, so they ARE the affordable tier. Do NOT skip a private candidate
merely because RV Life shows `$$$` — the price gate is already satisfied.

## For each KEEP, produce the record
- **`location`** — pin to the actual CAMPGROUND LOOP (where the pads are), 5 decimals,
  NOT the park HQ/entrance or town centroid. Verify on satellite + the agency
  campground-map PDF. RV Life coords are often km off.
- **`elevation_meters`** — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>`
  at your final pinned coord (number, not string).
- **`ownership`** — one of `provincial` / `federal` / `local` / `private` per above.
- **`website`** — official park/operator page first, then the deep reservation link
  (newline-separated, deduped by domain). URLs go HERE, not in `note`.
- **`phone`** — the park/office number if on the official page; else "". Never fabricate.
- **`note`** — concise, every claim sourced. Include the camping basics you confirmed
  (loops/site count, hookup level, transient vs seasonal mix, max RV length if
  notable, FCFS vs reservable, open season) and append
  ` RV Life <star>*/<price as $ signs> CAD ~$<avg_rate>/night (auto 7/2026). --Claude`
  (for public parks with avg_rate 0, just record the star/price). If FCFS with no
  booking channel, say "First-come, first-served." Do NOT copy aggregator
  boilerplate. Keep names/accents intact (UTF-8).
- **`inclusion_evidence`** — ONE line naming the authoritative source + what it showed,
  e.g. `Parks NB Mactaquac page + goingtocamp per-site list: 300+ serviced drive-in
  sites incl pull-thrus to 40 ft -> real transient RV campground`.
- **`waterfront`** — ALWAYS the literal placeholder `"not waterfront"` (a later audit
  decides; do NOT set it from name/marketing — many are named "…Beach"/"…Ocean" and
  that is explicitly NOT evidence).
- **`lead`** — head start for that later waterfront audit (NOT a verdict):
  `{"map_url": "<official per-site campground map/PDF or reservation-map url>",
    "water_body": "<named lake/river/sea or ''>",
    "candidate_sites": "<site numbers you saw at/near the water, or ''>",
    "note": "<one-line shoreline observation from the map/satellite, or ''>"}`.
  **Atlantic Canada is intensely coastal** — Bay of Fundy, the Atlantic, Gulf of St.
  Lawrence, Northumberland Strait. The **`coastal dunes`** override (undeveloped
  wind-dune field backing, e.g. PEI/Kouchibouguac/Îles beaches) and **`coastal
  woods`** override (set-back-in-the-shore-forest on the ocean/Gulf) can apply —
  note in the lead if sites sit behind a real shore dune field or shore forest.

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
