# catx.py FACILITY_ID: rec.gov per-site catalog summary via the public search API (no RIDB key needed)
import json,sys,urllib.request,collections
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
cid=sys.argv[1]; sites=[]; start=0
while True:
    u=f'https://www.recreation.gov/api/search/campsites?fq=asset_id%3A{cid}&size=200&start={start}'
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=40))
    sites+=d.get('campsites') or []
    if len(sites)>=int(d.get('total') or 0) or not d.get('campsites'): break
    start=len(sites)
json.dump(sites,open(f'cat_{cid}.json','w'))
print('sites',len(sites))
cnt=collections.Counter(); L=collections.Counter(); amps=collections.Counter(); ws=collections.Counter()
for s in sites:
    a={x['attribute_name']:x['attribute_value'] for x in s.get('attributes') or []}
    eq=sorted({e.get('equipment_name') for e in s.get('permitted_equipment') or []})
    cnt[(s.get('type'),s.get('type_of_use'),s.get('reservable'),tuple(eq))]+=1
    L[a.get('Max Vehicle Length')]+=1; amps[a.get('Electricity Hookup')]+=1
    ws[(a.get('Water Hookup'),a.get('Sewer Hookup'))]+=1
    if any(w in (s.get('name','')+s.get('loop','')).lower() for w in ['host']): print('HOST?',s.get('name'),s.get('loop'))
for k,v in cnt.most_common(): print(v,k)
print('maxlen',sorted(L.items(),key=lambda x:str(x[0])));print('electric',amps);print('water/sewer',ws)
