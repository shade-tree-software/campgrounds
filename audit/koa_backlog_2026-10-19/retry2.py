"""Quote the backlog KOAs RV Life listed without a koa.com slug (slugs found by hand), same nights as quote.py."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quote import quote, HERE, DATES
OUT = os.path.join(HERE, 'quotes_retry.jsonl')
SLUGS = ['wapakoneta', 'allendale', 'weidman', 'buffalo', 'lava-hot-springs-city-center']
done = {json.loads(l)['slug'] for l in open(OUT)} if os.path.exists(OUT) else set()
for s in SLUGS:
    if s in done:
        continue
    tries = []
    for ci, co in DATES:
        q = quote(s, ci, co); tries.append(q)
        if any(t['price'] for t in q['types']):
            break
    with open(OUT, 'a') as fh:
        fh.write(json.dumps({'slug': s, 'tries': tries}, ensure_ascii=False) + '\n')
    ps = [t['price'] for t in tries[-1]['types'] if t['price']]
    print('%-30s %s %s %s' % (s, tries[-1]['date'], min(ps) if ps else '-', tries[-1].get('info', '')[:90]), flush=True)
