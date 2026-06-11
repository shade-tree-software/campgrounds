# Waterfront re-audit (multi-state)

Ongoing re-audit of every `waterfront` value that predates the evidence gate
(commits 4f3160e / 9c28772). Scope: all entries with `waterfront != "not waterfront"`
whose `note` is NOT tagged `--AWH` (those are firsthand-confirmed), and that are
NOT named/described as dispersed (per AWH 2026-06-10: skip dispersed sites).
Working eastward from IL. **Git log is the progress record** — look for
"Audit all NN <ST> waterfront designations" commits to see which states are done.

Pending side-finding from the NY audit: ids 334 "Oneida Shores County Park" and
1467 "Oneida Shores Park" resolved to the same RV loop (~20 m apart) — likely
duplicates, awaiting AWH dedupe.

Remaining queue (counts as of 2026-06-10): the scattered remainder
(NJ 7, VT 5, MD 4, VA 4, FL/RI/ME 2 each, AL/NH/MA/CA/MN/TN/DE 1 each).
Done: MO, IL, IN, KY, OH, WV, PA, NY.

## Per-state workflow

1. Extract the state's entries to audit and split into batch files of ~8:
   `{id, name, location, waterfront, ownership, website}` per entry, written to
   `/tmp/<st>_batch_<n>.json`.
2. Fan out subagents (waves of ~5; one batch each). Each agent gets:
   "Read audit/waterfront_audit_instructions.md and follow it exactly. Your
   batch file is /tmp/<st>_batch_<n>.json. Return ONLY the JSON array."
   The instructions make the satellite look mandatory/asymmetric, default down,
   and require a one-line evidence string per entry. Tell agents to keep Esri
   export requests at size=1000,1000 or smaller (one agent died on a >32MB fetch).
3. Consolidate agent outputs into one results JSON array, then apply with
   `python3 audit/apply_waterfront_audit.py <results.json>` — surgical text edits
   (waterfront / location / elevation_meters by id), never a re-dump; validates
   with `json.load` and verifies every change before writing.
4. Commit with the MO/IL/IN-style message: summary buckets (downgrades to
   not-waterfront, on-water→view, upgrades, lateral type fixes, coord fixes,
   confirms) plus a per-entry `waterfront_evidence` line for every audited entry
   — that makes any later audit a grep of the git log.

## Findings pattern so far (MO, IL, IN, KY, OH, WV, PA, NY)

- ~40-50% of pre-gate designations change, almost all downward.
- ~Half of audited entries had mis-pinned coords (park office, entrance road,
  day-use area, open field). Agents repin onto the campground loop and refresh
  elevation from Open-Meteo; apply script writes both.
- Upgrades are allowed only with counting evidence (legible satellite pads at
  waterline, per-site map, rec.gov shoreline flags) and do happen (~2-4/state).
- USACE campgrounds usually confirm via rec.gov per-site "Lakefront" flags;
  state parks usually downgrade (loops inland of the lake they're named for).
