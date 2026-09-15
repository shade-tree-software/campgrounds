---
name: project_pre_playbook_private_gap
description: CLOSED 2026-09-15. Pre-playbook states (VA/MD/DE/PA/WV) had Good-Sam-sourced private stages so unrated independents were never candidates; all five re-swept, 39 adds total
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

**WV is DONE** (2026-09-15, commit `68f7811`, ids 13119-13122). 13 candidates ->
**4 adds, 9 skips** (31%, well under VA/PA). Instructions:
`audit/add_research_instructions_wv_private.md`; per-candidate reasoning in
`audit/wv_private/results_*.json`, which is COMMITTED - a campground that was
never added leaves no trace in the data, so the skip reasons are the only record.

**MD is DONE** (2026-09-15, commit `2c24291`, ids 13123-13124). 8 candidates ->
**2 adds, 6 skips**. Reasoning in `audit/md_private/results_*.json`.

**DE is DONE** (2026-09-15, commit below). 3 candidates -> **0 adds, 3 skips**:
two Elks lodges, and Sun Retreats Rehoboth Bay, which is predominantly a
manufactured-home community (see `audit/de_private/results_de.json`). The
predicted yield was "1 add, possibly 0" and it was 0 - a state can be genuinely
finished.

**PROJECT CLOSED.** All five pre-playbook states re-swept: VA 15 + PA 18 + WV 4
+ MD 2 + DE 0 = **39 campgrounds** that were invisible to the original Good-Sam
sourcing. Nothing is outstanding. Do NOT re-open without a new reason - the
remaining skips are documented per candidate and several are deliberate
"cannot verify" holds, not oversights.

**One finding worth keeping loose from the project:** Sun Communities runs TWO
different Delaware properties both named "Rehoboth Bay" - `Sun Outdoors Rehoboth
Bay` (id 959, ex-Resort at Massey's Landing, 20628 Long Beach Dr, 302-947-2600,
the one in the DB) and `Sun Retreats Rehoboth Bay` (ex-Leisure Point RV Resort,
25491 Dogwood Ln, 302-945-2000, 4.9 km away, skipped). A future sweep hitting
either name should check WHICH before calling it a duplicate. Verified 2026-09-15
that id 959's name is still current - Sun's Outdoors->Retreats rebrand has not
reached it.

**What the last two states added to the method:**
- **Do the research INLINE, not in a subagent** (AWH 2026-09-15). One agent on 7
  WV candidates ate half a session and returned all-or-nothing; done inline the
  remaining 6 took a fraction of that, with a stop point after every candidate
  and each verdict written to disk as it was made. See
  [[feedback_sequential_sweep_agents]] and `audit/README.md` step 2.
- **The parked official domain is the dominant WV/MD failure**, hit 3 of 13 WV
  candidates. familyfishingncamping.com and littlecoalrivercampground.com both
  return a stub that JS-redirects to /lander. Probe with
  `curl -sS -L -w '%{size_download}'` - a ~114-byte 200 is the tell - before
  trusting a domain an aggregator lists. Gheny Nook survived the same dead-domain
  problem only because its operator has a live Facebook page and a county CVB
  listing.
- **Skip reasons must say WHICH KIND of no.** Several of these are "real campground,
  cannot verify" (parked domain, no booking channel) or "real campground, wrong
  size" (Spring Gap's 20-ft NPS cap) rather than "not a campground". Those are
  re-openable and the reason has to record that, with the phone number where one
  exists.
- **`append_state.py` now writes `rating`** (commit `1617f6d`) - it did not before,
  so VA/PA got theirs only by accident of a later `extract_rating.py` pass. No
  manual step needed any more.

**Why:** the gap is invisible from inside the data — a campground that was never
a candidate leaves no trace, and every VA entry passed its inclusion audit, so
the coverage looked complete. Only re-running detection from the other source
surfaces it.

**How to apply:** copy the nearest state's instructions file (WV's is the most
evolved: `audit/add_research_instructions_wv_private.md`) and swap the
state-specific authorities section, then **do the research inline yourself, one
candidate at a time**, writing each verdict to `audit/<st>_private/results_*.json`
as you make it. Then `append_state.py --state <ST> --leads`, the waterfront audit,
and `apply_waterfront_audit.py`. If you ever do use subagents instead, it is ONE
candidate per agent - see [[feedback_sequential_sweep_agents]] and
`audit/README.md` step 2. Also [[reference_rvlife_price]].

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
