# North Dakota phase 7 - resume notes

Applied through **p3-462** (ND first read COMPLETE) (2026-11-12). Unread/held for the sweep or phone: 5975 Fordville, 5980 Hazelton, 6001 Neameyer (result in scratch, rests on silence), 5986 Seeman Park, 5995 Buffalo Lodge Lake, 5994 Drake, 5982 Northwood, 5979 Strasburg, 5971 Willowood, 6010 Bisbee, 5992 Bowdon, 6015 Coldwater, 5964 Glen Ullin, 5998 Golva, 6009 Hendrickson, 5991 West Side Park, 6005 Berthold, 6036 Munich, 6040 CAB Park, 6039 Columbus, 6042 Dickey, 6022 Glenfield, 6023 Goodrich, 6021 Hague, 6031 Elgin, 6032 Monango, 6037 New England, 13570 Page, 6048 Sarles, 5899 Sheep Creek Dam, 6053 Turtle Lake. Asks open: none (5961 Larimore dropped under test 4, 5930 RRV Fair kept as local, AWH 2026-11-12). (6013 Warsing dropped and 5880 Fort Lincoln set riverfront, AWH 2026-11-12.) Next: vet the 28 leads in audit/verify/leads/nd_leads.txt (one agent each from leads/nd_lead_prompt_template.txt; add with leads/add_results.py), then Illinois. The unread/phone list waits for AWH's go-ahead on calls. Next new id **15698** (leads added: 15674 Cross Ranch Governors Centennial Loop, 15675 Smishek Lake, 15676 Prairie Knights Marina, 15677 Chahinkapa Zoo Campground, 15678 Wilson Dam, 15679 Big Coulee Dam Campground, 15680 Eagles Campground - Beulah, 15681-15686 Lake Tschida areas, 15687 Drayton RV Park, 15688 Wilderness Drive Campground, 15689 Lake Brekken Campground, 15690 HaRVey Campground, 15691 Lone Tree Campground, 15692 Ball Park RV Park, 15693 Nelson Lake West, 15694 Nelson Lake East, 15695 Tioga Peaceful Valley, 15696 Whitestone Hill Campground, 15697 Baukol-Noonan Trout Pond; lead 5 Stump Lake skipped pending a call). Phone candidates: audit/verify/phone_list.md. ND queue at start: 179 (local 120, federal 22, private 19, state 18). ONE verifier at a time (AWH 2026-11-11).

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

**After each commit (AWH 2026-11-12, disk space):** copy any result JSON still in `$S/p3-NNN/` (drops, held) to `$S/kept_results/`, then `rm -rf $S/p3-NNN $S/p3-NNN_agent.txt $S/p3-NNN_prompt.txt $S/post_p3-NNN.py`. Keep only the newest `_para.txt` and `post_p3-446.py`.
