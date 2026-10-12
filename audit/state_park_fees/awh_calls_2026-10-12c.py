"""AWH's calls of 2026-10-12 (late evening): python3 -I awh_calls_2026-10-12c.py [--apply]

"Drop St. Ambroise, Shimek's, and Minnesota Valley."

- St. Ambroise Beach Provincial Park - Surfside Beach Campground (MB 9351): the commercial operator now offers seasonal
  lots and day camping, and its Campspot listing has no sites.
- Shimek State Forest - White Oak Campground (IA 2930): Iowa's booking site types all of its sites 'Tent Only'.
- Minnesota Valley State Recreation Area (MN 5402): ReserveMN lists only its equestrian campground.
Each drop is logged in dropped.jsonl."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import trips  # noqa: E402
D = "2026-10-12"
CALL = f"AWH {D}: drop."
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
DROPS = {
    9351: "no nightly camping found: the commercial operator, Surfside Beach, now advertises 'Seasonal RV lots and day "
          "camping sites' with seasonal rates only ($2,500-3,000 a season), and its Campspot listing shows no sites "
          f"(surfsidebeach.ca and campspot.com/park/surfside-beach-rv-park-mb, read {D}). " + CALL,
    2930: "tent sites: Iowa's booking site types all 11 White Oak sites 'Tent Only' ('Looking For Category: Tent Site'; "
          f"one 'Site can accommodate a pop up camper'; 35-45 ft gravel pads), read {D} "
          "(ia_ne_site_details_2026-10-12.jsonl). " + CALL,
    5402: "horse camp only on the booking site: ReserveMN lists only Minnesota Valley's Equestrian Campground (place "
          f"129); the Lawrence Unit's 25 drive-in sites the note described are not on it (read {D}). " + CALL,
}
log = []
for i, why in DROPS.items():
    e = by.get(i)
    if e is None:
        print(i, "already dropped")
        continue
    assert not trips.campground_references(i), (i, "referenced by a trip")
    log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e.get("ownership"),
                "action": "dropped", "decided": D, "why": why})
gone = {x["id"] for x in log}
rows[:] = [r for r in rows if r["id"] not in gone]
for x in log:
    print(x["action"], x["id"], x["state"], x["name"])
if "--apply" in sys.argv:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    with open(os.path.join(HERE, "dropped.jsonl"), "a", encoding="utf-8") as fh:
        for x in log:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("written")
else:
    print("(dry run)")
