---
name: project-keys-rescreen
description: DONE 2026-10-30 - Florida Keys price re-screen: 26 RV Life candidates vetted, +14 (15574-15587), 12 skips; AWH rules for the Keys (owner-lot, RV Life tier as price) inside
metadata:
  type: project
---

AWH 2026-10-30: "do a mini-sweep of the florida keys to see if any campgrounds were dropped due to price. Campgrounds on the keys that pass all other criteria can be kept even if the price is too high."

**What was found:** nothing in the Keys had been removed from the DB on price (git-history scan). The gap was upstream: the FL private sweep only screened RV Life `$`/`$$` parks, and nearly every Keys park is `$$$`+, so only 4 Keys entries existed (Pennekamp 370, Bahia Honda 371, Curry Hammock 636, Sugarloaf KOA 15422).

**Method:** copy of the family-home re-screen ([[project-family-home-rescreen]]) in `audit/keys_rescreen_2026-10-30/`: candidates.json (26 from RV Life's Keys list, incl. Long Key SP), verdicts.jsonl (9 name pre-skips: 3 Sun Outdoors, 2 Encore, Elks, 3 military), instructions.md, add_results.py (dry run; --apply), results/<slug>.json. One agent per candidate, sequentially. Owner-lot (CONDO_PARK) resorts: AWH 2026-10-30 "Florida Keys owner lot resorts that rent spots by the night are ok if they have a normal booking site which works like a regular nightly campground and they meet all other criteria (except price)" - so test 5's "sells lots" is waived in the Keys for an association/manager-run booking engine; owner-only VRBO/phone rentals still skip. Canals: size rule (~30 m+ riverfront, narrower creekside); a marina basin open to the bay with the bay in view = bayfront.

**Resume:** run add_results.py for what's done; the next candidate is the first slug in candidates.json with no results file.

**DONE 2026-10-30: +14 (ids 15574-15587), 12 skips, all committed (through 43dfee31), NOT pushed.** Adds: Key Largo Kampground (owner-lot, riverfront channel), Keys Palms, Kings Kamp, Grassy Key RV Park, Jolly Roger, Bonefish Bay (passes on RV Life $$$$ - AWH 2026-10-30 "you can let RV Life $$$ or $$$$ count as a price in the Florida Keys"), Coconut Cay, Safe Harbor Marathon, Big Pine Key, Sugarloaf Key RV Resort (= ex-Sun Outdoors Sugarloaf Key, off the Sun brand since 2025-04-15; added as not-Sun, ask logged in audit/verify/asks.md), Bluewater Key (owner-lot; 3-night advance minimum waived by phone within 7 days), Geiger Key (creekside), Boyd's, Leo's (pond). Skips: Campers Cove, Captain Jax, Calusa, Venture Out, Breezy Pines (owner-only rentals), Pelican Cay, Point of View, America Outdoors, Knights Key (redeveloped), Bluefin (no rate + 3-night minimum), Long Key SP (tent-only), El Mar (30-ft rig minimum). Lessons: agents twice put two URLs in `website` (add_results.py now refuses whitespace); agents called marina channels "bayfront" - I defaulted Key Largo Kampground to riverfront, Bonefish to not waterfront, Geiger to creekside; a 7-night Dec-Mar minimum is time-of-year (Quartzsite), the 3-month cap is for 28/30/90-night minimums only.
