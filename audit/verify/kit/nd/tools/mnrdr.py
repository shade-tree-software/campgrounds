import json, sys, time, urllib.request, collections
base = "https://mnrdr.usedirect.com/MinnesotaRDR/rdr/"
UA = "Mozilla/5.0"
d = sys.argv[2] if len(sys.argv) > 2 else "2027-06-15"
def call(path, body=None):
    time.sleep(0.4)
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())
pid = int(sys.argv[1])
sp = call("search/place", {"Nights": 1, "IsADA": False, "MinVehicleLength": None, "UnitCategoryId": None, "StartDate": d,
      "CustomerId": 0, "Sort": None, "WebOnly": True, "NearbyCountLimit": 10, "AmenityIds": None, "CountUnits": True,
      "Longitude": None, "isSearchAllParks": False, "PlaceId": pid, "Latitude": None, "NearbyOnlyAvailable": False,
      "UnitTypesGroupIds": None, "SleepingUnitId": None, "HighlightedPlaceId": 0, "customerClassificationId": 0,
      "InSeasonOnly": False, "NearbyLimit": 0, "RestrictADA": False, "CountNearby": False})["SelectedPlace"]
print("PLACE", sp and sp.get("Name"), sp and (sp.get("Latitude"), sp.get("Longitude")))
for f in (sp.get("Facilities") or {}).values():
    print("FAC", f["FacilityId"], f["Name"], {u["UnitTypeId"]: u["Name"] for u in (f.get("UnitTypes") or {}).values()})
    try:
        g = call("search/grid", {"FacilityId": f["FacilityId"], "UnitTypeId": 0, "StartDate": d, "InSeasonOnly": False,
              "WebOnly": True, "IsADA": False, "SleepingUnitId": 0, "MinVehicleLength": 0, "UnitCategoryId": 0,
              "UnitTypesGroupIds": [], "MinDate": d, "MaxDate": d})
    except Exception as x:
        print("  grid err", x); continue
    F = g.get("Facility") or {}
    us = (F.get("Units") or {}).values()
    c = collections.Counter((u.get("UnitTypeId"), u.get("VehicleLength")) for u in us)
    print("  units", len(list((F.get("Units") or {}).values())), sorted(c.items(), key=lambda kv: str(kv[0])))
    for u in list((F.get("Units") or {}).values())[:1]:
        print("  sample", json.dumps({k: u.get(k) for k in ("Name", "UnitTypeId", "VehicleLength", "AllowWebBooking", "IsWebViewable", "UnitCategoryId", "IsAda")}))
    print("  web", collections.Counter(u.get("AllowWebBooking") for u in (F.get("Units") or {}).values()))
