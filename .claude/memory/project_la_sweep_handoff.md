---
name: project_la_sweep_handoff
description: "Louisiana sweep COMPLETE — all 4 buckets added + waterfront-audited & pushed (147 entries, ids 6862-7008); no legacy loose ends"
metadata: 
  node_type: memory
  type: project
  originSessionId: c0aef648-c57e-4c31-a4af-e7ec646bdc21
---

**Louisiana sweep — COMPLETE (2026-07-03).** Near-fresh state (LA had only 2
prior entries: id 674 Cypress Bend Park [SRALA] + id 712 Lake D'Arbonne SP, both
firsthand `--AWH`, left in place). **147 new LA entries** (ids 6862-7008). Both
audits folded into the add per current standard: every entry carries
`inclusion_evidence` (add-time, 147/147) AND `waterfront_evidence` (147/147).
Committed + pushed to master in 5 commits (state/federal/local/private adds + one
waterfront-audit commit). Method identical to [[project_ok_sweep_handoff]] /
[[project_wy_sweep_handoff]] / [[project_mn_sweep_handoff]].

By ownership: **private 79, state 24, local 23, federal 21.**

**Buckets (RV Life Algolia, app H0LPZK92QJ, LA bbox 28.85,-94.10,33.05,-88.75 →
380 LA hits):**
- **State** (26 cand in 4 batches → 23 keep, ids 6862-6884): LA State Parks
  reserve via **gooutdoorslouisiana.com** (`reservations.gooutdoorslouisiana.com/
  FacilityDetails.aspx?facID=<id>`, add `&tab=map`) — NOT ReserveAmerica (that was
  the addendum's initial guess, corrected batch 1). Official pages
  `lastateparks.com/parks-preserves/<slug>`. Kept all LA state parks + **SRALA**
  (Sabine River Authority) Toledo Bend parks (Oak Ridge, Pleasure Point — both
  `state`) + Indian Creek Rec Area (LA Dept of Ag & Forestry, `state`, uses
  ResNexus). Skips: Converse Bay (now day-use only), Toledo Bend Reservoir
  (generic dup of Pleasure Point), Lake D'Arbonne (id 712 dup).
- **Federal** (33 cand in 5 batches → 21 keep, ids 6885-6905): **USFS Kisatchie
  NF dominates** — developed rec areas (Beaver Dam/Caney Lakes, Gum Springs,
  Valentine Lake Northshore, Fullerton, Stuart Lake, Cloud Crossing, Corney Lake,
  Dogwood on rec.gov) + many primitive FCFS **hunter camps** (Bankston, Hwy 472,
  Custis, Hunter, Oak, Pearson, Turkey Trot, Bucktail, Coyote, Loran/Claiborne,
  Enduro, Evangeline). RV Life mis-tags many Kisatchie sites `park_type=national`
  → all `federal`. One USACE: Tom Merrill Rec Area (Bayou Bodcau, Vicksburg Dist).
  Skips: **4 military FamCamps** (Barksdale AFB, NAS JRB/Aviation Arbor, Fort Polk/
  Alligator Lake, Camp Beauregard/Twin Lakes), **Kincaid Lake** (camping CLOSED for
  post-Hurricane-Laura reconstruction, day-use beach only reopened), walk-in/tent
  (Saddle Bayou, Red Bluff, Kisatchie Bayou Rec Complex), Turtle Slide (closed),
  dups (Fullerton Complex, Loran dup, Kincaid dup).
- **Local** (20 cand in 3 batches → 19 keep, ids 6906-6924): parish/police-jury &
  municipal parks (Calcasieu Police Jury runs several: White Oak/Intracoastal/
  Holbrook/Lorrain; plus Lincoln/Bossier[Cypress Black Bayou]/Rapides[Cotile]/
  Grant[Colfax=Red River Waterway Comm]/St Martin[Uncle Dick Davis]/St Mary[Kemper
  Williams]/Ouachita[Cheniere]/Caddo[Earl Williamson]/Cameron[Rutherford Beach]/
  Acadia[Rayne]/Ascension[Lamar Dixon]/Webster[Frank Anthony]). No star/price gate.
  1 reclassed state (San Miguel=SRALA), 1 fairground kept as private (State Fair of
  LA, year-round transient). Skip: Lighthouse Bend (private resort, below gate).
- **Private** (109 gated [price<=2 & star>=4] in 14 batches → 84 keep, ids
  6925-7008): commercial RV parks statewide. **8 RV-Life-mistagged government parks
  reclassified in place** (Acadiana Park/Farr Park[BREC]/Lake End[Morgan City]/
  Niblett's Bluff[Ward 7]/Crooked Creek[Evangeline PJ]/Burns Point[St Mary]=local).
  25 skips: **6 casino lots** (Coushatta/Paragon/Cypress Bayou/Delta Downs/Hollywood/
  Boomtown), **3 Elks lodges**, membership resorts (Abita Springs/Hideaway Ponds=
  Ocean Canyon), **~9 workforce/long-term & residential-MH parks** (common in south-
  LA oilfield/plant corridor: Pavilion/Cajun Country/St James/Choctaw/Mozella/
  Country Meadow/Mylander/Seth's Haven/B&B), closed/defunct (Acorn Hill/Wooden
  Horse/Oak Tree), unconfirmable (Tiger RV).

**Waterfront audit — DONE (100%, 147/147).** 116 water-adjacent entries run through
`audit/waterfront_audit_instructions.md` subagents in **12 batches of 10**
(sequential per [[feedback_sequential_sweep_agents]], carrying each entry's research
`lead`), applied with `apply_waterfront_audit.py`. 31 pure-inland entries (Kisatchie
upland hunter camps + in-town/highway RV parks) stamped not-waterfront by
default-down with a no-water evidence string (no satellite look). **Final
distribution:** 104 not waterfront, 16 lakefront, 9 pond, 8 lakeview, 4 riverfront,
3 bayfront, 2 riverview, 1 coastal dunes (**43 upgrades**; **2 coord fixes**: Lake
Claiborne 6877, Beaver Dam 6885). LA-specific patterns: **Grand Isle SP = coastal
dunes** (open undeveloped beach/dune apron to the Gulf, no road between); **9 private
on-site fishing PONDS** earned `pond` (Poche's, Isle of Iberia, Flagon Creek, Bayou
Black, Rest Hill, Village Oaks, Bonnie&Clyde, Bucks&Ducks, Choupique); Toledo Bend
SRALA + Caney lakes lakefront; **Mississippi-River-levee parks all not-waterfront**
(river screened by levee: Poche Plantation/Farr/Sugar Hill/Nelson/AMA/Stumpfs);
state-park RV loops usually set back in bottomland forest → not-waterfront even when
named for a lake (Fontainebleau/Chicot/Palmetto Island/Tickfaw).

**LA is fully done — no legacy loose ends** (both audits folded into the add).
Reusable plumbing (adapted from OK): `/tmp/pull_la.py`, `/tmp/bucketize_la.py`,
`/tmp/split_la.py`, `/tmp/append_la.py` (stamps LA, saves id->lead map),
`/tmp/la_addendum.md` (LA authorities incl gooutdoorslouisiana + Kisatchie + private
rules), leads in `/tmp/la_leads_*.json`, add results in `/tmp/la_results/`, waterfront
results in `/tmp/la_wf_results/`. See [[reference_inclusion_audit]],
[[feedback_waterfront_evidence_in_json]], [[reference_rvlife_price]],
[[reference_local_campground_method]].
