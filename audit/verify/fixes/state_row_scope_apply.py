#!/usr/bin/env python3
"""Entries that their state's PARKS row does not describe stop inheriting it.

    python3 -I audit/verify/fixes/state_row_scope_apply.py [--apply]

From state_row_scope.json (a research agent, 2026-10-20, after the Sexton Pond finding):
state forests, wildlife areas and Montana's fishing access sites run by a different agency
or reservation system, or walk-up only, were showing the state parks' booking window,
minimums and fees as "typical". policy_ref "none" = inherit nothing (doc §3). Rows that
APPLY (same agency, same system: WI, MA, NJ, CT, IA, RI, MD forests; WV state forests) keep
inheriting. Montana fishing access sites missed by the research regex are added by name.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import campground_schema as cs
CG = os.path.join(ROOT, "campgrounds.json")
scope = json.load(open(os.path.join(HERE, "state_row_scope.json"), encoding="utf-8"))
ids = {i for v in scope.values() for i in (v.get("entry_ids_affected") or [])}
rows = json.load(open(CG, encoding="utf-8"))
fas = re.compile(r"fishing access|\bFAS\b", re.I)
ids |= {e["id"] for e in rows if e["state"] == "MT" and e.get("ownership") == "state"
        and fas.search(e["name"]) and "state park" not in e["name"].lower()}
n = 0
for e in rows:
    if e["id"] in ids and e.get(cs.POLICY_REF) != cs.POLICY_REF_NONE:
        cs.apply_update(e, {cs.POLICY_REF: cs.POLICY_REF_NONE})
        n += 1
        print(" ", e["id"], e["state"], e["name"][:60])
print(n, "to change of", len(ids))
if "--apply" in sys.argv and n:
    with open(CG, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("written")
