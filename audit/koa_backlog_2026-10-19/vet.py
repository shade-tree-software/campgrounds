"""Turn hand decisions (decisions_NN.json) for gate-passing KOAs into append_state rows + waterfront rows.

A decision is {slug, px, py, src: "sheet"|"zoom", center: [lat,lng] (zoom only), hw (zoom only),
waterfront, wf, extra (optional note sentence), drop (optional reason)}. px/py are pixel coordinates in
the 900x900 crop the pin was read from: sheet crops are 500 m half-width around RV Life's pin, zoom crops
are centred on `center` with half-width `hw`. Name, street, town and phone come from the booking form's
"Your Reservation" block; the rate from the quote; elevation from Open-Meteo.

python3 vet.py decisions_NN.json   -> results_NN.json (append_state format), wf_NN.json, vetted.json updated"""
import json, math, os, re, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
dec_path = sys.argv[1]
tag = re.search(r'decisions_(\w+)\.json', dec_path).group(1)
V = {v['slug']: v for v in json.load(open(os.path.join(HERE, 'verdicts.json')))}
Q = {}
for line in open(os.path.join(HERE, 'quotes.jsonl')):
    q = json.loads(line); Q[q['slug']] = q
if os.path.exists(os.path.join(HERE, 'quotes_retry.jsonl')):  # retry.py's later night, as gate.py reads it
    for line in open(os.path.join(HERE, 'quotes_retry.jsonl')):
        q = json.loads(line)
        if q['slug'] in Q:
            Q[q['slug']]['tries'] += q['tries']
B = {r['slug']: r for r in json.load(open(os.path.join(HERE, 'backlog.json'))) if r['slug']}


def pin(d):
    v = V[d['slug']]
    if d['src'] == 'sheet':
        c, hw = (v['lat'], v['lng']), 500
    else:
        c, hw = d['center'], d['hw']
    m = 2 * hw / 900
    return (round(c[0] - (d['py'] - 450) * m / 111320, 5),
            round(c[1] + (d['px'] - 450) * m / (111320 * math.cos(math.radians(c[0]))), 5))


def reservation_block(slug):
    t = Q[slug]['tries'][-1]
    L = [l.strip() for l in open(os.path.join(HERE, t['dump']), encoding='utf-8') if l.strip()]
    i = L.index('Your Reservation:')
    name, street, town, phone = L[i + 1:i + 5]
    town = re.sub(r'\s+,', ',', town)
    return name, street, town, phone


def money(x, cad):
    s = '%.2f' % x if x != int(x) else '%d' % x
    return ('C$' if cad else '$') + s


def summary(slug):
    names = ' '.join(t['name'] for t in Q[slug]['tries'][-1]['types'] if t['price'])
    bits = []
    if re.search(r'(?i)full hookup', names): bits.append('full-hookup')
    if re.search(r'(?i)water/electric', names): bits.append('water/electric')
    s = ' and '.join(bits) + ' RV sites' if bits else 'RV sites'
    if re.search(r'(?i)pull thru', names): s += ', pull-throughs'
    return s


decisions = json.load(open(dec_path))
pts = [pin(d) for d in decisions if not d.get('drop')]
elev = []
if pts:
    u = 'https://api.open-meteo.com/v1/elevation?latitude=%s&longitude=%s' % (
        ','.join(str(p[0]) for p in pts), ','.join(str(p[1]) for p in pts))
    elev = json.load(urllib.request.urlopen(u, timeout=60))['elevation']
rows, wf, k = [], [], 0
for d in decisions:
    v, b = V[d['slug']], B[d['slug']]
    if d.get('drop'):
        rows.append({'decision': 'skip', 'name': v['name'], 'reason': d['drop']}); continue
    lat, lng = pts[k]; e = elev[k]; k += 1
    name, street, town, phone = reservation_block(d['slug'])
    cad = v['currency'] == 'CAD'
    lo, hi = money(v['base'], cad), money(v['high'], cad)
    rate = lo if lo == hi else '%s-%s' % (lo, hi.replace('C$', '').replace('$', ''))
    mo, dy, yr = (int(x) for x in v['date'].split('/'))
    when = '%s-%s %d' % ('early' if dy <= 10 else 'mid' if dy <= 20 else 'late',
                         ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                          'October', 'November', 'December'][mo - 1], yr)
    stars = ('%g' % b['stars']) + '*'
    tier = '$' * (b['price_level'] or 0)
    kind = re.search(r'KOA (Holiday|Journey|Resort)', name)
    note = ('%s at %s, %s; %s. RV sites %s a night before tax for %s weeknight on KOA\'s booking form.%s RV Life %s%s. --Claude'
            % ('KOA ' + kind.group(1) if kind else 'KOA campground', street, town.split(',')[0], summary(d['slug']),
               rate, ('an ' if when[0] in 'aeiou' else 'a ') + when, (' ' + d['extra']) if d.get('extra') else '', stars, (', ' + tier) if tier else ''))
    ev = ('KOA booking form (koa.com/campgrounds/%s/reserve/) quoted %s, 1 night, 23-ft motorhome: RV site types %s before tax (read 2026-10-19); RV Life %s over %s reviews, %s sites'
          % (d['slug'], '%s-%s-%s' % (v['date'][6:], v['date'][:2], v['date'][3:5]), rate, stars, b['reviews'], b['sites']))
    if v['good_sam']:
        ev += '; a Good Sam Park, tested at the rate less 10%'
    if v['verdict'] == 'pass (gateway)':
        ev += '; within 40 km of a gateway (%s, gateways.py), so the price gate is lifted' % v['gateway']
    rows.append({'decision': 'add', 'name': name, 'location': '%s,%s' % (lat, lng), 'elevation_meters': e,
                 'ownership': 'private', 'website': 'https://koa.com/campgrounds/%s/' % d['slug'],
                 'phone': re.sub(r'^1-', '', phone).replace('(', '').replace(') ', '-'), 'note': note,
                 'inclusion_evidence': ev, 'waterfront': d['waterfront'], 'wf': d['wf'], 'state': v['state'], 'slug': d['slug']})
json.dump(rows, open(os.path.join(HERE, 'results_%s.json' % tag), 'w'), indent=1, ensure_ascii=False)
vp = os.path.join(HERE, 'vetted.json')
vetted = json.load(open(vp)) if os.path.exists(vp) else []
vetted += [d['slug'] for d in decisions if d['slug'] not in vetted]
json.dump(vetted, open(vp, 'w'), indent=0)
for r in rows:
    print(r['decision'], r.get('state', ''), r['name'], r.get('location', ''), r.get('waterfront', ''), '|', r.get('note', r.get('reason', ''))[:200])
