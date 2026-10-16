"""BC local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), CAD.
python3 -I build_bc.py > findings_bc.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(8579, 35, 35, None, "$35 per night", "Metro Vancouver (Edgewater Bar): unserviced sites $35 a night, seniors and disability permit holders $32; $12 per extra vehicle; March 1 - October 31."),
 (8589, 40, 40, None, "Serviced Sites # 3-10", "Village of New Denver 2026, GST extra: serviced sites (30-amp and water) $40 a night; regular $30, lakeside $50."),
 (8594, 44, 56, None, "50 amp/water - $56", "Golden Municipal Campground: 20-amp $44, 30-amp $47, 30-amp/water $53, 50-amp/water $56 a night for 2 adults; non-serviced RV sites $41-43."),
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
