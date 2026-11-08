"""Apply a season-pass out/NN.json: write each `differs` row's agency season, with the
agency page as provenance and the old calendar edges recorded as the reservable window.
Dry run unless --apply. Usage: apply.py out/NN.json [--apply] [--skip id,id]"""
import json, sys
sys.path.insert(0, "audit/note_prices")
import lib

path = sys.argv[1]; do = "--apply" in sys.argv
skip = set()
if "--skip" in sys.argv:
    skip = {int(x) for x in sys.argv[sys.argv.index("--skip") + 1].split(",")}
EXTRA = json.load(open(path.replace("/out/", "/extra/"))) if __import__("os").path.exists(path.replace("/out/", "/extra/")) else {}
cg, _ = lib.load(); by = {c["id"]: c for c in cg}
n = 0
for r in json.load(open(path)):
    if r["verdict"] != "differs" or r["id"] in skip:
        print(r["id"], r["verdict"], "- left"); continue
    c = by[r["id"]]; old = c["season"]
    assert c["provenance"]["season"]["source"].startswith("recreation.gov availability calendar"), r["id"]
    new = dict(r["agency_season"])
    note = EXTRA.get(str(r["id"]), {}).get("season_note")
    if note: new["note"] = note
    edges = {k: v for k, v in old.items() if k in ("opens", "closes")}
    src = f"{r['url']} ('{r['quote']}')"
    if r.get("calendar_is_booking_window"):
        src += f"; the recreation.gov calendar edges {edges} were the reservable window, not the open season"
    c["season"] = new
    c["provenance"]["season"] = {"source": src, "checked": r["read"], "method": "manual"}
    n += 1
    print(r["id"], c["name"][:34], old, "->", new)
print(n, "written" if do else "would write")
if do: lib.dump(cg)
