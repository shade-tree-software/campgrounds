# alld.py facilityId date -> per unit: name len web rate type amp water/sewer lake-distance lat lng
import sys,json,urllib.request,time,re
base="https://threeriversparks-rdr.recreation-management.tylerapp.com/ThreeRiversrdr/rdr/"
def call(p,b=None):
    time.sleep(0.35)
    r=urllib.request.Request(base+p,data=json.dumps(b).encode() if b is not None else None,headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r,timeout=90).read())
fid,d=int(sys.argv[1]),sys.argv[2]
g=call("search/grid",{"FacilityId":fid,"UnitTypeId":0,"StartDate":d,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":d,"MaxDate":d})
for u in sorted(g["Facility"]["Units"].values(),key=lambda u:u.get("OrderBy") or 0):
    try: x=call(f"search/details/{u['UnitId']}/startdate/{d}/nights/1/0/0")
    except Exception as e: print(u["Name"],"ERR",e); continue
    am={v["ShortName"]:v.get("Value") for v in (x.get("Amenities") or {}).values()}
    U=x.get("Unit") or {}
    print("|".join(str(v) for v in (u["Name"].split("#")[-1],u.get("VehicleLength"),u.get("AllowWebBooking"),x.get("Rate"),am.get("Pull-thru/Back-in"),am.get("Amp"),am.get("Water Hookup",am.get("Water")),am.get("Sewer Hookup",am.get("Sewer")),am.get("Lake/River/Creek"),U.get("Latitude"),U.get("Longitude"))))
