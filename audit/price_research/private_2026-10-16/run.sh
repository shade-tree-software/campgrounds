#!/bin/bash
# Worker K of 4: every 4th state of order.txt (smallest first). Resumable.
cd "$(dirname "$0")/../../.."
P=audit/price_research/private_2026-10-16; K=$1
awk -v k=$K 'NR%4==k' $P/order.txt | while read s; do
  [ -f $P/done_$s ] && continue
  python3 -I audit/price_research/local_pages.py - $P/pages_$s.jsonl --idfile $P/ids/$s.json >> $P/run_$K.log 2>&1
  touch $P/done_$s; echo "DONE $s $(date +%T)" >> $P/run.log
done
