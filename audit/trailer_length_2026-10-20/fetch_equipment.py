#!/usr/bin/env python3
"""Re-read the candidates' campsites from RIDB, keeping PERMITTEDEQUIPMENT max lengths.

    set -a; . ./.env; set +a; python3 -I audit/trailer_length_2026-10-20/fetch_equipment.py FID...

The recgov_hookups cache keeps only equipment NAMES, and the site attribute "Max Vehicle
Length" turned out to be a flat 20 across whole facilities whose driveways run 40-90 ft.
The per-equipment MaxLength is what recreation.gov prints as "RV up to N ft". Writes
equipment.json beside this script, {fid: [{id, name, reservable, type, attrs, equip: {NAME: maxlen}}]}.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from recgov_hookups import fetch_campsites, compact_site

OUT = os.path.join(HERE, "equipment.json")
data = json.load(open(OUT)) if os.path.exists(OUT) else {}
for fid in sys.argv[1:]:
    if fid in data:
        continue
    sites = []
    for s in fetch_campsites(fid):
        c = compact_site(s)
        c["equip"] = {(e.get("EquipmentName") or "").strip().upper(): e.get("MaxLength")
                      for e in s.get("PERMITTEDEQUIPMENT") or []}
        sites.append(c)
    data[fid] = sites
    json.dump(data, open(OUT, "w"), indent=0)
    print(fid, len(sites), flush=True)
