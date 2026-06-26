---
name: project_co_sweep_handoff
description: "CO waterfront audit COMPLETE (430/430) — 256-entry sweep done in 11 chunks; inclusion done for the swept 256 (other 177 CO entries predate inclusion discipline)"
metadata: 
  node_type: memory
  type: project
  originSessionId: cb0288c6-b9b0-47e3-af4f-27a2c9c6f479
---

**STATUS: COMPLETE (2026-06-25).** All 11 chunks committed (f2669b7 → 2a20f59).
CO **waterfront audit is 430/430 (100%)**. The 256 swept entries also all carry
`inclusion_evidence`. Final tally: **~54 waterfront upgrades, ~15 coord fixes, 3
removals** (Gothic 2474 under-23ft/4WD; High Country 2602 closed; Riverdale 2663
duplicate of 2662). CO went 433 → 430 campgrounds. Final waterfront distribution:
not waterfront 224, lakeview 69, lakefront 42, riverfront 46, riverview 22,
creekside 26, pond 1.

**Residual:** CO inclusion is 253/430 — the other **177 CO entries** were
waterfront-audited in earlier sessions (before the inclusion discipline) and were
NOT inclusion-audited (separate retroactive-inclusion backlog, like other
pre-discipline states). Next-biggest WATERFRONT backlogs after CO: IA (221), MO
(143), WI (113).

--- (original handoff notes below, kept for method reference) ---

Closing out the **Colorado** waterfront audit AND inclusion audit together (user
chose "Waterfront + inclusion" on 2026-06-25), the same dual treatment as the KS
close-out. CO started with **256 unaudited** entries (178 federal/USFS, 51
private, 24 local, 2 state, 1 hipcamp); almost all were `not waterfront`
placeholders needing a satellite look — and CO USFS/federal sits on lots of
creeks/reservoirs, so real upgrades happen (unlike KS's in-town parks).

**Method:** process in **24-entry chunks** (3 waterfront batches of 8 + 3
inclusion batches of 8), waterfront stage → apply → inclusion stage → apply →
commit per chunk. One commit per chunk = "Audit CO chunk N/11 (ids …):
waterfront + inclusion". Agents run **sequentially** (one at a time, per
[[feedback_sequential_sweep_agents]]). Batch generator: `/tmp/co_gen_chunk.py`
(reads frozen id list `/tmp/co_unaud_ids.json`) — but those /tmp files are
session-scoped; **to resume, regenerate**: query CO entries lacking
`waterfront_evidence`/`--AWH`, sort by id, chunk by 24. Git log "Audit CO chunk
N/11" commits are the real progress record.

**Done so far (chunks 1-6, ids 276-2515, 144 entries, all USFS/NP/SP):**
- Chunks 1-4 (commits f2669b7, 25d226e, 67e7fdb, e797e2f): 18 upgrades, ~9 coord
  fixes, 0 removals.
- Chunk 5/11 (commit 668bacc): 7 upgrades; **1st REMOVAL — Gothic (2474)**,
  under-23ft/4WD (rec.gov no RV length; firsthand "RVs not recommended, 4WD",
  prior note's "lower sites OK" was speculative). Slumgullion kept (decommissioned
  but open free dispersed). CO total 433->432.
- Chunk 6/11 (commit 24977ca): 8 upgrades.
- Chunk 7/11 (commit 6793e14): 5 upgrades.
- Chunk 8/11 (commit b3dfb98): 8 upgrades, 1 coord fix; first private RV parks
  begin here (Canon Bonito/Dark Sky/Drake riverfront). All private parks so far
  confirmed transient nightly (no membership/residential removals).
- **46 waterfront upgrades total, ~12 coord fixes, 1 removal (191/192 keep).**

**Remaining: 64 waterfront unaudited (chunks 9-11): 39 private, 1 hipcamp, 24
local.** USFS block is DONE (100% keep except Gothic on 4WD). Now in private/
local: vet private parks for membership/residential/seasonal-only/defunct
(verify from operator site or RoverPass/Campspot/Good Sam, not aggregators);
vet local for genuine local-government operator. Private parks rarely on-water
unless satellite legibly shows pads on an open bank within ~50m. Pattern: lake/
creek-named loops mostly default down (forest/road/treeline/bench screens);
upgrades come from open aprons, rec.gov "site at river's edge" flags, agency/
operator per-site statements in canopy-blind cases. For REMOVE candidates verify
against operator/agency authority (not just the agent's aggregator) before
excising — check trip_data/ for campground_id refs first (apply_inclusion_audit.py
only reports removes, never auto-deletes; excise the {} block by id manually).

Other big waterfront backlogs after CO: IA (221), MO (143), WI (113). See
[[reference_inclusion_audit]] and the audit/ tooling.
