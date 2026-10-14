"""clsdet.py OUT.jsonl CG [TYPE,TYPE...]: CampLife's own detail record (description, length, notices) for every site
sold online, or only for the named site types (batch 29, 2026-10-14: Josephine County sells some "Tent" sites that
'can accommodate a self-contained RV', which only the per-site descriptions say). One JSON line per park; b29_camplife_details.jsonl is its output."""
import datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "private_gap_browser"))
import camplife_api as C
out = open(sys.argv[1], "a", encoding="utf-8")
cg = int(sys.argv[2]); types = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
C.load(cg)
st, s = C.api('GET', '/api/reservation/session?campgroundIdOrAlias=%s' % cg)
sm = {k: [v.get('name'), v.get('typeName')] for k, v in ((s or {}).get('siteMap') or {}).items()}
rec = {"cg": cg, "name": ((s or {}).get("campground") or {}).get("name"), "read": datetime.date.today().isoformat(),
       "details": {}}
for sid, (name, typ) in sm.items():
    if types and typ not in types:
        continue
    st, info = C.api('GET', '/api/campground/%s/site/%s' % (cg, sid))
    info = info or {}
    rec["details"][sid] = {"name": name, "type": typ, "description": info.get("description"), "maxLength": info.get("maxLength"),
                           "messages": [m for m in (info.get("messages") or []) if m], "equipTypeIds": info.get("equipTypeIds"),
                           "amenityIds": info.get("amenityIds")}
out.write(json.dumps(rec) + "\n"); out.flush()
print(rec["name"], len(rec["details"]), "sites")
for sid, d in sorted(rec["details"].items(), key=lambda x: (x[1]["type"], str(x[1]["name"]))):
    print(f'  {d["type"]:14} {str(d["name"]):8} len {d["maxLength"]}: {(d["description"] or "").strip()[:160]}')
