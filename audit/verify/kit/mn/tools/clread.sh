#!/bin/bash
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/4dfcd82f-59f6-4dfa-978f-ba76c2044814/scratchpad/p3-437
export DRV_SOCK=./drv.sock PYTHONPATH=/home/andrew/.cache/ekko-pw
P=/home/andrew/Dev/campgrounds/audit/private_gap_browser
python3 $P/drv_server.py > dl/drv_server.log 2>&1 &
for i in $(seq 1 30); do [ -S drv.sock ] && break; sleep 1; done; sleep 5
rm -f dl/cl_redhead.jsonl
timeout 170 python3 $P/camplife_api.py dl/cl_redhead.jsonl 99999:https://www.camplife.com/6651542 2>&1 | tail -5
python3 $P/drv.py quit
sleep 2
