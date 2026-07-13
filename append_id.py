#!/usr/bin/env python3
"""Append Idaho add-research results to campgrounds.json.

Usage: python3 append_id.py <results.json> [results2.json ...]
Each results file is a JSON array of add-research objects (add|skip). Only
decision=="add" are appended. Ids assigned from current max+1. Fields written
in canonical order WITHOUT waterfront_evidence (empty/absent = not yet audited;
the waterfront apply script stamps it later). `lead` is stripped from the stored
entry but recorded to /tmp/id_leads.json keyed by assigned id for the audit stage.
"""
import json, sys, io, html

CG = "/home/andrew/Dev/campgrounds/campgrounds.json"
LEADS = "/tmp/id_leads.json"

def main(files):
    data = json.load(open(CG))
    next_id = max(e["id"] for e in data) + 1
    try:
        leads = json.load(open(LEADS))
    except FileNotFoundError:
        leads = {}

    new_blocks = []
    added = []
    for f in files:
        for r in json.load(open(f)):
            if r.get("decision") != "add":
                continue
            def u(x):
                return html.unescape(x) if isinstance(x, str) else x
            e = {
                "id": next_id,
                "kind": "campground",
                "name": u(r["name"]),
                "location": r["location"],
                "elevation_meters": r["elevation_meters"],
                "state": "ID",
                "ownership": r["ownership"],
                "waterfront": "not waterfront",
                "inclusion_evidence": u(r.get("inclusion_evidence", "")),
                "website": u(r.get("website", "")),
                "phone": r.get("phone", ""),
                "note": u(r.get("note", "")),
            }
            block = "\n".join("  " + ln for ln in json.dumps(e, indent=2, ensure_ascii=False).splitlines())
            new_blocks.append(block)
            leads[str(next_id)] = {
                "id": next_id, "name": e["name"], "location": e["location"],
                "ownership": e["ownership"], "website": e["website"],
                "lead": r.get("lead", {}),
            }
            added.append((next_id, e["name"], e["ownership"]))
            next_id += 1

    if not new_blocks:
        print("no adds")
        return

    raw = open(CG).read()
    idx = raw.rstrip().rfind("]")
    head = raw[:idx].rstrip()          # ends with the last entry's "}"
    tail = raw[idx:]                     # the closing "]"
    merged = head + ",\n" + ",\n".join(new_blocks) + "\n" + tail
    open(CG, "w").write(merged)

    # validate
    check = json.load(open(CG))
    json.dump(leads, open(LEADS, "w"), indent=1, ensure_ascii=False)
    print(f"appended {len(added)} entries; file now {len(check)} entries; ids {added[0][0]}..{added[-1][0]}")
    for i, n, o in added:
        print(f"  {i} [{o}] {n}")

if __name__ == "__main__":
    main(sys.argv[1:])
