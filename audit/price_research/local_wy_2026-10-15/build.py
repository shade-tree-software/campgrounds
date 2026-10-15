"""WY local findings from wy_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(6515, 25, 25, None, "Fee is $25 per day", "City of Torrington: 50-amp and water $25 a day; 10-day limit."),
 (6517, 40, 40, None, "Spaces are $40/night", "Albany County: $40 a night, 2-week maximum."),
 (6523, 35, 35, None, "In season rate: $35 a night", "Park County: full hookups $35 a night in season plus lodging and sales tax."),
 (6535, 45, 45, None, "Daily rate is $45 plus tax", "Sweetwater Events Complex: $45 a day plus tax."),
 (6544, 20, 20, None, "Fees are $20 per night for sites with electricity", "Johnson County: electric sites $20 a night, others $15; honor system."),
]
pages = [json.loads(l) for l in open("wy_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_wy_2026-10-15/wy_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
