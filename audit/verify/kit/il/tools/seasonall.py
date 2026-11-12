# seasonall.py facilityId start end -> in-season runs over a long span (grid calls in 20-day steps)
import sys,json,urllib.request,datetime,time
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
fid=int(sys.argv[1]); s=datetime.date.fromisoformat(sys.argv[2]); e=datetime.date.fromisoformat(sys.argv[3])
allv={}
d=s
while d<=e:
    d2=min(d+datetime.timedelta(days=20),e)
    b={"FacilityId":fid,"UnitTypeId":0,"StartDate":d.isoformat(),"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d.isoformat(),"MaxDate":d2.isoformat()}
    r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    F=json.loads(urllib.request.urlopen(r,timeout=90).read())["Facility"]
    allv.update({k[:10]:v for k,v in (F.get("SeasonDates") or {}).items()})
    d=d2+datetime.timedelta(days=1); time.sleep(0.4)
runs=[]
for k,v in sorted(allv.items()):
    if runs and runs[-1][2]==v: runs[-1][1]=k
    else: runs.append([k,k,v])
for a in runs: print(a)
