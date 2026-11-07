"""Write the extra-vehicle pass inputs: python3 -I audit/extra_vehicle/chunk.py OUTDIR SIZE

Entries whose note or fees.note mention a per-vehicle charge, an extra-vehicle charge or a
vehicles-per-site cap, and whose fees hold no extra_vehicle yet (AWH 2026-11-07)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "note_prices"))
import lib
import campground_schema as cs
VEH = re.compile(r"(extra|additional|second|each additional|2nd|third|3rd) (vehicles?|cars?|autos?)"
                 r"|\bper (vehicle|car)\b|/\s?(vehicle|car)\b|\ba (vehicle|car)\b(?=[^.]{0,30}(night|day))"
                 r"|(\d+|one|two|three|four) (vehicles?|cars?) (per site|per campsite|max|maximum|allowed|limit|included)"
                 r"|max(imum)?( of)? (\d+|one|two|three|four) (vehicles?|cars?)", re.I)
out, size = sys.argv[1], int(sys.argv[2]); os.makedirs(out, exist_ok=True)
cg, reg = lib.load(); items = []
for e in cg:
    if e.get("kind") != "campground": continue
    r = cs.resolve(e, reg).get("fees", {}); f = r.get("values", {})
    if "extra_vehicle" in f: continue
    n = e.get("note") or ""; fn = str((e.get("fees") or {}).get("note", ""))
    if not (VEH.search(n) or VEH.search(fn)): continue
    p = (e.get("provenance") or {}).get("fees") or {}
    items.append({"id": e["id"], "name": e["name"], "state": e["state"], "ownership": e["ownership"],
                  "note": n, "fees_note": fn or None,
                  "fees": {k: v for k, v in f.items() if k not in ("note",)},
                  "inherited_from_agency": sorted(r.get("inherited", [])),
                  "fee_source": (str(p.get("source", "")) + " " + str(p.get("checked", ""))).strip()[:200]})
for i in range(0, len(items), size):
    json.dump(items[i:i+size], open(os.path.join(out, f"{i//size+1:03d}.json"), "w"), ensure_ascii=False, indent=1)
print(len(items), "items,", (len(items) + size - 1) // size, "chunks")
