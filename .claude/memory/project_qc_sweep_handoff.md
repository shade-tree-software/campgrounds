---
name: project_qc_sweep_handoff
description: Quebec campground sweep — COMPLETE (6th Canadian province). 98 entries, adds + inclusion + waterfront all done + committed.
metadata:
  node_type: memory
  type: project
  originSessionId: e360afcf-a955-46e0-8838-fddebbc8d878
  modified: 2026-07-23T20:47:15.690Z
---

**Quebec sweep COMPLETE 2026-07-23** — 6th Canadian province, after ON/BC/AB/SK/MB.
**98 entries, ids 12474-12571** (provincial 45, local 24, private 24, federal 5).
Waterfront 100% + inclusion 100% (every entry carries both evidence fields).
**Committed to master and pushed** (pushed 2026-07-23). 5 commits: 04e0af4
federal+prov, 543989e local, 171c379 private, 68e1474 waterfront audit, cfd4530
Jacques-Cartier mispin fix. Follows [[reference_canada_sweep_adaptation]], ran
**sequentially** ([[feedback_sequential_sweep_agents]]). Clean fresh-state sweep.
Waterfront: 27 on-water (12 lakefront, 6 bayfront, 4 riverfront, 3 coastal woods,
1 coastal dunes = Oka on Lac des Deux Montagnes, 1 pond), 15 view (7 lakeview,
6 riverview, 2 bayview), 56 not waterfront; 42 upgrades from placeholder, 1 coord
fix (Jacques-Cartier 12492 was on the Rte-175 interchange → re-pinned to the
Camping de la Vallée loop). Coastal woods = Forillon Petit-Gaspé/Des-Rosiers +
Havre-St-Pierre (Gulf shore forest). **NOTE: 143 commercial parks were gate-excluded
(98 as $$$ price>2, 45 star<4) — QC private camping skews expensive; if owner wants
the $$$ parks, revisit the ≥4★/≤$$ gate for QC.** No legacy loose ends.
Next province: NB/NS/PE/NL (Atlantic) or any.

**UPDATE 2026-07-23 — currency-corrected private pass DONE (owner asked).** RV
Life's `price_level` $ tags are NOT currency-adjusted: the $/$$/$$$ cutoffs
($20/$40/$70 nominal) are identical for US and Canada, applied to the raw
`avg_rate` — which for Canadian parks is CAD. Confirmed vs a 794-park US sample
(both put the $$/$$$ boundary at exactly $40; QC $$$ median $46 CAD ≈ US$33). So
CAD parks are pushed up ~one tier and the original ≥4★/≤$$ gate wrongly excluded
~63 genuinely affordable ($$ in USD terms) QC private parks. Re-ran the private
bucket with a corrected gate (`avg_rate` ≤ ~$55 CAD ≈ $40 USD AND ≥4★) → 63
candidates; **added 62** (ids 12572-12633, dropped 1 dup Camping Québec en ville).
By owner: private 51, local 9 (municipal Haltes VR / town campgrounds), provincial
2 (SEPAQ Lac-Simon, Des Voltigeurs). Waterfront-audited (8 batches): 27 upgrades
(16 on-water, 11 view). Commits ce3e87d (adds) + 85f241d (audit). **QC TOTAL NOW
160 entries** (federal 5, provincial 47, local 33, private 75), 100% both-audited.
LESSON for all future Canada sweeps: apply the affordable gate on CAD→USD-converted
rate (or `avg_rate` ≤ ~$55 CAD), NOT the raw RV Life $ tag. The 5 earlier provinces
(ON/BC/AB/SK/MB) used the raw nominal gate → likely under-added private parks; a
top-up pass there is queued/optional. Pushed 2026-07-23.

## Detection (DONE)
- RV Life Algolia app `H0LPZK92QJ`, key `88da91e06e8ee5ec4aba26675ac26b99` (still
  valid). Tiled 7×8 bbox lat 44.9–62.6 / lng -79.9 to -56.9, post-filter
  `region_abbvr=="QC"`. **253 QC hits.** Scripts `/tmp/qc_detect.py`,
  `/tmp/qc_classify.py`, `/tmp/qc_build_batches.py`; hits `/tmp/qc_hits.json`,
  buckets `/tmp/qc_buckets.json`.
- park_type raw: commercial 173, provincial 51, city 20, canadian 7, national 1, county 1.
- **Buckets: federal 6, provincial 51, local 24, private 29** (110 candidates);
  **skip_gate 143** excluded by the ≥4★/≤$$ private gate (98 price>2, 45 star<4).
  Batches of 8 in `/tmp/qc_add_batches/{bucket}_NN.json` (15 files: federal 1,
  provincial 7, local 3, private 4).

## QC-specific classification rules (baked into /tmp/qc_classify.py)
- **`parc national` = SEPAQ PROVINCIAL** (QC calls its provincial parks "national");
  **réserve faunique = SEPAQ provincial** too. The 2 RV-Life `canadian`/`national`
  "…Reserve" mistags (Rouge-Matawin, Ashuapmushuan) were moved federal→provincial.
- **federal = Parks Canada ONLY** = La Mauricie (3 cgs) + Forillon (3 cgs) = 6.
- **local** = city/county park_type + `provincial`-mistagged municipals (Camping
  Municipal l'Oasis, Lac Ha Ha Municipal Park) + `Camping Manic 2` (Hydro-Québec
  dam — agent decides local vs private-utility). No star/price gate on local.
- **private** = commercial with price≤2 AND star≥4 (established gate). NOTE: QC
  camping skews expensive — 98 commercial parks are $$$ (price 3-4) and were
  gate-excluded. If owner wants those, revisit the gate.
- `parc régional` = LOCAL (MRC/regional), not provincial. ZEC = local (community).

## Plumbing
- Research instructions: `audit/add_research_instructions_qc.md` (SEPAQ/Parks-Canada/
  municipal authorities, French camping vocab, coastal-dunes note). Append via
  `python3 append_state.py --state QC --leads /tmp/qc_leads.json <results...>`
  (machine-independent, textual append, dedup guard). Results → /tmp/qc_results/.
- Waterfront audit later: `audit/waterfront_audit_instructions.md` subagents
  (SEQUENTIAL), carry each entry's `lead`, apply `audit/apply_waterfront_audit.py`.
  Canada has NO rec.gov per-site API — lean on satellite + SEPAQ/BC-style per-site
  map PDFs. QC IS coastal (Gulf/Gaspé/North Shore/Îles-de-la-Madeleine) → coastal
  dunes/woods overrides can apply.

## Progress
- Detection + classify + batches DONE.
- **ADDS DONE + COMMITTED**: 98 QC entries, ids 12474-12571 (provincial 45, local 24,
  private 24, federal 5). All carry inclusion_evidence. 3 commits (04e0af4 federal+prov,
  543989e local, 171c379 private). Skips: Cap-Bon-Ami, 5 Mont-Tremblant/Mastigouche
  rustic-under-23ft, Lac Charron cabins, Les Coteaux/Mont-St-Pierre/Lamoureux/St-André/
  Ancre Jaune (closed/seasonal). Results in /tmp/qc_results/, leads /tmp/qc_leads.json.
- **WATERFRONT AUDIT IN PROGRESS**: 13 batches in /tmp/qc_wfaudit/batch_NN.json (carry
  leads), sequential. Apply with `python3 audit/apply_waterfront_audit.py <results>`.
  QC IS coastal (Gulf/Gaspé/North Shore/Îles-de-la-Madeleine) — coastal dunes/woods can
  apply. Then commit + update memory. Push only when asked.
