"""Land cleaned-up campground notes: python3 -I clean_notes.py NOTES.json [--apply]

AWH 2026-10-13: a note that is already being read or edited for some task is rewritten as clean, current prose, and
may drop what a data field already holds (docs/campground-schema.md §6; .claude/memory/feedback_clean_up_notes.md).
NOTES is a list of
    {"id": N, "was": <the note being replaced, verbatim>, "note": <the cleaned note>,
     "set": {group: {...}}, "provenance": {group: {...}}}             <- "set"/"provenance" optional
- "was" must equal the entry's note as it stands, so a note that changed after it was read is refused, not clobbered.
- Text signed --AWH is AWH's own: a cleaned note that drops an "--AWH" marker is refused UNLESS the item lists
  what it drops in "awh_dropped" ([{"old": ..., "why": ...}]). AWH 2026-10-21: AWH's text may be trimmed when
  it repeats a data field or is now wrong (pricing and ratings included); "why" names the field or the source.
- Every group whose provenance source is exactly "note prose" is re-tagged "note prose (cleaned out of the note
  <today>)". The cleaned note no longer repeats what the fields hold, so the field is now the record, and
  apply_absent.py --rescan, which re-reads only an exact "note prose", can't strip it later.
- "set" writes a field fix found while reading (cs.apply_update merge), with its own provenance from "provenance".
The new note re-queues the entry for the note scan (its hash changed): afterwards run extract_fields.py --dump and
apply_absent.py on the queued entries. --apply writes campgrounds.json (indent 2, ensure_ascii False)."""
import datetime, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

TODAY = datetime.date.today().isoformat()
TAG = f"note prose (cleaned out of the note {TODAY})"
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
done = 0
for item in json.load(open(sys.argv[1], encoding="utf-8")):
    e = by[item["id"]]
    if (e.get("note") or "") != item["was"]:
        print("refused (note changed since it was read):", e["id"], e["name"]); continue
    if item["was"].count("--AWH") > item["note"].count("--AWH") and not item.get("awh_dropped"):
        print("refused (an --AWH marker would be lost):", e["id"], e["name"]); continue
    prov = dict(e.get(cs.PROVENANCE) or {})
    retagged = []
    for group, p in list(prov.items()):
        if isinstance(p, dict) and p.get("source") == "note prose":
            prov[group] = dict(p, source=TAG)
            retagged.append(group)
    for group, p in (item.get("provenance") or {}).items():
        prov[group] = p
    update = dict(item.get("set") or {})
    update[cs.PROVENANCE] = prov
    cs.apply_update(e, update)
    e["note"] = item["note"]
    cs.validate_row(e, label=e["name"])
    done += 1
    print(e["id"], e["name"], "| re-tagged:", ",".join(retagged) or "-", "| set:", ",".join(item.get("set") or {}) or "-")
print(done, "notes", "(written)" if "--apply" in sys.argv else "(dry run)")
if "--apply" in sys.argv and done:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
