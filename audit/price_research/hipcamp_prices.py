#!/usr/bin/env python3
"""Per-site nightly prices off Hipcamp listing pages (2026-10-10). Plain urllib.

The server-rendered __NEXT_DATA__ carries land.sites.edges: each edge has the
host's pricePerNight, Hipcamp's serviceFee, minNights, and a node with the
site name, accommodationKeys and rvMaxLength.

    python3 audit/price_research/hipcamp_prices.py LIST.tsv OUT.jsonl
LIST rows: id<TAB>...<TAB>url (url last).
"""
import json, re, sys, time, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def find_land(o):
    if isinstance(o, dict):
        if isinstance(o.get("sites"), dict) and "edges" in o["sites"]:
            return o
        for v in o.values():
            r = find_land(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_land(v)
            if r:
                return r


def money(x):
    return (x or {}).get("minorAmount", 0) / 100 if x else None


out = open(sys.argv[2], "a")
for row in open(sys.argv[1]).read().splitlines():
    cols = row.split("\t")
    eid, url = int(cols[0]), cols[-1]
    rec = {"id": eid, "url": url, "sites": []}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
        d = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, re.S).group(1))
        land = find_land(d)
        rec["land"] = land.get("name")
        for e in land["sites"]["edges"]:
            n = e.get("node") or {}
            rec["sites"].append({
                "name": n.get("name"), "acc": n.get("accommodationKeys"),
                "rv_max": (n.get("rvMaxLength") or {}).get("formatShort"),
                "price": money(e.get("pricePerNight")), "service_fee": money(e.get("serviceFee")),
                "min_nights": e.get("minNights"), "count": n.get("campsitesCount"),
            })
    except Exception as ex:
        rec["error"] = str(ex)[:200]
    out.write(json.dumps(rec) + "\n")
    out.flush()
    print(eid, len(rec["sites"]), rec.get("error", ""), flush=True)
    time.sleep(1)
