---
name: project_al_sweep_handoff
description: Alabama campground sweep status — state/federal/local/gov-misclassified DONE; only the private bucket remains
metadata: 
  node_type: memory
  type: project
  originSessionId: aac3f4a3-f43e-40eb-aa96-cc363a5944f5
---

Alabama state-by-state campground sweep (started 2026-06-22). Buckets, in order, are all DONE + committed + waterfront-audited EXCEPT private:

- **State** (ids 4861-4879): 19 state-park/forest entries. Committed + audited.
- **Federal** (4880-4903): 24 USACE + USFS entries. Committed + audited.
- **Local** (4904-4928): 25 county/city/regional + Bear Creek Development Authority (5 campgrounds) + Fort Toulouse (state, AHC). Committed + audited.
- **Gov mis-tagged "commercial"** (4929-4937): 9 parks RV Life labeled `commercial` whose names lack gov keywords so the name-scan missed them — Chickasabogue, Ditto Landing, Goose Pond Colony, Noccalula Falls, Point Mallard, Sherling Lake, Higgins Ferry, Point A Park, Moundville (state). Committed + audited.

**REMAINING: the private (commercial) bucket — not started.** Method: RV Life `commercial` with `price_level` ≤ 2 AND `star_rating` ≥ 4, non-membership, then vet each per inclusion criteria. That gate yields **126 candidates** (list reproducible from `/tmp/al_rvlife.json` — 519 AL records pulled via Algolia `H0LPZK92QJ`, or re-pull). After removing the 9 gov parks already added, the Elks/club lodges (Calera/Decatur/Anniston/Florence/Marion-Co), membership parks (Thousand Trails Hidden Cove, Talladega Creekside, Mountain Lakes RV Resort, Styx River — Coast-to-Coast/RPI/AOR), MH/residential (Sawyers, Enterprise MH&RV), and the Wind Creek **casino** lot, ~80 genuinely-private candidates remain to vet one-by-one (real transient RV park, not seasonal/residential/workforce; dead-website strike; 23-ft fit; waterfront via the satellite evidence gate → coords + elevation + audit + commit).

Notes for the private pass:
- **Red Bay cluster**: several tiny "RV park" entries there (1st Class, Convenient Camping, Bunk House, Red Bay Self Service, Detail Depot, Tiffin Wayfarer/Customer Service) are **Tiffin Motorhomes factory service-center** parks — campers waiting on warranty work. Scrutinize whether each is a real public transient campground before adding.
- A few more **government** parks may still hide in the commercial bucket (RV Life mis-tags AL gov parks heavily) — keep watching for them while vetting private.

See [[reference_local_campground_method]] and [[feedback_campground_vetting_discipline]].
