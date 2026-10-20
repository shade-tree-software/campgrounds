#!/usr/bin/env python3
"""Entries whose note or `sites.max_rig_ft` states a length limit under 23 ft. Free, read-only.

    python3 -I audit/trailer_length_2026-10-20/note_scan.py

Prints each hit with the sentence around the number; every one is read by hand, because the
number may describe one loop, a tent pad, a road warning or a site type rather than the
campground's limit.
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEN = re.compile(r"(\d{1,2})(?:\s*-\s*\d{1,2})?\s*(?:-|\s)?(?:ft|feet|foot|')(?![a-z])", re.I)
CTX = re.compile(r"\b(trailers?|rvs?|rigs?|vehicles?|motorhomes?|motor homes?|campers?|length|max(imum)?|limit(ed)?|up to|under)\b", re.I)
ELEV = re.compile(r"elev|deep|tall|high|wide|width|depth|drop|cliff|falls?\b", re.I)
rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
n = 0
for e in rows:
    note = e.get("note") or ""
    mr = (e.get("sites") or {}).get("max_rig_ft")
    hits = []
    for m in LEN.finditer(note):
        v = int(m.group(1))
        if not 8 <= v < 23:
            continue
        near = note[max(0, m.start() - 50): m.end() + 25]
        if CTX.search(near) and not ELEV.search(note[m.end(): m.end() + 12]):
            ctx = note[max(0, m.start() - 120): m.end() + 60]
            hits.append(ctx.replace("\n", " "))
    if hits or (mr is not None and mr < 23):
        n += 1
        print(f"\n== {e['id']} {e['state']} {e['ownership']} {e['name']} | max_rig_ft={mr}")
        for h in hits:
            print("   ..", h)
print("\n", n, "entries")
