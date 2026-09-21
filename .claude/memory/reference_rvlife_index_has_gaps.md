---
name: reference_rvlife_index_has_gaps
description: RV Life's park index silently omits real agency campgrounds — cross-check the agency's own park list before calling a state sweep complete
metadata:
  type: reference
---

**RV Life's Algolia `park` index is not a complete list of a state agency's campgrounds, and the gap is silent.** Five South Dakota GFP campgrounds that publish sites, rates and a per-site campground map on `gfp.sd.gov` return **nothing** from the index when queried by name: Buryanek (44 sites), Sheps Canyon (22 electric + 40 non-electric), Platte Creek (36), Lake Carthage (13 electric), Amsden Dam (12). They were never rejected by the sweep's gates — they were never seen, because detection starts from RV Life (see [[project_sd_sweep_handoff]], [[reference_local_campground_method]]).

**Why it matters:** an RV-Life-driven sweep can reach "100% audited" while missing real, bookable, publicly-run campgrounds, and nothing in the evidence fields reveals it — `waterfront_evidence`/`inclusion_evidence` only tell you about entries that exist.

**How to apply:** for any state whose parks are run by one agency, walk the AGENCY's own park list (SD: the region-grouped `<select>` of park links in any `gfp.sd.gov/parks/detail/<slug>/` page; most states have an equivalent index page) and diff the names against what's already in `campgrounds.json`. It is a free check and it is the only one that catches this class of miss. Do it as a closing stage of a state sweep, not as a separate project.

Corollary: those five have **no `rating` group**, and that is correct rather than a gap — `rating` comes from RV Life and there is no row to read. Don't backfill stars/price from another source without changing `rating.source`.

Related: [[feedback_absent_is_not_unknown]], [[project_campground_schema]].
