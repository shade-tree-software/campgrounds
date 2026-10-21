#!/usr/bin/env python3
"""Sort screen.py's flags.json into review tiers and write tiers.md.

    python3 -I audit/dam_screen/tiers.py

screen.py compares each campground with the pool of every dam near it, and a dam near a
campground is often some OTHER lake's (a small pond up the hill, the next reservoir upstream).
So a raw "below the pool" is weak on its own. The tiers add what ties the dam to THIS
campground:

  A  below the pool AND (downstream of the dam OR the nearest water is lower than the pool)
     AND the dam is the campground's own (its name/river shares a word with the entry's name
     or note) - the case AWH described.
  B  below the pool of a dam that is the campground's own, but neither the side test nor the
     nearest water says tailwater (a berm with the lake right beside it, or a pin off the loop).
  C  below the pool of a dam whose name shares nothing with the entry, and the campground
     sits on its own water at its own level - almost always a different, higher lake.
  D  the pin sits more than 3 m BELOW the flat water beside it (within 300 m), whatever the
     dam - a levee/berm signal that needs no dam match.
  L  an A whose nearest water is itself lake-sized (1,500+ pixels, ~25 ha at z13): usually a
     lower lake below the dam (an afterbay, forebay or lagoon), so probably labelled right;
     a quick look confirms which lake the label means.

A dam whose "pool" is under 100 flat pixels is skipped: on a reservoir that isn't
hydro-flattened in the tiles the most common flat value is a puddle, not the lake.
Entries in more than one tier are listed under the first that applies (D, A, L, B, C).
"""
import json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GENERIC = set("""dam dams lake lakes reservoir res no number site structure pond ponds main north south east west
upper lower dike levee saddle auxiliary the of and creek river fork branch trib tributary to a in at on
mill county state park recreation area watershed project subwatershed wildlife fish site""".split())


def words(s):
    return {w for w in re.findall(r"[a-z]{3,}", (s or "").lower()) if w not in GENERIC}


MIN_POOL_PX = 100
LOWER_LAKE_PX = 1500


def tier(e, b):
    if not b or b.get("pool") is None or "error" in b or (b.get("pool_px") or 0) < MIN_POOL_PX:
        return None
    pool, camp, water = b["pool"], b["camp"], b.get("water")
    if water is not None and (b.get("water_m") or 0) <= 300 and camp < water - 3 and (b.get("water_px") or 0) >= 200:
        return "D"
    if not camp < pool - 3:
        return None
    own = bool((words(b.get("dam")) | words(b.get("river"))) & (words(e["name"]) | words(e.get("note"))))
    tail = b.get("downstream") or (water is not None and water < pool - 3)
    if own and tail:
        return "L" if (b.get("water_px") or 0) >= LOWER_LAKE_PX else "A"
    if own:
        return "B"
    return "C"


def main():
    flags = json.load(open(os.path.join(HERE, "flags.json")))
    cg = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
    rows = []
    for r in flags:
        e = cg.get(r["id"])
        if not e:
            continue
        best = None
        for b in r["dams"]:
            t = tier(e, b)
            if t and (best is None or "DALBC".index(t) < "DALBC".index(best[0])):
                best = (t, b)
        if best:
            rows.append((best[0], r, best[1]))
    cnt = Counter(t for t, _, _ in rows)
    print(len(flags), "screened;", dict(sorted(cnt.items())))
    out = ["# Dam screen review tiers", "",
           f"{len(flags)} US lakefront/lakeview entries with a dam nearby were screened "
           f"(screen.py); {len(rows)} are flagged. Tiers are defined in tiers.py.", ""]
    for t in "DALBC":
        sel = sorted([x for x in rows if x[0] == t], key=lambda x: (x[1]["state"], x[1]["id"]))
        out += [f"## Tier {t} ({len(sel)})", "",
                "| id | state | name | stored | dam | dam m | pool | camp | nearest water |",
                "|---|---|---|---|---|---|---|---|---|"]
        for _, r, b in sel:
            out.append(f"| {r['id']} | {r['state']} | {r['name']} | {r['waterfront']} | {b.get('dam')} | "
                       f"{b.get('dam_m')} | {b['pool']} | {b['camp']} | {b.get('water')} |")
        out.append("")
    open(os.path.join(HERE, "tiers.md"), "w").write("\n".join(out))


if __name__ == "__main__":
    main()
