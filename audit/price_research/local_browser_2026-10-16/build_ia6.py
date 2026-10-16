"""IA6 local findings from the browser pass (follow-up: county page text read by AWH in their browser 2026-10-16 and pasted in; Cloudflare blocks our fetches), USD.
python3 -I build_ia6.py > findings_ia6.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(3026, 15, 15, None, "https://www.hardincountyia.gov/bessman-kemp-campground", "Hardin County Conservation: 30/50-amp electric sites $15 a night; primitive tent sites $10."),
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
    out.append({"id": i, "fees": f, "source": urls[0] + " (page text read by AWH in their browser; Cloudflare blocks our fetches), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
