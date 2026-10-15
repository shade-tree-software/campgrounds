"""ID local findings from id_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(9769, 30, 30, None, "R.V. Spaces- $30.00 a night", "Twin Falls County: RV spaces $30 a night, tents $15."),
 (9771, 35, 35, None, "$35.00 a night", "Twin Falls County: 25 RV spots $35 a night, no tents; 15-day limit."),
 (9772, 45, 45, None, "Full Hookup – Nightly", "Twin Falls County Fair: full hookup $45 a night including tax, dry camping $25."),
 (9777, 53, 55, None, "Full Hookup Sites as low as $53/Night", "Concessionaire: full hookup sites from $53 a night, $55 for 36-ft-plus pull-throughs."),
 (9784, 40, 40, None, "$40 per Camper, RV or Tent Per Night", "City of Idaho Falls: $40 a night per camper, RV or tent; no hookups."),
 (9786, 40, 40, None, "Single RV Campsites, nightly: $40", "Jefferson County: single RV sites $40 a night, double $50, tents $25."),
 (9787, 40, 40, None, "it is $40 per night", "City of Parma: overnight parking including tents $40 a night; 7 days in 30."),
 (9788, 10, 10, None, "Camping fee required $10 nightly", "Madison County: $10 a night or 5 nights for $40; no reservations."),
 (9789, 20, 20, None, "$20 per Day due at check-in", "Gem County: $20 a day; no reservations, 7-day maximum."),
 (9790, 25, 25, None, "Fee is $25.00 per day", "City of Emmett: $25 a day, first come, first served; 10-day maximum."),
 (9793, 44, 44, None, "$44.00/night for a pull-through site", "City of Leadore: pull-through with water and electric $44 a night, without $27.50."),
 (9795, 26, 26, None, "DAILY = $26.00", "City of Kendrick: $26 a day, $130 a week."),
 (9797, 45, 45, None, "Regular: $45/Night", "City of Troy: $45 a night, seniors $40."),
 (9799, 25, 25, None, "RV area with 10 pull-through sites", "Latah County: 10 pull-through sites with power and water $25 a night, primitive $15; no reservations."),
 (9801, 20, 20, None, "$20 per night for hook up", "Benewah County Fair: hookup sites $20 a night, dry $15; exhibitors only during the fair."),
 (9826, 30, 30, None, "$30 full hookups", "Full hookups $30 a night, tent and dry camping $20."),
]
pages = [json.loads(l) for l in open("id_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_id_2026-10-15/id_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
