#!/usr/bin/env python3
"""Schema phase 7: which campgrounds to verify next, and the batch files the verifier reads.

    python3 -I audit/verify/queue.py [--limit N] [--state XX] [--report]
    python3 -I audit/verify/queue.py --batch NAME --limit N   # write batches/NAME.json

Order (AWH 2026-10-20: "popups and stays count", then work through everything, states most
heavily visited first):
  1. campgrounds stayed at that carry an inherited value   (the 67)
  2. the other campgrounds stayed at
  3. campgrounds anyone in the family opened on the map in the last 60 days
     (trip_data/campground_views.jsonl), most-opened first
  4. everything else, by state in order of stays there, then RV Life stars, then name
An entry whose verify_scan is present is done and drops out; results already on disk in
results/ (written, not yet applied) also drop out, so two batches never overlap.
"""
import argparse, datetime, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs

VIEW_DAYS = 60


def load():
    rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
    reg = json.load(open(os.path.join(ROOT, "campground_policies.json"), encoding="utf-8"))
    trips = json.load(open(os.path.join(ROOT, "trip_data", "trips.json"), encoding="utf-8"))
    trips = trips if isinstance(trips, list) else trips.get("trips", [])
    return rows, reg, trips


def views():
    path = os.path.join(ROOT, "trip_data", "campground_views.jsonl")
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=VIEW_DAYS)).isoformat()
    c = Counter()
    try:
        for line in open(path, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("ts", "") >= since:
                c[r.get("id")] += 1
    except FileNotFoundError:
        pass
    return c


def ranked(rows, reg, trips):
    by = {e["id"]: e for e in rows}
    stays = Counter(s.get("campground_id") for t in trips for s in t.get("stays", [])
                    if s.get("campground_id"))
    state_stays = Counter()
    for cid, n in stays.items():
        if cid in by:
            state_stays[by[cid]["state"]] += n
    state_rank = {s: i for i, (s, _) in enumerate(state_stays.most_common())}
    seen = views()
    pending = {int(f[:-5]) for f in os.listdir(os.path.join(HERE, "results")) if f.endswith(".json")}
    out = []
    for e in rows:
        if e.get("kind") != "campground" or e.get(cs.VERIFY_SCAN) or e["id"] in pending:
            continue
        inherited = any(g["inherited"] for g in cs.resolve(e, reg).values())
        if stays[e["id"]]:
            tier = 1 if inherited else 2
        elif seen[e["id"]]:
            tier = 3
        else:
            tier = 4
        stars = (e.get("rating") or {}).get("stars") or 0
        out.append(((tier, -stays[e["id"]], -seen[e["id"]], state_rank.get(e["state"], 99),
                     -stars, e["name"]), e))
    out.sort(key=lambda x: x[0])
    return [(k[0], e) for k, e in out]


def dossier(e, reg):
    """What the verifier gets for one entry: the record minus bulky audit text, plus the
    resolved groups so it can see which values are inherited from the agency row."""
    keep = {k: v for k, v in e.items() if k not in ("waterfront_evidence", "note_scan", "stays")}
    return {"entry": keep, "resolved": cs.resolve(e, reg),
            "policy_refs": cs.policy_refs(e)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--state")
    ap.add_argument("--batch")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    rows, reg, trips = load()
    q = ranked(rows, reg, trips)
    if a.state:
        q = [x for x in q if x[1]["state"] == a.state]
    if a.report:
        done = sum(1 for e in rows if e.get(cs.VERIFY_SCAN))
        print(f"verified {done}; queued {len(q)}:", dict(Counter(t for t, _ in q)))
        print("by state (top 15):", Counter(e["state"] for _, e in q).most_common(15))
        sys.exit()
    q = q[:a.limit]
    if a.batch:
        path = os.path.join(HERE, "batches", a.batch + ".json")
        json.dump([dossier(e, reg) for _, e in q], open(path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("wrote", path, len(q))
    for t, e in q:
        print(t, e["id"], e["state"], e["ownership"], e["name"])
