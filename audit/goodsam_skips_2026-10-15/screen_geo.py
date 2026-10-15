"""Second screen: price skips with candidate coordinates that sit within 400 m of a Good Sam Park whose name
did not match (renamed parks, d/b/a names). python3 -I screen_geo.py"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from screen import PRICE, NOT_PRICE, km, gs, ROOT  # noqa: E402
done = {(o["state"], o["name"]) for o in json.load(open(os.path.join(HERE, "candidates.json")))}
for vf in sorted(glob.glob(os.path.join(ROOT, "audit/*_private/verdicts.jsonl"))):
    st = os.path.basename(os.path.dirname(vf)).split("_")[0].upper()
    latest = {}
    for line in open(vf, encoding="utf-8"):
        try:
            r = json.loads(line); latest[r.get("name")] = r
        except ValueError:
            pass
    cf = os.path.join(os.path.dirname(vf), "candidates.json")
    if not os.path.exists(cf):
        print("no coords:", st, sum(1 for r in latest.values() if r.get("decision") == "skip" and PRICE.search((r.get("kind_of_no") or "") + " " + (r.get("why") or ""))))
        continue
    c = json.load(open(cf)); c = c if isinstance(c, list) else c.get("candidates", []) if isinstance(c, dict) else []
    co = {x.get("name"): (float(x["lat"]), float(x["lng"])) for x in c if isinstance(x, dict) and x.get("lat") is not None}
    for name, r in latest.items():
        k = r.get("kind_of_no") or ""
        if r.get("decision") != "skip" or (st, name) in done or name not in co or NOT_PRICE.search(k):
            continue
        if not (PRICE.search(k) or (k in ("", "_auto") and PRICE.search(r.get("why") or ""))):
            continue
        for p in gs:
            if km(*co[name], p["lat"], p["lng"]) < 0.4:
                print(st, "|", name, "=>", p["name"], "|", (r.get("why") or "")[:140])
