---
name: project_inclusion_backfill_remaining
description: "DONE. Inclusion backfill is 100% COMPLETE across the entire database (2026-07-23) — every campground-kind entry carries inclusion_evidence AND waterfront_evidence (12261/12261 both). The final 10 states (OH/MD/ME/VT/NH/NJ/MA/CT/DE/RI) + all 6 owner-held items resolved. Nothing left; this effort is closed."
metadata: 
  node_type: memory
  type: project
  originSessionId: 924e9250-c8f8-4fce-9046-abea78d94c66
  modified: 2026-07-23T10:22:37.318Z
---

**Inclusion backfill is DONE — CLOSED 2026-07-23.** Every `campground`-kind entry in `campgrounds.json` now carries `inclusion_evidence` (12261/12261) AND `waterfront_evidence` (12261/12261). The state-by-state retroactive inclusion audit is complete with zero remaining items. Re-scan below returns 0 unstamped.

**Re-scan command (ground truth — a designation is inclusion-audited iff `inclusion_evidence` is non-empty):**
```
python3 -c "import json;from collections import defaultdict;d=json.load(open('campgrounds.json'));cg=[e for e in d if isinstance(e,dict) and e.get('kind')=='campground'];r=defaultdict(lambda:[0,0])
for e in cg:
 r[e.get('state','?')][1]+=1
 if not e.get('inclusion_evidence'): r[e.get('state','?')][0]+=1
L=sorted([(s,v[0],v[1]) for s,v in r.items() if v[0]],key=lambda x:-x[1]);print('states',len(L),'entries',sum(x[1] for x in L))
[print(f'{s}: {a} left / {b}') for s,a,b in L]"
```

## STATUS 2026-07-22 (FINAL — backfill complete)
- **Waterfront: 100%.** Nothing left.
- **Inclusion: 100%** except the owner-held items below. The last 10 states were finished this session over 24 sequential batches (OH 6, MD 4, ME 3, VT 3, NH 2, NJ 2, MA 1, CT 1, DE 1, RI 1). Method held perfectly — 100% id-match every batch, no session-limit issues.
- **This session's per-state results:**
  - **OH:** 43 keeps, 1 review held (559 Vermilion Travel Plaza = Ohio Turnpike overnight RV lot, 24hr transit parking, owner-added).
  - **MD:** 28 keeps, 1 review held (465 15 Mile Creek = rec.gov 252968 lists 20ft RV max, owner-added --AWH).
  - **ME:** 22 keeps, 1 REMOVE candidate held (209 Schoodic Woods = rec.gov 251833 bans RVs/vehicles >21ft on Schoodic Loop Rd beyond day-use → EKKO 23ft not permitted).
  - **VT:** 17 keeps, 2 held (19 Moosalamoo = rec.gov 256347 20ft max, owner-added --AWH, review; 4087 Lake Eden Rec Area = Town of Eden fall-lottery seasonal full-hookup for summer-long RV owners, not transient, REMOVE candidate).
  - **NH:** 15 keeps, 0 removals (clean).
  - **NJ:** 9 keeps, 1 REMOVE candidate held (125 Worthington State Forest Campsite = duplicate of 1812 Worthington State Forest, identical coords + njportal locationId=20).
  - **MA:** 7 keeps, 0 removals (clean).
  - **CT:** 7 keeps, 0 removals (clean).
  - **DE:** 5 keeps, 0 removals (clean).
  - **RI:** 4 keeps, 0 removals (clean).
- **Earlier this session (recap):** 9 states AR/GA/NC/MS/KS/MO/VA/WV/SC also done (see their per-state memories). All committed + pushed.

## The 6 owner-held items — RESOLVED 2026-07-23 (none were trip-referenced)
Owner decided via AskUserQuestion:
- **REMOVED (excised by id):** 4087 VT Lake Eden Rec Area (fall-lottery seasonal, not transient); 125 NJ Worthington SF Campsite (duplicate of 1812); 559 OH Vermilion Travel Plaza (Ohio Turnpike overnight rest-area lot); 465 MD 15 Mile Creek (rec.gov 20ft max); 19 VT Moosalamoo (rec.gov 20ft max).
- **KEPT + stamped:** 209 ME Schoodic Woods — owner special case despite the posted 21ft Schoodic Loop Rd limit (owner accepts as a squeeze case for EKKO 23ft). inclusion_evidence records the --AWH override.

Note the pattern: owner removed the borderline 20ft-max ones but KEPT the harder >21ft-road-ban Schoodic Woods — owner-added/owner-relevant entries are the owner's call; surface, don't presume. `campgrounds.json` dropped 12266→12261 campground entries.

## Method (proven — 100% id-match, no session-limit issues)
Standard retroactive inclusion backfill per [[reference_inclusion_audit]]:
1. `python3 /tmp/gen_incl_batches.py <ST>` builds batches of 8 from `state==ST and kind=='campground' and not inclusion_evidence` into `/tmp/<st>_incl/batch_NN.json`. (~15-line script; recreate if gone: select those entries sorted by id, emit `{id,name,location,ownership,state,website,note}` in chunks of 8.)
2. Run inclusion subagents **SEQUENTIALLY, one at a time** ([[feedback_sequential_sweep_agents]]) — each reads `audit/inclusion_audit_instructions.md`, loads WebFetch+WebSearch, verifies against operator/agency/reservation-system authority (NOT aggregators). **Tell each agent to prefer WebFetch of URLs already in the note's `website` field over open-ended WebSearch** (kept the WebSearch budget comfortable all session). Have each agent write its result to `/tmp/<st>_incl/result_NN.json` AND return the same JSON.
3. **Cross-check result ids == batch ids before applying** (quick python compare) — a shifted id silently writes wrong evidence.
4. Apply each with `python3 audit/apply_inclusion_audit.py <result.json>` — stamps keeps, REPORTS removes/reviews without auto-deleting.
5. Commit every ~1-2 states straight to master.

See [[reference_inclusion_audit]], [[feedback_sequential_sweep_agents]], [[feedback_campground_vetting_discipline]].
