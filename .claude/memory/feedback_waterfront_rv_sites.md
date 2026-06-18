---
name: feedback-waterfront-rv-sites
description: "The waterfront field must reflect RV-accessible sites only, and be researched accurately in every case"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c8ea6a71-08f2-45a1-8ff8-4a363d1ac421
---

The whole database targets RV camping in an EKKO-class rig (23 ft, AWD-not-4WD, no hookups needed). The `waterfront` field must describe what's available **to an RV**, not tent or cabin sites.

**Rules:**
- Set an on-water value (`lake`/`river`/`creek`/`pond`/`bay`/etc.) ONLY with site-level confirmation that some **RV-accessible** sites sit directly on/along the water. Riverfront/lakefront **cabins or tent-only sites do NOT qualify** — if the only on-water sites are tents/cabins/shelters, it is not `river`/`lake`.
- Use a `*view` value (`riverview`/`lakeview`/`bayview`) ONLY if at least some **RV** sites actually have a view of the water (even if not on it).
- Otherwise `none` — including water that's merely "nearby," reachable by trail, or viewed only from tent/cabin areas.

**Strengthen the research:** the waterfront field should be set accurately in every case, even when that takes extra work — pull the campground's own site map, recreation.gov/Campspot/ReserveAmerica per-site details, campsitephotos.com, and satellite imagery, and specifically determine the RV-site-to-water relationship (distinguish RV loops from tent/cabin/shelter areas). Don't default to a water tag from general "on the river" marketing.

**Why:** confirmed on Glen Maury Park — its riverside sites are tent-only; the RV loops sit on a rise overlooking the river (so `riverview`, not `river`) or up in the woods. Several other June-2026 VA local adds had the same tent-vs-RV issue and were re-vetted. Refines the older [[feedback-attribute-note-edits]]-era waterfront guidance and the CLAUDE.md waterfront vocabulary; relates to [[reference-local-campground-method]] and [[feedback-min-site-length]].
