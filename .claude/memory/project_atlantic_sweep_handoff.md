---
name: project_atlantic_sweep_handoff
description: "Atlantic Canada sweep (NB/NS/PE/NL) — COMPLETE. 261 adds, waterfront + inclusion 100%, committed (not pushed)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3cab67-a02e-4507-bbcc-335279c4c558
  modified: 2026-07-24T23:37:39.120Z
---

**Atlantic Canada sweep COMPLETE 2026-07-24** — first Atlantic Canada coverage,
all four provinces in one pass (NB/NS/PE/NL). **261 entries, ids 12824-13084.**
Fresh-state sweep (0 prior Atlantic entries). Waterfront 100% + inclusion 100%
(every entry carries both evidence fields). **Committed to master, NOT yet pushed.**
3 commits: `e456d67` research instructions, `29c8ec0` the 261 adds, `596c044`
waterfront audit. Ran **sequentially** ([[feedback_sequential_sweep_agents]]).

By province: NB 77, NS 84, PE 25, NL 75. By ownership: private 160, local 32,
federal 20, provincial 49. Detection tiled per-province RV Life bboxes → 399
unique hits; private gated on the **CAD-corrected** affordable rate (≤ ~$55 CAD ≈
$40 USD AND ≥4★) per [[reference_rvlife_price_cad]] — folded into the sweep from
the start (not a later top-up). 278 candidates researched over 37 batches
(provincial 8, federal 4, local 3, private 22) → 261 adds / 16 skips + 1 dup.

Waterfront: 133 upgrades (80 on-water: 31 bayfront, 17 riverfront, 14 lakefront,
8 pond, 8 coastal woods, 2 coastal dunes; 53 view: 37 bayview, 11 riverview, 5
lakeview), 128 not waterfront, 1 coord fix (Shubie). **Coastal woods/dunes richly
apply here** (Fundy/Bay of Chaleur/Atlantic/Gulf of St. Lawrence): PEI dune fields
(Cavendish, Cedar Dunes), NS Atlantic (Broad Cove, MacLeod's Beach), NL Atlantic
(Blow Me Down, Frenchman's Cove, Green Point, Shallow Bay), NB (Côte-à-Fabien,
North Head) — all confirmed genuine ocean/Gulf shore (never inland).

## Atlantic-specific rules (baked into audit/add_research_instructions_atlantic.md)
- **Four provincial park systems = `provincial`:** Parks NB/NS (both goingtocamp),
  PEI Provincial Parks, NL Provincial Parks. **NL nuance:** most NL provincial
  parks are run by **private concessionaires under licence on provincial park
  land** — land/designation is provincial so ownership stays **provincial** (note
  the concessionaire). Flatwater Pond is the exception (former provincial park, now
  a reserve, privately operated → private).
- **`federal` = Parks Canada only:** Fundy & Kouchibouguac (NB), Kejimkujik & Cape
  Breton Highlands (NS), PEI NP (Cavendish/Stanhope), Gros Morne & Terra Nova (NL).
  reservation.pc.gc.ca (goingtocamp). Several sub-23-ft skips in Cape Breton
  Highlands (Corney Brook/Ingonish Beach/MacIntosh Brook cap ~21 ft).
- **`local`:** municipal/town/village parks + **Lions/Kinsmen/service-club** parks
  on municipal land (many RV-Life "commercial"/"city" mistags rescued here).
- **`private`:** commercial, First Nations/Mi'kmaq-run, utility. Seasonal-park trap
  is the #1 private risk (kept only when a real nightly transient inventory exists).
- park_type: RV Life uses `provincial`/`city`/`canadian`/`national`/`commercial`;
  `canadian`+`national` → Parks Canada (federal). Many mislabels — agents reclassify.

## Plumbing (reusable)
- Detection/classify scratch scripts: `detect_atl.py` / `classify_atl.py` (RV Life
  Algolia app `H0LPZK92QJ`, key `88da91e06e8ee5ec4aba26675ac26b99`, valid 7/2026).
- Batches were bucketed by OWNERSHIP (mixed provinces), so results had to be
  **re-tagged to province** from the matching candidate's `prov` (zip results[i]
  with batch[i]) before `append_state.py --state XX` per province. Remember this if
  reusing an ownership-bucketed layout.
- Waterfront audit: `audit/waterfront_audit_instructions.md`, apply with
  `audit/apply_waterfront_audit.py <merged.json>`. **apply script reads ONE file
  arg** — merge all batch results into one JSON array first. **Gotcha:** if an agent
  records `current` as its final value (not the true 'not waterfront' placeholder),
  the apply skips the edit and the verify-assert fails; normalize every result's
  `current` to 'not waterfront' before applying (all fresh entries are placeholders).

## Remaining frontier
US: only **AK** and **HI** have zero entries. Canada: only the **3 territories**
(YT/NT/NU) remain — Atlantic is now done. Everything else in the DB is 100%
waterfront + inclusion audited.
