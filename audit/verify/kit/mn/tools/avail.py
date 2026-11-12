# avail.py facilityId date -> per unit availability slice for that date
import sys,json,urllib.request,collections
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
fid,d=int(sys.argv[1]),sys.argv[2]
b={"FacilityId":fid,"UnitTypeId":0,"StartDate":d,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d,"MaxDate":d}
r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
F=json.loads(urllib.request.urlopen(r,timeout=90).read())["Facility"]
c=collections.Counter()
for u in F["Units"].values():
    for s in (u.get("Slices") or {}).values():
        c[(s.get("IsFree"),s.get("IsBlocked"),s.get("Lock"),s.get("ReservationId") and 'res')]+=1
print(F.get("Name"),d,dict(c), {k:F.get(k) for k in ("IsInSeason","Restrictions") if k in F})
u=list(F["Units"].values())[0]; print(json.dumps((list((u.get("Slices") or {}).values()) or [None])[0])[:400])
