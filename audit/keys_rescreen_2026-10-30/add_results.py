"""Append the Florida Keys re-screen adds (results/*.json, decision "add") to campgrounds.json.

Each result already carries its waterfront audit, fees and any standing min_stay, so the entry is written
whole: rating from the result's `rvlife` ("4.5*/$$$"), fees and booking with their provenance. Ids continue
from max(id) over BOTH location files. A result whose name or pin (300 m) is already in the database is
refused. Skips go to verdicts.jsonl; a "hold" (an owner-lot resort waiting on AWH) is listed and left alone. Dry run by default; --apply writes.
"""
import glob, json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CG = os.path.join(ROOT, 'campgrounds.json')
FAM = os.path.join(ROOT, 'trip_data', 'family.json')
TODAY = '2026-10-30'


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def pt(loc):
    return tuple(map(float, loc.split(',')))


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


cg = json.load(open(CG, encoding='utf-8'))
fam = json.load(open(FAM, encoding='utf-8')) if os.path.exists(FAM) else []
if not fam:
    sys.exit('no trip_data/family.json: ids would collide; run where it exists')
next_id = max(e['id'] for e in cg + fam) + 1
names = {norm(e['name']) for e in cg}
pins = [(pt(e['location']), e['id']) for e in cg if e.get('location')]
done = {v['name'] for v in map(json.loads, open(os.path.join(HERE, 'verdicts.jsonl')))}

adds, skips = [], []
for p in sorted(glob.glob(os.path.join(HERE, 'results', '*.json'))):
    r = json.load(open(p))
    if r['name'] in done:
        continue
    if r['decision'] == 'hold':
        print('HOLD', r['state'], r['name'], '|', '; '.join(r.get('flags') or [])[:200])
        continue
    if r['decision'] != 'add':
        skips.append({k: r.get(k) for k in ('name', 'state', 'decision', 'kind_of_no', 'why')} | {'decided': TODAY})
        continue
    loc = pt(r['location'])
    clash = [i for q, i in pins if km(loc, q) < 0.3]
    if norm(r['name']) in names or clash:
        sys.exit(f"{r['name']}: already in the database ({clash})")
    m = re.fullmatch(r'([\d.]+)\*/(\$*)', r.get('rvlife', '') or '')
    e = {'id': next_id, 'kind': 'campground', 'name': r['name'], 'location': r['location'],
         'elevation_meters': r['elevation_meters'], 'state': r['state'], 'ownership': r['ownership'],
         'waterfront': r['waterfront'], 'waterfront_evidence': r['waterfront_evidence'],
         'inclusion_evidence': r['inclusion_evidence'], 'website': r['website'], 'phone': r['phone'],
         'note': r['note']}
    if m:
        e['rating'] = {'stars': float(m.group(1)), 'price_tier': len(m.group(2)), 'source': 'rvlife'}
    prov = {}
    if r.get('fees'):
        e['fees'] = r['fees']
        prov['fees'] = {'source': r['fees_source'], 'checked': TODAY, 'method': 'manual'}
    if (r.get('booking') or {}).get('min_stay'):
        e['booking'] = {k: r['booking'][k] for k in ('min_stay', 'note') if r['booking'].get(k)}
        prov['booking'] = {'source': r['booking_source'], 'checked': TODAY, 'method': 'manual'}
    if prov:
        e['provenance'] = prov
    adds.append(e)
    names.add(norm(r['name']))
    pins.append((loc, next_id))
    next_id += 1

for e in adds:
    print(e['id'], e['state'], e['name'], '|', e['waterfront'], '|', e.get('fees'), '|', e.get('booking'))
for s in skips:
    print('skip', s['state'], s['name'], '|', s['kind_of_no'], '|', s['why'][:120])
if '--apply' in sys.argv:
    cg.extend(adds)
    with open(CG, 'w', encoding='utf-8') as f:
        f.write(json.dumps(cg, ensure_ascii=False, indent=2) + '\n')
    with open(os.path.join(HERE, 'verdicts.jsonl'), 'a', encoding='utf-8') as f:
        for e in adds:
            f.write(json.dumps({'name': e['name'], 'state': e['state'], 'decision': 'add', 'id': e['id'],
                                'decided': TODAY}, ensure_ascii=False) + '\n')
        for s in skips:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')
    print(f'applied: +{len(adds)}, {len(skips)} skips')
