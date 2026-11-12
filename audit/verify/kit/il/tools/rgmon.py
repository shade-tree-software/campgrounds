# rgmon.py CID YYYY-MM ... : per-day status counts from rec.gov month availability
import json,sys,urllib.request,collections
UA='Mozilla/5.0'
cid=sys.argv[1]
for m in sys.argv[2:]:
    u=f'https://www.recreation.gov/api/camps/availability/campground/{cid}/month?start_date={m}-01T00%3A00%3A00.000Z'
    try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":UA}),timeout=40))
    except Exception as e: print(m,"ERR",e); continue
    byday=collections.defaultdict(collections.Counter)
    for sid,s in d.get('campsites',{}).items():
        for day,st in (s.get('availabilities') or {}).items(): byday[day[:10]][st]+=1
    runs=[];prev=None
    for day in sorted(byday):
        sig=tuple(sorted(byday[day].items()))
        if sig!=prev: runs.append((day,sig)); prev=sig
    for r in runs: print(m,r[0],dict(r[1]))
