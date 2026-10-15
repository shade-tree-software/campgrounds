"""IL local findings from il_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(1765, 25, 50, None, "(Thu. – Sat. Nights)", "Forest Preserves of Cook County: April-October $40 Thursday-Saturday and $35 Sunday-Wednesday for county residents ($50/$45 non-residents); November-March $25 ($35)."),
 (1766, 26, 41, None, "Improved camp site (with electric and water)", "Forest Preserve District of Kane County: electric and water $26 a day for county residents, $41 non-residents; primitive $18/$24."),
 (1768, 25, 40, None, "DuPage Resident $25/night", "Forest Preserve District of DuPage County: $25 a night for residents, $40 non-residents."),
 (1775, 25, 40, None, "Sunday-Thursday Campsite", "Champaign County Forest Preserve District: $25 Sunday-Thursday, $30 Friday-Saturday, $40 holidays."),
 (1776, 25, 30, None, "$25 for 30 amp service and $30 for 50 amp", "Macon County Conservation District: 30-amp $25 a day, 50-amp $30."),
 (1779, 20, 20, None, "The rate per night is currently $20.00", "City of Gibson City: $20 a night, paid through Campspot."),
 (1782, 20, 20, None, "Camping fees are $20 per night", "Village of Arthur: $20 a night."),
 (1783, 25, 25, None, "There is a $25.00 per day fee", "City of Robinson: 50/20-amp sites $25 a day."),
 (1786, 25, 25, None, "RV Camping is $25", "Village of Karnak: RV camping $25 a night, tents $21; $20 deposit to reserve."),
 (1788, 45, 50, None, "Bicentennial and Equestrian RV Camps", "City of Litchfield: RV sites $45 a day, $50 on holidays (two-night minimum), $250 a week."),
 (1791, 30, 30, None, "Rates - $30 per night", "Carthage Park District: $30 a night, $180 a week."),
 (1792, 13, 13, None, "Prices are $13 per night", "City of Kewanee: $13 a night or $78 for 7 nights."),
 (1794, 22, 25, None, "River front is $25.00 a night", "City of Keithsburg: water and electric $22-25 a night (riverfront $25), full hookup $25."),
 (1795, 30, 30, None, "RV, Trailers, Motor Homes $30.00", "City of New Boston: RVs $30 a day, $100 a week; tents $15."),
 (1796, 20, 20, None, "1 Night…..$20.00", "City of Warsaw: campers $20 a night, multi-night discounts; tents $7."),
 (1799, 25, 25, None, "Per Day Camping: $", "City of Roodhouse: campers/RVs $25 a day, $125 a week; tents $10."),
]
pages = [json.loads(l) for l in open("il_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_il_2026-10-15/il_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
