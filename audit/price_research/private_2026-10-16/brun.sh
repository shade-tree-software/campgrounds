#!/bin/bash
# Browser follow-up worker: for each state whose plain fetch is done, the ids with no $ line go through bcrawl.
cd "$(dirname "$0")/../../.."
P=audit/price_research/private_2026-10-16; T=audit/price_research/local_browser_2026-10-16/tools
while :; do
  left=0
  for s in $(cat $P/order.txt); do
    [ -f $P/bdone_$s ] && continue
    if [ ! -f $P/done_$s ]; then left=1; continue; fi
    python3 -I - $P/pages_$s.jsonl $P/bids_$s.json <<'PY'
import json,sys
ids=[]
for l in open(sys.argv[1]):
    r=json.loads(l)
    if not any(p.get('lines') for p in r['pages']): ids.append(r['id'])
json.dump(ids,open(sys.argv[2],'w'))
PY
    python3 $T/bcrawl.py $P/bids_$s.json $P/browser_$s.jsonl >> $P/brun.log 2>&1 || { echo "BFAIL $s $(date +%T)" >> $P/run.log; exit 1; }
    touch $P/bdone_$s; echo "BDONE $s $(date +%T)" >> $P/run.log
  done
  [ $left = 0 ] && break
  sleep 60
done
echo BALLDONE >> $P/run.log
