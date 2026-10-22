#!/usr/bin/env python3
"""SC 'state' entries that are not SC State Parks stop inheriting the state:SC row.

    python3 -I audit/verify/fixes/sc_not_state_parks.py [--apply]

Found by the phase 7 verifier at Sexton Pond (2026-10-20): state:SC is the SC State Parks
row (13-month window, 2-night minimum), but these are SC Forestry Commission state-forest
sites (Sand Hills, Manchester) and an SCDNR field-trial area, which book by phone a day at
a time or not at all. Inheriting the parks' rules printed them as "typical" where they are
wrong. policy_ref "none" = inherit nothing (doc §3); their own verified values stay.
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
import campground_schema as cs
IDS = [606, 607, 608, 609, 610, 611, 612]  # 13978 H. Cooper Black removed 2026-10-21: it books on SC State Parks under the state:SC rules (p3-71)
CG = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(CG, encoding="utf-8"))
n = 0
for e in rows:
    if e["id"] in IDS and e.get(cs.POLICY_REF) != cs.POLICY_REF_NONE:
        cs.apply_update(e, {cs.POLICY_REF: cs.POLICY_REF_NONE})
        n += 1
        print(" ", e["id"], e["name"])
print(n, "to change")
if "--apply" in sys.argv and n:
    with open(CG, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("written")
