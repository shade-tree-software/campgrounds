# sat1.py facId date name1 name2 ... -> rate for named units on date
import sys,json,urllib.request,time
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
def call(p,b=None):
    time.sleep(0.4)
    r=urllib.request.Request(base+p,data=json.dumps(b).encode() if b is not None else None,headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r,timeout=90).read())
fid,d=int(sys.argv[1]),sys.argv[2]
g=call("search/grid",{"FacilityId":fid,"UnitTypeId":0,"StartDate":d,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d,"MaxDate":d})
for u in g["Facility"]["Units"].values():
    if u["Name"].split("#")[-1] in sys.argv[3:]:
        x=call(f"search/details/{u['UnitId']}/startdate/{d}/nights/1/0/0"); print(u["Name"],d,x.get("Rate"))
