---
name: campgrounds-only-role
description: Planned "Campgrounds only" user type (AWH 2026-11-07) — sees only the campground map; no trips, stats, family, home, banner, Availability or Weather
metadata:
  type: project
---

AWH asked 2026-11-07 for a user type that sees ONLY the campgrounds map and no personal
family data: no trips, no trip stats, no family homes, no home location, not even the
"Hamilton family road trips" banner. Not built yet (estimate given: ~1 day, 400-700 lines).

Decided so far:
- **No Availability page and no Weather Finder** for this role (AWH 2026-11-07), so the
  allowlist is the campground map + its popup/marker data, tiles, geocode, logout.
- Year-round/part-open is not personal; the `--AWH` note question is open: AWH is reviewing
  a generated list (588 entries with their own `--AWH` prose, 123 that only mention AWH;
  none first person, 4 mention EKKO/"camped"). Builder: scratchpad `awh/build.py`.

Planned design: default-deny allowlist in `_require_login_globally` for the role (new routes
refused by default), plus server-side scrubbing of base.html (subtitle, og text, counts, nav),
the map (HOME, FAMILY, visit_count, popup trips list, route-tool home), family rows in
/api/campgrounds, ETag varied by role, manifest name, sw tile precache. Prove it with a
route-crawler test and a no-leak test. Related: [[app-is-private-family-only]], [[auth-model-decisions]].
