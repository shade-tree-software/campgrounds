#!/bin/bash
# Sequential HTTP crawl of unpriced local entries' own pages, one state at a time (resumable).
cd "$(dirname "$0")/../../.."
W=audit/price_research/local_2026-10-17
for ST in "$@"; do
  python3 -I audit/price_research/local_pages.py $ST $W/pages_$ST.jsonl >> $W/run.log 2>&1
  echo "DONE $ST $(wc -l < $W/pages_$ST.jsonl)" >> $W/run.log
done
