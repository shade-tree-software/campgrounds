"""Drop note sentences that only say FCFS / no reservations, where booking says so (AWH 2026-11-07).

AWH's example: Laurel Fork's "First-come, first-served (no reservations)." beside booking
{reservable: false, fcfs: always}, which the popup already draws as "not reservable" / "FCFS".

A sentence (or ;-clause) goes only when it is NOTHING but that wording, and only on the
entry's OWN booking values: FCFS wording needs fcfs == "always", "no reservations" wording
needs reservable == false. An agency-inherited value is drawn as "typical for <agency>",
which is weaker than the note's claim about this park, so it does not license a deletion.
A sentence with anything else in it ("FCFS; pay at the honor box") is left for the read-through.

    python3 audit/note_dupes/fcfs.py            # dry run
    python3 audit/note_dupes/fcfs.py --apply
"""
import os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "note_prices")); sys.path.insert(0, HERE)
import lib  # noqa: E402
from rvlife import clean  # noqa: E402

FC = r"(?:first[- ]come,?\s?first[- ]serve[d]?|FCFS)"
NR = (r"(?:no (?:advance )?reservations(?: accepted| taken)?|not reservable|non-reservable"
      r"|not bookable in advance|not on recreation\.gov|no online booking)")
PURE = re.compile(rf"\s*(?:{FC}|{NR}|only|[-–—;,:()]|\s)+\s*", re.I)
CLAUSE = re.compile(r"(?:^|(?<=[.;]\s)|(?<=--Claude\s)|(?<=--AWH\s))[^.;]*?[.;]")

def ok(s, b):
    if not PURE.fullmatch(s.rstrip(".;")): return False
    if s.count("(") != s.count(")"): return False      # half of a parenthetical
    fc, nr = re.search(FC, s, re.I), re.search(NR, s, re.I)
    if not (fc or nr): return False
    return (not fc or b.get("fcfs") == "always") and (not nr or b.get("reservable") is False)

def propose(e):
    n = e.get("note") or ""; b = e.get("booking") or {}
    out = n
    for m in reversed(list(CLAUSE.finditer(n))):
        if ok(m.group(0).strip(), b):
            rest = out[m.end():].lstrip()
            opens = m.start() == 0 or re.search(r"(\.|--\w+)\s*$", out[:m.start()])
            if opens and m.group(0).rstrip().endswith(";") and rest[:1].islower():
                rest = rest[0].upper() + rest[1:]      # the clause opened its sentence
            out = out[:m.start()] + (" " if out[m.end():m.end()+1].isspace() else "") + rest
    if out == n: return None
    out = clean(out)
    return out if out != n else None

def main():
    cg, _ = lib.load(); apply = "--apply" in sys.argv
    items = [{"id": e["id"], "was": e["note"], "note": p} for e in cg
             if e.get("kind") != "family" and (p := propose(e)) is not None]
    print(len(items), "proposals")
    random.seed(3)
    if not apply:
        for it in random.sample(items, min(20, len(items))):
            print(f"\n{it['id']}:\n  - {it['was']}\n  + {it['note']}")
    done, refused = lib.land(cg, items, "2026-11-07", apply)
    print(len(done), "landed" if apply else "would land", "|", len(refused), "refused", refused[:10])

if __name__ == "__main__":
    main()
