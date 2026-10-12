"""US eDirect (Tyler) RDR place search: each park's campground facilities and their unit types.

    python3 -I rdr_place.py API_BASE START_DATE PLACEID [PLACEID ...] > OUT.json

API_BASE e.g. https://ohiordr.usedirect.com/Ohiordr/rdr/ or
https://il-rdr.recreation-management.tylerapp.com/IllinoisRDR/rdr/; START_DATE MM-DD-YYYY.
Prints, per facility: name, unit types (name, max vehicle length, available count)."""
import json, sys, time, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
base, start = sys.argv[1], sys.argv[2]
out = {}
for pid in sys.argv[3:]:
    body = {"PlaceId": int(pid), "Latitude": 0, "Longitude": 0, "HighlightedPlaceId": 0, "StartDate": start, "Nights": 1,
            "CountNearby": False, "NearbyLimit": 0, "NearbyOnlyAvailable": False, "NearbyCountLimit": 0, "Sort": "Distance",
            "CustomerId": "0", "RefreshFavourites": True, "IsADA": False, "UnitCategoryId": 0, "SleepingUnitId": 0,
            "MinVehicleLength": 0, "UnitTypesGroupIds": []}
    req = urllib.request.Request(base + "search/place", data=json.dumps(body).encode(),
                                 headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=60).read())
    except Exception as x:  # noqa: BLE001
        out[pid] = {"error": str(x)}
        continue
    sp = d.get("SelectedPlace") or {}
    facs = {}
    for f in (sp.get("Facilities") or {}).values():
        facs[f["FacilityId"]] = {"name": f["Name"], "inSeason": f.get("InSeason"),
                                 "units": {u["Name"]: [u.get("MaxVehicleLength"), u.get("AvailableCount")]
                                           for u in (f.get("UnitTypes") or {}).values()}}
    out[pid] = {"name": sp.get("Name"), "description": (sp.get("Description") or "")[:600], "facilities": facs}
    time.sleep(0.5)
json.dump(out, sys.stdout, indent=1)
