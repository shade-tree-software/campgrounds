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

## Progress (as of 2026-07-08)
- **provincial DONE + committed**: 191 entries (ids 8372-8562, all 25 batches; parts 1-10, commits fdfd6c5/6e951fd/c11e005/9ac3958/6a80ad6/4fe4e4d/1f7dd2f/a7e806c/f62bf5e/60b6802). 189 provincial + 2 reclassified local (Kearsley Creek, Cumberland Lake, Sudeten) — well, provincial-tagged became mostly provincial; reclassifications: Kearsley/Cumberland/Sudeten→local, sẁiẁs/Haynes Point→private.
- **federal DONE + committed** (1ae6d49): 11 Parks Canada (ids 8563-8573). Skip: Kootenay Marble Canyon (<15ft).
- **local DONE + committed** (290d781): 33 (ids 8574-8606). Forest Rose→provincial, Monkman RV→private reclassified.
- **private IN PROGRESS** (`/tmp/bc_private/`, 25 batches, 198 cands): batches 1-2 done+appended (ids 8607-8620, NOT yet committed). Fairy Lake/Maple Grove RSTBC→provincial. **CLEANUP PENDING: Rondalyn Resort** (dropped by batch-1 agent) stashed in `/tmp/bc_private/cleanup.json` — research + append before finishing.
- **Waterfront audit: PENDING** — run over ALL BC ids (8372+) after private done; leads in /tmp/bc_leads.json.
- BC total so far: 249 entries. Checkpoint-commit private every ~4 batches.

## (old provincial detail below)

## Resume
Launch next pending batch → append_bc.py → repeat. Commit per bucket ("Add BC <bucket> bucket: N campgrounds"). After all buckets, waterfront-audit all BC ids and commit. Push when asked.
