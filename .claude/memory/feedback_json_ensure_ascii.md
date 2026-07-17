---
name: feedback_json_ensure_ascii
description: "The app must write JSON data files with ensure_ascii=False so UI edits don't re-escape unicode and churn the diff."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f190f1c-07bb-4e79-9669-7f1ed2fc3d0e
---

When the app writes `campgrounds.json` (and other JSON stores), it MUST use `json.dump(..., ensure_ascii=False)` + explicit `encoding="utf-8"`. The default `ensure_ascii=True` escapes every non-ASCII char (`—`→`—`, `★`→`★`, `°`, `•`, `'`) — so editing ONE campground in the UI rewrote every other note into escaped form, producing hundreds of spurious diff lines and painful git merges.

**Why:** the owner (AWH) flagged this 2026-07-16 — a subtle whole-file churn on every UI save.

**How to apply:** `_save_json` in `ekko_trips_app.py` is the single writer behind `campgrounds.json`/`users.json`/captions/etc. — it was fixed to `ensure_ascii=False`. The roadside writer and the curation `append_*.py`/`apply_waterfront_audit.py` scripts must match. If you ever re-introduce a JSON writer, use `ensure_ascii=False`. A one-time normalization of the ~1780 already-escaped lines was committed alongside the fix (dry-run first: a load→save round-trip should change ONLY unicode escaping — no float reformatting, no key reordering — before you rewrite the whole file). See [[project_or_sweep_handoff]].
