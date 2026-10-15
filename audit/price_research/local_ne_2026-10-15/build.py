"""NE local findings from ne_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY,
or the URL given when KEY starts with http (a peek at the same page, 2026-10-15)."""
import json
ROWS = [
 (2768, 25, 25, None, "The sites cost $25", "Village of Arnold: electric and water sites $25 a night, primitive $10; no reservations."),
 (2771, 25, 25, None, "Suggested donations of $25", "City of Bassett: suggested donation $25 a night, electricity and water; first come, first served."),
 (2773, 0, 25, None, "Next eight (8) nights", "City of Bayard: first two nights free, the next eight $25 a night; 10-day maximum."),
 (2785, 20, 20, None, "RV: $20.00/DAY", "City of O'Neill (Carney Park): RV $20 a day."),
 (2792, 20, 20, None, "RATES for camping are $20.00", "City of Fairbury: $20 a night; lakeside sites by reservation."),
 (2795, 25, 25, None, "Rental fee: $25/electrical", "City of Weeping Water: electric sites $25, tents $10; no reservations."),
 (2797, 20, 25, None, "30-amp service at $20.00", "Village of Diller: 30-amp $20 a night, 50-amp $25."),
 (2808, 15, 15, None, "Each spot is $15/day", "City of Humboldt: $15 a day."),
 (2809, 25, 25, None, "Camping rates are $25 per night", "City of Lyons: $25 a night, $150 a week."),
 (2810, 20, 20, None, "The cost to reserve a space is $20", "City of McCook: 50-amp sites $20 a night by reservation."),
 (2815, 20, 20, None, "https://littlebluenrd.org/recreation/", "Little Blue NRD: nineteen electric RV pads, $20 a night (effective May 1, 2021)."),
 (2818, 20, 20, None, "RV Sites—$20/night", "City of Atkinson: RV sites $20 a night, tents $10; no reservations."),
 (2821, 20, 20, None, "RV Camping Pads | $20 per day", "City of Neligh: RV pads with electric and water $20 a day, tents $5."),
 (2823, 10, 10, None, "Suggested donation of $10/night", "City of Osmond: suggested donation $10 a night, 30/50-amp."),
 (2828, 10, 10, None, "$10 / night", "City of Burwell: $10 a night, first come, first served."),
 (2829, 25, 25, None, "The camping rate is $25.00", "City of Beatrice: $25 a night."),
 (2832, 30, 30, None, "Each site is $30/day", "Seward County Fairgrounds: 30-amp sites $30 a day."),
 (2840, 35, 35, None, "$35/day", "City of Broken Bow: $35 a day."),
 (2841, 15, 15, None, "Fee is $15 per day", "City of Crete: 21 RV sites $15 a day, first come, first served."),
 (2847, 15, 20, None, "Water & Electricity ($15 for 30 Amp", "York County Fair: water and electric $15 (30-amp) or $20 (50-amp); tents $5."),
 (2883, 25, 25, None, "All Electric pads", "Lower Elkhorn NRD: electric pads $25, tents $10."),
 (2884, 25, 25, None, "NEW PRICES as of 3/3/25", "City of Hebron (prices as of 3/3/25): motor homes and campers $25."),
 (2885, 28, 37, None, "Electric - $28.00 a day", "City of South Sioux City: electric $28 a day, with water $30, full hookup $33, pull-through $37."),
 (14519, 10, 10, None, "A donation of $10", "Village of Beaver Crossing: suggested donation $10 a night, electric and water."),
 (14520, 20, 20, None, "Reservations $20.00 per night", "City of Auburn: $20 a night."),
]
pages = [json.loads(l) for l in open("ne_pages.jsonl")]
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
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_ne_2026-10-15/ne_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
