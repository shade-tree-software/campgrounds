"""NL local findings from nl_pages.jsonl (operators' own pages, read 2026-10-15), CAD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(13022, 35, 35, None, "29 Serviced Sites (Electricity & Water)", "Town of Springdale: electricity and water $35 a day, $225 a week."),
 (13049, 38, 45, None, "Fully Serviced Lot | $45.00", "Kinsmen: semi-serviced $38 (tax included), fully serviced $45, non-serviced $30."),
 (13056, 44.78, 49.56, 2, "Full Service Site (FS)", "Pippy Park: full service $44.78-49.56 a night plus tax; $2 reservation fee."),
]
pages = [json.loads(l) for l in open("nl_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_nl_2026-10-15/nl_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
