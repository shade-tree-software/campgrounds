---
name: project_id_sweep_handoff
description: Idaho campground sweep — COMPLETE. Fresh state, 447 entries (ids 9425-9871), adds + inclusion + waterfront audit all done + pushed.
metadata: 
  node_type: memory
  type: project
  originSessionId: 2f190f1c-07bb-4e79-9669-7f1ed2fc3d0e
---

**Idaho sweep COMPLETE 2026-07-14** — 447 entries (ids 9425-9871), fresh-state sweep; all committed + pushed to origin/master. By ownership: federal 314, private 69, local 40, state 24. Every entry carries `inclusion_evidence` (folded into adds, 447/447) AND `waterfront_evidence` (audit 100%, 447/447). Waterfront: **98 on-water** (51 riverfront, 36 lakefront, 9 creekside, 2 pond) + **72 view** (44 riverview, 28 lakeview) = **170 upgrades** from the not-waterfront placeholder; 277 not-waterfront. ~5 coord fixes during audit. Clean fresh-state sweep — no legacy loose ends. **KEY ID RULES proven: (1) park_type `dnr` = BLM (federal), NOT state DNR — Idaho has no state-DNR campgrounds, state = IDPR parks only; (2) Idaho Power utility parks (CJ Strike/Hells Canyon/Woodhead/McCormick/Cottonwood) = private; (3) heavy USFS river/creek corridors — most canopy-blind forest CGs default-down not-waterfront, on-water reserved for open-apron gravel-bar/reservoir sites + rec.gov per-site shoreline flags.** Reservations: recreation.gov (federal), IDPR via ReserveAmerica/getoutside.idaho.gov, Idaho Power via CampLife. Next state: any.

**Idaho sweep STARTED 2026-07-12.** Clean fresh-state sweep — ID had **0** entries. Next id starts **9425** (prev max 9424). Runs **sequentially** ([[feedback_sequential_sweep_agents]]). Follows the standard fresh-state pipeline (like [[project_wy_sweep_handoff]]/[[project_nm_sweep_handoff]]/[[project_sd_sweep_handoff]]): add with `inclusion_evidence` folded in + `waterfront:"not waterfront"` placeholder, then waterfront audit as its own stage.

## Detection (DONE)
- RV Life Algolia app `H0LPZK92QJ`, key `88da91e06e8ee5ec4aba26675ac26b99`. Tiled 5×4 bbox lat 41.99–49.02 / lng -117.30 to -111.00, post-filter `region_abbvr=="ID"`. **770 ID hits.** Script `/tmp/id_detect.py` → `/tmp/id_hits.json`; classify `/tmp/classify_id.py`; batches `/tmp/build_id_batches.py` → `/tmp/id_batches/{bucket}_NN.json`.
- park_type raw: commercial 309, usfs 202, national 147, state 34, dnr 30, county 21, city 15, coe 7, military 2, us_forest_service 2, provincial 1.
- **Buckets after classify + private gate (≥4★ & ≤$$) + dedup:** federal **357** (45 batches), state **64** (8 batches), local **40** (5 batches), private **85** (11 batches). 2 military skipped; 1 true dup dropped (Malad Summit CG, 0km apart). **69 batches total.**
- `national`/`usfs`/`coe` all → federal (mostly USFS mis-tags; agent assigns exact USFS/BLM/NPS/USACE — all federal). `dnr`→state (IDL/IDFG). `county`/`city`→local + gov-name-scan of commercial.

## Plumbing (DONE)
- `append_id.py` (repo root; state=ID, leads→`/tmp/id_leads.json`; strips `lead` to leads file, appends preserving indentation, validates).
- `audit/add_research_instructions_id.md` (ID authorities: recreation.gov for USFS/BLM/NPS/USACE/Reclamation; IDPR state parks via ReserveAmerica idahostateparks.reserveamerica.com; IDL/IDFG=state; City of Rocks NR=federal).

## ID-specific method notes
- **Federal dominates** (357). Idaho = huge national forests (Boise/Payette/Sawtooth/Salmon-Challis/Nez Perce-Clearwater/Caribou-Targhee/Idaho Panhandle) + BLM + NPS (Craters of the Moon, City of Rocks NR) + USACE (Dworshak, Lucky Peak) + Reclamation reservoirs (Palisades, Ririe, American Falls). Many small forest CGs are FCFS — note it.
- **State**: IDPR state parks (parksandrecreation.idaho.gov) reserve via ReserveAmerica; `dnr`=Idaho Dept of Lands (IDL) + Idaho Fish & Game (IDFG) WMAs — all `state`. Watch: IDFG WMAs may be day-use/hunt-access only → skip if no overnight camping.
- **Cascade** = STATE park (Lake Cascade SP), not federal despite the reservoir.
- Access: gravel forest roads are fine (drive-in); only skip for genuine 4WD-required or all-tiny-tent-sites.

## Progress
- Detection + classify + batches + plumbing DONE. Results saved to `/tmp/id_results/<bucket>_NN.json`; leads accumulate in `/tmp/id_leads.json`.
- **FEDERAL: COMPLETE** — all 45 batches done+committed+**pushed** (284 entries, ids 9425-9708). All 7 ID national forests + BLM + NPS (City of Rocks, Craters Lava Flow) + USACE (Dworshak, Albeni Falls) + Reclamation/Idaho Power (private: McCormick/Hells Canyon Park). Heavy skips for Magruder/high-clearance/boat-in/tent-only/group-only/16ft sites.
- **STATE COMPLETE** — all 8 batches done+committed+pushed (58 entries, ids 9709-9766). IDPR state parks (Lake Cascade ×6 loops, Heyburn ×2, Priest Lake, Farragut, Dworshak, Henrys Lake, Ponderosa, Winchester, Hells Gate, Bruneau Dunes, Massacre Rocks, Bear Lake, Eagle Island new-2025, etc.) + heavy BLM reclass (Idaho `dnr` park_type = BLM river/reservoir sites, NOT state DNR — Salmon/Lemhi/Clearwater/Blackfoot rivers, Magic/Mackay/CJ Strike/Brownlee reservoirs) + Idaho Power private (CJ Strike Locust/Scout/North). Skips: Castle Rocks SP (dup of Smoky Mountain CG 9428), FAMCAMP (military), yurts. **KEY ID RULE: park_type `dnr` = BLM (federal), NOT state — Idaho has no state-DNR campgrounds; state = IDPR parks only.**
- **LOCAL COMPLETE** — all 5 batches done+committed+pushed (39 entries, ids 9767-9805). County parks (Twin Falls/Bingham/Jefferson/Madison/Fremont/Latah/Bonner...), city RV parks, county fairgrounds (year-round camping confirmed, not event-only), Idaho Power reclassed private where they slipped in. Skips: dup names (O'Connor=Caldwell), Jim Johnson=BLM reclass.
- **ALL ADDS COMPLETE** — 447 ID entries, ids 9425-9871 (federal 314, private 69, local 40, state 24), all committed+pushed, all carry inclusion_evidence. Private bucket: many Elks/casino/residential skips; several cross-bucket dups caught (McCormick 9602, Powell 9662, Woodhead, Osprey).
- **Next: WATERFRONT AUDIT (IN PROGRESS).** Build script `/tmp/build_id_wfaudit.py` → `/tmp/id_wfaudit/` (52 audit batches of ~8 + dry_results.json). 34 dry (no-water) entries auto-stamped not-waterfront + committed. **413 water-adjacent entries need the satellite/per-site audit (52 batches).** Run `audit/waterfront_audit_instructions.md` subagents per batch, save results to `/tmp/id_wfaudit/results_N.json`, apply with `python3 audit/apply_waterfront_audit.py <results>`. Then commit + push + write COMPLETE handoff. Then waterfront audit (build `/tmp/build_id_wfaudit.py` from a prior state's, carry `/tmp/id_leads.json` leads, apply `audit/apply_waterfront_audit.py`). A few private-owned entries landed in the federal buckets (Silver Creek Plunge, McCormick Park, Hells Canyon Park) + a few local (Moose Creek Reservoir); these are already in the DB — waterfront audit covers all new ids regardless of bucket.
- Task list ids: #2 federal, #3 state, #4 local, #5 private, #6 waterfront audit.
- **Name disambiguation applied** where two ID campgrounds share a name: Riverside (Idaho City/Henrys Fork/Salmon River) + Riverside Park; Park Creek (Lowman) vs Salmon-Challis Park Creek; Flat Rock (Island Park) vs Yankee Fork Flat Rock; Beaver Creek (Stanley). Watch for more (Big Springs Caribou already suffixed).
