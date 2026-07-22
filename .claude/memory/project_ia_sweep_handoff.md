---
name: project_ia_sweep_handoff
description: "IA waterfront 100% (371/371); inclusion INCOMPLETE — 152 currently-waterfront IA entries still need inclusion audit (55 state/77 local/10 federal/10 private). THE LAST remaining legacy-inclusion backfill as of 2026-07-21 (CO/WI/NY/NE/IL/TN/IN all done)"
metadata: 
  node_type: memory
  type: project
  originSessionId: b2af1a68-1b19-44e5-866e-f5b81f755a78
  modified: 2026-07-22T00:14:00.016Z
---

**STATUS (2026-06-26):** Audited the **220 Iowa campgrounds that were `not waterfront` + unaudited** (ids 2943–3258), both audits, run as two sequential full stages (all waterfront first, then all inclusion), agents one-at-a-time per [[feedback_sequential_sweep_agents]].

**Waterfront stage** — 220/220 audited via the evidence gate. **29 upgrades** (13 lakeview, 8 riverview, 3 pond, 3 riverfront, 2 lakefront), 11 coord fixes; rest confirmed `not waterfront`. Committed in 3 chunks (5cc72ad, 011ff6e, bb4b0bc).

**Inclusion stage** — 219 keeps stamped with `inclusion_evidence`; **1 removal**: id **3097 Greater Ottumwa Park Campground** = duplicate of **3124 Ottumwa Park Campground** (same City-of-Ottumwa campground, identical website/coords). Kept 3124 (carries audited `pond` waterfront + richer note); no `trip_data` campground_id refs to 3097. Committed in 3 chunks (cc6a414, 88361e6, 4e153b8). All 219 survivors now carry BOTH evidence fields.

**Gotcha:** one inclusion agent (batch 03) shifted an id — labeled id 2979 as "Elbert Park" (really id 2977) and skipped Glenwood Lake Park. Caught by an id/name cross-check and re-run. **Always verify result ids match batch names before applying** (apply scripts match by id, so a shifted id silently writes wrong evidence).

**IA WATERFRONT: 100% DONE (371/371).** The lone loose end, **id 4860 Lake Fisher Park**, was waterfront-audited 2026-06-26 — `lakeview` confirmed (sites ~90m back across open grass, beyond on-water bound), `waterfront_evidence` written, committed. Zero IA entries lack `waterfront_evidence`.

**IA INCLUSION loose end still open (NOT done) — the actual count is 152, not 39:**
The 2026-06-26 inclusion stage stamped 219 keeps (over the 220 not-waterfront
entries, 1 removed). The remaining **152 IA campgrounds that carry a waterfront
value** were never inclusion-audited — **55 state, 77 local, 10 federal, 10
private** (incl id 4860 Lake Fisher Park). This is **THE LAST remaining
legacy-inclusion backfill**: as of 2026-07-21 CO, WI, NY, NE, IL, TN, and IN are
all 100% inclusion-complete. IA is the only state left with the loose end.

**Method to finish (standard, per this session's other 7 states):**
`python3 /tmp/gen_incl_batches.py IA` builds ~19 batches of 8 from
`state==IA and not inclusion_evidence`; run the inclusion subagents SEQUENTIALLY
(one at a time), apply each with `audit/apply_inclusion_audit.py`, commit every
~3 batches. IA is LOCAL-HEAVY (77 county/city/lake parks) so those need web
*search* to find operator/county pages — **on 2026-07-21 the session WebSearch
budget hit 200/200 before IA could start**, so IA was deferred to a fresh session
(or raise CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION). WebFetch still worked but
open-ended discovery of local-park pages needs search.

See [[reference_inclusion_audit]], [[project_co_sweep_handoff]] for the method,
and [[feedback_sequential_sweep_agents]].
