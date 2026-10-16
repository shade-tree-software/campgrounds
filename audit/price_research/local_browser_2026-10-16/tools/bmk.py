# usage: bmk.py st CUR rows_file -> writes local_browser_2026-10-16/build_st.py (rows: id, low, high, resfee, KEY-or-URL, note)
import sys
st, cur, rows = sys.argv[1], sys.argv[2], open(sys.argv[3]).read()
d = "local_browser_2026-10-16"
open(f"/home/andrew/Dev/campgrounds/audit/price_research/{d}/build_{st}.py", "w").write(f'''"""{st.upper()} local findings from the browser pass (operators' own pages in the driver browser, read 2026-10-16), {cur}.
python3 -I build_{st}.py > findings_{st}.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
{rows.strip()}
]
recs = {{}}
for l in open("browser.jsonl"):
    x = json.loads(l); recs[x["id"]] = x
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for p in recs[i]["pages"] if key in p.get("lines", "")]
    assert urls, (i, key)
    f = {{"nightly_low": lo, "nightly_high": hi, "currency": "{cur}"}}
    if rf:
        f["reservation_fee"] = rf
    f.update({{"checked": "2026", "note": note + " Read 2026-10-16."}})
    out.append({{"id": i, "fees": f, "source": urls[0] + " (audit/price_research/{d}/browser.jsonl), read 2026-10-16"}})
print(json.dumps(out, ensure_ascii=False, indent=1))
''')
