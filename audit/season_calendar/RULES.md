# Season pass: calendar-derived seasons vs the agency's stated season (AWH 2026-11-08)

`season` is when the campground is OPEN. 151 entries got their `opens`/`closes` from the
recreation.gov availability calendar (`recgov_calendar.py`), which only sees nights a site
can be RESERVED. Where a campground runs first-come either side of its booking window, the
calendar edge is the end of reservations, not the closing date: four were found wrong this
way (Devils Garden, Furnace Creek, Ackerman, Sunset Falls), and the Chequamegon loops whose
calendar "closes Sep 7" (Labor Day 2026) while their notes say open into October look the
same. AWH asked for every one to be checked against the agency's own stated season.

Schema rule (docs/campground-schema.md, "A reservation season is not a campground
season"): `season` = open; `booking.season` = when reservations are taken (same shape).

## Input
`in/NN.json`, 10 items: `id`, `name`, `state`, `ownership`, `website`, `recgov_facility`
(the recreation.gov facility id: https://www.recreation.gov/camping/campgrounds/<id>),
`season` (what the map shows now), `season_source`, `booking`, `note`.

## What to find, per item
The season the AGENCY states for this campground, from (in this order):
1. the agency's own page for it — for the Forest Service the `fs.usda.gov` recarea page in
   `website` (its "Open Season" / "Operational Hours" / "Area Status" lines); BLM, NPS,
   USACE likewise their own site;
2. the recreation.gov facility page's own text (Overview / Need to Know / "Season").
Fetch with WebFetch; if a site refuses it, try `curl -sL -A "Mozilla/5.0"` from Bash. Do not
use a browser, and do not work around a bot wall (403/captcha): record it and move on.
Aggregators (Campendium, RV Life, The Dyrt, hipcamp, campgroundviews, etc.) do NOT count.
The entry's own `note` does not count as a source either (it is what may be wrong).

## Verdicts
- `confirms` — the agency's season matches the chip (same month at each stated edge, or
  within ~10 days when the agency gives exact dates). Year-specific dates ("open May 22,
  2026") count as matching when the chip's MM-DD is within ~10 days.
- `differs` — the agency states a different open season. Give it in schema shape:
  `{"opens": "MM-DD", "closes": "MM-DD"}` or `{"year_round": true}`. A month-only edge:
  opens = the 1st, closes = the last day of that month ("May - October" → 05-01 / 10-31).
  An edge the agency does not state stays out (only `closes`, say). Holiday edges:
  Memorial Day → note it in `quote`, use `"05-25"`; Labor Day → `"09-07"`; also say
  "holiday-anchored" in `remark`. If the agency's season is wider than the chip and the
  campground has first-come sites or periods, the calendar span is the reservation window:
  set `calendar_is_booking_window: true`.
- `no_source` — no agency statement of the season found (or only a bot wall). Say what you
  tried in `remark`.
- `closed` — the agency lists it closed (fire, flood, construction) for now. Quote it.
  That is a `status`, not a season; still give the normal season if the page states one.

## Output
Write a JSON array to `out/NN.json`, one row per input item:
`{"id": N, "verdict": "...", "agency_season": {...} | null, "quote": "<exact words from the
page>", "url": "<the page>", "read": "2026-11-08", "calendar_is_booking_window": bool,
"remark": "<short, optional>"}`.
`quote` must be copied exactly from the page. No quote = `no_source`.
Do not edit campgrounds.json or any repo file other than your output file.
