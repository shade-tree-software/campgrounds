# Shared head for phase-7 post scripts (pins, phones, websites, waterfront; apply.py writes none of these).
# Use: a post script starts with  exec(open("audit/verify/kit/post_head.py").read())  and runs from the
# repo root as  python3 -I $S/post_p3-NNN.py p3-NNN  (argv[1] = batch label written into waterfront_evidence).
# pin(id, old_loc, lat, lng) re-pins + refetches elevation (Open-Meteo, then NED 10 m); ph/web(id, old, new) assert
# the old value (web new falsy = delete); wf(id, old, new, evidence) refuses --AWH entries; save() writes ensure_ascii=False.
import json, urllib.request, sys, datetime
P='campgrounds.json'; D=datetime.date.today().isoformat(); B=sys.argv[1]
d=json.load(open(P,encoding='utf-8')); by={c['id']:c for c in d}
def elev(lat,lng):
    for u,f in ((f'https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lng}',lambda j:j['elevation'][0]),
                (f'https://api.opentopodata.org/v1/ned10m?locations={lat},{lng}',lambda j:round(j['results'][0]['elevation'],1))):
        for t in range(2):
            try: return f(json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)))
            except Exception as ex: print('elev retry',u[:40],ex)
    raise SystemExit('no elevation')
def pin(i,old,lat,lng):
    c=by[i]; assert c['location']==old,(i,c['location'])
    c['location']=f'{lat},{lng}'; e=elev(lat,lng); print(i,'elev',c.get('elevation_meters'),'->',e); c['elevation_meters']=e
def ph(i,old,new):
    c=by[i]; assert c.get('phone')==old,(i,c.get('phone')); c['phone']=new
def web(i,old,new):
    c=by[i]; assert c.get('website')==old,(i,c.get('website'))
    if new: c['website']=new
    else: del c['website']
def wf(i,old,new,ev):
    c=by[i]; assert c.get('waterfront')==old; assert '--AWH' not in (c.get('note') or '') and '--AWH' not in (c.get('waterfront_evidence') or '')
    c['waterfront']=new; c['waterfront_evidence']=(c.get('waterfront_evidence') or '').rstrip()+f' | {B} ({D}): {ev}'
def save():
    open(P,'w',encoding='utf-8').write(json.dumps(d,ensure_ascii=False,indent=2)+'\n'); print('written')
