---
name: project_id_sweep_handoff
description: Idaho campground sweep — IN PROGRESS. Fresh state (0 prior entries). Detection+plumbing done; add-research running federal first.
metadata: 
  node_type: memory
  type: project
  originSessionId: 2f190f1c-07bb-4e79-9669-7f1ed2fc3d0e
---

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
- Detection + classify + batches + plumbing DONE. **Add-research: NOT yet started** — begin federal_01, sequential, commit per batch to master. Then state (8), local (5), private (11). Then waterfront audit (build `/tmp/build_id_wfaudit.py` from a prior state's, carry `/tmp/id_leads.json` leads, apply `audit/apply_waterfront_audit.py`).
- Task list ids: #2 federal, #3 state, #4 local, #5 private, #6 waterfront audit.
