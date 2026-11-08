"""Read-only: for the 46 'not reservable' entries RIDB disagrees with, ask
recreation.gov whether the FACILITY takes bookings.

Signals per entry:
  - RIDB facility `Reservable` flag
  - live availability statuses over three months inside the booking window:
    Available/Reserved = a bookable site; Open = in service but walk-up;
    Not Reservable / NYR = no booking signal.
Writes JSON to argv[1].
"""
import collections, json, os, re, sys, time
sys.path.insert(0, "/home/andrew/Dev/campgrounds")
sys.path.insert(0, "/home/andrew/Dev/campgrounds/ridb")
from recgov_calendar import facility_ids
import fetch_facility as ff

IDS = [5579, 3323, 3330, 3343, 3347, 3356, 3746, 5183, 5255, 6427, 6434, 6478, 6505, 6511,
       8021, 9463, 9502, 9517, 9560, 9890, 9936, 9937, 9952, 9957, 9960, 9968, 9975, 10047,
       10048, 10050, 10051, 10331, 10690, 10977, 11868, 11905, 11908, 12001, 12057, 12070,
       12086, 12155, 12156, 12169, 12272, 12387, 13272]
MONTHS = [(2026, 12), (2027, 3), (2027, 6)]

rows = json.load(open("/home/andrew/Dev/campgrounds/campgrounds.json"))
by = {r["id"]: r for r in rows}
links = facility_ids([by[i] for i in IDS])
out = []
for i in IDS:
    e = by[i]; fid = links.get(i)
    rec = {"id": i, "name": e["name"], "state": e.get("state"), "fid": fid,
           "booking": e.get("booking"), "note": e.get("note")}
    if fid:
        try:
            f = ff._get(f"facilities/{fid}", {"full": "false"})
            rec["facility_reservable"] = f.get("Reservable")
            rec["facility_name"] = f.get("FacilityName")
        except Exception as ex:  # noqa: BLE001
            rec["facility_error"] = str(ex)
        st = collections.Counter()
        for y, m in MONTHS:
            try:
                for days in ff.fetch_availability_month(fid, y, m).values():
                    st.update(days.values())
            except Exception as ex:  # noqa: BLE001
                rec.setdefault("avail_errors", []).append(f"{y}-{m:02d}: {ex}")
            time.sleep(1.0)
        rec["statuses"] = dict(st)
    out.append(rec)
    print(i, fid, rec.get("facility_reservable"), rec.get("statuses"), flush=True)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
