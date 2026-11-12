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

**The definitive rule, AWH 2026-10-14** (asked for after the RoverPass pass; full text in docs/campground-curation.md): a private park that mostly sells months or seasons, or houses residents, but also sells nights stays only if (1) at most US$50/C$69 unless gateway/exception; (2) nights really for sale: a nightly rate on its own site + phone, or a booking site selling one night, with no application/approval/background check/lease/waitlist/membership/rig photos (an RV Life tier does NOT stand in here); (3) no minimum over 2 nights except holiday weekends; (4) at least 1 site in 10 sold nightly where any count exists (no count = pass); (5) not a home community (sells homes/lots, or homes outnumber RV sites). Note says what it mostly is; 55+/adults-only = note line. 26 dropped on it 2026-10-14 incl. Tymber 1224 and Clemson Hills 4377 (AWH: "drop both, my mistake").

**Ambiguous "units for sale" = drop (AWH 2026-10-21, Ridge Manor 14409):** a 55+ resident community advertising "units for sale" with a resident application and seasonal/yearly lots fails test 5 even when it's unclear whether the park or the residents sell the units, and even with nights sold online at the $50 line. Don't ask about this pattern again; drop it and report it.

**Keys owner-lot exception (AWH 2026-10-30):** in the Florida Keys only, an owner-lot (condo) RV resort that rents lots by the night through a normal booking site that works like a regular nightly campground passes test 5 despite selling lots; every other test still applies. See [[project-keys-rescreen]].

AWH 2026-10-30 (River Bend, OH 1300): "tent sites can count toward the nightly number" - test 4 (1 site in 10 sold nightly) counts ALL nightly sites, tent sites included, not only RV sites (16 of 231 RV sites + ~25 tent = 16%, kept).

**On the fence = drop (AWH 2026-10-31, rest of phase 7):** "if you are on the fence about a mostly seasonal campground that looks iffy, just go ahead and drop it and let me know." Don't park these in asks.md; drop and report. Applied that day to 9 open asks.

**Resident-style rules page alone is not a drop (AWH 2026-11-06, Jayhawker RV Park KS 14543: "keep jayhawker"):** a park that sells daily stays with a normal check-out, has a decent Google rating (4.1/65), and only reads residential in its rules (P.O.-box mail, held deliveries, liability insurance, "lessee") stays. Judge by what it sells, not the tone of its rules page.

**Workforce-heavy but a big nightly block = keep (AWH 2026-11-09, I-49 RV Park MO 14586: "keep" because "it still sells plenty of single nights" and "cheapest site a 23-ft rig fits is $48.93 a night on most dates"):** ~60% long-term on a November weeknight, marketed to travel nurses and pipeline crews, yet 44-103 nightly sites open. With dynamic pricing, judge the price gate by the cheapest one-night rate on most dates; an occasional date over $50 ($51.50 in November) doesn't fail it. Don't ask about this pattern again; keep and report.

**Operator says it doesn't want nightly guests = drop (AWH 2026-11-11, Cavens Landing 5522):** "Drop Cavens Landing. I'd rather not stay at a place that clearly doesn't want to deal with nightly guests." The park passed all five written tests ($40 posted, phone, 4.3/29), but its own site said "Seasonal leases preferred! Short term stays are limited." Operator wording that discourages nightly stays (seasonal preferred, short-term limited/by approval, "call to see if we have room") is a drop on its own; drop and report, don't ask. **How to apply:** quote the operator's wording in the drop evidence.

**Test 4 applies to public parks too (AWH 2026-11-10/12):** town-run Drayton Valley 12801 (4 of 42 nightly, 9.5%) and county-run Larimore Dam 5961 (12 of ~144, ~8%) were both dropped under the 1-in-10 line. The price gate (test 1) does not apply to a public park: Red River Valley Fair Campground 5930, a fair association stored `local`, was kept at $55 a night (18 of 75 nightly, 24%). Apply test 4 to a public park and report; don't ask.

**Caveat bands (AWH 2026-11-12):** "A campground that reserves between 10% and 50% of its sites for nightly visitors can be kept but with a caveat that more than half of the sites are long-term residents. A campground in which 50% or more of the sites are nightly needs no caveat." Under 10% fails test 4 (drop).
