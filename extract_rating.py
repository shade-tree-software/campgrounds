#!/usr/bin/env python3
"""Lift the RV Life rating out of `note` prose into the `rating` group.

The rating is structured data that has been stored as English on 80% of the
database — `RV Life 4.5*/$$ (auto 6/2026)`. This moves it into the field that
can be searched and sorted, per docs/campground-schema.md §6, which names it as
the ONE exception to "extraction is additive": everything else a note says stays
in the note, because no vocabulary holds "longer rigs may curb-park".

Dry-run by default. `--apply` backs the file up first.

**Populate liberally, excise conservatively — the two halves are separate.**
There are 595 distinct shapes of this clause across 12,025 mentions, so a single
regex that both reads and removes would be wrong somewhere in the long tail, and
a mangled note is unrecoverable where a duplicated fact is merely untidy. So:
reading uses tolerant token-level patterns and runs on anything it can parse;
removal happens only when the clause is a COMPLETE tail at the end of the note,
matching one exact shape, with nothing else inside it. Anything else keeps its
prose and gets the structured field anyway.

Three traps found in the data, each of which broke an earlier version:

* **A note can mention RV Life twice.** Ouabache Trails Park (id 1349) says
  "(RV Life mis-tagged commercial; it is county-run...)" and THEN carries the
  real "RV Life 4*/$$." tail. Taking the first match reads the prose. Every
  occurrence is parsed and the best one wins.
* **"$" is not always a price tier.** "CAD ~$40/night" and "$50/night" are money.
  A tier is a run of `$` NOT followed by a digit.
* **"not on RV Life" is a finding, not a failure.** 172 entries say it, and
  it means the campground is absent from the directory — different from
  "unrated". Nothing is written for those and the sentence stays put, because
  `rating` has no vocabulary for "not listed" and inventing one to hold a
  negative would be a schema change smuggled in by a data script.

Also left alone: 15 entries using AWH's older "RVLife 9.5/10" notation. That is
a different scale by a different author; mapping 9.5/10 onto a 5-star field
would invent a precision the source never had.
"""

import argparse
import json
import re
import shutil
import sys
import time
from collections import Counter

import campground_schema

CAMPGROUNDS_JSON = "campgrounds.json"

LEAD = re.compile(r'RV\s*Life\b', re.I)
# Money vs tier: "$$" is a tier, "$45" and "~$40/night" are not.
# A money amount always has a digit straight after the sign ("$45", "~$40/night",
# "$4.50"), so excluding a following DIGIT is enough. Excluding a following dot
# as well — which an earlier version did, to guard a "$.50" that never occurs —
# rejected the very common "RV Life 4*/$. --Claude", silently losing the price
# tier on ~700 entries while the star rating parsed fine.
TIER = re.compile(r'(?<![\w$])(\$+)(?!\d)')
# "4.5*", "4★", "5 stars" and the hyphenated "5-star" all appear; so does an
# out-of-five score ("RV Life 4/5, $"). The /5 form is matched separately so it
# cannot be confused with the "(3/4)" price-tier notation or the /10 scale.
STARS = re.compile(r'(\d+(?:\.\d+)?)[-\s]*(?:\*|★|stars?\b)', re.I)
STARS_OF_5 = re.compile(r'(?<![(\d])(\d+(?:\.\d+)?)\s*/\s*5(?![\d/])')
UNRATED = re.compile(r'\bunrated\b', re.I)
CHECKED = re.compile(r'\((?:auto\s*)?(\d{1,2})/(\d{4})\)')
NOT_LISTED = re.compile(r'\bnot\s+(?:on|listed\s+on)\s+RV\s*Life\b', re.I)
# AWH's older notation, and a few "~9/10" variants. A different scale by a
# different author: mapping 9.5/10 onto a 5-star field invents precision.
TEN_SCALE = re.compile(r'RV\s*Life\s*:?\s*~?\s*\d+(?:\.\d+)?\s*/\s*10', re.I)

# The ONLY shapes that may be cut out of a note: a complete clause, at the end,
# holding nothing but rating tokens. Everything optional, order as authored.
CLEAN_TAIL = re.compile(
    r'\s*[(\[]?\s*RV\s*Life\s*:?\s*'
    r'(?:listed\s+but\s+)?'
    r'(?:unrated|\d+(?:\.\d+)?\s*/\s*5|\d+(?:\.\d+)?[-\s]*(?:\*|★|stars?))'
    r'(?:\s*[,/]?\s*(?:price\s*)?\$+(?:\s*\(\d\s*/\s*4\))?)?'
    r'(?:\s*,?\s*\d+\s+reviews?)?'
    r'(?:\s*,?\s*CAD\s*~?\$\d+(?:\.\d+)?\s*/\s*night)?'
    r'(?:\s*\.?\s*\((?:auto\s*)?\d{1,2}/\d{4}\))?'
    r'\s*[.,;)\]]*\s*'
    # The attribution sits INSIDE the brackets on ~535 entries
    # ("[RV Life: 4★, price $$$ (3/4). --Claude]"), so the closing bracket has
    # to be allowed after it or the clause never reaches end-of-note and is
    # (correctly, but needlessly) left alone.
    r'(?:--\s*Claude\s*\.?)?\s*[)\]]?\s*$',
    re.I)


def parse_rating(note):
    """Best rating readable from a note, or None. Never guesses."""
    best = None
    for m in LEAD.finditer(note or ""):
        window = note[m.end():m.end() + 70]
        rating = {}
        st = STARS.search(window) or STARS_OF_5.search(window)
        if st:
            try:
                stars = float(st.group(1))
            except ValueError:
                stars = None
            # A 5-star scale. Anything above it is a different scale (the /10
            # notation) or a typo; either way, not ours to convert.
            if stars is not None and 0 < stars <= 5:
                rating["stars"] = stars
        elif UNRATED.search(window):
            rating["unrated"] = True          # marker only; see below
        tier = TIER.search(window)
        if tier:
            rating["price_tier"] = min(len(tier.group(1)), 4)
        ck = CHECKED.search(window)
        if ck:
            rating["checked"] = f"{int(ck.group(2)):04d}-{int(ck.group(1)):02d}"
        if not rating:
            continue
        score = len(rating)
        if best is None or score > best[0]:
            best = (score, m, rating)
    if best is None:
        return None, None
    _, match, rating = best
    # "unrated" is the directory saying it has no score — that is the absence of
    # a star rating, so nothing is written for it. A price tier alongside it is
    # still real and is kept.
    rating.pop("unrated", None)
    if not rating:
        return None, None
    rating["source"] = "rvlife"
    return rating, match


SIGNED_OFF = re.compile(r'--\s*\w+\s*[\].)]*\s*$')


def excise(note, match):
    """Remove the rating clause if it is a clean complete tail. Else unchanged."""
    tail = CLEAN_TAIL.match(note, match.start())
    if not tail or tail.end() != len(note):
        return note, False
    # Strip an orphaned opening bracket left by a "[RV Life: ...]" clause, which
    # would otherwise dangle at the end of the surviving prose.
    cut = re.sub(r'[\s\[(]+$', '', note[:match.start()])
    # The clause usually carried a "--Claude". Whether that marker belongs to the
    # REMAINING prose or only to the clause being removed is decided by what
    # precedes it: prose already signed by someone else ("--AWH") means the
    # marker was the clause's alone and leaves with it, while unsigned prose was
    # Claude's and keeps its attribution. Getting this backwards leaves notes
    # ending "--AWH --Claude", which reads as two authors with nothing between.
    if cut and re.search(r'--\s*Claude\b', note[match.start():], re.I):
        if not SIGNED_OFF.search(cut):
            cut += " --Claude"
    return cut, True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the file (default: report only)")
    ap.add_argument("--file", default=CAMPGROUNDS_JSON)
    ap.add_argument("--show", type=int, default=6,
                    help="sample rows to print per category")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        entries = json.load(f)

    stats = Counter()
    samples = {}
    changes = 0
    for entry in entries:
        note = entry.get("note") or ""
        if not LEAD.search(note):
            stats["no mention"] += 1
            continue
        if TEN_SCALE.search(note):
            stats["left alone: /10 scale"] += 1
            samples.setdefault("left alone: /10 scale", []).append(entry)
            continue
        rating, match = parse_rating(note)
        if rating is None:
            if NOT_LISTED.search(note):
                key = "left alone: says not listed"
            elif UNRATED.search(note):
                # Listed but scoreless. That is the ABSENCE of a star rating, so
                # nothing is written — `rating` has no vocabulary for it and
                # inventing one to hold a negative would be a schema change
                # smuggled in by a data script.
                key = "left alone: listed but unrated"
            else:
                key = "UNPARSED"
            stats[key] += 1
            samples.setdefault(key, []).append(entry)
            continue

        if entry.get("rating"):
            stats["already has a rating"] += 1
            continue

        new_note, cut = excise(note, match)
        stats["populated + note cleaned" if cut
              else "populated, note left as-is"] += 1
        samples.setdefault("populated + note cleaned" if cut
                           else "populated, note left as-is", []).append(
            (entry, note, new_note, rating))
        # Validate against the same vocabulary the API enforces, so this script
        # cannot write a shape the manage form would then refuse to save.
        staged = {}
        campground_schema.apply_update(staged, {"rating": rating})
        entry["rating"] = staged["rating"]
        if cut:
            entry["note"] = new_note
        changes += 1

    width = max(len(k) for k in stats)
    print(f"{len(entries)} entries")
    for key, count in stats.most_common():
        print(f"  {key:{width}}  {count:6}  {100*count/len(entries):5.1f}%")
    print(f"\n  would change: {changes}")

    for key in ("populated + note cleaned", "populated, note left as-is"):
        rows = samples.get(key, [])[:args.show]
        if not rows:
            continue
        print(f"\n── {key} ──")
        for entry, old, new, rating in rows:
            print(f"  [{entry['id']}] {entry['name'][:44]}")
            print(f"      rating  {rating}")
            if old != new:
                print(f"      note -  ...{old[-72:]!r}")
                print(f"      note +  ...{new[-72:]!r}")
    for key in ("UNPARSED", "left alone: listed but unrated",
                "left alone: says not listed", "left alone: /10 scale"):
        rows = samples.get(key, [])[:args.show]
        if not rows:
            continue
        print(f"\n── {key} ──")
        for entry in rows:
            note = entry.get("note") or ""
            m = LEAD.search(note)
            print(f"  [{entry['id']}] {entry['name'][:38]} :: "
                  f"...{note[max(0, m.start()-30):m.start()+56]!r}")

    if not args.apply:
        print("\nDry run. Nothing written. Re-run with --apply to write.")
        return 0

    backup = f"{args.file}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(args.file, backup)
    with open(args.file, "w", encoding="utf-8") as f:
        # ensure_ascii=False or every em-dash in every note re-escapes and the
        # diff becomes the whole file instead of the entries that changed.
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nWrote {args.file} ({changes} entries changed). Backup: {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
