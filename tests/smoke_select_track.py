"""Smoke-test for _select_track_per_day on real trip data.

Not a unit test — hits the live timeline API for both primary and alt
tids, then runs the per-day selector and prints what it picked for
each day of the trip. Read-only: doesn't modify trips.json or the
track cache.

Usage (from project root, with .env present):

    python -m tests.smoke_select_track <trip_id> [<trip_id> ...]

Example:

    python -m tests.smoke_select_track 66

If no trip ids are given, defaults to a small set of recent trips.

Requires TIMELINE_API_TOKEN, TIMELINE_TID, TIMELINE_TID_ALT in env or
.env. If TIMELINE_TID_ALT is unset, the script will tell you so and
exit — there's nothing for the selector to choose between.
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_dotenv():
    """Minimal .env loader so we don't depend on python-dotenv."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            # Support `export KEY=VALUE` shell-style entries (which is how
            # this project's .env is written).
            if line.startswith("export "):
                line = line[len("export "):]
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)


_load_dotenv()


from ekko_trips_app import (  # noqa: E402  (after env load)
    _fetch_timeline_points,
    _enrich_with_timezone,
    _select_track_per_day,
    parse_trips,
    enrich_trip_locations,
    _map_config,
)


def _anchors_for_trip(trip):
    """Stay coords + event coords, skipping items without lat/lng."""
    anchors = []
    for s in trip.get("stays", []):
        if s.get("lat") is not None and s.get("lng") is not None:
            anchors.append((s["lat"], s["lng"]))
    for e in trip.get("events", []):
        if e.get("lat") is not None and e.get("lng") is not None:
            anchors.append((e["lat"], e["lng"]))
    return anchors


def _smoke_one(trip_id, token, primary_tid, alt_tid):
    trips = parse_trips()
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        print(f"trip {trip_id}: not found")
        return
    if not trip.get("start") or not trip.get("end"):
        print(f"trip {trip_id}: empty trip, skipping")
        return
    enrich_trip_locations(trip)
    home, _family = _map_config()

    start_dt = datetime.fromisoformat(trip["start"]) - timedelta(days=1)
    end_dt = datetime.fromisoformat(trip["end"]) + timedelta(days=2)
    from_ts = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_ts = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        p_pts = _fetch_timeline_points(primary_tid, token, from_ts, to_ts)
    except Exception as e:
        print(f"trip {trip_id}: primary fetch failed: {e}")
        return
    try:
        a_pts = _fetch_timeline_points(alt_tid, token, from_ts, to_ts)
    except Exception as e:
        print(f"trip {trip_id}: alt fetch failed: {e}")
        return

    _enrich_with_timezone(p_pts)
    _enrich_with_timezone(a_pts)

    anchors = _anchors_for_trip(trip)
    overrides = trip.get("tid_overrides") or {}
    chosen, choices = _select_track_per_day(
        p_pts, a_pts, anchors, home,
        trip["start"], trip["end"],
        tid_overrides=overrides,
    )

    # Per-day report.
    label = trip.get("summary") or trip.get("trip_note") or "(no summary)"
    print(f"\n── trip {trip_id}: {trip['start']} → {trip['end']} — {label}")
    print(f"   anchors: {len(anchors)} stay/event coords, "
          f"primary={len(p_pts)} pings, alt={len(a_pts)} pings, "
          f"chosen={len(chosen)}")
    # Bucket each tid's pings by day so we can show counts alongside the choice.
    from ekko_trips_app import _local_date_of_ping
    p_count = {}
    a_count = {}
    for p in p_pts:
        d = _local_date_of_ping(p)
        if d:
            p_count[d] = p_count.get(d, 0) + 1
    for p in a_pts:
        d = _local_date_of_ping(p)
        if d:
            a_count[d] = a_count.get(d, 0) + 1
    for day in sorted(choices):
        marker = "★" if choices[day].startswith("override") else " "
        print(f"   {marker} {day}: {choices[day]:<22} "
              f"(primary={p_count.get(day, 0):3d}, alt={a_count.get(day, 0):3d})")


def main():
    token = os.environ.get("TIMELINE_API_TOKEN")
    primary_tid = os.environ.get("TIMELINE_TID")
    alt_tid = os.environ.get("TIMELINE_TID_ALT")
    if not token or not primary_tid:
        print("ERROR: TIMELINE_API_TOKEN and TIMELINE_TID must be set.")
        sys.exit(2)
    if not alt_tid:
        print("ERROR: TIMELINE_TID_ALT is not set — nothing for the "
              "selector to choose between. Set it and rerun.")
        sys.exit(2)

    ids = sys.argv[1:]
    if ids:
        try:
            trip_ids = [int(x) for x in ids]
        except ValueError:
            print("ERROR: trip ids must be integers")
            sys.exit(2)
    else:
        # Default: trip 66 (mentioned in the conversation as having
        # bad_track_windows + relocations) plus a couple recent ones.
        trip_ids = [66]

    for tid in trip_ids:
        _smoke_one(tid, token, primary_tid, alt_tid)


if __name__ == "__main__":
    main()
