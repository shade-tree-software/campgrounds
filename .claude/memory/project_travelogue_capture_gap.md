---
name: project_travelogue_capture_gap
description: Memo-to-rollup pipeline — AWH judged the drafts redundant with the timeline 2026-09-10; a typed day note now owns that slot and the archive run is off
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

## Where it landed (2026-09-10)

Trip 95 was re-drafted after the join-invention fixes (14 days, $0.22, no
truncation) and AWH's verdict on the prose was **not that it was wrong — that
it was redundant**: "The rollups are OK, but they basically repeat what anyone
can read later on in the timeline for that day. If we simply add a new option
to add a visible note for each day, it will probably be just as nice without
the need to make API calls to an AI." He is right and it is the diagnosis the
whole project needed: the dossier is assembled FROM the cards printed directly
below the write-up, so faithful prose is by construction a restatement. The
model can only add what it is not allowed to add.

**So the day note now owns that slot** (`day_notes` on the trip record; a typed
note always beats a draft — see CLAUDE.md "The Day's Write-Up"). This is
consistent with the capture-gap finding rather than a contradiction of it: he
won't write a day REPORT, but he writes a sentence when it has somewhere to go
(33 event descriptions on trip 95).

**The generated half is not deleted, just demoted**, and two questions are open:
1. **Retire the drafts or keep them as a fallback?** Trip 95's 14 still display
   on days he hasn't written over. Ask before deleting `day_rollups.json` —
   unwritten days are the only case they were ever the better answer.
2. **The archive run (~321 days, ~$3.50-5) is OFF** unless he revives it. Its
   one real argument survives his verdict: he will never hand-write 321 days of
   back-catalogue, and there the restatement is of cards a reader would
   otherwise have to assemble themselves.

Still unanswered from before, and now probably moot: each day was a separate API
call with no knowledge of the other thirteen, losing the trip's arc — and there
is nowhere to record a trip's reason or theme (`trip_note` is just the name).

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

- **This laptop has NO `ekko_trips_venv/`** despite every doc naming it; the
  interpreter that has the app's dependencies is `~/.virtualenvs/ekko/bin/python3`
  (the same split `_people_scan_python()` probes for). `anthropic` was installed
  there 2026-09-10 to run the rollups. A `source ekko_trips_venv/bin/activate`
  fails silently and leaves you on system python, which has none of it.
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
