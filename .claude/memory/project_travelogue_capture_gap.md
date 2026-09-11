---
name: project_travelogue_capture_gap
description: Day write-ups — AWH rejected the long rollups as redundant and APPROVED short per-day summaries (trip 95 done by hand in-session 2026-09-10); typed day notes own the slot; resuming on another machine
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

The long rollups are OUT and **short per-day summaries are IN**. AWH on the
rollups: "they basically repeat what anyone can read later on in the timeline
for that day" — and he was right for a structural reason, not a prose one: the
dossier is assembled FROM the cards printed directly below the write-up, so
faithful prose is a restatement by construction. The model could only add what
the rules forbid it to add.

What he asked for instead, and approved ("This is good. Much better than the big
rollups."): **a short summary telling a first-time reader the gist of the day,
deliberately NOT repeating the notes and captions**, which he can then add to by
hand. Trip 95's 14 days were written **by me in conversation, no API call**, from
the route/mileage/day-shape alone. Choices that earned the approval, keep them:

- **Impersonal voice, not "we"** — it reads as a subtitle standing over his own
  words rather than competing in the same voice, and keeps whose text is whose
  obvious at a glance.
- **The SHAPE of the day is the content**: distance, direction, terrain, what
  kind of day it was (haul / touring / moving day / the turn for home). That is
  exactly what the cards below cannot say and a first-time reader cannot
  assemble.
- **Name nothing the cards already name.** No Harleys, no Snake Alley, no
  Christmas tree in August. 24-41 words each, about a third of a rollup.

**If this is ever automated, the prompt is much cheaper than the rollup one:**
it needs the route, the mileage and the day's shape — NOT the descriptions and
captions, which were most of the dossier's cost and all of its redundancy.

## Two slots, one page (shipped 2026-09-10)

`day_notes` on the trip record + `_trip_day_writeups` — a typed note always beats
a generated write-up, editing a draft writes a note OVER it rather than editing
it, and the "Drafted by <model>" line keys on `model` so a note retires it. See
CLAUDE.md "The Day's Write-Up". `tests/test_day_notes.py`, 10 tests.

## RESUME ON THE OTHER MACHINE

**The trip-95 summaries are NOT in git** — they are in `trip_data/day_rollups.json`,
which is gitignored and excluded from the PA sync, and PA has never had them.
The code travels by git; the summaries travel only in the backup bundle made
2026-09-10 (`backup/ekko-backup-*.tar.gz`, `restore.sh` on the far side). Without
it the other machine shows a trip 95 with no write-ups at all.

Open, in his hands:
1. **Publishing them to PA.** There is no automated local->PA path (deploy key is
   a forced command, sync key is read-only), so either he re-types them on the
   live site or they ride a bundle. Note the natural workflow does it for him:
   editing a summary turns it into a day note in `trips.json`.
2. **The other 94 trips.** ~321 days. Doing them the way trip 95 was done is a
   conversation, not a script; automating it is the cheap-prompt note above.
3. `process_rollups.py` and its 17-rule SYSTEM prompt are now superseded but not
   deleted. Ask before removing them.

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
