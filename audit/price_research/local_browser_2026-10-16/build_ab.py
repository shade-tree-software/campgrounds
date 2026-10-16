"""AB local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), CAD.
python3 -I build_ab.py > findings_ab.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(8949, 26, 32, None, "$26 per day", "MD of Wainwright (Arm Lake), GST included: power only C$26 a day, power and water C$28, full service C$32; unserviced C$15."),
 (9098, 39, 55, 10, "15 amp power/water $39.00", "Devon Lions 2026 (same as 2025): power/water C$39-44, power/water/sewer C$48-55, unserviced C$31; C$10 non-refundable reservation fee; 2-night weekend minimum."),
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
