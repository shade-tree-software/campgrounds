#!/usr/bin/env python3
"""rec.gov leftovers priced from per-campsite rates (recgov_sites.py cache), read by hand 2026-10-16.

    python3 -I build_recgov.py  -> recgov_sites_findings.json for ../apply.py
"""
import json
SITES = "https://www.recreation.gov/api/search/campsites?fq=asset_id:{}"
# id, facility, low, high, note
ROWS = [
 (33, "10046915", 20, 20, None),
 (377, "259242", 10, 20, "$20/night May 15-Oct 15, $10 in the shoulder seasons."),
 (579, "247603", 25, 25, None),
 (5780, "233921", 26, 26, "rec.gov types every site tent-only; towing prohibited, 24 ft max."),
 (5913, "10369364", 10, 10, None),
 (6392, "247785", 53, 53, None),
 (6886, "10052170", 20, 20, "Every site has electric."),
 (9760, "273785", 60, 60, "BLM's page: $30 site + $15 electric/water + $15 dump station, billed together as $60/night on rec.gov."),
 (9889, "272257", 16, 16, None),
 (10288, "10389244", 30, 30, "Tent-only sites $15."),
 (10764, "10060885", 16, 16, None),
 (10786, "232840", 26, 26, None),
 (10968, "232789", 54, 81, "Every RV site is a double ($54) or triple ($81); the one single site is tent-only ($27)."),
 (11000, "10355857", 10, 15, None),
 (11339, "258825", 30, 30, None),
 (11382, "10215909", 18, 18, None),
 (12093, "10300375", 24, 24, None),
 (12360, "247867", 20, 20, None),
]
F = []
for i, fid, lo, hi, note in ROWS:
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if note:
        fees["note"] = note
    src = SITES.format(fid) + " (per-campsite rates, current seasons, read 2026-10-16)"
    if i == 9760:
        src += "; https://www.blm.gov/visit/huckleberry-campground (Fees)"
    F.append({"id": i, "fees": fees, "source": src})
json.dump(F, open("recgov_sites_findings.json", "w"), indent=1, ensure_ascii=False)
print(len(F))
