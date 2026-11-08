"""Idaho state-park entries carried `entrance` $7/day (some $14 non-resident) from the sweep.
IDPR: "Use fees allow for one vehicle per reservation for the length of stay" — a lone
motorhome pays no entry; the $7 is what a SECOND vehicle pays, which the state:ID row now
holds as extra_vehicle. So the entry entrance is removed and the row's values inherit
(fee-registry b01, 2026-11-07)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "note_prices"))
import lib
cg, reg = lib.load()
n = 0
for e in cg:
    f = e.get("fees") or {}
    if (e.get("ownership") == "state" and e.get("state") == "ID" and not e.get("policy_ref")
            and (f.get("entrance") or {}).get("resident") == 7 and f["entrance"].get("per") == "vehicle_day"):
        del f["entrance"]
        prov = e.setdefault("provenance", {}).setdefault("fees", {})
        prov["source"] = (prov.get("source", "") + " | " if prov.get("source") else "") + \
            "2026-11-07: entrance removed — IDPR 'Use fees allow for one vehicle per reservation for the length of stay' (parksandrecreation.idaho.gov); the $7 day fee is the second vehicle's, on the state:ID row"
        n += 1
if "--apply" in sys.argv:
    lib.dump(cg)
print(n, "entries")
