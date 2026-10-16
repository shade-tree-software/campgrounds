#!/usr/bin/env python3
"""Edit whole campgrounds.json entries in place without re-dumping the file (2026-10-16).

    from edit_entries import edit
    edit({id: fn(entry) -> entry or None (None removes it)}, note_rescanned=True)

Each entry's text block is replaced by its own json.dumps (indent 2, ensure_ascii=False),
so the diff touches only the edited entries. When an edited entry's note changed and
note_rescanned is set, note_scan.sig is set to the new note's hash: the edit was made
from a source, so the note holds nothing for extract_fields.py to re-derive.
"""
import json, re, sys, datetime
ROOT = __file__.rsplit("/audit/", 1)[0]
sys.path.insert(0, ROOT)
from extract_fields import note_sig
P = ROOT + "/campgrounds.json"


def edit(fns, note_rescanned=True):
    s = open(P).read()
    for i, fn in fns.items():
        m = re.search(r'\n  \{\n    "id": %d,\n' % i, s)
        a = m.start() + 1; b = s.index("\n  }", a) + 4
        e = json.loads(s[a:b]); before = e.get("note")
        e = fn(e)
        if e is None:
            if s[b] == ",":
                s = s[:a] + s[b + 2:]          # drop "},\n"
            else:
                s = s[:a - 2] + s[b:]          # last entry: drop the comma before it
            continue
        if note_rescanned and e.get("note") != before and e.get("note_scan"):
            e["note_scan"] = {"sig": note_sig(e["note"]), "checked": datetime.date.today().isoformat(),
                              "model": "claude-opus-5-5/session"}
        s = s[:a] + "\n".join("  " + l for l in json.dumps(e, indent=2, ensure_ascii=False).split("\n")) + s[b:]
    json.loads(s)
    open(P, "w").write(s)
