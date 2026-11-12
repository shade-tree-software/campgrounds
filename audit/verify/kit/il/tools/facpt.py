import sys,json,urllib.request
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
for fid in sys.argv[2:]:
    d=sys.argv[1]
    b={"FacilityId":int(fid),"UnitTypeId":0,"StartDate":d,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d,"MaxDate":d}
    r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    F=json.loads(urllib.request.urlopen(r,timeout=90).read())["Facility"]
    us=list(F["Units"].values())
    print(fid,F["Name"],F.get("Latitude"),F.get("Longitude"),"units",len(us),"unit coords",sum(1 for u in us if u.get("Latitude")))
