---
name: reference_roverpass_api
description: "How to price a RoverPass park - plain-HTTP GraphQL (no browser), isBookable is the line between a claimed listing and an unclaimed directory page, closed dates list no rates, and the traps of the 2026-10-14 pass (rally carts, \"RV on site\" rentals, amenity tags vs rules, implausible Discount Clubs, rate tables of closed parks, camper reports)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 697b5c76-5652-4131-bd7c-1761a58eb19c
  modified: 2026-10-14T08:49:51.114Z
---

RoverPass prices come from RoverPass's own booking API over **plain HTTP, no browser**: the park's `/c/<slug>/booking/` page gives the session cookie, the csrf token and a static API token, and every query is a GraphQL POST. The queries and the pacing (`RP_PAUSE`, 1 s) are at the top of `audit/private_gap_browser/roverpass_api.py`, and what is stored is described in the docstring of `audit/price_research/roverpass_tier_build.py`. Built for the 347 tier-only entries that link roverpass.com, 2026-10-14 ([[project_price_research]]). Batch outputs and the per-batch report are in `audit/price_research/roverpass_tier/`, and the steps are the Campspot pass's ([[reference_campspot_api]]).

- **`isBookable` is the line.** Only 55 of the 347 took bookings. 285 were directory listings nobody has claimed ("Claim my Campground", "Last Updated: 11/15/2024"), and their rate tables are not the operator's ([[feedback_note_rate_sourcing]]). 3 were claimed with booking switched off, and 4 listings were gone. AWH's #8f (2026-10-14) settled them: price each from the operator's own pages, remove the unclaimed link whenever an entry is touched, and drop under the usual rules without asking. Done in 37768ea (`audit/price_research/roverpass_ops_2026-10-14/`): 104 priced, 143 links removed, 64 dropped, 34 held.
- **Closed dates list no rates**, unlike Campspot's. The reader falls back to the first dates after the closure.
- **"Open" with an empty `ratesAvailableDuring` means nothing is on sale** (Western Pines 7911 on every date), not that the park is free.
- **Rates that aren't campsites:**
  - "RV on site" is a night in the park's own trailer (Cozy Acres 7475); leave it out.
  - A rate needing 8+ nights is a long-stay product.
  - A rate sold only to a group (military, first responders, members) is a discount.
  - A rate needing 2-7 nights on a date is priced, and the minimum is said. The builder writes `booking.min_stay` only when no RV rate sells one night (The Preserve 7861).
- **The cart can price a different product.** Bulldog Creek 5818's October dry-camping cart priced the Sturgis Rally variant, with a $15 mandatory spot fee. Check the cart's item names before reading a fee off it.
- **Rates can include tax.** Lake Chalet 1521 and Kenolie 4090 say so in their rules, and the fee note must say so. RoverPass's platform fee, its processing fee and tax are never stored.
- **Amenity tags can contradict the rules.** Tin Valley 7870's rate is tagged water and sewer, but its description and rules deny both. The park's own words win.
- **"Discount Clubs" is the operator's checklist and can be implausible.** Tin Valley lists KOA, Jellystone and Thousand Trails; don't use a list like that. A plausible one may set `good_sam` true against Good Sam's directory (Lake Point 7617, Western Pines 7911), and goodsam_discounts.py then lists the conflict.
- **A claimed listing's rate table can price a closed park.** Fairview 12653 was closed until May and sold no date, so it was priced from the claimed listing's own rate table (it carries a "Last Updated" date). An unclaimed listing's table never counts.
- **A listing with no rates and no operator page:** a dated 2024+ camper report may price it, and the note must say so ([[feedback_camper_report_rates]]). Western Pines 7911 was priced $40-50 from RV Life reviews of January and October 2026.
- **The park record's phone often differs from the entry's.** Since AWH's #6 (2026-10-14) the number the park publishes wins ([[feedback_follow_published_identity]]).
- **A "Waterfront" tag or riverfront marketing is a lead for a re-audit, never a call**, as with Campspot's.
- **Watch for parks that read as communities rather than campgrounds:** monthly-only RV sites, waitlists, leases, background checks, or lots for sale. Price them anyway and hold them for the long-stay criteria AWH asked for on 2026-10-14 (proposed that day, not yet approved).
