"""FL state forest campgrounds: the booking site's nightly price (floridastateforests.reserveamerica.com),
sampled for Tue 2027-01-12 and Sat 2027-01-16, read 2026-10-12 (fl_forest_booking_sample_2026-10-12.jsonl).

    python3 -I fl_forests_build.py OUT

FDACS's per-campground prices come out in odd cents and are the same on a weekday and a Saturday; the
reservation fee is $5.79. Hookups as the site details list them."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
# id: (parkId, price, what the sites have)
P = {101: (1120135, 22.52, "water and 30/50-amp electric"), 165: (1120180, 22.42, "water and 30/50-amp electric"),
     166: (1120172, 22.52, "30/50-amp electric, most with water"), 167: (1120155, 8.89, "no hookups"),
     169: (1120169, 13.76, "water, no electric"), 4712: (1121200, 22.52, "no hookups listed (RV/trailer-only sites)"),
     4713: (1120116, 22.73, "30/50-amp electric"), 4715: (1120101, 22.32, "water and 30/50-amp electric"),
     4716: (1120113, 22.32, "water and 30/50-amp electric"), 4717: (1120105, 22.12, "30/50-amp electric, most with water"),
     4718: (1120109, 22.12, "water and 30/50-amp electric"), 4720: (1120104, 22.32, "water and 30/50-amp electric"),
     4721: (1120121, 9.13, "no hookups"), 4722: (1121250, 22.62, "water and 30/50-amp electric"),
     4726: (1120404, 8.93, "no hookups"), 4727: (1120193, 9.09, "no hookups"), 4728: (1120195, 9.09, "no hookups")}
out = []
for eid, (pid, price, what) in sorted(P.items()):
    out.append({"id": eid, "name": rows[eid]['name'], "fees": {
        "nightly_low": price, "nightly_high": price, "currency": "USD", "reservation_fee": 5.79, "checked": "2026",
        "note": (f"${price:.2f} a night, weekday or weekend; the sites have {what}. $5.79 reservation fee. The Florida "
                 f"Forest Service's booking site, read {D} for January 2027 nights.")},
        "source": f"floridastateforests.reserveamerica.com parkId {pid} (sampled sites' 1-night price for 2027-01-12 and "
                  f"2027-01-16, read {D})"})
json.dump(out, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)
print(len(out), 'FL forest findings')
