"""GA3 local findings from the browser pass (follow-up: county booking catalog read in the driver browser 2026-10-16, after the crawl), USD.
python3 -I build_ga3.py > findings_ga3.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(4667, 27, 30, None, "https://secure.rec1.com/GA/lake-tobesofkee-ga/catalog/index/5050606a78c1b36454b1e1e1eebb5413", "Macon-Bibb County (Lake Tobesofkee) booking catalog: RV sites $27 a night, sewer and waterfront RV sites $30; tent sites $23; lake admission may apply."),
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
    out.append({"id": i, "fees": f, "source": urls[0] + " (driver browser follow-up after the crawl), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
