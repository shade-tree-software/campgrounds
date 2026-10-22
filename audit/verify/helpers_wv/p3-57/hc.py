import re,json,sys
sys.setrecursionlimit(10000)
s=open(sys.argv[1]).read()
d=json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',s,re.S).group(1))
def find_land(o):
    if isinstance(o,dict):
        if isinstance(o.get("sites"),dict) and "edges" in o["sites"]: return o
        for v in o.values():
            r=find_land(v)
            if r: return r
    elif isinstance(o,list):
        for v in o:
            r=find_land(v)
            if r: return r
L=find_land(d)
for k in ['fullName','status','cityName','countyName','bookingsCount','recommendsCount','recommendsPercentage','isNameAddressPhoneVisible','checkInStartTime','checkOutTime','overview','description','hostDescription','updatedAt','publishedAt']:
    if k in L: print(k,':',str(L[k])[:1500])
for k,v in L.items():
    if isinstance(v,(str,int,float,bool)) and k not in ('overview','description'): print(' ',k,'=',str(v)[:200])
for e in L['sites']['edges']:
    n=e.get('node',{})
    print('SITE',json.dumps({k:v for k,v in e.items() if k!='node'})[:600])
    print('  NODE',json.dumps({k:v for k,v in n.items() if not isinstance(v,(dict,list)) or k in('accommodationKeys','amenities','features')})[:2500])
print('=== NODE nested')
for e in L['sites']['edges']:
    n=e['node']
    for k,v in n.items():
        if isinstance(v,(dict,list)) and k not in('photos','images','contributedPhotos','reviews','media'):
            print(k, json.dumps(v)[:1200])
print('=== LAND nested keys', [k for k,v in L.items() if isinstance(v,(dict,list))])
for k in ('amenities','features','activities','terrains','rules','policies','cancellationPolicy','checkIn','checkOut','host','lodgingFeatures','landFeatures','siteFeatures'):
    if k in L: print('LAND',k,json.dumps(L[k])[:1200])
