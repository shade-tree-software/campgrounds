import json,sys,urllib.request
base="https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
def call(p,b):
    r=urllib.request.Request(base+p,data=json.dumps(b).encode(),headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r,timeout=60).read())
sp=call("search/place",{"Nights":1,"StartDate":sys.argv[2] if len(sys.argv)>2 else "2027-06-15","PlaceId":int(sys.argv[1]),"WebOnly":True,"CountUnits":True,"InSeasonOnly":False})["SelectedPlace"]
print(sp["Name"],sp.get("Latitude"),sp.get("Longitude"))
for f in sp["Facilities"].values(): print(f["FacilityId"],f["Name"],f.get("Latitude"),f.get("Longitude"))
g=call("search/grid",{"FacilityId":int(sys.argv[3]),"UnitTypeId":0,"StartDate":"2027-06-15","InSeasonOnly":False,"WebOnly":True,"IsADA":False,"SleepingUnitId":0,"MinVehicleLength":0,"UnitCategoryId":0,"UnitTypesGroupIds":[],"MinDate":"2027-06-15","MaxDate":"2027-06-15"}) if len(sys.argv)>3 else None
if g:
    u=list(g["Facility"]["Units"].values())[0]; print({k:v for k,v in u.items() if k!="Slices"})
