"""Over-gate sweep (AWH 2026-10-19): private entries whose base nightly rate is over US$50 / C$69.

Screens out the specific exceptions before anything is dropped:
named keeps (feedback_price_gate_proximity_exceptions), any entry carrying an --AWH note, gateways.py (40 km), the Good Sam
rate test (discounts.good_sam -> rate less 10%), and any entry a trip references.
Writes candidates.json (to review) and exempt.json (with the reason each one stays).
"""
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE.rsplit('/audit/', 1)[0]
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.dirname(HERE))
import gateways, trips

LIMIT = {'USD': 50, 'CAD': 69}
NAMED = {14435}  # Fort Myers ids and Liberty Harbor 3363 left 2026-10-21: covered by gateways.py (family homes; New York 3 km)
d = json.load(open(ROOT + '/campgrounds.json'))
cand, exempt = [], []
for e in d:
    if e.get('kind') != 'campground' or e.get('ownership') not in ('private', 'hipcamp'):
        continue
    f = e.get('fees') or {}
    low, cur = f.get('nightly_low'), f.get('currency', 'USD')
    if low is None or cur not in LIMIT or low <= LIMIT[cur]:
        continue
    lat, lng = map(float, e['location'].split(','))
    row = {'id': e['id'], 'name': e['name'], 'state': e['state'], 'ownership': e['ownership'],
           'low': low, 'high': f.get('nightly_high'), 'cur': cur, 'fees_note': f.get('note'),
           'gs': (e.get('discounts') or {}).get('good_sam'), 'note': e.get('note')}
    why = None
    if e['id'] in NAMED:
        why = 'named exception'
    elif 'AWH' in (e.get('note') or ''):
        why = "AWH's own note (chosen knowing the price)"
    elif row['gs'] and low * 0.9 <= LIMIT[cur]:
        why = 'Good Sam Park: %.2f after 10%%' % (low * 0.9)
    else:
        g = gateways.gateways(lat, lng)
        if g:
            why = 'gateway: ' + ', '.join('%s %.0f km' % (n, k) for k, _, n in g[:2])
        elif trips.campground_references(e['id']):
            why = 'family stayed here'
    row['why'] = why
    (exempt if why else cand).append(row)
json.dump(cand, open(HERE + '/candidates.json', 'w'), indent=1, ensure_ascii=False)
json.dump(exempt, open(HERE + '/exempt.json', 'w'), indent=1, ensure_ascii=False)
print('candidates', len(cand), 'exempt', len(exempt))
from collections import Counter
print(Counter(r['why'].split(':')[0] for r in exempt))
