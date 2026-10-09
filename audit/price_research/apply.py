#!/usr/bin/env python3
"""Write researched `fees` onto entries (2026-10-09, AWH: find out whether the
dispersed sites with no price info are free).

    python3 audit/price_research/apply.py FINDINGS.json [--apply]

FINDINGS is a list of {"id", "fees": {...}, "source": "<url>"}; every one came
from reading that source, which goes into `provenance.fees` (no `method`: a
research check, not a machine extraction, so it outranks note-derived values
per docs/campground-schema.md §3). Validated through the schema; an entry that
already has `fees`, or whose fees group is manual/reported, is left alone.
Dry run unless --apply.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
import extract_fields as ef     # noqa: E402

TODAY = "2026-10-09"


def main():
    findings = json.load(open(sys.argv[1]))
    apply = "--apply" in sys.argv
    rows = ef.load_rows()
    by_id = {r.get("id"): r for r in rows}
    wrote, skipped = 0, []
    for f in findings:
        entry = by_id.get(f["id"])
        if entry is None or entry.get("fees") or ef.human_verified(entry, "fees"):
            skipped.append(f["id"])
            continue
        cs.apply_update({}, {"fees": f["fees"]})      # raises on a bad value
        if apply:
            prov = dict(entry.get(cs.PROVENANCE) or {})
            prov["fees"] = {"source": f["source"], "checked": TODAY}
            cs.apply_update(entry, {"fees": f["fees"], cs.PROVENANCE: prov})
        wrote += 1
    print(f"{len(findings)} findings, {wrote} {'written' if apply else 'would write'}, "
          f"skipped {skipped or 'none'}")
    if apply:
        tmp = ef.CAMPGROUNDS_JSON + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, ef.CAMPGROUNDS_JSON)


if __name__ == "__main__":
    main()
