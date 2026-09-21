---
name: reference_session_note_scan
description: extract_fields.py can be run without an API key — dump the queued notes, read them in-session, and apply through its own validation path
metadata:
  type: reference
---

`extract_fields.py` calls `claude-opus-5` to turn note prose into structured fields, but **it does not need `ANTHROPIC_API_KEY` to do the work** — the assistant in session *is* that model, and the script already carries the door:

```
python3 extract_fields.py --report                      # free, what's queued
python3 extract_fields.py --dump 60 --out queued.json   # the notes to read
#   ... read them against the SYSTEM prompt in extract_fields.py ...
python3 extract_fields.py --apply-file proposals.json --dry-run
python3 extract_fields.py --apply-file proposals.json
```

`--apply-file` runs proposals through the **same** `clean_proposal` validation, `write_deltas` merge, provenance stamping and `note_scan` signature the API path uses; it only tags the model `claude-opus-5/session` (`SESSION_MODEL`) so the two are distinguishable later. Nothing is hand-edited into `campgrounds.json`. Used 2026-09-21 for the last 49 entries, which took the queue to zero.

**Read the `SYSTEM` constant in the script as the spec** — it is the field vocabulary, the allowed enum values, and the worked examples, and it is stricter than it looks (`electric` may only be 0/20/30/50; a stated amperage outside those is OMITTED, never rounded).

**Two traps worth knowing before applying:**

- **`HUMAN_METHODS = {"manual", "reported"}`** — those groups are dropped silently, which is the protection working. Of 126 groups proposed in that run, 71 were dropped this way, and one was a real save: a note reading "38 pull-thru sites … plus back-ins" yielded `count: 38` where the entry's `reported` 56 was correct.
- **`derived` is NOT protected.** A group an earlier script wrote — notably `hookups` filled by `recgov_hookups.py` from the rec.gov catalog — *will* be overwritten by a note-derived proposal. Omit that group from the proposals rather than trusting the merge, or prose written *from* the catalog silently replaces the catalog ([[feedback_trust_recgov_over_sweep_notes]]).

Related: [[project_campground_schema]], [[feedback_absent_is_not_unknown]], [[reference_ridb_gap_pipeline]].
