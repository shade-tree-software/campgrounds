"""Parse trip data from JSON (preferred) or CSV (legacy fallback)."""

import csv
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timedelta

_DIR = os.path.dirname(os.path.abspath(__file__))
TRIPS_JSON = os.path.join(_DIR, "trip_data", "trips.json")

# Photo storage root. MUST match `UPLOAD_DIR` in ekko_trips_app.py — it is
# deliberately a sibling of static/, not inside it (see the "Photo System"
# notes there: anything under the deployment's static root is served straight
# off disk by the front-end web server, bypassing Flask's login gate).
#
# This file used to build photo paths from `static/uploads/`, and kept doing
# so after the photos moved. Nothing raised: every `os.path.isdir()` on a
# path that no longer exists simply came back False, so the directory renames
# below quietly did nothing while the metadata remap — which reads live paths
# under trip_data/ — went ahead. That is exactly how photos came to shift a
# slot when an event or campspot was inserted or deleted.
UPLOAD_DIR = os.path.join(_DIR, "photo_uploads")

# The per-photo metadata stores, all keyed "{trip_id}/{idx}[/events/{idx}]/file".
# A new one belongs in this list, or it silently detaches from its photo the
# first time an index moves.
_PHOTO_METADATA_FILES = ("captions.json", "photo_order.json",
                         "photo_uploaders.json", "photo_favorites.json",
                         "photo_people.json")


def _photo_paths(trip_id, kind):
    """(photo directory root, metadata key prefix) for a trip's stays or events."""
    if kind == "stay":
        return (os.path.join(UPLOAD_DIR, str(trip_id)), str(trip_id))
    return (os.path.join(UPLOAD_DIR, str(trip_id), "events"),
            f"{trip_id}/events")


# ── Public API ────────────────────────────────────────────────────────────

def parse_trips(csv_path=os.path.join(_DIR, "EKKO_Trips.csv")):
    """Return a list of enriched trip dicts.

    Prefers trip_data/trips.json when it exists; falls back to CSV parsing.
    """
    if os.path.exists(TRIPS_JSON):
        return _load_trips_json()
    stays = _parse_stays(csv_path)
    return _group_into_trips(stays)


# ── JSON persistence ──────────────────────────────────────────────────────

def _load_raw_trips():
    """Load the raw trip list from trips.json (no computed fields)."""
    if os.path.exists(TRIPS_JSON):
        with open(TRIPS_JSON) as f:
            return json.load(f)
    return []


def raw_trip_records():
    """The raw trip list straight off disk (no computed/display fields).

    Exposed for callers that need fields `parse_trips()` doesn't
    materialize — notably the admin-override lists (`suppressed_pings`,
    `relocated_pings`) — and that want them for every trip without
    re-reading trips.json once per trip."""
    return _load_raw_trips()


def _save_trips(data):
    """Write the raw trip list to trips.json."""
    os.makedirs(os.path.dirname(TRIPS_JSON), exist_ok=True)
    with open(TRIPS_JSON, "w") as f:
        json.dump(data, f, indent=2)


def _load_trips_json():
    """Load trips from JSON and compute derived fields."""
    raw = _load_raw_trips()
    locations = _load_locations_by_id()
    trips = [_make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                        t.get("events", []), locations,
                        home_start_time=t.get("home_start_time", ""),
                        home_end_time=t.get("home_end_time", ""),
                        bad_track_windows=t.get("bad_track_windows"),
                        tid_overrides=t.get("tid_overrides"),
                        tid_windows=t.get("tid_windows"))
             for t in raw]
    trips.sort(key=lambda t: t["start"])
    n = 0
    for t in trips:
        if t.get("home_only"):
            t["number"] = None
        else:
            n += 1
            t["number"] = n
    return trips


def _next_trip_id(raw_trips):
    if not raw_trips:
        return 1
    return max(t["id"] for t in raw_trips) + 1


def migrate_csv_to_json(csv_path=os.path.join(_DIR, "EKKO_Trips.csv")):
    """One-time migration: parse CSV and write trip_data/trips.json."""
    stays = _parse_stays(csv_path)
    trips = _group_into_trips(stays)
    raw = []
    for t in trips:
        trip_note = t["stays"][0].get("trip_note", "") if t["stays"] else ""
        raw_stays = []
        for s in t["stays"]:
            raw_stays.append({
                "start": s["start"],
                "end": s["end"],
                "nights": s["nights"],
                "place": s["place"],
                "locale": s["locale"],
                "state": s["state"],
                "site": s["site"],
                "campers": s["campers"],
                "notes": s["notes"],
            })
        raw.append({
            "id": t["id"],
            "trip_note": trip_note,
            "stays": raw_stays,
        })
    _save_trips(raw)
    return len(raw)


# ── CRUD operations ───────────────────────────────────────────────────────

def create_trip(trip_note=""):
    """Create a new trip. Returns the new trip dict (with computed fields)."""
    raw = _load_raw_trips()
    new_id = _next_trip_id(raw)
    raw.append({"id": new_id, "trip_note": trip_note, "stays": [], "events": []})
    _save_trips(raw)
    return _make_trip(new_id, [], trip_note)


def update_trip(trip_id, fields):
    """Update trip-level fields (trip_note, home_start_time, home_end_time).
    Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            if "trip_note" in fields:
                t["trip_note"] = fields["trip_note"]
            for key in ("home_start_time", "home_end_time"):
                if key in fields:
                    val = (fields[key] or "").strip()
                    if val:
                        t[key] = val
                    else:
                        t.pop(key, None)
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t.get("events", []),
                              home_start_time=t.get("home_start_time", ""),
                              home_end_time=t.get("home_end_time", ""),
                              bad_track_windows=t.get("bad_track_windows"))
    return None


def delete_trip(trip_id):
    """Delete a trip. Returns True if found and deleted."""
    raw = _load_raw_trips()
    before = len(raw)
    raw = [t for t in raw if t["id"] != trip_id]
    if len(raw) < before:
        _save_trips(raw)
        return True
    return False


def campground_references(location_id):
    """Trips that reference a campgrounds.json entry, as a list of
    ``{"trip_id", "trip_note", "via"}`` dicts (``via`` is "campspot" or
    "family visit").

    Deleting a referenced entry is silently destructive: the campspot's
    ``place`` falls back to ``custom_place or ""`` and it loses its
    coordinates entirely, so it turns into a blank, unmapped row with no
    warning anywhere. Callers use this to refuse the delete instead.
    """
    hits = []
    for trip in _load_raw_trips():
        for stay in trip.get("stays", []):
            if stay.get("campground_id") == location_id:
                hits.append({"trip_id": trip.get("id"),
                             "trip_note": trip.get("trip_note", ""),
                             "via": "campspot"})
        for event in trip.get("events", []):
            if event.get("family_id") == location_id:
                hits.append({"trip_id": trip.get("id"),
                             "trip_note": trip.get("trip_note", ""),
                             "via": "family visit"})
    return hits


def add_stay(trip_id, stay_data):
    """Add a stay to a trip. Stays are sorted by start date. Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            default_start = t["stays"][0]["start"] if t["stays"] else date.today().isoformat()
            default_end = (date.fromisoformat(default_start) + timedelta(days=1)).isoformat()
            start = stay_data.get("start", default_start)
            end = stay_data.get("end", default_end)
            # Ensure start is always before end
            if end <= start:
                end = (date.fromisoformat(start) + timedelta(days=1)).isoformat()
            stay = {
                "start": start,
                "end": end,
                "nights": int(stay_data.get("nights", 1)),
                "campground_id": stay_data.get("campground_id"),
                "custom_place": stay_data.get("custom_place", ""),
                "locale": stay_data.get("locale", ""),
                "state": stay_data.get("state", ""),
                "site": stay_data.get("site", ""),
                "campsite_location": (stay_data.get("campsite_location") or "").strip(),
                "campers": stay_data.get("campers", ""),
                "notes": stay_data.get("notes", ""),
            }
            t["stays"].append(stay)
            old_order = list(t["stays"])
            t["stays"].sort(key=lambda s: s["start"])
            _remap_indices_after_sort(trip_id, old_order, t["stays"], "stay")
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t.get("events", []),
                              home_start_time=t.get("home_start_time", ""),
                              home_end_time=t.get("home_end_time", ""),
                              bad_track_windows=t.get("bad_track_windows"))
    return None


def update_stay(trip_id, stay_idx, fields):
    """Update fields on a specific stay. Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            if stay_idx < 0 or stay_idx >= len(t["stays"]):
                return None
            stay = t["stays"][stay_idx]
            for key in ("start", "end", "campground_id", "custom_place",
                        "locale", "state", "site", "campers", "notes"):
                if key in fields:
                    stay[key] = fields[key]
            if "campsite_location" in fields:
                val = (fields["campsite_location"] or "").strip()
                if val:
                    stay["campsite_location"] = val
                else:
                    stay.pop("campsite_location", None)
            if "nights" in fields:
                stay["nights"] = int(fields["nights"])
            # Ensure start is always before end
            if stay["end"] <= stay["start"]:
                stay["end"] = (date.fromisoformat(stay["start"]) + timedelta(days=1)).isoformat()
            old_order = list(t["stays"])
            t["stays"].sort(key=lambda s: s["start"])
            _remap_indices_after_sort(trip_id, old_order, t["stays"], "stay")
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t.get("events", []),
                              home_start_time=t.get("home_start_time", ""),
                              home_end_time=t.get("home_end_time", ""),
                              bad_track_windows=t.get("bad_track_windows"))
    return None


def delete_stay(trip_id, stay_idx):
    """Delete a stay from a trip. Handles photo directory renaming.
    Returns updated trip, or None if trip not found, or 'empty' if last stay deleted (trip removed)."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            if stay_idx < 0 or stay_idx >= len(t["stays"]):
                return None
            t["stays"].pop(stay_idx)

            # Move photos + their metadata so each campspot keeps its own.
            _remap_indices_after_delete(trip_id, "stay", stay_idx,
                                        len(t["stays"]))

            if not t["stays"] and not t.get("events"):
                raw = [tr for tr in raw if tr["id"] != trip_id]
                _save_trips(raw)
                return "empty"

            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t.get("events", []),
                              home_start_time=t.get("home_start_time", ""),
                              home_end_time=t.get("home_end_time", ""),
                              bad_track_windows=t.get("bad_track_windows"))
    return None


def _remap_indices_after_sort(trip_id, old_items, new_items, kind):
    """Move photos to follow their stay/event after a sort changes indices.

    kind is 'stay' or 'event'. old_items and new_items are the lists before and
    after sorting (items must be the same object references so identity
    comparison works).
    """
    mapping = {}
    for old_idx, item in enumerate(old_items):
        new_idx = next(i for i, x in enumerate(new_items) if x is item)
        if old_idx != new_idx:
            mapping[old_idx] = new_idx
    _apply_photo_index_mapping(trip_id, kind, mapping)


def _remap_indices_after_delete(trip_id, kind, deleted_idx, remaining_count):
    """Move photos to follow their stay/event after the one at `deleted_idx`
    is removed: its own photos and metadata go with it, and everything above
    it shifts down one slot."""
    mapping = {deleted_idx: None}
    for old_idx in range(deleted_idx + 1, remaining_count + 1):
        mapping[old_idx] = old_idx - 1
    _apply_photo_index_mapping(trip_id, kind, mapping)


def _apply_photo_index_mapping(trip_id, kind, mapping):
    """Apply an `old_idx -> new_idx` move to a trip's photo directories and to
    every per-photo metadata store. A `None` target means the slot is gone: its
    directory is removed and its metadata keys are dropped.

    Sort and delete both funnel through here on purpose. They used to be
    separate implementations, and the delete one (`_shift_photo_dirs`) moved
    directories WITHOUT touching captions/order/uploaders/favorites/people — so
    even once its path was right, a delete would have left every caption and
    favorite pointing at the neighbouring campspot's photos.
    """
    if not mapping:
        return
    upload_base, key_prefix = _photo_paths(trip_id, kind)

    if os.path.isdir(upload_base):
        # Two-phase rename: a shift-down maps 3->2 while 2 still exists, so
        # every source moves aside first and only then lands on its target.
        tmp_names = {}
        for old_idx, new_idx in mapping.items():
            old_dir = os.path.join(upload_base, str(old_idx))
            if not os.path.isdir(old_dir):
                continue
            if new_idx is None:
                shutil.rmtree(old_dir)
                continue
            tmp_dir = os.path.join(upload_base, f"_tmp_{old_idx}")
            if os.path.exists(tmp_dir):        # leftover from an interrupted run
                shutil.rmtree(tmp_dir)
            os.rename(old_dir, tmp_dir)
            tmp_names[old_idx] = tmp_dir
        for old_idx, tmp_dir in tmp_names.items():
            os.rename(tmp_dir, os.path.join(upload_base, str(mapping[old_idx])))

    for name in _PHOTO_METADATA_FILES:
        _remap_json_keys(os.path.join(_DIR, "trip_data", name),
                         key_prefix, mapping)


def _remap_json_keys(filepath, key_prefix, mapping):
    """Remap the numeric index in JSON keys shaped `key_prefix/{idx}[/...]`.
    A mapping value of None drops the key (its stay/event was deleted)."""
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        data = json.load(f)

    prefix_slash = key_prefix + "/"
    new_data = {}
    for key, value in data.items():
        if not key.startswith(prefix_slash):
            new_data[key] = value
            continue
        rest = key[len(prefix_slash):]
        parts = rest.split("/", 1)
        try:
            idx = int(parts[0])
        except ValueError:
            new_data[key] = value
            continue
        if idx in mapping:
            if mapping[idx] is None:
                continue                       # deleted along with its slot
            suffix = ("/" + parts[1]) if len(parts) > 1 else ""
            new_data[f"{prefix_slash}{mapping[idx]}{suffix}"] = value
        else:
            new_data[key] = value

    # ensure_ascii=False + explicit utf-8 to match how the app writes these
    # stores (_save_json in ekko_trips_app.py). Without it, a re-sort rewrites
    # every caption containing an em-dash or accent into escaped \uXXXX form.
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)


# ── Event CRUD ────────────────────────────────────────────────────────────

def add_event(trip_id, event_data):
    """Add an event to a trip. Events are sorted by date. Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            default_date = t["stays"][0]["start"] if t["stays"] else date.today().isoformat()
            time = event_data.get("time", "")
            end_time = event_data.get("end_time", "")
            # end_time requires time
            if end_time and not time:
                end_time = ""
            event = {
                "date": event_data.get("date", default_date),
                "time": time,
                "end_time": end_time,
                "name": event_data.get("name", "New Event"),
                "description": event_data.get("description", ""),
                "location": event_data.get("location", ""),
                "locale": event_data.get("locale", ""),
                "state": event_data.get("state", ""),
                "waypoint": bool(event_data.get("waypoint", False)),
                "family_id": event_data.get("family_id"),
                # True for events/waypoints auto-created by GPS-track stop
                # detection; admin clears it by editing/saving. The detection
                # endpoint creates these in bulk; the admin reviews each
                # before clearing the flag.
                "needs_vetting": bool(event_data.get("needs_vetting", False)),
            }
            events = t.get("events", [])
            events.append(event)
            old_order = list(events)
            events.sort(key=lambda e: (e["date"], e.get("time") or "12:00"))
            _remap_indices_after_sort(trip_id, old_order, events, "event")
            t["events"] = events
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t["events"])
    return None


def update_event(trip_id, event_idx, fields):
    """Update fields on a specific event. Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            events = t.get("events", [])
            if event_idx < 0 or event_idx >= len(events):
                return None
            event = events[event_idx]
            for key in ("date", "time", "end_time", "name", "description",
                        "location", "locale", "state", "family_id"):
                if key in fields:
                    event[key] = fields[key]
            if "waypoint" in fields:
                event["waypoint"] = bool(fields["waypoint"])
            if "needs_vetting" in fields:
                # Saving an edited event clears the flag — the admin's act of
                # opening/saving is how vetting happens. Bulk-detected stops
                # are created with this set to True; subsequent edits flip it.
                event["needs_vetting"] = bool(fields["needs_vetting"])
            # end_time requires time
            if event.get("end_time") and not event.get("time"):
                event["end_time"] = ""
            old_order = list(events)
            events.sort(key=lambda e: (e["date"], e.get("time") or "12:00"))
            _remap_indices_after_sort(trip_id, old_order, events, "event")
            t["events"] = events
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t["events"])
    return None


def delete_event(trip_id, event_idx):
    """Delete an event from a trip. Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            events = t.get("events", [])
            if event_idx < 0 or event_idx >= len(events):
                return None
            events.pop(event_idx)

            # Move photos + their metadata so each event keeps its own.
            _remap_indices_after_delete(trip_id, "event", event_idx,
                                        len(events))

            t["events"] = events
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t["events"])
    return None


# ── GPS-ping suppression ─────────────────────────────────────────────────
# Each trip carries an optional `suppressed_pings` list of integer Unix
# timestamps. The GPS-track endpoint filters these out before returning the
# polyline / per-point markers, so admins can hide pings they've identified
# as spurious (cell-tower jumps, single outliers) without re-running the
# upstream pre-processor. Suppression is by `tst` so it survives cache
# invalidation and OwnTracks pagination — the same physical ping always
# reports the same timestamp.

def get_suppressed_pings(trip_id):
    """Return the trip's suppressed-ping timestamp list (empty if none)."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            return list(t.get("suppressed_pings", []))
    return []


def add_suppressed_pings(trip_id, tsts):
    """Add timestamps to a trip's suppressed list. Idempotent (set semantics).
    Returns the resulting list, or None if the trip doesn't exist."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            current = set(t.get("suppressed_pings", []))
            current.update(int(x) for x in tsts)
            t["suppressed_pings"] = sorted(current)
            _save_trips(raw)
            return t["suppressed_pings"]
    return None


def remove_suppressed_pings(trip_id, tsts):
    """Remove timestamps from a trip's suppressed list. Idempotent.
    Returns the resulting list, or None if the trip doesn't exist."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            current = set(t.get("suppressed_pings", []))
            current.difference_update(int(x) for x in tsts)
            if current:
                t["suppressed_pings"] = sorted(current)
            else:
                t.pop("suppressed_pings", None)
            _save_trips(raw)
            return sorted(current)
    return None


# ── GPS-ping relocation ──────────────────────────────────────────────────
# Each trip carries an optional `relocated_pings` list of
# {tst, lat, lon, orig_lat, orig_lon} entries. The track endpoint rewrites
# each matching ping's lat/lon to the override target before returning the
# polyline. Originals are preserved server-side only (in the OwnTracks
# cache); removing the entry restores the ping to its original coords on
# the next fetch.
#
# `orig_lat`/`orig_lon` are the ping's RAW OwnTracks coords at the moment
# the relocation was recorded. They disambiguate the (otherwise common)
# case of multiple OwnTracks pings sharing a `tst`: matching on tst alone
# would relocate every sibling to the same target. Legacy entries written
# before this disambiguator was added carry only `tst`/`lat`/`lon` and the
# applier falls back to the old by-tst behavior for those.

def get_relocated_pings(trip_id):
    """Return the trip's relocated-ping list (each entry is
    {tst, lat, lon} for legacy entries or
    {tst, lat, lon, orig_lat, orig_lon} for newer ones)."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            return list(t.get("relocated_pings", []))
    return []


def _relocation_entry_key(item):
    """Hashable identity for a relocation entry. Newer entries are keyed
    by (tst, orig_lat, orig_lon); legacy entries that lack the originals
    fall back to (tst, None, None). Used by add/remove for idempotent
    upserts and precise removal."""
    tst = int(item["tst"])
    if item.get("orig_lat") is not None and item.get("orig_lon") is not None:
        return (tst, float(item["orig_lat"]), float(item["orig_lon"]))
    return (tst, None, None)


def add_relocated_pings(trip_id, items):
    """Add or update relocations. `items` is an iterable of dicts with
    keys `tst`, `lat`, `lon`, and optionally `orig_lat`/`orig_lon`. If an
    entry's key (tst + originals) already exists, its target is replaced.
    Returns the resulting list, or None if the trip is missing."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            current = {_relocation_entry_key(it): it
                       for it in t.get("relocated_pings", [])}
            for it in items:
                entry = {
                    "tst": int(it["tst"]),
                    "lat": float(it["lat"]),
                    "lon": float(it["lon"]),
                }
                if it.get("orig_lat") is not None and it.get("orig_lon") is not None:
                    entry["orig_lat"] = float(it["orig_lat"])
                    entry["orig_lon"] = float(it["orig_lon"])
                current[_relocation_entry_key(entry)] = entry
            # Stable order: (tst, then any-orig-coord) so trips.json diffs
            # stay readable. None-keyed legacy entries sort before keyed ones
            # for any given tst.
            t["relocated_pings"] = [
                current[k] for k in sorted(
                    current.keys(),
                    key=lambda x: (x[0], x[1] is not None, x[1] or 0, x[2] or 0))
            ]
            _save_trips(raw)
            return list(t["relocated_pings"])
    return None


def remove_relocated_pings(trip_id, tsts=None, items=None):
    """Remove relocations. Pass `tsts=[...]` to remove every entry with
    those `tst`s (legacy / coarse), or `items=[{tst, orig_lat, orig_lon},
    ...]` to remove specific entries (precise — leaves any sibling
    relocation that shares the `tst` but has different originals).

    Idempotent. Returns the resulting list, or None if the trip is missing."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            existing = t.get("relocated_pings", [])
            if items is not None:
                precise_keys = set()  # (tst, orig_lat, orig_lon)
                broad_tsts = set()    # tsts to drop wholesale (no orig given)
                for it in items:
                    tst = int(it["tst"])
                    if it.get("orig_lat") is not None and it.get("orig_lon") is not None:
                        precise_keys.add((tst, float(it["orig_lat"]), float(it["orig_lon"])))
                    else:
                        broad_tsts.add(tst)
                def _keep(e):
                    tst = int(e["tst"])
                    if tst in broad_tsts:
                        return False
                    if e.get("orig_lat") is not None and e.get("orig_lon") is not None:
                        return (tst, float(e["orig_lat"]), float(e["orig_lon"])) not in precise_keys
                    return True  # legacy entry, only droppable via broad_tsts
                keep = [e for e in existing if _keep(e)]
            elif tsts is not None:
                wanted = {int(x) for x in tsts}
                keep = [it for it in existing if int(it["tst"]) not in wanted]
            else:
                return list(existing)
            if keep:
                t["relocated_pings"] = keep
            else:
                t.pop("relocated_pings", None)
            _save_trips(raw)
            return keep
    return None


# ── Per-day tid overrides ────────────────────────────────────────────────
# Each trip can carry an optional `tid_overrides` dict mapping
# 'YYYY-MM-DD' → 'primary'|'alt'. Keys present here force the per-day
# tid selector to use that tid regardless of the heuristic. Missing
# keys defer to the heuristic (see _select_track_per_day in
# ekko_trips_app.py). This is the admin's escape hatch when the
# heuristic picks the wrong phone for a day.

def get_tid_overrides(trip_id):
    """Return the trip's tid_overrides dict (empty if none)."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            return dict(t.get("tid_overrides", {}))
    return {}


def set_tid_override(trip_id, day, value):
    """Set or clear a single date's tid override.

    `day` is a 'YYYY-MM-DD' string. `value` must be 'primary' or 'alt'
    to set, or None to clear (deletes the key). Other values raise
    ValueError. Returns the resulting overrides dict, or None if the
    trip is missing."""
    if value is not None and value not in ("primary", "alt"):
        raise ValueError("tid override value must be 'primary', 'alt', or None")
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            current = dict(t.get("tid_overrides", {}))
            if value is None:
                current.pop(day, None)
            else:
                current[day] = value
            if current:
                t["tid_overrides"] = current
            else:
                t.pop("tid_overrides", None)
            _save_trips(raw)
            return current
    return None


# ── CSV parsing (legacy) ─────────────────────────────────────────────────

def _parse_date(s):
    """Parse M/D/YYYY to a date object."""
    return datetime.strptime(s.strip(), "%m/%d/%Y").date()


def _parse_stays(csv_path):
    """Read CSV and return list of valid overnight stays."""
    stays = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start = row.get("Start Date", "").strip()
            end = row.get("End Date", "").strip()
            nights_str = row.get("Nights", "").strip()

            if not start or not end or not nights_str:
                continue

            try:
                nights = int(nights_str)
            except ValueError:
                continue

            if nights <= 0:
                continue

            place = row.get("Place", "").strip()

            try:
                start_dt = _parse_date(start)
                end_dt = _parse_date(end)
            except ValueError:
                continue

            stays.append({
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "nights": nights,
                "place": row.get("Place", "").strip(),
                "locale": row.get("Locale", "").strip(),
                "state": row.get("State", "").strip(),
                "site": row.get("Site", "").strip(),
                "campers": row.get("Campers", "").strip(),
                "trip_note": row.get("Trip Note", "").strip(),
                "notes": row.get("Note", "").strip(),
            })
    return stays


def _group_into_trips(stays):
    """Group consecutive stays into trips.

    Two stays are consecutive if the first stay's end date equals
    the second stay's start date.
    """
    if not stays:
        return []

    def _is_home(stay):
        return "basset" in stay["place"].lower()

    trips = []
    current_trip_stays = [stays[0]]

    for stay in stays[1:]:
        prev_end = current_trip_stays[-1]["end"]
        consecutive = stay["start"] == prev_end
        # Break into separate trip if: not consecutive, or home boundary
        if not consecutive or _is_home(stay) != _is_home(current_trip_stays[-1]):
            trips.append(_make_trip(len(trips) + 1, current_trip_stays))
            current_trip_stays = [stay]
        else:
            current_trip_stays.append(stay)

    trips.append(_make_trip(len(trips) + 1, current_trip_stays))
    return trips


# A "home stay" is a night spent at the family's own house rather than at a
# campsite. Home isn't a campgrounds.json entry — it's recorded as a free-text
# `custom_place` with `campground_id: null`, the same way a hotel or Airbnb is.
#
# Go through is_home_stay() everywhere. This rule drives BOTH `home_only`
# (which hides an entire trip from the map, calendar, list and landing page)
# and the stats night counts, so a false positive is expensive and silent: a
# real trip would simply disappear from every public surface.
#
# Fallback marker, used only when home.json doesn't configure
# `home_place_names`. It is a SUBSTRING test, which is exactly why it isn't
# trusted on its own — "basset" is a substring of "Bassett City Park" (a real
# municipal campground in Nebraska, id 2771). The campground_id guard in
# is_home_stay() is what actually makes that safe; see there.
_LEGACY_HOME_MARKER = "basset"

HOME_JSON = os.path.join(_DIR, "home.json")
_home_names_cache = {"mtime": None, "names": None}


def _home_place_names():
    """Exact place names meaning "home", from home.json's `home_place_names`
    (a list of strings), lowercased. None when unconfigured, which selects the
    legacy substring fallback.

    The names live in gitignored config rather than in code on purpose: this
    repo is public, and the home place name is a street address.
    """
    try:
        mtime = os.path.getmtime(HOME_JSON)
    except OSError:
        mtime = None
    if _home_names_cache["mtime"] != mtime:
        names = None
        if mtime is not None:
            try:
                with open(HOME_JSON) as f:
                    raw = json.load(f).get("home_place_names")
                if isinstance(raw, list):
                    names = {str(n).strip().lower() for n in raw if str(n).strip()} or None
            except (ValueError, OSError):
                names = None          # malformed config → fall back, never crash
        _home_names_cache["mtime"] = mtime
        _home_names_cache["names"] = names
    return _home_names_cache["names"]


def is_home_stay(stay):
    """True if a stay record is a night at home rather than camping."""
    # THE load-bearing check: a stay that references a campgrounds.json entry
    # is a real campground, so it can never be home — home is always free text.
    # This alone rules out every campground-name collision, including the one
    # already in the database ("Bassett City Park" contains "basset"), and it
    # holds regardless of which matching mode runs below.
    if stay.get("campground_id") is not None:
        return False
    place = (stay.get("place") or "").strip().lower()
    if not place:
        return False
    names = _home_place_names()
    if names is not None:
        return place in names               # configured: exact match
    return _LEGACY_HOME_MARKER in place     # unconfigured: legacy substring


def camping_nights(trip):
    """Nights actually spent camping — `total_nights` minus any home stays.

    Trips made up entirely of home stays are flagged `home_only` and dropped
    from the stats wholesale, but a MIXED trip (drove home mid-trip, then back
    out) keeps its home nights in `total_nights`. Those aren't camping, so any
    "nights" aggregate should come through here rather than summing
    `total_nights` directly.
    """
    return sum(s.get("nights", 0) for s in trip.get("stays", [])
               if not is_home_stay(s))


def _visit_place_key(stay):
    """Identity of the PLACE a stay is at, or None when there isn't one.

    Campground-backed stays key off the id (renames can't split a run);
    free-text stays off the normalized place text, so two different hotels
    on consecutive nights stay distinct. A stay with neither is unkeyable
    and never groups with its neighbour.
    """
    cid = stay.get("campground_id")
    if cid is not None:
        return ("cg", cid)
    place = " ".join((stay.get("place") or stay.get("custom_place") or "").lower().split())
    return ("place", place) if place else None


def visit_runs(stays):
    """Group a trip's stays into VISITS — lists of indices into `stays`.

    A visit is a run of consecutive stays at the same place with no gap in
    the dates. One record per campsite is how a mid-stay site change gets
    recorded (trip 93: night 1 on site 67, nights 2-3 on site 36), and every
    per-campground count downstream — the trips-map dot size and its popup
    list, the campground-map popup, the stats page's most-visited list —
    would otherwise read those two records as visiting twice.

    Contiguity is required, not just a matching place: a trip that camps
    somewhere, moves on, and comes back later really did visit twice (trip
    16 does exactly that at two campgrounds), so those stay separate.
    """
    runs = []
    prev_key, prev_end = None, None
    for i, stay in enumerate(stays):
        key = _visit_place_key(stay)
        continues = (runs and key is not None and key == prev_key
                     and prev_end and stay.get("start") == prev_end)
        if continues:
            runs[-1].append(i)
        else:
            runs.append([i])
        prev_key, prev_end = key, stay.get("end")
    return runs


def _site_label(site):
    """The campsite as it should read on a card, or "" when it isn't a label.

    Some legacy stays stash GPS coordinates in `site` (enrich_trip_locations
    still parses them as a last-resort position); those aren't a site name
    and don't belong in the header line. The "Site" prefix is skipped when
    the value already says it ("Canoe w/River View (Site 3)"), and pluralized
    when the stay lists several ("H253, H255").
    """
    site = (site or "").strip()
    if not site or _parse_site_coords(site):
        return ""
    if "site" in site.lower():
        return site
    return f"Site{'s' if ',' in site else ''} {site}"


def is_day_trip(trip):
    """True for a trip with events but no campspots.

    An EMPTY trip (no campspots AND no events) is not a day trip — it's a
    placeholder with no date range, excluded from the calendar and every
    count. The header and the stats page must agree on that, so both go
    through here rather than each spelling out the predicate.
    """
    return not trip.get("stays") and bool(trip.get("events"))


def _make_trip(trip_id, stays, trip_note="", events=None, locations=None,
               home_start_time="", home_end_time="",
               bad_track_windows=None, tid_overrides=None,
               tid_windows=None):
    """Build a trip dict from a list of stays and optional events.

    If `locations` (id → info map from `_load_locations_by_id`) is supplied,
    each stay gets a `place` string materialized from its `campground_id`
    (or `custom_place` fallback), and each event gets a `family_visit`
    label materialized from its `family_id`. These materialized fields are
    display-only — the authoritative values remain `campground_id` /
    `custom_place` / `family_id`.
    """
    if events is None:
        events = []
    if locations is None:
        locations = _load_locations_by_id()

    for s in stays:
        cid = s.get("campground_id")
        if cid is not None and cid in locations:
            s["place"] = locations[cid]["name"]
        else:
            s["place"] = s.get("custom_place", "") or ""
        s["site_label"] = _site_label(s.get("site"))

    # Consecutive stays at one place are ONE visit (see `visit_runs`). Each
    # stay carries where it sits in its own visit so a card can say "night 2
    # of 3" across the whole visit rather than "night 1 of 2" of one campsite,
    # and so the maps can count a visit once.
    for run in visit_runs(stays):
        visit_nights = sum(stays[i].get("nights", 0) for i in run)
        nights_before = 0
        for pos, i in enumerate(run, start=1):
            stays[i]["visit_num"] = pos              # 1 == this stay starts the visit
            stays[i]["visit_stays"] = len(run)
            stays[i]["visit_nights"] = visit_nights
            stays[i]["visit_night_offset"] = nights_before
            nights_before += stays[i].get("nights", 0)

    total_nights = sum(s["nights"] for s in stays)
    places = []
    seen = set()
    for s in stays:
        key = f"{s['place']}, {s['locale']}, {s['state']}"
        if key not in seen:
            seen.add(key)
            places.append(s["place"])

    # Use explicit trip_note, or fall back to first stay's trip_note (CSV legacy)
    if not trip_note:
        trip_note = stays[0].get("trip_note", "").strip() if stays else ""
    if trip_note:
        summary = trip_note
    elif not places and events:
        summary = "Events Only"
    elif not places:
        summary = "New Trip"
    elif len(places) == 1:
        summary = places[0]
    elif len(places) == 2:
        summary = f"{places[0]} & {places[1]}"
    else:
        summary = f"{places[0]} & {len(places) - 1} more"

    # Collect all unique campers across stays
    all_campers = set()
    for s in stays:
        if s["campers"]:
            for c in s["campers"].split(","):
                name = c.strip().lstrip("(").rstrip(")")
                if "--" in name:
                    name = name.split("--")[0].strip()
                if name:
                    all_campers.add(name)

    home_only = bool(stays) and all(is_home_stay(s) for s in stays)

    # Build chronological timeline interleaving stays and events.
    # Sorting rules:
    #   - Event on same date as stay's start → event first (_order=0 vs 1)
    #   - Event on same date as stay's end → stay already sorted earlier by start date
    #   - Events on same date ordered by time (default noon)
    # Multi-night stays with at least one event on a strictly-interior day
    # (i.e., arrival < event_date < departure) are split into per-night
    # copies so the timeline shows which night you slept there in between
    # daytime excursions. Each copy sorts at "end of its own day" so that
    # all daytime events on date D land before the copy representing the
    # night of date D.
    def _stay_needs_split(s):
        nights = int(s.get("nights") or 0)
        if nights <= 1 or not s.get("start") or not s.get("end"):
            return False
        try:
            start_d = date.fromisoformat(s["start"])
            end_d = date.fromisoformat(s["end"])
        except ValueError:
            return False
        for e in events:
            ed = e.get("date")
            if not ed:
                continue
            try:
                e_d = date.fromisoformat(ed)
            except ValueError:
                continue
            if start_d < e_d < end_d:
                return True
        return False

    # Every stay card also carries the nights it covers as a span within its
    # VISIT (`night_from`..`night_to` of `night_total`) plus the dates those
    # nights run between (`card_start` to `card_end`). Numbering across the
    # visit is what makes a split card unambiguous: "night 2 of 3" is the
    # trip's second night at the campground, whichever campsite record it
    # belongs to. Every card gets a date RANGE so the format doesn't change
    # between a whole stay and one night of one.
    timeline = []
    for i, s in enumerate(stays):
        offset = s.get("visit_night_offset", 0)
        night_total = s.get("visit_nights", s.get("nights", 0))
        if _stay_needs_split(s):
            start_d = date.fromisoformat(s["start"])
            nights = int(s["nights"])
            for n in range(1, nights + 1):
                night_date = start_d + timedelta(days=n - 1)
                timeline.append(dict(s, type="stay", idx=i,
                                     sort_date=night_date.isoformat(),
                                     card_start=night_date.isoformat(),
                                     card_end=(night_date + timedelta(days=1)).isoformat(),
                                     night_from=offset + n, night_to=offset + n,
                                     night_total=night_total,
                                     _order=1, _time="23:59",
                                     copy_num=n, copy_count=nights))
        else:
            timeline.append(dict(s, type="stay", idx=i, sort_date=s["start"],
                                 card_start=s["start"], card_end=s["end"],
                                 night_from=offset + 1,
                                 night_to=offset + s.get("nights", 0),
                                 night_total=night_total,
                                 _order=1, _time="00:00",
                                 copy_num=1, copy_count=1))
    for i, e in enumerate(events):
        # Default optional fields and materialize family_visit label for display
        e.setdefault("location", "")
        e.setdefault("time", "")
        e.setdefault("end_time", "")
        e.setdefault("waypoint", False)
        e.setdefault("locale", "")
        e.setdefault("state", "")
        e.setdefault("needs_vetting", False)
        fid = e.get("family_id")
        if fid is not None and fid in locations:
            e["family_visit"] = locations[fid]["name"]
        else:
            e["family_visit"] = ""
        timeline.append(dict(e, type="event", idx=i, sort_date=e["date"],
                             _order=0, _time=e.get("time") or "12:00"))
    timeline.sort(key=lambda x: (x["sort_date"], x["_order"], x["_time"]))

    if stays:
        start = stays[0]["start"]
        end = stays[-1]["end"]
    elif events:
        start = events[0]["date"]
        end = max(e["date"] for e in events)
    else:
        start = end = ""

    return {
        "id": trip_id,
        "trip_note": trip_note,
        "stays": stays,
        "events": events,
        "timeline": timeline,
        "start": start,
        "end": end,
        "total_nights": total_nights,
        "summary": summary,
        "campers": sorted(all_campers),
        "home_only": home_only,
        "home_start_time": home_start_time,
        "home_end_time": home_end_time,
        "bad_track_windows": list(bad_track_windows) if bad_track_windows else [],
        "tid_overrides": dict(tid_overrides) if tid_overrides else {},
        "tid_windows": list(tid_windows) if tid_windows else [],
    }


FAMILY_JSON = os.path.join(_DIR, "trip_data", "family.json")


def _mtime_or_zero(path):
    """mtime, or 0 if the file is missing — a cheap cache-key component."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0


def _load_family_entries():
    """Family-kind location entries; missing file → [].

    Absent is normal, not an error: a fresh clone gets campgrounds.json from
    git and nothing else, and family.json arrives via backup/sync (or is
    created by the first family entry added in the manage UI).
    """
    try:
        with open(FAMILY_JSON) as f:
            entries = json.load(f)
    except (FileNotFoundError, ValueError):
        return []
    return entries if isinstance(entries, list) else []


# mtime-keyed cache for _load_locations_by_id. The ~1,100-entry
# campgrounds.json was being re-parsed for every trip on the map pages
# (enrich_trip_locations calls this per trip — ~630ms of a render); the
# cache cuts that to one parse per file change. Callers treat the
# returned dict as read-only, so sharing one instance is safe.
_LOCATIONS_CACHE = {"key": None, "by_id": None}


def _load_locations_by_id(json_path="campgrounds.json"):
    """Load id → {name, lat, lng, kind, driveway: (lat,lng)|None}.

    Reads BOTH location files: campgrounds.json (tracked) and trip_data/
    family.json (gitignored — family entries are relatives' addresses and this
    repo is public). Ids are unique across the two, and a stay's
    `campground_id` / an event's `family_id` doesn't record which file it points
    into, so both must be resolvable from one map.
    """
    base = os.path.dirname(__file__)
    path = os.path.join(base, json_path)
    key = (path, _mtime_or_zero(path), _mtime_or_zero(FAMILY_JSON))
    if _LOCATIONS_CACHE["by_id"] is not None and _LOCATIONS_CACHE["key"] == key:
        return _LOCATIONS_CACHE["by_id"]
    with open(path) as f:
        cgs = json.load(f)
    cgs = cgs + _load_family_entries()

    by_id = {}
    for c in cgs:
        if "id" not in c or "location" not in c:
            continue
        lat, lng = c["location"].split(",")
        driveway = None
        dl = c.get("driveway_location")
        if dl:
            dlat, dlng = dl.split(",")
            driveway = (float(dlat), float(dlng))
        by_id[c["id"]] = {
            "name": c["name"],
            "lat": float(lat),
            "lng": float(lng),
            "kind": c.get("kind", "campground"),
            "driveway": driveway,
        }
    _LOCATIONS_CACHE.update(key=key, by_id=by_id)
    return by_id


def _parse_site_coords(site):
    """Try to parse GPS coordinates from the site field (e.g. '43.071924, -89.476718')."""
    if not site:
        return None
    m = re.match(r'^(-?\d+\.\d+),\s*(-?\d+\.\d+)$', site.strip())
    if m:
        return (float(m.group(1)), float(m.group(2)))
    return None


def enrich_trip_locations(trip):
    """Add lat/lng to each stay and event in a trip where a match is found.

    Stays resolve via `campground_id` → campgrounds.json. For family-kind
    entries, the `driveway_location` is preferred so the stay marker
    doesn't collide with the family house icon. As a last resort the
    `site` field is parsed for embedded GPS coordinates.
    """
    by_id = _load_locations_by_id()
    for stay in trip["stays"]:
        # Resolve the campground-level coords first (independent of any per-stay
        # override) so the main map can group all stays at the same campground
        # onto a single marker — even when individual stays carry a different
        # `campsite_location` for the trip-detail view. Family-kind entries
        # still prefer their `driveway_location` to avoid colliding with the
        # red house marker.
        cg_coords = None
        cid = stay.get("campground_id")
        if cid is not None and cid in by_id:
            info = by_id[cid]
            if info["kind"] == "family" and info["driveway"]:
                cg_coords = info["driveway"]
            else:
                cg_coords = (info["lat"], info["lng"])
        if cg_coords:
            stay["cg_lat"] = cg_coords[0]
            stay["cg_lng"] = cg_coords[1]

        coords = None
        # Per-stay override takes precedence — used to correct cases where the
        # campground's listed coords are at the office/entrance and the actual
        # campsite is meaningfully offset.
        override = (stay.get("campsite_location") or "").strip()
        if override:
            coords = _parse_site_coords(override)
        if not coords and cg_coords:
            coords = cg_coords
        if not coords:
            coords = _parse_site_coords(stay.get("site", ""))
        if coords:
            stay["lat"] = coords[0]
            stay["lng"] = coords[1]
    for event in trip.get("events", []):
        loc = event.get("location", "")
        if loc:
            coords = _parse_site_coords(loc)
            if coords:
                event["lat"] = coords[0]
                event["lng"] = coords[1]


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "migrate":
        count = migrate_csv_to_json()
        print(f"Migrated {count} trips to {TRIPS_JSON}")
    else:
        trips = parse_trips()
        for t in trips:
            print(f"Trip {t['id']}: {t['start']} to {t['end']} ({t['total_nights']} nights) - {t['summary']}")
            for s in t["stays"]:
                print(f"  {s['start']} to {s['end']} ({s['nights']}N) {s['place']}, {s['locale']}, {s['state']}")
