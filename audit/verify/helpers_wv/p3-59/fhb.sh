#!/bin/bash
cd /tmp/claude-1000/-home-andrew-Dev-campgrounds/5a2365fc-fe6c-4508-9059-5f9b77057f7c/scratchpad/p3-59
B=https://fareharbor.com/embeds/book/riverriders/items
BW_WAIT=9000 PYTHONPATH=/home/andrew/.cache/ekko-pw timeout 200 python3 bw.py fhb $B/340530/availability/1892326709/book/ $B/658002/availability/1903617024/book/ $B/340530/availability/1892327786/book/ $B/643828/availability/1892574424/book/
