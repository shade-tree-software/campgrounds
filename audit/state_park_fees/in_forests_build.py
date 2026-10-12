"""IN state forest campgrounds: the DNR's first-come, first-served rates, read 2026-10-12.

    python3 -I in_forests_build.py OUT

https://www.in.gov/dnr/state-parks/rates-and-fees/camping-fees: 'First-Come, First-Served Camping -
Available at the rates listed below for State Forest properties ... that are not on Indiana's Central
Reservation System: Non-Electric $12, Primitive $12.15' (Horsemen's Improved $15, Horsemen's Primitive
$14.95). These campgrounds are not on the reservation system."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
out = []
for eid in (1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1099):
    out.append({"id": eid, "name": rows[eid]['name'], "fees": {
        "nightly_low": 12, "nightly_high": 12.15, "currency": "USD", "checked": "2026",
        "note": ("$12 a night for a non-electric site, $12.15 for a primitive one: the Indiana DNR's first-come, "
                 "first-served rate for state forest campgrounds, which are not on the reservation system. Read " + D + ".")},
        "source": f"https://www.in.gov/dnr/state-parks/rates-and-fees/camping-fees (First-Come, First-Served Camping: "
                  f"'State Forest properties ... Non-Electric $12, Primitive $12.15', read {D})"})
json.dump(out, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)
print(len(out), 'IN forest findings')
