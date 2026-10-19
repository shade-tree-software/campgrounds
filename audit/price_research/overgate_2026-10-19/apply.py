"""Apply the over-gate sweep + the long-minimum drops (AWH 2026-10-19). Run once."""
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from edit_entries import edit

KEEP = {  # read from each candidate's fees note: base rate actually at/under the gate, or a family-proximity exception
    556: 'Fort Myers family exception: 9 km from family (same basis as the named Fort Myers keeps)',
    4761: '$52.62 INCLUDES Florida tax; ~$49 before tax',
    4768: '$60 tax included at a Good Sam Park; before tax less 10% is ~$48-50, too close to call',
    2038: 'posted 20% discount for 2 people: $45',
    4622: 'posted Good Sam rate $45.90',
    11483: '$50 cash or check (at the gate, not over)',
    15169: 'C$62.83 before HST (stored figure includes tax)',
    12882: 'C$75 HST included = ~C$65 before tax',
    14684: '$56.25 includes taxes and fees; before them ~$50, too close to call',
}
NAMES = {3903: ('Kritters Northcountry Campground and Cabins', 'MI', 'private'),
         3981: ('Buttersville Campground', 'MI', 'local'), 12768: ('Salmon Point RV Park', 'BC', 'private')}
MIN_DROPS = {
    3903: 'Campspot requires 3 nights on every date read (May-Oct 2027); own pages state no minimum and no phone waiver found',
    3981: "township page: 'A minimum stay of 3 nights is required' on every stay; no first-come sites named",
    12768: 'Campspot requires 3 nights on every date read, Oct 2026-Jun 2027; own pages state no minimum and no phone waiver found',
}
RULE = '(AWH 2026-10-19 standing rule)'
cand = json.load(open(HERE + '/candidates.json'))
log = open(os.path.dirname(HERE) + '/dropped_2026-10-19.jsonl', 'a')
fns, kept = {}, []
for r in cand:
    if r['id'] in KEEP:
        r['why'] = KEEP[r['id']]; kept.append(r); continue
    gs = ' (Good Sam Park; %.2f after 10%%)' % (r['low'] * 0.9) if r['gs'] else ''
    why = 'over the %s gate: base %s %s%s; no gateway within 40 km, no named exception' % (
        'US$50' if r['cur'] == 'USD' else 'C$69', r['cur'], r['low'], gs)
    log.write(json.dumps({'id': r['id'], 'name': r['name'], 'state': r['state'], 'ownership': r['ownership'],
                          'action': 'removed', 'why': why + ' ' + RULE}, ensure_ascii=False) + '\n')
    fns[r['id']] = lambda e: None
for i, w in MIN_DROPS.items():
    fns[i] = lambda e: None
    n, st, o = NAMES[i]
    log.write(json.dumps({'id': i, 'name': n, 'state': st, 'ownership': o, 'action': 'removed', 'why': w + ' ' + RULE}, ensure_ascii=False) + '\n')
json.dump(kept, open(HERE + '/kept_on_review.json', 'w'), indent=1, ensure_ascii=False)
edit(fns, note_rescanned=False)
print('dropped', len(fns), 'kept on review', len(kept))
