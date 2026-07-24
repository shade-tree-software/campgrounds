---
name: project_ab_sweep_handoff
description: "Alberta campground sweep — COMPLETE (3rd Canadian province). 360 entries, all buckets + waterfront + inclusion audits done."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce97efd5-14f0-45d6-a525-4f876acb65c5
---

**Alberta sweep COMPLETE 2026-07-12** — third Canadian province, after [[project_on_sweep_handoff]] (Ontario pilot) and [[project_bc_sweep_handoff]] (BC). Follows [[reference_canada_sweep_adaptation]]. Ran **sequentially** ([[feedback_sequential_sweep_agents]]). Clean fresh-state sweep — AB had 0 entries before.

## FINAL RESULT: 360 entries, ids 8790-9149
By ownership: **provincial 199, local 75, private 59, federal 27**. Committed to master and **pushed** (2026-07-23).

- **Adds COMPLETE** — every entry carries `inclusion_evidence` (inclusion folded into adds, no separate pass; 0 missing). Commits: federal 15310a4; provincial parts 1-6 (ac25c0f/cd88b17/1fc7de3/bf8d496/b7c253c/13b2fc9); local parts 1-2 (af2012c/81066bc); private parts 1-3 (d74d99b/97bc7ea/b3bbde8).
- **Waterfront audit COMPLETE** — all 360 carry `waterfront_evidence` (0 missing). 47 dry in-town stamped not-waterfront; 313 water-adjacent audited in 40 batches. Final wf distribution: **39 lakefront, 15 riverfront, 6 pond, 5 creekside (=65 on-water) + 40 lakeview, 26 riverview (66 view) + 229 not waterfront**. ~3 coord fixes (Dutch Creek, Whitehorse Creek + one). Audit commits: dry stamp + batches 1-5/6-9/10-12/13-15/16-18/19-20/21-22/23-24/25-27/28-29/30-31/32-33/34-35/36-37/38-40.

## AB-specific method notes (proven)
- **Detection**: RV Life Algolia (app H0LPZK92QJ, key rotates — was `88da91e06e8ee5ec4aba26675ac26b99`), tiled bbox over lat 48.9-60.1/lng -120.1 to -109.9 (5x4 grid), post-filter `region_abbvr=="AB"`. 499 AB hits. park_type: provincial 217, commercial 192, city 42, canadian 31, county 15, +2 mistags. `/tmp/ab_detect.py`, `/tmp/classify_ab.py`.
- **Ownership**: `canadian`→federal (Parks Canada: Banff/Jasper/Waterton/Elk Island NP + Rocky Mtn House NHS). `provincial`+`national`(mistag)→provincial (Alberta Parks). city/county→local. commercial→private (gate ≥4★/≤$$) or local (gov name-scan).
- **Reservation deep links (AB = ReserveAmerica ".do", Platform B, contractCode ABPP)**: `https://shop.albertaparks.ca/camping/<park-slug>/r/campgroundDetails.do?contractCode=ABPP&parkId=<id>` (parkIds ~330100-330373; shared per-park across its campgrounds). shop.albertaparks.ca is Queue-it fronted — **no clean API**, agents found parkIds per-park via web search. Federal = Parks Canada goingtocamp `reservation.pc.gc.ca` (Platform A). Many small PRAs are FCFS or contractor-booked (LetsCamp/Campspot/West Fraser/Red Rock Sawmills).
- **Provincial gotchas**: Alberta Parks PRAs run by private contractors/municipalities/First Nations *under Alberta Parks land* stay **provincial** (Kananaskis Campground Services, West Fraser Mills, Kehiwin Cree Nation, Town of Fox Creek/Milo/MD of Opportunity/Mackenzie County contracts). ONLY reclass to local if the facility was actually *transferred to/owned by* a municipality (Willow Creek PP→MD of Willow Creek; Prairie Oasis→Special Areas Board). Lots of equestrian-only skips (Dawson/Etherington/Mesa Butte equestrian loops — but general campgrounds that merely *offer* horse sites kept: Whitehorse Creek, Machesis). 4WD-only skips (Two Lakes PP, Horburg, Saunders, Peppers Lake, Seibert Lake). Decommissioned (Raven), day-use-only (Engstrom), restricted-access (William Watson Lodge = disabled/seniors), hard-sided-RV-banned (Lake Louise Soft-Sided).
- **Local**: don't apply ≥4★/≤$$ gate (public gov cheap/lightly-reviewed). Many town/village/county/Lions/Kinsmen-run municipal campgrounds. Special Areas Board (No.2) = local special-municipality.
- **Private**: gate ≥4★/≤$$; skipped seasonal-lease/adults-only/50+ communities (Willowbend/Riverside/Bluebird/Rosewood/Great Canadian Barn Dance), Elks/Moose lodge parks (Didsbury Elks), workforce-only. Legion campgrounds open to public nightly kept (Sunset Legion). EID (Eastern Irrigation District, Rolling Hills) = private.
- **Waterfront**: AB landlocked → only lakefront/riverfront/creekside/pond + lakeview/riverview + not waterfront (NO coastal woods/dunes). AB reservoirs heavily drawn down — measure to beach/high-water edge not drawn-down waterline (open-apron rule caught many lakefronts). Watch off-vocab "creekview" (agents emitted once → map to riverview).

## Plumbing (reused, all ephemeral in /tmp + repo root)
- `append_ab.py` (repo root; = append_bc.py with state=AB, leads→/tmp/ab_leads.json). Throwaway — can delete/re-derive.
- Add batches `/tmp/ab_{prov,federal,local,private}_batches/`; results `/tmp/ab_results/`.
- Waterfront audit `/tmp/ab_wfaudit/` (build script `/tmp/build_ab_wfaudit.py`; batches carry leads; apply `audit/apply_waterfront_audit.py`).

## Remaining
- **Push to origin when the user asks** (push only when asked). No legacy loose ends — fresh-state sweep, inclusion + waterfront both folded in / done. Next province: any (method fully proven, 3 provinces done: ON/BC/AB).
