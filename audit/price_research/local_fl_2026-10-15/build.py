"""FL local findings from fl_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(14, 60, 80, None, "Daily: $80 + tax", "Miami-Dade County: $80 a night plus tax November-March, $60 April-October; tents $25."),
 (4816, 20, 20, None, "Fees : Camping: $20", "City of Sopchoppy: camping $20."),
 (4820, 18, 20.25, None, "Non-Escambia County residents: $20.25/day", "Escambia County: $18 a day for county residents, $20.25 for non-residents; senior/disabled discounts."),
 (4828, 40, 40, None, "RV- $40.00 per night", "Volusia County: RVs $40 a night including power, plus tax; tents $25."),
 (4843, 24, 24, None, "Regular rate | $24 per night", "Hillsborough County: $24 a night, $18 for adults 55+, $12 for resident adults 65+."),
 (4846, 24, 24, None, "Regular rate | $24 per night", "Hillsborough County: $24 a night, $18 for adults 55+, $12 for resident adults 65+."),
 (4847, 24, 24, None, "Regular rate | $24 per night", "Hillsborough County: $24 a night, $18 for adults 55+, $12 for resident adults 65+."),
 (4848, 35, 35, None, "Electric sites 27-30 are $35/night", "Indian River County: electric sites $35 a night, primitive $25."),
]
pages = [json.loads(l) for l in open("fl_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_fl_2026-10-15/fl_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
