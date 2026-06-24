---
name: project_ar_sweep_handoff
description: "Arkansas campground sweep COMPLETE — all 4 buckets added+audited (232 entries, ids 5126-5357)"
metadata: 
  node_type: memory
  type: project
  originSessionId: ef827276-a332-4f0b-940c-edb10b3a783c
---

**COMPLETE (2026-06-24).** Arkansas state-by-state sweep: all 4 buckets added + waterfront-audited + committed. AR went from 1 to 233 entries (232 added, ids 5126-5357). By ownership: federal 101, private 84, state 29, local 19. Every new entry carries a `waterfront_evidence` string (fully audited). Detection via RV Life Algolia (app `H0LPZK92QJ`, key from campgrounds.rvlife.com HTML, index `park`, AR string bbox `33.0,-94.62,36.5,-89.64` → 512 AR hits).

- **State** (5126-5154, 29): AR State Parks. Dropped 4 COE-mislabeled, 2 Cossatot tent units, Lone Pine, Logoly.
- **Federal** (5155-5255, 101): USACE 85 (Beaver/Bull Shoals/Norfork/Greers Ferry/DeGray/Greeson/Millwood/Dierks-Gillham-DeQueen/Lake Ouachita/Arkansas River pools/Nimrod/Blue Mtn) + USFS 11 + NPS 5 (Gulpha Gorge + Buffalo NR).
- **Private** (5256-5338, 83): commercial gated price_level<=2 AND star>=4, then vetted; dropped membership/residential/seasonal/event-only.
- **Local** (5339-5357, 19): city/county/municipal; 4 caught during private vetting (Berryville, Fairfield Bay, Holiday Island, Craighead Forest).

**KEY TECHNIQUE discovered (reusable for any USACE sweep):** rec.gov per-site API `https://www.recreation.gov/api/camps/campgrounds/<facility_id>/campsites` carries an authoritative `site_details_map.proximity_water` flag (Lakefront/Riverfront) that COUNTS as gate evidence — USACE PDF site maps are Akamai-403-blocked from the sandbox.

Lake Sylvia (USFS-built, now AR State Parks-run) was added as a STATE entry (id 5358) after the main sweep — management transferred from USFS to AR State Parks.

Per-bucket workflow used: research agent (vet+pin+elevation+waterfront lead) → append with `waterfront: "not waterfront"` placeholder → commit add → fan out `audit/waterfront_audit_instructions.md` subagents over new ids (batches of 8, SEQUENTIAL per [[feedback_sequential_sweep_agents]]) → `python3 audit/apply_waterfront_audit.py <results>` → commit audit. See [[feedback_waterfront_evidence_in_json]], [[feedback_campground_vetting_discipline]], [[reference_rvlife_price]], [[reference_local_campground_method]].
