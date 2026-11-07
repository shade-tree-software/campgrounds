"""Write the read-through inputs: python3 -I audit/note_prices/chunk.py OUTDIR SIZE"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
out, size = sys.argv[1], int(sys.argv[2]); os.makedirs(out, exist_ok=True)
cg, reg = lib.load(); items = []
for e in cg:
    if not lib.in_scope(e, reg): continue
    f = lib.fees(e, reg); p = (e.get("provenance") or {}).get("fees") or {}
    items.append({"id": e["id"], "name": e["name"], "note": e["note"],
                  "fees": {k: f[k] for k in ("nightly_low", "nightly_high", "currency", "checked", "extra_person") if k in f},
                  "fee_source": (str(p.get("source", "")) + " " + str(p.get("checked", ""))).strip()[:160]})
for i in range(0, len(items), size):
    json.dump(items[i:i+size], open(os.path.join(out, f"{i//size+1:03d}.json"), "w"), ensure_ascii=False, indent=1)
print(len(items), "items,", (len(items) + size - 1) // size, "chunks")
