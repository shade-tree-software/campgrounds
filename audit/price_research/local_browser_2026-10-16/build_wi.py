"""WI local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_wi.py > findings_wi.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(3539, 35, 35, None, "Family Electric Campsite: $35/night", "Waukesha County (Muskego Park): electric campsites $35 a night, non-electric $25."),
 (3563, 35, 40, None, "$35.00/night Sunday night", "Racine County (Cliffside): $35 a night Sunday-Thursday, $40 Friday-Saturday."),
 (3588, 40, 50, None, "Weekly Campsite", "City of Washburn: campsites $40 a night, lakeside premium $50."),
 (3589, 40, 50, None, "Weekly Campsite", "City of Washburn: campsites $40 a night, lakeside premium $50."),
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
