#!/usr/bin/env python3
"""Parks Canada rows, read by hand from pages.json (each park's visit/tarifs-fees, 2026-10-16).

    python3 -I build.py   -> findings.json for ../apply.py

nightly_low/high = the cheapest and dearest drive-in RV-usable site class AT THAT CAMPGROUND
in the peak-season table (high-occupancy rates included; oTENTiks, cabins, walk-in, group
and Two Jack's 'Equipped Campsites' excluded). Shoulder-season rates go in the note. The
C$11.50 online reservation fee is recorded only where the campground takes reservations.
Jasper's table is by site type; each campground's type comes from its own block on
/pn-np/ab/jasper/activ/passez-stay/camping ('Site type: Primitive, with fire pit').
Left out: Monarch 8569 (Parks Canada now lists it 'walk-in - Primitive' - for AWH),
Rocky Mountain House 8815 (no fees page), PEI 12985/12986 (fees page has no camping table).
"""
import json
P = json.load(open("pages.json"))
JASPER_SITES = "https://parks.canada.ca/pn-np/ab/jasper/activ/passez-stay/camping"
# id: park, low, high, reservable, KEY (text on the fees page), note
ROWS = [
 (8265, "pn-np/on/bruce", 34, 34, 1, "Unserviced with Washroom Building Having Toilets and Showers | $ 34.00", "Winter camping C$26.75 (Nov 1-Apr 30)."),
 (8267, "pn-np/on/pukaskwa", 31.75, 36.75, 1, "Hattie Cove - Serviced with electricity (washroom building having toilets and showers) | $ 36.75", "Shoulder season C$19.50 unserviced, C$24.50 electric."),
 (8563, "pn-np/bc/gulf", 22, 22, 1, "SMONEĆTEN, per party, per vehicle (May 15 to September 30) | $ 22.00", "Per party and vehicle; extra vehicle C$8.75."),
 (8564, "pn-np/bc/gulf", 22, 22, 1, "Prior Centennial (North Pender Island), per party, per vehicle (May 15 to September 30) | $ 22.00", "Per party and vehicle; extra vehicle C$8.75."),
 (8565, "pn-np/bc/pacificrim", 34, 40, 1, "Long Beach - Serviced with Electricity (Drive-in) | $ 40.00", "Unserviced C$34, electric C$40."),
 (8566, "pn-np/bc/kootenay", 34, 47.25, 1, "Redstreak - Water, sewer, and electrical | $ 47.25", "Unserviced C$34, electric C$40, full hookup C$47.25."),
 (8567, "pn-np/bc/kootenay", 26.75, 26.75, 1, "McLeod Meadows - Unserviced with washroom building having toilets only | $ 26.75", None),
 (8568, "pn-np/bc/revelstoke", 34, 40, 1, "Snowforest - Electrical | $ 40.00", "Unserviced C$34, electric C$40."),
 (8570, "pn-np/bc/yoho", 34, 34, 1, "Kicking Horse - Unserviced sites with washroom building having toilets and showers | $ 34.00", None),
 (8573, "pn-np/bc/yoho", 19.5, 19.5, 0, "Hoodoo Creek - Primitive with pit privies | $ 19.50", None),
 (8571, "pn-np/bc/glacier", 26.75, 26.75, 1, "Illecillewaet - Unserviced with washroom building having toilets only | $ 26.75", None),
 (8572, "pn-np/bc/glacier", 26.75, 26.75, 1, "Loop Brook - Unserviced with washroom building having toilets only | $ 26.75", None),
 (8790, "pn-np/ab/waterton", 34, 47.25, 1, "Townsite Campground: Full service (water, sewer, electrical), per night | $ 47.25", "Unserviced C$34, electric C$40, full hookup C$47.25."),
 (8791, "pn-np/ab/waterton", 22, 22, 1, "Belly River Campground: Unserviced, basic sites, per night | $ 22.00", None),
 (8792, "pn-np/ab/jasper", 34, 61, 1, "Full service, with fire pit | $ 61.00", "Unserviced C$34, electric C$40, full hookup C$47.25; a site with a fire pit costs C$13.75 more."),
 (8793, "pn-np/ab/jasper", 34, 53.75, 1, "Electrical services, with fire pit | $ 53.75", "Unserviced C$34, electric C$40; a site with a fire pit costs C$13.75 more."),
 (8794, "pn-np/ab/jasper", 22, 22, 1, "Primitive, no fire pit | $ 22.00", None),
 (8795, "pn-np/ab/jasper", 43.25, 43.25, 1, "Unserviced, no showers, with fire pit | $ 43.25", "Sites have fire pits; the rate includes the fire permit."),
 (8796, "pn-np/ab/jasper", 35.75, 35.75, 0, "Primitive, with fire pit | $ 35.75", "Rate includes the fire permit."),
 (8797, "pn-np/ab/jasper", 35.75, 35.75, 0, "Primitive, with fire pit | $ 35.75", "Rate includes the fire permit."),
 (8798, "pn-np/ab/jasper", 35.75, 35.75, 0, "Primitive, with fire pit | $ 35.75", "Rate includes the fire permit."),
 (8803, "pn-np/ab/jasper", 22, 22, 0, "Primitive, no fire pit | $ 22.00", None),
 (8812, "pn-np/ab/jasper", 35.75, 35.75, 0, "Primitive, with fire pit | $ 35.75", "Rate includes the fire permit."),
 (8814, "pn-np/ab/jasper", 35.75, 35.75, 0, "Primitive, with fire pit | $ 35.75", "Rate includes the fire permit."),
 (8799, "pn-np/ab/banff", 47.25, 47.25, 1, "Tunnel Mountain - Water, sewer, and electrical | $ 47.25", None),
 (8800, "pn-np/ab/banff", 40, 40, 1, "Lake Louise - Electrical | $ 40.00", None),
 (8801, "pn-np/ab/banff", 40, 40, 1, "Tunnel Mountain - Electrical | $ 40.00", None),
 (8802, "pn-np/ab/banff", 34, 34, 1, "Tunnel Mountain - Unserviced with washroom building having toilets and showers | $ 34.00", None),
 (8804, "pn-np/ab/banff", 22, 22, 1, "Silverhorn Creek - Primitive | $ 22.00", None),
 (8805, "pn-np/ab/banff", 26.75, 26.75, 1, "Protection Mountain - Unserviced with washroom building having toilets only | $ 26.75", None),
 (8806, "pn-np/ab/banff", 34, 34, 1, "Johnston Canyon - Unserviced with washroom building having toilets and showers | $ 34.00", None),
 (8807, "pn-np/ab/banff", 22, 22, 1, "Rampart Creek - Primitive | $ 22.00", None),
 (8808, "pn-np/ab/banff", 34, 34, 1, "Two Jack Lakeside - Unserviced with washroom building having toilets and showers | $ 34.00", None),
 (8809, "pn-np/ab/banff", 26.75, 26.75, 0, "Waterfowl - Unserviced with washroom building having toilets only | $ 26.75", None),
 (8810, "pn-np/ab/banff", 22, 22, 0, "Mosquito Creek - Primitive | $ 22.00", None),
 (8811, "pn-np/ab/banff", 29.5, 29.5, 1, "Two Jack Main - Unserviced with washroom building having toilets only | $ 29.50", None),
 (8813, "pn-np/ab/banff", 29.5, 29.5, 1, "Castle Mountain - Unserviced with washroom building having toilets only | $ 29.50", None),
 (8816, "pn-np/ab/elkisland", 31.75, 31.75, 1, "Astotin Lake - Unserviced with washroom building having toilets and showers | $ 31.75", "Overflow C$19.50."),
 (9150, "pn-np/sk/princealbert", 48.5, 48.5, 1, "Beaver Glen - Electrical, with washroom building having toilets and showers (includes fire permit) | $ 48.50", "Rate includes the fire permit."),
 (9152, "pn-np/sk/princealbert", 19.5, 19.5, 0, "Namekus Lake - Primitive | $ 19.50", "Shoulder season C$16.25."),
 (9153, "pn-np/sk/princealbert", 38.5, 38.5, 0, "Unserviced with washroom building having toilets only, per night (includes fire permit) | $ 38.50", "Rate includes the fire permit; C$239.25 a week."),
 (9154, "pn-np/sk/princealbert", 43.75, 47.25, 1, "Red Deer Campground - Water, sewer, and electrical - high occupancy | $ 47.25", "Full hookup C$43.75, C$47.25 at high occupancy."),
 (9156, "pn-np/sk/princealbert", 19.5, 19.5, 0, "Sandy Lake - Primitive | $ 19.50", "Shoulder season C$16.25."),
 (9151, "pn-np/sk/grasslands", 40, 40, 1, "Front Country, Serviced with electricity – Frenchman Valley (Peak) | $ 40.00", "Peak season (June-August) C$40, shoulder C$36.75."),
 (9155, "pn-np/sk/grasslands", 36.75, 36.75, 1, "Front Country, Serviced with electricity – Rock Creek | $ 36.75", None),
 (9316, "pn-np/mb/riding", 19.5, 19.5, 0, "Moon Lake, Lake Audy, Whirlpool, and Deep Lake - Primitive | $ 19.50", None),
 (9317, "pn-np/mb/riding", 19.5, 19.5, 0, "Moon Lake, Lake Audy, Whirlpool, and Deep Lake - Primitive | $ 19.50", None),
 (9318, "pn-np/mb/riding", 34, 47.25, 1, "Wasagaming - Water, sewer, and electrical | $ 47.25", "Unserviced C$34, electric C$40, electric + water C$43.75, full hookup C$47.25."),
 (12474, "pn-np/qc/mauricie", 33.75, 42, 1, "With electricity, per site, per night, high occupancy | $ 42.00", "Without electricity C$33.75 (C$36 at high occupancy), with electricity C$38.75 (C$42)."),
 (12475, "pn-np/qc/mauricie", 33.75, 42, 1, "With electricity, per site, per night, high occupancy | $ 42.00", "Without electricity C$33.75 (C$36 at high occupancy), with electricity C$38.75 (C$42)."),
 (12476, "pn-np/qc/mauricie", 33.75, 42, 1, "With electricity, per site, per night, high occupancy | $ 42.00", "Without electricity C$33.75 (C$36 at high occupancy), with electricity C$38.75 (C$42)."),
 (12477, "pn-np/qc/forillon", 34, 43.75, 1, "Serviced with Electricity and Water | $ 43.75", "Unserviced C$34, electric C$40, electric + water C$43.75 (park-wide table)."),
 (12478, "pn-np/qc/forillon", 34, 43.75, 1, "Serviced with Electricity and Water | $ 43.75", "Unserviced C$34, electric C$40, electric + water C$43.75 (park-wide table)."),
 (12824, "pn-np/nb/fundy", 43.75, 43.75, 1, "Cannontown, Serviced with electricity, water, and sewer | $ 43.75", "Shoulder season C$35."),
 (12825, "pn-np/nb/fundy", 31.75, 43.75, 1, "Chignecto North - Serviced with electricity, water, and sewer | $ 43.75", "Unserviced C$31.75, electric + water C$40, full hookup C$43.75; shoulder C$25.25-35."),
 (12827, "pn-np/nb/fundy", 31.75, 43.75, 1, "Headquarters - Serviced with electricity, water, and sewer | $ 43.75", "Unserviced C$31.75, full hookup C$43.75; shoulder C$25.25-35."),
 (12828, "pn-np/nb/fundy", 36.75, 36.75, 1, "Lakeview - serviced with electricity | $ 36.75", "Shoulder season C$27.25."),
 (12829, "pn-np/nb/fundy", 31.75, 40, 1, "Point Wolfe – Serviced with electricity and water | $ 40.00", "Unserviced C$31.75, electric + water C$40."),
 (12826, "pn-np/nb/kouchibouguac", 19.5, 19.5, 1, "Côte-à-Fabien - Primitive (June to September) | $ 19.50", None),
 (12830, "pn-np/nb/kouchibouguac", 34, 47.25, 1, "South Kouchibouguac – Electricity, sewage and water (Last full week in June to Labour Day) | $ 47.25", "Peak: unserviced C$34, electric C$40, full hookup C$47.25; shoulder C$26.75-43.75."),
 (12901, "pn-np/ns/cbreton", 22, 22, 0, "Unserviced with Pit Privies (Big Intervale) | $ 22.00", None),
 (12902, "pn-np/ns/cbreton", 31.75, 43.75, 1, "Serviced with Electricity, Water, and Sewer (Chéticamp and Broad Cove) | $ 43.75", "Unserviced C$31.75-34, full hookup C$43.75."),
 (12903, "pn-np/ns/cbreton", 31.75, 43.75, 1, "Serviced with Electricity, Water, and Sewer (Chéticamp and Broad Cove) | $ 43.75", "Unserviced C$31.75-34, electric C$36.75, full hookup C$43.75."),
 (12904, "pn-np/ns/kejimkujik", 34, 40, 1, "Jeremy's Bay - Serviced with electricity | $ 40.00", "Peak: unserviced C$34, electric C$40; shoulder C$31.75-36.75."),
 (13010, "pn-np/nl/grosmorne", 34, 43.75, 1, "Berry Hill serviced, water and electricity | $ 43.75", "Peak (Jun 12-Sep 14): unserviced C$34, water + electric C$43.75; off season C$31.75-40."),
 (13011, "pn-np/nl/grosmorne", 34, 43.75, 1, "Green Point serviced, water and electricity | $ 43.75", "Peak (Jun 12-Sep 14): unserviced C$34, water + electric C$43.75; off season C$31.75-40."),
 (13012, "pn-np/nl/grosmorne", 34, 34, 1, "Lomond - Unserviced with washroom building having toilets and showers | $ 34.00", "Off season C$31.75."),
 (13015, "pn-np/nl/grosmorne", 34, 34, 1, "Shallow Bay - Unserviced with washroom building having toilets and showers | $ 34.00", "Off season C$31.75."),
 (13016, "pn-np/nl/grosmorne", 34, 34, 1, "Trout River - Unserviced with washroom building having toilets and showers | $ 34.00", "Off season C$31.75."),
 (13013, "pn-np/nl/terranova", 26.25, 26.25, 1, "Malady Head - Unserviced with washroom building having toilets and showers | $ 26.25", "Shoulder season C$17.75."),
 (13014, "pn-np/nl/terranova", 31.75, 47.25, 1, "Newman Sound- Serviced with electricity, water and sewer | $ 47.25", "Unserviced C$31.75, electric C$40, full hookup C$47.25; lower shoulder and 8+-night rates."),
]
F, bad = [], []
for i, park, lo, hi, res, key, note in ROWS:
    text = P[park]["camping"].replace("\xa0", " ")
    if key not in text:
        bad.append((i, key))
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if res:
        fees["reservation_fee"] = 11.5
    if note:
        fees["note"] = note
    src = P[park]["url"] + f" ('{key}', read 2026-10-16)"
    if park == "pn-np/ab/jasper":
        src += f"; site type from {JASPER_SITES}"
    F.append({"id": i, "fees": fees, "source": src})
assert not bad, bad
json.dump(F, open("findings.json", "w"), indent=1, ensure_ascii=False)
print(len(F), "findings")
