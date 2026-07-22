---
name: project_ia_sweep_handoff
description: "IA COMPLETE: waterfront 100% (371/371) AND inclusion 100% (371/371, 0 removals). The 152-entry legacy-inclusion backfill was finished 2026-07-21 over 19 sequential batches. (NOTE: IA was the last of ONE COHORT — CO/WI/NY/NE/IL/TN/IN/IA — NOT the last state overall; 19 early-sweep states still need inclusion. See [[project_inclusion_backfill_remaining]].)"
metadata: 
  node_type: memory
  type: project
  originSessionId: b2af1a68-1b19-44e5-866e-f5b81f755a78
  modified: 2026-07-22T10:46:36.045Z
---

**IA DONE — no loose ends.** Both audits are 100% complete: waterfront 371/371 and inclusion 371/371.

**Waterfront (2026-06-26):** the 220 `not waterfront`+unaudited IA entries (ids 2943–3258) were audited via the evidence gate — 29 upgrades (13 lakeview, 8 riverview, 3 pond, 3 riverfront, 2 lakefront), 11 coord fixes. Plus id 4860 Lake Fisher Park (`lakeview`). Zero IA entries lack `waterfront_evidence`.

**Inclusion stage 1 (2026-06-26):** the 220 not-waterfront entries were inclusion-audited — 219 keeps, **1 removal**: id **3097 Greater Ottumwa Park Campground** = duplicate of **3124 Ottumwa Park Campground** (kept 3124).

**Correction (2026-07-22):** the earlier "IA is THE LAST remaining legacy-inclusion backfill" claim was wrong — it was scoped to one COHORT (CO/WI/NY/NE/IL/TN/IN/IA). A full-DB scan on 2026-07-22 found **19 early-sweep states still lacking `inclusion_evidence`** (~1,483 entries): AR/GA/MS/SC (zero, added pre-discipline), NC, KS/MO/VA/WV, OH/MD/ME/VT/NH, NJ/MA/CT/DE/RI. See the authoritative list in [[project_inclusion_backfill_remaining]]. Waterfront IS 100% everywhere.

**IA inclusion backfill — FINISHED 2026-07-21.** The remaining **152 IA campgrounds that carry a waterfront value** (55 state / 77 local / 10 federal / 10 private) were inclusion-audited over **19 sequential batches of 8** (one subagent at a time per [[feedback_sequential_sweep_agents]]), applied with `audit/apply_inclusion_audit.py`, committed every ~2 batches. Result: **152 keeps, 0 removals, 0 reviews** — IA was uniformly clean. Evidence came from iowadnr.gov park pages + ReserveAmerica per-site type lists (state parks/forests), recreation.gov (USACE Rathbun/Saylorville/Coralville/Red Rock/Mississippi), mycountyparks.com + county-conservation/city operator pages (the local-heavy bulk), and operator sites (private). Notable judgment call: id 3234 Wild Rose Casino RV Park KEPT — a real developed 68-full-service RV park (bathhouse/dump/pool), not a casino overnight lot. WebSearch budget was NOT hit this session (agents leaned on WebFetch of the URLs already in each note's website field).

**Process notes:** `python3 /tmp/gen_incl_batches.py IA` builds the batches from `state==IA and not inclusion_evidence`. Batch 7 correctly skipped id 2943 (already stamped in stage 1) and included 2944 — the generator + apply-script match by id, so always cross-check result ids == batch ids before applying (did so every batch; all matched).

See [[reference_inclusion_audit]] and [[feedback_sequential_sweep_agents]].
