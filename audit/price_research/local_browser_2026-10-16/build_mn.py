"""MN local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_mn.py > findings_mn.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(5582, 40, 40, None, "RV Sites: $40 per night", "Sylvan Park: RV sites $40 a night, $200 a week; tents $25."),
 (5617, 25, 25, None, "$25 per night per unit", "Cedar Hanson County Park: electrical camping $25 a night, primitive $15."),
 (5634, 30, 30, None, "$30 per day/hook-ups", "Glenn Johnson Memorial Park: hookups $30 a day, $175 a week; no hookups $15."),
 (5658, 43.15, 43.15, None, "Improved site with 20, 30 or 50 amps", "City of Mankato (Land of Memories): improved sites with 20/30/50-amp $43.15 a day; tent sites $26.98."),
 (5693, 33, 33, None, "$33.00", "Stonehill Regional Park: electric and water $33 a day; overflow electric only $23."),
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
