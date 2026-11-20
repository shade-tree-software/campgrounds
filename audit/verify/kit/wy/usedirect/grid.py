import sys,json,urllib.request
base="https://wyordr.usedirect.com/wyomingrdr/rdr/"
fid,s,e=int(sys.argv[1]),sys.argv[2],sys.argv[3]
b={"FacilityId":fid,"UnitTypeId":0,"StartDate":s,"InSeasonOnly":False,"WebOnly":False,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":s,"MaxDate":e}
r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
g=json.loads(urllib.request.urlopen(r,timeout=60).read())
json.dump(g,open(f"grid_{fid}_{s}.json","w"))
F=g["Facility"]
for k in F:
    if k!="Units":
        v=F[k]; print(k,json.dumps(v)[:600])
for u in F["Units"].values():
    print(u["UnitId"],u["Name"],u.get("ShortName"),u.get("UnitTypeId"),u.get("VehicleLength"),u.get("Latitude"),u.get("Longitude"),u.get("AllowWebBooking"),u.get("IsWebViewable"),"".join(('A' if sl.get("IsFree") else ('w' if sl.get("IsWalkin") else ('-' if not sl.get("IsInSeason",True) else 'x'))) for sl in u.get("Slices",{}).values()))
