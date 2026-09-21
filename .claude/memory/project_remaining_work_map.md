---
name: project_remaining_work_map
description: What is actually left on the campground database, measured 2026-09-21 — one schema body and a gap family with four faces
metadata:
  type: project
---

Measured 2026-09-21, after AR and CO. AWH framed it as three bodies; the third is really a family and was missing a member.

## 1. Schema — real, and partly blocked

Coverage: rating 92.0%, hookups 84.3%, booking 80.4%, sites 78.4%, facilities 63.1%, season 30.6%, discounts 14.1%, **fees 0.7%**. Note scanning is DONE — 12,747 of 12,747 scannable notes, queue zero (see [[reference_session_note_scan]] for running it with no API key).

- **Phase 6, the policy registry**: 30 rows covering 45.4% of entries. `policy_priority.py` now reports every remaining candidate at **zero nights slept** — the nights signal that used to prioritise it is spent, so what is left is pick-by-entry-count or pick-when-a-trip-needs-it.
- **Phase 4, the season walk**: running on the other machine as of 2026-09-21. Must accumulate across months ([[reference_recgov_calendar_limits]]).
- **Phase 7**: the "inherited, never verified" UI surfacing, which is what makes the other 55% tractable without hand-verifying 12,832 entries.

## 2. Federal gap — the only body measured AND tooled

152 of 178 `likely_rv` left (CA 36, OR 23, UT 16, OK 14), roughly one state per working chunk. Plus **182 `no_catalog`** rows (FS 113, BLM 63) that are nominally federal but behave like body 3: no per-site data means no size gate, no inclusion evidence and no pad plotting, so all three shortcuts that made AR and CO fast are absent. `python3 audit/ridb_gap_triage.py --status` says what is left with no cache and no network. Method: [[reference_ridb_gap_pipeline]].

## 3. Non-RV-Life gap — four faces, only federal measured

- **state** — 2,202 entries, ~48 agencies. One data point: SD, 5 missed of 59 (~8%). No list, no tool.
- **local** — 2,511 entries, the face AWH's framing omitted, and *worse* than state: detection is a name-scan of RV Life's own buckets, so it inherits RV Life's omissions twice over ([[reference_local_campground_method]]).
- **Canada** — 700 provincial, and there is no RIDB equivalent at all.
- **private** — 3,574, and probably fine: RV Life is natively a private-park directory and Good Sam independently cross-checked it ([[reference_good_sam_ratings]]).

**Possible mechanical check for state and local:** the Good Sam directory (14,993 parks) covers public campgrounds too, not only Good Sam Parks. Whether it is *comprehensive* for state parks is unknown — measure before trusting it.

## The coupling

They are not independent: **every gap add lands with zero schema fields**, so body 2 manufactures body 1. Close it per state as you go — `recgov_hookups.py` for the federal ones (the catalog answers it), then the note scan.

## Recommended order

Before committing to body 3, spend one session **measuring** it — walk two or three agency park lists and diff. SD's 8% is a single data point and the answer changes the priority a lot: 8% of 2,202 is ~175 campgrounds, 20% is ~440 and outranks everything else here.
