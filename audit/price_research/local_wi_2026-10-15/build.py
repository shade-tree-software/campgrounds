"""WI local findings from wi_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY,
or the URL given when KEY starts with http (a peek at the same page, 2026-10-15)."""
import json
WASHB = "Washburn County: full hookups $35 a night, water and electric $30, electric $25, no hookups $20; $8 reservation fee."
DODGE = "Dodge County: electric sites $30 a night, non-electric $20; $6 reservation fee."
DANE = "Dane County 2026: electric sites $38 a night, non-electric $25; $2 off for seniors, military and veterans; $10 administration fee per reservation."
MARI = "Marinette County: electric sites $35 a night, $30 on Tuesdays and Wednesdays; $10 reservation fee; 2.5% card fee."
ADAMS = "Adams County 2026: camper/RV $25 a night, premium/lakefront $30, including 2 car passes."
WOOD = "Wood County 2026: electric sites $27 a night, waterfront $30, sewer and water $40, non-electric $22; $10 reservation fee."
BARRON = "Barron County: electric sites $30 a day."
BROWN = "Brown County: water and electric sites $34 a night, rustic $22."
JUN = "Juneau County 2026: electric sites $25 a night, non-electric $20, vehicle pass included; $10 reservation fee."
CHIP = "Chippewa County: sites $20 a night plus $7 for 20/30/50-amp electricity."
CLARK = "Clark County: campsites {} a night; park use free; $10 reservation change fee."
FDL = "Fond du Lac County: $28 a night; $6 reservation fee."
DOUG = "Douglas County: electric sites $25 a night, electric and water $30, non-electric $20."
PRICE = "Price County: $30 a night, cash or check at the campground."
ROWS = [
 (3411, 45, 45, None, "Camping fees are $45.00", "Village of Minong: 20 full-hookup RV sites $45 a night, tents $20."),
 (3532, 25, 35, 8, "Camping rates are $35", WASHB),
 (3570, 25, 35, 8, "Camping rates are $35", WASHB),
 (3447, 35, 35, None, "https://amerywisconsin.org/622/North-Park-RV-Campground", "City of Amery: 8 improved sites with 50-amp, water and sewer, $35 a night; book through City Hall."),
 (3451, 25, 30, None, "Nightly camper/RV $25", ADAMS),
 (3491, 25, 30, None, "Nightly camper/RV $25", ADAMS),
 (3452, 27, 40, 10, "Electric S", WOOD),
 (3558, 27, 40, 10, "Electric S", WOOD),
 (3597, 27, 40, 10, "Electric S", WOOD),
 (3458, 30, 35, None, "$30.00 a night for camping", "Village of Avoca: electric only $30 a night, electric and water $35; payment box."),
 (3459, 45, 45, None, "https://baycitywi.gov/lodging/bay-city-campground/", "Village of Bay City: 44 full-hookup sites $45 a day, $300 a week; tents $25."),
 (3461, 30, 30, None, "Rates: $30.00 per site", "City of Bayfield: $30 a site, electric hookups; no refunds."),
 (3462, 30, 30, 6, "Electric Sites - $30", DODGE),
 (3473, 30, 30, 6, "Electric Sites - $30", DODGE),
 (3504, 30, 30, 6, "Electric Sites - $30", DODGE),
 (3510, 30, 30, 6, "Electric Sites - $30", DODGE),
 (3463, 45, 45, None, "Daily | $45", "Village of Birchwood: $45 a day including electric and sales tax, $250 a week; tents $20."),
 (3468, 33, 33, 10, "https://www.danecountyparks.com/about/fees", "Dane County 2026: Brigham (rustic, no showers) electric sites $33 a night, non-electric $23; $10 administration fee per reservation."),
 (3480, 38, 38, 10, "https://www.danecountyparks.com/about/fees", DANE),
 (3517, 38, 38, 10, "https://www.danecountyparks.com/about/fees", DANE),
 (3522, 38, 38, 10, "https://www.danecountyparks.com/about/fees", DANE),
 (3530, 38, 38, 10, "https://www.danecountyparks.com/about/fees", DANE),
 (3469, 30, 30, None, "electricity is $30 per day", BARRON),
 (3543, 30, 30, None, "electricity is $30 per day", BARRON),
 (3475, 35, 35, 10, "Camper Sites ($35/Night)", "Forest County: camper sites $35 a night plus tax, tents $20; $10 registration fee."),
 (3476, 30, 35, 10, "Electric Sites: $35.00/night", MARI),
 (3477, 30, 35, 10, "Electric Sites: $35.00/", MARI),
 (3548, 30, 35, 10, "Electric Sites: $35.00/night", MARI),
 (3484, 20, 20, 10, "Rustic Sites: $20.00", "Marinette County: rustic sites $20 a night (no hookups); $10 reservation fee."),
 (3481, 34, 34, None, "All sites $34/night", BROWN),
 (3544, 34, 34, None, "Water & Electric Sites: $34", BROWN),
 (3579, 34, 34, None, "Water & Electric Sites: $34", BROWN),
 (3482, 22, 25, None, "Water & Electricity Only", "City of Dorchester: water and electric $22 a night, full-hookup 50-amp pull-throughs $25; tents $12."),
 (3483, 25, 25, None, "first come, first served at $25.00", "Drummond Lake Campground (late season): electric-only sites $25 a night, first come, first served."),
 (3489, 40, 40, None, "$40.00 per night", "Fond du Lac County Fairgrounds RV park: $40 a night."),
 (3518, 28, 28, 6, "Camping Fee: $28.00", FDL),
 (3590, 28, 28, 6, "Camping Fee: $28.00", FDL),
 (3495, 20, 20, None, "Sites with Electric | $20", "Village of Gratiot: electric sites $20 a night."),
 (3497, 24, 35, None, "range from $24 to $35", CLARK.format("$24-35")),
 (3527, 24, 37, None, "range from $24 to $37", CLARK.format("$24-37")),
 (3594, 24, 37, None, "range from $24 to $37", CLARK.format("$24-37")),
 (3541, 30, 30, None, "range from $30", CLARK.format("$30")),
 (3559, 24, 30, None, "range from $24 to $30", CLARK.format("$24-30")),
 (3503, 27, 27, None, "Electricity is $7.00", CHIP),
 (3542, 27, 27, None, "Electricity is an addit", CHIP),
 (3573, 27, 27, None, "Electricity is $7.00", CHIP),
 (3507, 35, 35, None, "Daily | $25 | $35", "Bayfield County: electric sites $35 a day, non-electric $25."),
 (3508, 35, 35, None, "Daily | $25 | $35", "Bayfield County: electric sites $35 a day, non-electric $25."),
 (3509, 35, 35, None, "https://townofironriver.com/moon-lake-park-campground/", "Town of Iron River: daily with electric $35 plus 5.5% sales tax, tents $25."),
 (3513, 20, 20, None, "Camping fee required - $20.00", "Price County: $20 a night, no hookups."),
 (3553, 30, 30, None, "$30.00 per night", PRICE),
 (3514, 20, 20, None, "$20 per RV site", "Village of La Farge: 16 electric sites $20 a night, self-service; tents $10."),
 (3515, 45, 45, None, "Electric Sites - $45", "Town of La Pointe (Big Bay Town Park): electric sites $45 a night plus sales tax."),
 (3516, 30, 30, None, "Electrical hookup sites are available for $30", "Village of Lake Nebagamon: 6 electric sites $30 a day."),
 (3519, 40, 40, None, "Camping cost is $40", "Manitowoc County Expo: $40 a night, $240 a week; not available during large events."),
 (3520, 20, 20, None, "$20.00 / night per site", "City of Marinette: nine sites $20 a night."),
 (3521, 25, 30, 10, "Electric- $25.00", JUN + " Some Castle Rock sites $30."),
 (3540, 25, 25, 10, "Electric- $25.00", JUN),
 (3546, 15, 15, None, "Camping is allowed in the park for $15", "Juneau County: camping $15 a night, self-registration; 14-night limit."),
 (3523, 15, 15, None, "Fee is $15.00 per day", "City of Medford: $15 a day, first come, first served; 14-day maximum."),
 (3534, 40, 40, None, "Campers: $40.00", "Green County Fair: campers $40 a night, tents $30; first come, first served."),
 (3538, 25, 25, None, "$25 per night on an electric site", "Village of Muscoda: electric sites $25 a night; Passport America $12.50."),
 (3547, 35, 35, None, "Campsites are $35 per night", "City of New Richmond: $35 a night."),
 (3555, 35, 40, None, "Campsite Rates (NO SEWER)", "City of Peshtigo: water and electric $35 a night, with sewer $40."),
 (3557, 30, 30, None, "The nightly rate is $30", "City of Phillips: electric sites $30 a night, first come, first served."),
 (3565, 30, 30, None, "Electric site fee is $30", "City of River Falls: electric sites $30 a night; online reservations."),
 (3569, 35, 40, None, "Water/electric sites $35/night", "Shawano County 2026: water and electric $35 a night, holidays $40 (2027: $40/$45); electric-only tent/pop-up sites $30."),
 (3571, 25, 25, None, "Electric sites: $25.00", "Village of Soldiers Grove: electric sites $25, non-electric $23."),
 (3572, 25, 30, None, "Electric site: $25.00/night", DOUG),
 (3575, 27, 27, None, "$27 per night", "Village of Stockholm: RV camping with electricity $27 a night, $150 a week; tents $20."),
 (3582, 25, 25, None, "RV & Tent Camping: $25", "Village of Turtle Lake: water and electric $25 a night, first come, first served."),
 (3586, 30, 30, None, "Camper & RV | $30.00", "Vernon County Fair: camper and RV $30 a day, tents $15."),
]
pages = [json.loads(l) for l in open("wi_pages.jsonl")]
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
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_wi_2026-10-15/wi_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
