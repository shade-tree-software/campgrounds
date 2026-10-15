"""IN local findings from in_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(1318, 40, 53, None, "Water/30amp (per night)", "Elkhart County 4-H Fair (rates from January 1, 2026): water and 30-amp $40 a night, full hookup with 50-amp $53, plus tax."),
 (1319, 25, 45, None, "WATER & ELECTRIC SITES", "Town of Lynnville: water and 50-amp electric $25 a night, full hookup $45; tents $20; $5 entry per adult."),
 (1321, 20, 20, None, "night's rental of $20.00", "Town of Edinburgh: water and electric sites $20 a night."),
 (1322, 25, 45, None, "Standard Campsite Rate (April", "Johnson County Park 2026: electric and water $30 a night April-October, full hookup $45, electric only $25 November-March; plus tax."),
 (1324, 45, 45, None, "Nightly: $45.00 plus", "City of Warsaw 2026: $45 a night plus tax, $275 a week."),
 (1328, 25, 35, None, "Full hookup (sewer/water/electric)", "Jennings County: electric and water $25 a night, full hookup $35, primitive $18; plus tax."),
 (1334, 42, 42, None, "Camping fee $42.00 per night", "St. Joseph County 4-H Fair: $42 a night outside fair week."),
 (1338, 35, 35, None, "Modern Camping $35.00 per night", "Modern camping $35 a night plus tax, primitive $17."),
 (1339, 25, 25, None, "All RV Camping $25.00/night", "Dubois County: RV camping $25 a night, tents $15."),
 (1345, 30, 45, None, "Price: $ 45 per night", "Wabash & Erie Canal Park: RV sites $30-45 a night by site."),
 (1350, 36, 36, None, "Tent and RV with hook-up (electric & water)", "City of Kendallville: electric and water $36 a night plus tax, primitive $25; more on holidays and Apple Festival weekends."),
]
pages = [json.loads(l) for l in open("in_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_in_2026-10-15/in_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
