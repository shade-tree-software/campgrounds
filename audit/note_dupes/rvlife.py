"""Drop RV Life rating clauses the `rating` field already holds (AWH 2026-11-07).

AWH: notes that "say something that should be conveyed in the fields" go — e.g.
"RV Life 4.5*/$$ ~$21/night (auto 9/2026). --Claude" on Graves Mountain. The popup
draws `rating` as chips, so the clause is a second, staler copy.

A clause goes only when every figure it states matches the field: its stars equal
`rating.stars` (or it says unrated and the field has no stars) and its $ count
equals `rating.price_tier`. An aggregator average ("~$21/night") goes only when the
entry's resolved fees hold a nightly rate. Anything else in the clause (review
counts, "mis-tagged commercial", a geolocation remark) means it is left alone for
the read-through. Deletion only, landed through note_prices/lib.land.

    python3 audit/note_dupes/rvlife.py            # dry run: counts + samples
    python3 audit/note_dupes/rvlife.py --apply [--limit N]
"""
import os, random, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "note_prices"))
import lib  # noqa: E402

STARS = r"(?P<stars>\d(?:\.\d)?)\s?(?:\*|★|\s?stars?)(?:\s?\(\d+(?:\.\d)?/10\))?"
UNR = r"(?P<unr>(?:0\s?\*\s?)?\(?unrated(?:\s?\(0\*\))?\)?|0\s?\*)"
PRICE = r"(?:price(?: rating)?\s)?(?P<price>\$+|\d \$ signs?)"
AVG = r"(?P<avg>~\s?\$\d+(?:/night| avg)?)"
AUTO = r"(?P<auto>\((?:auto )?\d{1,2}/\d{4}(?:,\s?unrated)?\))"
SEP = r"\s?(?:/|,)?\s?"
CLAUSE = re.compile(
    r"RV\s?Life:?\s"
    r"(?:(?:" + STARS + r"|" + UNR + r")" + SEP + r")?"
    r"(?:(?P<unr2>\(?unrated\)?)" + SEP + r")?"
    r"(?:" + PRICE + r")?"
    r"(?:\s?(?P<unr3>\(?unrated\)?))?"
    r"(?:\s" + AVG + r")?"
    r"(?:\s?" + AUTO + r")?"
    r"(?P<end>[.;]|(?=\s--)|$)")

def tier(p):
    if not p: return None
    return int(p[0]) if p[0].isdigit() else len(p)

def matches(m, e, f):
    r = e.get("rating") or {}
    if r.get("source") != "rvlife": return False
    if not (m.group("stars") or m.group("unr") or m.group("unr2") or m.group("unr3") or m.group("price")):
        return False
    if m.group("stars"):
        s = float(m.group("stars"))
        if s == 0 and r.get("stars") is None: pass
        elif r.get("stars") is None or float(r["stars"]) != s: return False
    elif (m.group("unr") or m.group("unr2") or m.group("unr3")):
        if r.get("stars"): return False
    if m.group("price") is not None and tier(m.group("price")) != r.get("price_tier"): return False
    if m.group("avg") and not ("nightly_low" in f or "nightly_high" in f): return False
    return True

def clean(note):
    """Whitespace and orphaned-marker tidy after a deletion."""
    n = re.sub(r"\s{2,}", " ", note)
    # A --Claude marker attributes everything back to the previous marker, so it
    # goes only when the deletion left its segment empty.
    n = re.sub(r"(^|--\w+\s)\s*--Claude\b", r"\1", n.strip())
    n = re.sub(r"\s+([.;,])", r"\1", n).replace(";.", ".").replace("..", ".")
    n = re.sub(r";\s*$", ".", n.strip())
    n = re.sub(r"--Claude\s+--Claude", "--Claude", n)
    return n.strip()

def propose(e, reg):
    n = e.get("note") or ""
    if "RV" not in n: return None
    f = lib.fees(e, reg); out = n; hit = False
    for m in reversed(list(CLAUSE.finditer(n))):
        if not matches(m, e, f): continue
        s, t = m.start(), m.end()
        out = out[:s] + out[t:]; hit = True
    if not hit: return None
    out = clean(out)
    return out if out != n else None

def main():
    cg, reg = lib.load()
    apply = "--apply" in sys.argv
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    items = []
    for e in cg:
        if e.get("kind") == "family": continue
        p = propose(e, reg)
        if p is not None: items.append({"id": e["id"], "was": e["note"], "note": p})
    if lim: items = items[:lim]
    print(len(items), "proposals")
    random.seed(7)
    for it in random.sample(items, min(25, len(items))) if not apply else []:
        print(f"\n{it['id']}:\n  - {it['was']}\n  + {it['note']}")
    done, refused = lib.land(cg, items, "2026-11-07", apply)
    print(len(done), "landed" if apply else "would land", "|", len(refused), "refused", refused[:10])

if __name__ == "__main__":
    main()
