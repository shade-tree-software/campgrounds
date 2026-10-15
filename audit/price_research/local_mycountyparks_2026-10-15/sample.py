"""Second pass for parks priced per SITE on mycountyparks: read up to 10 RV-site pages spread across
the park's site list (not the first four), skipping tent/host sites. python3 -I sample.py IN.jsonl OUT.jsonl"""
import json, re, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import read
TENT = re.compile(r"tent|host|walk-?in|hike|cabin|shelter|group|equestrian|horse", re.I)
done = set()
try:
    done = {json.loads(l)["id"] for l in open(sys.argv[2])}
except FileNotFoundError:
    pass
for l in open(sys.argv[1]):
    r = json.loads(l)
    if r["id"] in done or not r.get("facility_names"):
        continue
    picked = [f["name"] for f in r["facilities"]]
    if not picked or not any(read.SITE.search(n) for n in picked) and not any(TENT.search(n) for n in picked):
        continue
    sites = [n for n in r["facility_names"] if read.CAMP.search(n) and not TENT.search(n) and not read.NOT.search(n)]
    if not sites:
        continue
    step = max(1, len(sites) // 10)
    pick = sites[::step][:10]
    base = r["park_url"].split("/Park/")[0] if "/Park/" in r.get("park_url", "") else None
    park = r["park_url"].rstrip("/")
    park = re.sub(r"/(Facility|Activity)/.*$", "", park, flags=re.I)
    out = {"id": r["id"], "name": r["name"], "n_sites": len(sites), "facilities": []}
    for n in pick:
        try:
            out["facilities"].append(read.facility(park + "/Facility/" + n))
        except Exception as e:
            out["facilities"].append({"name": n, "error": repr(e)[:200]})
    with open(sys.argv[2], "a") as fh:
        fh.write(json.dumps(out, ensure_ascii=False) + "\n")
    print(r["id"], r["name"][:30], len(sites), "|", " / ".join(sorted({re.sub(r'\s+', ' ', f.get('fees', '')[:40]) for f in out['facilities']}))[:200])
