---
name: project-keys-rescreen
description: IN PROGRESS 2026-10-30 - Florida Keys price re-screen (AWH lifted the price gate for the whole Keys); 26 RV Life candidates, one agent each; tooling in audit/keys_rescreen_2026-10-30/
metadata:
  type: project
---

AWH 2026-10-30: "do a mini-sweep of the florida keys to see if any campgrounds were dropped due to price. Campgrounds on the keys that pass all other criteria can be kept even if the price is too high."

**What was found:** nothing in the Keys had been removed from the DB on price (git-history scan). The gap was upstream: the FL private sweep only screened RV Life `$`/`$$` parks, and nearly every Keys park is `$$$`+, so only 4 Keys entries existed (Pennekamp 370, Bahia Honda 371, Curry Hammock 636, Sugarloaf KOA 15422).

**Method:** copy of the family-home re-screen ([[project-family-home-rescreen]]) in `audit/keys_rescreen_2026-10-30/`: candidates.json (26 from RV Life's Keys list, incl. Long Key SP), verdicts.jsonl (9 name pre-skips: 3 Sun Outdoors, 2 Encore, Elks, 3 military), instructions.md, add_results.py (dry run; --apply), results/<slug>.json. One agent per candidate, sequentially. Owner-lot (CONDO_PARK) resorts come back as "hold" for an AWH call (test 5 says selling lots fails, but many run rental programs).

**Resume:** run add_results.py for what's done; the next candidate is the first slug in candidates.json with no results file.
