"""NB local findings from nb_pages.jsonl (operators' own pages, read 2026-10-15), CAD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(12868, 35, 35, None, "Rates (HST not included)", "Village of Belledune: serviced $35 a day, non-serviced $30, HST extra."),
 (12870, 64, 70, None, "$64/Night Taxes Included", "Kiwanis: full hookup pull-throughs $64-70 a night, taxes included."),
]
pages = [json.loads(l) for l in open("nb_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_nb_2026-10-15/nb_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
