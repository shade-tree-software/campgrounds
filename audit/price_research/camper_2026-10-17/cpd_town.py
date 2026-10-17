#!/usr/bin/env python3
"""Second pass over cpd_read.py's misses: Campendium suffixes a repeated name with its town
(enon-beach-campground-springfield-oh, tree-haven-campground-westerville), so look the town up from
our pin (Nominatim reverse, 1 req/s per its policy) and try <slug>-<town>-<st> and <slug>-<town>.

    python3 -I audit/price_research/camper_2026-10-17/cpd_town.py CANDIDATES.json CPD.jsonl

Matched records REPLACE the miss lines in CPD.jsonl (rewritten at the end); the same MATCH_KM check applies.
"""
import json, os, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpd_read as cr


def town(lat, lng):
    q = urllib.parse.urlencode({"lat": lat, "lon": lng, "format": "json", "zoom": 12, "addressdetails": 1})
    url, body = cr.fetch("https://nominatim.openstreetmap.org/reverse?" + q)
    time.sleep(1.1)
    if not url:
        return []
    a = json.loads(body).get("address", {})
    return [a[k] for k in ("city", "town", "village", "hamlet", "municipality", "county") if a.get(k)]


def main():
    cands = {c["id"]: c for c in json.load(open(sys.argv[1]))}
    path = sys.argv[2]
    recs = [json.loads(l) for l in open(path)]
    for r in recs:
        if r.get("url") or r.get("town_pass"):
            continue
        c = cands[r["id"]]
        pin = tuple(float(v) for v in c["location"].split(","))
        r["town_pass"] = towns = town(*pin)
        base = cr.slugs(c["name"])[0]
        st = c["state"].lower()
        tries = []
        for t in towns[:2]:
            ts = cr.slugify(t.replace(" County", ""))
            tries += [f"{base}-{ts}-{st}", f"{base}-{ts}"]
        for s in dict.fromkeys(tries):
            url, page = cr.fetch("https://www.campendium.com/" + s)
            time.sleep(cr.PAUSE)
            if not url or "maps.campendium.com" not in url:
                r["tried"].append([s, page if not url else url[:80]])
                continue
            p = cr.parse(cr.text_of(page))
            d = cr.km(pin, p["coords"]) if p.get("coords") else None
            r["tried"].append([s, url, None if d is None else round(d, 2)])
            if d is not None and d <= cr.MATCH_KM:
                r.update(p, url=url, km=round(d, 2))
                break
        print(r["id"], c["name"][:40], towns[:2], "->", r.get("url", "no match")[-60:], r.get("last_rate"), flush=True)
        with open(path + ".tmp", "w") as fh:
            for x in recs:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
        os.replace(path + ".tmp", path)


if __name__ == "__main__":
    main()
