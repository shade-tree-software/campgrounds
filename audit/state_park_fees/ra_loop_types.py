"""Price every (loop, site type) of classic ReserveAmerica parks already listed by ra_list.py (2026-10-12).

    python3 -I ra_loop_types.py TUE,SAT LISTING.json [LISTING.json ...] > OUT.jsonl

For each loop and site type (cabins, shelters, group, equestrian, tent-only and walk-in types skipped), up to two
sites are priced on the first date and the first one on the second date, with the site page's hookup attributes and
max vehicle length. A site whose page shows no price for a date (booked, or not yet open) is replaced by the next
site of the same loop and type, up to four tries. One JSON line per priced site and date."""
import json, os, re, sys, time, urllib.request, http.cookiejar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ra_price  # noqa: E402
SKIP = re.compile(r"(?i)shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|"
                  r"equest|lean-to|meeting|remote|tent|walk|hike|palapa|tiny|bunk|room")
KEYS = ("Electricity Hookup", "Water Hookup", "Sewer Hookup", "Full Hookup", "Max Vehicle Length", "Type",
        "Site, Loop", "Site Access", "Driveway Entry")
dates = sys.argv[1].split(",")
for path in sys.argv[2:]:
    d = json.load(open(path))
    groups = {}
    for r in d["sites"]:
        t = r["cells"][1] if len(r["cells"]) > 1 else "?"
        if SKIP.search(t) or "host" in (r.get("site") or "").lower():
            continue
        groups.setdefault((r["cells"][0] if r["cells"] else "?", t), []).append(r)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", ra_price.UA)]
    op.open(f"{d['host']}/campgroundDetails.do?contractCode={d['contract']}&parkId={d['parkId']}", timeout=60).read()
    for (loop, t), members in sorted(groups.items()):
        for di, dt in enumerate(dates):
            want, tries, got = (2 if di == 0 else 1), 0, 0
            for r in members:
                if got >= want or tries >= 4 + want:
                    break
                tries += 1
                try:
                    p, L = ra_price.price(d["host"], d["contract"], d["parkId"], r["siteId"], dt, op)
                except Exception as x:  # noqa: BLE001 - one bad page shouldn't stop the run
                    p, L = None, [f"ERROR {x}"]
                time.sleep(0.4)
                if not p:
                    continue
                attrs = {}
                for line in L:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        if k.strip() in KEYS and k.strip() not in attrs:
                            attrs[k.strip()] = v.strip()
                print(json.dumps({"parkId": d["parkId"], "loop": loop, "type": t, "site": r["site"],
                                  "cells": r["cells"], "date": dt, "price": p, **attrs}), flush=True)
                got += 1
            if not got:
                print(json.dumps({"parkId": d["parkId"], "loop": loop, "type": t, "date": dt, "price": None,
                                  "n": len(members)}), flush=True)
