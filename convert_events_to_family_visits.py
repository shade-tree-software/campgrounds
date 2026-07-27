#!/usr/bin/env python3
"""Convert plain events near a family location into family visits.

Events logged before the family-visit feature existed (or just entered as
ordinary events) sit at a relative's address with `family_id: null`, so they
render as gold event stars rather than red house markers and get the full event
edit form instead of the simplified one. This retrofits them: it finds every
event within a radius of a `kind: "family"` entry and links it, producing
exactly what the "Add Family Visit" button would have.

Dry run by default — nothing is written without --apply, and --apply takes a
timestamped backup of trips.json first (that file is gitignored, so there is no
other undo).

  ./convert_events_to_family_visits.py --family "Papa & Bonnie's Place on Tidy Island"
  ./convert_events_to_family_visits.py --family "..." --apply

Run it where the data lives. `sync-from-pa.sh` only PULLS, so a local edit never
reaches the live site and is overwritten by the next sync — on a PythonAnywhere
deployment, run this there.
"""

import argparse
import json
import math
import os
import shutil
import sys
import time

DEFAULT_RADIUS_FT = 1000.0


def haversine_ft(lat1, lng1, lat2, lng2):
    r_ft = 3958.7613 * 5280
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lng2 - lng1) * p / 2) ** 2)
    return 2 * r_ft * math.asin(math.sqrt(a))


def parse_latlng(value):
    try:
        lat, lng = (float(x) for x in str(value).split(","))
        return lat, lng
    except (ValueError, AttributeError):
        return None


def find_family(entries, name=None, family_id=None):
    families = [e for e in entries if e.get("kind") == "family"]
    if family_id is not None:
        match = [e for e in families if e.get("id") == family_id]
        if not match:
            sys.exit(f"error: no kind:'family' entry with id {family_id}.\n"
                     + _family_listing(families))
        return match[0]
    wanted = (name or "").strip().lower()
    match = [e for e in families if (e.get("name") or "").strip().lower() == wanted]
    if len(match) == 1:
        return match[0]
    if not match:
        sys.exit(f"error: no kind:'family' entry named {name!r}.\n"
                 + _family_listing(families))
    # Names are not unique in this database by design, so say so rather than
    # silently linking to whichever came first.
    sys.exit(f"error: {len(match)} family entries are named {name!r} "
             f"(ids {', '.join(str(m['id']) for m in match)}). Use --family-id.")


def _family_listing(families):
    lines = ["  known family entries:"]
    for f in sorted(families, key=lambda e: e.get("id", 0)):
        lines.append(f"    id={f.get('id')}  {f.get('name')!r}  {f.get('location')}")
    return "\n".join(lines)


def family_visit_location(fam):
    """The coordinates "Add Family Visit" would store on the event.

    Mirrors familyVisitCoordsById() in static/trip-detail/timeline.js: the
    driveway wins when present, so the event marker doesn't sit exactly under
    the red house marker.
    """
    return fam.get("driveway_location") or fam.get("location")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--family", help="Name of the kind:'family' entry to link to.")
    g.add_argument("--family-id", type=int, help="Its id, if the name is ambiguous.")
    ap.add_argument("--radius-ft", type=float, default=DEFAULT_RADIUS_FT,
                    help=f"How near counts as 'at' the family location (default {DEFAULT_RADIUS_FT:.0f}).")
    ap.add_argument("--trips", default="trip_data/trips.json")
    ap.add_argument("--campgrounds", default="campgrounds.json")
    ap.add_argument("--rename", action="store_true",
                    help="Also set each event's name to the family label. Off by "
                         "default because Add Family Visit keeps a custom name — "
                         "it only auto-fills a blank one or one that already "
                         "matched a family label.")
    ap.add_argument("--include-waypoints", action="store_true",
                    help="Also convert waypoints. Off by default: a waypoint is a "
                         "brief stop, and one that merely passes the house isn't a visit.")
    ap.add_argument("--force", action="store_true",
                    help="Also relink events already pointing at a DIFFERENT family.")
    ap.add_argument("--apply", action="store_true", help="Write the change (default: dry run).")
    args = ap.parse_args()

    with open(args.campgrounds, encoding="utf-8") as f:
        entries = json.load(f)
    fam = find_family(entries, args.family, args.family_id)
    fam_coords = parse_latlng(fam.get("location"))
    if not fam_coords:
        sys.exit(f"error: family entry {fam.get('id')} has no usable location.")
    target_location = family_visit_location(fam)

    with open(args.trips, encoding="utf-8") as f:
        trips = json.load(f)

    hits, already, conflicts, skipped_wp = [], [], [], []
    for trip in trips:
        for idx, ev in enumerate(trip.get("events", [])):
            coords = parse_latlng(ev.get("location"))
            if not coords:
                continue
            dist = haversine_ft(fam_coords[0], fam_coords[1], *coords)
            if dist > args.radius_ft:
                continue
            row = (trip, idx, ev, dist)
            if ev.get("family_id") == fam["id"]:
                already.append(row)
            elif ev.get("family_id") is not None and not args.force:
                conflicts.append(row)
            elif ev.get("waypoint") and not args.include_waypoints:
                skipped_wp.append(row)
            else:
                hits.append(row)

    print(f"Family: id={fam['id']} {fam['name']!r}")
    print(f"        location {fam.get('location')}"
          + (f"  driveway {fam['driveway_location']}" if fam.get("driveway_location") else ""))
    print(f"        events within {args.radius_ft:.0f} ft will be linked; "
          f"they will be stored at {target_location}")
    print()

    for label, rows in (("already linked — skipping", already),
                        ("linked to a DIFFERENT family — skipping (use --force)", conflicts),
                        ("waypoints — skipping (use --include-waypoints)", skipped_wp)):
        if rows:
            print(f"{len(rows)} {label}:")
            for trip, idx, ev, dist in sorted(rows, key=lambda r: (r[0]["id"], r[1])):
                print(f"   trip {trip['id']:>3} event[{idx:>2}] {ev.get('date')}  "
                      f"{dist:>4.0f} ft  {ev.get('name')!r}")
            print()

    if not hits:
        print("Nothing to convert.")
        return

    print(f"{len(hits)} event(s) to convert:")
    for trip, idx, ev, dist in sorted(hits, key=lambda r: (r[0]["id"], r[1])):
        rename = " → name " + repr(fam["name"]) if args.rename else ""
        print(f"   trip {trip['id']:>3} event[{idx:>2}] {ev.get('date')}  "
              f"{dist:>4.0f} ft  {ev.get('name')!r}{rename}")

    if not args.apply:
        print("\nDry run — nothing written. Re-run with --apply.")
        return

    # Back up first: trip_data/ is gitignored, so this is the only undo.
    backup = f"{args.trips}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(args.trips, backup)

    for trip, idx, ev, _ in hits:
        ev["family_id"] = fam["id"]
        if target_location:
            ev["location"] = target_location
        if args.rename:
            ev["name"] = fam["name"]
        # A family visit is a destination, never a drive-past.
        ev["waypoint"] = False

    # Temp file + atomic replace, and ensure_ascii=False to match the app's
    # writer — otherwise every accented character in the file gets re-escaped
    # and the diff churns.
    tmp = args.trips + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(trips, f, indent=2, ensure_ascii=False)
    os.replace(tmp, args.trips)

    print(f"\nConverted {len(hits)} event(s). Backup: {backup}")
    print("Restart the app (or hard-refresh) to see the red house markers.")


if __name__ == "__main__":
    main()
