#!/usr/bin/env python3
"""Per-site rec.gov rates for unpriced federal entries matched by name + position
(recgov_byname.py -> byname.json, recgov_sites.py --fetch byname_sites.json IDS), 2026-10-16.
Only matches that are the campground itself (not a group/cabin/day-use facility nearby)
and whose sites carry a current-or-future season; one-site listings are placeholders and skipped.
"""
import json
RG = "https://www.recreation.gov/camping/campgrounds/"
ROWS = [  # entry id, rec.gov facility, low, high, note
 (37, 233369, 30, 30, None),
 (504, 10351700, 15, 30, None),
 (6401, 10048028, 21.53, 42.17, None),
 (6677, 10309470, 25, 25, "rec.gov types all 24 sites RV ELECTRIC."),
 (9589, 10351673, 10, 10, None),
 (9630, 10386871, 15, 15, None),
 (10055, 202192, 10, 10, None),
 (10276, 10363770, 20, 20, None),
 (10279, 10363762, 15, 15, None),
 (10699, 10372616, 6, 6, None),
 (11164, 10372540, 13, 13, None),
 (11378, 256350, 18, 18, None),
 (12331, 272109, 5, 5, None),
]
F = []
for i, fid, lo, hi, note in ROWS:
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if note:
        fees["note"] = note
    F.append({"id": i, "fees": fees, "source": f"{RG}{fid} (per-campsite rates via /api/search/campsites, RV-usable sites, current season; read 2026-10-16)"})
json.dump(F, open("byname_findings.json", "w"), indent=1, ensure_ascii=False)
print(len(F))
