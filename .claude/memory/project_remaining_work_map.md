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

**Only CA's 33 `likely_rv` left (2026-09-24; UT 10 added ids 13223-13232, OK 12 ids 13233-13244, WA 7 ids 13245-13251, the 18 scattered rows 13 ids 13252-13264 in audit/ridb_gap_misc_decisions.json)**; RIDB's state field was wrong on 3 of those 18, roughly one state per working chunk. UT's lesson: RIDB's `state` can be wrong (Echo Park is in CO), and a notice saying "RVs and trailers are not recommended" settles the size gate before the catalog does. OK's: the rec.gov October calendar is the cheap operating check (a campground whose sites all read Closed while its shelters read Available is closed), and OSM reservoir polygons disagree with the imagery's pool both ways. 10 of the original 178 were never missing — already in the DB under the same rec.gov id, which the coordinate-only gap match could not see; the triage now checks ids. The East yielded 16 adds from 33 rows: size gates, horse camps and dispersed-site systems account for most of the rest. Plus **182 `no_catalog`** rows (FS 113, BLM 63) that are nominally federal but behave like body 3: no per-site data means no size gate, no inclusion evidence and no pad plotting, so all three shortcuts that made AR and CO fast are absent. `python3 audit/ridb_gap_triage.py --status` says what is left with no cache and no network. Method: [[reference_ridb_gap_pipeline]].

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
