"""LA local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_la.py > findings_la.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(6907, 12, 12, None, "RV campsites with electricity can be rented for $12 per night", "White Oak Park: RV sites with electricity $12 a night."),
 (6937, 20, 40, None, "Peak Season RV Rates", "Lake End Park, before taxes: April 1 - October 31 $20 a night Sunday-Wednesday, $40 Thursday-Saturday; otherwise $40 a night; $8 vehicle entry in gatehouse season."),
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
