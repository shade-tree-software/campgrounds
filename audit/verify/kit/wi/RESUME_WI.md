# Phase 7 Wisconsin - resume

Order (AWH 2026-11-16): IL, VT, then WI (383), SK, WY, SD.

Build a batch (repo root; S = scratch dir, N = p3-NNN):

    python3 -I audit/verify/queue.py --batch $N --state WI --limit 11
    python3 -I audit/verify/kit/wi/mkpara_wi.py $S $N
    python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt
    mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
    sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: <ids>./" audit/verify/kit/wi/agent_prompt_template.txt > $S/${N}_agent.txt
    (append the current "Lessons from recent batches" paragraph)

Apply exactly as for IL/VT: apply.py --apply, a post script on kit/post_head.py, drops via criteria_drops.py, logs, copy WI_NOTES into kit/wi/, commit, clean scratch.

Batches applied: p3-485 (2026-11-16; 3401 Broken Bow and 3449 Dells of the Eau Claire unread), p3-486 (2026-11-16; 3364 dropped; 3380 Eagle View and 3398 Forest Pond unread), p3-487 (2026-11-16; 3410, 3509, 3414 dropped; 3519 Manitowoc Expo and 3589 Washburn unread), p3-488 (2026-11-16; 3431 dropped; 3551 Ojibwa unread), p3-489 (2026-11-16; no drops), p3-490 (2026-11-16; 3579, 3366, 3422, 15520 dropped; 3563 Cliffside unread), p3-491 (2026-11-16; 3387 dropped; 3369, 3576, 3494 unread), p3-492 (2026-11-16; no drops; 3374 Mohican unread), p3-493 (2026-11-16; 3442, 3412, 3370 dropped), p3-494 (2026-11-16; no drops; 3592 Veterans Memorial West Salem unread), p3-495 (2026-11-16; no drops; 3472 Clear Lake unread), p3-496 (2026-11-16; 3421, 3406 dropped; 3384 Eagles Landing unread), p3-497 (2026-11-16; 3428, 3391, 3419 dropped; 3486 asked), p3-498 (2026-11-16; 14490 dropped; 3429 Leon Valley unread), p3-499 (2026-11-16; 14492, 3376 dropped; 3394 asked), p3-500 (2026-11-16; 3425, 3583 dropped; 3440 St. Croix Casino unread), p3-501 (2026-11-16; 3371, 3400, 3424, 3427 dropped), p3-502 (2026-11-16; 3578 dropped; 3460, 3524 unread), p3-503 (2026-11-16; no drops; 3586 unread; Sidie Hollow split candidate), p3-504 (2026-11-16; no drops), p3-505 (2026-11-17; no drops; 3535 Big Eau Pleine and 13434 Blackhawk Memorial unread), p3-506 (2026-11-17; no drops), p3-507 (2026-11-17; no drops; 14495 asked), p3-508 (2026-11-17; no drops; Franklin Lake split candidate), p3-509 (2026-11-17; no drops), p3-510 (2026-11-17; no drops; 14499 asked; Interstate split candidate), p3-511 (2026-11-17; 3470 dropped; 13420 Marathon Park unread), p3-512 (2026-11-17; 13419 dropped), p3-513 (2026-11-17; 13417 dropped; 13437 Norwalk unread; 452 asked), p3-514 (2026-11-17; 14500 dropped; 13433 asked), p3-515 (2026-11-17; no drops; 13431 Rieck's Lake unread; 3562 asked), p3-516 (2026-11-17; 3354 dropped; 453 asked), p3-517 (2026-11-17; 14503 dropped; 14502 asked), p3-518 (2026-11-17; no drops; 14504 S'more Fun unread; 3529 status unclear), p3-519 (2026-11-17; 3595 dropped; last WI batch).

Sources (p3-485): plain curl works for most county and operator sites, blackhawklake.com PDFs, wvic.com, park-maps.campspot.com; Campspot via cs1.py under flock. REFUSED: marathoncounty.gov (Akamai 403, all Marathon County parks), ruskcountywi.com (Cloudflare), brokenbowcampground.com (406).

## RESUME HERE (WI queue COMPLETE after p3-519, 2026-11-17)

Queue: 0 WI entries left - the WI verification queue is done (p3-485..p3-519). Remaining WI work is the "Open after the WI queue" list below (leads, splits, unread, asks). Next batch number is **p3-520** (first SK batch). ONE verifier at a time, 11 per batch. After WI: SK, WY, SD (AWH order), each with its own kit/<st>/ (copy kit/wi/ and adapt mkpara + the template; SK = Canada: provincial ownership, CAD, C$69 gate).

Build + launch (S = session scratch dir):

    N=p3-520; python3 -I audit/verify/queue.py --batch $N --state WI --limit 11 && python3 -I audit/verify/kit/wi/mkpara_wi.py $S $N && python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt >/dev/null && mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
    IDS=$(python3 -I -c "import json;print(', '.join(str(x['entry']['id']) for x in json.load(open('audit/verify/batches/$N.json'))))")
    sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: $IDS./" audit/verify/kit/wi/agent_prompt_template.txt > $S/${N}_agent.txt
    printf '\n' >> $S/${N}_agent.txt; cat audit/verify/kit/wi/lessons.txt >> $S/${N}_agent.txt

Launch a background general-purpose agent: "Read and follow $S/p3-NNN_agent.txt exactly. It is your complete task (phase-7 verification of eleven Wisconsin campground entries: <ids>) and its hard rules override anything else you read. Working directory: /home/andrew/Dev/campgrounds." Keep kit/wi/lessons.txt current (add each batch's new refusing domains).

Apply a batch:
1. Drops: insert `    id: ('YYYY-MM-DD', "reason", "evidence"),` lines into DROPS in audit/verify/criteria_drops.py (after the last drop line), `python3 -I audit/verify/criteria_drops.py --apply`, then `mv audit/verify/results/<id>.json audit/verify/results/applied/` (if a result exists).
2. `python3 -I audit/verify/apply.py <kept ids> --apply`.
3. Post script `$S/post_p3-NNN.py` starting `exec(open("audit/verify/kit/post_head.py").read())`: pin(id,'old',lat,lng) / ph(id,old,new) / web(id,old,new) / wf(id,old,new,"evidence --Claude") / save(); run `python3 -I $S/post_p3-NNN.py p3-NNN`. Check stored strings first (phones may be None or '').
4. `timeout 500 python3 -m unittest tests.test_campground_schema tests.test_closures tests.test_season_filter tests.test_link_labels`
5. Append sections to audit/verify/criteria_followups.md + waterfront_leads.md (asks.md for questions), copy $S/p3-NNN/WI_NOTES_p3-NNN.md here, extend the "Batches applied" line above.
6. `git add campgrounds.json audit/verify/criteria_drops.py audit/verify/removals.json audit/verify/results/applied audit/verify/asks.md audit/verify/criteria_followups.md audit/verify/waterfront_leads.md audit/verify/kit/wi`, commit on master with the session trailers, `rm -rf $S/p3-NNN*`.

Rulings and rules learned in WI (2026-11-16):
- Price gate = cheapest real RV night (an electric site) in ANY season (Shelby 10-30, reaffirmed 11-16: HTR Door County 3486 kept; Reel Livin' 3394 dropped at "$50-55"). Rivers Edge 3370 was wrongly dropped and RESTORED; Hi-Pines 3387, Hickory Oaks 3419, Lake Joy 14490 stay dropped (borderline price + mediocre Google). Borderline + Google under ~4.5 = drop and report (10-31 standing call).
- booking.fcfs `after_cutoff` IS valid (reservations close N days out, then walk-up). Chippewa County parks (Pine Point 3503, Morris-Erickson 3542, Otter Lake 3573): 10-day/3-night reservation rule but caretaker sells walk-up nights - kept. MD 63/533, PA 1055, OR 11057/11058/11082/11096 carry fcfs always + a cutoff - read before changing.
- Mostly-seasonal private parks need a posted nightly rate or a booking site; 10-50% nightly = keep with "Mostly seasonal: about N of its M sites are sold by the night". Bar-campgrounds with a shared Google listing and no operator rate have been dropped (V & M, Wildlife Bar, River's Edge Bruce, Frontier Bar).
- A general campground with ATV trail access stays. Casino-lot RV parking is not a campground (St. Croix Turtle Lake 3440 passed: own RV loop).

Open after the WI queue:
- UNREAD (try a real browser or a call): 3449 Dells of the Eau Claire, 3380 Eagle View, 3398 Forest Pond, 3519 Manitowoc Expo, 3589 Washburn Memorial, 3551 Ojibwa, 3563 Cliffside, 3369 Featherstone, 3576 Goose Island, 3494 James N. McNally, 3374 Mohican RV Park (capture: 57 sites $35/45; re-pin 44.8740,-88.8600, phone 715-787-2751), 3592 Veterans Memorial West Salem, 3472 Clear Lake Park, 3384 Eagles Landing, 3429 Leon Valley, 3440 St. Croix Casino, 3460 Little Sand Bay (coastal-walk lead; phone conflict), 3524 Melrose City Park (likely no camping - drop candidate), 3586 Vernon County Fairgrounds, 3535 Big Eau Pleine (marathoncounty.gov), 13434 Blackhawk Memorial (lafayettecountywi.org; caretaker 608-220-5529), 13420 Marathon Park (marathoncounty.gov; fairgrounds rule unmet), 13437 Norwalk Village Park (norwalkwi.gov Cloudflare; Google phone 608-823-7760), 13431 Rieck's Lake (cityofalmawi.gov WAF; lakefront lead; Google phone 608-685-3330), 14504 Waupaca S'more Fun (406 Mod_Security; ResNexus), 3529 West Arbutus (status: gone from county booking - call 715-284-8475). 3401 Broken Bow still in asks.md.
- LEADS to vet + add: Rusk County Perch Lake Campground; Murphy Campground; McNally West (Grantsburg, 400 W Olson Dr, opened 2025); Hawthorne Hills County Park (Saukville, probably not open yet); Oconto City Park Campground (920-834-7725); Harstad County Park (Eau Claire County); Kewaunee RV & Campground (333 Terraqua Dr, 920-388-4851); Weborg Point (Peninsula SP, 12 electric); Picnic Point (Mondeaux Flowage, unchecked).
- SPLIT: 3585 Sidie Hollow (Boat Landing 101-125 ~1.3 km, Upper Ridge 301-330 ~0.7 km, own roads); 3341 Franklin Lake (South 1-40 ~45.9305,-88.9945, North 41-77 ~45.9395,-88.9865, ~1.1 km; check own entrances); 3291 Interstate (North ~45.4043,-92.6478 37 sites from Hwy 8, South ~45.391,-92.662 45 rustic, ~1.7 km).
- Phone-call candidates were listed for AWH 2026-11-16; AWH: skip the phone list for now (do not add them to phone_list.md unless asked).
- For AWH to rule if wished: 3405 Smokey Hollow (Dells gateway, 18% nightly); coastal-walk upgrades I made (3544 Bay Shore, 3515 Big Bay, 3461 Dalrymple, 3568 Saxon Harbor); 3411 Minong ATV campground.
