"""SC findings: each park's reservation calendar on reserve.southcarolinaparks.com, read 2026-10-12.

    python3 -I sc_build.py SUMMARY.json OUT

SUMMARY is vendor_parse.py's digest of vendor_calendar.py's text (sc_calendar_summary_2026-10-12.json):
every bookable night's price for two weeks from 2026-10-13 and from 2027-06-15. South Carolina prices by
site and night (demand pricing), publishes no table, charges no reservation fee and has no non-resident
rate (registry row state:SC), so each entry gets the range of its standard RV sites; full-service and
non-electric sites go in the note."""
import json, os, sys
summary, out_path = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
S = json.load(open(summary))
D = "2026-10-12"
SLUG = {52: "devils-fork", 96: "lake-wateree", 99: "dreher-island", 175: "huntington-beach", 176: "myrtle-beach",
        177: "colleton", 179: "hunting-island", 221: "paris-mountain", 589: "cheraw", 621: "santee",
        624: "little-pee-dee", 683: "edisto-beach", 686: "calhoun-falls", 702: "hamilton-branch",
        706: "lake-hartwell", 717: "lake-greenwood", 719: "baker-creek", 721: "sadlers-creek"}


def rng(park, kind):
    vals = [w[kind] for w in S[park].values() if kind in w]
    return (min(v["min"] for v in vals), max(v["max"] for v in vals)) if vals else None


out = []
for eid, slug in sorted(SLUG.items()):
    std, fhu, ne = rng(slug, "std"), rng(slug, "fhu"), rng(slug, "ne")
    if std:
        low, high = std
        text = f"${low}-{high} a night for a standard campsite"
    else:
        low, high = fhu
        text = f"Every campsite is full-service: ${low}-{high} a night"
    if ne:
        low = min(low, ne[0])
        text += f"; sites without electric ${ne[0]}-{ne[1]}"
    if fhu and std:
        text += f"; full-service sites ${fhu[0]}-{fhu[1]}"
    text += (". The price changes by site and night, higher on weekends and busy dates. No reservation fee and no "
             f"out-of-state rate. Every bookable night on the park's reservation calendar for two weeks from 2026-10-13 "
             f"and from 2027-06-15, read {D}.")
    out.append({"id": eid, "name": rows[eid]['name'],
                "fees": {"nightly_low": low, "nightly_high": high, "currency": "USD", "checked": "2026", "note": text},
                "source": f"https://reserve.southcarolinaparks.com/{slug}/campsites (Calendar View, every site's price for "
                          f"the two weeks from 2026-10-13 and from 2027-06-15, read {D})"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'SC findings')
for x in out:
    print(x['id'], x['name'][:36], x['fees']['nightly_low'], x['fees']['nightly_high'], '|', x['fees']['note'][:110])
