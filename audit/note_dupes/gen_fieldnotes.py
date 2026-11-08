"""Build read-through items for notes that repeat a group's own note (AWH 2026-11-08).

    python3 audit/note_dupes/gen_fieldnotes.py audit/note_dupes/fn_in 25

Pohick Bay's note carried its minimum-stay rules a second time, beside `booking.note`
holding them in full. The popup now draws the season, booking, fees and sites notes
under their rows (folded to one line), so a note sentence they already say is a second,
staler copy. Each item carries `shown` (the chips, as gen.py builds them) and
`field_notes` (each popup-drawn group's OWN note, by row label). Scope: a note with a
sentence whose words mostly reappear in one of those group notes; the reader decides
whether it is really the same fact.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen  # noqa: E402

GROUPS = ("season", "booking", "fees", "sites")   # the group notes the popup draws
STOP = {"the", "a", "an", "and", "of", "to", "on", "in", "for", "at", "is", "are", "with", "or",
        "by", "from", "per", "it", "its", "be", "as", "no", "not", "site", "sites", "night", "nights"}

def toks(s):
    return set(re.findall(r"[a-z0-9$]+(?:\.\d+)?", s.lower())) - STOP

def overlaps(note, gnote):
    gt = toks(gnote)
    for seg in re.split(r"(?<=[.;])\s+", note):
        t = toks(seg)
        if len(t) >= 6 and len(t & gt) / len(t) >= 0.6:
            return True
    return False

def main():
    out, size = sys.argv[1], int(sys.argv[2]); os.makedirs(out, exist_ok=True)
    cg = json.load(open(os.path.join(gen.ROOT, "campgrounds.json")))
    cand = []
    for e in cg:
        n = e.get("note") or ""
        if e.get("kind") == "family" or not n: continue
        fn = {g: e[g]["note"] for g in GROUPS if isinstance(e.get(g), dict) and e[g].get("note")}
        if any(overlaps(n, v) for v in fn.values()):
            cand.append((e, fn))
    # chips exactly as gen.py draws them
    import quickjs, campground_schema as cs
    ctx = quickjs.Context()
    ctx.eval(open(os.path.join(gen.ROOT, "static", "campground-schema.js"), encoding="utf-8").read())
    ctx.eval("function pc(g, v, k) { return JSON.stringify(sfPopupChips(JSON.parse(g), JSON.parse(v), new Set(JSON.parse(k)))); }")
    pc = ctx.get("pc")
    groups = {g["key"]: g for g in cs.to_client()}
    reg = json.load(open(os.path.join(gen.ROOT, "campground_policies.json")))
    items = []
    for e, fn in cand:
        shown = {}
        for gk, block in cs.resolve(e, reg).items():
            if gk == "status" or gk not in groups: continue
            own = [k for k in block["values"] if k not in set(block.get("inherited") or [])]
            if not own: continue
            chips = json.loads(pc(json.dumps(groups[gk]), json.dumps(block["values"]), json.dumps(own)))[:gen.CHIP_MAX]
            if chips: shown[groups[gk]["label"]] = chips
        items.append({"id": e["id"], "name": e["name"], "state": e.get("state"),
                      "ownership": e.get("ownership"), "note": e["note"], "shown": shown,
                      "field_notes": {groups[g]["label"]: v for g, v in fn.items()}})
    for i in range(0, len(items), size):
        json.dump(items[i:i + size], open(os.path.join(out, f"{i // size + 1:03d}.json"), "w"),
                  ensure_ascii=False, indent=1)
    print(len(items), "items,", (len(items) + size - 1) // size, "chunks")

if __name__ == "__main__":
    main()
