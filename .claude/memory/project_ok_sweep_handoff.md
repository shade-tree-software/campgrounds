---
name: project_ok_sweep_handoff
description: "Oklahoma sweep COMPLETE — all 4 buckets added + waterfront-audited & pushed (291 entries, ids 6571-6861); no legacy loose ends"
metadata:
  node_type: memory
  type: project
  originSessionId: 74933f40-e902-4f5d-8928-35991a7686c7
---

**Oklahoma sweep — COMPLETE (2026-07-02).** Near-fresh state (OK had only 1 prior
entry: id 673 Lake Murray SP, left in place). **291 new OK entries** (ids
6571-6861). Both audits folded into the add per current standard: every entry
carries `inclusion_evidence` (add-time, 291/291) AND `waterfront_evidence`
(291/291 audited). Committed + pushed to master in 5 commits (state/federal/
private/local adds + one waterfront-audit commit).

By ownership: **private 134, federal 62, state 51, local 44.** Method identical to
[[project_wy_sweep_handoff]] / [[project_mt_sweep_handoff]] / [[project_mn_sweep_handoff]].

**Buckets (RV Life Algolia, app H0LPZK92QJ, OK bbox 33.62,-103.0,37.0,-94.43 →
622 OK hits):**
- **State** (32→... 62 cand in 4 batches → 56 keep, ids 6571-6626): OK State Parks
  reserve via **ReserveAmerica** (`okstateparks.reserveamerica.com/camping/<slug>/r/campgroundDetails.do?contractCode=OK&parkId=<id>`),
  official pages `travelok.com/state-parks/<slug>` (NOT GoingToCamp — addendum was
  wrong, agent corrected). Kept OK state parks + their named sub-campgrounds (Lake
  Murray ×8 landings, Lake Wister ×3, Fort Cobb ×3, Grand Lake areas, McGee Creek
  ×2, Beaver Dunes ×2). Skips: Thunderbird Casino, Sunset Bay (tent-only+closed),
  dup re-lists (Twin Bridges, Cherokee SP, Disney/Little Blue, Wards Landing).
  Reclassed OUT to local (Hatbox/Muskogee, Dripping Springs Red Oak+Clovis Point/
  Okmulgee, Adair/Stilwell) and federal (Kiamichi Park + Caney Bend = USACE).
- **Federal** (66 cand [Kiamichi dropped as dup] in 4 batches → 58 keep, ids
  6627-6684): **USACE Tulsa District dominates** (Eufaula, Texoma, Fort Gibson,
  Keystone, Skiatook, Kaw, Canton, Oologah, Copan, Heyburn, Fort Supply, Birch,
  Sardis, Hugo, Waurika, Robert S. Kerr, Tenkiller, Pine Creek — all rec.gov). NPS
  Chickasaw NRA (The Point/Buckhorn/Guy Sandy), USFWS Wichita Mtns (Doris), USFS
  Ouachita NF (Cedar Lake/Winding Stair) + Black Kettle Natl Grassland (Skipout/
  Spring Creek), Fort Sill LETRA (public MWR). Echota Village reclassed private.
  Skips: **military-only FamCamps** (Tinker/Altus/McAlester-Murphy's Meadow/Camp
  Gruber-Blackhawk/Medicine Creek), Dam Site (closed ~2.5yr bridge work), Billy
  Creek (tent-only), Pecan Park (unconfirmable).
- **Private** (170 gated [price<=2 & star>=4] in 9 batches → 142 keep, ids
  6685-6826): commercial RV parks statewide. 28 skips — casino players-club/
  overnight lots, **8 Elks fraternal-club lodges**, residential/mobile-home & 55+
  communities (kept Oak Glen for its segregated transient area), Horse Heaven
  (equestrian), Cypress Cove (marina/cabins-only), dups (Beaver's Bend SP, Doris,
  Deep Creek), unconfirmable (Schroeders, CJ's). Several reclassed to federal
  (Heyburn Park/Burns Run West/Kiowa Park I = USACE mistagged commercial), state
  (Quartz Mtn), local (Perry Lake, Wes Watkins, Lake Carl Blackwell/OSU, Bell Cow,
  Brushy Lake, New Mannford Ramp, Lake McMurtry, Wah-Sha-She/Osage, Doby Springs,
  Boggy Depot/Chickasaw).
- **Local** (39 cand [38 city/county park_type + Crowder Lake/SWOSU from the gov-
  name scan] in 2 batches → 35 keep, ids 6827-6861): municipal/county/university
  lake parks (no star/price gate). Reclassed to private: Cowboy Camp, Washita
  Valley, Nowata, Great Outdoors, Newberry Creek. Skips: Beaver Dunes Park (dup of
  Pioneer/Hackberry loops), Country Home Estates (residential), Issac Walton
  (tent-only), Racee/Ray See (day-use).

**Waterfront audit — DONE (100%, 291/291).** 200 water-adjacent entries run
through `audit/waterfront_audit_instructions.md` subagents in 20 batches of 10
(sequential per [[feedback_sequential_sweep_agents]], carrying each entry's
research `lead`), applied with `apply_waterfront_audit.py`. The 91 no-water
entries stamped not-waterfront by default-down with a no-water-exemption evidence
string (no satellite look). **Final distribution:** 170 not waterfront, 69
lakefront, 42 lakeview, 6 pond, 2 riverfront, 1 riverview, 1 creekside (**121
upgrades** from the placeholder; **18 coord fixes**). **Key OK pattern: USACE
reservoir sites confirmed by plotting rec.gov per-site lon/lat onto the satellite**
(many "proximity_water=Lakefront" flags; drawdown open-apron sites earned lakefront
to the high-water edge). State-park/municipal reservoir peninsula loops with open
grass/sand aprons → lakefront; set-back or treeline-screened loops → lakeview/not
waterfront. Lake Murray's 8 landings almost all lakefront; Fort Gibson/Skiatook/
Kaw/Oologah/Texoma/Eufaula COE loops heavily lakefront.

**OK is fully done — no legacy loose ends** (both audits folded into the add).
Reusable plumbing (adapted from WY): `/tmp/pull_ok.py`, `/tmp/bucketize_ok.py`,
`/tmp/split_ok.py`, `/tmp/append_ok.py` (stamps OK, saves id→lead map),
`/tmp/ok_addendum.md` (per-bucket OK authorities), leads in `/tmp/ok_leads_*.json`,
results in `/tmp/ok_results/` + `/tmp/ok_wf_results/`. See
[[reference_inclusion_audit]], [[feedback_waterfront_evidence_in_json]],
[[reference_rvlife_price]], [[reference_local_campground_method]],
[[reference_usedirect_deep_reservation_links]].
