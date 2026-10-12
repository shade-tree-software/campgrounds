"""One site's 1-night price per site type, per date, for parks already listed by ra_sites.py.

    python3 -I ra_type_prices.py 6/15/2027,6/19/2027 DIR/NH_270003.json [DIR/....json ...]

Like ra_check.py, but reads the saved listings instead of fetching them again. For each type it
tries up to 6 sites until one prints a price (a booked night can show none) and prints the price
breakdown lines: resident / non-resident prices where the host shows both, and the reservation fee."""
import json, os, re, sys, time, urllib.request, http.cookiejar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ra_price  # noqa: E402
SKIP = re.compile(r"(?i)shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|"
                  r"equest|bear den|lean-to|meeting|remote|tent only|walk-in|hike")
dates = sys.argv[1].split(",")
for path in sys.argv[2:]:
    d = json.load(open(path))
    types = {}
    for r in d["sites"]:
        t = r["cells"][1] if len(r["cells"]) > 1 else "?"
        if not SKIP.search(t):
            types.setdefault(t, []).append(r)
    print(f"== {os.path.basename(path)} ids {d.get('entry_ids')} {d['url'].split('/camping/')[-1].split('/')[0]}: "
          f"{ {k: len(v) for k, v in types.items()} }", flush=True)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", ra_price.UA)]
    op.open(f"{d['host']}/campgroundDetails.do?contractCode={d['contract']}&parkId={d['parkId']}", timeout=60).read()
    for t, members in types.items():
        for dt in dates:
            got = None
            for r in members[:6]:
                try:
                    p, L = ra_price.price(d["host"], d["contract"], d["parkId"], r["siteId"], dt, op)
                except Exception as x:  # noqa: BLE001 - one bad page shouldn't stop the run
                    p, L = None, [str(x)]
                time.sleep(0.3)
                if p:
                    k = next(j for j, l in enumerate(L) if "Camping Fees" in l or "Use Fees" in l)
                    amen = ",".join(a for a in r.get("amenities", []) if "yes" in a.lower() or "amp" in a.lower())
                    got = (r["site"], " / ".join(l for l in L[k + 1:k + 7] if not l.startswith("Note")), amen)
                    break
            print(f"   {t:28} {dt:10} {got[0] if got else '-':16} {got[1] if got else 'no price on first 6 sites'}"
                  f"{'  [' + got[2] + ']' if got and got[2] else ''}", flush=True)
