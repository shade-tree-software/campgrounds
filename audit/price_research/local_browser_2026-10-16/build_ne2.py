"""NE2 local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_ne2.py > findings_ne2.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(2769, 39, 49, None, "Regular- $39/night", "Bader Memorial Park: RV sites $39-49 a night by service (30-amp to full), annual pass holders $30-40."),
 (2794, 25, 25, None, "Camper Hookups-$25 per night", "Dawson County Fairgrounds: camper hookups with electric and water $25 a night."),
 (2824, 15, 15, None, "$15.00/night with water and electric", "Pawnee City: $15 a night with water and electric; tents $8."),
 (2845, 20, 20, None, "first come first serve, $20 per night", "City of Papillion (Walnut Creek): 44 electric sites (30/50-amp) $20 a night, first come, first served."),
 (2886, 28, 28, None, "for concrete pad & electrical hookup", "City of Norfolk (TaHaZouka): $28 a night with concrete pad and electric, $18 without."),
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
