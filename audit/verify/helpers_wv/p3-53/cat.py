import json,sys,collections
c=json.load(open('/home/andrew/Dev/campgrounds/trip_data/ridb_campsites.json'))[sys.argv[1]]
print(c['fetched'],len(c['sites']))
cnt=collections.Counter(); L=collections.Counter(); de=collections.Counter(); ak=collections.Counter()
for s in c['sites']:
    cnt[(s['type'],s['reservable'],tuple(s['equip']))]+=1
    a=s['attrs']; L[a.get('Max Vehicle Length')]+=1; de[a.get('Driveway Entry')]+=1
    for k in a: ak[k]+=1
for k,v in cnt.items(): print(v,k)
print('len',sorted(L.items(),key=lambda x:str(x[0])));print('entry',de);print('attrs',ak)
for s in c['sites']:
    if any(w in json.dumps(s).lower() for w in ['host','shore','water','elect','amp']): print(s['name'],s['type'],{k:v for k,v in s['attrs'].items() if k not in('Max Vehicle Length','Driveway Entry')})
