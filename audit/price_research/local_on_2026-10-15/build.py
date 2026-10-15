"""ON local findings from on_pages.jsonl (operators' own pages, read 2026-10-15), CAD. python3 -I build.py > findings.json
low/high = RV (hydro/hookup) sites; unserviced/tent in the note. Source = first page whose rate lines contain KEY,
or the URL given when KEY starts with http (a peek at the same page, 2026-10-15)."""
import json
LPRCA = "Long Point Region CA 2026: hydro 15-amp $58.50 a night, 30-amp $66.50, with sewer $70.50-78; unserviced $43; 20% off for seniors; $16 online reservation fee."
NPCA = "Niagara Peninsula CA (HST included): 15-amp $64.57 a night, premium $70.13, 30-amp $72.91, premium $75.69; non-serviced $59.02; $13 reservation fee."
ROWS = [
 (8264, 58.50, 78, 16, "https://www.lprca.on.ca/outdoor-recreation/camping/", LPRCA),
 (8291, 58.50, 78, 16, "https://www.lprca.on.ca/outdoor-recreation/camping/", LPRCA),
 (8266, 52, 52, None, "https://www.otonabeeconservation.com/conservation-areas/warsaw-caves-conservation-area/", "Otonabee Conservation: unserviced campsites $52 a night."),
 (8285, 55.45, 55.45, None, "Camping Fees (+HST)", "TRCA: 30-amp hydro and water $55.45 a night plus HST, unserviced $48.30."),
 (8288, 64.57, 75.69, 13, "Camping 15Amp (single night)", NPCA),
 (8296, 64.57, 75.69, 13, "Camping 15Am", NPCA),
 (8300, 60, 60, None, "Serviced sites are $60.00", "Northern Bruce Peninsula: serviced transient sites (hydro, water, sewer) $60 a night including HST, unserviced $48."),
 (8306, 43.47, 61.43, None, "Per night 15 amp", "Town of New Tecumseth 2026: 15-amp $43.47 a night, 30-amp $61.43, plus tax; non-serviced $43.47."),
 (8310, 96, 96, None, "Recreational vehicle (with 30-amp servi", "Marmora and Lake 2026: RV with 30-amp $96 a day, tents $72."),
 (8311, 39.91, 39.91, None, "Daily | Electricity | $39.91", "Town of Thessalon: electric sites $39.91 a day before HST, no electricity $31.93."),
 (8312, 45, 45, None, "SERVICED SITE", "Bruce Mines: serviced sites $45 a day, tents $25, taxes included."),
 (8317, 60, 60, None, "Daily Electrical Sites", "Town of Marathon: electrical sites $60 a day, non-electrical $32."),
 (12640, 61, 64, None, "Campsite, 30-amp service/night", "Otonabee Conservation: 30-amp sites $61 a night, 50-amp $64, unserviced $52."),
 (12714, 55.57, 74.47, 15, "Interior H&W", "Town of Cobourg 2026: interior hydro and water $55.57, with sewer $58.91, waterfront $70.02-74.47; tents $50.02; $15 reservation fee."),
]
pages = [json.loads(l) for l in open("on_pages.jsonl")]
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
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_on_2026-10-15/on_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
