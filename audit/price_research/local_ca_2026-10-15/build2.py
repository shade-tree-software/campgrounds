"""CA local, browser pass (browser.jsonl via bcrawl, read 2026-10-15). python3 -I build2.py > findings2.json"""
import json
SCC = "Santa Clara County Parks from 2026-03-01: RV campsites $53 a night peak (water and electric; 2 vehicle entries and dump included), tent $41; 25% off outside peak season."
ROWS = [  # id, low, high, resfee, key text to find the page, note
 (11726, 35, 35, None, "Sites 1-30: $35.00", "Bogart Regional Park (Beaumont-Cherry Valley Rec and Park): sites 1-30 $35 a night."),
 (11727, 24, 40, None, "Waterfront Campsite (With Utilities)", "Kern County: sites with utilities $36 non-waterfront / $40 waterfront in peak season (Mar 15-Oct 15), $24/$25 off-peak; no-utility sites $16-34; $2 off for seniors."),
 (11770, 12, 24, None, "Campsite (includes First Vehicle)\t$24.00", "Kern County: $24 a night in peak season (Mar 15-Oct 15), $12 off-peak, first vehicle included; no hookups."),
 (11728, 35, 35, None, "Individual campsites 1-45", "Yolo County: individual sites $35 a night; extra vehicle $10; online reservations."),
 (11729, 45, 55, 10, "Full Hookups (Water, Electric, and Sewer)", "Santa Barbara County: partial hookups $45 (Oct-Mar) / $50 (Apr-Sep), full hookups $50 / $55; $10 reservation fee."),
 (11733, 51, 53, None, "Full Hook Ups $53.00", "Ventura County: full hookups $53 a day peak season, $51 off season."),
 (11734, 25, 25, None, "$25 per night per single campsite", "Fresno County: $25 a night per site including the first vehicle ($9 seniors, free for veterans and active military)."),
 (11741, 53, 53, None, "RV campsites", SCC),
 (11795, 53, 53, None, "RV campsites", SCC),
 (12379, 47, 51, None, "RV Fees\t$51.00", "Ventura County: $51 a day peak season, $47 off season, per site."),
]
recs = [json.loads(l) for l in open("browser.jsonl")]
def hit(p, key):
    return key in (p.get("lines") or "")
out = []
for i, lo, hi, rf, key, note in ROWS:
    own = [p["url"] for r in recs if r["id"] == i for p in r["pages"] if hit(p, key)]
    other = [p["url"] for r in recs for p in r["pages"] if hit(p, key)]
    url = (own or other or [None])[0]
    assert url, i
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": url + " (browser; audit/price_research/local_ca_2026-10-15/browser.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
