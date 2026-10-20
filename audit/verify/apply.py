#!/usr/bin/env python3
"""Write verification results (results/<id>.json) into campgrounds.json.

    python3 -I audit/verify/apply.py [--apply] [ID ...]

Dry run unless --apply. Every result is validated through campground_schema.apply_update on
a copy first, so a malformed one is reported and skipped rather than half-written. Refuses to
overwrite a group whose provenance is manual/reported (that conflict should have been a flag).
Writes each group's provenance, the entry's verify_scan, and a proposed note if present.
Applied results move to results/applied/, which is what keeps a rerun idempotent.
Flags are printed for a human; nothing here acts on them.
"""
import copy, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs

CG = os.path.join(ROOT, "campgrounds.json")
RES = os.path.join(HERE, "results")
DONE = os.path.join(RES, "applied")
HUMAN = {"manual", "reported"}


def awh_segments(note):
    """Each run of text the note attributes to AWH, marker included. A rewrite must keep
    them verbatim (curation doc: someone else's attributed text stays in their words)."""
    out = []
    for m in re.finditer(r"--AWH", note):
        start = max(note.rfind("--", 0, m.start()), -1)
        start = 0 if start < 0 else note.find(" ", start) + 1
        out.append(note[start:m.end()].strip())
    return out


def plan(entry, r):
    """(payload, problems) for one result."""
    problems, payload = [], {}
    prov = entry.get(cs.PROVENANCE) or {}
    for g, spec in (r.get("groups") or {}).items():
        if g not in cs.SCHEMA:
            problems.append(f"unknown group {g}")
            continue
        old = prov.get(g) or {}
        vals = spec.get("values") or {}
        if old.get("method") in HUMAN and old.get("checked", "") < r["checked"]:
            held = entry.get(g) or {}
            clash = {k: v for k, v in vals.items() if k in held and held[k] != v}
            if clash:
                problems.append(f"{g}: would overwrite {old['method']} values {sorted(clash)}")
                continue
        if not vals:
            continue
        if spec.get("method") not in ("manual", "reported") or not spec.get("source"):
            problems.append(f"{g}: needs method manual/reported and a source")
            continue
        payload[g] = vals
        payload.setdefault(cs.PROVENANCE, {})[g] = {
            "source": spec["source"], "checked": r["checked"], "method": spec["method"]}
    payload[cs.VERIFY_SCAN] = {"checked": r["checked"],
                               "sources": " ".join(r.get("sources") or []),
                               "note": (r.get("summary") or "")[:500]}
    return payload, problems


if __name__ == "__main__":
    os.makedirs(DONE, exist_ok=True)
    want = {int(a) for a in sys.argv[1:] if a.isdigit()}
    files = sorted(f for f in os.listdir(RES) if f.endswith(".json"))
    rows = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in rows}
    applied, notes = [], 0
    for f in files:
        r = json.load(open(os.path.join(RES, f), encoding="utf-8"))
        if want and r["id"] not in want:
            continue
        e = by.get(r["id"])
        if e is None:
            print(f"!! {f}: no entry {r['id']}")
            continue
        payload, problems = plan(e, r)
        trial = copy.deepcopy(e)
        try:
            touched = cs.apply_update(trial, payload)
        except cs.SchemaError as err:
            problems.append(f"schema: {err}")
        if problems:
            print(f"!! {r['id']} {e['name']}: " + "; ".join(problems))
            continue
        if r.get("note") and r["note"] != e.get("note"):
            lost = [seg for seg in awh_segments(e.get("note") or "") if seg not in r["note"]]
            if lost and not r.get("awh_superseded"):
                print(f"!! {r['id']} {e['name']}: note rewrite drops --AWH text: {lost[0][:80]!r}")
                continue
            trial["note"] = r["note"]
            notes += 1
        groups = sorted(g for g in touched if g in cs.SCHEMA)
        print(f"   {r['id']} {e['state']} {e['name']}: {', '.join(groups) or 'nothing new'}"
              + (" + note" if r.get("note") and r["note"] != e.get("note") else ""))
        for fl in r.get("flags") or []:
            print(f"      FLAG {fl}")
        by[r["id"]].clear()
        by[r["id"]].update(trial)
        applied.append(f)
    print(len(applied), "results ready,", notes, "note rewrites")
    if "--apply" in sys.argv and applied:
        with open(CG, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        for f in applied:
            shutil.move(os.path.join(RES, f), os.path.join(DONE, f))
        print("written")
