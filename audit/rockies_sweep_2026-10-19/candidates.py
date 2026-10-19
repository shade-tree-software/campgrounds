"""Directory rows in the study area with no database entry.

RV Life (every park_type, not just commercial) and the Good Sam directory,
diffed with private_gap_list.held(). Writes candidates.json."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import private_gap_list as pg  # noqa: E402
from area import inside, nearest, BOXES  # noqa: E402

db = pg.entries()
out, seen = [], set()
for box in BOXES:
    for h in pg.rv_box(box):
        g = h.get("_geoloc") or {}
        pt = (g.get("lat"), g.get("lng"))
        if None in pt or h["objectID"] in seen or not inside(pt):
            continue
        seen.add(h["objectID"])
        ok, why = pg.held(h.get("cg_name") or "", pt[0], pt[1], db)
        if ok:
            continue
        a, k = nearest(pt)
        out.append({"src": "rvlife", "name": h.get("cg_name"), "city": h.get("city_name"),
                    "st": h.get("region_abbvr"), "type": h.get("park_type"),
                    "price": h.get("price_level"), "stars": h.get("star_rating"),
                    "rate": h.get("avg_rate"), "sites": h.get("cg_site_count"),
                    "reviews": h.get("cg_rating_count"),
                    "closed": h.get("closed") or h.get("temp_closed"),
                    "lat": pt[0], "lng": pt[1], "anchor": a, "km": round(k, 1), "why": why,
                    "url": "https://campgrounds.rvlife.com" + (h.get("url") or "")})
    time.sleep(0.3)

gsp = json.load(open(os.path.join(pg.ROOT, "trip_data", "goodsam_parks.json")))["parks"]
for p in gsp.values():
    pt = (p.get("lat"), p.get("lng"))
    if None in pt or not inside(pt):
        continue
    ok, why = pg.held(p["name"], pt[0], pt[1], db)
    if ok:
        continue
    a, k = nearest(pt)
    out.append({"src": "goodsam", "name": p["name"], "city": p.get("city"), "st": p.get("state"),
                "type": p.get("type"), "gs": p.get("gs"), "phone": p.get("phone"),
                "lat": pt[0], "lng": pt[1], "anchor": a, "km": round(k, 1), "why": why})

out.sort(key=lambda r: (r["anchor"], r["km"]))
json.dump(out, open(os.path.join(HERE, "candidates.json"), "w"), indent=1, ensure_ascii=False)
for r in out:
    extra = (f'{r["type"]:10} {"$"*(r["price"] or 0):4} {r["stars"] or 0:3} rev={r["reviews"]} rate={r["rate"]} sites={r["sites"]}'
             if r["src"] == "rvlife" else f'{r["type"]:10} gs={r["gs"]}')
    print(f'{r["src"][:2]} {r["st"]} {r["anchor"][:14]:14} {r["km"]:5} | {r["name"][:42]:42} | {extra} | {r["why"][:50]}')
print(len(out))
