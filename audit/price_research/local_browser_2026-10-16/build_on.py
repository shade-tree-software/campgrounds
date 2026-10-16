"""ON local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), CAD.
python3 -I build_on.py > findings_on.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(8270, 59, 74, 16, "https://thamesriver.on.ca/parks-recreation-natural-areas/fees/", "Upper Thames River Conservation Authority 2026 (May 1 - October 17): 30/15-amp sites C$59 a night off-peak, C$64 peak (June 19 - September 7 and long weekends); 50-amp C$69/C$74; non-electric C$49-54; C$16 reservation fee."),
 (8268, 59, 74, 16, "https://thamesriver.on.ca/parks-recreation-natural-areas/fees/", "Upper Thames River Conservation Authority 2026 (May 1 - October 17): 30/15-amp sites C$59 a night off-peak, C$64 peak (June 19 - September 7 and long weekends); 50-amp C$69/C$74; non-electric C$49-54; C$16 reservation fee."),
 (8301, 10, 10, None, "A Daily Camping Pass (Trailer)", "Ontario Steelheaders (Denny's Dam): daily camping pass for a trailer C$10, includes a day parking pass with overnight privileges."),
 (12670, 63.25, 70.25, None, "30-amp service", "Lower Beverley Lake Park: 30-amp sites C$63.25 a night, 50-amp C$70.25; non-serviced C$38.25."),
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
