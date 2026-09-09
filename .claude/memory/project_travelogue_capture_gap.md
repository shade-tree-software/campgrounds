---
name: project_travelogue_capture_gap
description: Memo-to-rollup pipeline — why it exists, steps 1-3 shipped 2026-09-09, what's left (display + judging the prose + running the archive)
metadata:
  type: project
---

Measured 2026-09-09: the app records trips beautifully and contained almost no
human writing. **1,116 events → 37 descriptions (3.3%). 172 campspots → 11
notes (6.4%). 1,718 photos → 51 captions (3.0%). 3 favorites, ever.** Meanwhile
747 of those 1,116 events are machine-detected waypoints.

**AWH's constraint, in his words (2026-09-09) — the design input, not a
motivation problem:** "I rarely have the desire to write up a day report at the
end of a long day, partly because I'm tired, partly because I don't have a
decent keyboard and display with me, partly because I often have no signal.
After the trip I've forgotten things, back at work, other things to do. Just
uploading the pics is hard enough."

**So: never ship a feature that asks him to type prose on the road.** A blank
day-entry box was proposed and correctly rejected. The split instead: the
machine supplies facts (it already knows them and still will in five years),
AWH supplies meaning only, in the cheapest possible form. Design doc (artifact):
"Memo to Rollup" — https://claude.ai/code/artifact/eff04982-ac31-45d9-b696-2640d9a2ef97

## Shipped 2026-09-09 (all deployed to PA)

- **Waypoint collapse** — 663 of 747 waypoints fold into "N brief stops" chips.
- **Step 1: memo capture + filing** — `/memos`, MediaRecorder in the PWA,
  IndexedDB queue, filed against the GPS track. 285/285 real pings file to the
  trip that owns their day.
- **Step 2: local Whisper transcription** — `process_memos.py`, auto-triggered
  on upload, plus a read-path catch-up sweep (`queue_once`).
- **`speaker` field** — who talked, from `campers` not `users.json`.
- **Step 3 generator: `process_rollups.py`** — see below.
- Requirements split (`ekko_trips_requirements.txt` vs `tools_requirements.txt`)
  and the map fractional-zoom fix. All detail is in CLAUDE.md.

## Where step 3 stands — RESUME HERE

Generator works and trip 95 is drafted (14 days, in the gitignored
`trip_data/day_rollups.json`). Three things left:

1. **AWH has not yet read the prose.** That was the whole point of doing one
   trip first — the judgement is his, not mine. `--force --trip 95` redraws for
   $0.15 if the prompt needs another turn.
2. **Nothing displays rollups yet.** The trip page's day divider is where they
   belong, beside the mileage chip. This is the natural last commit of step 3.
3. **The archive has not been run.** ~321 days ≈ **$3.50** (measured, not
   estimated — far under the $12 in the design doc).

**Verified: no fabrication, on the first attempt.** Audit method worth reusing —
take every evaluative-sounding phrase and trace it back. "A nice overlook of the
Swanson Reservoir", "an unexpected outdoor church service" and "gas in
Benkelman" were all verbatim from event descriptions or a photographed waypoint.
What DID go wrong was reciting the archive (all 14 days stated a photo count,
four ended in a roll call of who was there); fixed in the system prompt — photo
counts are now a signal for choosing what to write about, never something to
state.

**AWH's decision (2026-09-09):** a day with **no memos still gets an entry**,
written from facts alone. Memos improve a day, they don't gate it. That is what
lets the whole back catalogue be covered before a single new memo exists.

## Environment facts that aren't in the repo

- **`ANTHROPIC_API_KEY` is in the LOCAL `.env` only** (added by AWH 2026-09-09,
  `sk-ant-api03-…`). `.env` is gitignored, so **PA does not have it** — if
  rollups should ever run there, the key has to be added separately.
- `faster-whisper` and `anthropic` are installed in the local
  `ekko_trips_venv`; PA has the tools requirements installed in its own venv.
- Installing faster-whisper bumped `click` 8.3.1 → 8.5.0; the pin was updated
  because huggingface_hub requires >=8.4.2.

## Still not built, from the original review

- **Reader comments** — 6 share links, 3 users, no feedback channel. Still the
  cheapest thing with the biggest effect on whether AWH keeps feeding the app.
- Photo captions on the ~907 face-flagged shortlist (~$9 batched).
- `campers` is still free text, so "every trip Chris came on" is unanswerable —
  but `trips.camper_names()` is now the shared normalizer, so the parsing half
  is done.
- **The memo feature has never met a real campsite.** Zero real memos exist. A
  single overnight would test mic permission, no signal, and the button in the
  dark better than any further building. See [[project_ux_review_2026_07]].
