"""Read-only follow-up: the Dec/Mar/Jun sample can't see a summer-only campground (closed
or not yet released). Read the PAST months still in the window (Jul-Oct 2026) for the
entries that showed no bookable night, and count sites with Reserved/Available nights."""
import json, sys, time, collections, urllib.error
sys.path.insert(0, "."); sys.path.insert(0, "ridb")
import fetch_facility as ff
d = json.load(open("audit/booking_recgov/booking_check.json"))
cache = json.load(open("trip_data/ridb_campsites.json"))
def month(fid, y, m):
    for wait in (0, 60, 180, 400):
        time.sleep(wait)
        try: return ff.fetch_availability_month(fid, y, m)
        except urllib.error.HTTPError as e:
            if e.code == 400: return {}
            if e.code != 429: raise
    raise RuntimeError("rate-limited")
out = []
for r in d:
    st = r.get("statuses") or {}
    if st.get("Available", 0) + st.get("Reserved", 0) or not r.get("fid"): continue
    fid = r["fid"]; sites = {s["id"]: s for s in (cache.get(fid) or {}).get("sites", [])}
    book, seen = set(), collections.Counter()
    for y, m in [(2026, 7), (2026, 8), (2026, 9), (2026, 10)]:
        for sid, days in month(fid, y, m).items():
            seen.update(days.values())
            if any(v in ("Available", "Reserved") for v in days.values()): book.add(sid)
        time.sleep(3)
    kinds = collections.Counter(sites.get(s, {}).get("type", "?") for s in book)
    rec = {"id": r["id"], "name": r["name"], "fid": fid, "total_sites": len(sites),
           "bookable_sites": len(book), "kinds": dict(kinds), "statuses": dict(seen),
           "catalog_reservable": sum(1 for s in sites.values() if s.get("reservable"))}
    out.append(rec); print(json.dumps(rec), flush=True)
json.dump(out, open("audit/booking_recgov/past_months.json", "w"), ensure_ascii=False, indent=1)
