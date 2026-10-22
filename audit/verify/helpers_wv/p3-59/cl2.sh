#!/bin/bash
export DRV_SOCK=/home/andrew/.cache/p359drv.sock PYTHONPATH=/home/andrew/.cache/ekko-pw
cd /home/andrew/Dev/campgrounds
rm -f /home/andrew/.cache/p359drv.sock /tmp/claude-1000/-home-andrew-Dev-campgrounds/5a2365fc-fe6c-4508-9059-5f9b77057f7c/scratchpad/p3-59/drv.log; python3 -u audit/private_gap_browser/drv_server.py > /tmp/claude-1000/-home-andrew-Dev-campgrounds/5a2365fc-fe6c-4508-9059-5f9b77057f7c/scratchpad/p3-59/drv.log 2>&1 &
for i in $(seq 1 30); do grep -q ready /tmp/claude-1000/-home-andrew-Dev-campgrounds/5a2365fc-fe6c-4508-9059-5f9b77057f7c/scratchpad/p3-59/drv.log 2>/dev/null && break; sleep 1; done
timeout 200 python3 audit/private_gap_browser/camplife.py 6385653 2026-10-27 2026-10-29 3
timeout 200 python3 audit/private_gap_browser/camplife.py 6385653 2026-11-10 2026-11-12 2
python3 audit/private_gap_browser/drv.py quit
wait
