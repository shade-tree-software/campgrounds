"""MI local findings from mi_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY,
or the URL given when KEY starts with http (a peek at the same page, 2026-10-15)."""
import json
MUSK = "Muskegon County: campsites ${} a day; vehicle day pass $7."
HURON = "Huron County Parks: {} plus $5 on holidays, $5 off in the off season."
MENO = "Menominee County: electric sites $30 a night{}; $10 reservation fee; $5 daily vehicle entrance fee."
GOG = "Gogebic County 2026: ${} a night."
ROWS = [
 (3913, 35, 35, None, "Daily Rate: | $35", "City of Lapeer (rates as of July 1, 2025): $35 a day, $200 a week; no tents."),
 (3914, 35, 35, None, "Campsite Nightly Rental with Camper", "Belvidere Township: campsite with camper $35 a night, tent $25."),
 (3924, 40, 40, None, "Daily Rate: $40.00", "U.P. State Fair 2026: water and electric $40 a day per unit."),
 (3927, 40, 40, None, "Full Hookup Site $40", "St. Joseph County: full hookup sites $40, rustic $30."),
 (3928, 30, 40, None, "30 amp hookup per night", "Hillsdale County Fair: 30-amp $30 a night, 50-amp $40, $5 more with sewer."),
 (3933, 45, 45, None, "RV/Camper Site (per night): $45", "Huron-Clinton Metroparks: RV/camper sites $45 a night, tents $35; $10 daily or annual vehicle pass."),
 (3947, 38, 38, None, "Daily – $38", "Village of Otter Lake: full-hookup 30/50-amp lots $38 a day."),
 (3948, 38, 47, None, "50 Amp RV Sites", "Fisherman's Landing (City of Muskegon): 50-amp RV sites $38 a night, pull-through $44, waterfront $47."),
 (3949, 45, 45, None, "Campsite Fee: $45/day", MUSK.format(45)),
 (3953, 45, 45, None, "$45.00 per day", "Muskegon County: campsites $45 a night, May 15 - September 15."),
 (3955, 52, 52, None, "Campsite Fee: $52/day", MUSK.format(52)),
 (3951, 31, 36, None, "Campsite (Electric) | $36", "Newaygo County: electric sites $36 Thu-Sun, $31 Mon-Wed; rustic $18-23."),
 (3965, 25, 41, None, "Campsite Full-hookup", "Newaygo County: electric $25-30, water and electric $31-36, full hookup $36-41 (lower rate Mon-Wed); rustic $15-20."),
 (3954, 47, 47, None, "$47 per day", "City of Fremont 2026: transient lots with sewer, water and electric $47 a day, $280 a week."),
 (3963, 28, 28, None, "Improved Campsites (with water and electric)", "Tuscola County: water and electric sites $28 a night."),
 (3966, 28, 30, None, "30 amp | Nightly | 28", "Finn Road Park (Hampton Township): 30-amp $28 a night, 50-amp $30."),
 (3969, 55, 70, None, "$55 - Deluxe", "John Gurney Park (Village of Hart): water and electric $55 a night, full hookup $70, rustic $40."),
 (3970, 50, 50, None, "Full Hookup | $50 per night", HURON.format("full hookup $50 a night, rustic $31,")),
 (3972, 42, 50, None, "Electric Only | $", HURON.format("electric $42 a night, electric lakeview $45, full hookup $50,")),
 (3982, 42, 50, None, "Electric Only | $", HURON.format("electric $42 a night, electric lakeview $45, full hookup $50,")),
 (3983, 55, 78, None, "Electric and Water | $55", HURON.format("electric and water $55 a night, full hookup $73, lakefront full hookup $78,")),
 (3987, 50, 50, None, "Full Hookup | $50 per night", HURON.format("full hookup $50 a night,")),
 (3988, 42, 50, None, "Electric or Electric Lakeview", HURON.format("electric $42-45 a night, full hookup $50, rustic $31,")),
 (3976, 33, 33, None, "Campsite, modern", "Bay County: modern campsites $33 a night."),
 (3994, 45, 45, None, "Modern Sites are $45", "Richfield Township: modern sites with 20/30/50-amp and water $45 a night, rustic $25."),
 (3995, 30, 30, None, "Sites with Electric", "Village of Kaleva: electric sites $30 a night, rustic $20."),
 (4001, 45, 55, None, "$55 per night", "Whitewater Township 2026: $55 a night May 22 - Sept 7, $45 Sept 8 - Oct 25."),
 (4004, 25, 30, None, "Nightly: $30", "Emerick Park (Village of Hale): 30-amp and water $25 a night, full hookup $30."),
 (4009, 35, 35, None, "$35 Nightly", "Village of Ellsworth: 45 water-and-electric sites $35 a night, tents $25."),
 (4012, 30, 30, 10, "ELECTRIC SITES: $30", MENO.format(", primitive $20")),
 (4014, 30, 30, 10, "ELECTRIC SITES: $30", MENO.format(", non-electric $20")),
 (4015, 30, 30, 10, "ELECTRIC SITES : $30", MENO.format("")),
 (4013, 35, 50, 8, "Full Hookup $40.00 $50.00", "City of Petoskey 2026: electric only $35 a night ($45 Memorial Day - Labor Day), full hookup $40 ($50); $8 transaction fee."),
 (4016, 40, 45, None, "Basic (Electric &Water ONLY)", "Delta County: electric and water $40 a night, full hookup or river/lake view $45; rustic tent $25."),
 (4017, 15, 15, None, "camping fee: $15.00", "Village of Powers: 14 rustic sites, $15."),
 (4022, 45, 45, None, "Daily - $45", "Iron County 2026: $45 a day."),
 (4025, 30, 30, None, "Non-Dickinson County", "Sagola Township: $30 a night, rustic $15."),
 (4026, 30, 30, None, "Electric Sites | $30/night", "Trout Lake Township 2026: electric sites $30 a night, non-electric $20."),
 (4031, 20, 20, None, "Rustic Camping with electric", "Tahquamenon Logging Museum: electric sites $20 a night plus tax, tents $10."),
 (4032, 30, 30, None, "Nightly $30.00 $30.00", GOG.format(30)),
 (4043, 35, 35, None, "Nightly $35.00 $35.00", GOG.format(35)),
 (4042, 25, 25, None, "Sites with hookups", "Bergland Township: sites with hookups $25 a night."),
 (4047, 28, 43, None, "https://ontonagontownshippark.com/rates-and-rules", "Ontonagon Township: sites $28 a night, lake sites $33, lake sites 65-70 $43 ($5 less for township residents); tents $23."),
 (4048, 60, 60, None, "Daily rate: $60", "City of Houghton: $60 a night daily, $55 by the week, $50 by the month."),
]
pages = [json.loads(l) for l in open("mi_pages.jsonl")]
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
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_mi_2026-10-15/mi_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
