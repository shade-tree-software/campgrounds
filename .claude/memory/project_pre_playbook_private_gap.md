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

**PA is DONE** (2026-09-08, commits `cae6715` add + `2f4fa00` audit, ids
13101-13118). 511 PA parks -> 399 commercial -> 62 pass gate -> 29 already in DB
-> 33 candidates -> **18 adds, 15 skips**; waterfront audit 7 changes / 11
confirmed. Instructions: `audit/add_research_instructions_pa_private.md`.

**STILL OPEN**, re-measured 2026-09-08 with a bounding box that actually covers
each state (an earlier pass used one box clipped at lat 40.9 and undercounted PA
by half - measure per state):
- **WV** — 36 pass gate, 23 in DB, **13 candidates**
- **MD** — 9 pass gate, 1 in DB, **8 candidates**
- **DE** — 3 pass gate, 0 in DB, **3 candidates**

24 candidates left; at the VA/PA keep rate (47% / 55%) expect roughly 12 adds.
Candidate lists saved to /tmp/{wv,md,de}_candidates.json during that pass -
regenerate rather than trusting them if /tmp has been cleared.

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

**Two more lessons from PA:**
3. **Agents can emit HTML entities into structured output.** Three PA park names
   came back as `L &amp; M Campground` etc. and would have been stored literally,
   showing as `&amp;` in the picker and every map popup. Run `html.unescape` over
   every string field of an agent's JSON before appending. Check with
   `grep -o '&\(amp\|gt\|lt\|quot\);' campgrounds.json`.
4. **Roughly 6% of gate-passing parks no longer exist**, and RV Life keeps serving
   the records with 4-star ratings intact (one PA slug literally contained
   `-closed-` while the record still rated 4*). VA had 2 closures, PA 2. The
   satellite look is what catches these - a park reading 4*/$$ can be a field.

**Method note for eastern sweeps** (from the PA waterfront audit): state leaf-off
orthoimagery beats Esri's summer tiles where canopy is the obstacle - PA's PEMA
2021-23 layer resolved entries Esri could not, converting forced default-downs
into real verdicts. A **USGS 3DEP elevation transect** settles bluff-versus-open-
bank when imagery argues either way. Look for the equivalent state layer in WV/MD/DE.
