---
name: project_ny_sweep_handoff
description: NY waterfront audit 100% complete; inclusion done for non-waterfront entries only; ~89 currently-waterfront NY entries still need inclusion
metadata: 
  node_type: memory
  type: project
  originSessionId: b381ad4f-360b-454f-aad3-29f38316291b
---

NY waterfront audit is now **100% COMPLETE** (193/193 NY campgrounds carry `waterfront_evidence`). NY was the last state needing a waterfront audit (per [[project_tn_sweep_handoff]]).

Done 2026-06-29 (commits `80a5454`, `7e6640f`, `527faee`):
- **Waterfront audit** of the 84 non-waterfront NY entries that lacked `waterfront_evidence` (the other 21 non-wf already had evidence from the 2026-06-11 re-audit). 7 upgrades: Cook Park #1458→lakefront, Country Hills #1475→pond, Pope Haven #1479→pond, Brookside Beach #1481→lakeview, Susquehanna Trail #1488→riverfront, Riverbend West #1519→riverfront, Lake Chalet #1521→lakefront. 4 coord fixes (327, 1396, 1415, 1476). Rest confirmed not waterfront.
- **Inclusion audit** of all 105 non-waterfront NY entries: 104 keep, 1 remove — Dewolf Point SP #315 excised (all sites cap at 20 ft, under the 23-ft threshold; owner's own note confirmed it; no trip_data refs). User approved the removal.

**Remaining NY loose end:** the ~89 currently-waterfront NY entries still need an **inclusion** audit (they have `waterfront_evidence` but not `inclusion_evidence`) — same pattern as [[project_in_sweep_handoff]], [[project_ne_sweep_handoff]], [[project_il_sweep_handoff]], [[project_tn_sweep_handoff]], [[project_wi_sweep_handoff]]. Build batches from `state==NY and waterfront!='not waterfront' and not inclusion_evidence`.

See [[reference_inclusion_audit]] and [[feedback_sequential_sweep_agents]] (ran the 25 batches one at a time).
