---
name: project_ut_sweep_handoff
description: Utah campground sweep — COMPLETE. Near-fresh state (2 legacy Zion/DHP entries), 321 new entries (ids 9872-10192), adds + inclusion + waterfront audit all done + pushed.
metadata: 
  node_type: memory
  type: project
  originSessionId: 2f190f1c-07bb-4e79-9669-7f1ed2fc3d0e
---

**Utah sweep COMPLETE 2026-07-14** — 321 new entries (ids 9872-10192), all committed + pushed to origin/master. Near-fresh state: UT had only **2 legacy entries** (274 Watchman/Zion, 281 Kayenta/Dead Horse Point SP), which were stamped with `inclusion_evidence` during setup (they already had `waterfront_evidence`). By ownership (new): **federal 227, state 43, private 43, local 8**. Every new entry carries `inclusion_evidence` (folded into adds, 321/321) AND `waterfront_evidence` (audit 100%, 321/321; all 323 UT entries audited). Waterfront: **100 upgrades** from the not-waterfront placeholder — **43 on-water** (20 riverfront, 16 lakefront, 7 creekside) + **57 view** (46 lakeview, 11 riverview); 221 not-waterfront. **2 coord fixes** during audit (Oaks Park, Quail Creek SP — both were pinned on day-use/boat-ramp lots). Clean near-fresh sweep — no legacy loose ends.

**KEY UT RULES proven:**
1. **RV Life `park_type: dnr` = BLM (federal), NOT state DNR** — Utah has no state-DNR campgrounds; `state` = Utah State Parks (IDPR-equivalent) only. Same as ID/NM. BLM is *enormous* in UT: the Moab river corridors (Colorado River SR-128: Goose Island/Big Bend/Hittle Bottom/Dewey Bridge/Hal Canyon/Drinks Canyon; Potash Rd SR-279: Kings/Williams Bottom/Gold Bar), Sand Flats, Canyon Rims (Windwhistle/Hatch Point), Little Sahara (Oasis/White Sands/Jericho), Calf Creek (Grand Staircase-Escalante NM), Red Cliffs, Simpson Springs, Ken's Lake, Henry Mtns.
2. **Federal DOMINATES (227/321)** — 5 NPS parks (Zion, Bryce, Arches Devils Garden, Canyonlands Needles/Willow Flat, Capitol Reef Fruita) + NMs (Natural Bridges, Hovenweep, Cedar Breaks, Dinosaur Green River) + Glen Canyon NRA (Bullfrog) + Flaming Gorge NRA (Ashley NF-run) + 5 national forests (Dixie, Fishlake, Manti-La Sal, Uinta-Wasatch-Cache, Ashley) + BLM + Reclamation reservoirs.
3. **Utah State Parks** reserve via **ReserveAmerica** (`utahstateparks.reserveamerica.com`, deep link `.../campgroundDetails.do?contractCode=UT&parkId=<id>`). Many big-park multi-campground splits (Bear Lake ×4, Scofield ×2, Yuba ×2, Willard Bay ×3, Antelope Island ×2, Fremont Indian ×2, Echo Dry Hollow + Red Rock Marina, Dead Horse Point Kayenta[legacy]+Wingate).
4. RV Life mis-tags several **USFS/BLM campgrounds as `commercial`** (Duck Creek, White Bridge, Soldier Creek, Sand Island) — the private-bucket agent caught + reclassed them to federal. Also reclassed Kolob Reservoir (RV Life `county` → private), Minersville (→ Beaver County local), Salamander Flat (→ USFS federal).
5. **Utah reservoirs are heavily drawn down** — audit measured to the beach/high-water edge, not the drawn-down waterline (per the CLAUDE.md rule). No Great Lakes/ocean in UT so coastal dunes/woods N/A (the agent correctly held Antelope Is Bridger Bay's flat beach to lakeview, not coastal dunes).

**Plumbing:** `append_ut.py` (repo root, state=UT, leads→/tmp/ut_leads.json), `audit/add_research_instructions_ut.md`, detection `/tmp/ut_detect.py`+`classify_ut.py`+`build_ut_batches.py`, waterfront `/tmp/build_ut_wfaudit.py`→`/tmp/ut_wfaudit/`. Detection: 607 RV Life hits → federal 274/state 44/local 10/private 53 (223 gated out, 2 military). Follows the standard fresh-state pipeline (like [[project_id_sweep_handoff]]/[[project_wy_sweep_handoff]]). Sequential agents per [[feedback_sequential_sweep_agents]]. Next state: any.

**Side task this session:** added the `tid_windows` GPS feature (sub-day tid override for trip 92, see the ekko_trips_app.py `_tid_window_tsts`/`_apply_tid_choice` helpers) and extended the `coastal dunes` waterfront rule to big inland lakes with genuine dune fields (re-audited MB: Grand Beach → coastal dunes). Both pushed.
