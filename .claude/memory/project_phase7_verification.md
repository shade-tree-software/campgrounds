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

**Progress / resume (2026-10-21, late):** ~445 verified (batches through p3-24 applied, last
commit c6366573; nothing pushed since ccbb5ed3). Batch `batches/p3-25.json` (last 3 VA + first 9
MD) and p3-26 (12 MD) each have a verifier RUNNING; prompts in the session scratchpad as
p325_prompt.txt / p326_prompt.txt (MD source notes inside). Pushed+deployed 397aa283. If the session died, check results/ for its files, else relaunch. Dropped on the
4WD rule 10-21: Long Run Road #1-3 + 521, Flagpole 404/405/406 (#4-6 and 55/402/403 kept on AWH 2WD reports). AWH (10-21 late) allows TWO verifiers in the background at once (was one since 10-20). Loop per batch: review flags → fix result files (e.g.
never clear a phase-5 good_sam false on private) → `apply.py --apply <ids>` → small python for
phones/websites/names from flags (check URL 200 first; prepend agency page to website) → presence
drops go in audit/verify/criteria_drops.py (DROPS dict, logs removals.json) → log to
waterfront_leads.md / criteria_followups.md / asks.md → commit → `queue.py --batch p3-N --limit 12`
→ launch verifier with the standard prompt (copy the latest Agent prompt from the transcript:
README first, economical, privacy line, rules list; tell it `flock -o` for a background driver).
Over-gate private flags: check `audit/price_research/gateways.py lat,lng` before dropping.
Open: asks.md #8 (DWR 300-ft rule vs WMA lot entries 123/124/254/236/482), #9 (Flagpole Knob
road vs 4WD rule), #10 (four dam-screen downgrades, audit/dam_screen/decisions_pending.json,
apply with audit/apply_waterfront_audit.py once approved), #11 (McNally 3494). Dam screen: 69 of
75 flags confirmed and committed (d70ff04f); 3900 Bond Falls / 3532 Totogatic need re-pinning
(waterfront_leads.md). Canada lakes not screened. rec.gov `soft` minimums are now RULES
(AWH 10-21, see [[feedback_minimum_stay]]).
