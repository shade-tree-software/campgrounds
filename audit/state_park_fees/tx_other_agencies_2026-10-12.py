"""Texas entries run by state agencies other than Texas Parks and Wildlife: python3 -I tx_other_agencies_2026-10-12.py [--apply]

The LCRA parks (and the two Lake Fayette parks Vista Recreation runs for it), the Historical Commission's Fort Griffin
and Mission Dolores, and the river authorities' parks (Lavaca-Navidad, Trinity, Guadalupe-Blanco, Brazos, West Central
Texas MWD) are `ownership: state`, so they inherited the state:TX row - TPWD's booking site, 150-day window, weekend
minimum and per-person park entry fee - none of which is theirs. They get policy_ref none (the rule for a campground
outside its state's park system); their own fees are on each entry (tx_other_build.py)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
cg_path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(cg_path, encoding="utf-8"))
n = 0
for e in rows:
    if e.get("state") == "TX" and e.get("ownership") == "state" and "tpwd.texas.gov" not in (e.get("website") or "") \
            and not e.get(cs.POLICY_REF):
        e[cs.POLICY_REF] = cs.POLICY_REF_NONE
        cs.validate_row(e, label=e["name"])
        n += 1
        print(e["id"], e["name"])
print(n, "entries -> policy_ref none")
if "--apply" in sys.argv:
    tmp = cg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, cg_path)
    print("written")
else:
    print("(dry run)")
