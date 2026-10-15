"""MB local findings from mb_pages.jsonl (operators' own pages, read 2026-10-15), CAD. python3 -I build.py > findings.json
low/high = RV (powered/hookup) sites, or the site rate where a park has no power; unserviced/tent in the note.
Source = first page whose rate lines contain KEY."""
import json
ROWS = [
(9374, 40, 45, None, "Camping Site 1-35", "Municipality of Prairie View: electric and water $40 a night, with sewer $45; $210-240 a week."),
 (9375, 25, 25, None, "$25 Plus GST a night", "Town of Carberry: $25 a night plus GST, $140 a week."),
 (9376, 38.50, 38.50, None, "Serviced Sites: $38.50/day", "2026: serviced sites $38.50 a day, non-serviced $22."),
 (9384, 30, 30, None, "Serviced (Water & Electric) sites 30 amp", "Town of Ste. Rose du Lac: water and electric (30 or 50 amp) $30, unserviced tenting $15."),
 (9390, 27.30, 27.30, None, "Power Sites | Nightly", "City of Selkirk 2026: power sites $27.30 a night, no power $21.80; weekly and monthly discounts."),
 (9394, 38, 44, None, "Water & Electric Sites: $38 per night", "Town of Souris: water and electric $38 a night, full service $44, tents $22."),
 (9400, 33, 49.50, None, "$33.00 (15 amp)", "Binscarth Park and Pool: 15-amp $33 a day, 30-amp $38.50, 50-amp $49.50; unserviced $16.50."),
 (9401, 43.15, 43.15, None, "Daily Site – $43.15/day", "Municipality of Norfolk Treherne: $43.15 a day including GST and the Let's Camp booking fee ($37 base)."),
 (9403, 25, 25, None, "Electrical $25.00/Night", "Municipality of WestLake-Gladstone: electrical $25 a night ($20 for 15+ days), no service $7.50."),
 (9409, 40, 40, None, "FULL SERVICE | Day: $40", "2026: full service $40 a day, $240 a week."),
]
pages = [json.loads(l) for l in open("mb_pages.jsonl")]
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [p["url"] for x in pages if x["id"] == i for p in x["pages"] if any(key in ln for ln in p.get("lines", []))]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-15."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (audit/price_research/local_mb_2026-10-15/mb_pages.jsonl), read 2026-10-15"})
print(json.dumps(out, ensure_ascii=False, indent=1))
