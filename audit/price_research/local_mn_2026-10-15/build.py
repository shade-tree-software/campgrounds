"""MN local findings from mn_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY."""
import json
ANOKA = "Anoka County Parks: 30-amp sites $40 a night, 50-amp $45, rustic $30; 7 nights in 30; vehicle permit required."
WASH = "Washington County: 20/30-amp sites $35 a night, 50-amp with water $45, with water and sewer $50, rustic $30; $6 off in October."
OLM = "Olmsted County: electric sites $35 a night, non-electric $25."
LINC = "Lincoln County Parks: overnight camping with electricity $30 a night, without $25."
WRIGHT = "Wright County: non-resident electric sites $40 a night ($32 resident)"
ROWS = [
 (5513, 33, 37, 8.25, "per site with 30 amp", "Three Rivers Parks: 30-amp sites $33 a night, 50/30-amp $37, non-electric $25 (tax included); $8.25 reservation fee."),
 (5519, 40, 45, None, "30 amp sites", ANOKA),
 (5679, 40, 45, None, "30 amp sites", ANOKA),
 (5523, 35, 35, None, "Cost $35 per night", OLM),
 (5555, 35, 35, None, "Cost $35 per night", OLM),
 (5524, 30, 35, None, "Electric/Water/Sewer, 30AMP $30.00", "City of Chisholm: full hookups 30-amp $30 plus tax a night, 50-amp $35; tents $25."),
 (5529, 30, 30, None, "currently $30", "City of Eveleth: campsite rental $30 a day, first day paid when reserving."),
 (5542, 35, 50, None, "20 or 30 amp", WASH),
 (5691, 35, 50, None, "20 or 30 amp", WASH),
 (5543, 35, 45, None, "Trailside Camping", "City of Hendricks 2026: trailside sites $35 a night, lakeside full hookups $45; tents $20."),
 (5551, 25, 25, None, "Rates: $25.00 per night", "City of Stephen: $25 a night plus 6.875% sales tax, $150 a week; tents without electricity $15."),
 (5552, 33, 33, None, "RV Sites – $33/night", "City of Glencoe: RV sites $33 a night, tents $22; May 8 - October 6."),
 (5559, 25, 25, None, "$25/night", "Plum Creek Park (Redwood County): RV sites with 30/50-amp, no water or sewer, $25 a night; non-electric $20."),
 (5588, 40, 40, None, "Hook-up Site | $40.00", "Wagner Park (Barnesville): hookup sites $40 a night including tax; tents $25."),
 (5596, 25, 25, None, "It costs $25 a night", "City of Adams: 14 water-and-electric sites $25 a night, honor-system envelopes; first come, first served."),
 (5597, 35, 40, None, "30-Amp Electric (with water) = $35", "City of Adrian 2026: 30-amp with water $35 a night, with sewer $36, 50-amp $38-40; tents $22."),
 (5598, 63, 63, None, "RV | Daily: $63", "Akeley City Campground: RV $63 a day, $345 a week; tents $40."),
 (5599, 28, 28, None, "Fee is $28", "City of Redwood Falls: 50-amp electric sites $28 plus tax; tents $15; 5-night limit."),
 (5602, 35, 35, None, "Hookup Sites Number", "City of Appleton 2026: hookup sites $35 a night; tents $25."),
 (5604, 35, 35, None, "RV Campsites: $35", "City of Bagley: RV sites $35 a night, tents $20."),
 (5605, 50, 55, None, "Full Hookup sites are $55", "City of Glenwood: full hookup $55 a night, water and electric $50, tents $35 (camping closed for the rest of 2026; 2027 bookings open April 1)."),
 (5609, 30, 30, None, "Camping: $30.00 per night", "Aitkin County: $30 a night per site."),
 (5610, 40, 40, None, "Electric Campsite (50 amp service/Water)", WRIGHT + "; full-service sites $35 resident."),
 (5622, 40, 43, 6, "Full service campsite", WRIGHT + ", full service $43 ($35); non-electric $28; $6 reservation fee."),
 (5687, 40, 40, 6, "Electric campsite", WRIGHT + "; $6 reservation fee."),
 (5611, 44.15, 44.15, None, "44.15", "City of Big Falls: $44.15 a night including tax and fees; 7th night free."),
 (5613, 25, 25, None, "Campers: $25.00", "Big Stone County: campers $25 plus tax a day, $150 a week; tents $10."),
 (5618, 40, 60, None, "RV CAMPSITES", "Cedar Lake Memorial Park: RV sites $40 a day, $60 on holidays (3-day minimum); tents $25."),
 (5619, 35, 40, None, "Camp Site 1-9", "City of Crookston: full hookups $35 a day (sites 1-9, 15-19) or $40 (sites 10-14); tents $20."),
 (5621, 50, 50, 8.25, "$50 per RV site", "Three Rivers Parks: RV sites $50 a day, campsites $20, plus sales tax; $8.25 reservation fee."),
 (5625, 50, 50, None, "With water/electric : $50", "Dakota County Fair: water and electric $50 a day, $40 without, tax included; two-night minimum."),
 (5629, 30, 40, None, "Lakeshore: $40", "City of Hoyt Lakes 2026: electric sites $40 lakeshore, $30 non-lakeshore (Apr 24 - Sep 21); off-season $18, first come."),
 (5631, 20, 20, None, "$20 per night", "City of Fosston: 11 electric sites $20 a night; first come, first served."),
 (5632, 40, 40, None, "Daily Price - $40", "Freeborn County Fair: non-fair camping $40 a day, $240 a week; mid-April to mid-October."),
 (5633, 30, 30, None, "DAILY $30", "City of Hallock: $30 a day, $125 a week; 30/50-amp; call City Hall to book."),
 (5635, 30, 30, None, "CAMPERS | $30", "City of Harmony: campers $30 a night, tents $15; payment box, first come, first served."),
 (5636, 30, 31, None, "RV Sites with Electricity (30 amp) & Water: $31", "Embarrass Township: 30-amp and water $31 a day by card, $30 cash or check; tents $20-21."),
 (5638, 38, 53, None, "Electric Hook-up", "City of Starbuck 2026: electric $38 a night, full hookup $53; tents $25."),
 (5639, 30, 30, None, "Electricity $30/night", LINC),
 (5672, 30, 30, None, "Electricity $30/night", LINC),
 (5641, 37, 51, None, "Rates for our sites range", "HooDoo Point (City of Tower): $37 a night for non-lakeside primitive sites up to $51 for lakeside water and electric."),
 (5643, 35, 35, None, "Standard Rate is $35", "City of Mountain Lake: $35 a night, first come, first served."),
 (5645, 20, 20, None, "Camping: $20.00 per night", "Aitkin County: $20 a night per site, no electricity."),
 (5652, 22, 24, 8.25, "Daily Rates $22", "Three Rivers Parks: $22 a site (tax included), $24 for site 57; no hookups; $8.25 reservation fee."),
 (5654, 25, 25, None, "Trailer Camping: $25", "Brown County: trailer camping $25 a site, tents $10."),
 (5655, 45, 45, None, "Electric RV site $45", "Meeker County: electric RV sites $45 plus tax a night (no water or sewer at sites); tents $25."),
 (5657, 30, 35, None, "Non sewer site: $30", "City of Litchfield: water and electric $30 plus tax a night, with sewer $35; 35-ft maximum; 3% card fee."),
 (5660, 33.17, 33.17, None, "Overnite $30.90", "City of Littlefork: water and electric $30.90 + tax = $33.17 a night; booked through Campspot."),
 (5665, 10, 20, None, "Full hook-up", "City of McIntosh: full hookup $20 a night, electric only $10; first come, first served."),
 (5666, 55, 55, None, "Electric | Daily: $55", "McKinley Park Campground 2025 schedule: electric $55 a day, non-electric $35."),
 (5667, 45, 45, None, "Rates are $45 per night", "City of Menahga: $45 a night plus tax."),
 (5668, 30, 30, None, "RV Fee:", "City of Granite Falls: RV sites $30 a night."),
 (5673, 40, 40, None, "$40 per night", "City of Peterson: $40 a night with water, sewer and electric."),
 (5676, 32.21, 42.95, None, "Camping with Electricity", "Polk County: electric $32.21 a day, with water $37.58, full hookup $42.95; daily park fee $10.74 per vehicle; 3-night holiday minimum."),
 (5698, 37.58, 37.58, None, "Camping Fee", "Polk County: camping $26.84 a day plus $10.74 for electricity; tents $21.48."),
 (5680, 25, 25, None, "$25.00 per night", "Riverside Park: 9 RV spots $25 a night, first come."),
 (5681, 30, 30, None, "Camp sites with electric - $30", "City of St. Peter: electric sites $30 a night."),
 (5683, 25, 30, None, "Daily Fees for camping", "City of Edgerton: water and 30-amp $25 a night along the river, full hookup 50-amp $30; tents $15."),
 (5684, 34, 34, None, "Daily | $34", "City of Roseau 2026: water-and-electric sites $34 a day, $210 a week; booked through Campspot."),
 (5685, 40, 40, None, "Full Hook-Up: $40/night", "City of Springfield: full hookup $40 a night, $240 a week; tents $15."),
 (5688, 25, 25, None, "Seven Mike Park", "Murray County: $25 a night; tents $15."),
 (5689, 20, 20, None, "Electric sites are $20", "City of Pelican Rapids: electric sites $20, non-electric $15."),
 (5695, 30, 30, None, "$30.00/Nightly", "City of Tracy: $30 a night, $175 a week."),
 (5696, 35, 35, None, "fee of $35.00 per night", "City of Blue Earth: 14 full-hookup 50/30-amp sites, $35 a night including WiFi and firewood."),
 (5697, 35, 35, None, "camper site is $35", "City of St. James 2026: camper sites $35 a night tax included, tents $20."),
 (5699, 35, 40, None, "RV Sites with electric, water and sewer", "City of Baudette (January 2026): water and electric $35 a night, full hookup $40 (full hookup monthly needs a 1-week minimum); tents $25."),
 (5701, 25, 25, None, "Water & Electric - $25", "City of Butterfield: water and electric $25 a day, primitive $15."),
 (5703, 35, 35, None, "$35: Site #4", "City of Breckenridge: electric and water sites $35 a night, rustic $25."),
 (5706, 35, 35, None, "$35/night RV site", "City of Williams: RV sites with water, sewer and electric $35 a night, tents $20."),
 (5708, 40, 50, None, "$40 per night for electric/water", "City of Zumbrota: electric and water $40 a night, with sewer $50; tents $25."),
]
pages = [json.loads(l) for l in open("mn_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_mn_2026-10-15/mn_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
