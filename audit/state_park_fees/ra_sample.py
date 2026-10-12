"""Sample sites across every loop of a classic ReserveAmerica park and read each one's 1-night
price and hookup attributes on a date.

    python3 -I ra_sample.py DATE LISTING.json [LISTING.json ...] [--per-loop 3] [--max 30] > OUT.jsonl

LISTING is a ra_sites.py file. Sites are taken round-robin across loops (cabins, lean-tos and
the like skipped by type), so a park whose electric sites sit in one loop still shows both
kinds. One JSON line per site read: park, site, loop, type, price line, Electricity/Water/Sewer
Hookup, Site Rating, Max Vehicle Length."""
import json, os, re, sys, time, urllib.request, http.cookiejar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ra_price  # noqa: E402
SKIP = re.compile(r"(?i)shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|"
                  r"equest|lean-to|meeting|remote|tent only|walk|hike")
args = [a for a in sys.argv[1:]]
per_loop = int(args[args.index("--per-loop") + 1]) if "--per-loop" in args else 3
cap = int(args[args.index("--max") + 1]) if "--max" in args else 30
files = [a for a in args[1:] if a.endswith(".json")]
date = args[0]
KEYS = ("Electricity Hookup", "Water Hookup", "Sewer Hookup", "Full Hookup", "Site Rating", "Max Vehicle Length",
        "Type", "Site, Loop", "Waterfront", "Site Access")
for path in files:
    d = json.load(open(path))
    loops = {}
    for r in d["sites"]:
        t = r["cells"][1] if len(r["cells"]) > 1 else "?"
        if SKIP.search(t):
            continue
        loops.setdefault(r["cells"][0] if r["cells"] else "?", []).append(r)
    picks = []
    for i in range(per_loop):
        for lp in sorted(loops):
            mem = loops[lp]
            if len(mem) > i:
                picks.append(mem[(i * max(1, len(mem) // per_loop)) % len(mem)])
    picks = picks[:cap]
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", ra_price.UA)]
    op.open(f"{d['host']}/campgroundDetails.do?contractCode={d['contract']}&parkId={d['parkId']}", timeout=60).read()
    for r in picks:
        try:
            p, L = ra_price.price(d["host"], d["contract"], d["parkId"], r["siteId"], date, op)
        except Exception as x:  # noqa: BLE001
            p, L = None, [f"ERROR {x}"]
        attrs = {}
        for line in L:
            if ":" in line:
                k, v = line.split(":", 1)
                if k.strip() in KEYS and k.strip() not in attrs:
                    attrs[k.strip()] = v.strip()
        k = next((j for j, l in enumerate(L) if "Camping Fees" in l or "Use Fees" in l), None)
        extra = " / ".join(l for l in L[k + 1:k + 7] if not l.startswith("Note")) if k is not None else ""
        print(json.dumps({"park": os.path.basename(path), "ids": d.get("entry_ids"), "site": r["site"],
                          "loop": r["cells"][0] if r["cells"] else None, "date": date, "price": p,
                          "breakdown": extra, **attrs}), flush=True)
        time.sleep(0.3)
