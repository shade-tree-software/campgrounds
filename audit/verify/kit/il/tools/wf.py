# wf.py facId date -> name|pad|WaterFront|Lake dist|shaded|desc
import sys,json,urllib.request,time,re
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
def call(p,b=None):
    time.sleep(0.4)
    r=urllib.request.Request(base+p,data=json.dumps(b).encode() if b is not None else None,headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r,timeout=90).read())
fid,d=int(sys.argv[1]),sys.argv[2]
g=call("search/grid",{"FacilityId":fid,"UnitTypeId":0,"StartDate":d,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d,"MaxDate":d})
for u in sorted(g["Facility"]["Units"].values(),key=lambda u:u.get("OrderBy") or 0):
    x=call(f"search/details/{u['UnitId']}/startdate/{d}/nights/1/0/0")
    am={v["ShortName"]:v.get("Value") for v in (x.get("Amenities") or {}).values()}
    U=x.get("Unit") or {}
    desc=re.sub(r'<[^>]+>|\s+',' ',(U.get("DescriptionHtml") or "").split("No Show Policy")[0]).strip()[:120]
    print(u["Name"],am.get("Pad Length"),am.get("Water Front"),am.get("Lake/River/Creek"),am.get("Shaded"),am.get("Amp"),x.get("Rate"),desc,sep="|")
