#!/usr/bin/env python3
"""Apply decisions.json to campgrounds.json (the 2026-10-11 Canada private re-check).

    python3 -I audit/canada_recheck/apply.py [--apply]

Each decided entry gets `; re-check 2026-10-11: <stamp>` appended to its inclusion_evidence. That
stamp is the progress record: an entry already carrying it is skipped, so this is safe to rerun.
Optional per-entry edits ride along: `note_line` (appended after two spaces, like the MINIMUM STAY
lines), `set` + `set_prov` (a whole schema group and its provenance) and `website` (null clears it).
A `drop_proposed` or `flag` verdict changes nothing; those wait for AWH. Dry run unless --apply. Prints the
ids whose note changed, for the note_scan re-stamp (extract_fields.py --apply-file).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MARK = "re-check 2026-10-11:"

dec = json.load(open(os.path.join(HERE, "decisions.json"), encoding="utf-8"))["entries"]
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
note_ids, n = [], 0
for k, d in sorted(dec.items(), key=lambda kv: int(kv[0])):
    e = by.get(int(k))
    if e is None:
        print(k, "MISSING (dropped?)")
        continue
    if d["verdict"] in ("drop_proposed", "flag") or MARK in (e.get("inclusion_evidence") or ""):
        continue
    n += 1
    e["inclusion_evidence"] = ((e.get("inclusion_evidence") or "").rstrip("; ") + f"; {MARK} {d['stamp']}").lstrip("; ")
    if d.get("note_line") and d["note_line"] not in (e.get("note") or ""):
        e["note"] = ((e.get("note") or "").rstrip() + "  " + d["note_line"]).strip()
        note_ids.append(int(k))
    for group, val in (d.get("set") or {}).items():
        e[group] = val
        e.setdefault("provenance", {})[group] = d["set_prov"][group]
    if "website" in d:  # null clears a dead link; the old URL stays in decisions.json
        if d["website"]:
            e["website"] = d["website"]
        else:
            e.pop("website", None)
    print(k, d["verdict"], e["name"][:40], "|", d["stamp"][:90])
print(n, "entries stamped; note ids:", ",".join(map(str, note_ids)) or "-")
if "--apply" in sys.argv:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("written")
