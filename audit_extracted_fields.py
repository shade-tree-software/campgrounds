#!/usr/bin/env python3
"""Check every field `extract_fields.py` derived against the note it came from.

Reading 24 entries by hand is how the extraction prompt got debugged; it does
not scale to 12,689. This does the part a machine can: it re-reads each derived
value next to its own note and asks whether the note actually supports it.

Two checks, aimed at the two ways an extraction pass goes wrong.

**Numbers that are not in the note.** A hallucinated site count is invisible —
it looks exactly like a real one — so every derived integer is matched against
the digits in its own note. This found the one genuine error in the first
3,675 values: `"15-amp electric only"` stored as `electric: 20`, rounded up to
reach a value the enum holds. It is also noisy in a specific, harmless way, and
the noise is worth understanding before trusting a run: a number spelled out
("Seven rustic sites" -> 7) or converted ("3-week RV max stay" -> 21 nights) is
correct and will be reported. **Read the flagged cases; do not assume a clean
count means clean data, or that a dirty one means bad data.**

**`false` values with nothing behind them.** Doc §2.1: a stored `false` is a
claim somebody looked and there are none, and it is indistinguishable from a
verification forever after. So every derived `false` is checked for a negation
near the relevant word. This check is *deliberately* crude and over-reports,
because the model reads notes better than a regex does — "electric-only" means
no water hookup, "no central toilets" means no flush toilets, "vault toilets
(bring water)" means no potable water, "dump station ~6 blocks away" means no
ON-SITE dump. Every one of those reads as unsupported here and every one is
right. Its value is the ratio and the outliers, not the raw count.

Read-only. Exits non-zero if anything was flagged, so it can gate a run, but
treat the output as a reading list rather than a verdict.

    ./audit_extracted_fields.py              # everything scanned so far
    ./audit_extracted_fields.py --limit 20   # show more examples per finding
"""

import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CAMPGROUNDS_JSON = os.path.join(ROOT, "campgrounds.json")

# Integer fields worth matching against the note's own digits.
NUMERIC = (("sites", "count"), ("sites", "max_rig_ft"),
           ("hookups", "electric"), ("booking", "max_stay_nights"))

# Values that are legitimately absent from the note as digits, because they are
# a reading of a phrase rather than a copy of a number.
NUMERIC_EXEMPT = {("hookups", "electric"): {0},        # "no hookups"
                  ("booking", "max_stay_nights"): {1}}  # "24-hour limit"

# The word each boolean is about, for the negation check.
BOOLEAN_KEYWORD = {
    ("facilities", "showers"): r"shower",
    ("facilities", "flush_toilets"): r"flush",
    ("facilities", "vault_toilets"): r"vault|pit toilet",
    ("facilities", "potable_water"): r"potable|drinking water|water",
    ("facilities", "laundry"): r"laundr",
    ("facilities", "camp_store"): r"store|commissary",
    ("facilities", "wifi"): r"wi-?fi|internet",
    ("hookups", "water"): r"water|hookup|hook-up",
    ("hookups", "sewer"): r"sewer|hookup|hook-up|full.service",
    ("facilities", "dump"): r"dump|sani",
    ("sites", "pull_through"): r"pull.?thr|back.?in",
    ("season", "year_round"): r"year.?round|season|open|clos",
}
NEGATION = (r"(no|not|none|without|lack\w*|absent|closed|unavailable|"
            r"non-?|un|only|seasonal)")
# Phrases that justify a whole group of falses at once.
BLANKET = re.compile(r"no hookups|primitive|non-?electric|rustic|dry camp"
                     r"|electric.only|seasonal|open [a-z]{3,9}[ .-]|clos")


def derived(entry, group):
    """True when this group's values came from the note, not a person or agency."""
    return (entry.get("provenance") or {}).get(group, {}).get("method") == "derived"


def audit(rows, examples):
    findings = collections.Counter()
    totals = collections.Counter()
    shown = collections.defaultdict(list)

    for entry in rows:
        note = entry.get("note") or ""
        digits = set(re.findall(r"\d+", note))
        low = note.lower()

        for group, key in NUMERIC:
            value = (entry.get(group) or {}).get(key)
            if value is None or not derived(entry, group):
                continue
            label = f"number not in note: {group}.{key}"
            totals[label] += 1
            if str(value) in digits or value in NUMERIC_EXEMPT.get((group, key), ()):
                continue
            findings[label] += 1
            if len(shown[label]) < examples:
                shown[label].append((entry.get("id"), value, note))

        for (group, key), keyword in BOOLEAN_KEYWORD.items():
            if (entry.get(group) or {}).get(key) is not False:
                continue
            if not derived(entry, group):
                continue
            label = f"unsupported false: {group}.{key}"
            totals[label] += 1
            near = NEGATION + r"[^.;]{0,45}?(" + keyword + ")"
            if re.search(near, low) or BLANKET.search(low):
                continue
            findings[label] += 1
            if len(shown[label]) < examples:
                shown[label].append((entry.get("id"), False, note))

    return findings, totals, shown


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--limit", type=int, default=3,
                    help="examples to print per finding (default 3)")
    args = ap.parse_args()

    with open(CAMPGROUNDS_JSON, encoding="utf-8") as fh:
        rows = [r for r in json.load(fh) if r.get("note_scan")]

    findings, totals, shown = audit(rows, args.limit)
    print(f"{len(rows):,} scanned entries; "
          f"{sum(totals.values()):,} derived values checked")
    print(f"{sum(findings.values()):,} flagged for reading\n")
    for label, n in findings.most_common():
        print(f"  {label}: {n} of {totals[label]}")
        for cid, value, note in shown[label]:
            print(f"     {cid} = {value!r}")
            print(f"       {note[:150]}")
        print()
    if not findings:
        print("nothing flagged")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
