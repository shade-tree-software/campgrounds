#!/usr/bin/env python3
"""Apply aggregator-URL cleanup decisions to campgrounds.json.

    python3 audit/aggregator_url/apply.py [--apply]

Reads decisions.jsonl (latest row per id wins). `set_site` puts the operator/agency
URL first in `website`; aggregator URLs after it are dropped, EXCEPT a RoverPass
listing that is bookable (Instant Book per probe.json, or Request to Book per rp_request.json) - that is a booking channel,
not just a directory record. Other non-aggregator URLs already present are kept.
Rows with any other action (keep / flag / remove_candidate) are reported, never
written. Dry run by default.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
AG = re.compile(r"rvlife|campgroundreviews|thedyrt|goodsam|campendium|allstays|roverpass|"
                r"freecampsites|rvparky|campnative|texascampgrounds", re.I)

dec = {}
for line in open(HERE / "decisions.jsonl"):
    if line.strip():
        r = json.loads(line)
        dec[r["id"]] = r
bookable = {p["id"] for p in json.load(open(HERE / "probe.json")) if p["instant"] > 0}
# "Request to Book" listings are claimed and bookable too (approval-gated)
bookable |= {int(k) for k, v in json.load(open(HERE / "rp_request.json")).items() if v > 0}

path = ROOT / "campgrounds.json"
data = json.loads(path.read_text())
changed = 0
for e in data:
    r = dec.get(e["id"])
    if not r or r["action"] != "set_site":
        continue
    old = (e.get("website") or "").split()
    keep = [u for u in old if not AG.search(u)
            or ("roverpass" in u and e["id"] in bookable)]
    new = [r["url"]] + [u for u in keep if u.rstrip("/") != r["url"].rstrip("/")]
    val = "\n".join(new)
    if val != e.get("website"):
        print(f"{e['id']} {e['name']}: {old} -> {new}")
        e["website"] = val
        changed += 1
print(changed, "changed")
others = [r for r in dec.values() if r["action"] != "set_site"]
for r in others:
    print("  not applied:", r["id"], r["action"], r.get("why", ""))
if "--apply" in sys.argv and changed:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("written")
