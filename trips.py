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
                        t.get("events", []), locations) for t in raw]
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
    """Update trip-level fields (trip_note). Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            if "trip_note" in fields:
                t["trip_note"] = fields["trip_note"]
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t.get("events", []))
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
                "campers": stay_data.get("campers", ""),
                "notes": stay_data.get("notes", ""),
            }
            t["stays"].append(stay)
            old_order = list(t["stays"])
            t["stays"].sort(key=lambda s: s["start"])
            _remap_indices_after_sort(trip_id, old_order, t["stays"], "stay")
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t.get("events", []))
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
                              t.get("events", []))
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
                              t.get("events", []))
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

    # Phase 3: remap caption and photo_order keys
    captions_file = os.path.join(_DIR, "trip_data", "captions.json")
    order_file = os.path.join(_DIR, "trip_data", "photo_order.json")
    _remap_json_keys(captions_file, key_prefix, mapping)
    _remap_json_keys(order_file, key_prefix, mapping)


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


def _make_trip(trip_id, stays, trip_note="", events=None, locations=None):
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
        coords = None
        cid = stay.get("campground_id")
        if cid is not None and cid in by_id:
            info = by_id[cid]
            if info["kind"] == "family" and info["driveway"]:
                coords = info["driveway"]
            else:
                coords = (info["lat"], info["lng"])
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
