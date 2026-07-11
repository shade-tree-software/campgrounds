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

## Progress (as of 2026-07-10)
- **ALL ADD BUCKETS DONE + committed**: BC total **417 entries, ids 8372-8788** (provincial 197, private 155, local 53, federal 11, hipcamp 1). Last add commit 71880f8.
  - provincial 191 (parts 1-10), federal 11 (1ae6d49), local 33 (290d781), private 182 across 25 batches (parts 1-11: 1462fa2/f6498df/e374c3d/a8e4e50/6823910/a321145/e0fbb25/8401727/f97bad0/94787b1/71880f8).
- **Rondalyn cleanup**: research agent running (was dropped by private batch 1). Bank result to private if add.
- **WATERFRONT AUDIT: IN PROGRESS** — 398 water-adjacent BC entries → **50 batches at `/tmp/bc_wfaudit/batch_N.json`** (built from /tmp/bc_leads.json; 19 dry in-town entries stay not-waterfront by default, ids in /tmp/bc_wfaudit/dry_ids.json). Run `audit/waterfront_audit_instructions.md` agents sequentially, save results `/tmp/bc_wfaudit/results_N.json`, apply with `python3 audit/apply_waterfront_audit.py <results.json>`, commit in chunks. NOT yet started applying.
- Push: NOT done yet (push only when asked).

## (old provincial detail below)

## Resume
Launch next pending batch → append_bc.py → repeat. Commit per bucket ("Add BC <bucket> bucket: N campgrounds"). After all buckets, waterfront-audit all BC ids and commit. Push when asked.
