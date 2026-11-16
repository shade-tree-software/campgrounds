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

Batches applied: p3-485 (2026-11-16; 3401 Broken Bow and 3449 Dells of the Eau Claire unread), p3-486 (2026-11-16; 3364 dropped; 3380 Eagle View and 3398 Forest Pond unread), p3-487 (2026-11-16; 3410, 3509, 3414 dropped; 3519 Manitowoc Expo and 3589 Washburn unread), p3-488 (2026-11-16; 3431 dropped; 3551 Ojibwa unread), p3-489 (2026-11-16; no drops), p3-490 (2026-11-16; 3579, 3366, 3422, 15520 dropped; 3563 Cliffside unread), p3-491 (2026-11-16; 3387 dropped; 3369, 3576, 3494 unread).

Sources (p3-485): plain curl works for most county and operator sites, blackhawklake.com PDFs, wvic.com, park-maps.campspot.com; Campspot via cs1.py under flock. REFUSED: marathoncounty.gov (Akamai 403, all Marathon County parks), ruskcountywi.com (Cloudflare), brokenbowcampground.com (406).
