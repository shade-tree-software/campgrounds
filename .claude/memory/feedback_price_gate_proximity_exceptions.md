---
name: feedback_price_gate_proximity_exceptions
description: AWH keeps some over-$50 / skip-brand campgrounds because of where they are (near family, near NYC); don't remove them on price or brand
metadata:
  type: feedback
---

Some campgrounds stay in the DB despite failing the $50 price gate or the KOA/Sun brand skip, because their location is unusually useful:

- 14882 Fort Myers / Pine Island KOA Holiday (FL, $104.50+) - near one of the family homes (AWH 2026-10-10).
- The Fort Myers relaxed-price mini-sweep (2026-10-05, ids 14868-14877 + holds 14880/14881) is the same family-proximity exception; AWH 2026-10-10 confirmed Bonita Lake 14875, Imperial Bonita Estates 14876, Sanctuary 14877 stay.
- 14435 Twin Palms Resort (FL, Lakeport; RV sites exactly $50) kept (AWH 2026-10-10) - $50 is at the gate, not over.
- 3363 Liberty Harbor RV Park (NJ, $170/$189 holiday) - "unusual proximity to New York City" (AWH 2026-10-10).

**Why:** the gate screens ordinary options; a rare location (family visits, a city with almost no RV camping) outweighs price.

**How to apply:** record the real price, but don't flag these for removal again. When a new over-gate entry is near family or a major city with few alternatives, ask rather than drop. Related: [[feedback_skip_sun_koa_brands]], [[feedback_mandatory_fees_count]].

**Scope of the gate (AWH 2026-10-10, confirmed):** the $50 price gate applies to PRIVATE campgrounds only. Government campgrounds (county/city/water district/fairgrounds/state/federal) have no price limit - don't flag them as over-gate (Santee Lakes $62-111 and Bay RV Stay $85-125 are fine).
