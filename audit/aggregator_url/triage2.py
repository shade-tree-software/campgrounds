import json,re,math,glob
C={c['id']:c for c in json.load(open('candidates.json'))}
P={p['id']:p for p in json.load(open('probe.json'))}
AG=r'rvlife|campgroundreviews|thedyrt|goodsam|campendium|allstays|roverpass|freecampsites|rvparky|hipcamp|koa\.com|facebook|yelp|tripadvisor|campnative|texascampgrounds|aaa\.com|harvesthosts'
def hv(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d));return 6371*2*math.asin(math.sqrt(math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2))
out=[]
for f in sorted(glob.glob('gm_q2_0*.txt')):
  for l in open(f):
    parts=l.split(' | ')
    try: name,la,lo,i=parts[0].split('|'); i=int(i)
    except: continue
    site=re.search(r"site=\['([^']+)'\]",l); ll=re.search(r"ll=\('([-\d.]+)', '([-\d.]+)'\)",l)
    rat=re.search(r"\('(\d\.\d)', '([\d,]+)'\)",l); h1=re.search(r"\| \['([^']*)'\] \|",l)
    dist=hv(float(la),float(lo),float(ll[1]),float(ll[2])) if ll else None
    s=site[1] if site else None
    cls='operator_site' if s and not re.search(AG,s,re.I) and dist is not None and dist<3 else ('site_far' if s and not re.search(AG,s,re.I) else 'none')
    out.append(dict(id=i,name=name,st=C[i]['state'],gname=h1[1] if h1 else None,site=s,dist=round(dist,2) if dist is not None else None,rating=rat.groups() if rat else None,rp_book=P[i]['instant']>0,code=P[i]['code'],cls=cls))
json.dump(out,open('triage2.json','w'),indent=1)
import collections;print(collections.Counter((o['cls'],o['rp_book']) for o in out))
for o in out:
  if o['cls']!='none': print(o['id'],o['name'][:32],o['st'],'|',(o['gname'] or '')[:30],o['dist'],o['site'],o['rating'])
