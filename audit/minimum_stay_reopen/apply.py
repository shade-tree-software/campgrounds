#!/usr/bin/env python3
"""Re-open campgrounds that the old standing-minimum rule removed or skipped (2026-10-11).

    python3 audit/minimum_stay_reopen/apply.py [--apply]

AWH 2026-10-10: a standing 2-night minimum no longer disqualifies a campground if it is
clearly marked. From 2026-10-01 to 2026-10-10 it did, and this undoes that rule's removals
and skips. decisions.json holds one verdict per candidate:

  restore   the entry's last record (removed_records.json, taken from git) comes back under
            a NEW id - ids are never reused - with the edits below;
  add       a park skipped under the old rule; `record` is the whole new entry;
  mark      the campground is already in the database under `id` (a later sweep re-added
            it); only the edits below are applied, so its minimum gets marked;
  minimum   an entry that was never removed but whose note names a minimum the data didn't
            carry (the 2026-10-12 follow-up); only the edits below, and `note_line` is how a
            rerun knows it is done;
  drop      AWH removed it (2026-10-12): the entry `id` is deleted and logged to dropped.jsonl;
            a rerun finds it gone and does nothing;
  skip/ask  nothing is written; `why` says what else it failed, or what AWH has to decide.

Edits on restore/add: `note_replace` ([old, new] pairs, each old text must be present),
`note_line` (appended after two spaces, like the other MINIMUM STAY lines), `booking`
(merged into the group; `min_stay` + `note`) and `fees`, each group with its `source`.
Values go through campground_schema.apply_update, so a bad one raises before anything is
written. Progress lives in the data: a written entry's inclusion_evidence carries MARK, and
a rerun skips any candidate already present (the stamp carries the decision's `decided`
date, 2026-10-11 when absent). Dry run unless --apply. Prints the new ids,
whose notes then need the session note scan (extract_fields.py --dump / --apply-file).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

MARK = "re-opened"
CG = os.path.join(ROOT, "campgrounds.json")
DROPPED = os.path.join(HERE, "dropped.jsonl")
FAMILY = os.path.join(ROOT, "trip_data", "family.json")
FIELD_ORDER = ["id", "kind", "name", "location", "elevation_meters", "state", "ownership",
               "waterfront", "waterfront_evidence", "inclusion_evidence", "website", "phone",
               "note", "rating", "status"]


def load(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        return []


def stamp(d):
    return f"{MARK} {d.get('decided', '2026-10-11')}"


def present(rows, d):
    """The entry this decision already wrote, if any."""
    for r in rows:
        if d["verdict"] == "minimum":
            if r["id"] == d["id"] and d["note_line"] in (r.get("note") or ""):
                return r
            continue
        ev = r.get("inclusion_evidence") or ""
        if MARK not in ev:
            continue
        if d["verdict"] == "restore" and f"was id {d['old_id']}," in ev:
            return r
        if d["verdict"] == "add" and (r["name"], r["state"]) == (d["record"]["name"], d["record"]["state"]):
            return r
        if d["verdict"] == "mark" and r["id"] == d["id"]:
            return r
    return None


def edit(e, d):
    note = e.get("note") or ""
    for old, new in d.get("note_replace") or []:
        if old not in note:
            raise SystemExit(f"{e['name']}: note text to replace not found: {old!r}")
        note = note.replace(old, new)
    if d.get("note_line") and d["note_line"] not in note:
        note = (note.rstrip() + "  " + d["note_line"]).strip()
    e["note"] = note
    prov = dict(e.get(cs.PROVENANCE) or {})
    update = {}
    if d.get("booking"):
        update["booking"] = d["booking"]
        prov["booking"] = {"source": d["booking_source"], "checked": d.get("checked", "2026-10-11")}
    if d.get("fees"):
        e.pop("fees", None)            # a replacement, never a merge over an old figure
        update["fees"] = d["fees"]
        prov["fees"] = {"source": d["fees_source"], "checked": d.get("checked", "2026-10-11")}
    if update:
        update[cs.PROVENANCE] = prov
        cs.apply_update(e, update)


def main():
    apply = "--apply" in sys.argv
    dec = json.load(open(os.path.join(HERE, "decisions.json"), encoding="utf-8"))["entries"]
    removed = {r["id"]: r for r in load(os.path.join(HERE, "removed_records.json"))}
    rows = json.load(open(CG, encoding="utf-8"))
    next_id = max(r["id"] for r in rows + load(FAMILY)) + 1
    new_ids, marked, dropped = [], [], []
    for d in dec:
        if d["verdict"] == "drop":
            e = next((r for r in rows if r["id"] == d["id"]), None)
            if e is None:
                print("already dropped:", d["id"], d["name"])
                continue
            rows.remove(e)
            dropped.append({"id": e["id"], "name": e["name"], "state": e["state"],
                            "ownership": e.get("ownership"), "action": "removed",
                            "why": d["why"], "decided": d["decided"]})
            print(e["id"], "drop", e["state"], e["name"])
            continue
        if d["verdict"] not in ("restore", "add", "mark", "minimum"):
            continue
        had = present(rows, d)
        if had:
            print("already written:", had["id"], had["name"])
            continue
        if d["verdict"] in ("mark", "minimum"):
            e = next(r for r in rows if r["id"] == d["id"])
            if d["verdict"] == "mark":
                e["inclusion_evidence"] = (e.get("inclusion_evidence") or "").rstrip("; ") + (
                    f"; {stamp(d)}: {d['why']}")
            edit(e, d)
            cs.validate_row(e, label=e["name"])
            marked.append(e["id"])
            print(e["id"], d["verdict"], e["state"], e["name"], "|", (e.get("booking") or {}).get("min_stay"))
            continue
        if d["verdict"] == "restore":
            e = json.loads(json.dumps(removed[d["old_id"]]))
            e["id"] = next_id
            e["inclusion_evidence"] = (e.get("inclusion_evidence") or "").rstrip("; ") + (
                f"; {stamp(d)}: restored (was id {d['old_id']}, removed {d['removed']} under the "
                f"standing-minimum rule AWH lifted 2026-10-10): {d['why']}")
        else:
            rec = dict(d["record"])
            rec["id"] = next_id
            rec["kind"] = "campground"
            rec["inclusion_evidence"] = rec["inclusion_evidence"].rstrip("; ") + (
                f"; {stamp(d)}: skipped {d['skipped']} for the minimum stay alone (AWH lifted that "
                f"rule 2026-10-10)")
            e = {k: rec[k] for k in FIELD_ORDER if k in rec}
        edit(e, d)
        cs.validate_row(e, label=e["name"])
        rows.append(e)
        new_ids.append(next_id)
        print(next_id, d["verdict"], e["state"], e["name"], "|", (e.get("booking") or {}).get("min_stay"))
        next_id += 1
    print(len(new_ids), "new", len(marked), "marked", len(dropped), "dropped",
          "(written)" if apply else "(dry run)",
          "- ids for the note scan:", ",".join(map(str, new_ids + marked)) or "-")
    if apply and dropped:
        with open(DROPPED, "a", encoding="utf-8") as fh:
            for x in dropped:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    if apply and (new_ids or marked or dropped):
        tmp = CG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, CG)


if __name__ == "__main__":
    main()
