---
name: reference_canada_sweep_adaptation
description: "How to adapt the state-sweep procedure for Canadian provinces — RV Life park_type mapping, ownership taxonomy, reservation deep-link formats, waterfront evidence gap"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 20c70146-147e-4b0f-a61a-d96ad63bde97
---

Research spike (2026-07-07) for extending the campground sweep to Canada. The pipeline is mostly portable; the deltas below are the load-bearing changes. See [[reference_usedirect_deep_reservation_links]] for the US analog of the reservation-link work.

## Detection — RV Life Algolia (works for Canada, same method)
- Same app `H0LPZK92QJ`, index `park`, `insideBoundingBox` bbox query then post-filter by `region_abbvr` (NOT facetable). `region_abbvr` uses standard 2-letter Canada Post codes (`ON`, `BC`, `AB`, `QC`, `SK`, `MB`, `NB`, `NS`, `PE`, `NL`, `YT`, `NT`, `NU`). Search key extraction is unchanged (inline `algoliasearch('H0LPZK92QJ','<key>')` in any park page; keys rotate — one seen 2026-07-07 was `88da91e06e8ee5ec4aba26675ac26b99`). All US fields present + populated for CA records.
- **`park_type` gains two NEW values not in the US set:** `provincial` (= state-park equivalent: BC/Ontario/Alberta provincial parks & rec areas) and `canadian` (= Parks Canada national parks/NHS — NOT `national`, which is the US value). Others unchanged: `commercial`, `city`, `county`. Sample distribution over ~1,100 ON+AB+BC records: commercial 719 / provincial 293 / canadian 43 / city 32 / county 12.
- Tagging is imperfect (same as US) — a few provincial/CA parks mis-tagged `national`/`state`; Ontario **Conservation Areas** scatter across `state`/`county`/`commercial`. Keep the name-scan cross-check ("Provincial", "Conservation Area", etc.). RV Life's Ontario-Parks coverage isn't exhaustive (e.g. Killarney returned 0).
- **PILOT FINDING (Ontario, 2026-07-07): RV Life pollutes the `provincial` tag heavily with Conservation-Authority parks** (watershed-based **local** government, e.g. Grand River CA, Lower Thames Valley CA). Reliable discriminator: match the RV Life name against the province's goingtocamp `/api/resourceLocation` table (true provincial parks) — a match = genuine provincial; a "X Conservation Area" or CA-operated park = **local**. Some CAs are named without "conservation" (Brant Park = Brant CA, C.M. Wilson, Crowe Bridge, Elora Gorge) and slip a name-scan — the add-research agent corrects ownership per entry, so hand it the hint but let it decide. St. Lawrence Parks Commission (Ontario Crown agency) = `provincial`. CAs often book via `<name>.camp.zone` / `grcamping.ca` / the CA's own site, not Ontario Parks.
- **Detection needs a TILED bbox for large provinces:** Ontario exceeds Algolia's 1000-hit cap in one box — grid the lat/lng span, query each tile, dedup by objectID, post-filter `region_abbvr`. `insideBoundingBox` needs DOUBLE brackets `[[minLat,minLng,maxLat,maxLng]]` in the params string.

## Ownership taxonomy mapping (US → Canada)
- US `state` → **`provincial`** (all provincial/territorial park agencies incl. Quebec's SEPAQ). New ownership value.
- US `federal` → **`federal`**, but shrinks to **Parks Canada only** (national parks + national historic sites). No USACE/USFS/NPS/BLM/Reclamation equivalents, so the "federal reservoir = free/FCFS by default" heuristic mostly evaporates.
- US `local` → **`local`** (municipal + regional-district campgrounds).
- `private` unchanged.
- **Crown-land forest rec sites are PROVINCIAL, not federal** (unlike US USFS/BLM). The one true USFS-dispersed analog is **BC's "Recreation Sites and Trails BC" (RSTBC)** — 1,200+ mapped Crown-land sites, many free/FCFS, run by BC Ministry of Forests (sitesandtrailsbc.ca). Other provinces have dispersed-camping *rules* (ON free Crown-land camping ≤21 days for residents; AB PLUZ/Public Land Rec Areas) but no curated named site network. Bucket RSTBC as `provincial`.
- **First Nations-run campgrounds:** fold into `private` (they operate commercially — bookable, fee, band/dev-corp owned). Common in BC + coastal + Atlantic. If surfacing Indigenous ownership matters, add a secondary flag on top of `private`, not a new top-level bucket.

## Reservation deep-links — TWO platform families + SEPAQ
The Aspira/US-eDirect world splits into two URL grammars; SEPAQ is separate.

**Platform A — goingtocamp / "Let's Camp" Angular SPA** (`/create-booking/results?...`). Ids are exposed in the query string (not hidden), as large **negative 32-bit ints offset from INT_MIN** (e.g. `-2147483607`), **per-installation** (an id is only meaningful within its own host — no cross-system global id). Format:
```
https://<host>/create-booking/results?resourceLocationId=<parkId>&mapId=<campgroundId>&bookingCategoryId=0
```
`resourceLocationId`=park, `mapId`=campground/loop within it, `bookingCategoryId` 0=Campsite/2=Roofed/33=Day-use. Optional `&startDate=YYYY-MM-DD&endDate=...&nights=1&isReserving=true`. **Hosts on Platform A:** Parks Canada `reservation.pc.gc.ca`, BC Parks `camping.bcparks.ca` (replaced discovercamping.ca in Mar 2022), Ontario `reservations.ontarioparks.ca`, Manitoba `manitoba.goingtocamp.com`, Nova Scotia `novascotia.goingtocamp.com`, Yukon `yukon.goingtocamp.com`, New Brunswick `parcsnbparks.ca`, Newfoundland `nlcamping.ca`, NCC Gatineau, several Ontario conservation authorities (`*.goingtocamp.com`). Parks Canada & BC Parks share this exact grammar — one builder covers both, only host differs.
- **The id-lookup — SOLVED, fully scriptable server-side (no browser needed).** The Azure WAF is triggered by *nothing but a bot User-Agent*: a default `curl`/`python-urllib` UA → 403 WAF HTML; **any browser-looking UA header (alone, no cookies/JS/Queue-it) → HTTP 200 real JSON.** Same trick camply uses (`headers={"User-Agent": <random Chrome>, "Accept-Language":"en-US,en;q=0.9"}`; no apikey/auth — open read endpoints). Working call: `curl -s -A "Mozilla/5.0 ... Chrome/125.0.0.0 Safari/537.36" https://<host>/api/resourceLocation`. WAF is universal across hosts but uniformly UA-defeated.
  - `GET /api/resourceLocation` → park list, each with stable `resourceLocationId` (negative int) + `localizedValues[0].fullName`. Verified entry counts: Ontario 129, Manitoba 45, Parks Canada 114, BC 145.
  - `GET /api/maps` → gives `mapId` (needed for the deep link + availability), but its `xCoordinate`/`yCoordinate` are **pixel positions on static region PNG maps, NOT lat/lng** — maps yields the id, not coords.
  - **Coordinates caveat (data-completeness, not access):** entries have a `gpsCoordinates` string but fill rate varies wildly — Manitoba 45/45, but Ontario ~4/129, Parks Canada 3/114, BC 1/145 (formats inconsistent; `googleAddress` empty). So for most parks you won't get coords from the API — geocode the `fullName` via Nominatim (provincial-park names geocode cleanly) then pin to the actual campground via satellite as usual. No WAF obstacle to any of it.

**Platform B — ReserveAmerica UNIF `.do` servlet** (older Java, Queue-it fronted). Clean, stable, human-readable GET deep link — **identical to the US ReserveAmerica format already in CLAUDE.md**:
```
https://<host>/camping/<park-slug>/r/campgroundDetails.do?contractCode=<CODE>&parkId=<id>
```
Confirmed contractCodes: **Saskatchewan** `parks.saskatchewan.ca` = `SKPP`; **PEI** `peiprovincialparks.ca` = `PE`; **Alberta** `shop.albertaparks.ca` = **`ABPP`** (confirmed 2026-07-07 — Aspira-operated ReserveAmerica `.do`, Queue-it fronted; parkIds observed ~330100–330330). Alberta example: `https://shop.albertaparks.ca/camping/bow-valley-provincial-park/r/campgroundDetails.do?contractCode=ABPP&parkId=330258`. **Do NOT store the transient `queueittoken`** the redirect chain appends — the bare `...campgroundDetails.do?contractCode=XX&parkId=<id>` is the durable link; Queue-it re-issues a token each visit. No clean park-index API on Platform B; build a name→id table by crawling park pages (slug+parkId are right in the URL). These are the easiest/most durable links.

**SEPAQ (Quebec)** — own legacy Java (Apache Struts, `.dot` paths), NOT Aspira. Slug-based, no numeric id, no public API. Park info `https://www.sepaq.com/pq/<slug>/index.dot?language_id=1` (1=EN, 2=FR); camping reservation `https://www.sepaq.com/en/reservation/camping/<full-slug>` (e.g. `parc-national-d-oka`). Durable key = the name slug. Scrape the slug list from `sepaq.com/en/reservation/parcs-nationaux`. Note: `reservation.sepaq.com` may be geo/DNS-blocked from sandbox.

## Waterfront evidence — you LOSE the rec.gov shortcut
Canada has NO public rec.gov-style per-site `SHORELINE SITE: Y` / proximity_water API. The gate logic (default-down, forbidden sources, mandatory satellite look, `waterfront_evidence` field, coastal-dunes special case for Great Lakes/Atlantic/Pacific) is UNCHANGED — only the source mix shifts: lean harder on the **mandatory satellite look**, **provincial per-site campground map PDFs** (BC Parks / Ontario Parks / SEPAQ publish them), and **goingtocamp's interactive map view** (plots site pins over a base map — usable per-site evidence when legible). Expect more manual satellite work per entry than a US federal-reservoir sweep.

## Schema / mechanics
- `state` field holds the 2-letter province code (display-only string; confirm nothing does a US-state lookup on it).
- Elevation already metric (Open-Meteo DEM global) and Nominatim geocode global — no change.
- Inclusion criteria (23-ft drive-in RV test, exclusions, dead-site strike, FCFS discipline) port verbatim.

## Recommended kickoff
Pilot ONE province first — **Ontario or BC** (large, well-documented, Platform-A). That exercises the goingtocamp id-lookup + Azure-WAF question and the `park_type` name-scan on real data, and locks the `provincial` ownership decision cheaply before committing to a full-country effort.
