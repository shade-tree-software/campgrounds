---
name: project_canada_cad_private_topup
description: ON/BC/AB/SK/MB CAD-corrected private top-up — COMPLETE. 190 adds re-including affordable Canadian private parks the raw-$ gate wrongly excluded.
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3cab67-a02e-4507-bbcc-335279c4c558
  modified: 2026-07-24T12:41:39.499Z
---

**Canada CAD-corrected private top-up COMPLETE 2026-07-24.** Re-ran the
commercial/private bucket for the 5 provinces done before the CAD-pricing
finding ([[reference_rvlife_price_cad]]) — ON/BC/AB/SK/MB — with the
CAD-corrected affordable gate (`avg_rate` ≤ $55 CAD ≈ $40 USD AND `star` ≥ 4,
NOT the raw RV Life $ tag which over-tiers Canadian parks ~1 level). This
recovered the affordable private parks the original raw-nominal gate wrongly
excluded.

**Result: 190 adds, ids 12634-12823** (ON 84, BC 75, AB 26, SK 3, MB 2).
By ownership: private 179, local 7, provincial 4. 17 skips (seasonal-only,
membership/share-ownership, closed, token-transient). Two commits on master
(NOT yet pushed — push when asked): `db27bde` adds, `278db72` waterfront audit.

- **Detection:** RV Life Algolia app `H0LPZK92QJ` key `88da91e06e8ee5ec4aba26675ac26b99`
  (valid 7/2026), tiled per-province bboxes → 2193 unique hits. Gate: park_type
  commercial, star≥4, price>2 (would've passed the OLD gate otherwise), 0<avg_rate≤55,
  minus dedup vs existing DB → 207 candidates in 28 batches of 8.
- **Plumbing:** research instructions `audit/add_research_instructions_canada_private.md`
  (the CAD-gate rationale + Canada ownership/reservation rules baked in). Appended
  per-province via `append_state.py --state XX --leads <path>`. Scratch scripts
  detect.py/classify.py + batches/results under the session scratchpad.
- **Waterfront audit:** 24 sequential batches carrying leads, `audit/apply_waterfront_audit.py`.
  77 upgrades (46 on-water: 16 lakefront/14 riverfront/9 bayfront/4 pond/2 coastal
  woods/1 creekside; 31 view), 113 not waterfront, 3 coord fixes. All 190 carry
  both inclusion_evidence and waterfront_evidence.

**Ownership rescues** (RV-Life-mistagged government parks): ON St. Lawrence Parks
Commission (Glengarry/Ivy Lea/McLaren) = provincial; Beavermead/Cobourg Victoria/
Port Glasgow/West Elgin/Lower Beverley = local. AB Drayton Valley (town) = local,
Mount Kidd (Alberta Parks) = provincial.

**Dedup false-positives to know about:** the append_state.py 150 m coord guard
dropped two GENUINE neighboring-park pairs added earlier in the same run —
Orchard Valley (2389 Rojem Rd) vs Orchard Hill (2351, id 12757), and Peachland RV
(4795 Paradise Valley Dr) vs Camp Okanagan (4835, id 12724). Both re-added by hand
as 12822/12823 after confirming distinct addresses. When the guard flags a pair,
check addresses before dropping — small farm/forest RV parks cluster.

Ran **sequentially** ([[feedback_sequential_sweep_agents]]); one session-limit hit
mid-audit (batch 05) recovered fine on reset. QC was already CAD-corrected in its
own sweep ([[project_qc_sweep_handoff]]). Canada provinces now all CAD-correct.
