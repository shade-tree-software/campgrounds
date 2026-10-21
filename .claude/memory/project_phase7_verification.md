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

**Progress / resume (2026-10-21, night):** ~490 verified (batches through p3-27 applied, pushed
+ deployed 0aa14416). Running: p3-28 (last 9 MD) and p3-29 (first 12 FL); prompts in the session
scratchpad as p328_prompt.txt / p329_prompt.txt (FL source notes in p329). If the session died,
check results/ for their files, else relaunch. LESSON: AWH edits notes on PA's manage page; when
local commits also touched campgrounds.json, capture-pa-edits.sh refuses - instead commit PA's
file exactly on top of the deployed commit (worktree), push that alone, run the deploy key's
`reconcile`, then merge it into local master (done 10-21, d93ec353). Also: `git add -A
audit/verify` stages a RUNNING verifier's results files; add applied/ + `-u` instead. AWH (10-21 late) allows TWO verifiers in the background at once (was one since 10-20). Loop per batch: review flags → fix result files (e.g.
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

**2026-10-21 late: FL under way (p3-29..p3-40 applied, p3-41 + p3-42 running). HURRICANE ISAIAS is a live Oct 2026 storm** (2026 reuses the 2020 name list; Escambia evacuations 10-21). 197 Topsail Hill and 4720 Coldwater were set temporarily_closed 2026-10-21. Re-check them and lift the statuses once the parks reopen. Panhandle entries verified before 10-21 may also be closed but aren't marked. Followups live in audit/verify/criteria_followups.md. Open asks in audit/verify/asks.md: 4774 Kelly's RV Park, 556 Periwinkle, 4814 Williams Landing.

**2026-10-21 late:** FLORIDA DONE. All 236 FL entries are verified (p3-28..p3-51). Deployed through 0a6df649; 546969a0 (p3-51) is local only. WV started: p3-52 and p3-53 are running.
- **New AWH rules:** the peak-season minimum rule (≤3 months, see [[feedback-minimum-stay]]); the Fort Myers exception is price-only (Gulf Waters 26-ft rule, Sanctuary, Orange Grove and Swan Lake were dropped); Big Scrub kept (OHV side).
- **FL items to re-check:** 4855 Easterlin (after 11-01), 197 Topsail and 4720 Coldwater (Isaias), 163 Highlands Hammock (renovation), NWFWMD 13375/13376/13377 (storm banners), 4821 Hutch Gibson.
- **Open ask:** 4822 Neals Landing.

**PAUSED by AWH 2026-10-21 night ("stop the stage 7 work for now").** Last applied batch: p3-52 (fa764ae1). The p3-53 and p3-54 verifiers were stopped mid-run, with their results unapplied in audit/verify/results/:
- p3-53 wrote 11 of 12; 427 Five River is missing, and 630 Coopers Rock may be partial.
- p3-54 wrote only 547.
- To resume: re-check those files, run p3-53/p3-54 for the missing ids, then apply.
- Open ask: 809 Sullivan's Camp Cacapon.
- Deployed through 0a6df649; later commits are local.
