# Phase 7 New Hampshire - resume

Order (AWH 2026-11-23): after SD (complete), New Hampshire first, then the queue's own order (Kentucky next).
52 queued 2026-11-23: federal 20 (WMNF), state 18, private 13, local 1.

Kit (built 2026-11-23 from kit/sd/ + kit/vt/): `nh_head.txt` (state paragraph: ownership, state:NH row, nhstateparks.org
+ newhampshirestateparks.reserveamerica.com as the authority, WMNF rec.gov/FS pages, designated road-side camping areas,
seasonal-heavy private parks, canopy + leaf-off imagery, Hampton Beach coastal dunes, kayak test), `mkpara_nh.py`,
`agent_prompt_template.txt` (SD template with NH links + coastal values), `lessons.txt` (general lessons kept from
SD/WY + the 2026-11-23 bank/creekside ruling; keep current). Sources probed 2026-11-23 with plain curl: nhstateparks.org,
newhampshirestateparks.reserveamerica.com, fs.usda.gov, recreation.gov, keenenh.gov, cannonmt.com 200;
www.reserveamerica.com/explore 403. Split template: copy kit/sd/split_prompt_template.txt when one is flagged.

## RESUME HERE

STARTED 2026-11-23 on AWH's go-ahead. **NH PHASE 7 COMPLETE 2026-11-23**: queue p3-581..585, leads 1-2 done, Jericho ask resolved (4110 kept with ATV caveat, 14368 dropped). Next id 15765.

Build + launch (repo root; S = session scratch dir):

    N=p3-581; python3 -I audit/verify/queue.py --batch $N --state NH --limit 11 && python3 -I audit/verify/kit/nh/mkpara_nh.py $S $N && python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null && mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
    IDS=$(python3 -I -c "import json;print(', '.join(str(x['entry']['id']) for x in json.load(open('audit/verify/batches/$N.json'))))")
    sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: $IDS./" audit/verify/kit/nh/agent_prompt_template.txt > $S/${N}_agent.txt
    printf '\n' >> $S/${N}_agent.txt; cat audit/verify/kit/nh/lessons.txt >> $S/${N}_agent.txt

(If batches/$N.json already exists, queue.py --batch rewrites it with the same ids.)

Launch a background general-purpose agent: "Read and follow $S/p3-NNN_agent.txt exactly. It is your
complete task (phase-7 verification of eleven New Hampshire campground entries: <ids>) and its hard
rules override anything else you read. Working directory: /home/andrew/Dev/campgrounds."

Apply a batch (as WY):
1. Drops: insert `    id: ('YYYY-MM-DD', "reason", "evidence"),` lines into DROPS in audit/verify/criteria_drops.py, `python3 -I audit/verify/criteria_drops.py --apply`, then `mv audit/verify/results/<id>.json audit/verify/results/applied/` (if a result exists). Check trips for stays first (a stayed-at entry is never dropped without AWH).
2. `python3 -I audit/verify/apply.py <kept ids> --apply`.
3. Post script (also replace inclusion_evidence where a flag gives "Suggested inclusion_evidence: '...'" - apply.py does not write evidence) `$S/post_p3-NNN.py` starting `exec(open("audit/verify/kit/post_head.py").read())`: pin / ph / web / wf / save(); run `python3 -I $S/post_p3-NNN.py p3-NNN`. Check stored strings first (phones may be None or '').
4. `timeout 500 python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`
5. Append to audit/verify/criteria_followups.md + waterfront_leads.md (asks.md for questions), copy $S/p3-NNN/NH_NOTES_p3-NNN.md here, extend "Batches applied" below, add lessons to lessons.txt.
6. `git add campgrounds.json campgrounds_audit.json audit/verify/criteria_drops.py audit/verify/removals.json audit/verify/results/applied audit/verify/asks.md audit/verify/criteria_followups.md audit/verify/waterfront_leads.md audit/verify/kit/sd`, commit on master with the session trailers, then save held results to kept_results/ and `rm -rf $S/p3-NNN*`.

Batches applied:
- p3-581 (2026-11-23): 10 applied, 1 drop (4146 Rudy's, price + seasonal); water down 4141/4106/4132, 4137 -> creekside; pins 4100/4103/4141. Lead Jacobs Brook (leads/nh_leads.txt).
- p3-582 (2026-11-23): 11 applied, no drops; 4135 Sunshine Valley kept with seasonal caveat (~14% nightly); 804 Hampton coastal dunes vs bayfront ask (asks.md).
- p3-583 (2026-11-23): 11 applied, no drops; 4110 Jericho OHV ask (asks.md); water down 4108/4110; 4104 pond kept on RA per-site data.
- p3-584 (2026-11-23): 11 applied, no drops, no water changes; 4124/4125 now rec.gov-reservable; pin 4123.
- p3-585 (2026-11-23): 7 applied, 1 drop (4133 Wheelock Park, campground closed); 4130 Zealand riverfront->not; pins 14368/4130; lead 2 Ashuelot River.
- Lead 1 jacobs-brook-orford +15764 (2026-11-23): private, W/E $48 (passes by $2), ~half seasonal (27 'All Season' of ~60), operator's truck detour around the 3-ton Archertown Rd bridge in the note; not waterfront. Next id 15765.
- Lead 2 ashuelot-river-keene SKIP (2026-11-23): private, cheapest RV night $52 ($2 over), no gateway/GS; Google 4.5/329 + RV Life 9.53/78 - below the ~4.7 tiebreaker, so skip; result file carries every add field (flip decision to reverse).
