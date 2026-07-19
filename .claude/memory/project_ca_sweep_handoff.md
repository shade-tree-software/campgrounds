---
name: project_ca_sweep_handoff
description: California sweep IN PROGRESS — state + local buckets added & inclusion-audited; waterfront audit and the federal + private buckets still outstanding
metadata: 
  node_type: memory
  type: project
  originSessionId: d8015b25-3a69-4c9c-b79b-cd3a86bc1083
  modified: 2026-07-19T20:25:38.252Z
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
1. **Federal bucket — NOT RUN.** Only 3 legacy CA federal entries exist (277 Kirk
   Creek, 279 Tuolumne Meadows, 295 Jumbo Rocks). CA federal is likely the largest
   single bucket of any state: NPS (Yosemite, Sequoia/Kings, Death Valley, Joshua
   Tree, Point Reyes, Channel Islands), 18 national forests, BLM, USACE, Reclamation.
3. **Private bucket — NOT RUN.** The 4 present came from the local pass. Expect
   AZ-grade difficulty: CA private skews hard to 55+/snowbird/membership parks.
4. Those 3 legacy federal entries lack `inclusion_evidence`.

Chosen order (AWH 2026-07-19): audit the completed 243 first, then add federal and
private with their audits folded in per the normal pipeline.

Audit batches run **sequentially** — see [[feedback_sequential_sweep_agents]].
Process reference: [[reference_inclusion_audit]],
[[reference_usedirect_deep_reservation_links]] (CA = ReserveCalifornia US eDirect).
