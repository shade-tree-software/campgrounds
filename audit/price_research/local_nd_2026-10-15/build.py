"""ND local findings from nd_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note."""
import json
ROWS = [
 (5927, 30, 30, None, "https://www.bisparks.org/facilities/general-sibley-park-campground/", "Bismarck Parks and Recreation: RV sites with electricity $30 a night, tent sites $15."),
 (5930, 55, 55, None, "https://www.redrivervalleyfair.com/p/fair-fun/campground", "Red River Valley Fair 2026: $55 a night plus fees and taxes; full hookups $1,150 a month."),
 (5932, 30, 30, None, "https://dickinsonparks.org/patterson-lake-recreation-area/", "Dickinson Parks: modern (electric, water) sites $30 a night May 8 - Oct 13, 2026, reserved in advance, daily entrance included; primitive $20. 14 days in 30."),
 (5951, 15, 15, None, "https://www.williamsnd.com/mcgregor-dam/", "Williams County: 17 electric sites $15 a night, primitive $10; cash or check, first come, first served."),
 (5955, 38, 38, None, "https://www.fargoparks.com/lindenwood-campground", "Fargo Parks: $38 a night including electricity and water; back-in sites."),
 (5956, 35, 35, None, "https://buffalond.com/buffalo-rv-park", "City of Buffalo: $35 a night, $200 a week, $500 a month; booked through Firefly Reservations."),
 (5960, 25, 25, None, "https://webreserv.com/lewisandclarkrvparknd", "Hazen Parks: short-term sites $25 a night, $150 a week. Open early May to September 30."),
 (5963, 30, 30, 3, "https://www.co.ward.nd.us/517/Old-Settlers-Park", "Ward County: RV sites $30 a night, tent $20; $3 service fee per online reservation; $10 to cancel."),
 (5965, 35, 35, None, "https://www.wahpetonparks.com/parks/campgrounds/", "Wahpeton Parks: $35 a night, paid in advance online; tents $20."),
 (5967, 30, 30, None, "https://graftonparks.com/leistikow-park-campground", "Grafton Parks: RV sites $30 a night, $155 a week, $465 a month; tents $10-15."),
 (5972, 25, 25, None, "https://pembina.govoffice.com/?SEC=4FB0691A-91D4-4AA2-A473-DEA20F6EA88F", "City of Pembina: 14 RV spaces with water, sewer and 30/50-amp, $25 a night; tents $10; first come, first served."),
 (5976, 25, 25, None, "https://sargentnd.com/dept_silver_lake_rec.php", "Sargent County: RV sites $25 a night ($100 a week); primitive area $15 for RVs, tents $10; no reservations. May 1 - October 1."),
 (5985, 25, 25, None, "https://www.beulahparks.com/parks-campgrounds/riverside-park/", "Beulah Park District: electric sites $25 a night, primitive $10, paid in full when booked; 7-day limit."),
 (5987, 20, 20, None, "https://anamoose.com/recreation.php", "City of Anamoose: two water and electric sites, $20 a day."),
 (5999, 35, 35, None, "https://mintocityparks.com/campground", "Minto Park Board: full-hookup sites $35 a day, $225 a week, $750 a month; pay at the drop box."),
 (6000, 25, 25, None, "https://www.renvillecountynd.org/community/mouse-river-park/", "Renville County: $25 a night, $150 a week, $500 a month; a reservation fee applies."),
 (6002, 25, 25, None, "https://www.cityofcando.com/campground-swimming-pool-city-park", "City of Cando: full and partial hookups $25 a day ($150 a week), primitive $15; self-register."),
 (6003, 20, 25, None, "https://mohallndak.com/", "City of Mohall: water and electric $20 a night, full hookup $25, tents $10; envelopes and drop box."),
 (6017, 35, 35, None, "https://www.surreynd.org/lodging-camping", "City of Surrey: RVs $35 a day, tents $10; pre-register with City Hall."),
 (6018, 20, 20, None, "https://www.bisparks.org/facilities/eagles-park-campground/", "Bismarck Parks and Recreation: 9 RV sites with 50-amp and 60-ft gravel pads, $20 a night, cash or check, first come, first served; reservable tent sites $12."),
 (6025, 24, 24, None, "https://laketschida.org/camping-fees", "Lake Tschida (Tri-Cities JJDA): electric sites $24 a night, primitive $14."),
 (6026, 20, 20, 3, "https://www.williamsnd.com/reserve-a-campsite/", "Williams County 2026: electric and water sites $20 a night, online only May-September; $3 service fee plus a card fee."),
 (6027, 35, 45, None, "https://mcville.com/parks", "City of McVille: RV water/electric $35 a day, full hookup $45; primitive $10; self check-in at the dam."),
 (6028, 25, 25, None, "https://www.milnornd.com/camping", "Milnor Park District: $25 a night, $125 a week; first come, first served."),
 (6035, 25, 25, None, "https://www.barnescounty.us/index.php/clausen-springs/", "Barnes County: electric sites $25 a night, primitive $20; reservable."),
 (6038, 25, 25, None, "https://www.newtownmarina.com/camping", "New Town Marina: electric RV sites (30/50-amp) $25 a day, electric tent sites $15."),
 (6045, 10, 10, None, "https://www.stutsmancounty.gov/departments/parks/campground-policies/", "Stutsman County: primitive only (no electric or water), $10 a night; dump station."),
 (6049, 35, 35, None, "https://draytonnd.com/park-facilities", "City of Drayton 2026: campers $35 a night ($150 a week), tents $20."),
 (6050, 30, 30, None, "https://tolnand.govoffice.com/camping", "City of Tolna: campers $30 a night, $200 a week; tents $15; book by phone."),
]
out = []
for i, lo, hi, rf, src, note in ROWS:
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": src + " (audit/price_research/local_nd_2026-10-15/nd_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
