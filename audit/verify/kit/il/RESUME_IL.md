# Phase 7 — Illinois (RESUME)

Started 2026-11-12 after ND (kit/nd/RESUME_ND.md). Queue at start: 203 (state 82, local 52, private 42, federal 27).
Batches applied: p3-463 (2026-11-12; 1747 dropped, 1700 split -> 15700), p3-464 (14618 dropped), p3-465 (1799 dropped), p3-466 (1728 dropped), p3-467. Unread (still queued): 1775 Middle Fork (Cloudflare), 1781 Fairview Park (Akamai), 1769 Illiniwek (Cloudflare).
Next new id **15701**. ONE verifier at a time (AWH 2026-11-11).

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
Drops -> DROPS in audit/verify/criteria_drops.py, `--apply`; then `apply.py <ids> --apply`; then a
post script for pins/phones/websites/waterfront (apply.py writes none of those); tests; copy
IL_NOTES_p3-N.md here; append criteria_followups.md + waterfront_leads.md (+ asks.md); commit with
explicit paths. Leads -> audit/verify/leads/il_leads.txt, vetted one at a time after the queue
(copy leads/nd_lead_prompt_template.txt to an IL version; add with leads/add_results.py).

**After each commit (disk space):** copy any result JSON still in `$S/p3-NNN/` to `$S/kept_results/`,
then `rm -rf $S/p3-NNN $S/p3-NNN_agent.txt $S/p3-NNN_prompt.txt $S/post_p3-NNN.py`.

## After Illinois
The 33 Vermont entries (kit/vt).
