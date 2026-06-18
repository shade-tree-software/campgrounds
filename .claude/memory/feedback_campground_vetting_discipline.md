---
name: feedback_campground_vetting_discipline
description: Tighter vetting before adding a campground — no unconfirmed/boilerplate entries; reservations-claim needs a booking channel
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f0f241c6-6ec0-4e4c-a2e2-5487197fe8e7
---

Don't add campground entries that rest on unconfirmed or aggregator-generated data. The Bear Creek Rec Area (IL, USACE) slip-through is the cautionary example: it was inserted with a `note` ("restrooms, hot showers… reservations required") lifted from snoflo's auto-generated boilerplate, while carrying no phone and no reservation website — and RV Life rated it 0 (unrated). All three were red flags that should have stopped insertion or triggered real research. It's actually a free, first-come-first-served, primitive USACE site.

**Why:** placeholder/boilerplate entries put wrong facts in front of the family and cost rework later. Public/government sites are legitimately unrated and lightly reviewed, so "unrated" isn't a reason to exclude — but it removes the safety net, so the basics must be confirmed firsthand.

**How to apply:**
- RV Life `star_rating` 0 (unrated) + thin/no reviews → confirm fee/reservation model, drive-in RV access, RV-fitting length, amenities, and that it's operating from a firsthand/authoritative source (official/agency page, site map/photos, dated trip report). Can't confirm → skip, don't guess.
- Never copy aggregator boilerplate (snoflo/camping.org/campingroadtrip/mobilerving) into a `note`. When aggregator prose contradicts its own structured field, the structured field wins.
- Consistency gate: a "reservations required" note must have a real booking channel (recreation.gov/reserveamerica/state portal website, or verified phone). Claim + no channel = contradiction, almost always actually free FCFS — resolve before inserting. USACE/federal river & reservoir areas default to free FCFS.

See also [[feedback_attribute_note_edits]], [[reference_rvlife_price]], [[reference_good_sam_ratings]].
