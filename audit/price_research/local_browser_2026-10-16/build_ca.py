"""CA local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_ca.py > findings_ca.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(11762, 38, 65, None, "Daily RV Park Site Fee (w/ 30 amp hookups)", "Merced Irrigation District (Lake McClure/McSwain) fee schedule: basic campsite $38 a night, RV park site with 30-amp hookups $48, premium RV site with 50-amp $65 (military, disabled and senior $3 off); $12 per extra vehicle."),
 (11775, 38, 65, None, "Daily RV Park Site Fee (w/ 30 amp hookups)", "Merced Irrigation District (Lake McClure/McSwain) fee schedule: basic campsite $38 a night, RV park site with 30-amp hookups $48, premium RV site with 50-amp $65 (military, disabled and senior $3 off); $12 per extra vehicle."),
 (11788, 38, 65, None, "Daily RV Park Site Fee (w/ 30 amp hookups)", "Merced Irrigation District (Lake McClure/McSwain) fee schedule: basic campsite $38 a night, RV park site with 30-amp hookups $48, premium RV site with 50-amp $65 (military, disabled and senior $3 off); $12 per extra vehicle."),
 (12414, 38, 65, None, "Daily RV Park Site Fee (w/ 30 amp hookups)", "Merced Irrigation District (Lake McClure/McSwain) fee schedule: basic campsite $38 a night, RV park site with 30-amp hookups $48, premium RV site with 50-amp $65 (military, disabled and senior $3 off); $12 per extra vehicle."),
 (11720, 38, 65, None, "https://book.lakemcclure.com/campgrounds/bagby-camping-recreation", "Merced Irrigation District (Lake McClure/McSwain) fee schedule: basic campsite $38 a night, RV park site with 30-amp hookups $48, premium RV site with 50-amp $65 (military, disabled and senior $3 off); $12 per extra vehicle."),
 (11816, 53, 53, None, "RV campsites", "Santa Clara County Parks (from March 1, 2026): RV campsites $53 a night, tent $41."),
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
