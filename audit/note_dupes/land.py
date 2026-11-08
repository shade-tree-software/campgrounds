"""Land a read-through chunk: cleaned notes, plus bookkeeping moved to `curation_note`.

    python3 audit/note_dupes/land.py out/001.json            # dry run
    python3 audit/note_dupes/land.py out/001.json --apply

Each row: {id, was, note, curation?, awh_dropped?, ask?}. The note side is
note_prices/lib.land (deletion only, --AWH guard, note_scan re-stamp). `curation` must be
text that LEFT the note, word for word: its words have to come out of what the note lost
(plus joining words and attribution markers), so the hidden field can't gain a fact the
note never had. It is appended to any curation_note already there.
"""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "note_prices"))
import lib  # noqa: E402

MARKERS = {"claude", "awh"}

def curation_problem(was, note, cur):
    lost = collections.Counter(lib.WORD.findall(was.lower())) - collections.Counter(lib.WORD.findall(note.lower()))
    extra = collections.Counter(lib.WORD.findall(cur.lower())) - lost
    bad = sorted(w for w in extra if w not in lib.JOIN and w not in MARKERS)
    return ("curation adds words " + ",".join(bad)) if bad else None

def main():
    path = sys.argv[1]; apply = "--apply" in sys.argv
    rows = json.load(open(path, encoding="utf-8"))
    cg, _ = lib.load(); by = {e["id"]: e for e in cg}
    pre = []
    for r in rows:
        cur = (r.get("curation") or "").strip()
        why = curation_problem(r["was"], r["note"], cur) if cur else None
        if why: pre.append((r["id"], why))
    ok = [r for r in rows if r["id"] not in {i for i, _ in pre}]
    done, refused = lib.land(cg, ok, "2026-11-07", False)
    for r in ok:
        if r["id"] in done and (r.get("curation") or "").strip():
            e = by[r["id"]]; c = r["curation"].strip()
            e["curation_note"] = (e["curation_note"].rstrip() + "  " + c) if e.get("curation_note") else c
    if apply and done: lib.dump(cg)
    print(f"{len(done)} {'landed' if apply else 'would land'}, "
          f"{sum(1 for r in ok if r['id'] in done and r.get('curation'))} with curation")
    for i, why in pre + refused: print("  REFUSED", i, why)
    for r in rows:
        if r.get("ask"): print("  ASK", r["id"], r["ask"])

if __name__ == "__main__":
    main()
