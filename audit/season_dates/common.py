"""Shared write path for the agency-by-agency season pass (2026-10-20).

Each state script holds DECISIONS = {id: (season, source)} read by hand from the
agency's own pages, and calls run(DECISIONS). Writes go through
campground_schema.apply_update, which validates before it mutates. An entry whose
season already came from anywhere but note prose is left alone (a person or the
rec.gov calendar outranks this pass); a note-derived one is replaced, since the
agency page is the better authority; so is one this pass wrote earlier the same day
from the same source, so a decision can be corrected by re-running. Dry run unless
--apply.

Approximate edges (the convention the state:VA row set): an agency's "mid-April" is
written 04-15, "early" opens on the 1st and closes on the 7th, "late" opens on the 20th
and closes on the month's last day, a bare month is its whole month, and a floating
weekday rule ("second Friday in April") takes its widest span. The note then quotes the
agency's wording, so the stored day is never mistaken for a published one. Notes do not
render in the popup, which is why the dates are written at all: a note-only season shows
the reader nothing but "seasonal".
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

CG = os.path.join(ROOT, "campgrounds.json")
DAY = "2026-10-20"


def run(decisions, extra=None):
    """decisions: {id: (season dict, source)}; extra: {id: {group: value, ...}} for
    other groups (status) written alongside, each with its own provenance source
    under the key "_sources"."""
    cg = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in cg}
    wrote = skipped = 0
    for i, (season, source) in decisions.items():
        e = by[i]
        prov = (e.get("provenance") or {}).get("season") or {}
        redo = prov.get("checked") == DAY and prov.get("source") == source
        if e.get("season") and prov.get("source") != "note prose" and not redo:
            print(f"  skip {i} {e['name'][:50]}: season from {prov.get('source', '?')[:50]}")
            skipped += 1
            continue
        update = {"season": None} if e.get("season") else {}
        cs.apply_update(e, update)
        cs.apply_update(e, {"season": season, "provenance": {
            "season": {"source": source, "checked": DAY, "method": "manual"}}})
        wrote += 1
        print(f"  {i} {e['name'][:50]}: {json.dumps(e['season'], ensure_ascii=False)[:150]}")
    for i, groups in (extra or {}).items():
        groups = dict(groups)
        sources = groups.pop("_sources")
        cs.apply_update(by[i], dict(groups, provenance={
            g: {"source": sources[g], "checked": DAY, "method": "manual"} for g in groups}))
        print(f"  {i} {by[i]['name'][:50]}: {json.dumps(groups, ensure_ascii=False)[:150]}")
    print(f"{wrote} seasons, {skipped} skipped, {len(extra or {})} other")
    if "--apply" in sys.argv:
        with open(CG, "w", encoding="utf-8") as f:
            json.dump(cg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("written")
