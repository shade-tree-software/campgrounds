---
name: project_road_photos
description: "On-the-road photo cards — shipped 2026-09-10; keyed by date, one card per leg, positioned from EXIF against the GPS track"
metadata: 
  node_type: memory
  type: project
  originSessionId: 81727cea-100e-42b3-9840-f0096b68cbc2
  modified: 2026-09-10T21:20:25.866Z
---

Donna photographs constantly from the moving RV and those photos had nowhere to
go: every photo in the app hangs off a campspot or an event, and both are places
you STOPPED. Shipped 2026-09-10. Full detail is in CLAUDE.md; this records the
decisions a future session would otherwise re-litigate.

**Keyed by DATE, not position.** `photo_uploads/{trip}/road/{YYYY-MM-DD}/`. The
rest of the library is keyed by index, so inserting an item mid-trip renumbers
every directory above it — the machinery that broke silently library-wide and
needed `repair_photo_metadata.py`. A date never renumbers, so road cards sit
outside that path entirely and need no record in trips.json at all: uploading to
a day creates the card, emptying it removes it.

**One card per LEG, not per day** — a card covers the driving between two
consecutive stops, split using the timeline's own breaks. A day can cover 400
miles, so one card per day put a Colorado mountain photo and a Kansas plains
photo in one grid under one heading.

**A photo's day comes from its EXIF, not from the card it was dropped on.**
Fourteen placeholders are visible during a drag; hitting the wrong one is easy.
`repair_road_days.py` fixes any filed before that rule.

**Position comes from EXIF time matched against the GPS track**, and the zone is
resolved by CONVERGENCE — read the clock in the best zone known, find the
nearest ping, ask what zone that place is in, repeat. `strptime().timestamp()`
reads a naive time in the SERVER's zone, which is never right: PA runs UTC, the
photos were Mountain, and every lookup landed six hours early. **A timezone bug
cannot be caught by a test that runs in one machine's timezone** — my local box
being Eastern made the error two hours instead of six and the wrong answer
looked plausible.

**Road cards alone opt into `nearest_town`'s wider last-resort radius.** A road
card has no name of its own and the distance is the information ("16 miles
northeast of Deer Trail"); an overlook names itself, so it keeps the strict rule
and its silence. Both answers are stored per coordinate; the caller chooses.

## Where a screenshot beat a render check

Counting classes in the HTML proved the CSS was APPLIED and said nothing about
whether it took EFFECT. `.event-card.wp-compact .event-header` lost on source
order to `.event-card.bare .event-header` at equal specificity, so compact rows
rendered at full card height and the only visible change was the type size. One
screenshot showed it instantly. **After a visual change, ask for one.** See
[[feedback_responsive_all_screens]].
