# Phase 7 Saskatchewan - resume

Order (AWH 2026-11-16): IL, VT, WI, then SK (169 queued), WY, SD.

Kit (built 2026-11-17 from kit/wi/ + the Alberta round, kit/ab/): `sk_head.txt` (the province
paragraph: Canada/CAD/C$69 rules, Regional Park = local, Sask Parks provincial:SK row, Parks Canada,
Let's Camp API, reservoir drawdown), `mkpara_sk.py`, `agent_prompt_template.txt`, `lessons.txt`
(keep current: add each batch's refusing domains). Sources probed 2026-11-17: parks.saskatchewan.ca
campgroundDetails.do pages answer curl with a cookie jar + -L (Queue-it safetynet passes);
saskparks.tourismsaskatchewan.com, saskregionalparks.ca, letscamp.ca API, parks.canada.ca answer;
reservation.pc.gc.ca 403s.

## RESUME HERE (p3-520 APPLIED 2026-11-18; next p3-521)

Next batch: **p3-527** (not built). 92 SK left after p3-526; SK splits + leads pending in criteria_followups.md (do after the queue). ONE verifier at a time, 11 per batch.
Add the previous batch's findings to lessons.txt before building (p3-520: SKPP detail pages slow to
~30 s each - read the paging table first and fetch details only for key sites; stored phones mostly
empty - the tourism parks.csv 'Phone Number Primary' has the park office).

Build + launch (repo root; S = session scratch dir):

    N=p3-527; python3 -I audit/verify/queue.py --batch $N --state SK --limit 11 && python3 -I audit/verify/kit/sk/mkpara_sk.py $S $N && python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null && mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
    IDS=$(python3 -I -c "import json;print(', '.join(str(x['entry']['id']) for x in json.load(open('audit/verify/batches/$N.json'))))")
    sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: $IDS./" audit/verify/kit/sk/agent_prompt_template.txt > $S/${N}_agent.txt
    printf '\n' >> $S/${N}_agent.txt; cat audit/verify/kit/sk/lessons.txt >> $S/${N}_agent.txt

(If batches/$N.json already exists, queue.py --batch rewrites it with the same ids.)

Launch a background general-purpose agent: "Read and follow $S/p3-NNN_agent.txt exactly. It is your
complete task (phase-7 verification of eleven Saskatchewan campground entries: <ids>) and its hard
rules override anything else you read. Working directory: /home/andrew/Dev/campgrounds."

Apply a batch (as WI):
1. Drops: insert `    id: ('YYYY-MM-DD', "reason", "evidence"),` lines into DROPS in audit/verify/criteria_drops.py, `python3 -I audit/verify/criteria_drops.py --apply`, then `mv audit/verify/results/<id>.json audit/verify/results/applied/` (if a result exists).
2. `python3 -I audit/verify/apply.py <kept ids> --apply`.
3. Post script `$S/post_p3-NNN.py` starting `exec(open("audit/verify/kit/post_head.py").read())`: pin / ph / web / wf / save(); run `python3 -I $S/post_p3-NNN.py p3-NNN`. Check stored strings first (phones may be None or '').
4. `timeout 500 python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`
5. Append to audit/verify/criteria_followups.md + waterfront_leads.md (asks.md for questions), copy $S/p3-NNN/SK_NOTES_p3-NNN.md here, extend "Batches applied" below.
6. `git add campgrounds.json audit/verify/criteria_drops.py audit/verify/removals.json audit/verify/results/applied audit/verify/asks.md audit/verify/criteria_followups.md audit/verify/waterfront_leads.md audit/verify/kit/sk`, commit on master with the session trailers, then save held results to kept_results/ and `rm -rf $S/p3-NNN*`.

Batches applied: p3-520 (2026-11-18; 9296 dropped; 9166 re-pinned 5.8 km), p3-521 (2026-11-18; no drops; Battlefords South split pending), p3-522 (2026-11-18; no drops; Blackstrap Hazelnut Grove split pending), p3-523 (2026-11-18; no drops; Palliser to lakeview, Palliser split + two leads pending, 9308 ownership ask), p3-524 (2026-11-18; 9293 dropped on Google 3.8; Duck Mountain re-pinned 2.7 km + lakeview; Buffalo Pound split pending), p3-525 (2026-11-18; 12818 dropped on Google 3.7; three lakefront downgrades; Makwa Mewasin split pending), p3-526 (2026-11-18; 9311 dropped (suites only); Thomson Lake to lakefront; Sask Landing re-pinned 1.9 km, split pending)

Things to watch in SK (from the sweep handoff, project_sk_sweep_handoff):
- Whole-park provincial entries (Crooked Lake, Douglas, Echo Valley, Good Spirit Lake...) may hold several campgrounds: split only campgrounds at separate places (~1 km+, own entrance) when a batch runs into one (feedback_split_multi_campground_parks).
- The sweep's waterfront audit upgraded 43 entries from a placeholder: expect downgrades.
- RV Life tagged ~35 regional parks provincial; the sweep reclassified them to local - check any that slipped.
