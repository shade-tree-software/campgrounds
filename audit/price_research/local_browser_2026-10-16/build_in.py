"""IN local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_in.py > findings_in.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(1344, 30, 30, None, "RV per night with electric service: $30", "City of Fort Wayne (Johnny Appleseed): RV sites with electric $30 a night, $600 for 28 days."),
 (1348, 15, 38, None, "https://www.harrisoncountyparks.com/rates", "Harrison County Parks (Buffalo Trace): modern sites $15-38 a day, primitive $12-20; 2-night weekend minimum, 3 nights on holiday weekends."),
 (1351, 27, 37, 6, "AA (full hook-up) $37 a night", "Parke County (Rockville Lake): water/electric $27 a night, full hookup $37, primitive $17; $6 reservation fee and $7 vehicle fee once per stay."),
]
recs = {}
for l in open("browser.jsonl"):
    x = json.loads(l); recs[x["id"]] = x
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for p in recs[i]["pages"] if key in p.get("lines", "")]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-16."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_browser_2026-10-16/browser.jsonl), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
