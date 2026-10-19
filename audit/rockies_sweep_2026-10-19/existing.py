import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from area import nearest, inside
d = json.load(open(os.path.join(os.path.dirname(__file__), "../../campgrounds.json")))
rows = []
for e in d:
    if e.get("kind") != "campground": continue
    try: pt = tuple(map(float, e["location"].split(",")))
    except Exception: continue
    if inside(pt):
        n, k = nearest(pt)
        rows.append((n, k, e))
rows.sort(key=lambda r: (r[0], r[1]))
for n, k, e in rows:
    print(f'{e["id"]:6} {e["state"]} {e["ownership"]:9} {n[:18]:18} {k:5.1f}  {e["name"]}')
print(len(rows))
