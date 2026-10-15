"""WA local findings from wa_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY,
or the URL given when KEY starts with http (a peek at the same page, 2026-10-15)."""
import json
BRIDGE = "City of Bridgeport: RV sites $55 a night (Marina Park and Conklin Landing), tents $27."
ROWS = [
 (10450, 25, 25, None, "11 RV sites($25/night)", "Cowlitz County: 11 RV sites $25 a night, tents $20."),
 (10451, 67, 98, None, "Starting at | $98/Daily", "Clark County Fairgrounds RV Park (RV Inn Style Resorts): from $98 a day May 1 - October 15, $67 in winter."),
 (10453, 45, 45, None, "RV Site - $45", "Port of Wahkiakum No. 1: power-only RV sites $45 a night (no water at sites), tents $30."),
 (10454, 65, 65, None, "Daily: $65 plus tax", "Franklin County (rates from 2025): full hookups $65 a day plus tax, $60 with Good Sam/AAA/AARP/military."),
 (10457, 40, 45, None, "OFF-PEAK: Overnight w/ hookup", "Grays Harbor County Fair: with hookup $40 a night off-peak, $45 peak; non-hookup $35-40."),
 (10460, 30, 45, None, "https://visitmorton.com/city-hall/parks-recreation/", "City of Morton: full hookups $45 (April-October) / $35 (November-March), power and water $40 / $30; tents $15."),
 (10463, 40, 40, None, "RV/Camper - Individual Reservation", "Kittitas Valley Event Center: RV/camper $40 a night ($30 in winter, no water), dry $20; 3-night maximum outside events."),
 (10464, 45, 50, None, "North campground rates are $45", "Grant County Fairgrounds: North and East campgrounds (30-amp) $45 a night, Pavilion $50, plus taxes and fees; 7-day limit."),
 (10465, 35, 75, None, "https://www.crescentbarrecreation.com/camping/", "Crescent Bar (Grant PUD): electric and sewer sites $50-60 a night April 1 - October 15, premium $65-75, $35 January-March; weekend minimums."),
 (10467, 40, 55, None, "Back-In Sites: $40", "City of Palouse: back-in $40 plus tax, pull-through $45 ($50/$55 on premium event weekends)."),
 (10470, 25, 25, None, "$25.00 per night for RV Camping", "Palouse Empire Fairgrounds: RV camping with water and electric $25 a night, tents $10."),
 (10479, 25, 25, None, "Fee: $25 per night", "Jefferson County: $25 a night, first come, first served."),
 (10484, 39, 52, None, "https://mansonparks.com/directory/wapato-lake-campground/", "Manson Parks: 30-amp RV sites $39 a night weekdays / $49 weekends, 50-amp $42 / $52; tents $34-46."),
 (10485, 55, 55, None, "RV Site $55.00", BRIDGE),
 (10486, 55, 55, None, "All RV Sites $55.00", BRIDGE),
 (10487, 40, 50, None, "Full Hookup | $50", "Coulee City: full hookup $50 ($40 off-season), dry sites $35."),
 (10495, 50, 50, None, "The nightly rate is $50", "San Juan County Fairgrounds: eight RV pedestals $50 a night plus tax."),
 (10506, 20, 50, None, "RVs under 34 ft. $20.00", "Pend Oreille County Fair: water and electric $20 a day for RVs under 34 ft, $50 over; dry $15."),
 (10510, 50, 60, None, "Full hook-up $60/night", "Port of Wahkiakum No. 2: full hookup $60 a night, river view $55, partial $50, tents $38."),
 (10511, 50, 60, None, "Per Night-$60.00", "Port of Wahkiakum No. 1: riverfront sites $60 a night, pull-throughs $50 (2-night minimum March-October)."),
 (10517, 45, 45, None, "RV Camping $45/night", "Crow Butte Park (Port of Benton) 2026: RV camping $45 a night, $35 for veterans."),
 (10533, 50, 70, None, "Daily Rate Oct. 1 - May 31 $50", "Riverside RV Park: $65-70 a day June-September, $50-55 October-May."),
 (10539, 44, 44, None, "Rate is $44* per night", "City of Moses Lake: RV sites with hookups $44 a night, tents $39, taxes included."),
 (10570, 53, 68, None, "Regular Back-in Sites: $53", "Port of Skagit summer rates: back-in $53 a night, pull-through and premium $68; 10% Good Sam discount."),
 (10572, 39, 39, None, "These rent for $39", "City of Anacortes: 46 water-and-electric sites $39 a night, 22 non-utility $31."),
]
pages = [json.loads(l) for l in open("wa_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    if key.startswith("http"):
        urls = [key]
    else:
        urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_wa_2026-10-15/wa_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
