---
name: project-family-home-rescreen
description: "TODO (AWH 2026-10-21) - re-screen private parks once rejected on price that sit within 40 km of a family home, now that family homes are gateways; candidate list and method inside"
metadata:
  node_type: memory
  type: project
  originSessionId: 5a2365fc-fe6c-4508-9059-5f9b77057f7c
  modified: 2026-10-21T18:36:13.301Z
---

**The task.** AWH 2026-10-21 made family homes gateways ([[feedback_price_gate_proximity_exceptions]]): `audit/price_research/gateways.py` now reads trip_data/family.json, so any private park within 40 km of a family home skips the US$50/C$69 cap. He wants the parks the earlier sweeps rejected on price only (never added) re-screened against the new rule. **To be done in a separate session.** It must run on a machine that has trip_data/family.json; without it, gateways.py finds no family homes.

**Already checked, 2026-10-21:** of the 548 ids dropped from the DB on price or in phase 7, none comes back. The four near a family home (Orange Grove 14868, Gulf Waters 14871, Sanctuary 14877, Swan Lake 14880) were all dropped for other reasons.

**Candidate list found 2026-10-21.** This covers parks within 40 km of a family home with no other gateway. A park that already had a gateway was exempt before, so it needs no re-screen.
- **Private-gap verdicts** (`audit/<st>_private/verdicts.jsonl`; decision skip, kind_of_no matching price/$/over). Joined to each dir's candidates/list JSON by name for lat/lng: 580 price skips, 5 unlocated.
  - **9 hits, all Pennsylvania** (pa_private): Quakerwoods, Tohickon Family, Brandywine Creek, Sara's (3 km), Boulder Woods, Little Red Barn, Hidden Acres, Adventure Bound Oak Creek, Family Affair. The last two were skipped on RV Life $$$+ alone, with no published rate.
- **KOA backlog** (`audit/koa_backlog_2026-10-19/verdicts.json`, verdict over / no quote), 3 hits: Bradenton / Hunsader Farms (FL, $72), Erie KOA Holiday (PA, no quote), Philadelphia / West Chester (PA, $70).
- **Fort Myers mini-sweep** (`audit/fortmyers_private/verdicts.jsonl`): Bermuda Lakes RV Resort ($159, over the old relaxed $150 cap). It's unlocated in that dir; look it up. That $150 cap is gone now.
- **Not yet scanned:**
  - The Sun Outdoors/Retreats brand pre-skips (kind_of_no "price (brand)"). Ask AWH whether the family-home gateway lifts a brand skip, since its stated reason is price.
  - `audit/canada_no_rate/`.
  - Any price skip recorded outside a verdicts.jsonl, e.g. audit/price_research/*/ run outputs.

**How to apply (each candidate is a normal add, not a restore):**
1. Re-run the full gate except price. That covers presence, star/quality, the long-stay tests ([[feedback_exclude_seasonal_residential]]), minimums ([[feedback-minimum-stay]]), the 23-ft fit and waterfront and inclusion evidence ([[feedback_campground_vetting_discipline]]).
2. Re-read current rates.
3. Append with `append_state.py`, and take the next id from BOTH location files.
4. Report the adds and skips to AWH in one list.
