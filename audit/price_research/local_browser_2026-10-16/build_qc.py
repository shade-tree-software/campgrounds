"""QC local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), CAD.
python3 -I build_qc.py > findings_qc.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(12533, 60, 70, None, "TERRAIN 3 SERVICES 50 AMP", "Camping Jonquière, plus taxes: 3-service sites C$60 a night, 50-amp C$70."),
 (12608, 45.65, 45.65, None, "$45.65/day", "Camping Pointe-aux-Oies (Montmagny): 2 or 3 services (20/30-amp) C$45.65 a day."),
 (12617, 50.40, 62, None, "2 services – eau et électricité 30 ampères", "Camping Rivière-Ouelle: 2 services C$56-58 a night, 3 services C$60-62 (C$50.40-55.80 in low season); unserviced C$43.45-45.49."),
 (12618, 48, 65, None, "PANO 2 SERVICES", "Camping Bon-Désir: 2 services C$48 a night, 3 services 30-amp C$54, panoramic 2 services C$58, panoramic 3 services 50-amp C$65."),
]
recs = {}
for l in open("browser.jsonl"):
    x = json.loads(l); recs[x["id"]] = x
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for p in recs[i]["pages"] if key in p.get("lines", "")]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-16."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_browser_2026-10-16/browser.jsonl), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
