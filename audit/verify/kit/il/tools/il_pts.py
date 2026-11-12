import sys,json,urllib.request
base="https://il-rdr.recreation-management.tylerapp.com/IllinoisRDR/rdr/"
fid,d=int(sys.argv[1]),sys.argv[2]
b={"FacilityId":fid,"UnitTypeId":0,"StartDate":d,"InSeasonOnly":False,"WebOnly":False,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d,"MaxDate":d}
r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
g=json.loads(urllib.request.urlopen(r,timeout=90).read())
us=list(g["Facility"]["Units"].values())
if len(sys.argv)>3: print(json.dumps(us[0],indent=0)[:2500]); sys.exit()
for u in us:
    m=u.get("MapInfo") or {}; print(u["Name"].split("#")[-1].strip(), m.get("Latitude"), m.get("Longitude"), u.get("VehicleLength"), u.get("IsWebViewable"), u.get("AllowWebBooking"))
