---
name: feedback_skip_sun_koa_brands
description: Skip Sun Outdoors / Sun Retreats on brand in private sweeps; the KOA brand skip is RETIRED (AWH 2026-10-19) - KOAs are vetted like any private park
metadata:
  type: feedback
---

**Sun Outdoors / Sun Retreats / Sun RV Resorts:** still pre-skipped on brand in the private gap and any private sweep, kind_of_no "price (brand)". AWH 2026-10-03: "I've never seen one that fits our price range." **Gateways don't lift it (AWH 2026-10-21):** a Sun park within 40 km of a family home is still skipped.

**KOA (Journey, Holiday, Resort): the brand skip is retired (AWH 2026-10-19).** "The existing KOA rule was from back when KOA prices were unreadable. Now that you can read them, treat them like any other private campground, subject to the regular rules, exclusions, and exceptions." So a KOA goes through the normal star gate, price gate (US$50 / C$69), gateway exemption ([[feedback_price_gate_proximity_exceptions]]), minimum-stay rule ([[feedback_minimum_stay]]) and presence checks.

**How to price a KOA:** `audit/private_gap_browser/koa.py SLUG MM/DD/YYYY MM/DD/YYYY` (needs `drv_server.py` running; KOA_DUMP=path saves the page text, which also carries minimum-stay lines). A plain fetch gets Cloudflare's 403. 28 of 30 quoted on 2026-10-19; the misses were calendars already closed for the season. Real quotes run well apart from the brand's reputation: Needles $37, Gros Morne $37, Spring Grove $40, but Glacier-area KOAs $96-269 in June.

**Backlog: DONE 2026-10-19** (audit/koa_backlog_2026-10-19/, followups.md there is the state). 400 RV Life 4*+ KOAs quoted on koa.com: +134 added (ids 15397-15530, 7 commits), 243 skipped over the gate (verdicts.json), 0 drops. Most "no quote" rows were calendars ending before May 2027 - the page says "the latest date you can make a reservation for is X"; retry.py re-quotes inside the window, and an off-season quote is only a lower bound (over = firm skip; a pass needs margin or the park's peak season). Left for spring 2027: dodge-city KS, cave-junction OR, beaver UT (at the gate off-season) and ~10 closed calendars; 5 RV Life rows whose koa.com reserve page 404s.

**Fort Myers / Pine Island KOA Holiday (14882, FL; $104.50+/night)** stays on the family-home gateway (10 km). It was a named exception until AWH retired those on 2026-10-21.
