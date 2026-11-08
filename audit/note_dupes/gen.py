"""Build read-through items: each note beside exactly what the popup already says (AWH 2026-11-07).

    python3 audit/note_dupes/gen.py out/ 40        # writes out/001.json ...

`shown` is the chip text the map popup draws from the entry's OWN values (the shipped
static/campground-schema.js run through quickjs, capped at CG_FACT_CHIP_MAX per group as
the popup does). Agency-inherited chips are left out: the popup marks them "typical for
<agency>", so a note's claim about this park is stronger and stays. The scope is notes
that still carry the wording AWH named: FCFS / reservation status, RV Life ratings, and
curator bookkeeping (correction histories, who found what, audit stamps).
"""
import json, os, re, sys
import quickjs
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

CHIP_MAX = 6
FC = re.compile(r"first[- ]come[- ,]+first[- ]serve|\bFCFS\b|no (advance )?reservations|not reservable|walk-?up only", re.I)
RV = re.compile(r"RV\s?Life\s?:?\s?(\d|unrated|listed)", re.I)
BK = re.compile(r"\b(corrected|verified|re-?checked|checked|confirmed|updated|re-?audited|audited|re-?pinned|moved"
                r"|dropped|removed|read)\b[^.]{0,40}\b20\d\d-\d\d(-\d\d)?|\(auto \d+/\d{4}\)|found by AWH|per AWH"
                r"|AWH \d{4}-|AWH asked|\bsweep\b|phase \d|Waterfront-audited|PIN APPROXIMATE|verify before relying", re.I)

def in_scope(e):
    n = e.get("note") or ""; b = e.get("booking") or {}
    return ((FC.search(n) and (b.get("fcfs") or b.get("reservable") is False))
            or (RV.search(n) and (e.get("rating") or {}).get("source") == "rvlife")
            or BK.search(n))

def main():
    out, size = sys.argv[1], int(sys.argv[2]); os.makedirs(out, exist_ok=True)
    ctx = quickjs.Context()
    ctx.eval(open(os.path.join(ROOT, "static", "campground-schema.js"), encoding="utf-8").read())
    ctx.eval("function pc(g, v, k) { return JSON.stringify(sfPopupChips(JSON.parse(g), JSON.parse(v), new Set(JSON.parse(k)))); }")
    pc = ctx.get("pc")
    groups = {g["key"]: g for g in cs.to_client()}
    reg = json.load(open(os.path.join(ROOT, "campground_policies.json")))
    cg = json.load(open(os.path.join(ROOT, "campgrounds.json")))
    items = []
    for e in cg:
        if e.get("kind") == "family" or not in_scope(e): continue
        shown = {}
        for gk, block in cs.resolve(e, reg).items():
            if gk == "status" or gk not in groups: continue
            own = [k for k in block["values"] if k not in set(block.get("inherited") or [])]
            if not own: continue
            chips = json.loads(pc(json.dumps(groups[gk]), json.dumps(block["values"]), json.dumps(own)))[:CHIP_MAX]
            if chips: shown[groups[gk]["label"]] = chips
        items.append({"id": e["id"], "name": e["name"], "state": e.get("state"),
                      "ownership": e.get("ownership"), "note": e["note"], "shown": shown})
    for i in range(0, len(items), size):
        json.dump(items[i:i + size], open(os.path.join(out, f"{i // size + 1:03d}.json"), "w"),
                  ensure_ascii=False, indent=1)
    print(len(items), "items,", (len(items) + size - 1) // size, "chunks")

if __name__ == "__main__":
    main()
