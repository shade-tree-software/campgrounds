"""Corrections the state-park price pass turned up: python3 -I corrections.py FILE [--apply]

FILE is a list of {"id", "why", "hookups": {...} + "hookups_source", "status": {...} + "status_source",
"note_line"}: `hookups` / `status` replace that group (values through campground_schema.apply_update,
provenance = its source, checked today); `note_line` is appended to the note with two spaces (a rerun finds it there and skips the
entry). Prints the ids whose notes changed, for the session note scan. Dry run unless --apply."""
import datetime, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
TODAY = datetime.date.today().isoformat()
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
changed = []
for c in json.load(open(sys.argv[1], encoding="utf-8")):
    e = by[c["id"]]
    if c.get("note_line") and c["note_line"] in (e.get("note") or ""):
        continue
    for g in ("hookups", "status"):
        if c.get(g):
            prov = dict(e.get(cs.PROVENANCE) or {})
            prov[g] = {"source": c[g + "_source"], "checked": TODAY}
            e.pop(g, None)
            cs.apply_update(e, {g: c[g], cs.PROVENANCE: prov})
    if c.get("note_line"):
        e["note"] = ((e.get("note") or "").rstrip() + "  " + c["note_line"]).strip()
    cs.validate_row(e, label=e["name"])
    changed.append(e["id"])
    print(e["id"], e["name"], "|", c["why"][:100])
print(len(changed), "corrected", "(written)" if "--apply" in sys.argv else "(dry run)", "- note scan ids:",
      ",".join(map(str, changed)))
if "--apply" in sys.argv and changed:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
