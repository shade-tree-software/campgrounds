#!/usr/bin/env python3
"""Apply decisions.json to campgrounds.json (the 2026-10-12 US private re-check).

    python3 -I audit/us_private_recheck/apply.py [--apply]

The Canada re-check's apply (audit/canada_recheck/apply.py) for the 125 US parks: each decided
entry gets `; re-check 2026-10-12: <stamp>` appended to its inclusion_evidence, which is the
progress record (an entry already carrying it is skipped, so a rerun is safe). Optional edits:
`note_line` (appended after two spaces), `set` + `set_prov` (schema groups merged through
campground_schema.apply_update, so a bad value raises before anything is written; a `fees`
group replaces the old one), `website` (null clears a dead link; the old URL stays in the
record) and `phone`. `drop_proposed` and `flag` change nothing: those wait for AWH. A `drop`
(AWH's yes, with `decided` and `why`) deletes the entry and logs it to dropped.jsonl; a rerun
finds it gone and does nothing. Dry run unless --apply. Prints the ids whose note changed,
for the note-scan re-stamp.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

MARK = "re-check 2026-10-12:"
dec = json.load(open(os.path.join(HERE, "decisions.json"), encoding="utf-8"))["entries"]
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
note_ids, n, dropped = [], 0, []
for k, d in sorted(dec.items(), key=lambda kv: int(kv[0])):
    e = by.get(int(k))
    if d["verdict"] == "drop":
        if e is None:
            print(k, "already dropped")
            continue
        rows.remove(e)
        dropped.append({"id": e["id"], "name": e["name"], "state": e["state"],
                        "ownership": e.get("ownership"), "action": "removed",
                        "why": d["why"], "decided": d["decided"]})
        print(k, "drop", e["state"], e["name"])
        continue
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
    if d.get("set"):
        prov = dict(e.get(cs.PROVENANCE) or {})
        prov.update(d["set_prov"])
        if "fees" in d["set"]:
            e.pop("fees", None)
        cs.apply_update(e, {**d["set"], cs.PROVENANCE: prov})
    if d.get("phone"):
        e["phone"] = d["phone"]
    if "website" in d:
        if d["website"]:
            e["website"] = d["website"]
        else:
            e.pop("website", None)
    cs.validate_row(e, label=e["name"])
    print(k, d["verdict"], e["name"][:40], "|", d["stamp"][:90])
print(n, "entries stamped;", len(dropped), "dropped; note ids:", ",".join(map(str, note_ids)) or "-")
if "--apply" in sys.argv:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    with open(os.path.join(HERE, "dropped.jsonl"), "a", encoding="utf-8") as fh:
        for rec in dropped:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("written")
