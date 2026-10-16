"""OR local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_or.py > findings_or.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(11009, 42, 60, 12.25, "Camping – partial utility (H20/elec.) sites", "Clackamas County: partial utility (water/electric) sites $42 a night, full utility $48.25; non-Oregon residents $52/$60; standard no-utility $31.75; $12.25 non-refundable reservation fee."),
 (11026, 42, 60, 12.25, "Camping – partial utility (H20/elec.) sites", "Clackamas County: partial utility (water/electric) sites $42 a night, full utility $48.25; non-Oregon residents $52/$60; standard no-utility $31.75; $12.25 non-refundable reservation fee."),
 (11061, 42, 60, 12.25, "Camping – partial utility (H20/elec.) sites", "Clackamas County: partial utility (water/electric) sites $42 a night, full utility $48.25; non-Oregon residents $52/$60; standard no-utility $31.75; $12.25 non-refundable reservation fee."),
 (11015, 45, 47, 8, "Standard Sites (60'x12')", "Jackson County: standard sites $45 a night, premium $47; $8 online reservation fee ($10 by phone)."),
 (11050, 30, 45, 10, "https://www.currycountyor.gov/departments/parks/rates.php", "Curry County: RV sites with electric and water $45 a day, $30 off-season (October 1 - April 30); non-electric $30/$20; $10 online reservation fee."),
 (11077, 25, 25, 10, "A $25/day RV camping fee", "Baker County: RV with electric and water hookups $25 a day plus county and state lodging tax, without $20; $10 reservation fee."),
 (11090, 30, 40, None, "Water and Power - $30/night", "Wasco County (Hunt Park): water and power $30 a night, with sewer $40; tents $15."),
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
