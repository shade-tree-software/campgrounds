import json,math,re,sys
st,path=sys.argv[1],sys.argv[2]
cg=[e for e in json.load(open('campgrounds.json')) if e.get('state')==st]
def hv(a,b,c,d):
    p=math.radians;x=math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2;return 12742*math.asin(math.sqrt(x))
STOP={'state','park','recreation','area','sra','sp','campground','historic','site','the','of','lake','forest','beach','camping','wma','reservation'}
def toks(s): return set(w for w in re.findall(r'[a-z]+',s.lower()) if w not in STOP)
for pid,p in sorted(json.load(open(path)).items(),key=lambda x:x[1]['name']):
    best=None
    for e in cg:
        la,lo=map(float,e['location'].split(','))
        d=hv(p['lat'],p['lng'],la,lo) if 'lat' in p else 999
        if (toks(p['name'])&toks(e['name']) and d<25) or d<1.5 or (toks(p['name']) and toks(p['name'])<=toks(e['name'])):
            if best is None or d<best[0]: best=(d,e['id'],e['name'])
    if not best: print('MISS',pid,p['name'],p.get('lat'),p.get('lng'))
