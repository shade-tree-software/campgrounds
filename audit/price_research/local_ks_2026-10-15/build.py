"""KS local findings from ks_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY."""
import json
ROWS = [
 (2165, 15, 15, None, "are $15/night", "City of Altamont: camping slots $15 a night."),
 (2168, 25, 25, None, "$25.00 a night, year round", "City of Sterling: RV spaces $25 a night, tents $5."),
 (2170, 20, 20, None, "Overnight fee is $20.00", "City of Stockton: water and 50-amp sites $20 a night."),
 (2171, 15, 15, None, "Rate: $15 a night", "City of Phillipsburg: $15 a night, first come, first served."),
 (2172, 20, 20, None, "RV Space Rental is $20", "City of Pittsburg: RV spaces $20 a day."),
 (2173, 15, 15, None, "A fee of $15 per recreational vehicle", "City of Ulysses: $15 per RV a night for the utility hookups."),
 (2174, 20, 20, None, "$ 20.00 per Space, per night", "City of Lincoln Center: full hookups $20 a night, $125 a week."),
 (2178, 15, 15, None, "Electric hook up is $15.00", "City of Oxford: electric hookup $15 a day, primitive $3.50."),
 (2179, 15, 15, None, "RATE IS $15 PER NIGHT", "City of Washington: electric and water $15 a night."),
 (2180, 15, 15, None, "are available for rent at $15/night", "City of Minneapolis: $15 a night; 14 days in 60."),
 (2181, 20, 20, None, "$20.00 a day for a maximum", "City of Montezuma: full hookups $20 a day, no reservations; 14-day maximum."),
 (2183, 10, 10, None, "Fee is $10 per night", "City of Pratt: electric and water $10 a night; 7-night maximum."),
 (2185, 15, 15, None, "5 RV hookups, $15 per day", "City of Cottonwood Falls: 5 water-and-electric hookups $15 a day."),
 (2187, 20, 20, None, "RV hookups are available at Rocky Pond for $20", "City of Belleville: full hookups $20 a night, $125 a week."),
 (2188, 20, 25, None, "$20.00 PER NIGHT ($25.00", "City of Yates Center: $20 a night ($25 for the first night if reserved)."),
 (2192, 15, 15, None, "per day donation of $15", "Blue Rapids Chamber of Commerce: suggested donation $15 a day."),
 (2194, 16, 16, None, "Electrical sites are $16 per day", "Douglas County: electric sites $16 a day, non-electric $11; no reservations."),
 (2195, 15, 15, None, "Daily permit for Campsites A, B, C, & D", "City of Anthony: improved campsites $15 a day including electric; unimproved $5."),
 (2197, 0, 20, None, "There is no charge for the first 24 hours", "City of Chanute: free for the first 24 hours, then $20 a day; 10 days in 30."),
 (2203, 18, 18, None, "$18.00 nightly (as of January 1, 2024)", "City of Valley Falls: $18 a night (rate as of January 1, 2024)."),
 (2204, 20, 20, None, "$20.00 per night with electricity", "City of Liberal: 30/50-amp sites $20 a night, $5 more per extra air conditioner; non-electric $5."),
 (2205, 22, 42, None, "Water/Electric Only Waterfront RV Sites", "Shawnee County 2026 season: water and electric $22-24 a night, full hookup $38-42; tents $24."),
 (2206, 25, 25, None, "DAILY UTILITY FEE $15.00", "Horsethief Reservoir: camping $10 plus utility fee $15 a day; vehicle permit $5."),
 (2207, 20, 20, None, "$20/night - Camper sites with electricity", "City of Leavenworth: camper sites with electricity $20 a night."),
 (2237, 25, 25, None, "$25.00 per Day/Night", "City of Ellis: electric and water pull-throughs $25 a day, primitive $15; no reservations."),
]
pages = [json.loads(l) for l in open("ks_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_ks_2026-10-15/ks_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
