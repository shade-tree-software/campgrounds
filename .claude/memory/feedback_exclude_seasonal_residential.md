---
name: feedback-exclude-seasonal-residential
description: "Don't add campgrounds that are mostly seasonal/full-timer/residential or membership/sales-pitch parks"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c8ea6a71-08f2-45a1-8ff8-4a363d1ac421
---

When vetting private (and any) campgrounds, EXCLUDE parks that are predominantly long-term rather than genuine transient/nightly RV destinations, even if they technically accept overnighters:
- mostly seasonal / full-timer campgrounds (the transient area is a small afterthought),
- residential / mobile-home-park-character parks (permanent residents, monthly leases, workforce/oil-&-gas housing),
- membership/club parks or ones run on a timeshare/sales-pitch model (Travel Resorts of America, Encore/Thousand Trails, Airstream/WBCCI clubs, "buy-in + annual fee" parks).

**Why:** the database is for finding places the family can actually pull into for a night or a short stay in the EKKO; a park full of permanent residents or one that gates access behind membership/sales pitches isn't a usable transient campground.

**How to apply:** during vetting, read reviews/operator pages for "mostly seasonal / full-timers / permanent residents / mobile-home park / monthly rent / membership / sales presentation" signals; exclude those. Confirmed by removing PA's Pittsburgh Roaring Run (membership/sales-pitch legacy), Camp Eriez (predominantly seasonal/full-timer), and Walmar Manor (permanent-resident MH-park character); Center Manor (UMH workforce MH park) and the membership clubs were excluded during vetting for the same reason. Relates to [[reference-rvlife-price]] and [[reference-local-campground-method]].

**Measuring it in Quebec (2026-10-08, Canada no_rate follow-up):** nearly every QC private park is part seasonal, so measure the traveller share: (1) the operator's map legend (Saisonnier vs Voyageur/Passant colours) or a stated count, (2) a booking engine's free-site count for a future weeknight, (3) a pre-opening/post-closing Esri Wayback frame (stored trailers on nearly every pad = seasonal). Working line used: traveller sites under ~10% of the park = mostly seasonal (Royal Papineau 7%, Panoramique 8%, Camping 15/30 5%); 12%+ with a real traveller block was added. That line extends the Sutter's (~9%) precedent and has not been separately confirmed by AWH. Recipes: [[reference-hidden-rates-playbook]].
