"""Print a chunk's cuts beside the entry's chips, one line each, for review before landing."""
import difflib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
n = sys.argv[1]
rows = json.load(open(os.path.join(HERE, "out", f"{n}.json")))
inp = {x["id"]: x for x in json.load(open(os.path.join(HERE, "in", f"{n}.json")))}
for r in rows:
    o, p = r["was"], r["note"]
    sm = difflib.SequenceMatcher(None, o, p, autojunk=False)
    cuts = [o[a:b].strip() for t, a, b, c, d in sm.get_opcodes() if t in ("delete", "replace") and o[a:b].strip(" .;,")]
    print(r["id"], "CUT:", " | ".join(cuts)[:260])
    if r.get("curation"): print("    CUR:", r["curation"][:200])
    print("    CHIPS:", "; ".join(f"{k}: {', '.join(v)}" for k, v in inp[r["id"]]["shown"].items())[:220])
