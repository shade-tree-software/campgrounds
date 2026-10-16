"""GA local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_ga.py > findings_ga.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(4683, 40, 50, None, "Full Hookup RV Sites", "Carroll County (John Tanner Park): water and electric sites $40 a night, full hookup $50; senior rates on request."),
 (4687, 20, 20, None, "$20 per night", "Carroll County (McIntosh Reserve): camping $20 a night."),
 (4688, 65, 65, None, "$65+tax per night", "Oconee Springs Park: campsites with 30/50-amp and water $65 a night plus tax."),
 (4695, 28, 28, None, "RV Camping Fees: $28 per night", "Gordon County: RV sites with water and electricity $28 a night, first weekend in April to first weekend in November; tents $18."),
 (4699, 30, 35, None, "Full hook up", "Macon County: RV sites without sewer $30 a night, full hookup $35; tents $18."),
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
