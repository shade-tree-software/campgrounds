---
name: project_inclusion_backfill_remaining
description: "AUTHORITATIVE inclusion-backfill status (as of 2026-07-22). Waterfront 100% everywhere; inclusion has ~1,483 entries across 19 early-sweep states still to do. Start here for the next inclusion session."
metadata: 
  node_type: memory
  type: project
  originSessionId: 924e9250-c8f8-4fce-9046-abea78d94c66
  modified: 2026-07-22T11:40:42.747Z
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

## STATUS 2026-07-22 (updated)
- **Waterfront: 100% complete** — all campground entries carry `waterfront_evidence`. Nothing left.
- **Inclusion: remaining 13 states, ~479 entries.**
- **MO DONE 2026-07-22:** all 256 MO entries inclusion-audited (115 backfilled this session over 15 sequential batches, other 141 done in a prior pass) — **115 keeps, 0 removals** (clean). MO state parks via mostateparks.com/ReserveMO (icampmo1.usedirect.com); USACE lakes (Table Rock/Truman/Bull Shoals/Stockton/Pomme de Terre/Clearwater/Wappapello/Long Branch/Smithville/Mark Twain Lake) via rec.gov per-site; Mark Twain NF + Ozark NSR NPS + MDC conservation areas; county/city park campgrounds (Smithville/Jackson Co/Jeff City/Mozingo) + private RV parks (Branson/Lake of the Ozarks). Pushed.
- **KS DONE 2026-07-22:** all 158 KS entries inclusion-audited (128 backfilled this session over 16 sequential batches, other 30 done in an earlier pass) — **128 keeps, 0 removals** (clean). KDWP state parks + state fishing lakes via ksoutdoors.gov/ReserveAmerica; USACE lakes (Clinton/Council Grove/Fall River/John Redmond/Kanopolis/Marion/Melvern/Milford/Perry/Pomona/Tuttle Creek/Wilson/Big Hill) via rec.gov per-site; Cimarron NG; many city/county lake campgrounds (city-park pages) + private RV parks. Pushed.
- **MS DONE 2026-07-22:** all 133 MS entries inclusion-audited over 17 sequential batches — **133 keeps, 0 removals** (clean). MDWFP state parks + state fishing lakes via mdwfp.com/reserve.mdwfp.com/eRegulations; USACE lakes (Sardis/Enid/Grenada/Arkabutla/Bay Springs/Okatibbee/Aberdeen/Columbus/Tenn-Tom) via rec.gov per-site; Natchez Trace NPS + De Soto/Bienville/Homochitto/Tombigbee NF; PRBDD/PHWD "water parks" (regional-authority = local) + Ross Barnett Reservoir (therez.ms.gov); county/municipal RV parks; ~55 private RV parks. Pushed.
- **NC DONE 2026-07-22:** all NC entries inclusion-audited over 22 sequential batches — **170 keeps, 2 removals** (both owner-approved: 267 Spruill Conservation Farm = all 3 Hipcamp sites cap under 22 ft < EKKO 23 ft, was an owner --AWH entry; 4280 Paul's RV Park & Boat Ramp New Bern = one directory 'permanently closed' + placeholder official site, owner chose remove over conflicting directory listings). No trip_data refs to either. NC total 174→172. Blue Ridge Pkwy/GSMNP/Cape Hatteras-Lookout NPS + Pisgah/Nantahala/Croatan/Uwharrie NF via rec.gov/USFS; NC state parks via ncparks.gov + ReserveAmerica; Kerr Scott/Kerr Lake/Jordan/Falls USACE+SRA; ~100 private RV parks + many county/city parks + Hipcamp (several owner --AWH). Pushed. LESSON: owner --AWH entries can still fail criteria (267) — surface, don't auto-delete; and mixed closed/open directory signals (4280) are an owner call.
- **AR DONE 2026-07-22:** all 234 AR entries inclusion-audited over 30 sequential batches — **234 keeps, 0 removals** (state parks via arkansasstateparks.com/reserve; USACE Beaver/Bull Shoals/Norfork/Table Rock/Greers Ferry/DeGray/Greeson/Millwood/Dierks/Gillham/De Queen/Nimrod/Blue Mtn + Arkansas River nav via recreation.gov per-site; Ozark/Ouachita NF + Hot Springs NP + Buffalo NR; ~90 private RV parks via operator sites/Campspot/RoverPass; municipal/county via city park pages). Pushed.
- **GA DONE 2026-07-22:** all 224 GA entries inclusion-audited over 28 sequential batches — **223 keeps, 1 removal** (4557 Harris Branch RA = day-use only, camping closed per FIND Outdoors/Carters Lake concessionaire; add-time note "Confirmed operating" was wrong; no trip_data refs). Also fixed 4571 River Junction website (was rec.gov 232580 = Eastbank, wrong CG → USACE Lake Seminole page). GA state parks via gastateparks.org + ReserveAmerica; USACE Lanier/Allatoona/Hartwell/West Point/Clarks Hill/Seminole + Chattahoochee/Oconee NF via rec.gov; GA Power lakes (gplakes.com); Hall/Forsyth/Bartow/Carroll/Cobb + many county parks; DNR PFAs (Go Outdoors GA); ~100 private RV parks. GA total dropped 225→224.

## Remaining inclusion work (biggest first)
| State | left / total | note |
|---|---|---|
| ~~AR~~ | ~~0 / 234~~ | ✅ DONE 2026-07-22 — 234 keeps, 0 removals |
| ~~GA~~ | ~~0 / 224~~ | ✅ DONE 2026-07-22 — 223 keeps, 1 removed (Harris Branch) |
| ~~NC~~ | ~~0 / 172~~ | ✅ DONE 2026-07-22 — 170 keeps, 2 removed (Spruill, Paul's RV) |
| ~~MS~~ | ~~0 / 133~~ | ✅ DONE 2026-07-22 — 133 keeps, 0 removed |
| ~~KS~~ | ~~0 / 158~~ | ✅ DONE 2026-07-22 — 128 keeps, 0 removed |
| ~~MO~~ | ~~0 / 256~~ | ✅ DONE 2026-07-22 — 115 keeps, 0 removed |
| VA | 113 / 163 | partial — NEXT UP |
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
