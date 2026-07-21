---
name: project_ca_sweep_handoff
description: California sweep COMPLETE — all 4 buckets (state/local/federal/private) added + inclusion + waterfront audited & pushed
metadata: 
  node_type: memory
  type: project
  originSessionId: d8015b25-3a69-4c9c-b79b-cd3a86bc1083
  modified: 2026-07-21T16:03:47.092Z
---

California is **COMPLETE** as of 2026-07-21 — the largest state sweep to date.
All four buckets added + inclusion-audited (`inclusion_evidence` on every entry)
+ waterfront-audited (`waterfront_evidence` on every entry), all pushed.

**By bucket (new entries this whole sweep):**
- **State parks** — 111 entries, ids 11605–11715 (commit `ad6abbd`).
- **Local** — 132 entries, ids 11716–11847 (`3f04f89`); 3 removed during inclusion
  (11722 Bear River, 11784 Los Gatos Creek, 11792 Lake San Antonio S dup) → net 240
  for state+local combined. Waterfront: 108 upgrades over the 240, 56 coord fixes
  (`ac40d61`/`735b869`/`baad937`); removals in `8f49e87`.
- **Federal** — 514 entries, ids 11848–12362 (507 federal / 6 private PG&E-SCE / 1
  local TCPUD; removed tent-only Hobo 12226). Waterfront 180 upgrades/35%. 8 add
  commits + 7 audit-tranche commits, all pushed. Kern River/Lake Isabella + Shasta/
  Trinity/Bucks/Antelope the richest on-water veins.
- **Private — DONE 2026-07-21 (this session).** 111 entries, ids **12363–12473**
  (private 74 / federal 23 / local 12 / state 2 — the non-private ones are RV-Life-
  mistagged "commercial" agency campgrounds the federal/state sweeps missed *because*
  they carry a commercial `park_type`: concessionaire USFS/BLM/NPS + irrigation/water-
  district [EID/NID/Merced ID/United Water] + SMUD + tribal casino RV parks). Add
  commit `7f9cd58`, waterfront-audit commit `3b3f7ea`.
  - Detection: RV Life Algolia (app H0LPZK92QJ, park_type=commercial, region_abbvr==CA),
    gated to ≤$$ & ≥4★ → 1030 raw → 212 candidates in 18 batches. 112 add / 98 skip
    (**53% skip — AZ-grade**: Coachella/Desert-Hot-Springs 55+ residential resorts,
    Escapees/Thousand-Trails/Colorado-River-Adventures membership, Elks/Moose club lots,
    bare casino overnight lots [0 sites], mobile-home/long-term parks). 1 dup dropped by
    append dedup (Albee Creek ~ existing 11605) → 111 added.
  - Waterfront: 43 upgrades/39% (25 on-water: 9 lakefront/9 creekside/5 riverfront/
    1 bayfront/1 coastal dunes [Wright's Beach, Sonoma Coast]; 18 view: 10 lakeview/
    7 riverview/1 bayview) + 4 coord fixes. Eastern Sierra (Convict/Coldwater/Sherwin
    Creek/Lee Vining/Owens River) + Colorado River (Rio Del Sol/Big River riverfront,
    Havasu Landing lakefront) the richest veins.

**Legacy loose ends (pre-existing CA entries, NOT from this sweep) — still open:**
- 3 legacy federal entries (ids 277/279/295 — Kirk Creek, Tuolumne Meadows, Jumbo
  Rocks) lack `inclusion_evidence`.
- The state/local/federal buckets folded inclusion+waterfront in at add time, so the
  240+514 new entries are fully covered; only those 3 legacy ids remain unaudited.

Process refs: sequential agents [[feedback_sequential_sweep_agents]],
[[reference_inclusion_audit]], [[reference_usedirect_deep_reservation_links]]
(CA = ReserveCalifornia US eDirect). Scratchpad for private bucket: session
`5c74c92e…986750` dirs `ca_priv/` (add batches+results) and `ca_priv_wf/`
(waterfront batches+results).
