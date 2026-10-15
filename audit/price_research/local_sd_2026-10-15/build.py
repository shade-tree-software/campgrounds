"""SD local findings from sd_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(5816, 22, 22, None, "The fee is currently $22/night", "City of Fort Pierre: water and electric pads $22 a night, first come, first served."),
 (5820, 16, 25, None, "$25 per night during May through October", "City of Pierre: $25 a night May-October, $16 November-April."),
 (5822, 33, 33, None, "$33 Hook-up: electricity, water, sewer", "City of Huron: full hookup $33 a night, no hookup $22; $198 a week."),
 (5825, 20, 20, None, "Hav-A-Rest Park & Campground fees: $20.00", "City of Redfield: $20 a night (effective April 1, 2021)."),
 (5836, 10, 10, None, "if electricity is needed the cost is just $10.00", "City of Arlington: electricity $10 a night; non-electric pads and tents free."),
 (5846, 41, 41, None, "RV Sites With Hookups (See Map)", "City of Mitchell: RV sites with hookups $41 a night plus local fees and taxes; tents $26-28."),
 (5850, 30, 45, 7, "Pads (Campers/Tents)", "City of Watertown: pads $30 a night, full service $45, plus tax; $7 online booking fee ($10 by phone)."),
 (5852, 25, 30, None, "Camping Fees are $25.00 per night", "Brown County: water and power $25 a night, with sewer $30; closed during the county fair."),
 (5854, 22, 36, None, "$22 for 30- & 50-amp service", "City of Colman 2026: 30/50-amp sites $22 a day, with water and sewer $36."),
 (5859, 20, 20, None, "Rate w electricity: $20/night", "City of De Smet: electric sites $20 a night, others $10."),
 (5861, 20, 20, None, "CAMPING FEES: Cost is $20.00 per night", "City of Flandreau: $20 a night, tents $7; no reservations."),
 (5864, 25, 25, None, "Cost: $25 per night", "City of Castlewood: $25 a night."),
 (5868, 32, 32, None, "The RV camping fees are $32 per day", "City of Aberdeen: 50-amp RV sites $32 a day including tax, tents $22."),
 (5871, 10, 10, None, "also some electrical hookups at Durkee Lake", "City of Faith: electrical sites $10 a night, first come, first served."),
 (5874, 25, 25, None, "$25.00/NIGHT", "City of Webster: RV hookups $25 a night, first come, first served."),
 (5877, 25, 30, None, "Camping fees: $30 per day", "City of Clear Lake: water and electric $25 a day, full hookup $30, tents $20."),
 (5879, 25, 30, None, "Camping fees: $30 per day", "City of Clear Lake: water and electric $25 a day, full hookup $30, tents $20."),
]
pages = [json.loads(l) for l in open("sd_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_sd_2026-10-15/sd_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
