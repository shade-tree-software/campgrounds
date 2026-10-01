---
name: feedback_wildlife_agency_camping
description: State wildlife-agency camping (MDC conservation areas, KS fishing lakes, NE WMAs) - add only real campgrounds (designated drive-in sites fitting 23 ft; a restroom is NOT required), skip parking-lot style areas (AWH 2026-09-29)
metadata:
  type: feedback
---

For the state gap, a wildlife-agency area (Missouri MDC conservation area, Kansas state fishing lake, Nebraska WMA and the like) gets an entry **only when it has an actual campground**: numbered or designated drive-in sites confirmed to fit a 23-ft rig. **A restroom, privy or water is NOT required** (AWH 2026-09-29: "don't worry about whether there's a restroom"). Those go in as `ownership: state`, like MDC's Hunnewell Lake / Whetstone Creek / Deer Ridge / Lead Mine (1930-1933). Areas where "designated camping" means an overnight spot in a parking lot or a pull-off are skipped, not added as `wma`.

**Why:** AWH chose this 2026-09-29 over adding all 263 MDC areas as `wma` or skipping the class. The map's value is real places to camp; a hundred gravel lots per state would bury them and cost weeks of vetting.

**How to apply:** use the agency's own facility list to filter (MDC area pages list campsites and privies), then confirm fit per area. Related: [[project_remaining_work_map]], [[feedback_add_with_caveat_not_withhold]].

**Update AWH 2026-09-29 (same day): for MDC, the agency's own tag is enough.** An area whose MDC page lists "Individual Campsites" or "Designated Camping Sites" qualifies for an entry; knowing how many sites is nice but not required. MDC's camping-point layer (MSDIS `MO_MDC_Camping_Sites` FeatureServer, services2.arcgis.com/kNS2ppBA4rwAQQZy) supplies the pins. Apply the same spirit to other states' wildlife-agency designations: an agency-designated campsite is the bar, a parking-lot overnight allowance is not.

**Ownership label (AWH 2026-10-01):** `wma` is ONLY for parking-lot camping (no dedicated campsites). A WMA with a genuine campground or marked/designated dispersed sites gets `state` (or `local` if county-run). Edwards Run (14099) is `wma` by AWH's explicit call despite 6 DNR-listed sites. Recorded in docs/campground-curation.md.
