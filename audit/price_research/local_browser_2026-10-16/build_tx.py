"""TX local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), USD.
python3 -I build_tx.py > findings_tx.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(7228, 35, 35, None, "The price for one night is $35 with full hook-up", "Andrews County (Florey Park): full hookup (30/50-amp, water, sewer) $35 a night; tents $10."),
 (7230, 60, 60, None, "Full hookups for $60 per day", "City of Mason: full hookups $60 a day; dry camping $10."),
 (7237, 25, 28, None, "Full Hookup", "Johnson County (Hamm Creek): water and electric $25, full hookup $28; no hookups $14."),
 (7273, 45, 45, None, "no reservations accepted", "City of Llano: RV park $45 a day, no reservations."),
 (7275, 45, 45, None, "Nightly", "City of Lometa: $45 a night."),
 (7280, 10, 10, None, "$10 camping pass (re-entry allowed)", "City of San Angelo (Middle Concho): $10 camping pass."),
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
