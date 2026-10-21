---
name: project-phase7-verification
description: Schema phase 7 started 2026-10-20 - verify every campground against its own pages; order = stayed-at (67 with inherited first), popups, then all by most-visited state; credits expire ~2026-11-20 so go big
metadata:
  type: project
---

AWH 2026-10-20: start phase 7 of [[project-campground-schema]] now. Use signals = stays AND
contributor popup opens (logged since 67b777e6 to trip_data/campground_views.jsonl; live only once
PA is deployed). Begin with the 67 stayed-at campgrounds carrying inherited values, then the other
stayed-at ones, then SYSTEMATICALLY every campground, states most heavily visited first (PA, VA,
MD, FL, WV, SC, NY, NC, MI, CO ...). **Why:** AWH has a lot of credits that expire within a month
(~2026-11-20), so large-scale work is wanted now.

**How to apply:** tooling in audit/verify/ (queue.py ranks + writes batches, README.md is the
per-entry procedure, apply.py validates and writes results/<id>.json, then moves them to
results/applied/). Entry-level `verify_scan` record (campground_schema.VERIFY_SCAN) takes an entry
off the queue even when nothing changed. Verifier writes `method: manual` for the operator/agency
page. Criteria problems are flags for me to decide (I may drop per the standing rules and report).

**Progress / resume (2026-10-21, evening):** ~382 verified (batches p2-1..p3-17 applied, last
commit d95de1e3). Batch `batches/p3-18.json` (12 VA) has a verifier RUNNING; if the session died,
check results/ for its files, else relaunch (prompt saved in the session scratchpad as
p318_prompt.txt; otherwise copy the latest Agent prompt from the transcript). AWH (10-20) cut back
to ONE verifier at a time (session limit). Loop per batch: review flags → fix result files (e.g.
never clear a phase-5 good_sam false on private) → `apply.py --apply <ids>` → small python for
phones/websites/names from flags (check URL 200 first; prepend agency page to website) → presence
drops go in audit/verify/criteria_drops.py (DROPS dict, logs removals.json) → log to
waterfront_leads.md / criteria_followups.md / asks.md → commit → `queue.py --batch p3-N --limit 12`
→ launch verifier with the standard prompt (copy the latest Agent prompt from the transcript:
README first, economical, privacy line, rules list; tell it `flock -o` for a background driver).
Over-gate private flags: check `audit/price_research/gateways.py lat,lng` before dropping.
Open: waterfront leads 806 Loraine (pin wrong, needs DCR map) and 1140 Glen Maury (riverside RV
areas); asks.md #6 Bear Creek Lake A18; criteria_followups 14312 James Creek, 525 Grindstone,
940 Tall Pines. Separate from phase 7: the below-the-dam screen ([[feedback_below_dam_not_lake]],
audit/dam_screen/tiers.md, 75 flagged) is waiting on AWH's decision about hand checks.
