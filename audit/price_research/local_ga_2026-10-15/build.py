"""GA local findings from ga_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
 (718, 30, 40, None, "Camping Rates $30 - $40", "Elbert County (Bobby Brown Park): camping $30-40 a night."),
 (4518, 30, 40, None, "Camping Rates $30 - $40", "Elbert County (Bobby Brown Park): camping $30-40 a night."),
 (725, 30, 30, None, "RV rental fee: $30/night", "City of Fitzgerald: RV sites $30 a night, tents $10."),
 (4596, 25, 33, 15, "RV Full Hookup", "Chehaw Park Authority: RV regular hookup $25 a day, full hookup $33; tents $20; $15 nonrefundable reservation fee."),
 (4664, 25, 25, None, "Regular (see note)", "Columbia County: camping $25 a night, seniors (55+) $22, primitive $15 a tent."),
 (4680, 21, 21, None, "Nightly Rate: $21", "Appling County: RV sites $21 a night, $105 a week."),
 (4685, 40, 50, None, "Full Hookup RV - $50 per night", "Carroll County: water and electric $40 a night, full hookup $50; tents and pop-ups $25; $5 daily parking per vehicle."),
]
pages = [json.loads(l) for l in open("ga_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_ga_2026-10-15/ga_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))

