---
name: feedback_waterfront_evidence_in_json
description: "Waterfront audit evidence lives in the campgrounds.json waterfront_evidence field, not (only) git commits"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a7a4f867-ccd2-4835-8503-a8eca1e49518
---

Per-entry waterfront audit evidence now lives in a `waterfront_evidence` field on each `campgrounds.json` entry — NOT only in git commit messages.

**Why:** A GA stage (2026-06-17) shipped with 67 state/federal entries left at the `not waterfront` placeholder because the "evidence lives in the commit message" convention made it easy to skip the audit and lose track of which entries were done. The JSON field makes audit status queryable and self-documenting.

**How to apply:**
- A non-empty `waterfront_evidence` == the entry has been waterfront-audited. Empty/absent == NOT audited. This single field is the whole answer — no need to also scan the `note`.
- `--AWH` (firsthand owner manual audit) entries were backfilled 2026-06-17 with a `waterfront_evidence` string (capturing the owner's pre-`--AWH` note text), so all 617 of them carry the field too. Invariant going forward: whenever recording a firsthand `--AWH` waterfront call, also write a `waterfront_evidence` string so the field stays the sole source of truth.
- `audit/apply_waterfront_audit.py` writes the field from each result's `evidence` string (upsert: replace if present, else insert right after the `waterfront` line). Still echo evidence in the commit message for `git log` grepping, but the field is the source of truth.
- One-time migration that moved all recoverable commit evidence into the field: `audit/migrate_evidence_to_json.py` (Pass1 rich per-entry parse, Pass2 GA /tmp results, Pass3 bucket-sweep synthesis for MI/IA/NE/WI-local, Pass4 blame-trace for residual on-water). Result: 2174 entries got the field; with 617 `--AWH` entries that's 2791/4548 audited; 0 on-water designations left unsupported.

Relates to [[feedback_campground_vetting_discipline]].
