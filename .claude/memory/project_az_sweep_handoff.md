---
name: project_az_sweep_handoff
description: "Arizona campground sweep COMPLETE — research + append + waterfront audit + inclusion all done (287 entries after 1 dup removal, ids 11317-11604). Committed."
metadata: 
  node_type: memory
  type: project
  originSessionId: 73603cb3-7fc8-428f-ba7a-dc64175e112b
---

**Arizona sweep — COMPLETE (2026-07-17).** Research + append + inclusion + waterfront audit
all done. AZ was a near-fresh state (only 1 prior entry: North Rim CG id 275, left as-is).
288 entries were appended (ids 11317-11604); **id 11494 was later removed as a duplicate of
11469 (both "Davis Camp" Mohave County local, same coords) — final count 287** (286 AZ + 1 UT
Lone Rock Beach id 11321, lat 37.016 north of the border → UT). AZ by ownership: federal 129,
private 110, local 30, state 17, hipcamp 1. Every entry carries `inclusion_evidence`.

## Waterfront audit — DONE (this session, 2026-07-17)
- Audit set = **109 water-adjacent entries** (107 with a `lead.water_body` + 2 borderline:
  11462 Gila-River-edge, 11567 retention-pond). The other ~178 are pure dry-desert (no water
  lead; researcher notes already say "satellite shows no water") → left `not waterfront` by
  default-down, no look, no evidence (per policy: skip the look only when no water is near).
- 14 batches of ~8 run **SEQUENTIALLY** via `audit/waterfront_audit_instructions.md` subagents
  (batches/results in gitignored `.az_sweep_wip/wf/`). **52 upgrades from placeholder**: 18
  lakefront, 11 riverfront, 4 creekside, 1 pond, 14 lakeview, 4 riverview. **3 coord fixes**
  (11320 Willow Beach → real desert loops; 11508 Colorado River Oasis; 11600 Wheatfields Lake,
  pin was in the water). All 108 audited entries (109 minus deleted 11494) carry
  `waterfront_evidence`; 0 on-water entries lack evidence.
- **Duplicate found during audit:** both 11469 & 11494 = Davis Camp; excised 11494's block by
  id (no trip_data refs), kept 11469 (riverfront). Applied via
  `python3 audit/apply_waterfront_audit.py .az_sweep_wip/wf/results_all.json`.
- Normalized one invalid agent verdict: 11327 Burro Creek "creekview" (not a vocab value;
  bench-top overlooking the creek canyon → the bluff/bench buffer) → `not waterfront`.
- Reservoir drawdown (Mead/Mohave/Powell/Roosevelt) killed most big-lake on-water (measured to
  beach/high-water edge per gate, but many pads sit atop drawdown benches / behind day-use
  strips → lakeview or not-waterfront). Colorado-River Parker strip & private river parks were
  the richest on-water vein (riverfront).
- **DONE — committed & pushed to master.** `audit/az_leads.json` removed (spent carrier).

## Waterfront parity pass — DONE (287/287 audited)
After the initial audit AZ sat at 108/287 evidence-stamped (only the water-adjacent
set), out of parity with every sibling sweep (NV/NM/etc. stamp evidence on ALL entries,
dry ones included). Ran an 18-batch parity pass (`.az_sweep_wip/wf2/`) over the 179 dry
entries — each got a mandatory satellite look + evidence string. **All 179 confirmed
`not waterfront`** (0 value changes, 0 coord fixes — validates the original water-lead
split caught every on-water site). AZ now **287/287 waterfront-audited**, matching the
100% coverage every other completed state has. Committed & pushed (5a3c27a).
LESSON for future landlocked sweeps: stamp `waterfront_evidence` on the dry entries too
(a quick "satellite: dry loop, no water" look) so the state hits 100% parity in one pass,
rather than splitting water-adjacent-only and leaving a gap.

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
