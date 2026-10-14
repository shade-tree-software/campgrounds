"""clest3.py OUT.jsonl ID DATE (batch 28, 2026-10-14; the by_amenities lines of b28_camplife_stays.jsonl are its
output): like clest2.py, but one site of each (type, amenity set) rather than of each type, so
a park whose types mix serviced and unserviced sites (batch 28, Lobies: Back-in holds full-service, water-and-hydro
and unserviced sites) gets a quote per tier. Site amenities come from camplife_tier_2026-10-14.jsonl; the quotes are
asked directly, with no availability call. One JSON line per park in cl2n.py's shape; each quote's type names the
amenities."""
import datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "private_gap_browser"))
import camplife_api as C
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "camplife_tier_2026-10-14.jsonl")
out = open(sys.argv[1], "a", encoding="utf-8")
eid, d = int(sys.argv[2]), sys.argv[3]
r = next(json.loads(l) for l in open(DATA, encoding="utf-8") if json.loads(l)["id"] == eid)
cg = r["cg"]
names = (r.get("config") or {}).get("amenities") or {}
C.load(cg)
st, s = C.api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
sm = {k: [v.get('name'), v.get('typeName')] for k, v in ((s or {}).get('siteMap') or {}).items()}
rec = {"cg": cg, "name": ((s or {}).get("campground") or {}).get("name"), "read": datetime.date.today().isoformat(),
       "direct": True, "by_amenities": True, "quotes": []}
by = {}
for k, (name, typ) in sm.items():
    am = sorted({names.get(str(a), str(a)).strip() for a in ((r.get("sites") or {}).get(str(k)) or {}).get("amenityIds") or []})
    by.setdefault((typ, tuple(am)), []).append(k)
for (t, am), sids in sorted(by.items()):
    sid = sids[0]
    for n in (1, 2, 3):
        st, q = C.api('POST', '/api/invoice/estimate',
                      {'reservation': {'checkinDate': C.mdy(d), 'checkoutDate': C.mdy(C.nxt(d, n)), 'siteId': int(sid),
                                       'occupancy': {'numAdults': 2, 'numChildren': 0, 'numPets': 0, 'numVehicles': 0},
                                       'equipment': {}, 'addOns': [], 'vehicles': []}})
        inv = (q or {}).get('invoice') or {}
        rec["quotes"].append({"date": d, "nights": n, "site": sm[sid][0], "type": "%s (%s; %d sites)" % (t, ", ".join(am) or "no amenities", len(sids)),
                              "sub": inv.get('resSubTotal'), "total": inv.get('total'), "items": inv.get('items')})
out.write(json.dumps(rec) + "\n"); out.flush()
for q in rec["quotes"]:
    print(cg, q["date"], q["type"], q["site"], q["nights"], q["sub"], q["total"], json.dumps(q["items"])[:300])
