"""AZ local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_az.py > findings_az.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(11449, 52, 52, None, "DAILY $52.00", "Pima County Fairgrounds RV park: full 30/50-amp $52 a day, $312 a week; dry camp $30."),
 (11459, 15, 15, None, "$15.00 (Per Night)", "City of Winslow (McHood Park): overnight camping $15 a night, first come, first served."),
 (11463, 30.89, 30.89, None, "Daily – $30.89", "City of Douglas: RV park $30.89 a day plus tax, $154.44 a week."),
 (11465, 25, 25, None, "$25 RV Hookups per night", "Graham County: RV hookups $25 a night."),
 (11467, 25, 25, None, "Campsite $25.00 per site/ per night", "City of Prescott (Watson Lake): $25 a site a night."),
 (11472, 20, 20, None, "Fee: $20/night", "City of Buckeye (Skyline): $20 a night."),
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
