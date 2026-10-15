"""Apply AWH's 2026-10-14 (late) answers to the #2-#8f report:
  1. the long-stay rule (docs/campground-curation.md), with the minimum at 2 nights (holiday weekends excepted)
  2. drop Tymber 1224 and Clemson Hills 4377 ("my mistake")
  4. an RV Life $ or $$ keeps a park that posts no rate: the hold="b" parks and Liberty Haven 11558 stay
Run from the repo root; --apply writes campgrounds.json and appends to dropped_2026-10-11.jsonl."""
import json, os, sys
sys.path.insert(0, ".")
import trips

T = " (AWH 2026-10-14: the long-stay rule, docs/campground-curation.md)"
DROP = {
    1361: "long-stay park over the price limit: $51.40 a night; 140 of its 168 sites are seasonal",
    1519: "long-stay park over the price limit: $65-70 a night; 'caters to long-term and seasonal guests'",
    1265: "long-stay park over the price limit: $61-76 a night; 470 sites, 37 sold online",
    14847: "long-stay park over the price limit: $55-65 a night; a 55+ snowbird community",
    7558: "long-stay park over the price limit ($60) that also keeps a waitlist and runs background checks",
    7627: "long-stay park with a long minimum: every site type needs 28 nights by June 2027",
    10188: "long-stay park that rents RV sites by the month only",
    14426: "home community: sells and rents homes, a 55+ RV and manufactured-home park with a 3-month winter minimum",
    7861: "home community: a development selling lots, homes and pads with owner financing",
    4636: "long-stay park with no nightly rate posted and no site open on CampLife on any of 14 dates",
    1312: "long-stay park selling under 1 site in 10 by the night (12 of 209 sites online)",
    7856: "long-stay park whose stays need approval, a background check and photos of the rig",
    1224: "long-stay park with no nightly rate or phone posted and nothing to book on Campspot (AWH 2026-10-14: drop, reversing the 10-13 keep)",
    4377: "long-stay park over the price limit at $55 (AWH 2026-10-14: drop, reversing the 10-13 keep)",
}
for i in (1984, 3379, 4624, 4655, 4790, 4792, 5102, 7491, 7517, 7871, 11308, 14429):
    DROP[i] = "long-stay park with no nightly rate posted and no booking site that sells a night"
KEEP_B = [1749, 4092, 4313, 4789, 5545, 5565, 5806, 7452, 7417, 11314, 7521, 7669, 3390, 6757, 7507, 13087,
          11540, 7909, 1996, 6847, 7703, 5098, 11558]
IE = ("kept 2026-10-14: own website and phone but no posted rate; AWH 2026-10-14 (#4 answer): an RV Life $ or $$ "
      "can add or keep a park in the absence of a published rate (RV Life tier {})")

path = "campgrounds.json"
rows = json.load(open(path, encoding="utf-8"))
by = {r["id"]: r for r in rows}
log = []
for i, why in DROP.items():
    e = by[i]
    assert e["ownership"] == "private", i
    assert not trips.campground_references(i), (i, "referenced by a trip")
    log.append({"id": i, "name": e["name"], "state": e["state"], "ownership": e["ownership"], "action": "removed",
                "why": why + T})
for i in KEEP_B:
    e = by[i]
    tier = (e.get("rating") or {}).get("price_tier")
    assert tier in (1, 2), (i, tier)
    line = IE.format("$" * tier)
    if line not in (e.get("inclusion_evidence") or ""):
        e["inclusion_evidence"] = ((e.get("inclusion_evidence") or "").rstrip() + "; " + line).lstrip("; ")
rows[:] = [r for r in rows if r["id"] not in DROP]
print(len(log), "drops;", len(KEEP_B), "keeps")
if "--apply" in sys.argv:
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False); fh.write("\n")
    os.replace(path + ".tmp", path)
    with open("audit/price_research/dropped_2026-10-11.jsonl", "a", encoding="utf-8") as fh:
        for x in log: fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("written")
