# Phase 7 — Illinois (RESUME)

Started 2026-11-12 after ND (kit/nd/RESUME_ND.md). Queue at start: 203 (state 82, local 52, private 42, federal 27).
Batches applied: p3-463 (2026-11-12; 1747 dropped, 1700 split -> 15700), p3-464 (14618 dropped), p3-465 (1799 dropped), p3-466 (1728 dropped), p3-467, p3-468 (1638 split -> 15701 Chippewa), p3-469 (2026-11-13), p3-470 (1755 dropped), p3-471 (1735 dropped), p3-472 (2026-11-13), p3-473 (2026-11-15; 1737 dropped; 1757, 1790, 1763 unread), p3-474 (2026-11-15), p3-475 (2026-11-15), p3-476 (2026-11-15; 1712 dropped; 1709, 1784 unread), p3-477 (2026-11-15; 13412, 1798 unread; 1800 asked), p3-478 (2026-11-15), p3-479 (2026-11-15; 1715 dropped; 14007 split held), p3-480 (2026-11-16; 14612, 13407, 13408 unread), p3-481 (2026-11-16; last 7). AWH rulings after p3-472: 15428 KOA kept (Chicago exception), 1687 year-round with the Coyote Cove caveat. Unread (still queued): 1775 Middle Fork (Cloudflare), 1781 Fairview Park (Akamai), 1769 Illiniwek (Cloudflare), 1773 Loud Thunder (Cloudflare). ExploreMoreIL per-unit points: tools/il_pts.py + ov.py.
Next new id **15702**.
**Paused 2026-11-15 after p3-479, resumed 2026-11-16 with p3-480.** After IL: VT, then WI, SK, WY, SD (AWH 2026-11-16). 18 IL left in the queue: about 7 never read plus 11 unread behind bot walls (1775 Middle Fork, 1781 Fairview Park, 1769 Illiniwek, 1773 Loud Thunder, 1757 Mt. CarMerriel, 1790 Pittsfield City Lake, 1763 Sandy Oaks, 1709 Bear Creek, 1784 Burrell Park, 13412 Citizens Lake, 1798 Great River Road) - phone-list candidates once the rest is done. Asks 1800 (kept) and 14615 (downgraded) resolved 2026-11-15/16. Held splits: 1679 Illini Whitetail, 14007 Horseshoe Lake (Alexander). Next batch p3-480; next new id still 15702. Add the 'From the last batches' paragraph (see p3-479 notes) to the agent prompt.
 ONE verifier at a time (AWH 2026-11-11).

## Build a batch (11 ids; the agent template says ELEVEN)
```
S=<session scratchpad>; N=p3-NNN
python3 -I audit/verify/queue.py --batch $N --state IL --limit 11 && python3 -I audit/verify/kit/il/mkpara_il.py $S $N && python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null && mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
IDS=$(python3 -I -c "import json;print(', '.join(str(x['entry']['id']) for x in json.load(open('audit/verify/batches/$N.json'))))")
sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: $IDS./" audit/verify/kit/il/agent_prompt_template.txt > $S/${N}_agent.txt
```
Brief = kit/brief_mo.txt + the IL paragraph (kit/il/il_head.txt + per-entry lines). The agent
prompt's hard rules override the long brief.

## Apply (same as ND/MN)
1. Drops -> DROPS in audit/verify/criteria_drops.py, inserted after the latest dated line, format
   `    <id>: ('<date>', '<reason>', "<evidence>"),`; run `python3 -I audit/verify/criteria_drops.py --apply`,
   then `mv audit/verify/results/<id>.json audit/verify/results/applied/`.
2. `python3 -I audit/verify/apply.py <remaining ids> --apply`.
3. Post script for pins, phones, websites, waterfront (apply.py writes none of those):
   `$S/post_p3-NNN.py` starting `exec(open("audit/verify/kit/post_head.py").read())`, then calls like
   `pin(id,'<old lat,lng>',lat,lng)`, `ph(id,<old or None>,'new')`, `web(id,'<old>','<new or None>')`,
   `wf(id,'<old>','<new>',"downgraded ... --Claude")`, `save()`; run from the repo root as
   `python3 -I $S/post_p3-NNN.py p3-NNN`. Never wf() an --AWH value (it asserts) - ask in asks.md instead.
4. `timeout 500 python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`
5. Append criteria_followups.md + waterfront_leads.md (+ asks.md); copy IL_NOTES_p3-N.md here; update
   the "Batches applied" line above.
6. Commit with explicit paths (campgrounds.json, criteria_drops.py, removals.json, results/applied,
   the three .md files, kit/il).
Leads -> audit/verify/leads/il_leads.txt, vetted one at a time after the queue
(copy leads/nd_lead_prompt_template.txt to an IL version; add with leads/add_results.py).

**After each commit (disk space):** copy any held result JSON still in `$S/p3-NNN/` to
`audit/verify/kept_results/` (in git since 2026-11-15; it was scratch-only before), then
`rm -rf $S/p3-NNN $S/p3-NNN_agent.txt $S/p3-NNN_prompt.txt $S/post_p3-NNN.py $S/p3-NNN_para.txt`.

## After Illinois
The 33 Vermont entries (kit/vt).

**IL QUEUE DONE 2026-11-16 (p3-481).** Left: 14 unread behind bot walls (their batch files keep them out of the queue): 1775, 1781, 1769, 1773, 1757, 1790, 1763, 1709, 1784, 13412, 1798, 14612, 13407, 13408 - phone-list / another-route candidates. Next: VT (kit/vt/RESUME_VT.md).
