---
name: campgrounds-only-role
description: "Campgrounds only" user type BUILT 2026-11-07 — map only, default-deny allowlist; climate mode dropped (home-relative); docs in CLAUDE.md Roles
metadata:
  type: project
---

Built 2026-11-07 at AWH's request: an account or share link flagged `campgrounds_only` sees
only the campground map, with nothing of the family (no trips, stats, photos, family/home
markers, visit lists, header counts or "EKKOing Around"/"Hamilton" branding, no Availability
or Weather). Rules and mechanics are in CLAUDE.md under Roles; the test is
tests/test_campgrounds_only.py.

Decisions: neutral name "Campgrounds"; share links can carry it; the `--AWH` sign-offs and
"per AWH's firsthand report" lines stay (AWH reviewed their notes, personal bits removed);
Climate colour mode is withheld because it is graded against home's lat/alt. Not done: the
app icon (static/icons) and the logged-out login page are unchanged, and JS identifiers like
`EKKO_TILES` remain in page source.

**How to apply:** any new page/API a campgrounds-only viewer should reach must be added to
`CAMPGROUNDS_ONLY_ENDPOINTS` and scrubbed; any new map/popup field derived from trips, home
or family goes in the `_FAMILY_ONLY_*` sets. Keep notes impersonal ([[feedback-notes-name-no-one]]).
