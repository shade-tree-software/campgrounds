"""Sample a classic ReserveAmerica park without listing every site: read the search results at a
few evenly spaced offsets, take sites from each page, and read their 1-night price and hookups.

    python3 -I ra_quick.py DATE[,DATE2] --pages 6 --per-page 3 URL [URL ...] > OUT.jsonl

DATE2, when given, is priced on the first site of each distinct (electric, price) kind only, to
show the weekend difference. One JSON line per site read (same fields as ra_sample.py)."""
import html, json, os, re, sys, time, urllib.request, http.cookiejar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ra_list, ra_price  # noqa: E402
SKIP = re.compile(r"(?i)shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|"
                  r"equest|lean-to|meeting|remote|tent only|walk|hike")
KEYS = ("Electricity Hookup", "Water Hookup", "Sewer Hookup", "Full Hookup", "Site Rating", "Max Vehicle Length",
        "Type", "Site, Loop", "Site Access")
args = sys.argv[1:]
dates = args[0].split(",")
pages = int(args[args.index("--pages") + 1]) if "--pages" in args else 6
per_page = int(args[args.index("--per-page") + 1]) if "--per-page" in args else 3
urls = [a for a in args if a.startswith("http")]


def read(op, host, cc, pid, sid, date):
    p, L = ra_price.price(host, cc, pid, sid, date, op)
    attrs = {}
    for line in L:
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip() in KEYS and k.strip() not in attrs:
                attrs[k.strip()] = v.strip()
    k = next((j for j, l in enumerate(L) if "Camping Fees" in l or "Use Fees" in l), None)
    extra = " / ".join(l for l in L[k + 1:k + 7] if not l.startswith("Note")) if k is not None else ""
    if k is None:
        j = next((j for j, l in enumerate(L) if l.startswith("Price Breakdown")), None)
        if j is not None:
            amts = [re.search(r"\$[\d,]+\.\d\d", l).group(0) for l in L[j + 1:j + 25]
                    if re.search(r"\$[\d,]+\.\d\d", l) and "x $" not in l and "Total" not in l]
            labels = [l for l in L[j + 1:j + 4] if l.endswith("Pay")]
            r = next((L[i + 1] for i in range(j, min(j + 40, len(L) - 1)) if L[i] == "Reservation Fees"), "")
            extra = " / ".join(f"{a} {b}" for a, b in zip(labels, amts)) + (f" / Reservation Fees / {r}" if r else "")
    return p, extra, attrs


for url in urls:
    host = re.match(r"https?://[^/]+", url).group(0)
    cc = re.search(r"contractCode=(\w+)", url).group(1)
    pid = re.search(r"parkId=(\d+)", url).group(1)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", ra_price.UA)]
    g = lambda u: op.open(u, timeout=60).read().decode("utf-8", "replace")  # noqa: E731
    try:
        g(f"{host}/campgroundDetails.do?contractCode={cc}&parkId={pid}")
        t = g(f"{host}/campsiteSearch.do?contractCode={cc}&parkId={pid}")
    except Exception as x:  # noqa: BLE001 - a park that refuses (401/404) is reported, the rest go on
        print(json.dumps({"parkId": pid, "url": url, "error": str(x)}), flush=True)
        continue
    flat = re.sub(r"[\s\xa0]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
    m = re.search(r"Search Results[^0-9]{0,40}\d+\s*-\s*\d+\s+of\s+(\d+)", flat) or re.search(r"\d+\s*-\s*\d+\s+of\s+(\d+)", flat)
    total = int(m.group(1)) if m else 25
    step = max(25, (total // pages) // 25 * 25)
    picks, seen = [], set()
    for start in range(0, total, step):
        if start:
            time.sleep(0.3)
            t = g(f"{host}/campsitePaging.do?contractCode={cc}&parkId={pid}&startIdx={start}")
        rows = [r for r in ra_list.rows(t) if len(r["cells"]) > 1 and len(r["cells"][1]) > 2
                and not SKIP.search(r["cells"][1]) and r["siteId"] not in seen]
        for r in rows[::max(1, len(rows) // per_page)][:per_page]:
            seen.add(r["siteId"])
            picks.append(r)
    kinds = set()
    for r in picks:
        try:
            p, extra, attrs = read(op, host, cc, pid, r["siteId"], dates[0])
        except Exception as x:  # noqa: BLE001
            p, extra, attrs = None, f"ERROR {x}", {}
        rec = {"parkId": pid, "url": url, "total": total, "site": r["site"], "loop": r["cells"][0], "date": dates[0],
               "price": p, "breakdown": extra, **attrs}
        print(json.dumps(rec), flush=True)
        kind = (attrs.get("Electricity Hookup"), attrs.get("Sewer Hookup"), p)
        if len(dates) > 1 and p and kind not in kinds:
            kinds.add(kind)
            time.sleep(0.3)
            p2, extra2, _ = read(op, host, cc, pid, r["siteId"], dates[1])
            print(json.dumps({**rec, "date": dates[1], "price": p2, "breakdown": extra2}), flush=True)
        time.sleep(0.3)
