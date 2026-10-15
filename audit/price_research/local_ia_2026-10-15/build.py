"""IA local findings from ia_pages.jsonl (operators' own pages, read 2026-10-15). python3 -I build.py > findings.json
low/high = RV (electric/hookup) sites; tent/primitive in the note. Source = first page whose rate lines contain KEY."""
import json
ROWS = [
 (2965, 20, 20, None, "Campers & motor homes", "City of Adair: campers and motor homes $20 a night, tents $6; first come, first served."),
 (2978, 30, 30, None, "Camping fees: $30 per night", "City of Emmetsburg: 21 full-hookup 30/50-amp sites $30 a night, drop-box payment."),
 (2984, 20, 20, None, "RV Camping is $20", "City of Sheldon: RV camping $20 a night, tents $10."),
 (2993, 25, 25, None, "RV: $25/Night", "Mike Macke Memorial Park: RV $25 a night, tents $10."),
 (2996, 25, 25, None, "The price is $25 per night", "Monona County Fair off-season camping: $25 a night, water and electric, no sewer."),
 (3002, 15, 15, None, "Electric/water sites are $15", "Page County Conservation: electric and water sites $15 a night, primitive $6."),
 (3014, 22, 22, None, "Daily Rate Spring/Summer Rate", "City of Fonda (May 2025 rates): RV/camper sites $22 a day."),
 (3020, 25, 35, None, "RATES/NIGHT", "City of Le Mars: north sites (electric, water) $25 a night, south sites (with sewer) $30, beach sites $35; tents $20."),
 (3030, 15, 15, None, "$15.00 per night for campers", "City of Casey: campers and RVs $15 a night, tents $10; first come, first served."),
 (3064, 40, 40, None, "RV camping will be $40", "Quarry Springs Park: RV camping $40 a night, primitive $15."),
 (3079, 25, 25, 5, "$25 per night for sites 1 to 40", "City of Winterset: sites 1-40 $25 a night, tents $15; $5 reservation fee."),
 (3090, 25, 25, None, "RV Sites $25.00 per evening", "City of Nashua: water and electric RV sites $25 a night, tents $15."),
 (3092, 25, 30, None, "Electric and Water - $25", "City of Evansdale: electric and water $25 a day, full hookup $30, non-electric $20; cash only."),
 (3094, 20, 20, None, "Cost is $20.00 dollars per night", "Mahaska County Conservation: $20 a night, payment envelopes at the kiosks."),
 (3096, 15, 20, None, "14 Full Hook Up Spots", "City of Rockford: full hookup $20 a night, electric and water $15, tents $12; no reservations."),
 (3103, 10, 10, None, "Camping fee is $10", "Howard County Fairgrounds: $10 a night; no showers outside fair week."),
 (3104, 35, 35, None, "50 Amp Regular WiFi Sites", "City of Independence 2026: 50-amp sites $35 a day ($30 seniors 60+), tents $10."),
 (3111, 22, 27, None, "$27/night reservable", "Van Buren County Conservation: full hookups $27 a night, electric and water $22; reservable on MyCountyParks."),
 (3124, 22, 25, None, "Regular camping (83 spots", "City of Ottumwa: regular sites $22 a day, full hookup $25."),
 (3127, 25, 35, None, "Full hookups sites - $35", "City of Marshalltown: 30/50-amp electric sites $25 a night, full hookups $35."),
 (3132, 25, 25, None, "Camping rates are $25/night", "Howard County Conservation: $25 a night, first come, first served."),
 (3159, 25, 25, None, "The daily fee is $25/night", "City of Maquoketa: $25 a night, $160 a week."),
 (3163, 25, 25, None, "$25/night", "City of Kalona: eight water-and-electric sites $25 a night, first come, first served."),
 (3164, 25, 25, None, "Camper-$25", "Louisa County Fair: campers $25 a day, tents $10; April 1 - November 1."),
 (3165, 20, 20, None, "Campsites: $20/night", "Washington County Conservation: campsites $20 a night."),
 (3167, 25, 25, None, "$25 per camping unit", "City of Dubuque: electric sites $25 a night, primitive $18."),
 (3177, 25, 25, None, "8 Electrical $25", "Clinton County Conservation: 8 electric sites $25 a night, 8 primitive $15."),
 (3185, 35, 35, None, "Camper RV: $35", "City of Waukon: camper/RV $35 a day with electric and water, tents $20."),
 (3186, 25, 25, None, "Electric sites: $25 per night", "Des Moines County Conservation: electric sites $25 a night ($20 in Sycamore loop), non-electric $10; first come, first served."),
 (3197, 15, 15, None, "Camping Fees - $15.00", "City of Sheffield: $15 a night; 2-night minimum on reserved weekends."),
 (3202, 25, 25, None, "Fees | $25/night", "Pottawattamie County Conservation: 18 30/50-amp sites $25 a night."),
 (3228, 20, 30, None, "Class F Site", "City of Storm Lake: electric-only sites $20 a day, water/sewer/electric $25, patio $28-30; tents $12."),
]
pages = [json.loads(l) for l in open("ia_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_ia_2026-10-15/ia_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
