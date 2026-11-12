#!/bin/bash
# clsess.sh : one locked browser session reading CampLife 1050's booking setup + an availability probe
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/4dfcd82f-59f6-4dfa-978f-ba76c2044814/scratchpad/p3-437
export DRV_SOCK=./drv.sock PYTHONPATH=/home/andrew/.cache/ekko-pw
P=/home/andrew/Dev/campgrounds/audit/private_gap_browser
python3 $P/drv_server.py > dl/drv_server.log 2>&1 &
for i in $(seq 1 30); do [ -S drv.sock ] && break; sleep 1; done
python3 $P/drv.py goto url=https://www.camplife.com/1050/reservation/step1 wait=9000 | head -c 300; echo
python3 $P/drv.py eval js="(async()=>{const r=await fetch('/api/reservation/session?campgroundIdOrAlias=1050');return await r.text()})()" max=5000000 > dl/cl_session.json
python3 $P/drv.py eval js="(async()=>{const r=await fetch('/api/campground/1050/availability',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({checkinDate:'06-09-2027',checkoutDate:'06-10-2027',numAdults:2,numKids:0,numPets:0})});return r.status+' '+await r.text()})()" max=3000000 > dl/cl_avail.json
python3 $P/drv.py text max=4000 > dl/cl_step1.txt
python3 $P/drv.py quit
sleep 2
