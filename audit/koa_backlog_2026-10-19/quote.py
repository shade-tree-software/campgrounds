"""Quote every backlog KOA on koa.com's own booking form (koa.py, through the one driver browser).

One night for a 23-ft motorhome, 2 adults, no pets: Tuesday 2027-05-18 first (the night the 2026-10-19
high-tier pass used, so the two passes compare), then Tuesday 2027-06-15 when May returns no priced RV
site (not open yet, or that night is sold out). Progress is the data: a row already in quotes.jsonl is
never re-quoted, so a killed run just resumes. Each page's text is kept in dumps/<slug>.txt.

python3 quote.py [--limit N]"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KOA = os.path.join(HERE, '..', 'private_gap_browser', 'koa.py')
OUT = os.path.join(HERE, 'quotes.jsonl')
DATES = [('05/18/2027', '05/19/2027'), ('06/15/2027', '06/16/2027')]


def quote(slug, ci, co):
    dump = os.path.join(HERE, 'dumps', '%s_%s.txt' % (slug, ci[:2]))
    env = dict(os.environ, KOA_DUMP=dump, PYTHONPATH=os.path.expanduser('~/.cache/ekko-pw'))
    try:
        out = subprocess.run(['python3', KOA, slug, ci, co], capture_output=True, text=True, timeout=300, env=env).stdout
    except subprocess.TimeoutExpired:
        return {'date': ci, 'error': 'timeout', 'types': []}
    types, info = [], ''
    for line in out.split('\n'):
        if line.startswith('dates '):
            info = line.split('|', 1)[-1].strip()
        m = re.match(r'^([\d,.]*)\s*\| (.+)$', line)
        if m and not line.startswith('dates'):
            types.append({'price': float(m.group(1).replace(',', '')) if m.group(1) else None, 'name': m.group(2).strip()})
    return {'date': ci, 'info': info, 'types': types, 'dump': os.path.relpath(dump, HERE)}


def main():
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 10 ** 6
    os.makedirs(os.path.join(HERE, 'dumps'), exist_ok=True)
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)['slug'] for l in open(OUT) if l.strip()}
    rows = [r for r in json.load(open(os.path.join(HERE, 'backlog.json'))) if r['slug'] and r['slug'] not in done]
    seen = set()
    for r in rows[:limit]:
        if r['slug'] in seen:
            continue
        seen.add(r['slug'])
        tries = []
        for ci, co in DATES:
            q = quote(r['slug'], ci, co)
            tries.append(q)
            if any(t['price'] for t in q['types']):
                break
        rec = {'slug': r['slug'], 'name': r['name'], 'state': r['state'], 'tries': tries}
        with open(OUT, 'a') as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
        best = tries[-1]
        ps = [t['price'] for t in best['types'] if t['price']]
        print('%-28s %s %s %s' % (r['slug'], best['date'], min(ps) if ps else '-', best.get('info', '')[:90]), flush=True)


if __name__ == '__main__':
    main()
