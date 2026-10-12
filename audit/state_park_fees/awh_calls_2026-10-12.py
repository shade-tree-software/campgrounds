"""AWH's calls of 2026-10-12: python3 -I awh_calls_2026-10-12.py [--apply]

- Drop Shangri-La Trailhead Campground (FL 155): every bookable site on Reserve Florida is a 'Horse Site' and the park
  says 'We are known for our equestrian camping' - an equestrian campground (docs/campground-curation.md).
- Merge seven Georgia parks entered twice (AWH's entry and a later sweep's, 0.1-2.2 km apart): the original keeps its id,
  name, pin, rating and waterfront call; it takes the sweep entry's links, phone, structured groups it lacks (with their
  provenance), evidence (appended, labelled) and description (appended under its own --Claude marker).
- Rename Stephen C. Foster State Park (GA 4543) to Okefenokee State Park, the park's name on gastateparks.org and the
  booking site.
Each drop/merge is logged in dropped.jsonl. Prints the ids whose notes changed, for the note scan."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
import trips  # noqa: E402
D = "2026-10-12"
path = os.path.join(ROOT, "campgrounds.json")
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
PAIRS = [(2, 4530), (3, 4537), (695, 4538), (173, 4521), (195, 4520), (693, 4545), (731, 4542)]
GROUPS = ("hookups", "sites", "facilities", "season", "booking", "discounts", "status")
log, gone, notes = [], set(), []

for keep, drop in PAIRS:
    k, d = by[keep], by[drop]
    assert not trips.campground_references(drop), (drop, "referenced by a trip")
    links = [u for u in (k.get("website") or "").split("\n") if u]
    links += [u for u in (d.get("website") or "").split("\n") if u and u not in links]
    k["website"] = "\n".join(links)
    if not k.get("phone") and d.get("phone"):
        k["phone"] = d["phone"]
    prov = dict(k.get(cs.PROVENANCE) or {})
    for g in GROUPS:
        if d.get(g) and not k.get(g):
            k[g] = d[g]
            if (d.get(cs.PROVENANCE) or {}).get(g):
                prov[g] = d[cs.PROVENANCE][g]
    if prov:
        k[cs.PROVENANCE] = prov
    for f in ("inclusion_evidence", "waterfront_evidence"):
        if d.get(f) and d[f] not in (k.get(f) or ""):
            k[f] = ((k.get(f) or "") + f"  | From merged entry {drop} ({D}): " + d[f]).strip(" |")
    if d.get("note") and d["note"] not in (k.get("note") or ""):
        k["note"] = ((k.get("note") or "").rstrip() + "  " + d["note"]).strip()
        notes.append(keep)
    cs.validate_row(k, label=k["name"])
    gone.add(drop)
    log.append({"id": drop, "name": d["name"], "state": d["state"], "ownership": d.get("ownership"), "action": "merged",
                "into": keep, "decided": D,
                "why": f"duplicate of {keep} {k['name']} (AWH's entry; this one came from a later sweep): the same park and "
                       f"booking listing, pins {d['location']} vs {k['location']}. AWH {D}: merge. {keep} keeps its id, name, "
                       f"pin, rating and waterfront call ({k.get('waterfront')}; this entry said {d.get('waterfront')}) and "
                       f"takes this entry's links, phone, missing structured groups, evidence and description."})

s = by[155]
assert not trips.campground_references(155)
gone.add(155)
log.append({"id": 155, "name": s["name"], "state": s["state"], "ownership": s.get("ownership"), "action": "dropped",
            "decided": D,
            "why": "equestrian campground: Reserve Florida (PlaceId 62) lists all 22 bookable sites as 'Horse Site' and its "
                   "notice says 'We are known for our equestrian camping and trails ... Horse sites have tie-outs "
                   "available' (read 2026-10-12). AWH 2026-10-12: drop. (Its note also misnamed it a private campground.)"})

f = by[4543]
f["name"] = "Okefenokee State Park"
line = (f"Renamed {D}: Georgia now calls the park Okefenokee State Park (gastateparks.org and the booking site); it was "
        f"Stephen C. Foster State Park. --Claude")
if line not in (f.get("note") or ""):
    f["note"] = ((f.get("note") or "").rstrip() + "  " + line).strip()
    notes.append(4543)
if f.get("fees", {}).get("note"):
    f["fees"]["note"] = f["fees"]["note"].replace(" The park is now called Okefenokee State Park.", "")
cs.validate_row(f, label=f["name"])

rows[:] = [r for r in rows if r["id"] not in gone]
for x in log:
    print(x["action"], x["id"], x["name"], "->", x.get("into", ""))
print("renamed 4543 ->", f["name"])
print("note scan ids:", ",".join(map(str, notes)))
if "--apply" in sys.argv:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    with open(os.path.join(HERE, "dropped.jsonl"), "a", encoding="utf-8") as fh:
        for x in log:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("written")
else:
    print("(dry run)")
