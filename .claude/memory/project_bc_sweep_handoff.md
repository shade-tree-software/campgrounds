---
name: project_bc_sweep_handoff
description: "British Columbia campground sweep — IN PROGRESS (2nd Canadian province). Bucket status, ids, plumbing, resume steps."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20c70146-147e-4b0f-a61a-d96ad63bde97
---

**British Columbia sweep STARTED 2026-07-08** — second Canadian province, after [[project_on_sweep_handoff]] (Ontario COMPLETE). Follows [[reference_canada_sweep_adaptation]]. Run **sequentially** ([[feedback_sequential_sweep_agents]]). Ontario's 6 commits are pushed; BC ids start at **8372**.

## Scope (446 candidates, RV Life detect, ~2× Ontario)
- **provincial 196** — BC Parks + RSTBC Crown rec sites. ownership `provincial`. 25 batches `/tmp/bc_provincial/batch_N.json` (131 deep-link matched to camping.bcparks.ca).
- **private 198** — commercial passing ≥4★ AND ≤$$ gate (356 commercial failed / mislabeled). 25 batches `/tmp/bc_private/`.
- **local 40** — city 32 + county 6 + regional-district reclassifications. 5 batches `/tmp/bc_local/`.
- **federal 12** — Parks Canada (Glacier: Illecillewaet/Loop Brook/Hoodoo Creek; Yoho: Kicking Horse/Monarch/Hoodoo; Kootenay: Redstreak/McLeod Meadows/Marble Canyon; Pacific Rim: Green Point; Gulf Islands: McDonald/Prior Centennial). 2 batches `/tmp/bc_federal/`.

## BC-specific gotchas
- **BC Parks goingtocamp table WORKS** (camping.bcparks.ca/api/resourceLocation, browser-UA): 145 parks, resourceLocationId + rootMapId. Deep link = `https://camping.bcparks.ca/create-booking/results?resourceLocationId=<rid>&mapId=<rootMapId>&bookingCategoryId=0`. Same Platform-A as Ontario.
- **Marine / walk-in / boat-in units are common** on the coast/islands (Montague Harbour, Juan de Fuca except China Beach) — SKIP unless a drive-in car campground exists.
- **RSTBC** (Recreation Sites and Trails BC, sitesandtrailsbc.ca) Crown forest rec sites = `provincial` (Crown land, provincial admin — NOT federal). **Regional District / municipal** parks = `local` (name-scan: "Regional District", "District/City/Town/Village of").
- Pacific **ocean** coast + big lakes = Great-Lakes-equivalent for the coastal-woods/dunes waterfront rule.

## Plumbing (reused from ON)
- Detection `/tmp/bc_detect.py` (tiled bbox, `insideBoundingBox=[[...]]`). Classify `/tmp/classify_bc.py`. goingtocamp raw `/tmp/bc_ggc_raw.json`.
- `append_bc.py` (repo root; = append_on.py with state=BC, leads → /tmp/bc_leads.json). Results kept in `/tmp/bc_results/`.
- Add-research agent prompt: BC overrides on `audit/add_research_instructions.md` (see the batch-1 prompt).
- Waterfront audit at end: build batches carrying leads from /tmp/bc_leads.json, run `audit/waterfront_audit_instructions.md`, apply `audit/apply_waterfront_audit.py`.

## Progress
- **provincial batches 1-8 DONE + committed** (61 entries, ids 8372-8432; commits fdfd6c5 part1 8372-8403, 6e951fd part2 8404-8425, + batch 8 uncommitted-then-part3). Vancouver Island/Gulf Islands/Sunshine Coast/Fraser Valley/Okanagan/Similkameen/Kootenays done. Reclassifications so far: Kearsley Creek→local, sẁiẁs/Haynes Point→private. Skips: Whitworth Horse Camp, Skyview($$$), Conkle Lake(RV-access).
- provincial batches 9-25: PENDING. federal/local/private: PENDING. Waterfront audit: PENDING (after all adds).
- Checkpoint-commit every ~3-4 batches ("Add BC provincial bucket (part N)").

## Resume
Launch next pending batch → append_bc.py → repeat. Commit per bucket ("Add BC <bucket> bucket: N campgrounds"). After all buckets, waterfront-audit all BC ids and commit. Push when asked.
