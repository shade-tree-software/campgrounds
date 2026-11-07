"""Check (and with --apply, land) an extra-vehicle output file.
    python3 -I audit/extra_vehicle/check.py out/NNN.json [--apply]"""
import datetime, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "note_prices"))
import lib
import campground_schema as cs
today = datetime.date.today().isoformat()
cg, reg = lib.load(); by = {e["id"]: e for e in cg}
rows = json.load(open(sys.argv[1], encoding="utf-8")); fields = []; notes = []; bad = 0
for r in rows:
    e = by.get(r["id"])
    if e is None: print("!! unknown id", r["id"]); bad += 1; continue
    if r.get("flag"): print("FLAG", r["id"], e["name"], "|", r["flag"])
    ev = r.get("extra_vehicle")
    if ev is not None:
        src = (e.get("note") or "") if r.get("from") == "note" else str((e.get("fees") or {}).get("note", ""))
        if r.get("from") == "note" and r.get("was"): src = r["was"]
        if r.get("from") not in ("note", "fees_note") or not r.get("evidence") or r["evidence"] not in src:
            print("!! evidence is not an exact substring of", r.get("from"), r["id"]); bad += 1; continue
        if "extra_vehicle" in lib.fees(e, reg) and not r.get("_landed"):
            print("!! already has extra_vehicle", r["id"]); bad += 1; continue
        try: cs.validate_row({"fees": {"extra_vehicle": ev}})
        except Exception as ex: print("!! invalid", r["id"], ex); bad += 1; continue
        if not ev: print("!! empty extra_vehicle", r["id"]); bad += 1; continue
        fields.append((e, r))
    if "note" in r:
        old = e.get("note") or ""; r.setdefault("was", old)
        if r["was"] != old and not r.get("_landed"): print("!! note changed since read", r["id"]); bad += 1; continue
        a = lib.added_words(r["was"], r["note"])
        if a: print("!! adds words", r["id"], a); bad += 1; continue
        if r["was"].count("--AWH") > r["note"].count("--AWH") and not r.get("awh_dropped"):
            print("!! drops an --AWH marker without awh_dropped", r["id"]); bad += 1; continue
        notes.append({"id": r["id"], "was": r["was"], "note": r["note"], "awh_dropped": r.get("awh_dropped")})
print(len(fields), "fields,", len(notes), "note edits,", bad, "problems")
if "--apply" in sys.argv:
    if bad: sys.exit("not applied: fix the problems first")
    for e, r in fields:
        f = e.setdefault("fees", {}); f["extra_vehicle"] = r["extra_vehicle"]
        p = e.setdefault("provenance", {}).setdefault("fees", {})
        where = "the entry note" if r["from"] == "note" else "fees.note (same source)"
        tag = f"extra_vehicle from {where}: '{r['evidence']}' ({today})"
        if p.get("source"): p["source"] += "; " + tag
        else: p.update({"source": tag, "checked": today, "method": "derived"})
        r["_landed"] = True
    lib.dump(cg)
    cg, reg = lib.load()
    done, refused = lib.land(cg, notes, today, True) if notes else ([], [])
    for r in rows:
        if "note" in r: r["_landed"] = True
    json.dump(rows, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(fields), "fields landed;", len(done), "notes landed", refused)
