---
name: project_pa_sf_reservable_gap
description: "PA state forest reservable-site gap closed 2026-10-10 (156 entries, 1 km clusters); recipe + exclusions in audit/pa_sf_dispersed/"
metadata:
  node_type: memory
  type: project
  originSessionId: a3b233bc-ce25-4f71-8a6d-0516b1e12984
  modified: 2026-10-10T20:16:34.666Z
---

2026-10-10, at AWH's request ("public PA dispersed sites that we missed but that are reservable online"):

- Every bookable DCNR state forest site on ReserveAmerica was enumerated: 730 sites across 18 forest "parks", stored in `audit/pa_sf_dispersed/ra_sites.jsonl`.
- 244 gated sites were added as **156 entries, ids 15183-15338**.
- **AWH chose one entry per 1 km cluster** of sites, rather than one per site or one per loop.
- Next free id: 15339.

**Why:** older PA SF entries were one per site and covered only ~26 of the bookable sites. Whole forests (Sproul, Buchanan, Loyalsock, Susquehannock, Bald Eagle) were absent.

**How to apply:**
- Re-run `enumerate.py` then `gap.py` to find new sites. The README has the full pipeline.
- `gap.py` matches siteIds in inclusion_evidence, including comma lists.
- Site-page exclusions:
  - tent-only
  - equine-only in summer (Yellow Snake)
  - hang-glider-only (Hyner River)
  - ATV-rider-only in summer (Susquehannock)
  - 4x4 recommended or required
  - trailers not recommended
- Bald Eagle's forest-wide "some roads require 4WD" line is a note caveat, not an exclusion. It's worth AWH's eye per [[user_ekko_no_4wd]].
- Waterfront rule used: an agency per-site "Streamside campsite along X" counts as per-site data only when the canopy is blind. Legible imagery showing a road or a wooded buffer overrides it.
- "Distance to Lake/Stream: Less than 300 feet" alone never earns on-water.
- Overpass 504s on bulk queries. The USGS NHD MapServer (layers 6/12/9) answers quickly.

See [[project_price_research]].
