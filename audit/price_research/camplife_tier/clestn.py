"""clestn.py OUT.jsonl CG DATE NIGHTS SITE[,SITE...] (batch 28, 2026-10-14; Roth Park's 7-night and 1-night lines
and Entwistle's 2-night line in b28_camplife_stays.jsonl are its output): CampLife invoice estimates of NIGHTS nights
from DATE on the named sites, with the raw response kept (Roth Park books only in one-week blocks until February 1, so
its 1-3 night estimates came back empty). One JSON line per park, 'direct': true."""
import datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "private_gap_browser"))
import camplife_api as C
out = open(sys.argv[1], "a", encoding="utf-8")
cg, d, n, names = int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5].split(",")
C.load(cg)
st, s = C.api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
sm = {k: [v.get('name'), v.get('typeName')] for k, v in ((s or {}).get('siteMap') or {}).items()}
rec = {"cg": cg, "name": ((s or {}).get("campground") or {}).get("name"), "read": datetime.date.today().isoformat(),
       "direct": True, "quotes": []}
for sid, (name, typ) in sm.items():
    if name not in names:
        continue
    st, q = C.api('POST', '/api/invoice/estimate',
                  {'reservation': {'checkinDate': C.mdy(d), 'checkoutDate': C.mdy(C.nxt(d, n)), 'siteId': int(sid),
                                   'occupancy': {'numAdults': 2, 'numChildren': 0, 'numPets': 0, 'numVehicles': 0},
                                   'equipment': {}, 'addOns': [], 'vehicles': []}})
    inv = (q or {}).get('invoice') or {}
    rec["quotes"].append({"date": d, "nights": n, "site": name, "type": typ, "sub": inv.get('resSubTotal'),
                          "total": inv.get('total'), "items": inv.get('items'), "status": st,
                          "raw": None if inv else json.dumps(q)[:600]})
out.write(json.dumps(rec) + "\n"); out.flush()
for q in rec["quotes"]:
    print(cg, q["date"], q["nights"], q["type"], q["site"], q["sub"], q["total"], json.dumps(q["items"])[:200], q["status"], q["raw"])
