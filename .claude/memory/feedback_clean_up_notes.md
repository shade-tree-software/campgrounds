---
name: feedback-clean-up-notes
description: "AWH 2026-10-13 standing rule: whenever I'm already reading or changing a campground's note, rewrite it into clean, current prose (no appended diary snippets, no stale or contradicting facts); never go looking for notes to clean"
metadata:
  type: feedback
---

**Rule (AWH 2026-10-13):** "if you are working on a campground and you are reading or updating the note field, go through it and clean it up ... Rephrase the notes so they look and read cleanly and so they don't look like a diary of cobbled together snippets of data. Don't go out of your way to clean up the notes. Do it only if you are already reading and/or modifying them."

**Why:** sweeps, audits and fixes kept appending to notes (dated lines, bracketed corrections, MINIMUM STAY and CAMPER-REPORTED RATE lines) without revising what was already there, so many notes carry old or contradictory facts and read like a log.

**How to apply:**
- Trigger: only a note I'm already reading or editing for the task at hand. Never a cleanup pass of its own, never a bulk rewrite.
- Rewrite the whole note as one clean description of the campground as it is now. Merge duplicates, drop facts that later lines superseded, and settle contradictions by the newer authoritative source (check it before choosing). Keep the two-space house style between sentences.
- Keep what the other rules require, as plain sentences rather than appended lines: a closure or other caveat with its date ([[feedback_add_with_caveat_not_withhold]]), a standing minimum stated clearly with its date ([[feedback-minimum-stay]]), and a camper-reported rate called camper-reported, with its month ([[feedback-camper-report-rates]]). URLs still go in `website` ([[feedback_urls_in_website_not_notes]]).
- AWH's own signed text (`--AWH`) is firsthand: keep it in AWH's words with the marker ([[feedback-attribute-note-edits]], docs/campground-curation.md). Clean everything around it and sign my rewrite once with `--Claude`, not line by line. This is the default I chose on 2026-10-13 and told AWH; if they say to tidy their text too, update this.
- A rewritten note changes its hash, so the entry re-queues for the note scan. Run `apply_absent.py --rescan` on it ([[reference_session_note_scan]]) so note-derived fields follow the new text and nothing rests on a fact I removed.
