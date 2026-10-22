import json,sys,urllib.request,re,html
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=40))
cid=sys.argv[1]
d=get(f'https://www.recreation.gov/api/camps/campgrounds/{cid}')['campground']
json.dump(d,open(f'rg_{cid}.json','w'))
def clean(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s or ''))).strip()
for k in ['facility_name','facility_type','facility_phone','facility_email','reservable','facility_longitude','facility_latitude','campsite_type_of_use','campsite_reserve_type']:
    print(k,':',d.get(k))
for k in ['facility_description_map','facility_directions']:
    v=d.get(k)
    if isinstance(v,dict):
        for kk,vv in v.items(): print('##',kk,':',clean(vv)[:1500])
    else: print('##',k,clean(str(v))[:800])
print('## notices'); 
for n in d.get('notices') or []: print(' -',n.get('notice_type'),clean(n.get('notice_text'))[:600])
print('## rules',json.dumps(d.get('facility_rules'))[:2500])
print('## amen',[a.get('attribute_name') if isinstance(a,dict) else a for a in (d.get('amenities') or [])][:40])
print('## addr',d.get('addresses'))
try:
    r=get(f'https://www.recreation.gov/api/camps/campgrounds/{cid}/rates')
    json.dump(r,open(f'rg_{cid}_rates.json','w'))
    for s in r.get('rates_list') or []:
        print('RATE',s.get('season_description'),s.get('season_start'),s.get('season_end'),json.dumps(s.get('price_map'))[:500])
except Exception as e: print('rates err',e)
