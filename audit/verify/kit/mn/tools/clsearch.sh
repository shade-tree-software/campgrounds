#!/bin/bash
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/4dfcd82f-59f6-4dfa-978f-ba76c2044814/scratchpad/p3-437
export DRV_SOCK=./drv.sock PYTHONPATH=/home/andrew/.cache/ekko-pw
P=/home/andrew/Dev/campgrounds/audit/private_gap_browser
python3 $P/drv_server.py > dl/drv_server.log 2>&1 &
for i in $(seq 1 30); do [ -S drv.sock ] && break; sleep 1; done; sleep 5
python3 $P/drv.py goto url=https://www.camplife.com/1050/reservation/step1 wait=8000 | head -c 200; echo
for n in "Fairgrounds%20and%20Redhead%20Camping" "Fairgrounds%20and%20Redhead%20Campground" "Redhead%20Campground"; do
python3 $P/drv.py eval js="(async()=>{const r=await fetch('/api/campground/search/events/$n');return r.status+' '+(await r.text()).slice(0,1500)})()" max=5000; sleep 1
done > dl/cl_search.txt
python3 $P/drv.py quit
sleep 2
