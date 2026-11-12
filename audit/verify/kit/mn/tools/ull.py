# ull.py facilityId [date] -> unit name, len, lat, lng from grid MapInfo + centroid
import json,sys,urllib.request
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
d=sys.argv[2] if len(sys.argv)>2 else "2027-06-15"
b={"FacilityId":int(sys.argv[1]),"UnitTypeId":0,"StartDate":d,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d,"MaxDate":d}
r=urllib.request.Request(base+"search/grid",data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
F=json.loads(urllib.request.urlopen(r,timeout=60).read())["Facility"]
la=[];lo=[]
for u in sorted(F["Units"].values(),key=lambda u:u.get("OrderBy") or 0):
    m=u.get("MapInfo") or {}
    if m.get("Latitude"): la.append(m["Latitude"]); lo.append(m["Longitude"])
    if len(sys.argv)>3: print(u["ShortName"],u.get("VehicleLength"),round(m.get("Latitude") or 0,5),round(m.get("Longitude") or 0,5))
if la: print("centroid",round(sum(la)/len(la),5),round(sum(lo)/len(lo),5),"n",len(la),"lat",round(min(la),5),round(max(la),5),"lng",round(min(lo),5),round(max(lo),5))
