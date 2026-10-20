#!/usr/bin/env python3
"""Entries whose note states a length limit under 23 ft. Free, read-only.

    python3 -I audit/trailer_length_2026-10-20/note_scan.py > note_hits_strict.txt

Only phrases that state a limit ("max 20 ft", "trailers to 22 ft", "22-ft max trailer"),
which keeps elevations, height clearances and depths out. Every hit was read by hand: the
number is often one loop, a trailer figure beside a longer motorhome one, or a reviewer's
report rather than a posted limit. 151 entries on 2026-10-20.
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
N = r"~?(\d{1,2})(?:\s*-\s*\d{1,2})?\s*-?\s*(?:ft|feet|foot|')"
PATS = [re.compile(p, re.I) for p in [
    r"(?:max(?:imum)?|limit(?:ed)?|up to|no more than|under|less than|<=?|not exceeding|cap(?:s|ped)? (?:\w+ ){0,3}at)\s*(?:of\s*)?(?:\w+\s){0,4}?" + N,
    N + r"\s*(?:\w+\s){0,2}(?:max(?:imum)?|limit|or less|or shorter|and under)",
    r"(?:trailers?|rvs?|rigs?|vehicles?|motorhomes?|campers?|units?)\s*(?:\w+\s){0,3}?(?:to|of|under|up to)\s*" + N,
    N + r"\s*(?:max\s*)?(?:trailers?|rvs?|rigs?|vehicles?|motorhomes?|campers?|units?|length)",
]]
rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
n = 0
for e in rows:
    note = e.get("note") or ""
    hits = set()
    for p in PATS:
        for m in p.finditer(note):
            if 8 <= int(m.group(1)) < 23:
                hits.add(note[max(0, m.start() - 110): m.end() + 70].replace("\n", " "))
    if hits:
        n += 1
        print(f"\n== {e['id']} {e['state']} {e['ownership']} {e['name']} | max_rig_ft={(e.get('sites') or {}).get('max_rig_ft')}")
        for h in sorted(hits):
            print("   ..", h)
print("\n", n, "entries")
