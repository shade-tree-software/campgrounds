"""MT local findings from mt_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(6124, 25, 40, None, "$40 per night – RV with full hookups", "Chouteau County Fair: RV with water or electric $30, both $35, full hookups $40; $25 for the lowest RV tier."),
 (6125, 15, 15, None, "Day Permit: $15 per day", "Hill County (Beaver Creek Park): camping day permit $15."),
 (6134, 23, 23, None, "RV spots with electricity are only $23", "City of Harlowton: RV spots with electricity $23, without $17; no water or sewer."),
 (6157, 40, 40, None, "RV with hookups is $40/night", "Great Northern Fair: RV with hookups $40 a night, $225 a week; dry camping and tents $20."),
]
pages = [json.loads(l) for l in open("mt_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_mt_2026-10-15/mt_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
