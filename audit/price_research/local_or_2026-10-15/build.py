"""OR local findings from or_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY."""
import json
COL = "Columbia County: full hookups $31 a night (Nov-Apr) / $33 (May-Oct), water and electric $28 / $30, no hookups $20 / $23."
MAL = "Malheur County: $25 a site a night including electricity and dumping."
ROWS = [
 (11006, 50, 50, None, "Daily rates", "Port of Arlington: full hookups $50 a day, $200 a week; tent/dry camp $20."),
 (11007, 28, 28, 8, "Campsites are $28/night", "Jackson County: campsites $28 a night, no hookups; $8 online reservation fee."),
 (11011, 30, 40, None, "$40/night Full Hookups", "Jackson County: full hookups $40 a night, water and electric $35, no hookups $30."),
 (11018, 40, 40, None, "$40.00 per night", "Gilliam County: 17 full-hookup sites $40 a night, $200 a week; tents $20."),
 (11022, 10, 10, None, "dry camping for $10", "City of Coquille: dry camping $10 a night."),
 (11024, 40, 40, None, "14 RV Campsites available at $40", "City of Dufur: 14 RV sites $40 a night, tents $25."),
 (11025, 26, 26, None, "starting at $26", "Fort Henrietta RV Park (City of Echo): RVs from $26 a night, tents and pull-throughs from $20."),
 (11031, 25, 30, None, "RV Space $30.00", "Wheeler County: RV space $30 a night, dry camp $25, tents $15."),
 (11035, 58, 64, 10, "Daily $ 64", "Port of Garibaldi (rates effective March 1, 2026): RVs $64 a day, $58 off season; $10 reservation fee."),
 (11039, 25, 25, None, "Campground overview $25", "Oregon Metro: $25 a site a night, one vehicle included."),
 (11043, 30, 40, None, "$40.00 - Riverside campsites", "Hood River County: riverside sites $40, other sites $30."),
 (11063, 30, 50, None, "$35.00 - Partial Hookup", "Hood River County: riverside sites $50, partial hookup $35, other sites $30."),
 (11044, 30, 30, None, "Campsites (includes 1 vehicle): $30", "Jackson County: campsites $30 a night."),
 (11045, 45, 45, None, "RV Park $45 nightly", "Grant County Fairgrounds: full hookups $45 a night including room tax; tents $10."),
 (11059, 35, 35, None, "$35 a night for RV sites", "Umatilla County: 30-amp RV sites $35 a night, tents $20."),
 (11062, 15, 40, None, "Nightly rates range from $15 to $40", "Sherman County: nightly rates $15-40."),
 (11064, 35, 35, None, "RV Full Hookups - $35", "City of Myrtle Creek: full hookups $35 a night."),
 (11067, 25, 25, None, "The camping fees are $25", MAL),
 (11182, 25, 25, None, "The camping fees are $25", MAL),
 (11068, 30, 30, None, "RV WITH WATER AND ELECTRIC", "Malheur County Fair: RV with water and electric $30 a night, dry $15."),
 (11076, 62, 62, None, "30 & 50 Amp sites: $62", "Deschutes County Expo: full-service 30/50-amp sites $62 a night plus 10.5% tax; $3.65 transaction fee."),
 (11081, 28, 33, None, "Campsite with Full Hookups", COL),
 (11184, 28, 33, None, "Campsite with Full Hookups", COL),
 (11185, 28, 33, None, "Campsite with Full Hookups", COL),
 (11086, 20, 20, None, "Only $20.00 a night", "Port of Tillamook Bay 2026: $20 a night, first come, first served; 14-day maximum."),
 (11091, 40, 40, None, "$40*per night", "Port of Columbia County: $40 a night (effective July 1, 2025); 14-night maximum."),
 (11094, 35, 45, None, "Rates range from $35 to $45", "Salmon Harbor (Douglas County): sites $35-45 a night."),
 (11095, 30, 55, None, "Rates range from $30", "Salmon Harbor (Douglas County): sites $30-55 a night."),
 (11099, 42, 42, None, "$42.00 per site", "Benton County: 13 electric RV sites $42, tents $30."),
 (11101, 43, 43, None, "RV Sites are $43/night", "Jackson County: full-hookup RV sites $43 a night; Oak Slope no-hookup sites $30."),
 (11112, 38, 48, None, "Full Hook-Up: $48", "Benton County Event Center: full hookup $48 a day, partial $38."),
 (11133, 26, 30, None, "Partial Hookup (water and power)", "Willow Creek Park District 2026: water and power $26 a day, full hookup $30, tents $10."),
 (11166, 25, 25, None, "RV / Tent Site $25", "Crook County Parks & Rec: RV/tent sites $25 a night."),
 (11183, 35, 35, None, "Full hook-up sites: $35", "City of Vernonia: full hookups $35 a night, tents $22."),
]
pages = [json.loads(l) for l in open("or_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_or_2026-10-15/or_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
