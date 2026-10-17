#!/usr/bin/env python3
"""Third pass over the misses: Campendium also suffixes a repeated name with its state
(heritage-village-campground-sd, cedars-rv-resort-bc--1). Tries <slug>-<st>, <slug>-<st>--0/--1 and the
name without its campground/rv-park word. Same MATCH_KM check; rewrites CPD.jsonl in place."""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpd_read as cr
cands = {c["id"]: c for c in json.load(open(sys.argv[1]))}
path = sys.argv[2]
recs = [json.loads(l) for l in open(path)]
for r in recs:
    if r.get("url") or r.get("state_pass"):
        continue
    c = cands[r["id"]]; st = c["state"].lower()
    pin = tuple(float(v) for v in c["location"].split(","))
    base = cr.slugs(c["name"])[0]
    short = cr.slugify(re.sub(r"(?i)\b(campgrounds?|rv park|rv resort|campsites?)\b", " ", re.sub(r"\s*\([^)]*\)", "", c["name"])))
    tried = {t[0] for t in r["tried"]}
    tries = [s for s in dict.fromkeys([f"{base}-{st}", f"{base}-{st}--0", f"{base}-{st}--1", short]) if s and s not in tried]
    r["state_pass"] = True
    for s in tries:
        url, page = cr.fetch("https://www.campendium.com/" + s); time.sleep(cr.PAUSE)
        if not url or "maps.campendium.com" not in url:
            r["tried"].append([s, page if not url else url[:80]]); continue
        p = cr.parse(cr.text_of(page))
        d = cr.km(pin, p["coords"]) if p.get("coords") else None
        r["tried"].append([s, url, None if d is None else round(d, 2)])
        if d is not None and d <= cr.MATCH_KM:
            r.update(p, url=url, km=round(d, 2)); break
    print(r["id"], c["name"][:40], "->", r.get("url", "no match")[-60:], r.get("last_rate"), flush=True)
    with open(path + ".tmp", "w") as fh:
        for x in recs:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    os.replace(path + ".tmp", path)
