"""SD local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_sd.py > findings_sd.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(5845, 42, 63, 3, "Motor Homes, Travel Trailers, 5th Wheels", "City of Spearfish 2027 fees: RV primitive sites $42 a night, full hookup (30/50-amp) $52, premium $63; tents $26; off-season (October and January-April) $21 plus a $3 booking fee."),
 (5856, 10, 10, None, "Camping fee of $10 per night", "City of Vermillion: $10 a night, paid before the first night."),
 (5869, 15, 15, None, "The cost is $15 per night", "City of Lake Preston: $15 a night, $400 a month."),
 (5870, 30, 30, None, "Campers- $30.00/night", "City of Groton: campers $30 a night, tents $10."),
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
