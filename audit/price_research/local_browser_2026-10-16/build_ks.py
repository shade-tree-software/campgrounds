"""KS local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_ks.py > findings_ks.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(2155, 20, 20, None, "Camping with Hookups", "Jackson County (Banner Creek): camping with hookups $20 a night, without $13; $5 daily vehicle entrance."),
 (2156, 17, 19.5, None, "Electric Hook-up", "Sedgwick County (Lake Afton): electric $17 a day, electric and water $19.50 (seniors and military $15-17.50); no hookups $13."),
 (2157, 18, 18, None, "Campsites with electricity & water", "City of Parsons: campsites with electricity and water $18 a night; tents $5."),
 (2199, 18, 18, None, "Campsites with electricity & water", "City of Parsons: campsites with electricity and water $18 a night; tents $5."),
 (2167, 10, 10, None, "RV Camping – Drake and Kelley $10 Nightly", "City of Burlington: RV camping $10 a night (rate effective April 2016, still the posted rate)."),
 (2177, 10, 10, None, "Electric & Water available -$10.00/night", "City of Lakin (Beymer): electric and water $10 a night, envelopes at the site."),
 (2189, 17, 17, None, "Daily Camping Fee- $17.00", "City of Horton (Mission Lake): daily camping fee $17."),
 (2193, 30, 30, None, "Daily Rate: $30.00", "Thomas County Fairgrounds: full service $30 a day, $200 a week; dry camping $20."),
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
