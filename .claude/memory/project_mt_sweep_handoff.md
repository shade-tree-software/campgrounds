---
name: project_mt_sweep_handoff
description: "Montana sweep — all 4 add-buckets DONE+committed+pushed (297 entries, ids 6054-6348); only the waterfront audit remains"
metadata: 
  node_type: memory
  type: project
  originSessionId: 28dfddfb-bc19-4a4e-802d-8b193b941500
---

**Montana sweep status (paused 2026-07-01):** all four ADD buckets are **complete, committed, and pushed** to master. **297 MT entries** total (ids 6054-6348 are the 295 new ones; +2 pre-existing Glacier NP Apgar #290 / Many Glacier #278). Ownership: federal 213, state 28, local 22, private 34. The **only remaining stage is the waterfront audit** (task #10), which was just started (batch 1 of ~32 was in flight at pause).

Add-bucket commits (all pushed):
- **state (55, ids 6054-6108)** — 61 RVLife state/dnr cands; 6 skips (2 FAS at 20ft, Yellow Bay tent-only, Big Arm & Clark Canyon dups). RVLife ownership tags VERY unreliable in MT: 29 reclassified to federal (mostly BLM — Holter Lake complex, Madison River Palisades/Red Mtn/Ruby Creek, UMR Breaks Coal Banks/Judith Landing/James Kipp, Zortman; Reclamation Clark Canyon/Canyon Ferry/Tiber; USFS Lonesomehurst/Moose Creek Flat). MT state parks via `fwp.mt.gov` + `montanastateparks.reserveamerica.com`.
- **local (17, ids 6109-6125)** — 18 city/county cands; 1 skip (Washoe Park closed). City parks + county fairgrounds (year-round RV OK). Yogo→private.
- **private (44, ids 6126-6169)** — 294 commercial → 51 gated (price≤$$ & star≥4) → 44 keep, 7 skips (closed/lodge/phantom/mobile-court/event-only). Reclassified to USFS (Parkside/Seeley Lake/Lee Creek), local (Chief Joseph/Lake Shel-Oole/Trafton/fairgrounds/Cow Bells), Reclamation (Walleye), state FAS (Russell Gates).
- **federal (179, ids 6170-6348)** — 266 RVLife usfs/national/coe/military cands across **34 research batches**. USFS national forests (Custer Gallatin, Bitterroot, Lolo, Kootenai, Flathead, Beaverhead-Deerlodge, Helena-Lewis&Clark), NPS (Glacier: St.Mary/Fish Creek/Two Medicine/Rising Sun/Avalanche — Apgar & Many Glacier skipped as already-in-DB; Bighorn Canyon: Afterbay/Barry's Landing), USACE (Fort Peck Downstream/West End, Libby Dunn Creek), Reclamation (Canyon Ferry, Clark Canyon, Tiber, Fresno). **The #1 skip reason was max-RV-length <23ft** (dozens skipped at 16-20ft); "22ft recommended" was KEPT (a 23-ft motorhome fits — standard set from federal batch 16 on). 3 military FamCamps skipped. Cross-bucket dups dropped: Moose Creek Flat, Big Creek, Holland Lake, Racetrack, Sam Billings, Lost Johnny Point, Seeley Lake Complex.

**WATERFRONT AUDIT — TODO (task #10):** every MT entry ids 6054-6348 currently has `waterfront:"not waterfront"` placeholder and NO `waterfront_evidence` (= unaudited). Resume by auditing them. Batch files were at `/tmp/.../scratchpad`-adjacent `/tmp/mt_wf_b*.json` (32 batches of the 251 water-adjacent; 44 research-confirmed-dry ids in `/tmp/mt_wf_dry_ids.json`) + prompt template `/tmp/mt_wf_prompt.txt` + leadmaps `/tmp/mt_*_leadmap*.json`. **If /tmp was wiped**, regenerate: the audit needs only id+location+website (leads are a head start, not required) — pull all MT entries with empty `waterfront_evidence`, batch ~8, run `audit/waterfront_audit_instructions.md` subagents (satellite look mandatory; MT is canopy-heavy so defer to rec.gov/USFS per-site maps; reservoir drawdown → measure to high-water edge), then `python3 audit/apply_waterfront_audit.py <results.json>` and also stamp the ~44 dry ones with an evidence string. Apply+commit+push in chunks. Expected: lots of creekside/lakeside upgrades since MT is mountain-creek/river/reservoir heavy.

Method identical to [[project_nd_sweep_handoff]] / [[project_sd_sweep_handoff]]; ran all agents sequentially per [[feedback_sequential_sweep_agents]]. Reusable MT append script (state='MT') was `/tmp/append_bucket_mt.py`.
