"""CO3 local findings from the browser pass (follow-up: agency fee pages read in the driver browser 2026-10-16, after the crawl), USD.
python3 -I build_co3.py > findings_co3.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(2641, 35, 45, 8.75, "https://www.larimer.gov/naturalresources/parks/permits", "Larimer County: electric sites $35 a night weekdays, $45 weekends, $55 holidays (April-September), $25-30 October-March; non-electric $25-35; daily entrance permit required in addition; $8.75 reservation fee."),
 (2642, 35, 45, 8.75, "https://www.larimer.gov/naturalresources/parks/permits", "Larimer County: electric sites $35 a night weekdays, $45 weekends, $55 holidays (April-September), $25-30 October-March; non-electric $25-35; daily entrance permit required in addition; $8.75 reservation fee."),
 (2648, 35, 45, 8.75, "https://www.larimer.gov/naturalresources/parks/permits", "Larimer County: electric sites $35 a night weekdays, $45 weekends, $55 holidays (April-September), $25-30 October-March; non-electric $25-35; daily entrance permit required in addition; $8.75 reservation fee."),
 (2659, 35, 45, 8.75, "https://www.larimer.gov/naturalresources/parks/permits", "Larimer County: electric sites $35 a night weekdays, $45 weekends, $55 holidays (April-September), $25-30 October-March; non-electric $25-35; daily entrance permit required in addition; $8.75 reservation fee."),
 (2652, 35, 60, 8.75, "https://www.larimer.gov/naturalresources/parks/permits", "Larimer County (Horsetooth Reservoir): electric sites $35 a night weekdays, $45 weekends (April-September); full hookup $45/$60; holidays $55/$65; October-March electric $25-30, full hookup $30-35; daily entrance permit required in addition; $8.75 reservation fee."),
 (2653, 35, 60, 8.75, "https://www.larimer.gov/naturalresources/parks/permits", "Larimer County (Horsetooth Reservoir): electric sites $35 a night weekdays, $45 weekends (April-September); full hookup $45/$60; holidays $55/$65; October-March electric $25-30, full hookup $30-35; daily entrance permit required in addition; $8.75 reservation fee."),
 (2651, 35, 45, 8.75, "https://www.larimer.gov/naturalresources/parks/permits", "Larimer County (Hermit Park): non-electric sites $35 a night weekdays, $45 weekends, $50 holidays (March-December); daily entrance permit required in addition; $8.75 reservation fee."),
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
