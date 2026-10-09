---
name: feedback_verify_image_reads
description: An image Read can silently return "[media removed: request limit]" - never write satellite/map evidence unless the image actually rendered; log what each image shows to a file at read time
metadata:
  type: feedback
---

On 2026-09-29 every satellite tile and map PDF read in a long session came back as `[media removed: request limit]`, and evidence text was written as if the imagery had been seen (entries 14046-14056; Jordanelle got an unearned `lakefront`). Caught and corrected the same night once reads worked again.

2026-10-09, second episode: a context summary reported that the images behind the QC no_rate adds (15126-15164) showed `[media removed: request limit]`. The flagged reads were exactly the ~44 OLDEST images in that context, which fits old media being pruned from later requests, not reads failing when made (the session log keeps the image either way, so it cannot tell). Re-viewed every flagged plan and frame in a fresh context: all waterfront calls stood, but one pin was the satz frame centre on an entrance road (St-Paulin), and one plan count was 2x too high (St-Édouard "~100 traveller sites" -> ~45 + ~15). Fixed by `audit/canada_no_rate/fix_qc_reverify_20261009.py`; the per-image log is `qc_reverify_20261009.md`.

**Why:** the waterfront gate is only as good as the satellite look behind it; a fabricated look is worse than none because `waterfront_evidence` non-empty means "audited".

**How to apply:**
- After every image/PDF Read, check that pixels actually came back before describing it. If reads are failing, stop writing waterfront calls; leave the entry un-added or default it down with evidence that says "imagery not viewed", and tell AWH.
- Write what each image shows into a scratch log the moment it renders (frame, centre, what is where, the call). Evidence is then anchored to a read that is known to have rendered, and a later summary that shows old images as removed can be checked against the log instead of being re-derived.
- Count map legends with pixels where possible (`colorcount.py`, or total colour area / one isolated cell), not by eye.
- Pin with `satpx.py` on a pixel that is ON the loops, never the frame centre.
- Keep a long imagery session under ~100 images per context (one frame per question; crop instead of re-fetching).

Related: [[feedback_waterfront_evidence_in_json]].
