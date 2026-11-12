#!/bin/bash
# d.sh <drv args> : run one drv.py command under the shared lock, from p3-437 dir
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/4dfcd82f-59f6-4dfa-978f-ba76c2044814/scratchpad/p3-437
DRV_SOCK=./drv.sock PYTHONPATH=/home/andrew/.cache/ekko-pw timeout 200 flock /tmp/ekko-headless-browser.lock python3 /home/andrew/Dev/campgrounds/audit/private_gap_browser/drv.py "$@"
