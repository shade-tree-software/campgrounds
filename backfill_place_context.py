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


def road_coords(trip):
    """Where the RV was when this trip's road photos were taken.

    Road photos have no stay or event to inherit a location from — that is the
    point of them — so their position comes from the trip's own GPS track,
    matched on the photo's EXIF timestamp. Resolved here rather than live in
    the request so the web process never has to load the 177k-place gazetteer.
    """
    import ekko_trips_app as A
    days = A._road_days(trip["id"])
    if not days:
        return []
    track = A._load_trip_track_for_detection(trip["id"])
    out = []
    for day in days:
        photo_dir = A._road_photo_dir(trip["id"], day)
        for fname in sorted(os.listdir(photo_dir)):
            if not A._allowed_file(fname):
                continue
            taken = A._photo_date_taken(os.path.join(photo_dir, fname))
            pos = A._road_photo_position(track, taken)
            if pos:
                out.append(pos)
    return out


def collect_coords(trips, locations):
    """Every coordinate the app draws or describes, deduped."""
    out = {}
    for trip in trips:
        for pos in road_coords(trip):
            out[coord_key(*pos)] = pos
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
    ap.add_argument("--only", nargs="+", metavar="TRIP_ID",
                    help="resolve only these trips, and write (this is the "
                         "path the app takes after a road photo is uploaded)")
    args = ap.parse_args()
    if args.only:
        args.apply = True

    sys.path.insert(0, HERE)
    from trips import _load_locations_by_id

    with open(TRIPS_FILE) as fh:
        raw = json.load(fh)
    trips = raw["trips"] if isinstance(raw, dict) else raw
    if args.only:
        wanted = {str(t) for t in args.only}
        trips = [t for t in trips if str(t.get("id")) in wanted]
    coords = collect_coords(trips, _load_locations_by_id())

    existing = {}
    if os.path.exists(OUT_FILE) and not args.rebuild:
        with open(OUT_FILE) as fh:
            existing = json.load(fh)

    # A key already resolved to nothing is redone when it has no far answer
    # recorded either — those were written before the far fallback existed and
    # would otherwise stay blank forever, since they are technically present.
    def _stale(k):
        e = existing.get(k)
        return e is None or (not e.get("label") and "far_label" not in e
                             and "far_checked" not in e)

    todo = {k: v for k, v in coords.items() if _stale(k)}
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
        if not hit:
            nothing += 1
            # Nothing qualified under the strict tiers. A far answer is stored
            # ALONGSIDE rather than instead, because only some callers should
            # see it: a road card has no name of its own and is helped by "16
            # miles northeast of Deer Trail", while an overlook names itself
            # and is better left silent. The coordinate cannot know which it
            # is, so it carries both and the caller chooses.
            far = nearest_town.nearest_town(lat, lng, nearest_town.FAR_MILES)
            entry = {"label": "", "far_checked": True}
            if far:
                entry.update(far_label=nearest_town.describe(
                                 lat, lng, nearest_town.FAR_MILES),
                             far_name=far["name"], far_state=far["state"])
            out[key] = entry
            continue
        if hit["inside"]:
            named += 1
        else:
            near += 1
        out[key] = {"label": nearest_town.describe(lat, lng),
                    "name": hit["name"], "state": hit["state"],
                    "miles": hit["miles"], "direction": hit["direction"],
                    "inside": hit["inside"]}
    # Drop keys for coordinates nothing points at any more (a moved pin). Never
    # when --only narrowed the sweep to one trip: every OTHER trip's
    # coordinates would look stale and the file would be gutted.
    stale = [] if args.only else [k for k in out if k not in coords]
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
