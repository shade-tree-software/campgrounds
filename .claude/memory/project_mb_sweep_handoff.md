---
name: project_mb_sweep_handoff
description: Manitoba campground sweep — COMPLETE (5th Canadian province). 109 entries, adds + inclusion + waterfront audit all done + pushed.
metadata: 
  node_type: memory
  type: project
  originSessionId: 16dee5e1-cf07-445f-b6d2-df6e4020c667
---

**Manitoba sweep COMPLETE 2026-07-12** — 109 entries (ids 9316-9424), federal 3 / provincial 53 / local 31 / private 22; all pushed to origin/master. Every entry carries `inclusion_evidence` (folded into adds) AND `waterfront_evidence` (audit 100%, 0 missing). Waterfront: 16 lakefront, 4 riverfront (=20 on-water), 16 lakeview, 1 riverview (17 view), 72 not-waterfront (**37 upgrades**; ~3 coord fixes: Nutimik, Steep Rock, +1). Clean fresh-state sweep — no legacy loose ends. **UPDATE 2026-07-14: the coastal-dunes rule was extended to any water body large enough to build a genuine wind dune field (incl. big inland lakes like Lake Winnipeg/Manitoba), and MB's big-lake not-on-water entries were re-audited — Grand Beach (9333) flipped not-waterfront → `coastal dunes` (genuine 12m Lake Winnipeg dune field). Winnipeg Beach/Hecla/Camp Morton/Hnausa/Manipogo unchanged. `coastal woods` stays Great-Lakes/ocean only.** (Superseded the original "Lake Winnipeg is inland → no coastal override, Grand Beach not-waterfront" call.) Reservations via goingtocamp (manitoba.goingtocamp.com); federal=Riding Mountain NP; Winnipeg River campgrounds=riverfront. 6 Canadian provinces now done: ON/BC/AB/SK/MB. Next province: any.

**Manitoba sweep STARTED 2026-07-12** — 5th Canadian province, after ON/BC/AB/[[project_sk_sweep_handoff]]. Follows [[reference_canada_sweep_adaptation]]. Runs **sequentially** ([[feedback_sequential_sweep_agents]]). Clean fresh-state sweep — MB had 0 entries. Next id starts **9316** (prev max 9315).

## MB-specific method notes
- **Reservation = goingtocamp (Platform A SPA), host `manitoba.goingtocamp.com`** — deep link `.../create-booking/results?resourceLocationId=<parkId>&mapId=<campgroundId>&bookingCategoryId=0` (both are big NEGATIVE ints from the goingtocamp API; `/api/resourceLocation` for parkId, `/api/maps` for mapId). Per [[reference_canada_sweep_adaptation]] the MB goingtocamp API had 45 parks with **45/45 gpsCoordinates filled** (good coord authority). Official park pages: gov.mb.ca/nrnd/parks / manitobaparks.com.
- **NO SK-style "Regional Park" class** — Manitoba provincial parks are provincial. But RV Life mis-tags a few town campgrounds `provincial` (e.g. Gilbert Plains) → agent reclasses to local.
- **Federal = Riding Mountain NP only** (Wasagaming + Lake Audy/Moon/Deep Lake), Parks Canada via reservation.pc.gc.ca.
- **Waterfront**: MB landlocked-ish — Lake Winnipeg/Manitoba are HUGE inland lakes with big beaches (Grand Beach, Winnipeg Beach dunes). **Since 2026-07-14 the `coastal dunes` override DOES apply to big inland lakes with a genuine wind dune field** (Grand Beach 9333 = coastal dunes); `coastal woods` still Great-Lakes/ocean only. Otherwise judge by standard open-apron/buffer + distance rules (lakefront/riverfront/creekside/pond + views + not waterfront).

## Detection (DONE)
- RV Life Algolia app `H0LPZK92QJ`, key `88da91e06e8ee5ec4aba26675ac26b99` (same). Tiled 4×3 bbox lat 48.99–60.05 / lng -102.05 to -95.10, post-filter `region_abbvr=="MB"`. **129 MB hits.** Scripts `/tmp/mb_detect.py`, `/tmp/classify_mb.py`, `/tmp/build_mb_batches.py`; hits `/tmp/mb_hits.json`, buckets `/tmp/mb_buckets.json`.
- park_type raw: provincial 56, commercial 48, city 20, canadian 4, county 1.
- **Buckets: federal 4, provincial 56, local 25, private 44** (129). Batches of 8 in `/tmp/mb_batches/{bucket}_NN.json` (18 files: federal 1, provincial 7, local 4, private 6).
- **DEDUP watch**: Paint Lake PP appears TWICE in RV Life (2 listings) → keep one. Big parks have many distinct named-lake campgrounds (legit separate).

## Plumbing
- `append_mb.py` (repo root; state=MB, leads→/tmp/mb_leads.json). `audit/add_research_instructions_mb.md` (MB authorities, goingtocamp). Waterfront audit later: build `/tmp/build_mb_wfaudit.py` from `/tmp/build_sk_wfaudit.py` (s/SK/MB/, ids/leads), apply `audit/apply_waterfront_audit.py`.

## Progress
- Detection+classify+batches DONE. **Add-research: federal batch (4 RMNP) launched, running.** Then provincial (7), local (4), private (6) sequentially. Commit per batch to master; push when milestone. Then waterfront audit (18-ish batches) + it's inclusion-folded-in so no separate inclusion pass.
