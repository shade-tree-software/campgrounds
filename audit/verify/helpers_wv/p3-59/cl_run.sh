#!/bin/bash
export DRV_SOCK=/home/andrew/.cache/p359drv.sock PYTHONPATH=/home/andrew/.cache/ekko-pw
cd /home/andrew/Dev/campgrounds
python3 -u audit/private_gap_browser/drv_server.py > /tmp/claude-1000/-home-andrew-Dev-campgrounds/5a2365fc-fe6c-4508-9059-5f9b77057f7c/scratchpad/p3-59/drv.log 2>&1 &
for i in $(seq 1 30); do [ -S /home/andrew/.cache/p359drv.sock ] && break; sleep 1; done
timeout 400 python3 audit/private_gap_browser/camplife_api.py "$@"
python3 audit/private_gap_browser/drv.py quit
wait
