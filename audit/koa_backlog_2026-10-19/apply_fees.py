"""Write fees for the KOA backlog adds (ids 15397-15530) from the koa.com quotes behind them.

The backlog put each park's quoted rate in its note but never filled the fees group, so the map
popup showed no price. Rates come from verdicts.json (gate.py's reading of quotes.jsonl + retries):
low = the cheapest hookup site a 23-ft motorhome fits (the gate's base), high = the dearest site
type quoted. Dry run by default; --apply writes campgrounds.json in place, touching only the
'fees' and 'provenance.fees' of entries whose fees are empty.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CG = os.path.join(ROOT, 'campgrounds.json')

verdicts = {v['slug']: v for v in json.load(open(os.path.join(HERE, 'verdicts.json')))}
cg = json.load(open(CG, encoding='utf-8'))
out, misses = [], []
for e in cg:
    if not (15397 <= e['id'] <= 15530) or (e.get('fees') or {}).get('nightly_low') is not None:
        continue
    m = re.search(r'koa\.com/campgrounds/([a-z0-9-]+)', str(e.get('website', '')))
    v = verdicts.get(m.group(1)) if m else None
    if not v or v.get('base') is None:
        misses.append((e['id'], e['name'], m and m.group(1)))
        continue
    mm, dd, yy = v['date'].split('/')
    night = f'{yy}-{mm}-{dd}'
    e['fees'] = {'nightly_low': v['base'], 'nightly_high': v['high'], 'currency': v['currency'], 'checked': '2026'}
    e.setdefault('provenance', {})['fees'] = {
        'source': f"https://koa.com/campgrounds/{v['slug']}/reserve/ (cheapest hookup site type and dearest site "
                  f"type, one night from {night}; RV, 2 adults, a 23-ft motorhome), read 2026-10-19",
        'checked': '2026-10-19'}
    note_rate = re.search(r'RV sites (C?\$[\d.,]+(?:-[\d.,]+)?)', e.get('note', ''))
    out.append((e['id'], v['base'], v['high'], v['currency'], note_rate and note_rate.group(1)))

for r in out:
    print(*r)
print(f'{len(out)} priced, {len(misses)} missing:', misses)
if '--apply' in sys.argv:
    with open(CG, 'w', encoding='utf-8') as f:
        json.dump(cg, f, ensure_ascii=False, indent=2)
        f.write('\n')
