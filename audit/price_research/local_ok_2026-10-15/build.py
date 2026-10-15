"""OK local findings from ok_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(6625, 20, 20, None, "Camping fees are $20 per day", "City of Stilwell: camping $20 a day, $100 a week; 14-day maximum."),
 (6733, 15, 20, None, "Campsite: March 1 through October 31", "City of Sallisaw: $20 a night March-October, $15 November-February."),
 (6749, 35, 40, None, "RV Campsites - $35-40", "Lake McMurtry: RV sites $35-40 a night including one vehicle permit; tents $25."),
 (6827, 25, 30, None, "Spaces 21–52 (water, sewer, and electricity)", "City of El Reno: water and electric $25 a night, full hookup $30; tents $20."),
 (6830, 25, 25, None, "RV & Tent camping at Elk City Lake is $25.00", "City of Elk City: RV and tent camping $25 a day."),
 (6831, 35, 35, None, "Per Night $35", "Cleveland County Fair: $35 a night, $210 a week; first come, first served."),
 (6835, 28.75, 34.50, None, "Preferred RV Sites - $34.50", "City of Lawton, prime season (March-September): preferred lakefront RV sites $34.50 a night, others $28.75 ($5.75 off for seniors 65+ and disability)."),
 (6840, 28.75, 34.50, None, "Preferred RV Sites - $34.50", "City of Lawton, prime season (March-September): preferred lakefront RV sites $34.50 a night, others $28.75 ($5.75 off for seniors 65+ and disability)."),
 (6836, 15, 15, None, "Camping with Electric & Water - $15.00/day", "Town of Webbers Falls: electric and water $15 a day, no utilities $7; seniors/military/disabled $13."),
 (6839, 25, 25, None, "*RV sites are $25.00 per night", "City of Ponca City: RV sites $25 a night, tents $15."),
 (6846, 18, 22, None, "RV Site full hook up- $22.00/night", "City of Cleveland: electric and water $18 a night, full hookup $22, seniors $17; tents $9."),
 (6856, 15, 25, None, "Non-Preferred RV Sites - $25.00 per night", "City of Lawton: RV sites $25 a night March-September, $15 October-February ($5 off for seniors 65+ and disability); no reservations."),
 (6857, 15, 25, None, "Non-Preferred RV Sites - $25.00 per night", "City of Lawton: RV sites $25 a night March-September, $15 October-February ($5 off for seniors 65+ and disability); no reservations."),
 (6861, 30, 45, None, "Standard RV sites rent for $30 per night", "Southwestern Oklahoma State University: standard RV sites $30 a night, full hookups $45, tents $25; $2 off for seniors and the disabled."),
]
pages = [json.loads(l) for l in open("ok_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_ok_2026-10-15/ok_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
