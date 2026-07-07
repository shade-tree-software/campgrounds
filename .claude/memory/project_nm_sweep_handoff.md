---
name: project_nm_sweep_handoff
description: "New Mexico sweep COMPLETE — all 4 buckets + both audits done & pushed (233 entries, ids 7931-8163); no legacy loose ends"
metadata: 
  node_type: memory
  type: project
  originSessionId: 835151ba-bac6-4e20-93a7-512ed92b619f
---

**New Mexico sweep — COMPLETE (2026-07-07).** Clean fresh-state sweep (NM had 0
entries). **233 new NM entries** (ids 7931-8163). Both audits folded into the add
per current standard: every entry carries `inclusion_evidence` (recorded at add
time) AND `waterfront_evidence` (233/233 audited). Committed + pushed to master
(5 commits, one per bucket + one audit commit).

By ownership: **private 106, federal 60, state 56 [incl BLM], local 11.**

**Detection (RV Life Algolia, app H0LPZK92QJ, key from campgrounds.rvlife.com/
homepage HTML):** NM bbox `[31.20,-109.20,37.05,-102.90]` → 562 NM hits. Bucketed
by `park_type`. **NM has NO state DNR — RV Life `park_type: "dnr"` = BLM = federal**
(like WY): Valley of Fires, Datil Well, Orilla Verde (Rio Bravo/Pilar/Arroyo Hondo),
Wild Rivers/El Aguaje, Aguirre Spring, Three Rivers Petroglyph, Chosa/Sunset Reef,
Santa Cruz Overlook, Brown Springs, Dog Canyon, Mesa de Cuba, Bill Evans (NMDGF=state).

**Buckets:**
- **State/BLM** (68 cand, 9 batches → 56 keep): NM State Parks (Elephant Butte
  loops, Caballo, Heron, Navajo, Bluewater, Ute, Conchas, Sumner, Santa Rosa,
  Clayton, Eagle Nest, Cimarron Canyon, Bottomless Lakes, Brantley, Rockhound,
  City of Rocks, Oliver Lee, Sugarite, Coyote Creek, Fenton, El Vado, Pecos Canyon
  Mora+Terrero, Villanueva, Pancho Villa, Leasburg, Percha, Oasis, Storrie, Hyde,
  Manzano) + BLM. Reserve via **newmexicostateparks.reserveamerica.com** + EMNRD
  park pages. Skips: Wild Rivers umbrella (under-20ft rim loops — but El Aguaje
  loop kept at 23-28ft), Bisti/De-Na-Zin & Ah-Shi-Sle-Pah (wilderness hike-in),
  Mescalero Sands (OHV), Morphy Lake (18ft/4WD), Angostura (unconfirmable/private
  Sipapu), Taos Junction (group-only), Orilla Verde Petaca (closed), Deming
  generic dispersed pin.
- **Federal** (118 cand, 15 batches → 60 keep): USACE (Cochiti/Tetilla Peak,
  Riana/Abiquiu), NPS (Bandelier Juniper, Chaco Gallo, El Morro), USFS Santa Fe/
  Carson/Cibola/Gila/Lincoln NFs. **High skip rate (58 skips)** — small mountain
  NF campgrounds cap under 23ft or are tent/walk-in; also post-fire closures
  (Hermits Peak/Calf Canyon 2022, South Fork/Blue 2 2024: El Porvenir, E.V. Long,
  Lower Gallinas, South Fork/Bonito). rec.gov per-site "Max Vehicle Length" often
  overrode a conservative FS-page trailer-turnaround caveat (Coal Mine, McGaffey,
  Water Canyon). 2 RV Life double-listings dropped (Juniper Quemado Lake x2,
  South Fork x2).
- **Local** (13 cand, 2 batches → 11 keep): municipal/county (Coronado/Bernalillo,
  Socorro, McGee Park/San Juan Co, Harry McAdams/Hobbs, Lordsburg, San Jon, Lake
  Van/Dexter, Lake Farmington, Sandoval Co Fairgrounds, Jal Lake). No star/price
  gate. Homestead RV Los Lunas reclassed private. Skips: Senator Willie Chavez
  (closed), Volunteer Park (genuinely military/WSMR, CAC required).
- **Private** (133 gated cand [price≤$$ & star≥4], 15 batches → 106 keep, after
  pre-dropping 13 Elks lodges/casinos). Vetted per inclusion. Reclassed to local:
  White Rock/Los Alamos Co, Escondida Lake/Socorro Co, Randolph Rampy/Tatum, Lester
  Jackson/Pie Town. Skips: membership (The Ranch=Escapees), casino lots (Black
  Mesa), residential/MH-only (El Rancho, Continental Acres, Sundowner, White Sands
  MH), workforce/oilfield (Artesia, Cowboys Country, Florez, Night Owl), horse
  stable (Lazy Sue), dead/defunct (Wolf, Roadrunner 66, Native American Camping).

**Waterfront audit — DONE (100%, 233/233).** 126 water-adjacent entries run through
`audit/waterfront_audit_instructions.md` satellite gate (16 batches of 8 carrying
each entry's research `lead`, sequential per [[feedback_sequential_sweep_agents]]);
107 no-water entries (desert/mesa/in-town) stamped not-waterfront by default-down
without a look. Applied with `apply_waterfront_audit.py` (0 coord fixes needed).
**41 upgrades** from placeholder: 3 lakefront (Lea Lake/Bottomless, Storrie, Bill
Evans), 8 riverfront (Arroyo Hondo, Pecos/Mora, Junebug, Rio de los Pinos,
Grapevine, Head of the Ditch, Little Creel, Rio Grande RV), 4 creekside (Coyote
Creek, Columbine, Rio de las Vacas, Holy Ghost), 2 pond (Cimarron/Maverick,
Seeping Springs), 19 lakeview, 5 riverview. **Final: 192 not waterfront, 41
on-water/view.** NM pattern: reservoir drawdown measured to high-water edge;
marina/marketing "lake" names + set-back bluff loops downgraded on the satellite
look; canopy-blind FS creek sites deferred to per-site authority or defaulted down.

**NM is fully done — no legacy loose ends.** Method identical to
[[project_wy_sweep_handoff]] / [[project_ok_sweep_handoff]]. Reusable plumbing:
`/tmp/append_nm.py` (html.unescapes agent entities, stamps NM, saves id→lead map to
`/tmp/nm_leads.json`), `/tmp/nm_addendum.md` (NM reservation-system research
addendum: ReserveAmerica for state parks, BLM=federal, no DNR), batch files in
`/tmp/nm_batches/`, results in `/tmp/nm_results/` + `/tmp/nm_wf/results/`. See
[[reference_inclusion_audit]], [[feedback_waterfront_evidence_in_json]],
[[reference_rvlife_price]], [[reference_local_campground_method]].
