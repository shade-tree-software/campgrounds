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

Batches applied: (none yet)
