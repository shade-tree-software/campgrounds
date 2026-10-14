"""clest2.py OUT.jsonl CG DATE (batch 27, 2026-10-14; the "direct" lines of b27_camplife_stays.jsonl are its output): one, two and three-night CampLife invoice estimates on one site of each type for DATE,
asked directly with no availability call (batch 27, 2026-10-14: West Two Rivers' calendar refused every date but its
estimate still quoted). One JSON line per park, in cl2n.py's shape, so clstays.py renders it; 'direct': true marks it."""
import datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "private_gap_browser"))
import camplife_api as C
out = open(sys.argv[1], "a", encoding="utf-8")
cg, d = int(sys.argv[2]), sys.argv[3]
C.load(cg)
st, s = C.api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
sm = {k: [v.get('name'), v.get('typeName')] for k, v in ((s or {}).get('siteMap') or {}).items()}
rec = {"cg": cg, "name": ((s or {}).get("campground") or {}).get("name"), "read": datetime.date.today().isoformat(),
       "direct": True, "quotes": []}
by = {}
for k, (name, typ) in sm.items():
    by.setdefault(typ, k)
for t, sid in by.items():
    for n in (1, 2, 3):
        st, q = C.api('POST', '/api/invoice/estimate',
                      {'reservation': {'checkinDate': C.mdy(d), 'checkoutDate': C.mdy(C.nxt(d, n)), 'siteId': int(sid),
                                       'occupancy': {'numAdults': 2, 'numChildren': 0, 'numPets': 0, 'numVehicles': 0},
                                       'equipment': {}, 'addOns': [], 'vehicles': []}})
        inv = (q or {}).get('invoice') or {}
        rec["quotes"].append({"date": d, "nights": n, "site": sm[sid][0], "type": t,
                              "sub": inv.get('resSubTotal'), "total": inv.get('total'), "items": inv.get('items')})
out.write(json.dumps(rec) + "\n"); out.flush()
for q in rec["quotes"]:
    print(cg, q["date"], q["type"], q["site"], q["nights"], q["sub"], q["total"], q["items"])
