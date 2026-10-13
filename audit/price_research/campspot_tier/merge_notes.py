"""Assemble clean_notes.py's input for one batch of the Campspot tier-only pass (2026-10-13).

    python3 -I merge_notes.py NEW_NOTES.json FIELDS.json [MORE_FIELDS.json ...] OUT.json

NEW_NOTES = {"<id>": "<cleaned note>" | null, ...} written by hand while reading each entry (null = the note stays as
it is, e.g. AWH's own); FIELDS = campspot_tier_build.py --fields (the empty groups the Campspot reads settle, and
note-scan values they contradict); MORE_FIELDS = sets written by hand while reading (a minimum, a booking channel),
merged over FIELDS group by group. OUT = [{id, was, note, set?, provenance?}] for audit/note_scan/clean_notes.py:
"was" is the entry's note as it stands, so a note edited since it was read is refused there."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
by = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
notes = {int(k): v for k, v in json.load(open(sys.argv[1], encoding="utf-8")).items()}
fields = {}
for path in sys.argv[2:-1]:
    for f in json.load(open(path, encoding="utf-8")):
        cur = fields.setdefault(f["id"], {"id": f["id"], "set": {}, "provenance": {}})
        for g, v in f["set"].items():
            cur["set"][g] = dict(cur["set"].get(g) or {}, **v) if isinstance(v, dict) else v
        cur["provenance"].update(f.get("provenance") or {})
out = []
for i in sorted(set(notes) | set(fields)):
    was = by[i].get("note") or ""
    item = {"id": i, "was": was, "note": notes.get(i) if notes.get(i) is not None else was}
    if i in fields:
        item["set"] = fields[i]["set"]
        item["provenance"] = fields[i]["provenance"]
    out.append(item)
json.dump(out, open(sys.argv[-1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "items;", sum(1 for x in out if x["note"] != x["was"]), "notes rewritten;",
      sum(1 for x in out if x.get("set")), "with field sets")
