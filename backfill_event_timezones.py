#!/usr/bin/env python3
"""Stamp an IANA `tz` on every event that has coordinates but no zone.

Events are ordered by their true instant rather than by wall clock (see the
"Event ordering across timezones" notes in trips.py), which needs to know what
zone each stored `time` is in. New events get that stamped at write time by
`_stamp_event_timezone` in ekko_trips_app.py; this backfills the ones written
before the field existed.

Without it the fix is inert on historical trips: `reference_timezone()` returns
"" for a trip where nothing carries a zone, every item gets the same constant
offset, and the ordering collapses back to the old naive sort.

What it does NOT do is re-sort the stored `events` array. That array's index is
what photo directories are keyed on, so re-ordering it means moving photos —
`add_event`/`update_event` already do that safely through
`_remap_indices_after_sort`, and letting it happen there on the next edit keeps
this script out of the photo library entirely. Display order does not wait for
it: the timeline sorts independently on every load.

Dry-run by default. Requires `timezonefinder` (the same optional dependency the
app's `_tz_for_coord` uses).

    python3 backfill_event_timezones.py           # report only
    python3 backfill_event_timezones.py --apply   # write, after a backup
"""
import argparse
import json
import os
import shutil
import sys
from collections import Counter
from datetime import datetime

import trips

TRIPS_JSON = trips.TRIPS_JSON


def _coords(event):
    """(lat, lng) from an event's "lat,lng" location string, or None."""
    loc = (event.get("location") or "").strip()
    if not loc:
        return None
    try:
        lat, lng = (float(x) for x in loc.split(",")[:2])
    except (ValueError, TypeError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None
    return lat, lng


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the changes (default: report only)")
    ap.add_argument("--trip", type=int, action="append", dest="only_trips",
                    metavar="ID", help="limit to this trip id (repeatable)")
    ap.add_argument("--restamp", action="store_true",
                    help="also recompute zones already present")
    args = ap.parse_args()

    try:
        from timezonefinder import TimezoneFinder
    except ImportError:
        sys.exit("error: timezonefinder is not installed in this interpreter.\n"
                 "       pip install timezonefinder  (or run this on PA)")
    finder = TimezoneFinder()

    with open(TRIPS_JSON, encoding="utf-8") as f:
        raw = json.load(f)

    stamped = skipped_no_coords = already = failed = 0
    multi = []

    for t in raw:
        if args.only_trips and t.get("id") not in args.only_trips:
            continue
        zones = Counter()
        for e in t.get("events", []):
            existing = e.get("tz") or ""
            if existing and not args.restamp:
                already += 1
                zones[existing] += 1
                continue
            pt = _coords(e)
            if pt is None:
                skipped_no_coords += 1
                continue
            tz = finder.timezone_at(lat=pt[0], lng=pt[1])
            if not tz:
                failed += 1
                continue
            if tz != existing:
                stamped += 1
            e["tz"] = tz
            zones[tz] += 1

        # Report on the ABBREVIATION, matching how `_make_trip` decides whether
        # to label times at all: two zone names that print the same three
        # letters are not a distinction a reader can act on.
        abbrs = set()
        for e in t.get("events", []):
            a = trips.tz_abbrev(e.get("date"), e.get("time"), e.get("tz"))
            if a:
                abbrs.add(a)
        if len(abbrs) > 1:
            multi.append((t.get("id"), sorted(abbrs), dict(zones)))

    print(f"stamped:            {stamped}")
    print(f"already had a zone: {already}")
    print(f"no coordinates:     {skipped_no_coords}")
    print(f"lookup failed:      {failed}")
    print()
    if multi:
        print(f"{len(multi)} trip(s) span more than one zone "
              f"(their times will now carry a label):")
        for tid, abbrs, zones in multi:
            print(f"  trip {tid}: {', '.join(abbrs)}")
    else:
        print("no trip spans more than one zone")

    if not args.apply:
        print("\ndry run — nothing written. Re-run with --apply.")
        return

    if not stamped:
        print("\nnothing to write.")
        return

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"{TRIPS_JSON}.bak-{stamp}"
    shutil.copy2(TRIPS_JSON, backup)
    tmp = TRIPS_JSON + ".tmp"
    # indent=2 matches _save_trips so the diff stays to the added lines.
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2)
    # Re-read before replacing: a malformed write must not be able to land on
    # top of the only copy of the trip database.
    with open(tmp, encoding="utf-8") as f:
        json.load(f)
    os.replace(tmp, TRIPS_JSON)
    print(f"\nwrote {TRIPS_JSON} (backup: {os.path.basename(backup)})")


if __name__ == "__main__":
    main()
