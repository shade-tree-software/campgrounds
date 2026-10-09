---
name: project_free_fees
description: 2026-10-09 free-camping fees pass (783 entries) and the two price-research follow-ups AWH asked for
metadata:
  type: project
---

AWH 2026-10-09: "pointless that we mention discounts for free dispersed sites and other free
campgrounds". Cause: `_moot_agency_keys` drops inherited discounts only when the entry's OWN
fees are $0/$0, and only 10 entries had fees. Fixed by recording fees from the notes —
`audit/free_fees/` (candidates.py finds, show.py prints, d*.txt are the hand decisions,
apply_free.py writes). 752 → 0/0, 31 → 0/N; discount chips on "free" notes 299 → 9 (the 9
have a paid tier/season or were skipped on purpose). Chip reads "free" / "free–$N/night" /
"some sites free". Rules in docs/campground-schema.md (fees section).

**Follow-ups AWH asked for (not started):**
1. Dispersed/boondocking entries with no price info anywhere: 89 (47 federal, 24 state,
   12 private, 6 wma) — research each (agency page / rec.gov / BLM-USFS site) for free vs fee.
2. Bigger: any entry with no price info (no fees, nothing priced in the note) AND no RV Life
   `price_tier`: 1,553 (596 federal, 452 state, 341 local, 130 private). Needs web research
   per entry; do it as chunked, committed batches ([[feedback_chunked_bulk_passes]]) and
   sequential agents ([[feedback_sequential_sweep_agents]]).
