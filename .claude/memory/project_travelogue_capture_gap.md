---
name: project_travelogue_capture_gap
description: The app is a superb logbook but almost no one writes in it (3% caption coverage); AWH can't write on the road, so capture must be voice + machine drafts, not text boxes
metadata:
  type: project
---

Measured 2026-09-09: the app records trips beautifully and contains almost no
human writing. **1,116 events → 37 descriptions (3.3%). 172 campspots → 11
notes (6.4%). 1,718 photos → 51 captions (3.0%). 3 favorites, ever.** Meanwhile
747 of those 1,116 events are machine-detected waypoints. The timeline is
mostly rows the computer wrote.

**AWH's constraint, in his words (2026-09-09) — this is the design input, not a
motivation problem:** "I rarely have the desire to write up a day report at the
end of a long day, partly because I'm tired, partly because I don't have a
decent keyboard and display with me, partly because I often have no signal.
After the trip I've forgotten things, back at work, other things to do. Just
uploading the pics is hard enough."

**So: never ship a feature that asks him to type prose on the road.** A blank
day-entry box was proposed and correctly rejected — it demands the scarcest
resource at the worst moment. The agreed split instead:

- **The machine supplies facts** — mileage, driving time, stops with dwell
  durations, campground name/elevation/waterfront, photo times, face counts.
  It already knows all of it and still will in five years.
- **AWH supplies meaning only, in the cheapest possible form.**

Agreed direction, in build order:

1. **Waypoint collapse — DONE 2026-09-09** (committed; see CLAUDE.md "Folded
   waypoint runs"). Removes work rather than adding it: 347 timeline rows gone.
2. **Voice memo ingest — steps 1 (capture + filing) and 2 (local Whisper
   transcription) SHIPPED 2026-09-09**; only the rollup step remains. See CLAUDE.md "Voice Memos
   (Contributor)". Design doc:
   https://claude.ai/code/artifact/eff04982-ac31-45d9-b696-2640d9a2ef97
   The unlock it was built for: Talking works tired,
   in the dark, one-handed, with no signal and no keyboard. iPhone Voice Memos
   needs no app written. **The differentiator nobody else has: a memo's
   timestamp × the OwnTracks track = exact coordinates = exact trip/day/card,
   so it files itself** (`_visit_windows_at` already answers this question).
   Transcribe at home with local faster-whisper / whisper.cpp — the Claude API
   has no audio input, and a local model is free, offline and private. Keep the
   audio regardless: AWH's recorded voice at a campsite beats any paragraph.
3. **Machine day-drafts, human edits — NEXT.** The input is now real: memo
   transcripts, filed to the day, alongside the structured facts. Editing beats writing-from-blank when
   tired, and works months later because GPS facts don't decay. Estimated
   **~$12 for all 331 trip-days** (claude-opus-5 + thumbnails), ~$9 for all
   1,718 photo captions; halve both via the Batch API.
4. **Comments from share-link readers** — 6 share links, 3 users, zero feedback
   channel. Cheapest feature with the biggest behavioral effect.

**Hard rule for 2 and 3: generated text NEVER writes into `captions.json` or a
`notes` field.** It goes to a separate store (`day_drafts.json`,
`photo_captions_auto.json`) rendered grey with one-tap Accept — the same
generated-vs-human distinction `waterfront_evidence` already enforces on
campground data. A bad batch run must be deletable, not restore-from-backup.

Also true and worth remembering: **the GUI is not the problem.** A browser pass
at desktop and phone widths found it genuinely good-looking. Real nits found:
the trip map opens at continental zoom instead of fitting the trip; on a phone
the map eats ~55% of the first screen; `/trips/photos` isn't in the nav at all
and highlights "Stats" when you're on it. See [[project_ux_review_2026_07]].
