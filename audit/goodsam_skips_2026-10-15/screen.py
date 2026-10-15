"""Earlier private-sweep skips made on PRICE, re-screened for the Good Sam gate rule (AWH 2026-10-14).
python3 -I screen.py -> candidates.json. Latest verdict row per (state, name) wins; a skip whose kind or
reason is about price is matched to the Good Sam directory (gs true) by name within ~3 km of the
candidate's coordinates (or by exact name in-state when the candidate list has none)."""
import glob, json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PRICE = re.compile(r"price|\$\d|over \$|rate", re.I)
NOT_PRICE = re.compile(r"no[_ ]rate|no published rate|unverifiable|rate unreadable", re.I)


def norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())
    s = re.sub(r"\b(rv|park|resort|campground|camping|and|the|of|llc|inc|&)\b", " ", s)
    return " ".join(s.split())


def km(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))


gs = [p for p in json.load(open(os.path.join(ROOT, "trip_data/goodsam_parks.json")))["parks"].values() if p.get("gs")]
db = json.load(open(os.path.join(ROOT, "campgrounds.json")))
db_pts = [(r["id"], r["name"], *map(float, r["location"].split(","))) for r in db if r.get("location")]
out = []
for vf in sorted(glob.glob(os.path.join(ROOT, "audit/*_private/verdicts.jsonl"))):
    st = os.path.basename(os.path.dirname(vf)).split("_")[0].upper()
    latest = {}
    for line in open(vf, encoding="utf-8"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        latest[r.get("name")] = r
    coords = {}
    cf = os.path.join(os.path.dirname(vf), "candidates.json")
    if os.path.exists(cf):
        c = json.load(open(cf))
        for x in (c if isinstance(c, list) else c.get("candidates", []) if isinstance(c, dict) else []):
            if isinstance(x, dict) and x.get("lat") is not None:
                coords[x.get("name")] = (float(x["lat"]), float(x["lng"]))
    for name, r in latest.items():
        if r.get("decision") != "skip":
            continue
        k, why = r.get("kind_of_no") or "", r.get("why") or ""
        if not (PRICE.search(k) or (k in ("", "_auto") and PRICE.search(why))) or NOT_PRICE.search(k):
            continue
        n = norm(name)
        if not n:
            continue
        hit = None
        for p in gs:
            if norm(p["name"]) != n and not (len(n) > 6 and (n in norm(p["name"]) or norm(p["name"]) in n)):
                continue
            if name in coords:
                if km(*coords[name], p["lat"], p["lng"]) < 3:
                    hit = p
            elif p["state"] == st:
                hit = p
            if hit:
                break
        if not hit:
            continue
        near = [i for i, nm, a, b in db_pts if km(hit["lat"], hit["lng"], a, b) < 0.3]
        out.append({"state": st, "name": name, "kind_of_no": k, "why": why, "decided": r.get("decided"),
                    "gs_name": hit["name"], "gs_city": hit["city"], "lat": hit["lat"], "lng": hit["lng"],
                    "gs_type": hit.get("type"), "in_db_within_300m": near})
json.dump(out, open(os.path.join(HERE, "candidates.json"), "w"), indent=1, ensure_ascii=False)
print(len(out))
for o in out:
    print(o["state"], "|", o["name"], "|", o["kind_of_no"], "|", o["why"][:150], "|", o["in_db_within_300m"])
