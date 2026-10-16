"""ND2 local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_nd2.py > findings_nd2.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(5961, 35, 35, None, "Nightly camping $35", "Grand Forks County (Larimore Dam): $35 a night, $175 a week."),
 (5964, 20, 30, None, "1 night $30.00 (full service)", "Glen Ullin Park District: electric only $20 a night, electric and water $25, full service $30; tents $6."),
 (5975, 40, 40, None, "Overnight RV Camping $40.00", "Grand Forks County (Fordville Dam): overnight RV camping $40, $150 a week; tents $10-20."),
 (6006, 20, 25, None, "$20 per day for electrical sites", "Cass County: electrical sites $20 a day, full hookup $25; tents $10."),
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
