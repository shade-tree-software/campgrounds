# season.py facilityId start end -> in-season date runs
import sys,json,urllib.request
base="https://threeriversparks-rdr.recreation-management.tylerapp.com/ThreeRiversrdr/rdr/"
fid,s,e=int(sys.argv[1]),sys.argv[2],sys.argv[3]
b={"FacilityId":fid,"UnitTypeId":0,"StartDate":s,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":s,"MaxDate":e}
r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
F=json.loads(urllib.request.urlopen(r,timeout=90).read())["Facility"]
sd=sorted(F["SeasonDates"].items()); runs=[]; 
for d,v in sd:
    if runs and runs[-1][2]==v: runs[-1][1]=d[:10]
    else: runs.append([d[:10],d[:10],v])
for a in runs: print(a)
