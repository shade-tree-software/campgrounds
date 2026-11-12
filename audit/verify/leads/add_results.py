"""Append phase-7 lead adds (results/*.json, decision "add") to campgrounds.json.

Each result already carries its waterfront audit and structured fields, so the entry is written whole:
rating from the result's `rvlife` ("4.5*/$$$"), fees and every structured group (hookups, sites,
facilities, season, booking) with its provenance. Ids continue from max(id) over BOTH location files. A result whose name or pin (300 m) is already in the database is
refused unless the result names that id in `separate_from` (checked by hand). `curation_note` is carried.
Skips go to verdicts.jsonl. Dry run by default; --apply writes.
"""
import glob, json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CG = os.path.join(ROOT, 'campgrounds.json')
FAM = os.path.join(ROOT, 'trip_data', 'family.json')
TODAY = __import__('datetime').date.today().isoformat()


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def pt(loc):
    return tuple(map(float, loc.split(',')))


GROUPS = ('hookups', 'sites', 'facilities', 'season', 'booking', 'status')


def provenance(r, g):
    """A group's provenance: its own *_source, else the lead's inclusion evidence; checked = last 'read' date."""
    src = r.get(g + '_source') or 'phase-7 lead result (the sources in inclusion_evidence)'
    dates = re.findall(r'\b(20\d\d-\d\d-\d\d)\b', src + ' ' + (r.get('inclusion_evidence') or ''))
    dates = [d for d in dates if d <= TODAY]  # a quote's stay date is not a read date
    return {'source': src, 'checked': max(dates) if dates else TODAY, 'method': 'manual'}


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
    if r['decision'] != 'add':
        skips.append({k: r.get(k) for k in ('name', 'state', 'decision', 'kind_of_no', 'why')} | {'decided': TODAY})
        continue
    loc = pt(r['location'])
    clash = [i for q, i in pins if km(loc, q) < 0.3 and i not in r.get('separate_from', [])]
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
    for g in GROUPS:
        if r.get(g):
            e[g] = r[g]
            prov[g] = provenance(r, g)
    if r.get('curation_note'):
        e['curation_note'] = r['curation_note']
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
