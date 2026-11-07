"""Apply a fee fix-up proposal file (AWH 2026-11-07 short pass after the extra-vehicle backfill).
    python3 -I audit/fee_fixups/apply.py out/<file>.json [--apply]
Rows: {id, set?, remove?, fees_note?, note?, awh_dropped?, sources, summary, flag?}. Fees keys are
validated; the entry note goes through audit/note_prices/lib.land (deletion only)."""
import copy, datetime, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "note_prices"))
import lib
import campground_schema as cs
today = datetime.date.today().isoformat()
cg, reg = lib.load(); by = {e["id"]: e for e in cg}
rows = json.load(open(sys.argv[1], encoding="utf-8")); notes = []; bad = 0; changed = []
for r in rows:
    e = by.get(r["id"])
    if e is None: print("!! unknown id", r["id"]); bad += 1; continue
    print(r["id"], e["name"][:40], "|", r.get("summary", "")[:160])
    if r.get("flag"): print("   FLAG", r["flag"][:300])
    f = copy.deepcopy(e.get("fees") or {})
    for k in r.get("remove", []): f.pop(k, None)
    f.update(r.get("set", {}))
    if "fees_note" in r: f["note"] = r["fees_note"]
    if f != (e.get("fees") or {}):
        try: cs.validate_row({"fees": f})
        except Exception as ex: print("!! invalid", r["id"], ex); bad += 1; continue
        if not r.get("sources"): print("!! no sources", r["id"]); bad += 1; continue
        changed.append((e, f, r))
    if "note" in r:
        a = lib.added_words(e.get("note") or "", r["note"])
        if a: print("!! adds words", r["id"], a); bad += 1; continue
        notes.append({"id": r["id"], "was": e.get("note") or "", "note": r["note"], "awh_dropped": r.get("awh_dropped")})
print(len(changed), "fee changes,", len(notes), "note edits,", bad, "problems")
if "--apply" in sys.argv:
    if bad: sys.exit("not applied")
    for e, f, r in changed:
        e["fees"] = f
        p = e.setdefault("provenance", {}).setdefault("fees", {})
        tag = f"fix-up {today}: " + "; ".join(r["sources"])
        p["source"] = (p["source"] + "; " + tag) if p.get("source") else tag
        p["checked"] = today; p.setdefault("method", "manual")
    lib.dump(cg)
    cg, reg = lib.load()
    done, refused = lib.land(cg, notes, today, True) if notes else ([], [])
    print(len(changed), "fee changes landed;", len(done), "notes", refused)
