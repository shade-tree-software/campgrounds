"""Check (and with --apply, land) a read-through output file.
    python3 -I audit/note_prices/check.py out/NNN.json [--apply]
Refuses an edit that adds a word, loses an --AWH marker without awh_dropped, or whose entry note
has changed since it was read. Prints flags for AWH/me."""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
cg, reg = lib.load(); by = {e["id"]: e for e in cg}
rows = json.load(open(sys.argv[1], encoding="utf-8")); items = []; bad = 0
for r in rows:
    e = by.get(r["id"])
    if e is None: print("!! unknown id", r["id"]); bad += 1; continue
    if r.get("flag"): print("FLAG", r["id"], e["name"], "|", r["flag"])
    if "note" not in r: continue
    old = e.get("note") or ""; r.setdefault("was", old)
    if r["was"] != old: print("!! note changed since read", r["id"]); bad += 1; continue
    a = lib.added_words(old, r["note"])
    if a: print("!! adds words", r["id"], a); bad += 1; continue
    if old.count("--AWH") > r["note"].count("--AWH") and not r.get("awh_dropped"):
        print("!! drops an --AWH marker without awh_dropped", r["id"]); bad += 1; continue
    if "  " not in r["note"] and "  " in old and r["note"].count(". ") > 1 and old.count(".  ") > 1:
        print("?? two-space style lost", r["id"])
    left = lib.PRICE.search(r["note"])
    if left and "CAMPER-REPORTED" not in r["note"]:
        print("?? price words remain", r["id"], "|", r["note"][max(0, left.start()-60):left.end()+40])
    items.append({"id": r["id"], "was": old, "note": r["note"], "awh_dropped": r.get("awh_dropped")})
print(len(items), "edits,", bad, "problems")
if "--apply" in sys.argv:
    if bad: sys.exit("not applied: fix the problems first")
    json.dump(rows, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    done, refused = lib.land(cg, items, datetime.date.today().isoformat(), True)
    print(len(done), "landed", refused)
