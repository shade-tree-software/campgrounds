"""AL findings: each park's reservation calendar on reserve.alapark.com, read 2026-10-12.

    python3 -I al_build.py SUMMARY.json OUT

SUMMARY is vendor_parse.py's digest of vendor_calendar.py's text (al_calendar_summary_2026-10-12.json):
every bookable night's price for two weeks from 2026-10-13 and from 2027-06-15, read with an Alabama zip;
Cheaha read again with a Pennsylvania zip showed the same prices, so there is no out-of-state rate.
Alabama prices by site and night and publishes no table; rows named as campsites only (primitive,
backcountry, equestrian and group sites left out)."""
import json, os, sys
summary, out_path = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
S = json.load(open(summary))
D = "2026-10-12"
SLUG = {199: "desoto", 200: "cheaha", 201: "monte-sano", 202: "gulf", 680: "lake-guntersville", 682: "wind-creek",
        707: "joe-wheeler"}
out = []
for eid, slug in sorted(SLUG.items()):
    vals = [w["std"] for w in S[slug].values() if "std" in w]
    low, high = min(v["min"] for v in vals), max(v["max"] for v in vals)
    text = (f"${low}-{high} a night for an RV campsite. The price changes by site and night, higher on weekends and busy "
            f"dates. No out-of-state rate. Every bookable night on the park's reservation calendar for two weeks from "
            f"2026-10-13 and from 2027-06-15, read {D}.")
    out.append({"id": eid, "name": rows[eid]['name'],
                "fees": {"nightly_low": low, "nightly_high": high, "currency": "USD", "checked": "2026", "note": text},
                "source": f"https://reserve.alapark.com/{slug}/campsites (Calendar View, every campsite's price for the two "
                          f"weeks from 2026-10-13 and from 2027-06-15 with an Alabama zip, read {D}; Cheaha re-read with a "
                          f"Pennsylvania zip showed the same prices)"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'AL findings')
for x in out: print(x['id'], x['name'][:36], x['fees']['nightly_low'], x['fees']['nightly_high'])
