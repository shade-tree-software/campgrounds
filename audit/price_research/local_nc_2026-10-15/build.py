"""NC local findings from nc_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(4319, 25, 25, None, "Trailer/RV Sites (water and electric included)", "Guilford County: trailer/RV sites with water and electric $25 a night for five people; tents $15."),
 (4321, 35, 35, None, "The nightly rate is $35", "Winston-Salem Fairgrounds: $35 a night, first come, first served."),
 (4327, 35, 40, None, "RV Sites $35 (R) $40 (NR)", "Mecklenburg County: RV sites $35 for county residents, $40 non-residents."),
 (4328, 30, 30, None, "($30/night)", "City of Kinston: 23 full hookup sites $30 a night, tents $15."),
 (4330, 45, 45, None, "2026: All sites are $45/night", "Forsyth County (Tanglewood): all sites $45 a night in 2026, $50 in 2027."),
]
pages = [json.loads(l) for l in open("nc_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_nc_2026-10-15/nc_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
