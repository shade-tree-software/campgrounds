"""AWH's call of 2026-10-12 (late night): python3 -I awh_calls_2026-10-12e.py [--apply]

"Drop Ben Avery."

- Ben Avery Shooting Facility Campgrounds (AZ 11547, Arizona Game and Fish): AZGFD's camping pages say the campgrounds
  are available exclusively for competition and recreational shooters. Logged in dropped.jsonl."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import trips  # noqa: E402
D = "2026-10-12"
CALL = f"AWH {D}: 'Drop Ben Avery.'"
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
DROPS = {
    11547: "shooters only: AZGFD's camping pages say the campgrounds are 'available exclusively for competition and "
           "recreational shooters', and the 2026 booking dates opened first to campers in competitive matches, events or "
           "registered shoots, then to other shooting sports campers (azgfd.com, read through a web search " + D +
           "; the pages refuse a plain fetch). " + CALL,
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
