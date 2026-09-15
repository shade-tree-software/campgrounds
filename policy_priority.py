#!/usr/bin/env python3
"""Rank the registry rows still worth writing, by NIGHTS SLEPT.

`campground_policies.json` buys coverage at roughly 50:1 — one researched row
answers for every campground under that agency (docs/campground-schema.md §5).
Which row to write next is therefore the whole question, and entry count is the
wrong way to ask it: the database is nationwide, the trips are not. Joining
`trip_data/trips.json` against the location database by nights actually slept is
what put PA/MD/VA ahead of MI/CA in the first pass.

Read-only. Prints two rankings and touches nothing.

**Two traps, both of which made an earlier version of this quietly wrong:**

* `trips.is_home_stay()` reads `stay["place"]`, a display field that only
  `parse_trips()` materializes. Run it over raw `trips.json` records and it
  returns False for every one of them, putting the home nights into the
  denominator and a street address at the top of the ranking.
* A `kind: "family"` entry has no `ownership`, so the driveways the EKKO parks
  in — 47 nights, the single largest bucket in the library — land in a bogus
  `NO-OWNERSHIP` row unless they are excluded outright. They have no agency and
  never will.

**The nights signal was spent as of 2026-09-15**, which is the other reason this
prints both rankings. Every uncovered row above the best remaining agency is
`private:*` / `hipcamp:*` / `local:*`, and doc §5 says not to research those:
there is no agency to inherit from, FCFS is the norm rather than a system, and
the right answer at 5pm on the road is the phone number. They are listed, marked
`skip`, rather than filtered out — a row hidden is one nobody can reconsider.
So the agency ranking below the nights table is now the operative one.

Works on a host with no trip data (a fresh clone has `campgrounds.json` from git
and nothing else): the nights half is skipped with a note and the entry ranking
still prints.
"""

import argparse
import collections
import datetime
import json
import os
import sys

import campground_schema
import trips

HERE = os.path.dirname(os.path.abspath(__file__))
POLICIES = os.path.join(HERE, "campground_policies.json")
CAMPGROUNDS = os.path.join(HERE, "campgrounds.json")
FAMILY = os.path.join(HERE, "trip_data", "family.json")
TRIPS = os.path.join(HERE, "trip_data", "trips.json")

# Ownerships that name an agency whose policy can be researched and inherited.
# Everything else is a private operator, a booking platform, or a county that is
# one of hundreds — see the module docstring and doc §5.
AGENCY = ("state", "provincial", "federal")


def _load(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        if default is None:
            raise
        return default


def _nights(stay):
    """Nights in one stay record, from the stored count or the dates."""
    n = stay.get("nights")
    if isinstance(n, int) and n > 0:
        return n
    try:
        start = datetime.date.fromisoformat(stay["start"])
        end = datetime.date.fromisoformat(stay["end"])
    except (KeyError, TypeError, ValueError):
        return 0
    return max((end - start).days, 0)


def _covering_ref(entry, registry):
    """The registry row this entry already inherits from, if any."""
    return next((r for r in campground_schema.policy_refs(entry) if r in registry),
                None)


def _candidate_ref(entry):
    """The row that WOULD cover this entry — the most specific one it names."""
    refs = campground_schema.policy_refs(entry)
    return refs[0] if refs else "NO-OWNERSHIP"


def count_nights(registry, by_id):
    """Join the trip library against the location database by nights slept."""
    uncovered = collections.Counter()
    places = collections.defaultdict(set)
    covered = collections.Counter()
    tally = collections.Counter()

    for trip in trips.parse_trips():          # parsed: stays carry `place`
        for stay in trip.get("stays", []):
            n = _nights(stay)
            if trips.is_home_stay(stay):      # needs `place`, hence parse_trips
                tally["home"] += n
                continue
            entry = by_id.get(stay.get("campground_id"))
            if entry is None:
                tally["free_text"] += n       # a hotel, an Airbnb, a driveway
                continue
            if entry.get("kind") == "family":
                tally["family"] += n          # no agency, and never will have
                continue
            tally["agency_backed"] += n
            ref = _covering_ref(entry, registry)
            if ref:
                covered[ref] += n
                continue
            key = _candidate_ref(entry)
            uncovered[key] += n
            places[key].add(entry["id"])
    return tally, covered, uncovered, places


def count_entries(registry, campgrounds):
    """Database entries per candidate row, counting only uncovered ones."""
    counts = collections.Counter()
    for entry in campgrounds:
        if entry.get("kind") != "campground":
            continue
        if _covering_ref(entry, registry):
            continue
        counts[_candidate_ref(entry)] += 1
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--top", type=int, default=15,
                    help="rows to print in each ranking (default 15)")
    ap.add_argument("--agency-only", action="store_true",
                    help="drop the rows doc §5 says not to research")
    args = ap.parse_args(argv)

    registry = _load(POLICIES)
    campgrounds = _load(CAMPGROUNDS)
    locations = campgrounds + _load(FAMILY, default=[])
    by_id = {c["id"]: c for c in locations}
    entries = count_entries(registry, campgrounds)

    total_entries = sum(1 for c in campgrounds if c.get("kind") == "campground")
    print(f"registry: {len(registry)} rows covering "
          f"{total_entries - sum(entries.values())} of {total_entries} entries "
          f"({(total_entries - sum(entries.values())) / total_entries:.1%})")

    if not os.path.exists(TRIPS):
        print(f"\nno {os.path.relpath(TRIPS, HERE)} on this host — nights ranking "
              "skipped (bring trip data over with ./sync-from-pa.sh or restore.sh)")
        uncovered, places = collections.Counter(), {}
    else:
        tally, covered, uncovered, places = count_nights(registry, by_id)
        agency_nights = tally["agency_backed"]
        cov = sum(covered.values())
        share = f" ({cov / agency_nights:.1%})" if agency_nights else ""
        print(f"\ncamping nights (excluding {tally['home']} at home): "
              f"{agency_nights + tally['family'] + tally['free_text']}")
        print(f"  at an agency-backed campground : {agency_nights}")
        print(f"    covered by a registry row    : {cov}{share}")
        print(f"    NOT covered                  : {sum(uncovered.values())}")
        print(f"  family driveways (no agency)   : {tally['family']}")
        print(f"  free text, no database entry   : {tally['free_text']}")

    if uncovered:
        scoped = " (agency rows only)" if args.agency_only else ""
        print(f"\nuncovered, by NIGHTS SLEPT{scoped}:")
        print(f"  {'candidate row':<26}{'nights':>7}{'places':>8}{'entries':>9}  note")
        shown = 0
        for key, n in uncovered.most_common():
            if shown >= args.top:
                break
            agency = key.split(":", 1)[0] in AGENCY
            if args.agency_only and not agency:
                continue
            note = "" if agency else "skip — §5: no agency to inherit from"
            print(f"  {key:<26}{n:>7}{len(places.get(key, ())):>8}"
                  f"{entries.get(key, 0):>9}  {note}")
            shown += 1

    print("\nuncovered AGENCY rows, by DATABASE ENTRIES:")
    print(f"  {'candidate row':<26}{'entries':>9}{'nights':>8}")
    shown = 0
    for key, n in entries.most_common():
        if key.split(":", 1)[0] not in AGENCY:
            continue
        if shown >= args.top:
            break
        print(f"  {key:<26}{n:>9}{uncovered.get(key, 0):>8}")
        shown += 1
    remaining = {k: v for k, v in entries.items() if k.split(":", 1)[0] in AGENCY}
    print(f"  ... {sum(remaining.values())} entries across {len(remaining)} "
          "agency rows remain")
    return 0


if __name__ == "__main__":
    sys.exit(main())
