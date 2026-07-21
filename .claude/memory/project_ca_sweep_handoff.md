---
name: project_ca_sweep_handoff
description: California sweep IN PROGRESS — state + local buckets added & inclusion-audited; waterfront audit and the federal + private buckets still outstanding
metadata: 
  node_type: memory
  type: project
  originSessionId: d8015b25-3a69-4c9c-b79b-cd3a86bc1083
  modified: 2026-07-21T01:33:57.016Z
---

California is **mid-sweep** as of 2026-07-19 (this file was missing until now, which
is why the sweep silently fell off the radar after the USB/tile work interrupted it —
every other state has a handoff memory; CA did not).

**Done — added and inclusion-audited (`inclusion_evidence` present on all 243):**
- **State parks** — 111 entries, ids 11605–11715, commit `ad6abbd`
- **Local** — 132 entries, ids 11716–11847, commit `3f04f89` (128 still `local`,
  4 reclassified `private` during vetting)

**Waterfront audit — DONE (2026-07-19), all 243 in 31 sequential batches.**
Commits `ac40d61` (1-10), `735b869` (11-20), `baad937` (21-31). 108 upgrades (44%):
26 lakefront, 19 creekside, 14 riverfront, 12 coastal dunes, 8 bayfront, 4 coastal
woods = 83 on-water; 13 lakeview, 11 bayview, 1 riverview = 25 view. 56 coord fixes
(23% — county reservoir parks were badly mis-pinned to marinas/day-use lots/open
water; the state-beach entries were mostly fine). All 243 now carry
`waterfront_evidence`. Batch files + results in the session scratchpad `ca_audit/`.

**Three inclusion problems surfaced during the audit — all REMOVED (commit `8f49e87`,
owner approved 2026-07-19; none had trip_data references):**
- **11722 Bear River Campground** (Placer County) — no campground on imagery; closed
  to overnight camping.
- **11784 Los Gatos Creek Park** (Fresno County) — closed indefinitely since Dec 2025.
- **11792 "Lake San Antonio South Shore (Monterey County)"** — duplicate of 11779.
CA new entries now number **240** (was 243).

**Outstanding:**
1. **Federal bucket — IN PROGRESS (started 2026-07-19).** Detection DONE: RV Life
   Algolia (app H0LPZK92QJ, key inline on campgrounds.rvlife.com/) tiled over the CA
   bounding box, park_type in {national,usfs,dnr,coe} (dnr=BLM=federal in CA), filtered
   region_abbvr==CA, dropped closed/test, deduped vs DB (caught the 3 legacy CA-fed +
   1 AZ border). **763 candidates → 64 batches of 12** (usfs 390 / national 301 /
   dnr-BLM 56 / coe 16), clustered by park_type + geo. Batch files in session scratchpad
   `ca_fed/batch_NN.json`; results to `ca_fed/results/`. Pipeline: sequential research
   agent per batch (contract = `audit/add_research_instructions_ca.md`) → append via
   `python3 append_state.py --state CA --leads <ca_fed_leads.json> <results...>` →
   commit in tranches (~8 batches) → then sequential waterfront audit over the new ids
   carrying the leads. Legacy CA federal is largest bucket of any state (NPS Yosemite/
   Sequoia-Kings/Death Valley/Joshua Tree, 18 NFs, BLM incl LTVAs/Glamis/King Range,
   USACE reservoirs). Track batch cursor here as it advances.
   - **ADD STAGE COMPLETE (2026-07-20): all 64/64 research batches added + committed +
     PUSHED.** 515 new entries, ids **11848-12362** (508 federal, 6 private PG&E/SCE
     project reservoirs, 1 local TCPUD), ~60% keep rate. Commits `18504ba` `9558736`
     `a9fd580` `d8ab819` `c11fd4f` `50912be` `5d5c61e` `f7296cd`. Dedup dropped re-listed
     Tree of Heaven/Red Feather/Upper Stony Creek/Rancheria/Green Valley; hand-re-added
     the distinct-but-<150m cluster neighbors (Davis Flat 12089, Hobo 12226, Stony Creek
     12227, Catavee/Kinnikinnick/Hungry Gulch/Live Oak N/Big Pine Creek 12290-12294), all
     verified via rec.gov as separate facilities. Inclusion folded in (every entry has
     `inclusion_evidence`).
   - **WATERFRONT AUDIT of the 515 new ids (11848-12362) — IN PROGRESS.** 65 batches of 8
     built in scratchpad `ca_fed_wf/wb_NN.json` (each carries its `lead`); results to
     `ca_fed_wf/results/wr_NN.json`. Run SEQUENTIALLY. Apply is PER-FILE (the script only
     reads argv[1]): `for i in ..; do python3 audit/apply_waterfront_audit.py wr_$i.json; done`.
     - **AUDIT CURSOR: batches 1-60/65 DONE + committed** (`9ed1679` `bdde20d` `0d6295c`
       `1a31121` `41c282f` `7b2bc24`; 479 audited, ~171 upgrades/36%, 11 coord fixes).
       Removed tent-only **Hobo 12226** (`d6069a4`, rec.gov all-tent — CA federal new now
       514). Next: audit batch 61. (5 audit batches left, ids 12329-12362 = the BLM
       desert LTVAs/Glamis + USACE reservoir tail.)
     THEN CA federal is fully done → only the private bucket remains for the whole CA sweep.
2. **Private bucket — NOT RUN.** The 4 present came from the local pass. Expect
   AZ-grade difficulty: CA private skews hard to 55+/snowbird/membership parks.
3. Those 3 legacy federal entries (277/279/295) lack `inclusion_evidence`.

Chosen order (AWH 2026-07-19): audit the completed 243 first, then add federal and
private with their audits folded in per the normal pipeline.

Audit batches run **sequentially** — see [[feedback_sequential_sweep_agents]].
Process reference: [[reference_inclusion_audit]],
[[reference_usedirect_deep_reservation_links]] (CA = ReserveCalifornia US eDirect).
