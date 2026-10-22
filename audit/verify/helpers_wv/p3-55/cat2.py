import json,sys,collections
d=json.load(open('/home/andrew/Dev/campgrounds/trip_data/ridb_campsites.json'))
v=d[sys.argv[1]]; S=v['sites']; print('fetched',v['fetched'],'n',len(S))
print('types',collections.Counter((s['type'],s['reservable']) for s in S))
ak=collections.Counter(k for s in S for k in s['attrs'])
print('attr keys',ak)
for k in ['Electricity Hookup','Water Hookup','Sewer Hookup','Driveway Entry','Max Vehicle Length','Full Hookup']:
    print(k,collections.Counter(s['attrs'].get(k) for s in S))
print('names',[ (s['name'],s['type']) for s in S if 'STANDARD' not in s['type']][:20])
L=[int(s['attrs'].get('Max Vehicle Length','0') or 0) for s in S]; print('maxlen',sorted(L)[-5:], 'count>=23',sum(1 for x in L if x>=23))
