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
1. DONE 2026-10-09 for 64 of the 89 dispersed entries (`audit/price_research/dispersed_*.json`,
   applied by `audit/price_research/apply.py`, source URL in provenance). Key sources:
   **16 U.S.C. 6802(d)(1)(C),(E)** (FLREA) bars FS/BLM/BoR fees for dispersed areas and
   undeveloped camping — the basis for the Monongahela + GWJ roadside sites; PA DCNR state
   FOREST motorized sites $10 res / $15 non-res (a different program from state parks).
   OPEN: WV WMAs 111/112 (no official fee statement), IL Pyramid SRA 1658 (2027 fee change),
   NM 8027, UT 10003, NV 11239/11251, ID 9427, WV 121, NV 11311 tribal permit, and 11 private
   parks (belong to task 2). **VA WMAs RESOLVED 2026-10-09** (AWH called the DWR helpline): $10 camping authorization per party (6 people, 14 nights) + $4 daily Access Permit per person 17+ for EVERY day on site, arrival and departure both (1 night = 2 permits each). `wma:VA` registry row rewritten (no nightly $0 any more) and all 23 VA WMA entry notes carry one standard line. Access Permit and authorization are the same price for non-residents.
2. IN PROGRESS - see [[project_price_research]]. Bigger: any entry with no price info (no fees, nothing priced in the note) AND no RV Life
   `price_tier`: 1,553 (596 federal, 452 state, 341 local, 130 private). Needs web research
   per entry; do it as chunked, committed batches ([[feedback_chunked_bulk_passes]]) and
   sequential agents ([[feedback_sequential_sweep_agents]]).
