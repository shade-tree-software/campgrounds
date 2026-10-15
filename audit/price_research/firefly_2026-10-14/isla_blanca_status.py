"""Isla Blanca 7248: 43 RV sites outside the gate are open while the ~577
inside stay closed (Firefly booking page, read 2026-10-14). A partial closure
is a note, not a status (campground-schema.md §4.5), so operating = open."""
import json
P = "campgrounds.json"
db = json.load(open(P, encoding="utf-8"))
e = next(x for x in db if x["id"] == 7248)
e["status"] = {"operating": "open"}
e.setdefault("provenance", {})["status"] = {
    "source": "https://app.fireflyreservations.com/reserve/property/CameronCountyIslaBlancaPark",
    "checked": "2026-10-14", "method": "manual",
    "quote": "43 RV sites remain open outside the park, south of Dirty Al's Restaurant"}
with open(P, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
    f.write("\n")
