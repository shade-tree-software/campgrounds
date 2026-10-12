"""Record surcharges an entry was checked for: python3 -I set_surcharges.py FILE [--apply]

FILE is a list of {"id", "surcharges": {...}, "why", "source"}. Written into the entry's own `fees.surcharges` (which
replaces the registry row's list whole), only where the entry already has its own researched fees and no surcharges of
its own; `provenance.fees.source` gains the reason. The case it exists for (2026-10-12): NY DEC campgrounds have a flat
nightly fee, but with no surcharges of their own they showed NY State Parks' weekend +$4 (and its electric, waterfront and
oceanfront add-ons) as typical - a $0 weekend surcharge is true and stops that; the popup prints no chip for $0.
Dry run unless --apply."""
import datetime, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
n = 0
for c in json.load(open(sys.argv[1], encoding="utf-8")):
    e = by[c["id"]]
    f = e.get("fees") or {}
    if "nightly_low" not in f or f.get("surcharges"):
        print("skip", e["id"], e["name"], "(no own fees, or own surcharges already)")
        continue
    cs.apply_update(e, {"fees": {"surcharges": c["surcharges"]}})
    prov = ((e.get(cs.PROVENANCE) or {}).get("fees") or {})
    if prov.get("source") and c["source"] not in prov["source"]:
        prov["source"] = prov["source"] + " + " + c["source"]
    cs.validate_row(e, label=e["name"])
    n += 1
    print(e["id"], e["name"], c["surcharges"])
print(n, "entries", "written" if "--apply" in sys.argv else "(dry run)")
if "--apply" in sys.argv and n:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
