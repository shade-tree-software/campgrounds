---
name: project_on_sweep_handoff
description: "Ontario campground sweep — IN PROGRESS (the Canada pilot). Bucket status, id ranges, plumbing, and how to resume."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20c70146-147e-4b0f-a61a-d96ad63bde97
---

**Ontario is the first Canadian province sweep** (the pilot for [[reference_canada_sweep_adaptation]]). Started 2026-07-07. Run **sequentially** ([[feedback_sequential_sweep_agents]]) — user chose sequential over parallel for this sweep.

## Scope (230 candidates, RV Life detect, ids start 8164)
- **provincial 102** — Ontario Parks + St. Lawrence Parks Commission. ownership `provincial`. 13 batches `/tmp/on_provincial/batch_N.json`.
- **local 61** — Conservation Authorities + city + county. ownership `local`. 8 batches `/tmp/on_local/`.
- **federal 7** — Parks Canada (park_type `canadian`). 1 batch `/tmp/on_federal/`.
- **private 60** — commercial passing ≥4★ AND ≤$$ gate (330 commercial failed the gate, dropped). 8 batches `/tmp/on_private/`.

## Progress
- **provincial bucket COMPLETE + COMMITTED** (commit "Add ON provincial bucket: 100 campgrounds (ids 8164-8263)"): 100 entries, 96 provincial + 4 reclassified local (C.M. Wilson 8168, Brant 8171, Elora Gorge 8173, Crowe Bridge 8221). All 13 batches added. NOT yet waterfront-audited (placeholder + leads in /tmp/on_leads.json).
- **federal bucket** (`/tmp/on_federal/batch_1.json`, 7 cands): IN PROGRESS. Mixed — Parks Canada (Cyprus Lake/Bruce Peninsula, Hattie Cove/Pukaskwa, Glen Rouge/Rouge NUP) = federal; Wawanosh/Waterford North/Warsaw Caves = mis-tagged CAs = local; Point Pelee oTENTik = skip.
- **local bucket** (`/tmp/on_local/`, 8 batches, 61 cands) + **private bucket** (`/tmp/on_private/`, 8 batches, 60 cands): PENDING.
- **Waterfront audit**: deferred to end — run ONCE over all ON ids (8164+) after all buckets added. Leads in /tmp/on_leads.json (ephemeral; audit can re-discover if lost).

## Key pilot findings (fold into reference_canada_sweep_adaptation)
- RV Life scatters Ontario **Conservation Authority** parks across `provincial`/`commercial`/`canadian` tags — all are **local**. goingtocamp-table match is the provincial discriminator; the add-agent corrects ownership per entry.
- goingtocamp deep-link auto-match worked (93/102 provincial). append_on.py unescapes `&amp;`.

## Plumbing (all reusable)
- Detection: `/tmp/on_detect.py` (tiled bbox — Ontario needs a lat/lng grid to beat Algolia's 1000-hit cap; **`insideBoundingBox=[[...]]` needs DOUBLE brackets**). Algolia key rotates; extract from any rvlife park page.
- Classifier: `/tmp/classify_on.py` — buckets on2 park_type + goingtocamp-table name-match + "conservation" scan. Writes `/tmp/on_<bucket>/batch_N.json`.
- goingtocamp deep-links: `/tmp/ggc_on.py` (fetch `/api/resourceLocation` with browser UA). Deep link = `https://reservations.ontarioparks.ca/create-booking/results?resourceLocationId=<rid>&mapId=<rootMapId>&bookingCategoryId=0`, matched into batches by park name.
- Add-research agent prompt: reuse the batch-2 prompt (Ontario overrides on `audit/add_research_instructions.md`); just swap the batch path. Per batch ~10-11 min.
- Append: `python3 append_on.py <results.json>` — assigns ids from max+1, writes canonical fields WITHOUT waterfront_evidence, records `lead`+location per id to `/tmp/on_leads.json` for the audit stage. Results files kept in `/tmp/on_results/`.
- Waterfront audit (after a bucket is added): build batches carrying each id's `lead` from `/tmp/on_leads.json`, fan out `audit/waterfront_audit_instructions.md`, apply with `audit/apply_waterfront_audit.py`.

## To resume
Launch the next pending batch through the add-research agent → `append_on.py` → repeat. Commit per bucket ("Add ON <bucket> bucket: N campgrounds"). After each bucket's adds, run the waterfront audit over its new ids and commit ("Audit all NN ON <bucket> waterfront designations"). Inclusion is folded into add (inclusion_evidence written at add time).
