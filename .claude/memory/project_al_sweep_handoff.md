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

**REMAINING: the private (commercial) bucket — IN PROGRESS.** Method: re-pull AL via Algolia `H0LPZK92QJ` (`park` index, `insideBoundingBox=[[30.1,-88.6,35.05,-84.85]]`, keep `region_abbvr=='AL'`), filter to `commercial` with `price_level` ≤ 2 AND `star_rating` ≥ 4 (gate = 126). Auto-categorize and drop: already-added (9 gov parks + McFarland/Elliott-Branch dupes), club lodges (Elks/Legion), Wind Creek casino, membership (affiliations contain Thousand Trails/Coast to Coast/RPI/AOR/ROD), MH/residential (name has "mobile/manufactured home"/"estates"), B&B, and the **Red Bay/Winfield Tiffin-factory cluster** (1st Class, Convenient Camping, Detail Depot, Bunk House, Red Bay RV/Downtown/Self-Service, Tiffin Wayfarer/Customer-Service — overnight parks for warranty customers, NOT general transient → exclude). Leaves **92 to vet one-by-one** (real transient RV park, not seasonal/residential/full-timer/lot-lease/55+; 23-ft fit; dead-website strike; waterfront via satellite gate → coords+elevation+audit+commit).

**Private progress (session 2026-06-22): vetted 20 of 92.**
- **ADDED (8, ids 4938-4945, committed):** General Lee Marina (Cropwell, lakefront), The Cove Lakeside RV Resort (Gadsden, lakefront), South Sauty Creek Resort (Langston, lakefront), Honeycomb Campground (Grant, lakefront), Seibold Campground (Guntersville, lakefront), Gulf Breeze RV Resort (Gulf Shores, not-wf), Sun Runners RV Park (Gulf Shores, not-wf), Winners Circle RV Resort (Theodore, not-wf).
- **EXCLUDED (8):** Bay Point (mostly part-time/seasonal), Clear Creek Cove (6-mo min), Logan Landing (1-30yr lot leases + park models), Smith Lake RV & Cabin Resort (lot ownership/custom homes), Blue Heron (91 deeded lots), Cedar Point (closed→private subdivision), Camellia RV Park & Azalea Acres RV Park (55+ adult-only, unusable by a family with kids).
- **DEFERRED (4, re-pin/verify before adding):** Gantt Lake RV (Andalusia — re-pin to 31367 Catfish Lane on Gantt Lake; daily rates + waterfront/canal lots, likely lakefront), Riverview RV Resort (Athens — 4900 Snake Rd; real 107-site park but sites set back ~300m from TN River, confirm waterfront), Lake Eufaula Campground (Eufaula — 151 W Chewalla Creek Dr; satellite shows mobile-home/residential, verify transient before adding), Gulf Coast RV Park (Gulf Shores — area is marina/MH, couldn't isolate the RV park).

**~72 still unvetted.** Watch for more 55+/lot-lease/deeded-lot/residential models (common among AL lake "resorts" — high exclusion rate) and further gov mis-tags while vetting.

See [[reference_local_campground_method]] and [[feedback_campground_vetting_discipline]].
