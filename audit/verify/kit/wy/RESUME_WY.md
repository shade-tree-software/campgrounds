# Phase 7 Wyoming - resume

Order (AWH 2026-11-16): IL, VT, WI, SK, then WY (244 queued 2026-11-20: federal 168, local 32, private 26, state 18), SD.
AWH 2026-11-20: SK pushed + deployed; "You can start Wyoming now."

Kit (built 2026-11-20 from kit/wi/ + kit/sk/ + the Montana round's lessons): `wy_head.txt` (the state
paragraph: ownership, state:WY row, rec.gov/RIDB, NPS concessions, access/4WD rule, local no-web-presence
ladder, energy-town workforce parks, gateways, waterfront/reservoir drawdown), `mkpara_wy.py`,
`agent_prompt_template.txt` (WI template + the wait-on-PID and permission-denial lines), `lessons.txt`
(keep current: add each batch's refusing domains and lessons). Sources probed 2026-11-20 with plain curl:
wyoparks.wyo.gov, reserve.wyoming.gov, nps.gov, fs.usda.gov, recreation.gov search API,
yellowstonenationalparklodges.com all 200.

## RESUME HERE

Next batch: p3-536 (first WY batch). ONE verifier at a time, 11 per batch.

Build + launch (repo root; S = session scratch dir):

    N=p3-536; python3 -I audit/verify/queue.py --batch $N --state WY --limit 11 && python3 -I audit/verify/kit/wy/mkpara_wy.py $S $N && python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null && mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
    IDS=$(python3 -I -c "import json;print(', '.join(str(x['entry']['id']) for x in json.load(open('audit/verify/batches/$N.json'))))")
    sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: $IDS./" audit/verify/kit/wy/agent_prompt_template.txt > $S/${N}_agent.txt
    printf '\n' >> $S/${N}_agent.txt; cat audit/verify/kit/wy/lessons.txt >> $S/${N}_agent.txt

(If batches/$N.json already exists, queue.py --batch rewrites it with the same ids.)

Launch a background general-purpose agent: "Read and follow $S/p3-NNN_agent.txt exactly. It is your
complete task (phase-7 verification of eleven Wyoming campground entries: <ids>) and its hard
rules override anything else you read. Working directory: /home/andrew/Dev/campgrounds."

Apply a batch (as WI/SK):
1. Drops: insert `    id: ('YYYY-MM-DD', "reason", "evidence"),` lines into DROPS in audit/verify/criteria_drops.py, `python3 -I audit/verify/criteria_drops.py --apply`, then `mv audit/verify/results/<id>.json audit/verify/results/applied/` (if a result exists). Check trips for stays first (a stayed-at entry is never dropped without AWH).
2. `python3 -I audit/verify/apply.py <kept ids> --apply`.
3. Post script `$S/post_p3-NNN.py` starting `exec(open("audit/verify/kit/post_head.py").read())`: pin / ph / web / wf / save(); run `python3 -I $S/post_p3-NNN.py p3-NNN`. Check stored strings first (phones may be None or '').
4. `timeout 500 python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`
5. Append to audit/verify/criteria_followups.md + waterfront_leads.md (asks.md for questions), copy $S/p3-NNN/WY_NOTES_p3-NNN.md here, extend "Batches applied" below, add lessons to lessons.txt.
6. `git add campgrounds.json audit/verify/criteria_drops.py audit/verify/removals.json audit/verify/results/applied audit/verify/asks.md audit/verify/criteria_followups.md audit/verify/waterfront_leads.md audit/verify/kit/wy`, commit on master with the session trailers, then save held results to kept_results/ and `rm -rf $S/p3-NNN*`.

Batches applied: (none yet)

Things to watch in WY (from the sweep handoff, project_wy_sweep_handoff):
- RV Life tagged BLM sites `dnr` and NPS/fairground sites `commercial`; the sweep reclassified them - check any that slipped.
- Whole-park state entries (Glendo, Boysen, Buffalo Bill, Keyhole, Curt Gowdy) may hold several campgrounds: split only campgrounds at separate places (~1 km+, own entrance) when a batch runs into one (feedback_split_multi_campground_parks).
- Yellowstone campground closures/construction change year to year (Norris, Pebble Creek, Tower Fall were closed at the sweep).
