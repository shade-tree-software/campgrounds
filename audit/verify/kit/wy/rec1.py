#!/usr/bin/env python3
"""rec1.py TABID -> list sections/groups; rec1.py TABID GROUPID -> facilities JSON (Natrona County Rec1 catalog)."""
import sys, json, subprocess, os
K='eb0d69a5af9968478d02f3431ce3274c'
B='https://secure.rec1.com/WY/natrona-county-wy/catalog'
CJ=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','w','dl','rec1','cj')
def get(path):
    out=subprocess.run(['curl','-s','-A','Mozilla/5.0','-b',CJ,'-c',CJ,'-H','X-Requested-With: XMLHttpRequest',B+path],capture_output=True).stdout
    return json.loads(out)
tab=sys.argv[1]
if len(sys.argv)==2:
    d=get('/getItems/%s/%s'%(K,tab))
    json.dump(d,open('rec1_tab_%s.json'%tab,'w'))
    for s in d.get('sections') or []:
        for g in s.get('groups') or []:
            print(s.get('name'),'|',g['id'],g['name'],g.get('type'),g.get('itemCount'),g.get('minPrice'),g.get('maxPrice'),'|',(g.get('descriptionText') or '')[:300].replace('\n',' '))
else:
    g=sys.argv[2]
    d=get('/getLocationFacilities/%s/%s/%s'%(K,tab,g))
    json.dump(d,open('rec1_g_%s.json'%g,'w'))
    for it in d.get('items') or []:
        print(json.dumps({k:v for k,v in it.items() if k not in('image','thumbnail','images')},ensure_ascii=False)[:700])
