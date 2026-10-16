"""IA local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_ia.py > findings_ia.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(2966, 15, 20, None, "$15 per night or $375 per month", "City of Audubon: electric/water sites $15 a night, full hookup $20."),
 (2986, 22, 25, None, "Full Hook-Up camping sites", "City of Cherokee: water and electric sites $22 a night, full hookup $25; tents $10; 14-day maximum."),
 (3216, 10, 10, None, "for $10.00 per night", "City of Perry: $10 a night with electric hookups and water; 5-day maximum."),
 (3251, 15, 15, None, "With electrical service", "City of Fort Madison (Rodeo Park): $15 a night with electric, $8 without; self-registration, first come, first served."),
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
