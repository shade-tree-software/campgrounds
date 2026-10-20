"""Price/minimum gate over quotes.jsonl -> verdicts.json (and a summary on stdout).

The base rate is the cheapest priced RV site with hookups on KOA's form for a 23-ft motorhome, one night,
before tax (curation doc: "the cheapest RV site a 23-ft rig fits, one night for two, before tax"); sites
named "No Hookups"/"Dry" don't count. Limit US$50 / C$69; a Good Sam Park (3 KOAs in the directory) is
tested at 90%; within 40 km of a gateway (gateways.py) the price half is lifted. Minimum-stay text on the
form is carried along for the per-park read (AWH 2026-10-19: >2 nights outside weekends/holidays = drop).
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'audit', 'price_research'))
from gateways import gateways  # noqa: E402

CANADA = {'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'ON', 'PE', 'QC', 'SK'}
NOHOOK = re.compile(r'(?i)no hook|dry|primitive|tent|no services|unserviced|non-serviced')
backlog = {r['slug']: r for r in json.load(open(os.path.join(HERE, 'backlog.json'))) if r['slug']}
gs = [p for p in json.load(open(os.path.join(ROOT, 'trip_data', 'goodsam_parks.json')))['parks'].values() if p.get('gs')]


def km(a, b):
    h = (math.sin(math.radians(b[0] - a[0]) / 2) ** 2 + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0]))
         * math.sin(math.radians(b[1] - a[1]) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(h))


def minimum_lines(dump):
    p = os.path.join(HERE, dump)
    if not os.path.exists(p):
        return []
    return sorted({l.strip() for l in open(p, encoding='utf-8') if re.search(r'(?i)\bminimum\b|night min', l)})[:4]


# retry.py re-quoted the no-quote rows on a night inside each calendar; its try becomes the last one
RETRY = {}
if os.path.exists(os.path.join(HERE, 'quotes_retry.jsonl')):
    RETRY = {json.loads(l)['slug']: json.loads(l) for l in open(os.path.join(HERE, 'quotes_retry.jsonl'))}
verdicts = []
for line in open(os.path.join(HERE, 'quotes.jsonl')):
    q = json.loads(line)
    if q['slug'] in RETRY:
        q['tries'] += RETRY[q['slug']]['tries']
    r = backlog[q['slug']]
    t = q['tries'][-1]
    hook = [x for x in t['types'] if x['price'] and not NOHOOK.search(x['name'])]
    base = min((x['price'] for x in hook), default=None)
    high = max((x['price'] for x in hook), default=None)
    cad = r['state'] in CANADA
    limit = 69 if cad else 50
    is_gs = any(km((r['lat'], r['lng']), (p['lat'], p['lng'])) < 0.8 and 'KOA' in p['name'] for p in gs)
    tested = round(base * 0.9, 2) if (base and is_gs) else base
    gw = gateways(r['lat'], r['lng'])
    mins = minimum_lines(t.get('dump', ''))
    if base is None:
        v = 'no quote'
    elif tested <= limit:
        v = 'pass'
    elif gw:
        v = 'pass (gateway)'
    else:
        v = 'over'
    verdicts.append({'slug': q['slug'], 'name': r['name'], 'koa_name': r['koa_name'], 'state': r['state'],
                     'lat': r['lat'], 'lng': r['lng'], 'stars': r['stars'], 'reviews': r['reviews'], 'date': t['date'],
                     'base': base, 'high': high, 'currency': 'CAD' if cad else 'USD', 'good_sam': is_gs,
                     'gateway': gw[0][2] + ' (%d km)' % round(gw[0][0]) if gw else None, 'minimum': mins,
                     'info': t.get('info', ''), 'verdict': v})
json.dump(verdicts, open(os.path.join(HERE, 'verdicts.json'), 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter(v['verdict'] for v in verdicts), 'with minimum text:', sum(1 for v in verdicts if v['minimum']))
