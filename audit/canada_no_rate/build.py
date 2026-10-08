# build.py -> worklist.json: the Canada private-gap parks whose ORIGINAL sweep verdict was
# no_rate (QC 72 / ON 50 / BC 36 = 158), joined with what the sweep already knew about each:
# verdicts.jsonl, list.json (RV Life / Good Sam rows), google.txt (gm.py), keys.tsv +
# sites.tsv (squashed key -> site URL).
#
# Membership is decided on the ORIGINAL rows only (verdict rows WITHOUT a "followup" key),
# so the list - and the per-province row numbers info.py uses - stay stable after follow-up
# verdicts are appended. Each row also carries the latest follow-up verdict, if any, as
# `followup` (decision / kind_of_no / base_rate).
import json, re, os
OUT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(OUT, '..', '..'))
rows = []
for st in ('qc', 'on', 'bc'):
    d = f'{REPO}/audit/{st}_private'
    orig, fu, order = {}, {}, []
    for line in open(f'{d}/verdicts.jsonl'):
        if not line.strip():
            continue
        v = json.loads(line)
        if v.get('followup'):
            fu[v['name']] = v
            continue
        if v['name'] not in orig:
            order.append(v['name'])
        orig[v['name']] = v
    lst = json.load(open(f'{d}/list.json'))
    byname = {}
    for b in ('passing', 'price_only', 'unrated', 'rv_other', 'goodsam_only'):
        for r in lst.get(b, []):
            byname.setdefault(r['name'], (b, r))
    keys = {}
    for l in open(f'{d}/keys.tsv'):
        k, n = l.rstrip('\n').split('\t')
        keys[n] = k
    sites = {}
    for l in open(f'{d}/sites.tsv'):
        k, u = l.rstrip('\n').split('\t')
        sites[k] = u
    goog = {}
    for l in open(f'{d}/google.txt'):
        goog[l.split(' | ')[0]] = l.rstrip('\n')
    for n in order:
        v = orig[n]
        if v.get('kind_of_no') != 'no_rate':
            continue
        b, r = byname.get(n, (None, {}))
        k = keys.get(n, re.sub(r'[^A-Za-z0-9]', '', n))
        g = next((gl for q, gl in goog.items() if q.startswith(n + ' ')), '')
        f = fu.get(n)
        rows.append({
            'st': st.upper(), 'name': n, 'bucket': b, 'key': k,
            'site': sites.get(k, ''),
            'rv': {x: r.get(x) for x in ('stars', 'rate', 'reviews', 'sites', 'city', 'lat', 'lng', 'url')} if b != 'goodsam_only' else None,
            'gs': {x: r.get(x) for x in ('city', 'lat', 'lng', 'phone', 'gs')} if b == 'goodsam_only' else None,
            'google': g,
            'why': v.get('why', ''),
            'has_txt': os.path.exists(f'{d}/txt/{k}.txt'),
            'followup': {x: f.get(x) for x in ('decision', 'kind_of_no', 'base_rate')} if f else None,
        })
json.dump(rows, open(f'{OUT}/worklist.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(rows), Counter(r['st'] for r in rows))
print('settled:', Counter((r['st'], r['followup']['decision']) for r in rows if r['followup']))
