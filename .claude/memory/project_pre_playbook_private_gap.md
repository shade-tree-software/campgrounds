---
name: project_pre_playbook_private_gap
description: Pre-playbook states (VA/MD/DE/PA/WV) had Good-Sam-sourced private stages, so independent parks with no Good Sam rating were never candidates; VA re-swept 2026-09-07, MD/DE/PA/WV still open
metadata:
  type: project
---

The five states swept BEFORE the RV-Life-first curation playbook was written
(commit `8b14294`, 2026-06-01) had their **private stage detected from Good Sam**,
with RV Life used only to *filter* that list on price/stars. Any independent park
with no Good Sam rating was therefore never a candidate at all. Affected:
**VA, MD, DE, PA, WV**.

**Found via:** AWH asked whether Gooney Creek Campground (Front Royal VA) existed
on 2026-09-07. It does — RV Life 5*/$$ — and it was missing. The cause was the
sourcing, not the gate.

**VA is DONE** (2026-09-07, commits `5940854` Gooney Creek + `0f4436c` add +
`60d153b` audit, ids 13085-13100). RV-Life-first detection: 317 VA parks -> 211
commercial -> 39 pass <=$$ / >=4-star -> 7 already in DB -> 32 candidates ->
**15 adds, 17 skips**; waterfront audit 5 changes / 10 confirmed. Instructions
file `audit/add_research_instructions_va_private.md` is reusable for the rest.

**STILL OPEN**, measured 2026-09-07 with the same gate + dedup:
- **PA** — 28 pass gate, ~18 not in DB
- **WV** — 36 pass gate, ~13 not in DB
- **MD** — 9 pass gate, ~8 not in DB
- **DE** — 3 pass gate, ~3 not in DB

~42 candidates; at VA's ~47% keep rate expect roughly 20 real adds.

**Why:** the gap is invisible from inside the data — a campground that was never
a candidate leaves no trace, and every VA entry passed its inclusion audit, so
the coverage looked complete. Only re-running detection from the other source
surfaces it.

**How to apply:** point the batches at
`audit/add_research_instructions_va_private.md` (swap the VA-specific
authorities section for the state's own), run research agents SEQUENTIALLY at
~8/batch, `append_state.py --state <ST> --leads`, then the waterfront audit
subagents and `apply_waterfront_audit.py`. See [[feedback_sequential_sweep_agents]]
and [[reference_rvlife_price]].

**Two lessons worth carrying into any private stage** (both cost real entries in VA):
1. **A dead official domain is a strike, NOT an automatic skip.** 4 of the 16 VA
   adds had dead domains while being demonstrably live and bookable — Gooney
   Creek's gooneycreek.com 301s to an unrelated veterinary company while the
   campground is instant-bookable on Hipcamp. Point `website` at the live booking
   channel and record the dead domain in the `note`.
2. **More than half the parks passing RV Life's price/star gate are not publicly
   bookable campgrounds.** VA's 17 skips: 6 Elks lodges, 4 Thousand Trails, a
   Bluegreen timeshare, an Airstream-owners co-op, 2 deeded-membership/lot-
   ownership parks, 2 closed, 1 unconfirmable. Budget agent time accordingly —
   the gate is a candidate filter, never a keep decision.
