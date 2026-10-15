"""BC local findings from bc_pages.jsonl (operators' own pages, read 2026-10-15), CAD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
 (8574, 25, 25, None, "Fees | $25/night", "Capital Regional District: $25 a night, no hydro; additional vehicle $10."),
 (8575, 58, 58, 3, "A rate of $44 per site", "Town of Lake Cowichan: $44 a site plus $14 for power ($58 powered); $3 booking fee."),
 (8576, 25, 25, None, "Fees | $25/night", "Capital Regional District: $25 a night; additional vehicle $10."),
 (8578, 47, 55, None, "Partial Hook-up", "Fraser Valley Regional District: water and 30-amp $47 a day, full hookup $55, plus GST; tents $37."),
 (8584, 20, 20, None, "user fee of $20 per night", "Village of Salmo: $20 a night per sleeping unit, first come, first served."),
 (8585, 15, 20, None, "$15.00-$20.00 /night/vehicle", "Village of Fruitvale listing for the RDKB park: $15-20 a night per vehicle."),
 (8586, 15, 25, None, "Individual Campsite (Peak Season", "Village of Gold River (GST included): $25 a night in peak season (June 15 to Labour Day), $15 off-peak, $7.50 off-peak seniors."),
 (8588, 44, 52.50, None, "Power only (tent)", "2026 rates including GST: water, power and sewer (30-amp) $52.50 a night, power only $44, no services $42."),
 (8591, 50, 55, None, "Power & Water- $50", "Power and water $50 a night in low season, $55 high season (June 12 to September 13); non-serviced and tents $35-40."),
 (8592, 15, 32, None, "15 and 30 amp hook-ups ($32", "District of Logan Lake: 15/30-amp sites $32 a night, unpowered $28, $15 in shoulder season; one-time $7 resort fee a stay."),
 (8593, 39, 49, None, "Powered with Water Campsites", "Village of Nakusp (taxes included): powered $39-46 a night, powered with water $42-49 (high season June 15-August 31); booking fee applies."),
 (8595, 39, 39, None, "30 AMP Service: $39/night", "30-amp sites $39 a night, no service $29, tents $23."),
 (8598, 45, 45, None, "Serviced Campsite (15 amps)", "Town of Smithers 2026: serviced (15 or 30 amp) $45 a night, unserviced $35, tents $28."),
 (8602, 23.10, 33.60, None, "Full Service Site", "District of Mackenzie (GST included): full service with 50-amp $33.60 a night, 30-amp power only $23.10, non-serviced $17.85."),
 (8606, 20, 20, None, "may be reserved in advance for $20/night", "Northern Rockies Regional Municipality: 25 unserviced sites $20 a night including tax and firewood."),
 (8647, 40, 40, None, "$40 full or partial service 20amp", "Full or partial service (20-amp) $40 a night, unserviced $30."),
 (8656, 30, 30, None, "Individual sites : $30 per unit", "qathet Regional District: $30 a unit a night (fees as of July 1, 2024)."),
 (8659, 42.83, 47.46, None, "Full Hook ups", "City of Merritt: full hookups $42.83 a day, pull-through $47.46, non-serviced $33.08, plus GST."),
 (8666, 43, 55, None, "15-amp electricity: $43.00", "Village of Kaslo 2026: 15-amp $43 a night, 30-amp $50, 30-amp with sewer $55; unserviced $38."),
 (8683, 40, 40, None, "RV sites: $ 40.00 / night", "Village of Ashcroft: RV sites $40 a night, $220 a week; tents $20."),
 (8685, 43, 53, None, "Full-Service Campsites", "Single service $43-48 a night, full service $48-53 (high season June 12 to September 13); non-serviced $35-40; taxes included."),
 (8691, 43, 43, None, "$43.00/day Additional person", "Lumby Lions: $43 a day."),
 (8732, 40, 47, None, "30 AMP Full Service (Sites 1-49)", "Williams Lake Stampede: 30-amp full service $40 a night, 50-amp full service $47."),
 (8748, 34.65, 34.65, None, "Electrical site (serviced) per night", "City of Terrace: electrical sites $34.65 a night, non-electric $25.40, taxes not included."),
 (8785, 39, 56, None, "50 Amp: $56", "Power and water $39-46 a night, full hookups $51-56; dry camping $35."),
]
pages = [json.loads(l) for l in open("bc_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_bc_2026-10-15/bc_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
