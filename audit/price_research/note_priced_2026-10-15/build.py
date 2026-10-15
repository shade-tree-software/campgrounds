"""Note-priced private entries: each priced from the OPERATOR's own page (never from our note), read 2026-10-15.
python3 -I build.py > findings.json   (rows also in build_*.py batches appended below)
low/high = RV sites; tent, cabin, weekly/monthly, holiday and guest charges go in the note."""
import json
ROWS = [
 (11, 70, 70, None, "https://www.sweetwatervacationproperties.com/rv-sites/rv-sites-rates/", "Sweetwater RV sites $70 a night for 4 people, $420 a week, year-round; $15 per extra person."),
 (13, 60, 60, None, "https://www.campriversedgeva.com/site-map", "River's Edge: full-hookup RV sites $60 a night for up to 5 people; primitive tent sites $36."),
 (51, 35, 80, None, "https://www.blueheroncampground.com/rv-sites", "Blue Heron: water and electric $35 a night, standard full hookup $45, riverview $55-65, riverfront $65-80 (first 4 guests); tents $25."),
 (427, 30, 55, None, "https://www.fiverivercampground.com/", "Five River: rates $30-55 a night for 2 adults and 2 children."),
 (461, 60, 60, None, "https://www.lazyacamping.com/camping-rv/", "Lazy A: RVs and pop-ups $60 a night plus tax for 1-2 adults; $65 on holidays (webreserv); tents $40."),
 (592, 62.30, 77, 3, "https://www.lakeairerv.com/features-rates", "Lake Aire rates from 10/1/26: 30-amp water/electric $62.30, waterfront water/electric back-in $68, full-hookup pull-throughs $67-77; plus 12% tax; $3 processing fee per reservation."),
 (972, 85, 108, 3.50, "https://www.barharborrvpark.com/rv-camping", "Bar Harbor 2026 (2 people): off-waterfront from $85 spring and fall, $95 peak (May 15 - Sep 14); waterfront and pull-throughs from $98 and $108; $80 all sites Dec-Mar; peak weekends 2-night minimum; $3.50 service fee per reservation."),
 (1500, 48, 53, None, "https://geneseecountrycampground.com/rates/", "Genesee Country: water/electric 30-amp pull-through $48 a night, 50-amp back-in $53; holidays 3-night minimum."),
 (1517, 50, 60, None, "http://www.treasureislervpark.com/rates", "Treasure Isle: water/electric $50 a night, $300 a week; holiday weekends $60 a night with a 3-night minimum."),
 (1742, 30, 40, None, "https://www.campawhilerv.com/", "Camp A While: electric only $30 a night, water/electric $35, full hookup $40; $260 a week."),
 (1745, 45, 45, None, "https://www.countrysidecampgroundil.com/", "Countryside: daily rate $45 a night."),
 (2632, 38, 38, None, "http://valleysunsetrvranchdelta.com/rates.htm", "Valley Sunset: $38 a night plus tax; seventh night free; monthly from $500 plus electric."),
 (2868, 38, 38, None, "https://nvv-ne.com/rv-park", "Niobrara Valley Vineyards: pull-through RV sites $38 a night plus tax, including 2 wine tastings; $28 for military, seniors and Harvest Hosts; tents $15."),
 (3211, 25, 25, None, "https://www.lizardcreekranch.com/camping/", "Lizard Creek: full-service sites $25 a day, $155 a week, $600 a month; tag and pay."),
 (3212, 20, 20, None, "https://www.whiterockconservancy.org/oak-ridge-rv-campground", "Whiterock Conservancy: $20 per RV a night with electric, $15 without; paid before the stay."),
 (3231, 20, 20, None, "https://www.westbendgrotto.com/visit/campground/", "Grotto of the Redemption: campers $20 a night, tents $10."),
 (3256, 50, 50, None, "https://www.tristateraceway.com/rv-park", "Tri-State Raceway: full hookups $50 a night, $300 a week; tents $10."),
 (3366, 40, 40, None, "https://dncampground.com/camping/", "DN Campground: electric and water sites $40 a night ($50 Friday and Saturday on holidays), prepaid online."),
 (3369, 35, 35, None, "https://www.featherstonervpark.com/", "Featherstone 2026: $35 a night including tax, 30 or 50 amp full hookups, 2 adults; $5 per extra adult."),
 (3421, 45, 45, None, "https://deeplakecampground.com/", "Deep Lake: nightly rates from $45; season May 1 - Oct 31."),
 (3437, 31, 43, None, "https://tomahawk-campground.com/rates/", "Tomahawk: electric only $31 a night, water/electric $34, full hookup $43; holiday weekends 3-night minimum."),
 (3826, 30, 50, None, "https://gilmorecarmuseum.org/visit/on-site-camping", "Gilmore Car Museum: 20-amp $30 a night, 30-amp $35, 50-amp $50, no electricity $20; no water or sewer; museum admission must be bought for each night."),
 (3840, 30, 35, None, "https://www.stlouiscampground.org/rates", "St. Louis Campground: water and electric, 30-amp $30 a night, 50-amp $35; weekly $170/$200."),
 (3881, 20, 20, None, "http://www.chalkhillscampground.com/CampgroundInfo.aspx", "Chalk Hills: all sites $20 a night (electric)."),
 (3939, 25, 26, None, "https://eatoncountyfair.com/pageserver/camping", "Eaton County Fairgrounds: $25 a day cash, $26 by card."),
 (4063, 70, 75, None, "https://laurellock.com/rates.aspx", "Laurel Lock: overnight sites $70-75 a night, 2-night minimum on weekends; holiday rates higher with a 3-night minimum."),
 (4094, 40, 40, None, "https://meadowcrestcampground.com/rates-%26-rv-rentals", "Meadowcrest: RV sites $40 a night, $240 a week; tents $25; 9% Vermont rooms tax added."),
 (4134, 47, 47, None, "https://www.storrspond.org/activities/camping/", "Storrs Pond: RV sites $47 a night for 4 people ($58 on holiday weekends); tents $37."),
 (4139, 45, 45, None, "https://wolfeborocampground.com/rates/", "Wolfeboro 2026: RV sites with water, sewer and electric $45 a night."),
 (4140, 70, 70, None, "https://www.beaverhollowcampground.com/rates-rentals-specials/campground-rates.php", "Beaver Hollow: camper/RV sites $70 a day, $420 a week."),
]
if __name__ == "__main__":
    import glob, importlib.util
    rows = list(ROWS)
    for f in sorted(glob.glob("build_b*.py")):
        sp = importlib.util.spec_from_file_location(f[:-3], f); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        rows += m.ROWS
        rows += [r + ("CAD",) for r in getattr(m, "CAD", [])]
    out = []
    for row in rows:
        i, lo, hi, rf, src, note = row[:6]
        f = {"nightly_low": lo, "nightly_high": hi, "currency": row[6] if len(row) > 6 else "USD"}
        if rf:
            f["reservation_fee"] = rf
        f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
        out.append({"id": i, "fees": f, "source": src + " (audit/price_research/note_priced_2026-10-15/pages.jsonl), read 2026-10-15"})
    print(json.dumps(out, ensure_ascii=False, indent=1))
