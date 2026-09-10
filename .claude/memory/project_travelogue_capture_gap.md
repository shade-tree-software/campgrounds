---
name: project_travelogue_capture_gap
description: Memo-to-rollup pipeline — steps 1-3 shipped and displayed; RESUME at judging trip 95's prose after the seam-rule rework, then the archive run
metadata:
  type: project
---

Measured 2026-09-09: the app records trips beautifully and contained almost no
human writing. **1,116 events → 37 descriptions (3.3%). 172 campspots → 11
notes. 1,718 photos → 51 captions.** AWH's constraint, in his words: "I rarely
have the desire to write up a day report at the end of a long day... Just
uploading the pics is hard enough." So: **never ship a feature that asks him to
type prose on the road.** The machine supplies facts; he supplies meaning in the
cheapest possible form. Design doc (artifact): "Memo to Rollup" —
https://claude.ai/code/artifact/eff04982-ac31-45d9-b696-2640d9a2ef97

That worked. By 2026-09-10 trip 95 had 33 event descriptions, 4 campspot notes
and 20 captions — he writes when the writing has somewhere to go.

## Shipped

Steps 1-3 plus display: `/memos` capture (voice AND typed — see
[[feedback_waypoints_are_orientation]] for the sibling reversal), GPS filing,
local Whisper transcription, `process_rollups.py`, and the day-divider display
on the trip page. Every unedited write-up carries "Drafted by <model>", the same
generated-vs-human line the memo page draws.

## RESUME HERE

1. **AWH has not judged the current prose.** He critiqued the 2026-09-10 run in
   nine specific places and the fixes are committed but NOT yet exercised —
   `--force --trip 95` costs ~$0.21. Verify against his nine before anything else.
2. **The archive is on hold at his request** (~321 days, ~$3.50-5). Do not run
   it until he approves the trip-95 output.
3. **Open design question he asked, unanswered:** each day is a separate API
   call with no knowledge of the other thirteen, which loses the trip's arc and
   repeats material across consecutive days. He said "there's a reason and a
   theme on most trips, and some of that develops throughout." Proposal to put
   to him: a factual trip-arc block in every dossier (day N of M, where it began
   and ends, the shape of the days) plus the previous day's finished text for
   continuity — NOT one call for the whole trip, which trades away the guard
   that a day cannot borrow another day's facts. **Gap found while checking:
   there is nowhere to record a trip's reason or theme.** `trip_note` exists on
   93 of 95 trips but is just the trip's name ("Rocky Mountain National Park").

## The lesson worth keeping from the nine faults

They were one fault. The model was not fabricating whole facts — it was
inventing the CONNECTIVE TISSUE that makes sentences flow, which is exactly what
a dossier lacks: where something happened relative to something else, why a stop
ran long, the mood of a day, whose idea something was, what a stop was for.
"We talked briefly to a group of men on Harleys" became "at the top we talked to
them"; they were in the car park. Four of the nine came from captions, which are
**labels on a photograph the model cannot see** — "Not in service" was an
abandoned phone booth, not the town. See rules 2 and 14 in `SYSTEM`.

## Environment facts that do not travel with the repo

- **`ANTHROPIC_API_KEY` is in the LOCAL `.env` only.** PA does not have it and
  cannot generate rollups.
- **`trip_data/day_rollups.json` exists only on the host that generated it.**
  Gitignored, excluded from sync (a `--delete` sync deleted a whole trip's prose
  before that exclude existed), now in `backup.sh`. On a new machine it does not
  exist — regenerate, or move it with `backup.sh`/`restore.sh`.
- `trip_data/place_context.json` likewise, but it regenerates free from the
  committed `places.tsv.gz`: `python backfill_place_context.py --apply`.
- A new machine needs its own PA SSH keys ([[reference_pa_ssh_keys]]), a `.env`
  with `GITHUB_PAT`, and `git config core.askPass`.
