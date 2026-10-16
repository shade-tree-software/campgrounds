"""NS2 local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), CAD.
python3 -I build_ns2.py > findings_ns2.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(12954, 58, 65, None, "30 Amp Power & Water Pull Thru", "Shubie Campground: 30-amp power and water C$58 a night, pull-through C$60, 50-amp pull-through C$65; 15-amp sites C$48-53; 3-way pump-out sites C$67+ for stays over 3 days."),
]
recs = {}
for l in open("browser.jsonl"):
    x = json.loads(l); recs[x["id"]] = x
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for p in recs[i]["pages"] if key in p.get("lines", "")]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-16."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_browser_2026-10-16/browser.jsonl), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
