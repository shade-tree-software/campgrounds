---
name: reference-camplife-api
description: How to price a CampLife-booked park (pass of 2026-10-14, 88 entries) - estimates expose per-stay fees, the messages that mean "no quote", wrong-park links, login gates, placeholder rig lengths
metadata:
  type: reference
---
Recipe from the CampLife tier-only pass (batches 25-31, 2026-10-14; files and report items in `audit/price_research/camplife_tier/`, builder `audit/price_research/camplife_tier_build.py`).

- **Reads:** `audit/private_gap_browser/camplife_api.py OUT.jsonl ID:URL` reads a listing's record (site types, per-site "longest rig", equipment, description) and one-night quotes on fixed dates; the builder turns that jsonl into fee findings and field sets. The session helpers (1-3 night estimates for one date, a page fetch through the driver browser for sites that 403 a plain fetch) were scratch scripts; rebuild them from camplife_api.py.
- **Per-stay fees only show up in 1-, 2- and 3-night estimates:** the step between nights is the nightly rate, the remainder is a flat per-stay fee. CampLife's own US$3.50 charge is never stored; a park's own flat fee goes in `fees.reservation_fee` (seen $3, $5, $10, C$3, C$8.50, C$9, C$15). Agency fees: Idaho Power $7 online / $15 phone, PacifiCorp Lewis River $8, Jackson $8, Josephine $9, Linn $12, George Lane C$5.
- **No-quote messages:** 'The park is closed at this time', 'The park is open April 24-Nov 1', 'We are not taking reservations for this time', 'Online Reservations for the 2026 season will open ...', and estimates that return no price (Sauble Beach). 'A 2 night minimum stay is required for all online reservations' is a real `min_stay`. 'please log in above' / 'You must be logged in to see availablility' = login-gated: price from the operator's own page and list it as ASK/DROP? ([[feedback_drop_login_required]]).
- **Traps:** a CampLife link can be a different park (id 331 is Newport RV Park in Rhode Island, not Newport WA); parks leave CampLife for ResNexus or Campspot (re-point website line 2); a generic idaho_power link must be relinked to the park's own listing; a "Tent" site counts only if its equipment list takes an RV (VAN/FOLDDOWN/TENT only = out); a lone 100-ft "longest rig" is a placeholder, a spread (100/90/85 ft) is real; ResNexus pages render only in the driver browser; quote checks break on U+2011 and on " | " table separators, so copy quotes from the bundle.
- **Canada:** quotes are before HST; price against the ~C$55 private gate and list over-gate parks as ASK/DROP?.
