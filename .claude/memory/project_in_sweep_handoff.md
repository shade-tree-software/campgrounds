---
name: project_in_sweep_handoff
description: Indiana audit status — waterfront 100% done; inclusion done for non-waterfront only
metadata: 
  node_type: memory
  type: project
  originSessionId: b95cfcd7-c453-40c6-ab56-d15b88386c38
---

Indiana (IN) audit status as of 2026-06-28 (114 IN campgrounds total):

- **Waterfront audit: 100% COMPLETE (114/114).** The 72 not-waterfront entries lacking `waterfront_evidence` were audited via the satellite/per-site-map gate (commit "Audit all 72 IN not-waterfront waterfront designations"). 11 upgrades (West Boggs/New Lake/All My Family & Friends/Camp Timber Lake/Long Lake Resort → lakefront; Old Mill Run/Happy Camper/Peaceful Waters/Eagles Nest → pond; Lake Waveland/Buffalo Trace → lakeview), 5 coord fixes (1073, 1088, 1100, 1102, 1345). The 33 already-on-water IN entries were already audited.
- **Inclusion audit: done for the 81 not-waterfront entries ONLY (all kept, 0 removals).** Commit "Inclusion-audit all 81 IN not-waterfront campgrounds." Pattern matched [[project_ky_sweep_handoff]]/[[project_wi_sweep_handoff]]: IN non-waterfront is dominated by well-documented DNR state parks + SRAs, state-forest Class C, Hoosier NF rec areas, and county/fairground locals.
- **REMAINING loose end:** the ~33 currently-waterfront IN entries still need an [[reference_inclusion_audit]] pass.

Notable: IN DNR state-park campground loops sit set back from their lakes/rivers behind treed buffers (only group/tent/canoe camps are on water); Hoosier NF rec areas keep RV loops on the interior ridge above the day-use shoreline strip.
