"""cl2n.py OUT.jsonl CG [CG...] (batch 26, 2026-10-14; b26_camplife_stays.jsonl is its output): one, two and three-night CampLife quotes on one site of each type (2027-01-26 first,
else 2027-06-08), one JSON line per park (a stay charge hides inside resSubTotal; three lengths separate it from the
nightly rate)."""
import datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "private_gap_browser"))
import camplife_api as C
out = open(sys.argv[1], "a", encoding="utf-8")
for cg in map(int, sys.argv[2:]):
    C.load(cg)
    st, s = C.api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
    sm = {k: [v.get('name'), v.get('typeName')] for k, v in ((s or {}).get('siteMap') or {}).items()}
    rec = {"cg": cg, "name": ((s or {}).get("campground") or {}).get("name"), "read": datetime.date.today().isoformat(), "quotes": []}
    for d in ("2027-01-26", "2027-06-08"):
        st, j = C.api('POST', '/api/campground/%s/availability' % cg,
                      {'flexible': False, 'displayStartDate': '', 'checkinDate': C.mdy(d),
                       'checkoutDate': C.mdy(C.nxt(d, 3)), 'cgAmenity': [], 'numAdults': 2, 'amenities': []})
        ids = [x.get('id') for x in (j or {}).get('sites') or []]
        by = {}
        for i in ids:
            by.setdefault((sm.get(str(i)) or [None, None])[1], i)
        if not ids:
            continue
        for t, sid in by.items():
            for n in (1, 2, 3):
                st, q = C.api('POST', '/api/invoice/estimate',
                              {'reservation': {'checkinDate': C.mdy(d), 'checkoutDate': C.mdy(C.nxt(d, n)), 'siteId': sid,
                                               'occupancy': {'numAdults': 2, 'numChildren': 0, 'numPets': 0, 'numVehicles': 0},
                                               'equipment': {}, 'addOns': [], 'vehicles': []}})
                inv = (q or {}).get('invoice') or {}
                rec["quotes"].append({"date": d, "nights": n, "site": (sm.get(str(sid)) or [sid])[0], "type": t,
                                      "sub": inv.get('resSubTotal'), "total": inv.get('total'), "items": inv.get('items')})
        break
    out.write(json.dumps(rec) + "\n"); out.flush()
    for q in rec["quotes"]:
        print(cg, q["date"], q["type"], q["site"], q["nights"], q["sub"], q["total"], q["items"])
