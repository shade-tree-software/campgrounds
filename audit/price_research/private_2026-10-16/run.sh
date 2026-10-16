#!/bin/bash
# Fetch each state's unpriced private parks' own pages, smallest state first. Resumable.
cd "$(dirname "$0")/../../.."
P=audit/price_research/private_2026-10-16
for s in $(cat $P/order.txt); do
  python3 -I audit/price_research/local_pages.py - $P/pages_$s.jsonl --idfile $P/ids/$s.json >> $P/run.log 2>&1
  echo "DONE $s $(date +%T)" >> $P/run.log
done
echo ALLDONE >> $P/run.log
