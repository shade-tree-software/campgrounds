"""LA local findings from la_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(6908, 43.80, 49.56, None, "RV Camping (full hook-ups)", "Cypress Black Bayou: partial hookups $43.80 a night, full hookups $49.56, tents $31.12."),
 (6913, 11, 11, None, "Rates: $11/Day", "City of Opelousas: $11 a day; 67 sites."),
 (6915, 25, 30, None, "Traveler Trailer or Tent $25/night", "Rapides Parish Police Jury: trailer or tent with electricity $25 a night, with sewer $30; no electricity $9."),
 (6919, 45, 45, None, "a day for full hook up", "Full hookup $45 a day, $200 a week; rallies $35 a day without sewer."),
 (6931, 28, 28, None, "The rental fee is $28.00 per pad per night", "Lafayette Consolidated Government: $28 a pad a night."),
]
pages = [json.loads(l) for l in open("la_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_la_2026-10-15/la_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
