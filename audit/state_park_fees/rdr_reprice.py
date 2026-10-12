"""Re-price the units of an rdr_rates.py run on other dates, 2026-10-12.

    python3 -I rdr_reprice.py API_BASE RATES.jsonl DATE[,DATE2] > OUT.jsonl

The grid (which lists a facility's units) only answers inside the booking window, but the per-unit call
search/details/<UnitId>/startdate/<date>/nights/1/0/0 answers beyond it, so a site found in October can be priced for
next June. Every unit of RATES is priced on DATE, and the first unit of each facility and type on DATE2 too. One JSON
line per unit and date, with RATES' fields."""
import json, os, sys, time, urllib.request
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
PAUSE = float(os.environ.get("RDR_PAUSE", "1.0"))
base, rates_path, dates = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
units, first = {}, set()
for line in open(rates_path, encoding="utf-8"):
    r = json.loads(line)
    if "unitId" in r and r["unitId"] not in units:
        units[r["unitId"]] = r
for uid, r in units.items():
    key = (r["placeId"], r["facilityId"], r["unitTypeId"])
    for d in (dates if key not in first else dates[:1]):
        rec = {k: r[k] for k in ("placeId", "park", "facilityId", "facility", "unitTypeId", "unitType", "unitId", "unit",
                                 "length")}
        rec["date"] = d
        time.sleep(PAUSE)
        try:
            x = json.loads(urllib.request.urlopen(urllib.request.Request(
                f"{base}search/details/{uid}/startdate/{d}/nights/1/0/0",
                headers={"User-Agent": UA, "Accept": "application/json"}), timeout=60).read())
            rec.update({"rate": x.get("Rate"), "fee": x.get("Fee"), "rateType": x.get("RateTypeName")})
        except Exception as e:  # noqa: BLE001
            rec["error"] = str(e)
        print(json.dumps(rec), flush=True)
    first.add(key)
