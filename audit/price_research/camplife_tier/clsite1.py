"""clsite1.py OUT.jsonl CG DATE (batch 28, 2026-10-14; b28_camplife_sites.jsonl is its output): a one-night
CampLife estimate on EVERY site sold online (Lobies' site types carry no amenities, so only per-site quotes show which
RV sites sell at the full-service, water-and-hydro or unserviced rate). One JSON line per park, 'each': true."""
import datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "private_gap_browser"))
import camplife_api as C
out = open(sys.argv[1], "a", encoding="utf-8")
cg, d = int(sys.argv[2]), sys.argv[3]
C.load(cg)
st, s = C.api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
sm = {k: [v.get('name'), v.get('typeName')] for k, v in ((s or {}).get('siteMap') or {}).items()}
rec = {"cg": cg, "name": ((s or {}).get("campground") or {}).get("name"), "read": datetime.date.today().isoformat(),
       "direct": True, "each": True, "quotes": []}
for sid, (name, typ) in sm.items():
    st, q = C.api('POST', '/api/invoice/estimate',
                  {'reservation': {'checkinDate': C.mdy(d), 'checkoutDate': C.mdy(C.nxt(d, 1)), 'siteId': int(sid),
                                   'occupancy': {'numAdults': 2, 'numChildren': 0, 'numPets': 0, 'numVehicles': 0},
                                   'equipment': {}, 'addOns': [], 'vehicles': []}})
    inv = (q or {}).get('invoice') or {}
    rec["quotes"].append({"date": d, "nights": 1, "site": name, "type": typ, "sub": inv.get('resSubTotal'), "total": inv.get('total')})
out.write(json.dumps(rec) + "\n"); out.flush()
agg = {}
for q in rec["quotes"]:
    agg.setdefault((q["type"], q["sub"]), []).append(q["site"])
for (t, sub), sites in sorted(agg.items(), key=lambda x: (x[0][0], str(x[0][1]))):
    print(cg, t, sub, len(sites), " ".join(sorted(sites, key=lambda x: (len(x), x))))
