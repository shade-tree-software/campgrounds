---
name: reference_rvlife_index_has_gaps
description: RV Life's park index silently omits real agency campgrounds — cross-check the agency's own park list before calling a state sweep complete
metadata:
  type: reference
---

**RV Life's Algolia `park` index is not a complete list of a state agency's campgrounds, and the gap is silent.** Five South Dakota GFP campgrounds that publish sites, rates and a per-site campground map on `gfp.sd.gov` return **nothing** from the index when queried by name: Buryanek (44 sites), Sheps Canyon (22 electric + 40 non-electric), Platte Creek (36), Lake Carthage (13 electric), Amsden Dam (12). They were never rejected by the sweep's gates — they were never seen, because detection starts from RV Life (see [[project_sd_sweep_handoff]], [[reference_local_campground_method]]).

**Why it matters:** an RV-Life-driven sweep can reach "100% audited" while missing real, bookable, publicly-run campgrounds, and nothing in the evidence fields reveals it — `waterfront_evidence`/`inclusion_evidence` only tell you about entries that exist.

**How to apply:** for any state whose parks are run by one agency, walk the AGENCY's own park list (SD: the region-grouped `<select>` of park links in any `gfp.sd.gov/parks/detail/<slug>/` page; most states have an equivalent index page) and diff the names against what's already in `campgrounds.json`. It is a free check and it is the only one that catches this class of miss. Do it as a closing stage of a state sweep, not as a separate project.

Corollary: those five have **no `rating` group**, and that is correct rather than a gap — `rating` comes from RV Life and there is no row to read. Don't backfill stars/price from another source without changing `rating.source`.

Related: [[feedback_absent_is_not_unknown]], [[project_campground_schema]].

## Measured nationwide, 2026-09-21 — the federal gap is ~585 candidates

SD was not a one-off. Diffing **RIDB** (recreation.gov's own facility catalog, `activity=9`, `FacilityTypeDescription == "Campground"`, the authoritative federal list and wholly independent of RV Life) against `campgrounds.json`:

- 4,371 RIDB campgrounds with coordinates → **1,684 have no DB entry within 1.5 km**
- minus Alaska (235, out of scope) → 1,449 in the lower 48
- minus 622 whose NAME says they are not a drive-in RV campground (group 166, cabin 143+6, guard station 72, lookout 66, picnic 34, day use 26, horse camp 21, shelter 17, …) → 827
- minus 202 that DO have a DB entry once the radius widens to 3 km (RIDB pin drift) → 625
- minus 40 with a same-name DB entry within 50 km → **585 genuinely absent**, 403 of them reservable

**Sampling 60 of the 585 against RIDB's per-campsite catalog:** 21 are real RV campgrounds with 3+ RV-capable public sites, 19 have no catalog at all (FCFS — unknown, not "no", and most are real USFS drive-in campgrounds), 19 have no RV sites (tent/cabin/boat-in), 1 has 1–2. So the firm floor is ~205 real missing RV campgrounds and the realistic figure is **~250–350**. Verified individually: Blanchard Springs (AR), Rocky Bluff (NC), Alum Ford (KY), Gypsum (CO), Howard Lake (MT), North Fork Siuslaw (OR), Porcupine Flat (Yosemite, 49 RV sites).

Concentrated in the public-land west: CA 111, OR 59, CO 39, MT 36, ID 33, UT 30, WY 27, AR 21, AZ 20, WA 19, TN 19, MI 19, OK 17, GA 16, NM 15.

**The work list is `audit/ridb_gap_2026-09-21.json`** (585 rows, per-state, with `facility_id` and a rec.gov deep link), written untracked. Regenerate it the same way after any federal top-up.

**What this means for "sweep COMPLETE".** Every per-state handoff marked complete means *complete against RV Life*, not against the agencies. The federal half now has a mechanical, authoritative cross-check (RIDB) that costs one paged API pull; there is no equivalent single source for state parks, so that side stays per-agency (the SD method). SD's own state rate was 5 missed out of 59 GFP campgrounds, ~8%; one data point, not a projection.
