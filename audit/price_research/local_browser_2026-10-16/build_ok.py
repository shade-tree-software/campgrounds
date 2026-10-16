"""OK local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_ok.py > findings_ok.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(6615, 24, 24, None, "RV sites with electric and water $24", "City of Okmulgee: RV sites with electric and water $24 a night; tents $15."),
 (6620, 24, 24, None, "RV sites with electric and water $24", "City of Okmulgee: RV sites with electric and water $24 a night; tents $15."),
 (6728, 25, 25, None, "RV Hookups per day– $25.00", "City of Chandler (Bell Cow Lake): RV hookups $25 a day, seniors $18."),
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
