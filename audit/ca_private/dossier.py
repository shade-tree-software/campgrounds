# usage: dossier.py IDX ...  -> candidate row + crawl block + Google line (CA private gap scratch)
import json,sys,glob,re,os
H=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(f'{H}/candidates.json'))['candidates']
crawl={}
for f in glob.glob(f'{H}/crawl.txt'):
    cur=None
    for l in open(f,errors='replace'):
        m=re.match(r'=== (\d+) ',l)
        if m: cur=int(m.group(1)); crawl[cur]=[l.rstrip()]
        elif cur is not None: crawl[cur].append(l.rstrip()[:200])
goog={}
for f in glob.glob(f'{H}/google.txt'):
    for l in open(f,errors='replace'):
        goog[l.split(' | ')[0].strip()]=l.strip()
done={}
for l in open(f'{H}/verdicts.jsonl'):
    r=json.loads(l); done[r.get('idx')]=r['decision']
for a in sys.argv[1:]:
    i=int(a); c=d[i]
    print(f"\n##### {i} {c['name']} | {c['city']} | {c['stars']}*{'$'*c['price']} avg${c['rate']} {c['sites']}s {c['reviews']}r | {c['lat']},{c['lng']} | {c['near']} | url={c.get('cg_url')} | {c.get('url')} {'[DONE '+done[i]+']' if i in done else ''}")
    for l in crawl.get(i,['(no crawl)'])[:12]: print('  C',l)
    print('  G',goog.get(f"{c['name']} {c['city']} CA",'(no google)'))
