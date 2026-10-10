#!/usr/bin/env python3
"""Record satellite waterfront calls: wf_add.py <site_id> <waterfront> <evidence> [...triples]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "waterfront.json")
wf = json.load(open(p)) if os.path.exists(p) else {}
a = sys.argv[1:]
for i in range(0, len(a), 3):
    wf[a[i]] = {"waterfront": a[i + 1], "evidence": a[i + 2]}
json.dump(wf, open(p, "w"), indent=1, ensure_ascii=False)
print(len(wf), "calls recorded")
