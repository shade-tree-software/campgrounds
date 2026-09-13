---
name: feedback_dont_open_with_away
description: AWH dislikes day rollups opening with a bare "Away <time of day>"; his own notes drop the departure and let the direction be the verb
metadata:
  type: feedback
---

AWH, 2026-09-13, on `Thanksgiving: away first thing and 183 miles northeast to
the Svendsens'` — "I don't like the frequent use of the word 'away'."

It is the drafter's tic, not his voice: **`Away <time of day> and <N> miles
<direction>` opened 84 of 327 entries** (93 use the word at all), so every day
it fronted read as the same day. His own 45 day notes use it three times, two of
those on days where he kept the draft sentence unchanged.

**Why:** a bare "away mid-morning" spends words on nothing — it is the same
fault as putting an hour on an arrival. The departure time is only worth
keeping when something concrete hangs off it ("Away mid-morning under light
snow"); `away from <place>` is a different phrase and is fine.

**How to apply:** of the 10 days where he wrote a note over an "Away" draft, he
replaced it four ways, all now in `process_rollups.py`'s `SYSTEM` (under the
`left_at`/`arrived_at` rule):

1. **Let the direction be the verb and drop the departure entirely** — draft
   `Northeast 188 miles to the Svendsens', away after midday.` → note
   `Northeast 188 miles to the Svendsens'`. Also `South 409 miles to Sexton
   Pond`, `Northwest 299 miles to Grove City`.
2. **Name the drive as a thing** — `An evening drive after work`, `a 24-mile hop
   down to Pohick Bay`, `the last leg`. Note he also moves "after work" to the
   END rather than opening with it.
3. **A phrase with a body in it** — `Back on the road before midday`, `Headed
   out after work`, `and then on to home`.
4. **Morning first, then the drive** — `One last run in the kayaks, then the
   last leg, 207 miles north for home`.

**When the morning held nothing, the direction and the distance are the whole
opening.** Same family of correction as
[[feedback_drive_figures_time_vs_miles]] and [[feedback_summaries_say_less]];
found the same way, by diffing notes against the drafts they replaced
([[project_rollup_examples_from_notes]]).
