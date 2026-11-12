# North Dakota phase 7 - resume notes

Applied through **p3-456** (2026-11-12). Unread/held for the sweep or phone: 5975 Fordville, 5980 Hazelton, 6001 Neameyer (result in scratch, rests on silence), 6013 Warsing Dam (maybe closed), 5986 Seeman Park, 5995 Buffalo Lodge Lake, 5994 Drake, 5982 Northwood, 5979 Strasburg, 5971 Willowood, 6010 Bisbee, 5992 Bowdon, 6015 Coldwater, 5964 Glen Ullin, 5998 Golva, 6009 Hendrickson, 5991 West Side Park. Asks open: 5961 Larimore long-stay, 6013 Warsing, 5880 Fort Lincoln riverfront upgrade. Next batch **p3-457**. Next new id **15674**. ND queue at start: 179 (local 120, federal 22, private 19, state 18). ONE verifier at a time (AWH 2026-11-11).

## Build a batch (11 ids; the agent template says ELEVEN)
```
S=<session scratchpad>; N=p3-NNN
python3 -I audit/verify/queue.py --batch $N --state ND --limit 11 && python3 -I audit/verify/kit/nd/mkpara_nd.py $S $N && python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null && mkdir -p $S/$N && cp -r audit/verify/kit/nd/tools $S/$N/tools
IDS=$(python3 -I -c "import json;print(', '.join(str(x['entry']['id']) for x in json.load(open('audit/verify/batches/$N.json'))))")
sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: $IDS./" audit/verify/kit/nd/agent_prompt_template.txt > $S/${N}_agent.txt
```
Brief = kit/brief_mo.txt + the ND paragraph (kit/nd/nd_head.txt + per-entry lines). The agent
prompt's hard rules override the long brief (notably: NO Wayback/archive route around a refusal;
an archive is allowed only for a site that is down/does not resolve).

## Apply (same as MN, see kit/mn/RESUME_MN.md steps)
Drops -> DROPS in audit/verify/criteria_drops.py, `--apply`; then `apply.py <ids> --apply`; then a
post script for pins/phones/websites/waterfront (apply.py writes none of those); tests; copy
ND_NOTES_p3-N.md here; append criteria_followups.md + waterfront_leads.md (+ asks.md); commit with
explicit paths. Leads -> audit/verify/leads/nd_leads.txt, vetted one at a time after the queue
(add_results.py does NOT write booking/hookups/sites/facilities - copy them with provenance).

## After North Dakota
ILLINOIS (203 queued; needs kit/il like this one), then the 33 Vermont entries (kit/vt).
