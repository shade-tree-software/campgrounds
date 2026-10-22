import json,sys,re
d=json.load(open(sys.argv[1]))['pageProps']['fallback']
land=None
for k,v in d.items():
    if isinstance(v,dict) and 'land' in v: land=v['land']; break
    if isinstance(v,dict) and 'data' in v and isinstance(v['data'],dict) and 'land' in v['data']: land=v['data']['land']; break
if not land:
    print([ (k[:80], list(v.keys())[:5] if isinstance(v,dict) else type(v)) for k,v in d.items()]); sys.exit()
print({k:land.get(k) for k in ['status','fullName','cityName','stateName','isBookable','bookable','instantBook','acreage','checkInTime','checkOutTime','minimumNights']})
print('KEYS',[k for k in land.keys()][:80])
def walk(o,path=''):
    if isinstance(o,dict):
        if 'pricePerNight' in o or ('name' in o and 'maxVehicleLength' in o):
            print(path, {k:o.get(k) for k in ['name','status','pricePerNight','basePrice','maxVehicleLength','rvAccess','accommodationType','siteType','isBookable','bookable','maxCapacity','minimumNights','rvHookups','hookups'] if k in o})
        for k,v in o.items(): walk(v,path+'.'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+f'[{i}]')
walk(land)
