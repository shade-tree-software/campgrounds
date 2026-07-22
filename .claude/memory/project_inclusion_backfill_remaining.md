---
name: project_inclusion_backfill_remaining
description: "AUTHORITATIVE inclusion-backfill status (as of 2026-07-22). Waterfront 100% everywhere; inclusion has ~1,483 entries across 19 early-sweep states still to do. Start here for the next inclusion session."
metadata: 
  node_type: memory
  type: project
  originSessionId: 924e9250-c8f8-4fce-9046-abea78d94c66
  modified: 2026-07-22T10:47:07.652Z
---

**This is the single source of truth for what inclusion work remains. Don't trust per-state "COMPLETE" memory lines for inclusion** — many say COMPLETE meaning their ADD + waterfront audit finished, but they were swept BEFORE the inclusion-at-ADD discipline (~2026-06-25), so they never got `inclusion_evidence`. **The live `campgrounds.json` field is ground truth — always re-scan before starting** (a designation is inclusion-audited iff its `inclusion_evidence` is non-empty).

**Re-scan command:**
```
python3 -c "import json;from collections import defaultdict;d=json.load(open('campgrounds.json'));cg=[e for e in d if isinstance(e,dict) and e.get('kind')=='campground'];r=defaultdict(lambda:[0,0])
for e in cg:
 r[e.get('state','?')][1]+=1
 if not e.get('inclusion_evidence'): r[e.get('state','?')][0]+=1
L=sorted([(s,v[0],v[1]) for s,v in r.items() if v[0]],key=lambda x:-x[1]);print('states',len(L),'entries',sum(x[1] for x in L))
[print(f'{s}: {a} left / {b}') for s,a,b in L]"
```

## STATUS 2026-07-22
- **Waterfront: 100% complete** — all 12,275 campground entries across 52 states/provinces carry `waterfront_evidence`. Nothing left.
- **Inclusion: 10,792 / 12,275 done.** Remaining: **19 states, ~1,483 entries.**

## Remaining inclusion work (biggest first)
| State | left / total | note |
|---|---|---|
| AR | 234 / 234 | zero — early sweep, added pre-discipline |
| GA | 222 / 225 | ~zero |
| NC | 172 / 174 | ~zero |
| MS | 133 / 133 | zero |
| KS | 128 / 158 | partial |
| MO | 115 / 256 | partial (141 already done in a prior pass) |
| VA | 113 / 163 | partial |
| WV | 110 / 164 | partial |
| SC | 93 / 93 | zero |
| OH | 44 / 152 | partial |
| MD | 29 / 47 | partial |
| ME | 23 / 45 | partial |
| VT | 19 / 46 | partial |
| NH | 15 / 51 | partial |
| NJ | 10 / 20 | partial |
| MA | 7 / 28 | partial |
| CT | 7 / 20 | partial |
| DE | 5 / 7 | partial |
| RI | 4 / 4 | zero |

Concentration: early-sweep **Deep South** (AR, GA, MS, SC, NC) and **Appalachia/Mid-Atlantic + New England** (VA, WV, KS, MO, OH, MD, ME, VT, NH, NJ, MA, CT, DE, RI).

## Method (proven this session on IA + the 7-state stragglers — 100% keep, 0 removals both times)
Standard retroactive inclusion backfill per [[reference_inclusion_audit]]:
1. `python3 /tmp/gen_incl_batches.py <ST>` builds batches of 8 from `state==ST and kind=='campground' and not inclusion_evidence` into `/tmp/<st>_incl/batch_NN.json`. (If `/tmp/gen_incl_batches.py` is gone, it's a ~15-line script — recreate: select those entries sorted by id, emit `{id,name,location,ownership,state,website,note}` in chunks of 8.)
2. Run the inclusion subagents **SEQUENTIALLY, one at a time** ([[feedback_sequential_sweep_agents]]) — each reads `audit/inclusion_audit_instructions.md`, loads WebFetch+WebSearch, verifies against operator/agency/reservation-system authority (NOT aggregators — they inflate cabin/day-use parks into fake "RV sites"). **Tell each agent to prefer WebFetch of URLs already in the note's `website` field over open-ended WebSearch** (keeps the session WebSearch budget from blowing — it never got close this session with that instruction).
3. **Cross-check result ids == batch ids before applying** (apply script + generator match by id; a shifted id silently writes wrong evidence — this bit a prior IA batch). Verify with a quick python id-list compare.
4. Apply each with `python3 audit/apply_inclusion_audit.py <result.json>` — stamps keeps, and REPORTS removes/reviews without auto-deleting (a human reviews the remove list; excise the `{ }` block by id AFTER checking `trip_data/` for `campground_id` refs).
5. Commit every ~2-3 batches straight to master; push when the user asks.

Local-heavy states need county/city operator pages (e.g. mycountyparks.com for Iowa-style county-conservation; each state has its own county-parks portal). State parks → agency "Stay"/camping page + its reservation system (ReserveAmerica/recreation.gov/US-eDirect). Federal → recreation.gov per-site.

See [[reference_inclusion_audit]], [[feedback_sequential_sweep_agents]], [[feedback_campground_vetting_discipline]].
