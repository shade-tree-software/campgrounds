"""IA3 local findings from the browser pass (follow-up: county fee page read in the driver browser 2026-10-16, after the crawl), USD.
python3 -I build_ia3.py > findings_ia3.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(3100, 20, 20, None, "https://www.bentoncountyia.gov/conservation/rulesandpolicies/", "Benton County Conservation: electric sites $20 a night, non-electric $10; first come, first served, self-register at the kiosk; open mid-April to the end of October."),
 (3128, 20, 20, None, "https://www.bentoncountyia.gov/conservation/rulesandpolicies/", "Benton County Conservation: electric sites $20 a night, non-electric $10; first come, first served, self-register at the kiosk; open mid-April to the end of October."),
 (3136, 20, 20, None, "https://www.bentoncountyia.gov/conservation/rulesandpolicies/", "Benton County Conservation: electric sites $20 a night, non-electric $10; first come, first served, self-register at the kiosk; open mid-April to the end of October."),
 (3102, 16, 16, None, "https://www.bentoncountyia.gov/conservation/rulesandpolicies/", "Benton County Conservation: electric sites $16 a night, non-electric $10; first come, first served, self-register at the kiosk; open mid-April to the end of October."),
 (3118, 16, 16, None, "https://www.bentoncountyia.gov/conservation/rulesandpolicies/", "Benton County Conservation: electric sites $16 a night, non-electric $10; first come, first served, self-register at the kiosk; open mid-April to the end of October."),
 (3085, 16, 16, None, "https://www.bentoncountyia.gov/conservation/rulesandpolicies/", "Benton County Conservation: electric sites $16 a night, non-electric $10; first come, first served, self-register at the kiosk; open mid-April to the end of October."),
]
recs = {}
for l in open("browser.jsonl"):
    x = json.loads(l); recs[x["id"]] = x
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for p in recs[i]["pages"] if key in p.get("lines", "")]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-16."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (driver browser follow-up after the crawl), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
