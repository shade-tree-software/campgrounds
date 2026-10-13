"""One unit of each site type in chosen facilities of a US eDirect (Tyler) RDR booking site, priced on later dates.

    RDR_PAUSE=1.0 python3 -I rdr_units.py API_BASE GRID_DATE PRICE_DATE[,PRICE_DATE2] FACILITYID [FACILITYID ...] > OUT.jsonl

rdr_rates.py walks every facility of every park and prices two units of each type; on a slow host that is hours. This
reads only the facilities named: the grid (which lists a facility's units, and answers only inside the booking window)
on GRID_DATE, then for each unit type the unit with the longest vehicle length is priced with the per-unit call
search/details/<UnitId>/startdate/<date>/nights/1/0/0, which answers beyond the window. Each line: the facility, the
unit type, how many units it has, the longest vehicle length among them, the priced unit and its rate on each date
(2026-10-12)."""
import json, os, re, sys, time, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
PAUSE = float(os.environ.get("RDR_PAUSE", "1.0"))
base, gdate, pdates, fids = sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4:]


def call(path, body=None):
    time.sleep(PAUSE)
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=90).read())


for fid in fids:
    try:
        g = call("search/grid", {"FacilityId": int(fid), "UnitTypeId": 0, "StartDate": gdate, "InSeasonOnly": False,
                                 "WebOnly": True, "IsADA": False, "SleepingUnitId": 0, "MinVehicleLength": 0,
                                 "UnitCategoryId": 0, "UnitTypesGroupIds": [], "MinDate": gdate, "MaxDate": gdate})
    except Exception as x:  # noqa: BLE001
        print(json.dumps({"facilityId": int(fid), "error": f"grid: {x}"}), flush=True)
        continue
    fac = g.get("Facility") or {}
    types = {t["UnitTypeId"]: t.get("Name") for t in (fac.get("UnitTypes") or {}).values()} if fac.get("UnitTypes") else {}
    by = {}
    for u in (fac.get("Units") or {}).values():
        by.setdefault(u.get("UnitTypeId"), []).append(u)
    if not by:
        print(json.dumps({"facilityId": int(fid), "facility": (fac.get("Name") or "").strip(), "error": "no units"}),
              flush=True)
        continue
    for tid, us in by.items():
        lens = [u.get("VehicleLength") or 0 for u in us]
        pick = max(us, key=lambda u: ((u.get("VehicleLength") or 0), not u.get("IsAda")))
        rec = {"facilityId": int(fid), "facility": (fac.get("Name") or "").strip(), "placeId": fac.get("PlaceId"),
               "unitTypeId": tid, "unitType": types.get(tid) or re.sub(r"\s*#.*$", "", pick.get("Name") or ""), "units": len(us),
               "maxLength": max(lens), "unitId": pick["UnitId"], "unit": pick.get("Name"), "rates": {}}
        for d in pdates:
            try:
                x = call(f"search/details/{pick['UnitId']}/startdate/{d}/nights/1/0/0")
                rec["rates"][d] = {"rate": x.get("Rate"), "fee": x.get("Fee"), "rateType": x.get("RateTypeName")}
            except Exception as e:  # noqa: BLE001
                rec["rates"][d] = {"error": str(e)}
        print(json.dumps(rec, ensure_ascii=False), flush=True)
