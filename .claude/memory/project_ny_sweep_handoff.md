---
name: project_ny_sweep_handoff
description: "NY COMPLETE — waterfront 100% AND inclusion 100% (193/193, no loose ends). 2026-07-21 the residual 89 waterfront entries were inclusion-audited: 89 keeps, 0 removals"
metadata: 
  node_type: memory
  type: project
  originSessionId: b381ad4f-360b-454f-aad3-29f38316291b
  modified: 2026-07-21T23:08:44.840Z
---

NY waterfront audit is now **100% COMPLETE** (193/193 NY campgrounds carry `waterfront_evidence`). NY was the last state needing a waterfront audit (per [[project_tn_sweep_handoff]]).

Done 2026-06-29 (commits `80a5454`, `7e6640f`, `527faee`):
- **Waterfront audit** of the 84 non-waterfront NY entries that lacked `waterfront_evidence` (the other 21 non-wf already had evidence from the 2026-06-11 re-audit). 7 upgrades: Cook Park #1458→lakefront, Country Hills #1475→pond, Pope Haven #1479→pond, Brookside Beach #1481→lakeview, Susquehanna Trail #1488→riverfront, Riverbend West #1519→riverfront, Lake Chalet #1521→lakefront. 4 coord fixes (327, 1396, 1415, 1476). Rest confirmed not waterfront.
- **Inclusion audit** of all 105 non-waterfront NY entries: 104 keep, 1 remove — Dewolf Point SP #315 excised (all sites cap at 20 ft, under the 23-ft threshold; owner's own note confirmed it; no trip_data refs). User approved the removal.

**NY inclusion is now COMPLETE (2026-07-21).** The residual 89 currently-waterfront
entries (57 state, 16 local, 15 private, 1 hipcamp) were inclusion-audited in 12
sequential batches of 8: **89 keeps, 0 removals** — a perfectly clean state. NY
state campgrounds are DEC (Adirondack/Catskill) + OPRHP state parks, all confirmed
via DEC pages + ReserveAmerica per-site data; county/town/village parks all real
transient RV campgrounds; private RV parks all confirmed via operator sites. No
under-23ft, boat-access, or seasonal-only removals surfaced in the waterfront set
(the one NY removal, Dewolf Point #315 under-23ft, was in the earlier non-wf pass).
**NY has no loose ends: waterfront 100% + inclusion 100% (193/193).**

See [[reference_inclusion_audit]] and [[feedback_sequential_sweep_agents]].
Remaining legacy-inclusion backfills: NE ~80, IL ~64, TN ~63, IN ~33, IA ~40.
