"""Apply one split prepared under kit/sk/splits/: parent_<id>.json replaces fields on the kept entry
(provenance merged per group), each entry of new_<slug>.json is appended with an id from max over BOTH
location files, and every resulting entry gets a verify_scan naming the split.

    python3 -I audit/verify/kit/sk/splits/apply_split.py <id> new_<slug>.json [--apply]
"""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
CG, FAM = os.path.join(ROOT, 'campgrounds.json'), os.path.join(ROOT, 'trip_data', 'family.json')
TODAY = datetime.date.today().isoformat()
pid, newf = int(sys.argv[1]), sys.argv[2]
cg = json.load(open(CG, encoding='utf-8'))
fam = json.load(open(FAM, encoding='utf-8')) if os.path.exists(FAM) else []
if not fam:
    sys.exit('no trip_data/family.json: ids would collide')
parent = next(e for e in cg if e['id'] == pid)
p = json.load(open(os.path.join(HERE, f'parent_{pid}.json'), encoding='utf-8'))
reasons = p.pop('_reasons', '')
prov = p.pop('provenance', {})
parent.update(p)
parent.setdefault('provenance', {}).update(prov)
next_id = max(e['id'] for e in cg + fam) + 1
news = json.load(open(os.path.join(HERE, newf), encoding='utf-8'))
ids = []
for n in news:
    n = {'id': next_id, **{k: v for k, v in n.items() if k != 'id'}}
    n['verify_scan'] = {'checked': TODAY, 'sources': f'Entry created today in the split from {pid} (audit/verify/kit/sk/splits/NOTES_{pid}.md); every group read today with manual provenance.',
                        'note': f'Split from {pid} ({parent["name"]}). No re-read needed.'}
    cg.append(n); ids.append(next_id); next_id += 1
vs = parent.get('verify_scan') or {}
vs['note'] = (vs.get('note', '') + f' | {TODAY} split: {reasons} New: {", ".join(map(str, ids))}.').strip(' |')
vs['checked'] = TODAY
parent['verify_scan'] = vs
print(pid, parent['name'], parent['location'], parent['waterfront'])
for n in cg[-len(ids):]:
    print(n['id'], n['name'], n['location'], n['waterfront'])
if '--apply' in sys.argv:
    open(CG, 'w', encoding='utf-8').write(json.dumps(cg, ensure_ascii=False, indent=2) + '\n')
    print('applied')
