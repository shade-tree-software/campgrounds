"""Fill fees.extra_person from note prose (AWH 2026-11-07, doc §4.2).

Every value was read by hand from the entry's own fees.note / note (the
decisions live in decisions/*.py as {id: values}); this script only validates
and writes. Never touches a note, never overwrites an existing extra_person,
and stamps fees provenance only where the group has none.

    python3 audit/extra_person/apply.py            # dry run
    python3 audit/extra_person/apply.py --apply
"""
import json, sys, glob, runpy, os, copy
sys.path.insert(0, os.getcwd())
import campground_schema as cs

HERE = os.path.dirname(os.path.abspath(__file__))
D, TEXT_RULES, REGISTRY, SKIP = {}, [], {}, set()
for f in sorted(glob.glob(os.path.join(HERE, "decisions", "*.py"))):
    g = runpy.run_path(f)
    for k in g.get("D", {}):
        assert k not in D, f"{k} decided twice"
    D.update(g.get("D", {})); TEXT_RULES += g.get("TEXT_RULES", [])
    REGISTRY.update(g.get("REGISTRY", {})); SKIP |= g.get("SKIP_STATES", set())

def norm(v):
    v = dict(v)
    if "amount" in v: v.setdefault("per", "night")
    order = ["included", "included_children", "amount", "per", "child", "child_max_age", "max_people"]
    staged = {}
    cs.apply_update(staged, {"fees": {"extra_person": v}})       # raises on a bad value
    return {k: v[k] for k in order if k in v}

PROV = {"checked": "2026-11-07", "method": "derived", "source": "note prose"}
apply = "--apply" in sys.argv
raw = open("campgrounds.json", encoding="utf-8").read(); cg = json.loads(raw)
assert json.dumps(cg, ensure_ascii=False, indent=2) + "\n" == raw
wrote = prov = 0; skipped = []
for e in cg:
    want = D.get(e["id"])
    if want is None:
        t = (e.get("fees") or {}).get("note") or ""
        for s, v in TEXT_RULES:
            if s in t: want = v
    if want is None: continue
    assert (e.get("state"), e.get("ownership")) not in SKIP, e["id"]
    fees = e.setdefault("fees", {})
    if "extra_person" in fees: skipped.append((e["id"], "has one")); continue
    p = (e.get("provenance") or {}).get("fees") or {}
    fees["extra_person"] = norm(want); wrote += 1
    if not p:
        e.setdefault("provenance", {})["fees"] = dict(PROV); prov += 1
missing = [i for i in D if i not in {e["id"] for e in cg}]
print(f"entries: {wrote} written, {prov} provenance stamped, skipped {skipped}, missing ids {missing}")

rraw = open("campground_policies.json", encoding="utf-8").read(); reg = json.loads(rraw)
for ind in (2, 1, None):
    if json.dumps(reg, ensure_ascii=False, indent=ind) + "\n" == rraw: break
else: sys.exit("registry does not round-trip")
for key, v in REGISTRY.items():
    reg[key].setdefault("fees", {})["extra_person"] = norm(v)
    cs.validate_row(reg[key], key)
print(f"registry rows: {list(REGISTRY)}")
if apply:
    open("campgrounds.json", "w", encoding="utf-8").write(json.dumps(cg, ensure_ascii=False, indent=2) + "\n")
    open("campground_policies.json", "w", encoding="utf-8").write(json.dumps(reg, ensure_ascii=False, indent=ind) + "\n")
    print("written")
