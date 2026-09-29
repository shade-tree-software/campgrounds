---
name: project_remaining_work_map
description: What is actually left on the campground database, measured 2026-09-21 — one schema body and a gap family with four faces
metadata:
  type: project
---

Measured 2026-09-21, after AR and CO. AWH framed it as three bodies; the third is really a family and was missing a member.

## 1. Schema — real, and partly blocked

Coverage: rating 92.0%, hookups 84.3%, booking 80.4%, sites 78.4%, facilities 63.1%, season 32.7%, discounts 14.1%, **fees 0.7%**. Note scanning is DONE — 12,747 of 12,747 scannable notes, queue zero (see [[reference_session_note_scan]] for running it with no API key).

- **Phase 6, the policy registry**: 30 rows covering 45.4% of entries. `policy_priority.py` now reports every remaining candidate at **zero nights slept** — the nights signal that used to prioritise it is spent, so what is left is pick-by-entry-count or pick-when-a-trip-needs-it.
- **Phase 4, the season walk**: first full walk APPLIED 2026-09-21 — 323 seasons written, season 30.6% -> 32.7%, and 1,943 facilities still without a verdict. The cache lives on the laptop. Re-run it months apart; that remainder only closes by accrual ([[reference_recgov_calendar_limits]]).
- **Phase 7**: the "inherited, never verified" UI surfacing, which is what makes the other 55% tractable without hand-verifying 12,832 entries.

## 2. Federal gap — the only body measured AND tooled

**The `likely_rv` list is DONE (2026-09-24): all 178 worked. That day added UT 10 (13223-13232), OK 12 (13233-13244), WA 7 (13245-13251), 18 scattered rows 13 (13252-13264, audit/ridb_gap_misc_decisions.json), CA 16 (13265-13280)**; RIDB's state field was wrong on 3 of the scattered 18, and CA's leftovers were mostly agency-stated size/access failures (17 of 33 excluded), roughly one state per working chunk. UT's lesson: RIDB's `state` can be wrong (Echo Park is in CO), and a notice saying "RVs and trailers are not recommended" settles the size gate before the catalog does. OK's: the rec.gov October calendar is the cheap operating check (a campground whose sites all read Closed while its shelters read Available is closed), and OSM reservoir polygons disagree with the imagery's pool both ways. 10 of the original 178 were never missing — already in the DB under the same rec.gov id, which the coordinate-only gap match could not see; the triage now checks ids. The East yielded 16 adds from 33 rows: size gates, horse camps and dispersed-site systems account for most of the rest. Plus **182 `no_catalog`** rows - ALL WORKED 2026-09-24: 37 added (ids 13281-13317), 145 excluded, per-state audit/ridb_gap_*_nocatalog_decisions.json. Yield ~1 in 5; most are small primitive camps failing on a stated 15-20 ft limit, tent/walk-in, closure or a road the agency says is unfit for trailers. **Every no_catalog id is a rec.gov POI record: link /camping/poi/<id> (or drop it), never /camping/campgrounds/<id>, which 404s.** The federal gap is therefore closed (FS 113, BLM 63) that are nominally federal but behave like body 3: no per-site data means no size gate, no inclusion evidence and no pad plotting, so all three shortcuts that made AR and CO fast are absent. `python3 audit/ridb_gap_triage.py --status` says what is left with no cache and no network. Method: [[reference_ridb_gap_pipeline]].

## 3. Non-RV-Life gap — four faces, only federal measured

- **state** — 2,202 entries, ~48 agencies. **MEASURED 2026-09-21 and it is small:** OH/FL/MN gave 2 real misses in 230 entries (0.9%), 2.4% pooled with SD, so ~20-55 statewide. Tooled: `audit/state_gap_portal.py` ([[reference_state_gap_measurement]]). Deprioritised below the federal gap.
- **local** — 2,511 entries, the face AWH's framing omitted, and *worse* than state: detection is a name-scan of RV Life's own buckets, so it inherits RV Life's omissions twice over ([[reference_local_campground_method]]).
- **Canada** — 700 provincial, and there is no RIDB equivalent at all.
- **private** — 3,574, and probably fine: RV Life is natively a private-park directory and Good Sam independently cross-checked it ([[reference_good_sam_ratings]]).

**Possible mechanical check for state and local:** the Good Sam directory (14,993 parks) covers public campgrounds too, not only Good Sam Parks. Whether it is *comprehensive* for state parks is unknown — measure before trusting it.

## The coupling

They are not independent: **every gap add lands with zero schema fields**, so body 2 manufactures body 1. Close it per state as you go — `recgov_hookups.py` for the federal ones (the catalog answers it), then the note scan.

## Recommended order

**The measuring session happened (2026-09-21) and settled this.** State came back at
1.3–2.8%, ~30–60 campgrounds, so it is no longer a candidate for the next big push; the
federal gap's 334 known rows (152 `likely_rv` + 182 `no_catalog`) are. **Local is still
unmeasured** and is the one left worth measuring — 2,511 entries, and its detection
inherits RV Life's omissions twice over, so it cannot borrow the state answer. The portal
method does not reach it (counties and towns are on no state platform), so it needs a
different instrument.


**UPDATE 2026-09-25:** the federal gap is fully worked (both lists), and the local face was measured: roughly a third of OSM-visible local campgrounds are missing ([[reference_local_gap_measurement]]). Local is now the priority gap.

## QUEUE AFTER THE LOCAL GAP (AWH 2026-09-28)

AWH's order: **finish the local gap first** (east of the Mississippi done 2026-09-27; west of the river next — [[reference_local_gap_measurement]]), **then** these three, all already surfaced by the local pass:

1. **RIDB 0,0 facilities.** RIDB carries some campgrounds at lat/lng 0,0 (Houchin Ferry, Mammoth Cave, RIDB 258992). The 2026-09-21 gap pull filtered to the lower 48 by coordinate, so these were silently dropped - the federal gap is NOT fully closed. Instrument: re-pull the ~6,000 RIDB activity-9 facilities, list type=Campground rows with zero/missing coordinates, pin each from the agency page, then run them through `audit/ridb_gap_triage.py`'s verdicts. Count unknown.
2. **State gap.** Bigger than the 2026-09-21 sample (0.9-2.8%) suggested in places: **Tennessee State Parks has ~10 campgrounds closed for renovation at once, none in the DB** (Big Hill Pond, Pickett, Norris Dam E/W, Pickwick main, Frozen Head, Montgomery Bell, Standing Stone, Cove Lake, Nathan Bedford Forrest) plus Meeman-Shelby (open, absent) - RV Life drops closed parks, so add each with a dated closure caveat ([[feedback_add_with_caveat_not_withhold]]). Also NY state thin (DEC Rogers Rock, Luzerne, Forked Lake, Alger Island, Moose River Plains; OPRHP Buttermilk Falls), NH Deer Mountain, VT Maidstone, NJ High Point, IN Glendale FWA, KY/other items in the audit/local_gap_*_decisions.json `state-gap` notes.
3. **Private gap.** NOT "probably fine" (the section-3 claim above is superseded): the OSM/Good Sam listings show ~100 unmatched private in OH, ~150 ME, ~120 NC, ~250 FL, ~120 TN, ~150 WI, ~150 MI (Steamboat Park, Grand Rapids, 108 full-hookup, among them), ~60 IL. Every per-state decisions file carries a `(private gap)` note with the count. Private adds must pass the live-web-presence rule ([[feedback_require_live_web_presence]]) and the seasonal/membership exclusions.


**2026-09-28: the local gap is CLOSED for the lower 48** (every state swept; see [[reference_local_gap_measurement]]). Next in AWH's queue: (1) RIDB 0,0-coordinate campgrounds, (2) state gap (TN closed parks, NY thin; OR ODF forest camps and CA Turlock Lake SRA logged in the local decisions files), (3) private gap. Possible residual: $$$ agency campgrounds RV Life tags `commercial`, which every state's private-sweep price gate dropped (found in CA).


**2026-09-28: RIDB 0,0 gap MEASURED and triaged (queue item 1).** 242 RIDB Campground facilities sit at 0,0: 77 already cited by rec.gov id, 34 name-excluded, 42 more already in the DB under FS URLs (they are newer FCFS rec.gov listings of campgrounds the sweeps already have), 32 dropped by catalog, **57 left to sweep** (OR 20 - mostly Wallowa-Whitman primitive camps; CO 6, OK 6 USACE, WA 5, WY/UT/CA 3, MT/ID/KS/WI/GA 2, AR 1). Work list = `todo` in `audit/ridb_gap_zero_decisions.json`; move each row to added/excluded there as it is worked. **RIDB has no pin but rec.gov's `/api/camps/campgrounds/<id>` does** (facility_latitude/longitude) for all but the USACE rows and Putah Canyon, which need pinning from the agency page. Side-find: entries 185 and 1105 are BOTH Pound River Campground (same rec.gov id 251949) - a DB duplicate to resolve.

- 2026-09-28 OR chunk done: 7 adds (13659-13665), 13 excluded + 3 carried-forward size-gate verdicts; **34 left** (OK 6, CO 5, WY/UT/WA/CA 3, MT/ID/KS/WI/GA 2, AR 1). Lessons: the 0,0 listings are often a NEW rec.gov id for a campground an earlier decisions file already judged under its old id - match decisions by NAME, not only facility id. For Lostine-type FCFS camps with no published length, Campendium's "Longest Vehicle Reported" + dated rig reviews is the deciding source (maps.campendium.com/us/<town>-or/nature/<slug>). This laptop's recgov_hookups cache holds only ~79 of 2,403 facilities, so fill new entries' hookups via the session note scan (`extract_fields.py --dump/--apply-file`) instead.
- 2026-09-28 Rocky Mountain chunk done: 10 adds (13666-13675), 5 excluded; **19 left** (OK 6, WA 3, CA 3, KS/WI/GA 2, AR 1 - the OK/KS/AR/GA rows are USACE with 0,0 pins even in rec.gov, pin from Corps park maps). Rule used twice: when the FS prose states a small trailer limit ("trailers under 22'") but the rec.gov catalog's MEASURED Driveway Length says 25-99 ft, a limit within ~1 ft of 23 was treated as a pass-with-caveat (a trailer limit counts the trailer, not truck+trailer), while a clear miss (Bottle Creek, "under 16 ft") stays a size-gate exclusion.
- 2026-09-28 USACE chunk done: 8 adds (13676-13683), 3 excluded; **8 left** (WA Cottonwood-Entiat, Lmuma Creek, Ten Mile; CA Penny Pines, Putah Canyon, Moore; WI Horseshoe Lake, Birch Grove). USACE pinning lesson: RIDB AND rec.gov (facility + per-campsite API) all hold 0,0; the catalog's own site coords exist for some; otherwise Good Sam cache (trip_data/goodsam_parks.json) / allstays / Dyrt pins, EACH checked on satellite (Good Sam put Dam Site East on the wrong bank of the river, Moneka in scrub). Catalog lengths often live under "Site Length" not "Max Vehicle Length" - ridb_gap_triage's fit_summary misses them. Side-find: Eufaula's Dam Site South is not in the DB either.
- **2026-09-28 RIDB 0,0 gap COMPLETE**: 57 candidates -> 28 added (13659-13686), 29 excluded; all recorded in audit/ridb_gap_zero_decisions.json. Queue item 1 is DONE; next in AWH's queue is (2) the state gap (TN closed parks, NY thin, OR ODF, CA Turlock Lake) then (3) private. Loose ends: Eufaula's Dam Site South absent; entries 185 and 1105 are a Pound River duplicate. Nothing pushed yet (commits from 2ac8ef2 on).
