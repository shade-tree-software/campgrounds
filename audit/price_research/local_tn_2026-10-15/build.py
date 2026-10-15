"""TN local findings from tn_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(4465, 30, 35, None, "40 short-term RV and Tent sites", "Anderson County: water and 30/50-amp sites $30-35 a night plus taxes and fees."),
]
pages = [json.loads(l) for l in open("tn_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_tn_2026-10-15/tn_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
