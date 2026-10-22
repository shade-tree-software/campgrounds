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

**RESUMED 2026-10-21 (new session d7b90449):** WV DONE (p3-62..p3-65); SC DONE (p3-65..p3-72); NY DONE (p3-72..p3-88); NC from p3-88. Applied through p3-88 (31978711), NOT pushed. p3-89 + p3-90 (NC) running; briefs in that session's scratchpad as p3-NN_prompt.txt, each built from the previous by swapping the batch paragraph + the other-verifier line (check that line's scratch path). Helpers: p3-86 scratch has the NY set; p3-88 adds rgsum.py (rec.gov rates) and cat.py (RIDB catalog); WebFetch reads dec.ny.gov; developer.nps.gov/api/v1 with DEMO_KEY for NPS campgrounds/alerts. Suffolk County parks: county rules give non-residents walk-ups, so the $50-key 4-night minimum is NOT a drop by itself (Indian Island 1448 restored); Smith Point 1446 dropped because its own page says reservations required for all sites. Drops this session are in removals.json (presence, price gate, residents-only, 15-ft sites, test 4). Open asks: 1454 McCann (mostly seasonal), 1473 Cayuga Wine Trail / 1518 Rancho Pines (Campspot Van vs Motorhome). If the session died, check results/ for their files, else relaunch. Commit with explicit paths (applied/ + `-u`), never `git add audit/verify/`. Never `pkill -f` a pattern matching your own command (killed the shell).

**PAUSED AGAIN by AWH 2026-10-21, very late ("pause when convenient").** Nothing is in flight: p3-55..p3-61 are applied (84 WV entries). Commits after c8f95e89 are NOT pushed; deployed through f37f3ac7. Verified 838.
- Dropped: Gheny Nook 13121 (long-stay test 2), The Dock 1221 (presence), Sunny Glen 1220 and Triple L 1223 (AWH).
- AWH answers: 869 narrowed to Cokeley Campground; 509 Beckys Creek -> wma; Dolly Sods 515/516/499 KEPT (AWH has driven past: unpaved driveways to clearings off the road, outside the 300-ft FR 19/75 ban).
- **Later AWH answers (same night):** 815 Harpers Ferry kept, since EKKO is under 10.5 ft and the tunnel is 11 ft ([[user-ekko-height]]); 1220 Sunny Glen and 1223 Triple L DROPPED (no posted nightly rate, workforce-leaning). No asks are open.
- AWH: "we'll continue with phase 7 in a new session."
- **To resume:** `queue.py --batch p3-62 --limit 12` and `--batch p3-63 --offset 12` (WV continues). Write each brief from **audit/verify/prompt_template_wv.txt** (p3-61's; swap the batch paragraph, update the scratch/helper paths to the new session's scratchpad) and launch the verifier with "read your brief from <file>". The old session's helpers are in **audit/verify/helpers_wv/** (README inside), since scratch dirs don't outlive a session; tell verifiers to copy helpers from there.
- The 22 re-screen adds (15531-15552) carry verify_scan, so the queue skips them.
- Registry lead: WV one-night Fridays sell inside ~24 days of arrival.

**(Earlier) PAUSED by AWH 2026-10-21 night ("stop the stage 7 work for now").** p3-53 and p3-54 were finished and applied afterwards at AWH's request (c41c6325, 4fdabc4b), so nothing is in flight. The WV dropped entries are 1200 Big Earl's and 1204 Camp Morning Wood (presence rule). 809 Sullivan's was dropped by AWH (0b38912e).
- To resume: `queue.py --batch p3-55 --limit 12` (WV continues), and derive the prompt from scratchpad p3-53/p3-54's.
- Deployed through 0a6df649; later commits are local.

**RESUMED 2026-10-22 (session f407aa47):** p3-90 + first five of p3-91 applied (e311c27a, 7f488d89; not pushed). Running: rest of p3-91 (7 NC) and p3-92 (12 WV entries an earlier `--offset` skipped - WV was NOT fully done). Briefs + copied helpers in that session's scratchpad (p3-9N_prompt.txt, helpers/). Old-session scratch d7b90449 still had p3-91_prompt.txt as the template. queue.py excludes ids sitting in pending batch files, so a stale batch hides entries; derive the next batch only after applying. CORRECTION: p3-89 dropped 4241 Country Woods / 4253 Ho-Hum on long-stay test 2 alone; restored (not long-stay parks; Google 25+ w/ phone + RV Life $/$$ pass) - README step 6 now says test 2 is only for long-stay parks. NC continues after p3-91 (~123 left, then MI).

**2026-10-22 later (session f407aa47):** applied through p3-100 (+ p3-91 rest, p3-92 WV gap, p3-93..p3-100), all committed on master, NOT pushed. Running at last save: p3-101 and p3-102 (NC). NC has ~36 left after p3-102, then MI. New: `audit/verify/leads/` = add pipeline for campgrounds found mid-pass (instructions.md + add_results.py, price gate in force; mark adds with a `verify_scan` so the queue skips them). Added Gibson Cove 15553 + Nantahala RV Resort 15554; next id 15555. Open asks in audit/verify/asks.md (497 Mower Tract pin, 258 Falls Lake split, 146 Jordan Lake split, 4256 Pride membership, 4298 Bannister felony question, 4314 Whippoorwill horse camp?). Hatteras re-checks: 15456 KOA, 380 Frisco, 4288 Sands of Time (all temporarily_closed on the Dare County evacuation). Brief template: last p3-NN_prompt.txt in the session scratchpad; per-entry text sits between "All twelve are NORTH CAROLINA entries." and "Lessons from the last batches".

**2026-10-22 evening:** AWH: ONE verifier at a time now ([[feedback_one_verifier]]). p3-109 was stopped before writing anything; its batch file stays and is relaunched after p3-108 is applied. Applied through p3-107; 3984 dropped on AWH's answer.

**2026-10-22 evening (session f407aa47):** applied through p3-108 (MI under way, ~500 left), plus AWH answers: 3984 dropped, 3852 Hillside kept (Google reviews show one-night stays). PUSHED and deployed through this commit at AWH's request. p3-109 (MI, 4036..14210) was running alone at the push; ONE verifier at a time. Next brief: build from p3-109_prompt.txt in session f407aa47's scratchpad (anchor "All twelve are MICHIGAN entries").

**STOPPED 2026-10-22 late (AWH: "stop after p3-113"), session f407aa47.** Applied through p3-113 (last commit 2bde5a48), nothing in flight, no pending batch files. Pushed + deployed only through c3e906f1 (p3-108); p3-109..p3-113 are local. A cloud session is doing MT ([[project-phase7-mt]]): fetch + merge origin/master before pushing. Drops since the push: 4037 Country Village (gate), 3819 Hemlock Lake + 3848 Martiny Lakes (test 4), 3826 Gilmore (AWH, per-night museum admission). Re-pin on imagery: 188 Ludington, 796 McLain (criteria_followups.md). To resume: `queue.py --batch p3-114 --limit 12`, brief from p3-113_prompt.txt in session f407aa47's scratchpad (replace the text from "State (all AWH-noted" to "For each record 2026 rates") - if that scratchpad is gone, rebuild from the rules in the README and an applied result.
