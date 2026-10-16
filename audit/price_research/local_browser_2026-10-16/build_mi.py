"""MI local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_mi.py > findings_mi.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(3935, 29, 29, 5, "Camping per night $29", "Kalamazoo County (Cold Brook): camping $29 a night; $5 non-refundable reservation fee."),
 (3936, 39, 39, 5, "Camping per night: $39", "Kalamazoo County (Markin Glen): camping $39 a night; $5 non-refundable reservation fee."),
 (3942, 33, 43, None, "Standard Sites: $38/night", "Oakland County (Addison Oaks): standard sites $38 a night, pull-throughs $43; county residents $33/$38 Sunday-Thursday; holidays $5 more."),
 (3946, 35, 40, None, "Electric/Shared Water", "Kent County (Wabasis Lake): electric with shared water $35 a night, full hookup $40; primitive $24."),
 (3956, 25, 41, 5, "Campsite (Electric)", "Newaygo County: electric $25 (Mon-Wed) / $30 (Thu-Sun), water and electric $31/$36, full hookup $36/$41; $5 reservation fee; holidays $5 more with a 3-night minimum."),
 (3968, 30, 30, None, "Camping Cost: $30/night.", "Midland County Fairgrounds: $30 a night."),
 (4003, 27, 40, None, "Otsego County Residents: $27.00 per night", "Otsego County: $27-37 a night for county residents and $30-40 for others, by service level."),
 (4036, 42, 48, 8, "$48 per night", "City of Sault Ste. Marie: non-waterfront sites $42 a night, premium waterfront $48; $8 non-refundable reservation fee."),
 (4046, 30, 50, 5, "Full Hook-Up", "Marquette County (Perkins Park): electric only $30, electric and water $40, full hookup $50; rustic $25; $5 reservation fee."),
 (4049, 28, 35, None, "Remaining regular sites", "City of Hancock: regular sites $28 a day; 50-amp, water-service and waterfront sites $35; tents $18."),
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
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_browser_2026-10-16/browser.jsonl), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
