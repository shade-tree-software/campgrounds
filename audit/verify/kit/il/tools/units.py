# units.py facilityId griddate [detaildate] [namefilter] -> unit id/name/len, and details (rate, amenities, desc) for filtered units
import sys,json,urllib.request,time,re
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
def call(p,b=None):
    time.sleep(0.5)
    r=urllib.request.Request(base+p,data=json.dumps(b).encode() if b is not None else None,headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r,timeout=90).read())
fid,gd=int(sys.argv[1]),sys.argv[2]; dd=sys.argv[3] if len(sys.argv)>3 else gd; flt=sys.argv[4] if len(sys.argv)>4 else None
g=call("search/grid",{"FacilityId":fid,"UnitTypeId":0,"StartDate":gd,"InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":gd,"MaxDate":gd})
for u in sorted(g["Facility"]["Units"].values(),key=lambda u:u.get("OrderBy") or 0):
    print(u["UnitId"],u["Name"],u.get("VehicleLength"),u.get("AllowWebBooking"))
    if flt and re.search(flt,u["Name"]):
        x=call(f"search/details/{u['UnitId']}/startdate/{dd}/nights/1/0/0")
        if len(sys.argv)>5: print(json.dumps(x)[:4000]); continue
        U=x.get("Unit") or {}
        d=(U.get("DescriptionHtml") or "").split("No Show Policy")[0]
        am=x.get("Amenities") or {}
        print("   rate",x.get("Rate"),x.get("RateTypeName"),x.get("PullInTypeName"),"|",re.sub(r'<[^>]+>|\s+',' ',d).strip()[:300],"|",{v["ShortName"]:v.get("Value") for v in am.values()})
