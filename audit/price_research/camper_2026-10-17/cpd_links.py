#!/usr/bin/env python3
"""Re-read matched Campendium pages for the operator links the listing shows (website, Facebook, phone);
cpd_read.py captured them only from 2026-10-17 on. Writes 'links' into CPD.jsonl in place."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpd_read as cr
path = sys.argv[1]
recs = [json.loads(l) for l in open(path)]
for r in recs:
    if not r.get("url") or "links" in r:
        continue
    url, page = cr.fetch(r["url"]); time.sleep(cr.PAUSE)
    if url:
        r["links"] = cr.parse(cr.text_of(page)).get("links", [])
        print(r["id"], r["links"], flush=True)
with open(path + ".tmp", "w") as fh:
    for x in recs:
        fh.write(json.dumps(x, ensure_ascii=False) + "\n")
os.replace(path + ".tmp", path)
