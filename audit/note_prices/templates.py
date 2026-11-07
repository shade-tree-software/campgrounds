"""Step 1: the templated free-camping sentences, on entries whose resolved rate is $0 (the popup
already says "Free"). Exact phrases only; everything else goes to the read-through (step 2).
    python3 -I audit/note_prices/templates.py [--apply]"""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
SUBS = [("No hookups, no fee, no reservations;", "No hookups, no reservations;"),
        ("Free primitive camping at MDC-designated", "Primitive camping at MDC-designated"),
        ("First-come, first-served, no fee.", "First-come, first-served."),
        ("Free, first-come, first-served", "First-come, first-served"),
        ("First-come, first-served, free.", "First-come, first-served."),
        ("First-come, first-served (free).", "First-come, first-served."),
        ("Free, first-come first-served", "First-come first-served")]
cg, reg = lib.load(); items = []
for e in cg:
    f = lib.fees(e, reg); n = e.get("note") or ""
    if f.get("nightly_low") != 0 or f.get("nightly_high") not in (None, 0): continue
    new = n
    for a, b in SUBS: new = new.replace(a, b)
    if new != n: items.append({"id": e["id"], "was": n, "note": new})
done, refused = lib.land(cg, items, datetime.date.today().isoformat(), "--apply" in sys.argv)
json.dump(items, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "000_templates.json"), "w"), ensure_ascii=False, indent=1)
print(len(done), "cleaned", refused, "(written)" if "--apply" in sys.argv else "(dry run)")
