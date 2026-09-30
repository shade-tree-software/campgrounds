---
name: feedback_verify_image_reads
description: An image Read can silently return "[media removed: request limit]" - never write satellite/map evidence unless the image actually rendered
metadata:
  type: feedback
---

On 2026-09-29 every satellite tile and map PDF read in a long session came back as `[media removed: request limit]`, and evidence text was written as if the imagery had been seen (entries 14046-14056; Jordanelle got an unearned `lakefront`). Caught and corrected the same night once reads worked again.

**Why:** the waterfront gate is only as good as the satellite look behind it; a fabricated look is worse than none because `waterfront_evidence` non-empty means "audited".

**How to apply:** after every image/PDF Read, check that pixels (or rendered text) actually came back before describing it. If reads are failing, stop writing waterfront calls - leave the entry un-added or default-down with evidence that says "imagery not viewed", and tell AWH. Related: [[feedback_waterfront_evidence_in_json]].
