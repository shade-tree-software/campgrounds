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

`process_rollups.py` and the day-divider display on the trip page. Every
unedited write-up carries "Drafted by <model>".

## The memo capability was REMOVED ENTIRELY (2026-09-11)

`/memos`, the API routes, `process_memos.py`, local Whisper transcription,
`memo_uploads/`, `trip_data/memos.json`, the nav entry and the sixth phone tab
— all gone, along with the two memos that existed. AWH: "It was added to give
the long-format rollups something to work with, and possibly to allow recording
a memo with no internet signal; but no internet signal also means no web app
unless the SD card version is around, which we cannot depend on."

**Don't rebuild it on the offline argument.** The service worker *could* serve
a previously-visited `/memos` and IndexedDB *would* queue the recording, so the
offline path was not strictly impossible — but pages are network-first, so it
only works if you happened to visit first, and that is a thin thread to hang a
feature on. The real reason it went is that the thing it fed was rejected.

What survived because it was always shared, not memo-specific:
`_BackgroundScan` (now behind the people scan and the place resolver),
`trips.camper_names()` (used by `_make_trip` for `trip["campers"]`), and the
`--force`/`edited` discipline the transcripts and the rollups both used.

## DONE: all 321 days written, deployed 2026-09-11

Every day of all 90 non-home trips has a short write-up, **written by hand in
conversation at no API cost**, and both `day_rollups.json` and `trips.json` are
uploaded to PA and verified identical by checksum. An earlier API run (~$1.85,
303 days) is entirely superseded.

**The short form replaced the long rollups.** AWH on the rollups: "they
basically repeat what anyone can read later on in the timeline for that day" —
structurally true, because the dossier was assembled FROM the cards printed
below the write-up. The approved form is impersonal, names what happened, and
leads a local day with what it was for rather than its mileage.

### The rules, each earned by a correction

Every one of these is in `process_rollups.py`'s SYSTEM prompt. They are listed
here because the reasoning is not recoverable from the rule text alone:

- **Length is a CEILING (45), never a target.** Every floor I set rejected text
  AWH had already approved — 25 rejected his own 24-word entries, 22 rejected
  "North for the new year...", 8 rejected "Fireworks at Franklin Park in
  Purcellville" as he called it good. Padding to reach a floor is exactly what
  produced "with nothing else on the day".
- **Never remark on what the record holds.** No "the only thing recorded",
  "nothing but the drive". Commentary about the archive, and it makes a thin day
  conspicuous instead of letting it be brief. 17 of my first 147 were guilty.
- **Never gloss a small distance OR its absence.** Not "barely out of town",
  not "no need to move the camper at all". AWH: "'Fireworks at Franklin Park in
  Purcellville' is good. 'barely out of town' is unnecessary."
- **A round_trip day carries NO distance at all** — the dossier withholds it
  rather than the prompt forbidding it. "Mileage is interesting on a 502 mile
  day, not on a day when miles just incidentally happened to add up due to a lot
  of local activities." The test is achievement vs by-product; round_trip is the
  proxy.
- **Waypoints are absent entirely, not even counted.** "If a stop is
  interesting, it's my job to mark it as an event rather than a waypoint, not
  the model's job to reinterpret." A count can only be characterised by guessing
  what was at them.
- **Names yes, descriptions no.** Events, family visits and campgrounds are
  named; their descriptions, captions, notes, site numbers and photo counts are
  not. Withholding names is what left a local day with nothing but mileage.
- **Events carry `time`/`until`, and the drive carries `left_at`/`arrived_at`.**
  Without them a single event reads as filling the day. AWH on trip 14's Ocean
  City (19:30-20:47): "We didn't spend the day in Ocean City."
- **THEY TRAVEL IN THE CAMPER AND NOTHING ELSE.** No second car; any local drive
  was in the camper. Never write it as though the camper stayed on the pitch.
- **Nothing is immune to redrafting.** `source: "conversation"` is provenance,
  not protection — freezing hand-written text would leave a library that cannot
  respond to its own facts being corrected. `day_notes` are the human channel
  and need no protection, since they outrank at display time.

### Two open items, AWH intends to address them next time

1. **Day one of any trip has no `heading`** — `_heading` needs both ends and
   home is not a campspot, so the drafter can never say which way a trip set
   off.
2. **The waypoint/event split is now the main lever on quality.** A report found
   135 of 747 waypoints carry a signal; **26 in tiers A/B carry photos or a
   description**, which is the app's OWN test for earning a full timeline card —
   so the page already treats them as interesting while the write-up cannot see
   them. Regenerate that report with a scan over `timeline` items where
   `waypoint` is true and the card has photos or a description.

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
- **`ANTHROPIC_API_KEY` is COMMENTED OUT in this machine's `.env`** (line 8,
  `#export ANTHROPIC_API_KEY=...`) and live on PA. To use it here without
  editing the file: `export ANTHROPIC_API_KEY="$(sed -n '8s/^#\s*export\s*ANTHROPIC_API_KEY=//p' .env)"`.
  `.env` is gitignored and excluded from `backup.sh`, so each host has its own.
  Anthropic keys do not expire on a timer, and when one fails the WEBSITE is
  unaffected — the app never imports `anthropic`.
- **`trip_data/day_rollups.json` exists only on the host that generated it.**
  Gitignored, excluded from sync (a `--delete` sync deleted a whole trip's prose
  before that exclude existed), now in `backup.sh`. On a new machine it does not
  exist — regenerate, or move it with `backup.sh`/`restore.sh`.
- `trip_data/place_context.json` likewise, but it regenerates free from the
  committed `places.tsv.gz`: `python backfill_place_context.py --apply`.
- A new machine needs its own PA SSH keys ([[reference_pa_ssh_keys]]), a `.env`
  with `GITHUB_PAT`, and `git config core.askPass`.
