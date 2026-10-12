"""For each park URL: read the first listing pages, take one site of each type, and print its
1-night price breakdown (resident / non-resident) on each date."""
import json, re, sys, time, urllib.request, http.cookiejar
sys.path.insert(0, __import__('os').path.dirname(__file__))
import ra_list, ra_price
SKIP = re.compile(r"(?i)shelter|amphi|yurt|cabin|cottage|lodge|group|pavil|picnic|boat|slip|day use|horse|equest|bear den")
dates = sys.argv[1].split(',')
for url in sys.argv[2:]:
    d = ra_list.park(url)
    types = {}
    for r in d['sites']:
        t = r['cells'][1] if len(r['cells']) > 1 else '?'
        if not SKIP.search(t): types.setdefault(t, []).append(r)
    print(f"== {url.split('/camping/')[1].split('/')[0]} parkId={d['parkId']}: {len(d['sites'])} sites; types { {k: len(v) for k, v in types.items()} }", flush=True)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())); op.addheaders = [("User-Agent", ra_price.UA)]
    op.open(f"{d['host']}/campgroundDetails.do?contractCode={d['contract']}&parkId={d['parkId']}", timeout=60).read()
    for t, members in types.items():
        for dt in dates:
            got = None
            for r in members[:6]:
                p, L = ra_price.price(d['host'], d['contract'], d['parkId'], r['siteId'], dt, op)
                time.sleep(0.3)
                if p:
                    k = next(j for j, l in enumerate(L) if 'Camping Fees' in l or 'Use Fees' in l)
                    got = (r['site'], ' / '.join(l for l in L[k+1:k+6] if not l.startswith('Note')))
                    break
            print(f"   {t:32} {dt:10} {got[0] if got else '-':14} {got[1] if got else 'no price on first 6 sites'}", flush=True)
