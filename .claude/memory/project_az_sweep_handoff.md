---
name: project_az_sweep_handoff
description: "Arizona campground sweep — research + append DONE (288 entries, ids 11317-11604), committed & pushed. WATERFRONT AUDIT STILL PENDING (to be run on a different machine). Inclusion folded in at add-time."
metadata:
  node_type: memory
  type: project
---

**Arizona sweep — RESEARCH + APPEND COMPLETE, WATERFRONT AUDIT PENDING (2026-07-17).**
Committed AND pushed to origin/master. AZ was a near-fresh state (only 1 prior entry:
North Rim CG id 275, left as-is). **288 new entries appended, ids 11317-11604**:
**287 AZ + 1 UT** (Lone Rock Beach id 11321 — lat 37.016 is north of the AZ/UT border,
so re-stamped UT; it wasn't in the completed UT sweep). AZ by ownership: **federal 129,
private 110, local 30, state 17, hipcamp 1**. Every entry carries `inclusion_evidence`
(inclusion audit folded in at add-time). **All `waterfront` = the `not waterfront`
placeholder — the waterfront audit has NOT run yet.**

## ⚠️ NEXT STEP (on the other machine): the waterfront audit
1. `git pull` brings down `campgrounds.json` (the 288 entries), this memory, and
   **`audit/az_leads.json`** (288 leads keyed by new id — the seam optimization; carry each
   entry's lead into its audit batch so the agent verifies the already-found per-site map
   instead of re-discovering it).
2. Build waterfront batches of ~8 over ids **11317-11604**, `{id, name, location, waterfront,
   ownership, website, lead}` per entry (lead from `audit/az_leads.json[str(id)]`). ~36 batches.
   Split water-adjacent (has a `lead.water_body` or near known AZ water) from pure dry-desert
   (in-town/fairground → stay `not waterfront` without a look). ~150 of 287 carry a water lead.
3. Run `audit/waterfront_audit_instructions.md` subagents **SEQUENTIALLY, one at a time**
   ([[feedback_sequential_sweep_agents]]). Satellite look mandatory; default-down; record a
   one-line `evidence` per entry.
4. Apply with `python3 audit/apply_waterfront_audit.py <results.json>` (sets `waterfront`,
   fixes mis-pinned `location`/`elevation_meters`, writes `waterfront_evidence` from evidence).
5. Commit "Audit all NN AZ waterfront designations" + push. Update this memory to COMPLETE.
6. `audit/az_leads.json` is a one-time carrier — delete it after the audit (optional cleanup).

## Key AZ facts proven (mirror of NV, plus AZ specifics)
- **park_type `dnr` = BLM (federal) in AZ** — AZ has NO state DNR campgrounds (State Trust land
  is permits, not developed CGs). Verified per entry; USFWS refuges (Kofa, Buenos Aires) also
  come in tagged `dnr`/`national` → still federal.
- **Federal dominates (129):** 6 National Forests (Coconino, Kaibab, Tonto, Apache-Sitgreaves,
  Prescott, Coronado), NPS (Grand Canyon Mather/Desert View, Glen Canyon/Lake Powell Wahweap/
  Lees Ferry, Lake Mead/Mohave Temple Bar/Katherine Landing, Organ Pipe, Chiricahua NM, Canyon
  de Chelly, Navajo NM), BLM (LTVAs **La Posa/Imperial Dam**, Quartzsite 14-day areas Hi Jolly/
  Dome Rock/Scaddan Wash/Plomosa, Gila Box). **HUGE under-23-ft skip rate** on high-elevation
  Sky-Island/Rim/White-Mtn sites (Coronado Mt Lemmon/Graham, many 16-22 ft caps) — 65 federal
  skips, mostly length.
- **Tribal = `private`** per convention: White Mountain Apache (Hon-Dah, Hawley/Horseshoe
  Cienega/Sunrise lakes), Navajo (Wheatfields, Cottonwood at Canyon de Chelly is NPS/Navajo).
- **State (17) = Arizona State Parks & Trails**, reserve via **azstateparks.com own portal (NOT
  rec.gov)**. Plus AZ Game & Fish areas (Willcox Playa, Ben Avery Shooting Facility) → `state`.
- **Local (30):** **Maricopa County Regional Parks** are the gems (Lake Pleasant, Usery Mtn,
  McDowell Mtn, Cave Creek, White Tank, Estrella), plus Pima (Gilbert Ray), **Mohave County
  (Davis Camp** — finally captured here; it's the AZ park dropped from the NV sweep**)**, La Paz
  County (Colorado River strip), many county fairgrounds w/ year-round public RV, city parks
  (Show Low Lake, Kearny, Watson Lake, Constellation/Wickenburg). RV Life mis-tags several
  county/city parks as commercial — gov-name-scan rescued them.
- **Private (110) needed the HARDEST vetting** — AZ is the national capital of 55+/snowbird/
  residential RV resorts (Yuma, Mesa/Apache Junction, Casa Grande, Tucson, Quartzsite, Lake
  Havasu City, Benson). ~130 private candidates SKIPPED as 55+/age-restricted, mobile-home/
  residential, Escapees/Elks/membership clubs, or bare casino overnight lots. Kept genuine
  all-ages transient parks (read each operator's own age policy — "resort" name means nothing).
- **Landlocked — NO coastal designations.** Big waters for the audit: Lake Powell, Lake Mead/
  Mohave (**major drawdown — verify current shoreline**, killed most Mead on-water), Lake Havasu,
  Colorado River (Parker strip: Buckskin Mtn/River Island/Davis Camp/La Paz County), Lake
  Pleasant, the Salt River chain (Roosevelt: Cholla/Windy Hill/Schoolhouse/Bermuda Flat; Apache:
  Burnt Corral/Crabtree; Canyon; Saguaro), Lyman/Roper/Patagonia/Alamo/San Carlos lakes, White
  Mtn lakes (Big Lake, Woods Canyon, Ashurst, Riggs Flat, Fool Hollow, Kaibab, Dogtown), and the
  Verde/Gila/Black/Little-Colorado rivers.

## Plumbing (this session)
- **Consolidated the 8 per-state `append_<st>.py` into ONE `append_state.py`** (`--state AZ
  --leads <path>`; resolves campgrounds.json via its own dir, so machine-independent — the old
  copies hardcoded a wrong `/home/andrew/...` path). `git rm`'d append_{ab,id,mb,nv,or,sk,ut,wa}.py.
  Use `append_state.py` for all future sweeps.
- `audit/add_research_instructions_az.md` (AZ-specific research agent instructions).
- Detection: RV Life Algolia `park` index, bbox AZ → 948 hits → 916 alive → 516 candidates
  (federal 204, state 19, local 33, private 260-gated) → 67 add-batches of 8. Scripts + all
  batch/result files backed up in gitignored `.az_sweep_wip/` (this machine only).
- **Dedup at append:** 15 RV Life double-listings collapsed by coord (<150 m box). **4 were
  FALSE positives** — genuinely distinct neighboring parks 116-190 m apart (Rancho Verde vs
  Verde River RV Resort; Petrified Forest vs Crystal Forest gift-shop CGs; Belly Acres vs Ajo
  Heights; Park Place vs Quartzsite RV Resort) — verified distinct and re-added as ids 11601-11604.
  Lesson: same-town private parks can sit inside the 150 m dedup box; spot-check same-town dedup
  skips before trusting them.
- **Dropped 2 gate-failing reclassifications:** Gila County RV Park (3★) & Sleeping Dog Ranch
  ($$$) came in via the local bucket, reclassified to private, but fail the private ≥4★/≤$$ gate
  → dropped for consistency (private gate applies to anything reclassified INTO private).

PROCESS ran all 67 add batches SEQUENTIALLY per [[feedback_sequential_sweep_agents]]; concise
agent returns (full JSON to /tmp + `.az_sweep_wip/`, short recap to caller) kept context light.
Reservenevada-style US-eDirect note doesn't apply; AZ State Parks uses its own azstateparks.com
portal. See [[project_nv_sweep_handoff]] for the immediately-prior fresh-state pattern.
