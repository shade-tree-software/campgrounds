---
name: project_ca_sweep_handoff
description: California sweep IN PROGRESS — state + local buckets added & inclusion-audited; waterfront audit and the federal + private buckets still outstanding
metadata: 
  node_type: memory
  type: project
  originSessionId: d8015b25-3a69-4c9c-b79b-cd3a86bc1083
  modified: 2026-07-19T14:54:01.531Z
---

California is **mid-sweep** as of 2026-07-19 (this file was missing until now, which
is why the sweep silently fell off the radar after the USB/tile work interrupted it —
every other state has a handoff memory; CA did not).

**Done — added and inclusion-audited (`inclusion_evidence` present on all 243):**
- **State parks** — 111 entries, ids 11605–11715, commit `ad6abbd`
- **Local** — 132 entries, ids 11716–11847, commit `3f04f89` (128 still `local`,
  4 reclassified `private` during vetting)

**Outstanding:**
1. **Waterfront audit — 0 of 243 audited.** All new entries carry the placeholder
   `waterfront: "not waterfront"` with no `waterfront_evidence`. This is actively
   wrong data, not merely unaudited: CA state parks are full of Pacific coastline
   and Sierra lakes. Expect a very high upgrade rate, and expect `coastal dunes` /
   `coastal woods` to matter (Pacific coast qualifies; watch for CA-1 running
   between campground and shore, which disqualifies).
2. **Federal bucket — NOT RUN.** Only 3 legacy CA federal entries exist (277 Kirk
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
