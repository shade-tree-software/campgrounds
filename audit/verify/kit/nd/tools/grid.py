# grid.py facilityId start end -> per-unit availability summary + facility season info
import sys,json,urllib.request,collections
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
fid,s,e=int(sys.argv[1]),sys.argv[2],sys.argv[3]
b={"FacilityId":fid,"UnitTypeId":0,"StartDate":s,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":s,"MaxDate":e}
r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
g=json.loads(urllib.request.urlopen(r,timeout=60).read())
F=g["Facility"]
for k in F:
    if k not in ("Units",): 
        v=F[k]; 
        if isinstance(v,(str,int,float,bool)) or (isinstance(v,(list,dict)) and len(json.dumps(v))<800): print(k,json.dumps(v)[:800])
units=list(F["Units"].values())
if len(sys.argv)>4:
    for u in units: print(u["Name"],u.get("VehicleLength"),u.get("Latitude"),u.get("Longitude"),"".join(('A' if sl.get("IsFree") else ('-' if not sl.get("IsInSeason",True) else 'x')) for sl in u.get("Slices",{}).values()))
else:
    u=units[0]; print("UNITKEYS",list(u.keys())); sl=list(u["Slices"].values()); print(json.dumps(sl[0])); print(json.dumps(sl[-1]))
