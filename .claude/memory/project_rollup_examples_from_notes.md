---
name: project_rollup_examples_from_notes
description: Day rollups now few-shot off AWH's own day_notes chosen per day by shape — writing a note IS how you correct the drafter; plus the two anchor bugs that caused the worst rewrites
metadata:
  type: project
---

2026-09-13. AWH asked what could be learned from the days where he had
overwritten a generated rollup with his own note. **39 such pairs existed**
(mean word-similarity 0.55; 23 of his notes were LONGER than the draft, so the
problem was never verbosity — the drafts said the wrong things).

## The mechanism that came out of it

`build_example_bank()` / `choose_examples()` in `process_rollups.py`: every
`day_notes` entry is paired with the dossier its day would be drafted from, and
the four closest in SHAPE (round-trip vs travel, mileage band by ratio,
first/last day, event count, family visit) ride in the user message ahead of
the day's own facts. The four hand-picked trip-95 exemplars that used to sit
frozen in `SYSTEM` are gone — one of them had already been superseded by
AWH's own note on that very day.

**So writing a note is now the way to correct the drafter**, with no prompt
edit and no redraft of anything else. That is the whole point: the examples
cannot go stale, and the correction arrives with its facts still attached.

## Two bugs, both anchors, both found by reading the rewrites

- **`day_clock` anchored on the day's first PING**, and OwnTracks suspends
  reporting while parked, so a day starting at home begins with the commute.
  Trip 90's 2026-06-05 reported "left 07:10, arrived 21:11" for a trip that
  actually left at 18:54 and drove two hours; the draft said "fourteen hours
  between leaving and arriving" and was the most-rewritten entry in the
  library. Now anchored on the BEDS (`day_anchors`: home.json on the first and
  last day).
- **No `heading` on any day that leaves or returns home** — `_heading` needs a
  stay at both ends. All three compass corrections AWH made were those days.
  Closes open item 1 of [[project_travelogue_capture_gap]].

## The homeward day had no divider (found 2026-09-13, same pass)

AWH: "a day that moves silently from a campground to home still has something
to say." It already did — **seven trips had a drafted summary of the drive home
that the page rendered nowhere**, because a stay's card sits on the night it
began, so the timeline loop ended on an earlier date and the home end card
landed under the wrong day's divider. Fixed in `trip_detail.html` with a
`day_divider()` macro emitted once more after the loop when
`trip.end > ns.last_date`. Days with no events were never the problem — 29 of
them had rollups already.

## The whole library was redrafted BY HAND, 2026-09-13

All 327 days rewritten in conversation at no API cost (AWH: "do the redraft
yourself rather than spending API credits ... we'll save those for the real
work once we're sure we've got everything ironed out"). Mean 16.7 words, max
33, zero lint violations. Method that made it tractable: dump every dossier to
JSON once (`--dry-run` equivalent), render it compact — one line per day plus
the trip's outline — then write ~20 days a batch through a stamping script that
lints each entry (word ceiling, first person, clock times, round-trip driving,
absent-mileage-as-zero) and stamps `inputs_sig` from the same dump, so the next
scheduled run sees nothing stale.

**`trip_data/day_rollups.json` is LOCAL-ONLY until it is pushed.**
`sync-from-pa.sh` PULLS it from PA and treats PA as authoritative, so running
that sync before uploading would overwrite all 327 with the old drafts.

## What else the 39 taught

Rules now in `SYSTEM`: clock order (an event before `left_at` is the morning at
the place the day started, and dropping it loses how the day began);
part-of-day anchors; `states` is an ordered CROSSING, so `["SC","GA"]` is
"through South Carolina and into Georgia"; place the day at most once and only
with something countable (never "the trip turns here from family visit to
touring"); "after work" for a weekday first day leaving after ~16:30 (AWH added
it to 4 of 4); 35-word hard ceiling. Figures: see
[[feedback_drive_figures_time_vs_miles]].

**Voice stays impersonal** though 5 of the 39 notes use "we" — AWH's call: the
notes are the human channel and a draft must stay visibly a different kind of
text.

**Terrain is allowed only where the dossier MEASURES it** (AWH's call, having
kept adding corridors like "through the Blue Ridge and into the Massanutten
Valley" by hand): `to.elevation_ft`, `high_point_ft` (DEM-sampled off the
track), `to.waterfront`/`to.water` and `to.within` (parsed from the campground
note), at most one per entry. The ban on everything else holds because the
model was already inventing geography and getting away with it — "Elizabeth
Furnace on Passage Creek" was correct and came from nowhere in the record.
