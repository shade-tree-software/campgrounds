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
                        tid_overrides=t.get("tid_overrides"))
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

            # Rename photo directories to keep indices aligned
            upload_base = os.path.join(_DIR, "static", "uploads", str(trip_id))
            if os.path.isdir(upload_base):
                _shift_photo_dirs(upload_base, stay_idx, len(t["stays"]))

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


def _shift_photo_dirs(upload_base, deleted_idx, remaining_count):
    """After deleting stay at deleted_idx, shift higher-indexed photo dirs down."""
    # Remove the deleted stay's photos
    deleted_dir = os.path.join(upload_base, str(deleted_idx))
    if os.path.isdir(deleted_dir):
        shutil.rmtree(deleted_dir)

    # Shift directories above deleted_idx down by one
    for i in range(deleted_idx + 1, remaining_count + 2):
        old_dir = os.path.join(upload_base, str(i))
        new_dir = os.path.join(upload_base, str(i - 1))
        if os.path.isdir(old_dir):
            os.rename(old_dir, new_dir)


def _remap_indices_after_sort(trip_id, old_items, new_items, kind):
    """Remap photo directories and caption/order keys after a sort changes indices.

    kind is 'stay' or 'event'. old_items and new_items are the lists before and
    after sorting (items must be the same object references so identity comparison works).
    """
    # Build old_idx -> new_idx mapping using object identity
    mapping = {}
    for old_idx, item in enumerate(old_items):
        new_idx = next(i for i, x in enumerate(new_items) if x is item)
        if old_idx != new_idx:
            mapping[old_idx] = new_idx

    if not mapping:
        return

    # Determine path prefix for dirs and keys
    if kind == "stay":
        upload_base = os.path.join(_DIR, "static", "uploads", str(trip_id))
        key_prefix = str(trip_id)
    else:
        upload_base = os.path.join(_DIR, "static", "uploads", str(trip_id), "events")
        key_prefix = f"{trip_id}/events"

    # Phase 1: rename directories to temporary names to avoid collisions
    tmp_names = {}
    for old_idx in mapping:
        old_dir = os.path.join(upload_base, str(old_idx))
        if os.path.isdir(old_dir):
            tmp_dir = os.path.join(upload_base, f"_tmp_{old_idx}")
            os.rename(old_dir, tmp_dir)
            tmp_names[old_idx] = tmp_dir

    # Phase 2: rename from temporary to final names
    for old_idx, tmp_dir in tmp_names.items():
        new_dir = os.path.join(upload_base, str(mapping[old_idx]))
        os.rename(tmp_dir, new_dir)

    # Phase 3: remap caption, photo_order, and per-photo uploader keys
    # (all three share the "{trip_id}/{idx}/..." key shape).
    captions_file = os.path.join(_DIR, "trip_data", "captions.json")
    order_file = os.path.join(_DIR, "trip_data", "photo_order.json")
    uploaders_file = os.path.join(_DIR, "trip_data", "photo_uploaders.json")
    _remap_json_keys(captions_file, key_prefix, mapping)
    _remap_json_keys(order_file, key_prefix, mapping)
    _remap_json_keys(uploaders_file, key_prefix, mapping)


def _remap_json_keys(filepath, key_prefix, mapping):
    """Remap numeric index in JSON keys matching key_prefix/{idx}[/...]."""
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
            suffix = ("/" + parts[1]) if len(parts) > 1 else ""
            new_key = f"{prefix_slash}{mapping[idx]}{suffix}"
            new_data[new_key] = value
        else:
            new_data[key] = value

    with open(filepath, "w") as f:
        json.dump(new_data, f, indent=2)


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

            # Remove event photos and shift directories
            upload_base = os.path.join(_DIR, "static", "uploads",
                                       str(trip_id), "events")
            if os.path.isdir(upload_base):
                _shift_photo_dirs(upload_base, event_idx, len(events))

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


def _make_trip(trip_id, stays, trip_note="", events=None, locations=None,
               home_start_time="", home_end_time="",
               bad_track_windows=None, tid_overrides=None):
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

    home_only = bool(stays) and all("basset" in s["place"].lower() for s in stays)

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

    timeline = []
    for i, s in enumerate(stays):
        if _stay_needs_split(s):
            start_d = date.fromisoformat(s["start"])
            nights = int(s["nights"])
            for n in range(1, nights + 1):
                night_date = (start_d + timedelta(days=n - 1)).isoformat()
                timeline.append(dict(s, type="stay", idx=i,
                                     sort_date=night_date,
                                     _order=1, _time="23:59",
                                     copy_num=n, copy_count=nights))
        else:
            timeline.append(dict(s, type="stay", idx=i, sort_date=s["start"],
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
    }


def _load_locations_by_id(json_path="campgrounds.json"):
    """Load id → {name, lat, lng, kind, driveway: (lat,lng)|None} from campgrounds.json."""
    base = os.path.dirname(__file__)
    with open(os.path.join(base, json_path)) as f:
        cgs = json.load(f)

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
