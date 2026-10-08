# info.py ST IDX [IDX...]   -> what the sweep knew about work-list rows (per-province index)
# info.py ST todo           -> the rows of that province with no follow-up verdict yet
# Rows come from worklist.json (rebuild with build.py after appending verdicts; the indexes
# are stable because membership is decided on the original sweep verdicts).
import json, sys, os
rows = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worklist.json')))
st = sys.argv[1].upper()
sub = [r for r in rows if r['st'] == st]
if len(sys.argv) > 2 and sys.argv[2] == 'todo':
    todo = [(i, r['name']) for i, r in enumerate(sub) if not r.get('followup')]
    print(f'{st}: {len(todo)} of {len(sub)} still open')
    for i, n in todo:
        print(f'  #{i} {n}')
    sys.exit()
for a in sys.argv[2:]:
    r = sub[int(a)]
    g = r['google'].split(' | ')
    print(f"#{a} {r['name']} [{r['bucket']}] site={r['site']}")
    print('   google:', ' | '.join(g[1:])[:260])
    if r['rv']:
        print('   rvlife:', {k: r['rv'][k] for k in ('stars', 'rate', 'reviews', 'sites', 'city')})
    if r['gs']:
        print('   goodsam:', r['gs'])
    print('   why:', r['why'][:160])
    if r.get('followup'):
        print('   FOLLOW-UP:', r['followup'])
