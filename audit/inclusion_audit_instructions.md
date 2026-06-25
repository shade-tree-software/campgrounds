# Campground inclusion audit — agent instructions

You are auditing whether each entry in a personal campground database is a **real, currently-operating, drive-in RV campground** that belongs in the database at all. This is SEPARATE from the waterfront audit (that one only checks the `waterfront` value). Your job is to verify the **inclusion criteria** and return a keep / remove / review verdict per entry.

Your batch file (path given in your prompt) is a JSON array: `{id, name, location: "lat,lng", ownership, state, website, note}`. Audit every entry and return a structured verdict for each.

## The standard (the database's inclusion criteria)

An entry BELONGS only if it is **a real, publicly-bookable (or genuinely FCFS public), currently-operating, drive-in RV campground usable by a 23-ft RV** — i.e. at least some drive-in sites a 23-ft rig can use, reachable by a normal vehicle (decent dirt/gravel OK; hardcore offroad / 4WD-required disqualifies). Hookups are NOT required; a grass pad is fine.

**REMOVE (does not belong)** if the entry is actually any of these:
- **Cabins-only / cottages-only** — no tent/RV campsites (e.g. a state park whose only overnight option is modern cabins). Watch for parks where aggregators invent "RV sites" that are really the cabin loop.
- **Tent-only** — campground exists but RVs/trailers are not permitted, OR all sites are walk-in/hike-in/cart-in tent sites.
- **Hike-in / boat-in / paddle-in / float-camp only** — no drive-in access to the sites.
- **Group-only / organized-group / youth-camp / scout / religious-retreat only** — not individually bookable transient sites.
- **Equestrian-only** (a general campground that merely *offers* horse sites is fine; an equestrian-only horse camp is not).
- **Day-use only** — picnic pavilions / boat launch / beach with NO overnight camping at all. (Common failure: a small state park that is day-use, with camping actually at an adjacent park.)
- **Fairground / event-lot** that allows camping ONLY during events.
- **Membership / club / sales-pitch park** (Thousand Trails, Encore, Bluegreen, Coast-to-Coast; Elks/Moose/Airstream-club lodges; timeshare buy-in).
- **Not a real transient campground** — mostly seasonal/full-timer, residential / mobile-home park, or workforce/long-term housing; casino/racetrack overnight lot.
- **Closed / defunct** — permanently closed, or no evidence it currently operates (dead official website + thin/no reviews is a strike toward removal).
- **Max RV length caps under ~23 ft** at every drive-in site (e.g. a forest campground whose largest sites fit only 20 ft), barring a genuinely special case.
- **Duplicate** of another entry (same campground, different name) — flag as remove with the surviving id named.

**KEEP** if you confirm it is a genuine drive-in RV campground fitting a 23-ft rig (even small, even FCFS, even water/electric-only or no hookups). Dispersed drive-in sites and single drive-in forest campsites (state-forest motorized/roadside sites) KEEP as long as a normal vehicle can reach them and a 23-ft rig can occupy at least one — these are legitimately primitive, not a reason to remove.

**REVIEW** (don't force a call) if you genuinely cannot determine status from available sources — e.g. ambiguous between tent-only and RV-capable, or can't confirm it currently operates. Say exactly what's missing.

## Evidence discipline
- **Authoritative sources win:** the operator's / agency's own page (state-park "Stay"/camping page, county/city parks page, the campground's own domain), the reservation system (ReserveAmerica / recreation.gov / Campspot per-site list showing the actual site types), an official campground map. For PA state parks the DCNR park "Stay the Night" page and the ReserveAmerica `campgroundDetails` site-type list are primary.
- **Aggregators lie by inflation:** snoflo, camperalerts, campscanner, camping.org, thedyrt summaries, etc. routinely list "RV sites" for cabin-only or day-use parks (they conflate cabins or copy boilerplate). NEVER conclude "keep / has RV sites" from an aggregator alone — confirm the site types from the operator or the reservation system. When an aggregator conflicts with the operator, the operator wins.
- A real per-site reservation listing that shows tent/RV sites (not just "Modern Cabin Area") is strong KEEP evidence. A reservation system that shows ONLY a cabin loop (or only pavilions / day-use) is strong REMOVE evidence.
- Use the satellite look as a cross-check when useful (a campground loop with parked RVs supports keep; only cabins-in-a-clearing or a picnic-lot supports remove), but the site-type authority is primary — don't keep or remove on satellite alone when the operator page is decisive.

## Tools
- Web verification is the core of this audit. Load `WebFetch` and `WebSearch` via ToolSearch (`select:WebFetch,WebSearch`) and use them freely.
- Optional satellite cross-check (GET; curl works):
  `curl -s "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=<lng-d>,<lat-d>,<lng+d>,<lat+d>&bboxSR=4326&size=1000,1000&format=jpg&f=image" -o /tmp/inc_<id>.jpg` with d=0.0035, then **Read** the jpg.

## Workflow per entry
1. Identify the campground from `name` + `location` + `website`. Pull the operator/agency page and the reservation-system site list to learn the actual overnight inventory (cabins? tents? RV sites? day-use only?).
2. Apply the standard above. Decide `verdict`: `keep` | `remove` | `review`.
3. Write a one-line `evidence` string **naming the authoritative source and what it said**, e.g. `DCNR Stay page: 'park does not have a campground', 8 modern cabins only -> cabins-only` / `ReserveAmerica site list: Loops A-C tent+RV W/E sites 1-43 -> real RV campground` / `operator site: 14 tent-only sites, RVs not permitted`.
4. For `remove`, set `reason` to the single best category from the REMOVE list (e.g. `cabins-only`, `tent-only`, `day-use-only`, `hike-in`, `closed`, `membership`, `residential-seasonal`, `equestrian-only`, `under-23ft`, `duplicate`). For `keep`/`review`, `reason` may be "".

## Output
Do NOT edit any files in the repository. Your final message must be ONLY a JSON array (no prose, no code fences), one object per entry, same order as the batch:
```
{"id": <int>, "name": "<name>", "verdict": "keep" | "remove" | "review", "reason": "<category or ''>", "evidence": "<one line naming the source>", "confidence": "high" | "low"}
```
Every object must have a non-empty `evidence` string. Default to `review` (not a guess) when you cannot confirm from an authoritative source.
