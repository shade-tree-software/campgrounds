---
name: project_note_price_cleanup
description: AWH 2026-11-07 pass removing nightly rates / extra-person charges from notes once fees holds them; tools + progress
metadata:
  type: project
---
AWH 2026-11-07: take the base nightly rate and the extra-person charge out of every note (--AWH text included) once `fees` records them; notes go stale (Low Water Bridge 12 said $50 beside a $35-60 field).

Tools in `audit/note_prices/`: RULES.md (what to cut/keep), templates.py (step 1, done: 345 $0 templates), chunk.py (inputs), check.py (deletion-only gate; `--apply` lands, re-tags note-prose provenance, re-stamps a matching note_scan sig), out/NNN.json = per-chunk edits incl. `awh_dropped`.

Progress: 2,341 notes in 15 chunks of 160 (inputs in the session scratchpad, regenerate with chunk.py — it skips already-clean notes). ALL 15 chunks landed 2026-11-07 (~1,900 read-through edits + 345 templated; AWH allowed chunks 12-15 in parallel). Flagged-not-cut items (unit mismatches, permit-priced camping, field gaps) were reported to AWH that day; open ones are listed in the session's final report, not here. Kept on purpose: camper-reported rates, weekly/monthly/cabin/entrance/permit prices. `fees.note` left untouched (offered to AWH).

**Why:** the fee fields are the record; prose copies drift.
**How to apply:** for a re-run, chunk.py skips clean notes; check + land each chunk; phase 7 waited ([[project_phase7_verification]]) since only one agent runs at a time ([[feedback_sequential_sweep_agents]]).
