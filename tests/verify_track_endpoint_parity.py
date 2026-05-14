"""Verify the wired-up selector doesn't regress the track endpoint
output on trips where alt-tid had no pings (which is every production
trip as of this change).

Read-only: doesn't modify caches or trip data. Runs the new
api_trip_track inner logic against the existing cache and checks that
the returned ping set is identical to the raw cache contents.

Usage:

    python -m tests.verify_track_endpoint_parity [trip_id ...]

Defaults to scanning every cached trip.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_dotenv():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

from ekko_trips_app import (  # noqa: E402
    parse_trips,
    enrich_trip_locations,
    _select_track_per_day,
    _migrate_track_cache_tids,
    _local_date_of_ping,
    _anchors_for_trip,
    _map_config,
    TRACK_CACHE_DIR,
)


def _simulate_new_flow(trip):
    """Reproduces the inner _select_chosen logic from api_trip_track,
    but without the suppressed/relocated/bad-window cleaning (none of
    the verification trips have these in numbers that would alter the
    decision when alt is empty). Verifies the SHAPE of the output
    matches today's response."""
    cache_file = os.path.join(TRACK_CACHE_DIR, f"{trip['id']}.json")
    if not os.path.isfile(cache_file):
        return None
    with open(cache_file) as f:
        cached = json.load(f)
    _migrate_track_cache_tids(cached)

    enrich_trip_locations(trip)
    home, _ = _map_config()
    anchors = _anchors_for_trip(trip)

    p_pts = [p for p in cached if p.get("tid") == "primary"]
    a_pts = [p for p in cached if p.get("tid") == "alt"]
    _, tid_choices = _select_track_per_day(
        p_pts, a_pts, anchors, home, trip["start"], trip["end"],
        tid_overrides=trip.get("tid_overrides") or {},
    )

    chosen = []
    for p in cached:
        d = _local_date_of_ping(p)
        if d is None:
            continue
        choice = tid_choices.get(d)
        if choice is None:
            if p.get("tid") == "primary":
                chosen.append(p)
            continue
        wanted = choice.split(":")[-1]
        if p.get("tid") == wanted:
            chosen.append(p)
    chosen.sort(key=lambda x: x.get("tst", 0))
    return chosen, tid_choices


def _verify_one(trip_id, trips):
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        print(f"  trip {trip_id}: not found")
        return None
    if not trip.get("start") or not trip.get("end"):
        print(f"  trip {trip_id}: empty trip, skipped")
        return None

    cache_file = os.path.join(TRACK_CACHE_DIR, f"{trip_id}.json")
    if not os.path.isfile(cache_file):
        print(f"  trip {trip_id}: no cache, skipped")
        return None

    with open(cache_file) as f:
        raw = json.load(f)
    raw_tsts = {p.get("tst") for p in raw}

    result = _simulate_new_flow(trip)
    if result is None:
        return None
    chosen, tid_choices = result
    chosen_tsts = {p.get("tst") for p in chosen}

    # Today's behavior: every cached ping ends up in the response.
    # With alt empty, the new flow should produce the same set.
    missing = raw_tsts - chosen_tsts
    extra = chosen_tsts - raw_tsts
    status = "OK" if not missing and not extra else "DIFF"
    n_alt = sum(1 for p in raw if p.get("tid") == "alt")
    print(f"  trip {trip_id}: {status:4s} "
          f"raw={len(raw)} chosen={len(chosen)} "
          f"alt-in-cache={n_alt} missing={len(missing)} extra={len(extra)}")
    if missing or extra:
        sample = list(missing)[:3] + list(extra)[:3]
        print(f"      sample diff tsts: {sample}")
        print(f"      tid_choices: {tid_choices}")
    return status == "OK"


def main():
    ids = sys.argv[1:]
    trips = parse_trips()
    if ids:
        try:
            trip_ids = [int(x) for x in ids]
        except ValueError:
            print("ERROR: trip ids must be integers")
            sys.exit(2)
    else:
        # Every cached trip.
        trip_ids = sorted(
            int(f.removesuffix(".json")) for f in os.listdir(TRACK_CACHE_DIR)
            if f.endswith(".json")
        )

    print(f"verifying {len(trip_ids)} trip(s):")
    n_ok = n_diff = n_skip = 0
    for tid in trip_ids:
        r = _verify_one(tid, trips)
        if r is True: n_ok += 1
        elif r is False: n_diff += 1
        else: n_skip += 1
    print(f"\ntotals: ok={n_ok}, diff={n_diff}, skipped={n_skip}")
    sys.exit(0 if n_diff == 0 else 1)


if __name__ == "__main__":
    main()
