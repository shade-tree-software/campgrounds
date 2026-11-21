---
name: project_campground_store_split
description: 2026-11-21 audit fields moved to tracked campgrounds_audit.json (main file 55.7 -> 40.7 MB, under GitHub's 50 MB warning); tools must use campground_store
metadata:
  type: project
---

On 2026-11-21 AWH's push warned that campgrounds.json was 53+ MB (GitHub warns at 50, refuses at 100; growth ~1 MB per 2 days from phase 7). AWH chose to split it now: `waterfront_evidence`, `inclusion_evidence`, `note_scan` and `verify_scan` moved to the tracked sidecar `campgrounds_audit.json` (15.2 MB), and the main file went to 40.7 MB.

**Why:** these four fields are never read by the app or the browser, so moving them needed no app change. LFS was rejected because PA deploys by plain `git pull`, and the free 1 GB quota counts every 55 MB version.

**How to apply:**
- Every tool loads and saves through `campground_store.load()` / `save()`. The phase-7 kit (apply, queue, criteria_drops, post_head, mkpara_*, apply_split, leads/add_results), extract_fields, append_state and note_prices/lib were switched.
- Old one-off scripts that `json.load` the main file see no audit fields.
- `save()` merges by default; deleting an audit field needs `authoritative=True`.
- To restore a dropped entry, take its audit row from `git show <c>^:campgrounds_audit.json`.
- Next valve if size bites again: `provenance` (15.7 MB), but the app's PUT merge reads it.

Relates to [[feedback_waterfront_evidence_in_json]], [[project_phase7_verification]].
