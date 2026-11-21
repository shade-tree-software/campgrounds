# Phase 7 unread retry - resume

AWH 2026-11-20: the entries earlier batches left UNREAD behind bot walls may be retried with a headless browser,
dated Wayback captures and strong secondary sources (rule text: retry_rule.txt; memory feedback_unread_retry_routes).
Scoped to these entries only. One agent at a time; SD waits until this is done or AWH says otherwise.

Plan (state kit's brief + template, rule 13 swapped): u-01 MN (9), u-02/03 IL (7+7), u-04..06 WI (9+9+8),
u-07..09 ND (11+10+10), then VT 4097 + AB 9047.

    S=<scratch>; audit/verify/kit/unread/build.sh $S u-NN ST id,id,...

Launch: "Read and follow $S/u-NN_agent.txt exactly. It is your complete task (phase-7 retry of N <state>
entries left unread behind bot walls: <ids>) and its hard rules override anything else you read.
Working directory: /home/andrew/Dev/campgrounds."
Apply as any phase-7 batch (kit/<st>/RESUME_<ST>.md steps), then save held results to kept_results/ and rm $S/u-NN*.

Batches applied: u-01 MN (2026-11-20; all 9 read, no drops; 5518 rate still unread), u-02 IL (2026-11-20; 5 applied, 1763 held (ask), 1709 unread), u-03 IL (2026-11-20; headless + Wayback refused by the permission system; 1784 + 13407 applied, 5 still unread), u-04 IL (2026-11-20; all 6 read: 1798 dropped, 13412 ask; IL DONE), u-05 WI (2026-11-20; 9 read, 3369 dropped ATV base), u-06 WI (2026-11-20; 9 read, 3524 dropped, 3494 re-scoped; 3535 split + English Pale lead pending)

**(Resumed 2026-11-20: AWH added the allow rules to .claude/settings.local.json; u-04 = the IL leftovers.)** Was paused after u-03: the Claude Code permission system (not the sites) refused headless-browser runs and web.archive.org fetches in u-02/u-03 (u-01 had both working). Resume only once AWH has allowed them; then re-run the IL leftovers (1709 1790 1798 13408 13412 14612; 1763 held as an ask) and continue with WI u-04.
