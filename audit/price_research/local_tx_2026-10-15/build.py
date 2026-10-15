"""TX local findings from tx_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note."""
import json
TRAVIS = "Travis County Parks: water-and-electric sites $30 a night plus day-use entry ($5 a person, $3 seniors); cash only at the booth."
CS = "Lake Cypress Springs (Franklin County WD), effective 2025-07-15: Walleye RV regular $50 a night, premium $65; seniors $40/$55; tents $25."
ROWS = [
 (7201, 30, 30, None, None, TRAVIS),
 (7203, 20, 20, None, None, "City of Ballinger: RV connections $20 a day."),
 (7209, 30, 30, None, None, "Angelina County: overnight camping $30; day use $5."),
 (7210, 40, 40, None, None, "Castroville Regional Park: $40 a day, $200 a week; monthly $475-525."),
 (7211, 15, 15, None, None, "City of Childress: $15 a night in the drop box; up to 3 days; first come, first served."),
 (7213, 0, 0, None, None, "City of Lamesa: free for up to 4 days, then $20 a day; 30-amp outlets."),
 (7221, 20, 30, None, None, "City of De Leon: full hookups, 30-amp $20 a day, 50-amp $30 ($2 off for seniors); $350 a month."),
 (7224, 20, 25, None, None, "City of Austin: water-and-electric sites $20 a night, waterfront $25 (32-ft maximum); primitive $10; vehicle entry $5 weekdays."),
 (7249, 50, 65, None, None, CS),
 (7257, 52, 59, 3.5, None, "City of Fredericksburg: tier-two sites $52 a night, tier-one pull-throughs $59; $3.50 Firefly reservation fee; tents $10."),
 (7259, 20, 35, None, None, "City of Bryan: electric-only sites $20 a night, water and electric $35 (higher on Aggie football weekends); 30-ft and under; day entry $5 a person."),
 (7262, 45, 45, None, None, "City of The Colony: RV camping with daily entrance $45 non-resident ($35 resident); tents $25; 14 days in 30."),
 (7266, 20, 20, None, None, "City of Sweetwater: lakeside water-and-electric sites $20 a night, $10 without hookups (some areas $10 with hookups); call to reserve."),
 (7273, None, None, None, None, None),
 (7274, 38.5, 38.5, None, None, "Log Cabin RV Park: water and electric $38.50 plus tax a night, $220 a week; tents $22-33; 4% card fee."),
 (7278, 15, 15, None, None, "City of Memphis: $15 a night; check availability with the police department."),
 (7283, 25, 25, None, None, "Old Fort Parker: 30/50-amp sites with water $25 a day, 14-day limit; dry camping $5; fort entry extra."),
 (7285, 50, 65, None, None, CS),
 (7286, 30, 30, None, None, TRAVIS),
 (7290, 15, 20, None, None, "City of Pampa: $15 a night Sunday-Thursday, $20 Friday-Saturday, paid at the drop box."),
 (7292, 45, 45, None, None, "Highland Village: improved camping $45 a night non-resident ($35 resident); vehicle admission $15 a day."),
 (7293, 15, 20, None, None, "City of Coleman: full hookups $20 a day, electric $15, primitive $10."),
 (7299, 30, 45, None, None, "Riverside Park: Wilderness (electric and water) $30 a day, Colorado Cove (full hookup) $45."),
 (7309, 40, 40, None, None, "SeaWind RV Resort: $40 a night, $200 a week; cash only at the office."),
 (7321, 35, 55, None, None, "Town of Flower Mound: water and electric $35 a night, full hookup $45, pull-through $55; vehicle entry $10 a day."),
 (7324, 15, 15, None, None, "City of Victoria: $15 a night with full utilities; 18 pull-throughs."),
 (7325, 50, 65, None, None, CS),
 (7339, 35, 35, None, None, "City of Winnsboro: water and electric $35 a day, $150 a week."),
 (7341, 25, 30, None, None, "Wise County: electric and water $25 a night, full hookup $30; rough camping $10."),
 (7554, 25, 25, None, None, "Harris Street RV Park: $25 a day per space, up to 7 consecutive days."),
 (7610, 30, 40, None, None, "Lake Hawkins RV Park: $30 a night weekdays, $40 weekends (2-night minimum), $50 holidays (3-night minimum)."),
 (7270, 0, 0, None, None, "City of Levelland: free for 3 nights with water and electric, then $25 a day by permit up to 10 days."),
 (7732, 0, 0, None, None, "City of Muleshoe: free with water, sewer and 50-amp electric; extra days $25 by permit."),
 (7907, 30, 30, None, None, "City of Littlefield: $30 a day, paid at City Hall; 10 days in 30; no tents."),
]
pages = {}
for l in open("tx_pages.jsonl"):
    x = json.loads(l)
    for p in x.get("pages", []):
        if p.get("lines"):
            pages.setdefault(x["id"], p["url"])
out = []
for i, lo, hi, rf, src, note in ROWS:
    if lo is None:
        continue
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": (src or pages[i]) + " (audit/price_research/local_tx_2026-10-15/tx_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
