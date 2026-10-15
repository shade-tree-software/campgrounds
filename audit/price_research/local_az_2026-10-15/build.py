"""AZ local findings from az_pages.jsonl (operators' own pages, read 2026-10-15), USD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(11450, 40, 40, 10, "https://www.maricopacountyparks.net/fees/", "Maricopa County: developed sites with electric and water $40 a night (rising to $50 on January 1, 2027); shaded RV sites $65 where offered; semi-developed $25; $10 reservation fee."),
 (11451, 40, 40, 10, "https://www.maricopacountyparks.net/fees/", "Maricopa County: developed sites with electric and water $40 a night (rising to $50 on January 1, 2027); shaded RV sites $65 where offered; semi-developed $25; $10 reservation fee."),
 (11452, 40, 40, 10, "https://www.maricopacountyparks.net/fees/", "Maricopa County: developed sites with electric and water $40 a night (rising to $50 on January 1, 2027); shaded RV sites $65 where offered; semi-developed $25; $10 reservation fee."),
 (11453, 40, 40, 10, "https://www.maricopacountyparks.net/fees/", "Maricopa County: developed sites with electric and water $40 a night (rising to $50 on January 1, 2027); shaded RV sites $65 where offered; semi-developed $25; $10 reservation fee."),
 (11454, 40, 40, 10, "https://www.maricopacountyparks.net/fees/", "Maricopa County: developed sites with electric and water $40 a night (rising to $50 on January 1, 2027); shaded RV sites $65 where offered; semi-developed $25; $10 reservation fee."),
 (11462, 40, 40, 10, "https://www.maricopacountyparks.net/fees/", "Maricopa County: developed sites with electric and water $40 a night (rising to $50 on January 1, 2027); shaded RV sites $65 where offered; semi-developed $25; $10 reservation fee."),
 (11598, 40, 40, 10, "https://www.maricopacountyparks.net/fees/", "Maricopa County: developed sites with electric and water $40 a night (rising to $50 on January 1, 2027); shaded RV sites $65 where offered; semi-developed $25; $10 reservation fee."),
 (11455, 60, 65, None, "Daily $65 $60 with Good Sam", "Fairgrounds RV Park: $65 a night, $60 with Good Sam or FMCA; $375 a week."),
 (11460, 30, 30, None, "Our rates are $30/night for electrical", "Verde Valley Fair: electrical sites $30 a night, dry camping $20; higher during Thunder Valley Rally."),
 (11469, 40, 40, None, "Full Hookup | $40", "Mohave County: electric and full hookup sites $40 a night, dry camping $20 a vehicle; pets $10 a day."),
 (11473, 20, 20, None, "Daily $20", "La Paz County: water and electric $20 a day plus electricity at $0.19/kWh, dry camping $10."),
 (11537, 24, 24, 10, "Per camp unit per night", "City of Show Low: standard family sites $24 a night plus tax; $10 reservation fee."),
 (11541, 10, 10, None, "$10 per night, per vehicle", "Town of Wickenburg: $10 a night per vehicle ($15 with a horse stall), first come, first served."),
]
pages = [json.loads(l) for l in open("az_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_az_2026-10-15/az_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
