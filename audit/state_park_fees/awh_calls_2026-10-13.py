"""AWH's calls of 2026-10-13: python3 -I awh_calls_2026-10-13.py [--apply]

"Drop Riverside (Chilliwack). Give me the URL for Darke Lake. Drop the ones that are too short."

- Riverside (Chilliwack) Recreation Site (BC 8403, Recreation Sites and Trails BC): its operator now books it as a group
  site, by phone only.
- The four too short for a 23-ft rig: Smelt Bay (BC 8449; camping.bcparks.ca allows only a trailer up to 18 ft or a
  van/camper), and on ReserveCalifornia Tamarisk Grove (CA 11608, longest site 21 ft), Emerald Bay's Eagle Point (CA 11635,
  18 ft) and Malakoff Diggins' Chute Hill (CA 11662, 19 ft).
All five logged in dropped.jsonl. Darke Lake (BC 8461) stays unpriced while AWH reads its page
(https://bcparks.ca/darke-lake-park/, the Camping section: 'best suited to truck and camper units as opposed to trailers
or motor homes')."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import trips  # noqa: E402
D = "2026-10-13"
READ = "2026-10-12"
RIVERSIDE = f"AWH {D}: 'Drop Riverside (Chilliwack).'"
SHORT = f"AWH {D}: 'Drop the ones that are too short.'"
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
DROPS = {
    8403: "group site only: its operator, Camp Chilliwack Valley, lists Riverside as a group site 'available for booking "
          f"at the RIVERSIDE Recreation Site by phone call only' (thurston.campchilliwackvalley.ca, read {READ}), and "
          "Recreation Sites and Trails BC's record REC0013 says Closed ('Seasonal Closure, Opening Spring 2027'), its $17 "
          f"overnight fee dated 2023-2025 (bc_rec_sites_2026-10-12.json). {RIVERSIDE}",
    8449: "too short: camping.bcparks.ca lets the Smelt Bay sites take only '1 Tent', '2 Tents', '3 Tents', 'Trailer up "
          f"to 18ft' and 'Van/Camper' (bc_booking_fees_2026-10-12.json), read {READ}. {SHORT}",
    11608: "too short: ReserveCalifornia lists no site at Tamarisk Grove for a vehicle over 21 ft (its 14 campsites and 9 "
           f"cabins; ca_units_2026-10-12.jsonl), read {READ}. {SHORT}",
    11635: "too short: ReserveCalifornia lists no site at Upper or Lower Eagle Point for a vehicle over 18 ft, premium "
           f"sites included (ca_units_2026-10-12.jsonl), read {READ}. {SHORT}",
    11662: "too short: ReserveCalifornia's 26 Chute Hill campsites (typed 'Tent Campsite') take a vehicle of 19 ft at most "
           f"(ca_units_2026-10-12.jsonl), read {READ}. {SHORT}",
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
