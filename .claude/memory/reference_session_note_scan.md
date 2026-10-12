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

**Read the `SYSTEM` constant in the script as the spec** — it is the field vocabulary, the allowed enum values, and the worked examples, and it is stricter than it looks (`electric` may only be 0/15/20/30/50 - 15 added 2026-10-09; a stated amperage outside those is OMITTED, never rounded).

**Two traps worth knowing before applying:**

- **`HUMAN_METHODS = {"manual", "reported"}`** — those groups are dropped silently, which is the protection working. Of 126 groups proposed in that run, 71 were dropped this way, and one was a real save: a note reading "38 pull-thru sites … plus back-ins" yielded `count: 38` where the entry's `reported` 56 was correct.
- **`derived` is NOT protected.** A group an earlier script wrote — notably `hookups` filled by `recgov_hookups.py` from the rec.gov catalog — *will* be overwritten by a note-derived proposal. Omit that group from the proposals rather than trusting the merge, or prose written *from* the catalog silently replaces the catalog ([[feedback_trust_recgov_over_sweep_notes]]).

Related: [[project_campground_schema]], [[feedback_absent_is_not_unknown]], [[reference_ridb_gap_pipeline]].

**2026-10-09 run (done):** queue was 1,114 (gap-sweep adds + edited notes); batches 1-19 applied, **queue back to 0**. Next time something is queued, use `extract_fields.py --report`, `--dump 60`, read, then `python3 audit/note_scan/apply_absent.py <dump> <proposals>` (it drops groups the entry already has, so a re-queued old entry keeps its rec.gov/agency values; omit `platform` unless the note names one of the enum channels - CampLife/Firefly/ResNexus/Newbook/Staylist are not in it, so those get `reservable: true` only). Conventions used: "30/50-amp" -> 50; FHU -> water+sewer; W/E sites -> water true; "primitive" FWP/DNR camps -> electric 0; "~N sites" -> N unless tent/cabin counts make the total ambiguous; a "pit toilet" counts as vault.



**2026-10-12 run (done, 235 entries):** `apply_absent.py --rescan` now re-reads groups whose provenance is note prose (a stale entry's derived group used to be kept as it was, so an edited note never corrected it: Powder Mill MO stayed 'first-come only' after its note said reservations are required) and `_unsupported` removes keys the note doesn't state. Groups from rec.gov, agencies or people are still never touched. Pad lengths are not rig limits (spec); I briefly set one from 'back-in pads 15-34 ft' and took it back.

**Resolved 2026-10-12 (commit 65d4628):** the ~124 note-derived 'no hookups' values the notes never stated (the 2026-09-16/17 hand passes reading 'vault toilets, no potable water' as no hookups) were checked against rec.gov and agency pages on AWH's call ('get the real data so we're not guessing'): electric 0 confirmed 55 / removed 69, water false confirmed 77 / removed 34, sewer false confirmed 16 / removed 98. Record and method: audit/hookups_recheck/. Lessons: a support regex must accept 'non-hookup' (16 of the first 140 said it); Forest Service pages state water ('Potable water is not available at this site') but almost never electricity; Yosemite and Lake Mead state 'no hookups' park-wide; a coordinate-matched RIDB facility can be the group camp or the concession RV park next door. See [[feedback-absent-is-not-unknown]].
