#!/usr/bin/env python3
"""Write `fees` for campgrounds whose note says the CAMPING is free (2026-10-09).

    python3 audit/free_fees/apply_free.py            # dry run: what would change
    python3 audit/free_fees/apply_free.py --apply

Reads the hand-made decision files beside it (d*.txt, one `id low high` per line,
`-` for a high the note does not state). Every line was decided by reading the
note, not by the regex in candidates.py, which only finds what to read:

- camping itself free (incl. donation-only, a free permit)      -> 0 / 0
- free primitive or off-season, paid hookups or season, price
  stated                                                        -> 0 / that price
- the same with no price stated                                 -> 0 / (absent)
- skipped: free for tents only, "first N nights free", free for
  customers only, "no fee listed", self-contradicting notes,
  and "free" that names an amenity (WiFi, showers, dump)

Why it matters beyond the fee: `campground_schema._moot_agency_keys` drops the
agency's discount defaults (the America the Beautiful senior discount on every
federal campground) only when the entry's OWN fees say $0 at both ends, so a
free campground with no recorded fees showed a discount on nothing.

Never overwrites: an entry that already has any `fees` is left alone, as is a
group whose provenance is manual/reported. The note is never edited.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
import extract_fields as ef     # noqa: E402

TODAY = "2026-10-09"


def decisions():
    out = {}
    for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "d*.txt"))):
        for line in open(path):
            if not line.strip():
                continue
            cid, low, high = line.split()
            fees = {"nightly_low": float(low) if "." in low else int(low)}
            if high != "-":
                fees["nightly_high"] = int(high)
                if int(high) > 0:
                    fees["currency"] = "USD"
            out[int(cid)] = fees
    return out


def main():
    apply = "--apply" in sys.argv
    plan = decisions()
    rows = ef.load_rows()
    by_id = {r.get("id"): r for r in rows}
    wrote = free = ranged = 0
    skipped = []
    for cid, fees in plan.items():
        entry = by_id.get(cid)
        if entry is None or entry.get("fees") or ef.human_verified(entry, "fees"):
            skipped.append(cid)
            continue
        cs.apply_update({}, {"fees": fees})          # vocabulary check; raises on a bad value
        if fees.get("nightly_high") == 0:
            free += 1
        else:
            ranged += 1
        if apply:
            prov = dict(entry.get(cs.PROVENANCE) or {})
            prov["fees"] = {"source": "note prose", "checked": TODAY, "method": "derived"}
            cs.apply_update(entry, {"fees": fees, cs.PROVENANCE: prov})
        wrote += 1
    print(f"{len(plan)} decisions: {free} free, {ranged} free-with-paid-tier; "
          f"{len(skipped)} skipped (already had fees / missing){' ' + str(skipped) if skipped else ''}")
    if apply:
        tmp = ef.CAMPGROUNDS_JSON + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, ef.CAMPGROUNDS_JSON)
        print(f"wrote {wrote}")
    else:
        print("[dry run]")


if __name__ == "__main__":
    main()
