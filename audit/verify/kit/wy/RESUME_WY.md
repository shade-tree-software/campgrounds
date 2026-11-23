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

WY COMPLETE 2026-11-20 (queue p3-536..559, leads, split). Next: SD - kit/sd/RESUME_SD.md. WY QUEUE EMPTY after p3-558 (2026-11-20). LEADS DONE 2026-11-20 (audit/verify/leads/wy_leads.txt, wy_lead_prompt_template.txt, 25 leads): added 15727 Buffalo Bill Lake Shore, 15728 Shadow Mountain, 15729 Buffalo Valley, 15730 Elk Fork, 15731-15732 Seminoe South Red Hills + Sunshine Beach, 15733-15737 Casper Mountain (Deer Haven, Elkhorn Springs, Skunk Hollow, Tower Hill, Archery Range), 15738-15745 Glendo (Cottonwood, Elkhorn, Indian Point, Mule Hill, Red Hills, Sagebrush, Shelter Point, Whiskey Gulch); skipped City Slickers, BJ's Hwy 20, Glendo Broken Arrow + Soldier Rock (4WD), Blackrock Meadows (snowmobile lot; ask); Spread Creek HELD (asks.md). SPLIT DONE 2026-11-20 (kit/wy/splits/): 6359 -> Popo Agie + 15746 Sawmill. Next id 15748 (15747 Blackrock Meadows added on AWH's word 2026-11-20; Spread Creek skipped). Then: p3-559 = single-entry re-read of 6547 Larson Park (hand-built batch file: queue.py skips ids listed in any batches/*.json), then SD (build kit/sd/ from kit/wy/). ONE verifier at a time, 11 per batch.
Lead adds and split entries carry no verify_scan and show in `queue.py --report` (as SK's did): they were fully vetted in the lead pipeline - don't re-batch them.

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
3. Post script (also replace inclusion_evidence where a flag gives "Suggested inclusion_evidence: '...'" - apply.py does not write evidence) `$S/post_p3-NNN.py` starting `exec(open("audit/verify/kit/post_head.py").read())`: pin / ph / web / wf / save(); run `python3 -I $S/post_p3-NNN.py p3-NNN`. Check stored strings first (phones may be None or '').
4. `timeout 500 python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`
5. Append to audit/verify/criteria_followups.md + waterfront_leads.md (asks.md for questions), copy $S/p3-NNN/WY_NOTES_p3-NNN.md here, extend "Batches applied" below, add lessons to lessons.txt.
6. `git add campgrounds.json audit/verify/criteria_drops.py audit/verify/removals.json audit/verify/results/applied audit/verify/asks.md audit/verify/criteria_followups.md audit/verify/waterfront_leads.md audit/verify/kit/wy`, commit on master with the session trailers, then save held results to kept_results/ and `rm -rf $S/p3-NNN*`.

Batches applied: p3-536 (2026-11-20; no drops; Brooklyn Lake lakefront -> lakeview, Eagle Creek up to riverview; 6568 Torrington golf course kept on thin presence), p3-537 (2026-11-20; no drops; four water downgrades, Island Park up to creekside (06-08); Medicine Lodge re-pinned 320 m), p3-538 (2026-11-20; no drops; Slough Creek to creekside, Ayres to not waterfront; four pins incl. Vedauwoo 6.3 km + rename), p3-539 (2026-11-20; no drops; Beartooth Lake + Cook Lake to not waterfront, Connor Battlefield to creekside, North Fork up to riverview; six pins), p3-540 (2026-11-20; no drops; no water changes; Fremont Lake re-pinned 950 m; five links fixed), p3-541 (2026-11-20; 6543 Lazy Acres dropped (closed); Little Ponderosa to hipcamp; Madison + Mammoth re-pinned), p3-542 (2026-11-20; 6538 Powder River (price) + 6528 JACZ (seasonal/iffy) dropped; 6541 Parkway ask; three water changes; Reuter re-pinned), p3-543 (2026-11-20; no drops; Station Creek to first-come, Threemile to some_sites; Sibley + Tower Fall re-pinned; Jackson RD leads), p3-544 (2026-11-20; no drops; Wapiti to riverview; six re-pins; Elk Fork lead), p3-545 (2026-11-20; no drops; 6560 Kettle ask; Guernsey Sandy Beach to lakeview + re-pinned; Gray Reef to local; Easy Spot RV rename), p3-546 (2026-11-20; no drops; 6547 Larson Park unread (re-queue); Saratoga Lake to lakeview, Sinks Canyon to creekside, Sinks Sawmill split pending; three re-pins), p3-547 (2026-11-20; no drops; 6358 ask; Slate Creek to riverview, Tongue River to not waterfront; two re-pins), p3-548 (2026-11-20; 6516 CAM-PLEX dropped (event-only); 6449 horse-loop ask; Lewis Park electric to 0; Park County re-pinned), p3-549 (2026-11-20; 6419 Sinks Canyon FS (20-ft spurs) + 6379 Angles (trailhead/stock) dropped; Bennett Peak + Seminoe North Red Hills downgraded; two Seminoe leads), p3-550 (2026-11-20; no drops; 6445 Brown Mountain + 6439 Bobbie Thomson asks; Brooks Lake to lakeview, Campbell Creek to not waterfront; Black Beach re-pinned; Casper Mountain leads), p3-551 (2026-11-20; no drops; Deer Park to not waterfront + re-pinned; East Fork re-pinned; Cottonwood Beach rename), p3-552 (2026-11-20; no drops; East Table to riverview + re-pinned; Five Springs re-pinned 1.2 km; French Creek booking fixed; ten Glendo leads), p3-553 (2026-11-20; 6395 Haskin Creek dropped (closed); Hog Park to lakeview; Grave Springs re-pinned), p3-554 (2026-11-20; no drops; Jack Creek (Shoshone) to riverview, Louis Lake to lakeview, Lily Lake to not waterfront; two booking fixes), p3-555 (2026-11-20; no drops; Meeks Cabin to lakeview; Pelton Creek to FCFS; Moose Flat re-pinned; Libby Creek Aspen/Spruce leads closed (decommissioned)), p3-556 (2026-11-20; 6377 Scab Creek dropped (stock shared with RV loop); Sage re-pinned; Sugarloaf policy_ref), p3-557 (2026-11-20; 6428 Turpin Meadow dropped (stock sites in the loop); Whiskey Grove to riverview; Tailrace/West Tensleep/Willow Lake re-pinned; Westside + Willow Lake lakefront leads), p3-558 (2026-11-20; no drops; Wood River pond -> creekside; Worthen Meadow re-pinned; queue empty), p3-559 (2026-11-20; single-entry re-read of 6547 Larson Park: new town site + phone, renamed, re-pinned 55 m; WY COMPLETE)

Things to watch in WY (from the sweep handoff, project_wy_sweep_handoff):
- RV Life tagged BLM sites `dnr` and NPS/fairground sites `commercial`; the sweep reclassified them - check any that slipped.
- Whole-park state entries (Glendo, Boysen, Buffalo Bill, Keyhole, Curt Gowdy) may hold several campgrounds: split only campgrounds at separate places (~1 km+, own entrance) when a batch runs into one (feedback_split_multi_campground_parks).
- Yellowstone campground closures/construction change year to year (Norris, Pebble Creek, Tower Fall were closed at the sweep).

WY leads/splits to vet after the queue (detail in criteria_followups.md): City Slickers RV Park; Buffalo Bill SP Lake Shore; BJ's Hwy 20 second location; Jackson RD designated sites (Spread Creek, Shadow Mountain, Curtis Canyon dispersed, Pacific Creek, Buffalo Valley); Elk Fork (likely out); Seminoe South Red Hills + Sunshine Beach; split 6359 Sinks Canyon SP -> Sawmill; re-read 6547 Larson Park; Natrona Casper Mountain campgrounds (Deer Haven, Elkhorn Springs, Skunk Hollow, Tower Hill, Archery Range); ten Glendo SP campgrounds (p3-552 followups).

2026-11-22: 13585 Sage (Pathfinder) re-checked under AWH's high-water-edge ruling: raised to lakefront at the three westernmost shore shelters (~7-14 m to the 5,852.49 ft spillway-crest edge over open ground); the old "sage draw" read was wrong. Follow-ups: 13586 Weiss (south-row shelters ~12-15 m, likely lakefront) and 13584 Diabase (2023 rebuild pads need placing first) - not decided.
