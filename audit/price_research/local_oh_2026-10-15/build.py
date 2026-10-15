"""OH local findings from oh_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(1232, 38, 47.75, None, "46 Sites $38/night to $47.75/night", "Great Parks of Hamilton County: 30-amp electric sites $38-47.75 a night."),
 (1234, 33, 38.50, None, "Electric sites: $33/week night", "Summit Metro Parks, May-October: electric $33 weeknights, $38.50 weekends and holidays; non-electric $26.25-31.50."),
 (1235, 40, 40, None, "2026 Non-Fair Camping Rates", "Darke County Fair 2026: $40 a night outside the fair, with 50-amp, water and sewer."),
 (1241, 45, 45, None, "Daily ………….……….……….………… $45.00", "Village of North Kingsville 2026: $45 a day, $200 a week."),
 (1246, 35, 35, None, "Year-Round Camping: $35.00/night", "Washington County Fair: $35 a night, $125 a week."),
 (1251, 40, 40, None, "Electric Sites – All $40.00", "Coshocton County 2026: electric sites $40."),
]
pages = [json.loads(l) for l in open("oh_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_oh_2026-10-15/oh_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
