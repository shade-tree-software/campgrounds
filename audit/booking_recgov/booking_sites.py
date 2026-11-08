"""Read-only: which individual sites at the 28 candidates are bookable, and what type."""
import json, sys, time, collections, urllib.error
sys.path.insert(0, "/home/andrew/Dev/campgrounds"); sys.path.insert(0, "/home/andrew/Dev/campgrounds/ridb")
import fetch_facility as ff

SP = "/tmp/claude-1000/-home-andrew-Dev-campgrounds/63033443-99f7-4b5a-af4e-d10daf222e24/scratchpad/"
d = json.load(open(SP + "booking_check.json"))
cache = json.load(open("/home/andrew/Dev/campgrounds/trip_data/ridb_campsites.json"))
RVE = {"RV", "RV/MOTORHOME", "TRAILER", "FIFTH WHEEL"}


def month(fid, y, m):
    for wait in (0, 60, 180, 400):
        time.sleep(wait)
        try:
            return ff.fetch_availability_month(fid, y, m)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
    raise RuntimeError("still rate-limited")


out = []
for r in d:
    st = r.get("statuses") or {}
    if st.get("Available", 0) + st.get("Reserved", 0) == 0:
        continue
    fid = r["fid"]; sites = {s["id"]: s for s in (cache.get(fid) or {}).get("sites", [])}
    book = set()
    for y, m in [(2026, 12), (2027, 3), (2027, 6)]:
        for sid, days in month(fid, y, m).items():
            if any(v in ("Available", "Reserved") for v in days.values()):
                book.add(sid)
        time.sleep(3)
    rows = []
    for sid in sorted(book):
        s = sites.get(sid, {})
        rows.append({"site": s.get("name"), "type": s.get("type"),
                     "rv": bool(set(s.get("equip") or []) & RVE), "cat_reservable": s.get("reservable")})
    rec = {"id": r["id"], "name": r["name"], "fid": fid, "total_sites": len(sites), "bookable": rows}
    out.append(rec)
    kinds = collections.Counter((x["type"], x["rv"]) for x in rows)
    print(r["id"], r["name"][:30], "| bookable", len(rows), "of", len(sites), "|", dict(kinds), flush=True)
json.dump(out, open(SP + "booking_sites.json", "w"), ensure_ascii=False, indent=1)
