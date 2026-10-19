---
name: feedback_skip_sun_koa_brands
description: Skip Sun Outdoors / Sun Retreats on brand in private sweeps; the KOA brand skip is RETIRED (AWH 2026-10-19) - KOAs are vetted like any private park
metadata:
  type: feedback
---

**Sun Outdoors / Sun Retreats / Sun RV Resorts:** still pre-skipped on brand in the private gap and any private sweep, kind_of_no "price (brand)". AWH 2026-10-03: "I've never seen one that fits our price range."

**KOA (Journey, Holiday, Resort): the brand skip is retired (AWH 2026-10-19).** "The existing KOA rule was from back when KOA prices were unreadable. Now that you can read them, treat them like any other private campground, subject to the regular rules, exclusions, and exceptions." So a KOA goes through the normal star gate, price gate (US$50 / C$69), gateway exemption ([[feedback_price_gate_proximity_exceptions]]), minimum-stay rule ([[feedback_minimum_stay]]) and presence checks.

**How to price a KOA:** `audit/private_gap_browser/koa.py SLUG MM/DD/YYYY MM/DD/YYYY` (needs `drv_server.py` running; KOA_DUMP=path saves the page text, which also carries minimum-stay lines). A plain fetch gets Cloudflare's 403. 28 of 30 quoted on 2026-10-19; the misses were calendars already closed for the season. Real quotes run well apart from the brand's reputation: Needles $37, Gros Morne $37, Spring Grove $40, but Glacier-area KOAs $96-269 in June.

**Backlog:** ~400 RV Life 4*+ KOAs (lower 48 + provinces) are not in the DB because earlier sweeps pre-skipped them; RV Life avg_rate puts ~56 at or under $50. Offered to AWH 2026-10-19, not started.

**Named exception (AWH 2026-10-10):** Fort Myers / Pine Island KOA Holiday (14882, FL; $104.50+/night) stays despite price, because it is near one of the family homes.
