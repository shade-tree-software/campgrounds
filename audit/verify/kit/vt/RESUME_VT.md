# Phase 7 Vermont - resume

Order (AWH 2026-11-16): IL, then VT (33 left), then WI, SK, WY, SD.

Build a batch (from the repo root, S = scratch dir, N = p3-NNN):

    python3 -I audit/verify/queue.py --batch $N --state VT --limit 11
    python3 -I audit/verify/kit/vt/mkpara_vt.py $S $N
    python3 -I audit/verify/kit/mkbrief_mo.py $S $N $S/${N}_para.txt
    mkdir -p $S/$N && cp -r audit/verify/kit/il/tools $S/$N/tools
    sed -e "s#SCRATCH#$S#g" -e "s/p3-NNN/$N/g" -e "s/: IDS\./: <ids>./" audit/verify/kit/vt/agent_prompt_template.txt > $S/${N}_agent.txt

Apply exactly as for IL (see kit/il/RESUME_IL.md): apply.py --apply, a post script on kit/post_head.py for pins/phones/websites/waterfront, drops via criteria_drops.py, logs, copy VT_NOTES into kit/vt/, commit, clean scratch.

Batches applied: p3-409 (2026-11-11), p3-482 (2026-11-16), p3-483 (2026-11-16; 4097 unread), p3-484 (2026-11-16; 4095 dropped). VT QUEUE DONE; 4097 Hazen's Notch unread (phone list).
