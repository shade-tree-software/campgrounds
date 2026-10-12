"""AWH's calls of 2026-10-12 (evening): python3 -I awh_calls_2026-10-12b.py [--apply]

"Drop the ones that are definitely too short. Switch ownership of Upper Canada."

- Drop three campgrounds whose sites the booking sites cap below EKKO's 23 ft (docs/campground-curation.md):
  Algonquin's Tea Lake (ON 8205), Lac Dunbar (QC 12495) and Baie aux Rats Musqués (QC 12501). Lac Arthur (QC 12523),
  whose site pages list no equipment at all, is not definitely too short and stays.
- Upper Canada Campground (ON 8343) is a private family campground (the Wells family, Campspot), not the St. Lawrence
  Parks Commission's: ownership private, its own site and phone, the note and inclusion evidence corrected, and its 2026
  rates, seasonal share and July-August weekend minimum recorded.
Each drop is logged in dropped.jsonl. Prints the ids whose notes changed, for the note scan."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
import trips  # noqa: E402
D = "2026-10-12"
CALL = f"AWH {D}: drop the ones that are definitely too short."
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}

DROPS = {
    8205: "too short for a 23-ft rig: Ontario Parks' booking site lists all 39 Tea Lake campsites as taking a "
          "'Trailer or RV up to 18ft (5.5m)' at most (the other 3 a single tent), read 2026-10-12. " + CALL,
    12495: "too short for a 23-ft rig: SEPAQ's Lac Dunbar site pages accept a 'Camping van', a 'Tent trailer under 6 "
           "meters (20 feet)' or a 'Trailer under 6 meters (20 feet)' at most (6 sites read 2026-10-12). " + CALL,
    12501: "too short for a 23-ft rig: SEPAQ's Baie aux Rats Musqués site pages accept a 'Camping van' or a 'Tent "
           "trailer under 4.5 meters (15 feet)' at most, and half list tents only (8 sites read 2026-10-12). " + CALL,
}
log, notes = [], []
for i, why in DROPS.items():
    e = by.get(i)
    if e is None:
        print(i, "already dropped")
        continue
    assert not trips.campground_references(i), (i, "referenced by a trip")
    log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e.get("ownership"),
                "action": "dropped", "decided": D, "why": why})

u = by[8343]
if u.get("ownership") != "private":
    u["ownership"] = "private"
    u["website"] = "http://uppercanadacampground.com/\nhttps://www.campspot.com/park/upper-canada-campground"
    u["phone"] = "613-543-2201"
    u["note"] = (
        "Private family campground (the Wells family) at 13390 County Road 41, Morrisburg, three minutes from Upper "
        "Canada Village: 250 sites with fire pit and picnic table, 15/30/50-amp and water hookups, pull-throughs, RVs to "
        "60 ft; two pools, a beach on a man-made pond, camp store, rec hall, laundry, dump station. 2026 rates for two "
        "people before HST: 15-amp C$48, 30-amp C$55, 50-amp C$65 a night. Open ~May-Sept, reservable online through "
        "Campspot. Corrected 2026-10-12: privately run, not a St. Lawrence Parks Commission campground as this note "
        "said. --Claude  SEASONAL SHARE: about 40 of its 250 sites take overnight campers and the rest are seasonal "
        "(ontariocamping.ca listing; Campspot books 41 RV sites), so book ahead (2026-10-12). --Claude  MINIMUM STAY: "
        "2 nights on July and August weekends, 3 on holiday weekends (uppercanadacampground.com rates page, "
        "2026-10-12). --Claude")
    u["inclusion_evidence"] = (
        "Operator site uppercanadacampground.com (the Wells family; facilities page: 'a family resort offering 250 "
        "campsites', 15/30/50-amp hookups; 2026 rates page) + Campspot listing (41 RV sites, 15- or 30-amp, water, "
        "pull-throughs; reviews July-September 2026), read 2026-10-12: a private drive-in RV campground at 13390 County "
        "Road 41, Morrisburg -> real RV campground. Corrected 2026-10-12: earlier evidence credited the St. Lawrence "
        "Parks Commission, which does not run it. Mostly seasonal (about 40 of 250 sites overnight, ontariocamping.ca); "
        "AWH 2026-10-12 kept it as private.")
    cs.apply_update(u, {
        "fees": {"nightly_low": 48, "nightly_high": 65, "currency": "CAD",
                 "note": "2026 rates for two people, before 13% HST: 15-amp sites C$48, 30-amp C$55, 50-amp C$65 a "
                         "night (the C$45 unserviced sites are Campspot's tent sites); extra adults C$5, children "
                         "C$2.50; weekly stays 5% off, monthly 10% off."},
        "booking": {"reservable": True, "platform": "campspot",
                    "url": "https://www.campspot.com/book/uppercanadacampground",
                    "min_stay": [{"nights": 2, "applies": "weekend", "season": "July and August"},
                                 {"nights": 3, "applies": "holiday"}]},
    })
    prov = dict(u.get(cs.PROVENANCE) or {})
    src = ("http://uppercanadacampground.com/26-2/ (2026 rates; 'July and August reservations are two nights minimum "
           "on weekends. Holiday weekends are a 3 night minimum'), read 2026-10-12; Campspot's site types agree "
           "(15 Amp RV Site from $48, 30 Amp RV Site from $55)")
    prov["fees"] = {"source": src, "checked": D}
    prov["booking"] = {"source": src, "checked": D}
    u[cs.PROVENANCE] = prov
    cs.validate_row(u, label=u["name"])
    notes.append(8343)
    print("8343 ->", u["ownership"], json.dumps(u["fees"], ensure_ascii=False))
    print("     booking", json.dumps(u["booking"], ensure_ascii=False))

gone = {x["id"] for x in log}
rows[:] = [r for r in rows if r["id"] not in gone]
for x in log:
    print(x["action"], x["id"], x["state"], x["name"])
print("note scan ids:", ",".join(map(str, notes)))
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
