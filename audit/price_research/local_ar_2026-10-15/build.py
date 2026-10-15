"""AR local findings from ar_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(5340, 19.64, 25.26, None, "30 AMP Hook Up is $", "City of Bull Shoals (tax included): 30-amp $19.64 a night, 50-amp $22.45, site 2 with sewer $25.26."),
 (5343, 25, 25, None, "$25.00/night or $125.00/week", "City of Hope: water and 30/50-amp $25 a night, $125 a week."),
 (5351, 20, 20, None, "Rental Rate is $20/night", "City of Paragould: $20 a night, seniors (60+) $15."),
]
pages = [json.loads(l) for l in open("ar_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_ar_2026-10-15/ar_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
