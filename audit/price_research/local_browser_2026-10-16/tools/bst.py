"""bst.py browser.jsonl ST  - show crawled records for one state, rate-ish lines only, deduped"""
import json, re, sys
st = sys.argv[2]
d = {r['id']: r for r in json.load(open('/home/andrew/Dev/campgrounds/campgrounds.json'))}
K = re.compile(r'(?i)\$\s?\d|\d\s?\$|night|daily|per day|/day|tarif|rate')
B = re.compile(r'(?i)loan|tax(es)? rate|millage|swim|softball|basketball|lifeguard|permit|deposit|ramada|pavilion|shelter|wedding|golf|membership|aerobic')
for l in open(sys.argv[1]):
    r = json.loads(l)
    if d.get(r['id'], {}).get('state') != st: continue
    print(f"## {r['id']} {r['name']}")
    seen = set()
    for p in r['pages']:
        if 'err' in p: print('   ERR', p['url'][:90]); continue
        print('   [' + p['title'][:110] + ']')
        for x in p['lines'].splitlines():
            x = x.strip()
            if x and x not in seen and K.search(x) and not B.search(x):
                seen.add(x); print('      ' + x[:170])
