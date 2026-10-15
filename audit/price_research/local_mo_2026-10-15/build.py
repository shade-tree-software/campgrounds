"""MO local findings from mo_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(1938, 40, 40, 2, "Electric Sites (50 amp)", "Clay County: 50-amp electric and water/electric sites $40 a day, unimproved $22; $2 reservation fee."),
 (1939, 40, 40, 2, "Electric Sites (50 amp)", "Clay County: 50-amp electric and water/electric sites $40 a day, unimproved $22; $2 reservation fee."),
 (1940, 40, 40, None, "Full service 20, 30, or 50-amp site", "City of Smithville: full service sites $40 a day, tents $22."),
 (1943, 40, 40, None, "20-50 amp electrical services", "City of Canton: electric pads $40 per 24-hour permit."),
 (1945, 20, 20, None, "The campground has a fee of $20.00 a night", "City of Brookfield: $20 a night with 30/50-amp electricity."),
 (1947, 25, 25, None, "30 or 50 AMP Electric Hook-Up S", "City of Shelbina: 30/50-amp electric sites $25, primitive $10."),
 (1948, 35, 35, None, "RV CAMPGROUNDS $ 35 / DAY", "Jefferson City Parks: RV sites $35 a day."),
 (1949, 55, 58, None, "BACK-IN 50/30 AMP SITES", "City of Branson: back-in 50/30-amp sites $55 a night, pull-throughs $58."),
 (1950, 0, 20, None, "The first night you stay with us is free", "City of Lamar: first night free, then $20 a night; 7-day maximum."),
 (1951, 20, 22, None, "WATER, SEWER, & ELECTRIC - $22.00", "City of Osceola: water and electric $20 a night, full hookup $22, tents $15."),
 (1953, 30, 30, None, "our RV sites are $30.00 per night", "RV sites with water and 30/50-amp $30 a night, tents $15."),
 (1955, 10, 20, None, "$10 per day per site for RVs and Campers", "City of Mexico: $10 a day for city residents, $20 non-residents; no reservations."),
 (1956, 25, 25, None, "$25.00 per night which includes electricity", "City of Neosho: $25 a night including electricity, water and dump station."),
 (1957, 30, 45, None, "rates are $35 per weeknight", "City of Lawson: March-October $35 Sunday-Thursday, $45 Friday-Saturday; $30 November-February."),
]
pages = [json.loads(l) for l in open("mo_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_mo_2026-10-15/mo_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
