"""Replace entries' researched fees with a re-check: python3 -I replace_fees.py FINDINGS.json [--apply]

FINDINGS is apply.py's format ({"id", "fees", "source"}). apply.py never overwrites fees that are not note-derived; this
does, for a re-check that supersedes an earlier research figure (2026-10-12: the 25 NY State Parks campgrounds priced
2026-10-09 from each park's posted range, which spanned site types and weekends). The old fees and their provenance are
written back into FINDINGS under "replaced" so the record keeps them. A manual/reported group is still refused."""
import datetime, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
TODAY = datetime.date.today().isoformat()
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
findings = json.load(open(sys.argv[1], encoding="utf-8"))
n = 0
for f in findings:
    e = by[f["id"]]
    prov = dict(e.get(cs.PROVENANCE) or {})
    old = prov.get("fees") or {}
    if old.get("method") in ("manual", "reported"):
        print("refused (manual/reported):", e["id"], e["name"]); continue
    f.setdefault("replaced", {"fees": e.get("fees"), "provenance": old})
    cs.apply_update({}, {"fees": f["fees"]})
    prov["fees"] = {"source": f["source"], "checked": TODAY}
    e.pop("fees", None)
    cs.apply_update(e, {"fees": f["fees"], cs.PROVENANCE: prov})
    cs.validate_row(e, label=e["name"])
    n += 1
print(n, "replaced", "(written)" if "--apply" in sys.argv else "(dry run)")
if "--apply" in sys.argv and n:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    json.dump(findings, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
