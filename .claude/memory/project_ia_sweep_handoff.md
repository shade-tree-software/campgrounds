---
name: project_ia_sweep_handoff
description: IA waterfront audit 100% COMPLETE (371/371, 2026-06-26); inclusion has a 39-entry retroactive backlog + id 4860 still
metadata: 
  node_type: memory
  type: project
  originSessionId: b2af1a68-1b19-44e5-866e-f5b81f755a78
---

**STATUS (2026-06-26):** Audited the **220 Iowa campgrounds that were `not waterfront` + unaudited** (ids 2943–3258), both audits, run as two sequential full stages (all waterfront first, then all inclusion), agents one-at-a-time per [[feedback_sequential_sweep_agents]].

**Waterfront stage** — 220/220 audited via the evidence gate. **29 upgrades** (13 lakeview, 8 riverview, 3 pond, 3 riverfront, 2 lakefront), 11 coord fixes; rest confirmed `not waterfront`. Committed in 3 chunks (5cc72ad, 011ff6e, bb4b0bc).

**Inclusion stage** — 219 keeps stamped with `inclusion_evidence`; **1 removal**: id **3097 Greater Ottumwa Park Campground** = duplicate of **3124 Ottumwa Park Campground** (same City-of-Ottumwa campground, identical website/coords). Kept 3124 (carries audited `pond` waterfront + richer note); no `trip_data` campground_id refs to 3097. Committed in 3 chunks (cc6a414, 88361e6, 4e153b8). All 219 survivors now carry BOTH evidence fields.

**Gotcha:** one inclusion agent (batch 03) shifted an id — labeled id 2979 as "Elbert Park" (really id 2977) and skipped Glenwood Lake Park. Caught by an id/name cross-check and re-run. **Always verify result ids match batch names before applying** (apply scripts match by id, so a shifted id silently writes wrong evidence).

**IA WATERFRONT: 100% DONE (371/371).** The lone loose end, **id 4860 Lake Fisher Park**, was waterfront-audited 2026-06-26 — `lakeview` confirmed (sites ~90m back across open grass, beyond on-water bound), `waterfront_evidence` written, committed. Zero IA entries lack `waterfront_evidence`.

**IA INCLUSION loose ends still open (NOT done):**
- **id 4860 Lake Fisher Park** — now has `waterfront_evidence` but still NO `inclusion_evidence` (waterfront done, inclusion pending).
- **39 older IA entries** were already marked with a waterfront value + `waterfront_evidence` in earlier sessions but were NEVER inclusion-audited (pre-discipline backlog, like other states). Retroactive-inclusion backlog.

**Next-biggest WATERFRONT backlogs after IA:** MO (143), WI (113), NE (105), IL (88), NY (84), TN (78), IN (72), KY (60). See [[project_co_sweep_handoff]] for the established chunked method.
