"""Nightly rates per site type off a US eDirect (Tyler) RDR booking site, 2026-10-12.

    python3 -I rdr_rates.py API_BASE DATE[,DATE2] PLACEID [PLACEID ...] > OUT.jsonl

API_BASE e.g. https://ohiordr.usedirect.com/Ohiordr/rdr/. The place search lists each park's campground facilities and
their unit types but no prices; the grid lists the units; a unit's rate comes from the call the page makes when a site
is clicked, GET search/details/<UnitId>/startdate/<YYYY-MM-DD>/nights/1/0/0 ({"Rate": "41.00", "Fee": "6.50",
"RateTypeName": "Standard", ...}). For every campground facility and unit type, up to two units are priced on DATE and
the first on DATE2. Cabins, group camps, shelters, day-use and other non-campsite types are skipped. One JSON line per
unit and date."""
import json, os, re, sys, time, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
SKIP = re.compile(r"(?i)cabin|lodge|yurt|cottage|group|shelter|day use|pavilion|boat|slip|dock|horse|equest|rent|teepee|"
                  r"lean|bunk|house|dorm|room|getaway|camper cabin|tent only|walk|hike|backpack|canoe|kayak")
base, dates, pids = sys.argv[1], sys.argv[2].split(","), sys.argv[3:]


PAUSE = float(os.environ.get("RDR_PAUSE", "0.3"))   # Virginia's host answered 403 after ~300 quick calls


def call(path, body=None):
    time.sleep(PAUSE)
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def place(pid):
    return call("search/place", {"Nights": 1, "IsADA": False, "MinVehicleLength": None, "UnitCategoryId": None,
                                 "StartDate": dates[0], "CustomerId": 0, "Sort": None, "WebOnly": True, "NearbyCountLimit": 10,
                                 "AmenityIds": None, "CountUnits": True, "Longitude": None, "isSearchAllParks": False,
                                 "PlaceId": int(pid), "Latitude": None, "NearbyOnlyAvailable": False, "UnitTypesGroupIds": None,
                                 "SleepingUnitId": None, "HighlightedPlaceId": 0, "customerClassificationId": 0,
                                 "InSeasonOnly": True, "NearbyLimit": 0, "RestrictADA": False, "CountNearby": False})


def grid(fid):
    return call("search/grid", {"FacilityId": fid, "UnitTypeId": 0, "StartDate": dates[0], "InSeasonOnly": True,
                                "WebOnly": True, "IsADA": False, "SleepingUnitId": 0, "MinVehicleLength": 0, "UnitCategoryId": 0,
                                "UnitTypesGroupIds": [], "MinDate": dates[0], "MaxDate": dates[0]})


for pid in pids:
    try:
        sp = place(pid)["SelectedPlace"]
    except Exception as x:  # noqa: BLE001
        print(json.dumps({"placeId": int(pid), "error": f"place: {x}"}), flush=True)
        continue
    if not sp:
        # a place with nothing in season on DATE comes back with SelectedPlace null
        print(json.dumps({"placeId": int(pid), "error": "place: no SelectedPlace (nothing in season on that date?)"}), flush=True)
        continue
    for f in (sp.get("Facilities") or {}).values():
        types = {u["UnitTypeId"]: u["Name"] for u in (f.get("UnitTypes") or {}).values() if not SKIP.search(u["Name"])}
        if not types:     # (a facility's name can mention a shelter or group site beside its campsites: 'Sites 1-52; Maple Shelter')
            continue
        try:
            units = (grid(f["FacilityId"]).get("Facility") or {}).get("Units") or {}
        except Exception as x:  # noqa: BLE001
            print(json.dumps({"placeId": int(pid), "facilityId": f["FacilityId"], "error": f"grid: {x}"}), flush=True)
            continue
        by_type = {}
        for u in units.values():
            if u.get("UnitTypeId") in types and not u.get("IsAda"):
                by_type.setdefault(u["UnitTypeId"], []).append(u)
        for tid, us in by_type.items():
            for k, u in enumerate(us[:2]):
                for d in (dates if k == 0 else dates[:1]):
                    rec = {"placeId": int(pid), "park": sp.get("Name"), "facilityId": f["FacilityId"], "facility": f["Name"].strip(),
                           "unitTypeId": tid, "unitType": types[tid], "unitId": u["UnitId"], "unit": u.get("Name"),
                           "length": u.get("VehicleLength"), "date": d}
                    try:
                        x = call(f"search/details/{u['UnitId']}/startdate/{d}/nights/1/0/0")
                        rec.update({"rate": x.get("Rate"), "fee": x.get("Fee"), "rateType": x.get("RateTypeName"),
                                    "use": x.get("UseTypeName")})
                    except Exception as e:  # noqa: BLE001
                        rec["error"] = str(e)
                    print(json.dumps(rec), flush=True)
