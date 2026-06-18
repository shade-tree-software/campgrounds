---
name: reference-local-campground-method
description: How to detect/vet/add local (county/town/city/regional) campgrounds per state
metadata: 
  node_type: memory
  type: reference
  originSessionId: c8ea6a71-08f2-45a1-8ff8-4a363d1ac421
---

Method for the `local` ownership category (county/town/city/regional-authority campgrounds), worked one state at a time. Validated on VA (June 2026): 13 added, growing VA local 9→22.

**Detect (multi-pronged — RV Life's `park_type` is a great classifier but NOT complete):**
- Pull all the state's RV Life parks (see [[reference-rvlife-price]] for the Algolia access + bbox trick). `park_type` values seen: commercial, state, national, coe (USACE), usfs, military, county, city, dnr, regional.
- Primary: `park_type ∈ {county, city, regional, dnr}` = local candidates.
- Supplement (REQUIRED): name-scan the `commercial` and `state` buckets for gov keywords (county|town|municipal|regional|authority|township). RV Life mislabels real local parks — in VA it tagged Pohick Bay & Lake Fairfax & Burke Lake as `commercial` and Bull Run as `state` (all are county/regional-authority parks).

**Inclusion policy the user set (June 2026): do NOT apply the private-campground ≥4★/≤$$ gate to local.** Local gov campgrounds are public + nearly always cheap + lightly reviewed, and the category is small, so include any *confirmed* local-gov drive-in RV campground regardless of star/price — just record the RV Life star+price in the note as info (like we do for state/federal).

**Vet each candidate (per-candidate web research — operator question is the crux):**
- Confirm the operator is genuinely LOCAL GOVERNMENT (name the county/town/city/authority); flag if actually private/state/federal. Watch concessionaire-run county parks (e.g. Explore Park is Roanoke-County-owned but camping is run by Don's Cab-Inns — still tag `local`).
- Standard inclusion criteria: drive-in, RV-usable at 23 ft (see [[feedback-min-site-length]]), not tent-only/hike-in/boat-in/equestrian/group-only.
- RV Life coords are often off (~6–10 km in VA for several) — pin to the real campground; pull elevation at the corrected coords.
- Waterfront: only `lake`/`river` with site-level confirmation that some sites sit on the water; else `*view` or `none`. Don't trust phone numbers from memory — verify (one of five I pre-filled, Rural Retreat, was wrong).

Dedupe by coordinate proximity (<~0.6 km), not just name (fuzzy name match gave false positives like Flag Rock↔Comers Rock). Add with `ownership: "local"`.
