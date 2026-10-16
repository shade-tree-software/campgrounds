#!/usr/bin/env python3
"""Find the current fs.usda.gov page for FS entries whose link 404s or lands on a generic
page (camping-cabins, a district, a trail), via the forest's own sitemap.xml (2026-10-16).

    python3 -I fs_sitemap.py OUT.json

Candidate slugs are scored by how many of the entry's name words (minus 'campground',
'recreation', 'area') they contain; ties and weak matches are printed for a human. Each
chosen page is fetched and its 'Fee Site and Info' block cached alongside. 1 s/request.
"""
import json, re, sys, time, urllib.request, os
ROOT = __file__.rsplit("/audit/", 1)[0]
sys.path.insert(0, ROOT + "/audit/price_research")
import fs_fees as F
UA = {"User-Agent": F.UA}
STOP = {"campground", "campgrounds", "recreation", "area", "site", "the", "and", "of", "camp", "nf", "national", "forest"}


def words(s):
    s = re.sub(r"\(.*?\)", " ", s.lower()).replace("'", "")
    return [w for w in re.findall(r"[a-z0-9]+", s) if w not in STOP]


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "ignore")


cache = json.load(open(ROOT + "/trip_data/fs_fees.json"))
out = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
maps = {}
for r, u in F.targets():
    c = cache.get(u)
    if not c or (c["status"] == 200 and c["block"]) or str(r["id"]) in out:
        continue
    forest = re.match(r"(https://www\.fs\.usda\.gov/r\d\d/[a-z0-9\-]+)", u).group(1)
    if forest not in maps:
        try:
            maps[forest] = re.findall(r"<loc>https?://www\.fs\.usda\.gov(/r\d\d/[a-z0-9\-]+/recreation/[a-z0-9\-]+)</loc>", get(forest + "/sitemap.xml"))
        except Exception as e:
            maps[forest] = []; print("no sitemap", forest, e)
        time.sleep(1)
    want = words(r["name"])
    scored = sorted(((sum(w in p.rsplit("/", 1)[1].split("-") for w in want), -len(p), p) for p in maps[forest]), reverse=True)
    best = [p for s, _, p in scored if s == scored[0][0]] if scored and scored[0][0] else []
    row = {"name": r["name"], "old": u, "want": want, "score": scored[0][0] if scored else 0,
           "candidates": best[:4]}
    if best and scored[0][0] == len(want):
        page = "https://www.fs.usda.gov" + best[0]
        try:
            row.update(url=page, block=F.fee_block(get(page)))
        except Exception as e:
            row.update(url=page, error=str(e))
        time.sleep(1)
    out[str(r["id"])] = row
    json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
print(len(out))
