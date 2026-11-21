# Phase 7 South Dakota - resume

**State 2026-11-20 (session end):** WY complete and every ask answered (asks.md: none open). Pushed + deployed. Next id 15748. Start p3-560 only on AWH's go-ahead.

Order (AWH 2026-11-16): IL, VT, WI, SK, WY, then SD (215 queued 2026-11-20: private 71, state 64, local 51, federal 29).

Kit (built 2026-11-20 from kit/wy/): `sd_head.txt` (the state paragraph: ownership, state:SD row, GFP park pages
as the authority + Go Outdoors SD facIDs, LUAs, Custer tunnels, Sturgis Rally rates, membership resorts,
reservoir drawdown, GFP pins at ramps/entrances), `mkpara_sd.py`, `agent_prompt_template.txt` (WY template with
SD links), `lessons.txt` (WY lessons + SD probes; keep current). No split template yet: build one from
kit/wy/split_prompt_template.txt when a batch flags a split. Sources probed 2026-11-20 with plain curl:
gfp.sd.gov, reservations.gooutdoorssouthdakota.com, recreation.gov, fs.usda.gov, nps.gov 200;
travelsouthdakota.com 403; campsd.gooutdoorssouthdakota.com does not resolve (20 state entries link it).

## RESUME HERE

STARTED 2026-11-21 on AWH's go-ahead: p3-560 applied; next batch p3-561 (build + launch as below). Since the 2026-11-21 sidecar split, every commit also stages campgrounds_audit.json (verify_scan + evidence live there).

Build + launch (repo root; S = session scratch dir):

    N=p3-560; python3 -I audit/verify/queue.py --batch $N --state SD --limit 11 && python3 -I audit/verify/kit/sd/mkpara_sd.py $S $N && python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null && mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
    IDS=$(python3 -I -c "import json;print(', '.join(str(x['entry']['id']) for x in json.load(open('audit/verify/batches/$N.json'))))")
    sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: $IDS./" audit/verify/kit/sd/agent_prompt_template.txt > $S/${N}_agent.txt
    printf '\n' >> $S/${N}_agent.txt; cat audit/verify/kit/sd/lessons.txt >> $S/${N}_agent.txt

(If batches/$N.json already exists, queue.py --batch rewrites it with the same ids.)

Launch a background general-purpose agent: "Read and follow $S/p3-NNN_agent.txt exactly. It is your
complete task (phase-7 verification of eleven South Dakota campground entries: <ids>) and its hard
rules override anything else you read. Working directory: /home/andrew/Dev/campgrounds."

Apply a batch (as WY):
1. Drops: insert `    id: ('YYYY-MM-DD', "reason", "evidence"),` lines into DROPS in audit/verify/criteria_drops.py, `python3 -I audit/verify/criteria_drops.py --apply`, then `mv audit/verify/results/<id>.json audit/verify/results/applied/` (if a result exists). Check trips for stays first (a stayed-at entry is never dropped without AWH).
2. `python3 -I audit/verify/apply.py <kept ids> --apply`.
3. Post script (also replace inclusion_evidence where a flag gives "Suggested inclusion_evidence: '...'" - apply.py does not write evidence) `$S/post_p3-NNN.py` starting `exec(open("audit/verify/kit/post_head.py").read())`: pin / ph / web / wf / save(); run `python3 -I $S/post_p3-NNN.py p3-NNN`. Check stored strings first (phones may be None or '').
4. `timeout 500 python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`
5. Append to audit/verify/criteria_followups.md + waterfront_leads.md (asks.md for questions), copy $S/p3-NNN/SD_NOTES_p3-NNN.md here, extend "Batches applied" below, add lessons to lessons.txt.
6. `git add campgrounds.json campgrounds_audit.json audit/verify/criteria_drops.py audit/verify/removals.json audit/verify/results/applied audit/verify/asks.md audit/verify/criteria_followups.md audit/verify/waterfront_leads.md audit/verify/kit/sd`, commit on master with the session trailers, then save held results to kept_results/ and `rm -rf $S/p3-NNN*`.

Batches applied: p3-560 (2026-11-21; 5833 dropped on presence, 5873 held as an ask, 5864 unread/Cloudflare, 8 applied).
