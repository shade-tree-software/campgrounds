#!/usr/bin/env python3
"""Digest of cpd.jsonl for hand review: per matched park, the header rate and every review dated
2024 or later (with its rate, if it gave one), plus any closure wording. Parks with no dated 2024+
rate are listed in one line at the end.

    python3 -I audit/price_research/camper_2026-10-17/cpd_dig.py CPD.jsonl
"""
import json, re, sys


def year_of_header(d):           # "5/7/26"
    return 2000 + int(d.split("/")[-1])


none = []
for l in open(sys.argv[1]):
    r = json.loads(l)
    if not r.get("url"):
        continue
    revs = [v for v in r.get("reviews", []) if int(v["date"][-4:]) >= 2024]
    hdr = r.get("last_rate")
    rated = [v for v in revs if v.get("rate")]
    if not rated and not (hdr and year_of_header(hdr[1]) >= 2024):
        none.append(f"{r['id']}" + (f"(hdr {hdr[0]} {hdr[1]})" if hdr else ""))
        continue
    print(f"## {r['id']} {r['state']} {r['name']}  [{r['km']} km] {r['url']}")
    if hdr:
        print(f"   HEADER {hdr[0]} reported {hdr[1]}")
    for v in revs:
        print(f"   {v['date']:>20} {v.get('rate', '-'):>8}  {v['text'][:230]}")
    if r.get("closed_text"):
        print("   CLOSED?", r["closed_text"])
print("\nNO 2024+ RATE:", " ".join(none))
