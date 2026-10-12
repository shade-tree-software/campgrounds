"""Replace dead booking links in `website`: python3 -I fix_links.py FIXES.json [--apply]

FIXES is a list of {"id", "old", "new", "why"}; `old` must be in the entry's website (a rerun
finds `new` already there and skips it). Dry run unless --apply."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
n = 0
for f in json.load(open(sys.argv[1], encoding="utf-8")):
    e = by[f["id"]]
    w = e.get("website") or ""
    if f["new"] in w:
        continue
    if f["old"] not in w:
        raise SystemExit(f"{f['id']}: old link not found")
    e["website"] = w.replace(f["old"], f["new"])
    n += 1
    print(f["id"], e["name"], "->", f["new"])
print(n, "links", "fixed" if "--apply" in sys.argv else "to fix")
if "--apply" in sys.argv and n:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
