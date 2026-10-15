"""CO local findings from co_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(2638, 35, 35, None, "Camping fee: $35 per night", "Boulder County: $35 a night, first come, first served."),
 (2643, 32.50, 40, None, "RV with 30 amp service", "Denver Mountain Parks: RV 30-amp $32.50 a night, 50-amp $35, with sewer $40; tents $23; one parking pass included."),
 (2649, 37, 58, None, "Water/Electric Back-In Sites: $44/night", "Town of Carbondale: electric only $37 a night, water and electric $44, full hookup $54 (back-in) to $58 (pull-through)."),
 (2655, 57, 69, None, "RV with Full Hookups | Nightly: $62-$67", "Town of Lyons: full hookups $62-67 a night in season, $64-69 on holidays, $57-62 off-season; tents $37-47; 2-night weekend minimum."),
 (2665, 35, 45, None, "Basic campsite: $35 per night", "City of Westminster: basic sites $35 a night, three electric sites $45."),
 (2668, 20, 20, None, "Rates: $20.00 per night", "Hinsdale County: $20 a night, no electricity; dump $20."),
]
pages = [json.loads(l) for l in open("co_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_co_2026-10-15/co_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
