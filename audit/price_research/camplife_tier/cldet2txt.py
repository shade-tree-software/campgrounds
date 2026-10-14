"""cldet2txt.py DETAILS.jsonl CG: render clsdet.py's site records for one park as bundle text, under the park's
CampLife booking-page header, with amenity and equipment names from the tier file (batch 29, 2026-10-14)."""
import json, os, sys
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "camplife_tier_2026-10-14.jsonl")
cg = int(sys.argv[2])
cfg = {}
for l in open(T, encoding="utf-8"):
    r = json.loads(l)
    if r.get("cg") == cg:
        cfg = r.get("config") or {}
am, eq = cfg.get("amenities") or {}, cfg.get("equip") or {}
recs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
r = [x for x in recs if x["cg"] == cg][-1]
print(f"##### https://www.camplife.com/{cg}/reservation/step1")
print(f"CampLife site records read {r['read']}: {r['name']}, {len(r['details'])} sites")
for sid, d in sorted(r["details"].items(), key=lambda x: (x[1]["type"] or "", str(x[1]["name"]))):
    a = ", ".join(am.get(str(x), str(x)) for x in d.get("amenityIds") or [])
    e = ", ".join(eq.get(str(x), str(x)) for x in d.get("equipTypeIds") or [])
    m = " | ".join(" ".join(x.split()) for x in d.get("messages") or [])
    print(f"site {d['name']} ({d['type']}): {' '.join((d['description'] or '').split())} | longest rig {d['maxLength']} ft | amenities: {a} | equipment: {e}" + (f" | {m}" if m else ""))
