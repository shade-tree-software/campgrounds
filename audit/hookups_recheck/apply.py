#!/usr/bin/env python3
"""Apply decisions.json to campgrounds.json (the 2026-10-12 hookups re-check).

    python3 -I audit/hookups_recheck/apply.py [--apply]

AWH 2026-10-12, on ~140 note-derived "no hookups" values whose notes never said so: "walk
through the rec.gov descriptions and get the real data so we're not guessing." scan.py and
pages.py fetched what recreation.gov (RIDB's site catalog, the facility description, the
campground page's amenities) and the agency page say; decisions.json records, per entry, what
each hookup key is on that evidence:

  set     {key: value}  the value a source states (confirming or correcting the held one);
  remove  [keys]        held keys no source states: absent is unknown, never a guessed "no";
  source  where the set values come from, quoted;
  derived true when a set value comes from RIDB's site catalog through recgov_hookups.derive
          (a machine reading, as the 2026-09-18 fill wrote it); a description or page read
          by hand carries no method, like the other hand-checked groups.

Keys a decision doesn't name are left as they are: those the note states. When a decision sets
values, the group's provenance becomes its source (prefixed "note prose; " when note-stated keys
remain, which also makes it `derived`); when it only removes, what is left is still the note's
and keeps its "note prose" provenance. `checked` records what was read for the entry. Values go
through campground_schema.apply_update, so a bad one raises before anything is written. A rerun
skips entries whose provenance already carries MARK, and finds removals already made.
Dry run unless --apply.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

MARK = "hookups re-check 2026-10-12"
TODAY = "2026-10-12"


def main():
    dec = json.load(open(os.path.join(HERE, "decisions.json"), encoding="utf-8"))["entries"]
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path, encoding="utf-8"))
    by = {r["id"]: r for r in rows}
    changed = 0
    for k, d in sorted(dec.items(), key=lambda kv: int(kv[0])):
        e = by.get(int(k))
        if e is None:
            print(k, "MISSING")
            continue
        prov = dict(e.get(cs.PROVENANCE) or {})
        if MARK in ((prov.get("hookups") or {}).get("source") or ""):
            continue
        held = dict(e.get("hookups") or {})
        new = dict(held)
        for key in d.get("remove") or []:
            new.pop(key, None)
        new.update(d.get("set") or {})
        kept = [key for key in new if key not in (d.get("set") or {})]
        if new == held and not d.get("set"):
            continue
        e.pop("hookups", None)
        if new and not d.get("set"):
            # Only removals: what is left is still the note's, so its provenance stays
            # "note prose" and a later edit of the note re-reads it (apply_absent --rescan).
            cs.apply_update(e, {"hookups": new})
            cs.validate_row(e, label=e["name"])
            changed += 1
            print(f"{k:>6} {e['state']} {e['name'][:38]:38} {held} -> {new}")
            continue
        prov.pop("hookups", None)
        if new:
            source = f"{d['source']} [{MARK}]"
            derived = d.get("derived") or bool(kept)
            if kept:
                source = "note prose; " + source
            prov["hookups"] = {"source": source, "checked": TODAY}
            if derived:
                prov["hookups"]["method"] = "derived"
            cs.apply_update(e, {"hookups": new, cs.PROVENANCE: prov})
        elif prov:
            e[cs.PROVENANCE] = prov
        else:
            e.pop(cs.PROVENANCE, None)
        cs.validate_row(e, label=e["name"])
        changed += 1
        print(f"{k:>6} {e['state']} {e['name'][:38]:38} {held} -> {new}")
    print(changed, "entries changed")
    if "--apply" in sys.argv:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
        print("written")


if __name__ == "__main__":
    main()
