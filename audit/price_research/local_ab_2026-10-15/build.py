"""AB local findings from ab_pages.jsonl (operators' own pages, read 2026-10-15), CAD. python3 -I build.py > findings.json
low/high = RV (power/hookup) sites; tent/unserviced in the note. Source = first page whose rate lines contain KEY,
or the URL given when KEY starts with http (a peek at the same page, 2026-10-15)."""
import json
ROWS = [
 (8852, 25, 25, None, "$25/night per unit", "Stavely Elks: $25 a night per unit."),
 (8950, 30, 40, None, "Power (20 or 30 amp)", "Town of Hanna (from April 1, 2025): power $30, power and water $35, full service $40; tent or non-serviced $25."),
 (9020, 50, 60, None, "30 amp w/s $50.00", "Granview Recreation Park (Granum): 30-amp with water and sewer $50, 50-amp $60; tents $25."),
 (9021, 35, 35, None, "Nightly Rate | $35.00", "Town of Vulcan: $35 a night."),
 (9022, 35, 35, None, "Power Sites 30 AMP", "Foothills Lions Club: 30-amp power sites $35 plus GST and fees, non-power $30."),
 (9024, 35, 35, None, "$35/night per unit per night for powered", "Stavely Elks: powered sites $35 a night per unit, non-power $25."),
 (9029, 25, 25, None, "Camping Unit w/ 15a Power & Water", "Village of Champion: 15-amp power and water $25 a night, first come, first served."),
 (9030, 38, 68, None, "https://www.medicinehat.ca/parks-recreation/camping/", "City of Medicine Hat: power $48 a night (shoulder $38), power and water $54 ($43), full service 30-amp $64 ($54), 50-amp $68 ($56.50); unserviced $34 ($26)."),
 (9031, 25, 30, None, "Full Service Sites (water/sewer/power", "Town of Milk River: full service $30 a night, water and power $25, tents $20."),
 (9035, 40, 45, None, "Power, Water, & Sewer-$45.00", "Town of Stettler: power, water and sewer $45 a night, power and water $40, no service $20."),
 (9036, 35, 35, None, "$35 Cdn/night", "Town of Carstairs: powered sites $35 a night (GST included), non-powered $28."),
 (9040, 30, 30, None, "The rates are $30.00 per night", "Village of Linden: water and 50-amp $30 a night, first come, first served."),
 (9041, 30, 30, None, "$30 per night — power only", "Town of Tofield: power-only sites $30 a night, self-registration."),
 (9043, 40, 40, None, "Serviced Sites- $40", "Kneehill County: serviced sites $40, unserviced $30."),
 (9044, 37, 37, None, "Serviced site (power & water hookup)", "Town of Rocky Mountain House: power and water $37 a night, no service $30."),
 (9045, 40, 66.15, None, "Full Service Sites (#1 - #10)", "Town of Sylvan Lake: power sites $40 a night, full service $66.15."),
 (9046, 35, 45, None, "15 AMP Power | Water", "Village of Beiseker: 15-amp and water $35, 30-amp and water $40, full hookup $45, unserviced $30."),
 (9052, 35, 35, None, "Fee: $35.00 per night", "Town of Oyen: 30-amp power and water $35 a night."),
 (9053, 5, 5, None, "Camping is $5.00 per night", "MD of Wainwright: $5 a night, no services."),
 (9056, 25, 25, None, "There is a $25 fee", "Special Areas: water and power lots $25 a night."),
 (9058, 45, 45, None, "$45 / night for full service", "County of Grande Prairie 2026: full service $45 a night plus a $7 fire permit fee."),
 (9060, 35, 35, None, "Daily $35", "Town of Valleyview: power and water $35 a day in summer, power only $25 in winter."),
 (9061, 20, 20, None, "Fee: $20.00 per night", "Yellowhead County: $20 a night."),
 (9062, 32, 34, None, "Power (30 AMP) and water only sites", "Town of Westlock: power and water $32 a night, full hookup $34."),
 (9071, 50, 50, 4, "DAILY - $50.00", "Okotoks Lions: full hookup $50 a day, unserviced $35; $4 booking fee."),
 (9080, 40, 45, None, "Full Service Site: $45.00", "Town of Pincher Creek: full service $45, electric $40, tents $30."),
 (9087, 45, 45, None, "With Services - Daily", "Town of Raymond: serviced sites $45 a day, no services $30."),
 (9090, 40, 40, None, "Power & Water Fees: 29 camp spots", "Town of Bow Island 2026: power and water $40 a night, tents $20."),
 (9092, 30, 30, None, "$30.00 per night", "Village of Warner: $30 a night, first come, first served."),
 (9099, 40, 65, None, "FULL HOOK UP - 30 AMP Regular", "Red Deer Lions: full hookup 30-amp $52.50-55 plus GST, 50-amp premium $65, 15-amp power only $40."),
 (9101, 49, 69, None, "15 amp Power", "Leduc Lions: 15-amp power and water $49 a day, 30-amp full $59, 50-amp $69, plus GST; unserviced $30."),
 (12801, 65.10, 65.10, None, "Full‑Service RV Campsites", "Town of Drayton Valley: 30-amp full service $65.10 a night (tax included); 15-amp tent sites $25."),
]
pages = [json.loads(l) for l in open("ab_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    if key.startswith("http"):
        urls = [key]
    else:
        urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_ab_2026-10-15/ab_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
