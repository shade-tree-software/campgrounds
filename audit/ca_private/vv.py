# usage: vv.py 'idx|decision|kind|why|base_rate'  ... -> append verdicts (CA scratch)
import json,sys,os
H=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(f'{H}/candidates.json'))['candidates']
with open(f'{H}/verdicts.jsonl','a') as f:
    for a in sys.argv[1:]:
        p=a.split('|'); i=int(p[0])
        r={"name":d[i]['name'],"decision":p[1],"why":p[3],"decided":"2026-10-07","idx":i}
        if p[2]: r["kind_of_no"]=p[2]
        if len(p)>4 and p[4]: r["base_rate"]=float(p[4])
        f.write(json.dumps(r,ensure_ascii=False)+"\n"); print(i,p[1],d[i]['name'])
