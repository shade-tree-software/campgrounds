"""VA local findings from va_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(430, 32, 37, None, "Regular Campsite (up to 6 people, two tents)", "Fairfax County Park Authority: regular campsites (no electric) $32 weekdays, $37 weekends and holidays; 9% county occupancy tax from May 1, 2026."),
 (431, 40, 55, None, "Regular Campsite | 20/30 Amp", "Fairfax County Park Authority: 20/30-amp sites $40 weekdays, $44 weekends; 50-amp $50/$55; no electric $32/$37; 9% county occupancy tax from May 1, 2026."),
 (531, 20, 20, None, "Each campsite is $20 a night", "City of Norton: $20 a night, first come, first served."),
]
pages = [json.loads(l) for l in open("va_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_va_2026-10-15/va_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
