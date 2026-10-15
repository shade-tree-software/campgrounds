"""ME local findings from me_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(614, 17, 58, None, "Nightly Campsite Rates for 2026", "Town of Freeport 2026: RV sites $17-18 for residents, $52 inland and $58 waterfront for non-residents, plus sales tax."),
 (4180, 31, 37, None, "Daily Rates Tent Sites: $24.00", "2026: electric only $31 a day, electric and water $34, full $37; tents $24."),
 (4181, 25, 25, None, "Campsite Rate per Day Electrical Amps", "Town of Portage Lake: 20/30-amp sites $25 a day plus 9% tax."),
 (4183, 25, 35, None, "First Night Rental", "Town of Madawaska: $35 the first night, $25 each additional, $125 a week."),
]
pages = [json.loads(l) for l in open("me_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_me_2026-10-15/me_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
