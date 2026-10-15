"""Show browser.jsonl records compactly: python3 -I bview.py browser.jsonl [FROM_LINE [TO_LINE]]"""
import json, sys
L = open(sys.argv[1]).read().splitlines()
a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
b = int(sys.argv[3]) if len(sys.argv) > 3 else len(L)
for l in L[a-1:b]:
    r = json.loads(l)
    print(f"## {r['id']} {r['name']}")
    for p in r['pages']:
        if 'err' in p:
            print('   ERR', p['url'][:90], p['err'][:90]); continue
        print('   [' + p['title'][:120] + ']')
        seen = set()
        for x in p['lines'].splitlines():
            x = x.strip()
            if x and x not in seen:
                seen.add(x); print('      ' + x[:170])
