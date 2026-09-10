#!/usr/bin/env python3
"""Resolve every located thing in the library to the town a person would name.

Writes `trip_data/place_context.json`: {"<lat>,<lng>": {...}}, keyed by the
coordinate rounded to 4 decimal places (about 11 m — finer than any campground
pin is accurate, coarse enough that the same place written twice hits one key).

WHY A SIDE FILE, NOT A FIELD ON THE RECORD
------------------------------------------
The answer is *derived* — from a coordinate and a gazetteer, both of which can
be re-read at any time — so storing it on the trip would mean a data migration
for something regenerable, and would overwrite `locale` values that were typed
by hand. Keyed by coordinate it is also shared: the campground stayed at on
four trips is resolved once, and moving a pin invalidates exactly that one
entry by simply not matching any more, which falls back to the stored `locale`.

Both consumers read this same file, so a trip page and its write-up cannot
disagree about where something is:
  - `trips._make_trip` materializes `where_label` on every timeline item
  - `process_rollups.day_dossier` puts it in the dossier as `where`

Run after adding trips, or after moving a pin:

    python backfill_place_context.py            # report what would change
    python backfill_place_context.py --apply
"""

import argparse
import json
import os
import sys

import nearest_town

HERE = os.path.dirname(os.path.abspath(__file__))
TRIPS_FILE = os.path.join(HERE, "trip_data", "trips.json")
OUT_FILE = os.path.join(HERE, "trip_data", "place_context.json")


def coord_key(lat, lng):
    return f"{round(float(lat), 4)},{round(float(lng), 4)}"


def _parse(value):
    if not value or "," not in str(value):
        return None
    try:
        lat, lng = [float(x) for x in str(value).split(",")[:2]]
    except ValueError:
        return None
    return lat, lng


def collect_coords(trips, locations):
    """Every coordinate the app draws or describes, deduped."""
    out = {}
    for trip in trips:
        for stay in trip.get("stays", []):
            pos = _parse(stay.get("campsite_location"))
            if pos is None:
                cg = locations.get(stay.get("campground_id")) or {}
                pos = _parse(cg.get("driveway_location") or cg.get("location"))
            if pos:
                out[coord_key(*pos)] = pos
        for evt in trip.get("events", []):
            pos = _parse(evt.get("location"))
            if pos:
                out[coord_key(*pos)] = pos
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the file")
    ap.add_argument("--rebuild", action="store_true",
                    help="recompute every key, not just the missing ones")
    args = ap.parse_args()

    sys.path.insert(0, HERE)
    from trips import _load_locations_by_id

    with open(TRIPS_FILE) as fh:
        raw = json.load(fh)
    trips = raw["trips"] if isinstance(raw, dict) else raw
    coords = collect_coords(trips, _load_locations_by_id())

    existing = {}
    if os.path.exists(OUT_FILE) and not args.rebuild:
        with open(OUT_FILE) as fh:
            existing = json.load(fh)

    todo = {k: v for k, v in coords.items() if k not in existing}
    print(f"{len(coords):,} distinct coordinates, {len(todo):,} to resolve")
    if todo:
        count = nearest_town.load()
        if not count:
            print(f"No gazetteer at {nearest_town.GAZETTEER_FILE} — it ships with "
                  "the repo, so a clone should have it; rebuild with "
                  "build_gazetteer.py --apply.", file=sys.stderr)
            return 1
        print(f"loading gazetteer ({count:,} places)…")

    out = dict(existing)
    named = near = nothing = 0
    for key, (lat, lng) in todo.items():
        hit = nearest_town.nearest_town(lat, lng)
        label = nearest_town.describe(lat, lng)
        if not hit:
            nothing += 1
            out[key] = {"label": ""}
            continue
        (named if hit["inside"] else near)
        if hit["inside"]:
            named += 1
        else:
            near += 1
        out[key] = {"label": label, "name": hit["name"], "state": hit["state"],
                    "miles": hit["miles"], "direction": hit["direction"],
                    "inside": hit["inside"]}
    # Drop keys for coordinates nothing points at any more (a moved pin).
    stale = [k for k in out if k not in coords]
    for k in stale:
        del out[k]

    print(f"  in a town {named}   nearby {near}   nothing worth naming {nothing}"
          + (f"   dropped {len(stale)} stale" if stale else ""))
    if not args.apply:
        for key in list(todo)[:10]:
            print(f"   {key:24s} {out[key].get('label','')!r}")
        print("\n(dry run — pass --apply to write)")
        return 0

    tmp = OUT_FILE + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, ensure_ascii=False)
    os.replace(tmp, OUT_FILE)
    print(f"wrote {OUT_FILE} ({len(out):,} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
