---
name: project_sk_sweep_handoff
description: Saskatchewan campground sweep — IN PROGRESS (4th Canadian province). Detection+classification done; add-research underway.
metadata: 
  node_type: memory
  type: project
  originSessionId: 16dee5e1-cf07-445f-b6d2-df6e4020c667
---

**Saskatchewan sweep STARTED 2026-07-12** — 4th Canadian province, after [[project_on_sweep_handoff]], [[project_bc_sweep_handoff]], [[project_ab_sweep_handoff]]. Follows [[reference_canada_sweep_adaptation]]. Runs **sequentially** ([[feedback_sequential_sweep_agents]]). Clean fresh-state sweep — SK had 0 entries before. Next id starts **9150** (prev max 9149).

## SK-SPECIFIC RULE (load-bearing): "Regional Park" = LOCAL, not provincial
Saskatchewan **Regional Parks** are run by local Regional Park Authorities (boards of member municipalities) under The Regional Parks Act — NOT the province. RV Life mis-tags ~35 of them as `park_type: provincial`. Reclassify every "X Regional Park" → **local** (analogous to Ontario's Conservation Authorities polluting the provincial tag). True provincial = "Provincial Park" / "Provincial (Rec/Recreation) Site" / "Interprovincial Park" (Cypress Hills) / provincial-forest rec sites (Bronson Forest).

## Detection (DONE)
- RV Life Algolia app `H0LPZK92QJ`, key `88da91e06e8ee5ec4aba26675ac26b99` (same as AB; rotates). Tiled 4×3 bbox lat 49.0–60.05 / lng -110.05 to -101.30, post-filter `region_abbvr=="SK"`. **198 SK hits.** Scripts: `/tmp/sk_detect.py`, `/tmp/classify_sk.py`, `/tmp/build_sk_batches.py`. Hits `/tmp/sk_hits.json`, buckets `/tmp/sk_buckets.json`.
- park_type raw: provincial 91, commercial 59, city 34, canadian 8, county 6.
- **After reclassification** (Regional Park→local; commercial gov-scan→local): **federal 8, provincial 57, local 84, private 49** (= 198). Batches of 8 in `/tmp/sk_batches/{bucket}_NN.json` (27 files: federal 1, provincial 8, local 11, private 7).

## Method notes
- **Ownership**: `canadian`→federal (Parks Canada: Prince Albert NP + Grasslands NP only). Provincial Parks/Rec Sites→provincial (Sask Parks). Regional Parks + city/county/town→local (don't apply ≥4★/≤$$ gate to local). commercial non-gov→private (gate ≥4★/≤$$).
- **Reservation deep links**: SK provincial = **ReserveAmerica `.do`, contractCode `SKPP`**, host `parks.saskatchewan.ca` → `.../campgroundDetails.do?contractCode=SKPP&parkId=<id>` (drop queueittoken). Federal = Parks Canada goingtocamp `reservation.pc.gc.ca`. Regional parks book via Campspot / Let's Camp / phone / FCFS (per-park).
- **Waterfront**: SK landlocked → lakefront/riverfront/creekside/pond + lakeview/riverview + not waterfront (NO coastal woods/dunes). SK reservoirs (Lake Diefenbaker: Danielson/Douglas; Buffalo Pound; Blackstrap) heavily drawn down — measure to beach/high-water edge, open-apron rule.
- Add-research instructions: `audit/add_research_instructions_sk.md` (SK-specific). Append with `append_sk.py` (state=SK, leads→/tmp/sk_leads.json).

## Progress
- **ALL ADDS DONE + pushed: 166 SK entries, ids 9150-9315** (federal 7, provincial 52, local 94, private 13). Every entry has `inclusion_evidence` (inclusion folded in, 0 missing). Detection+classify+batches all done.
- Add-stage skips: ~3 dupes (RV Life overlapping hits for multi-campground parks: Denare Beach=Sawmill Bay, GBH-Anglin=Anderson Point), several tent-only (Trappers/Cold River/Hirtz/Vivian/Big Shell), Sturgeon Weir (unverifiable), ~18 private-gate fails.
- **Reclassifications (agent-corrected ownership):** many RV-Life-mislabeled entries — Regional Parks provincial→local (the big one); "leased provincial rec site" private→provincial (Besant, Borden Bridge, Michel Point/Dore Lake, Nesslin Lake); village/town campgrounds commercial→local (Bonnington Springs/Kenaston, Gull Lake, Hanley, Val Marie, Windthorst, David Laird/North Battleford, Joe Tutt/Radisson, Prairie View/Wheatland non-profit).
- **Waterfront audit: IN PROGRESS.** 25 dry (no-water) entries auto-stamped not-waterfront + committed. 141 water-adjacent split into 18 batches (`/tmp/sk_wfaudit/batch_N.json`, each carries its `lead`); batch 1 running. Apply each with `python3 audit/apply_waterfront_audit.py /tmp/sk_wfaudit/results_N.json`. All entries start at `not waterfront` placeholder → auditor UPGRADES with counting evidence.
- Plumbing: `/tmp/build_sk_wfaudit.py`, results saved to `/tmp/sk_wfaudit/results_N.json`. Commit per batch/group to master.
- **Remaining:** finish 18 waterfront batches → apply → commit → push. Then SK is COMPLETE (inclusion already folded in; no legacy loose ends — fresh state).
