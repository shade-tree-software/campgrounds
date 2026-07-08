---
name: project_on_sweep_handoff
description: "Ontario campground sweep — COMPLETE (the Canada pilot). 207 entries, all buckets + waterfront audit done."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20c70146-147e-4b0f-a61a-d96ad63bde97
---

**Ontario is COMPLETE (2026-07-08)** — the first Canadian province sweep and the pilot for [[reference_canada_sweep_adaptation]]. Run sequentially ([[feedback_sequential_sweep_agents]]).

## Result: 207 entries, ids 8164-8371 (less 8305, a removed duplicate)
By ownership: **provincial 98, local 56, federal 2, private 51**. (Provincial incl. Ontario Parks + St. Lawrence Parks Commission + Fort William Historical Park, all Ontario Crown agencies.)

Commits: provincial 4b02934, federal 43209fd, local 84197a6, private 4f86a94, waterfront-audit+dup-removal 6c0cfed. **NOT yet pushed** (push when asked).

## Waterfront audit: 100% (207/207), 93 upgrades
52 on-water (20 lakefront, 12 riverfront, 8 coastal woods, 5 bayfront, 3 pond, 2 creekside, 2 coastal dunes) + 41 view (32 lakeview, 6 riverview, 3 bayview); 114 held not-waterfront (rigorous default-down — RV loops behind day-use beaches/treelines/bluffs/gorges). 4 coord fixes. Every entry carries `waterfront_evidence`. Great-Lakes coastal cases worked: Long Point & Presqu'ile (coastal dunes); Inverhuron/Pancake Bay/Agawa Bay/Hattie Cove/Neys/Norfolk CA/Brucedale/MacKenzie (coastal woods).

## Inclusion: folded into adds (every entry has inclusion_evidence) — no separate pass.

## Duplicate removed: id 8305 Meaford Harbour Campground = dup of 8303 Memorial Park (Meaford runs only one campground). No trip_data refs.

## Reusable plumbing (in repo / /tmp)
- `append_on.py` (repo root) — appends add-research results, assigns ids, unescapes `&amp;`, records leads to /tmp/on_leads.json. Untracked (ephemeral tool).
- Detection `/tmp/on_detect.py` (tiled bbox, `insideBoundingBox=[[...]]` DOUBLE brackets), classify `/tmp/classify_on.py`, goingtocamp `/tmp/ggc_on.py`.
- Waterfront audit batches `/tmp/on_wfaudit/batch_N.json` + `results_N.json`; combined `results_ALL.json`; applied via `audit/apply_waterfront_audit.py`.

## Pilot lessons (folded into reference_canada_sweep_adaptation)
- RV Life scatters Conservation-Authority parks across provincial/commercial/canadian tags — all are **local**; goingtocamp-table match is the provincial discriminator; the add-agent corrects ownership per entry.
- goingtocamp one-click deep-links auto-matched (create-booking?resourceLocationId=&mapId=); ReserveAmerica (SK/PEI-style) + camp.zone + LetsCamp + CampLife + Campspot + PerfectMind all appear as CA/municipal booking systems.
- St. Lawrence Parks Commission + Fort William Historical Park = provincial Crown agencies (not local/private).

## Next Canadian province
BC is the natural second pilot (Platform-A goingtocamp, big). Or any province — the method is proven. See [[reference_canada_sweep_adaptation]] for per-province reservation systems + ownership mapping.
