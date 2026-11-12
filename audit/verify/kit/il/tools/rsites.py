# rsites.py CID -> name loop lat lng maxlen (from cat_CID.json written by catx.py) + ptsfile pts_CID.txt
import json,sys
cid=sys.argv[1]; S=json.load(open(f'cat_{cid}.json'))
out=open(f'pts_{cid}.txt','w')
la=[];lo=[]
for s in sorted(S,key=lambda s:s.get('name')):
    a={x['attribute_name']:x['attribute_value'] for x in s.get('attributes') or []}
    lat=s.get('latitude');lng=s.get('longitude')
    print(s.get('name'),s.get('loop'),lat,lng,a.get('Max Vehicle Length'),a.get('Driveway Length'),s.get('type'))
    if lat: out.write(f"{s.get('name')} {lat} {lng}\n"); la.append(float(lat)); lo.append(float(lng))
if la: print('centroid',sum(la)/len(la),sum(lo)/len(lo),'n',len(la))
