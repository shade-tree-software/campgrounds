"""FL local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_fl.py > findings_fl.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(4841, 75, 75, None, "Rates (effective October 2024)", "Sarasota County (rates effective October 2024): $75 a night; 10% off stays of 21-30 nights."),
 (4842, 22.32, 25.89, None, "$22.32/night", "St. Lucie County, plus tax: full sites $22.32 a night, $25.89 November 1 - April 30; tent sites $19.64."),
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
