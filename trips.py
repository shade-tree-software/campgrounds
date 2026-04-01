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
    return [_make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                       t.get("events", [])) for t in raw]


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

def create_trip(trip_note="", stay=None):
    """Create a new trip. Returns the new trip dict (with computed fields)."""
    raw = _load_raw_trips()
    new_id = _next_trip_id(raw)
    if stay is None:
        today = date.today().isoformat()
        stay = {
            "start": today,
            "end": today,
            "nights": 1,
            "place": "New Campground",
            "locale": "",
            "state": "",
            "site": "",
            "campers": "",
            "notes": "",
        }
    raw.append({"id": new_id, "trip_note": trip_note, "stays": [stay], "events": []})
    _save_trips(raw)
    return _make_trip(new_id, [stay], trip_note)


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
            default_date = t["stays"][0]["start"] if t["stays"] else date.today().isoformat()
            stay = {
                "start": stay_data.get("start", default_date),
                "end": stay_data.get("end", default_date),
                "nights": int(stay_data.get("nights", 1)),
                "place": stay_data.get("place", "New Campground"),
                "locale": stay_data.get("locale", ""),
                "state": stay_data.get("state", ""),
                "site": stay_data.get("site", ""),
                "campers": stay_data.get("campers", ""),
                "notes": stay_data.get("notes", ""),
            }
            t["stays"].append(stay)
            t["stays"].sort(key=lambda s: s["start"])
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
            for key in ("start", "end", "place", "locale", "state", "site", "campers", "notes"):
                if key in fields:
                    stay[key] = fields[key]
            if "nights" in fields:
                stay["nights"] = int(fields["nights"])
            t["stays"].sort(key=lambda s: s["start"])
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

            if not t["stays"]:
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


# ── Event CRUD ────────────────────────────────────────────────────────────

def add_event(trip_id, event_data):
    """Add an event to a trip. Events are sorted by date. Returns updated trip or None."""
    raw = _load_raw_trips()
    for t in raw:
        if t["id"] == trip_id:
            default_date = t["stays"][0]["start"] if t["stays"] else date.today().isoformat()
            event = {
                "date": event_data.get("date", default_date),
                "name": event_data.get("name", "New Event"),
                "description": event_data.get("description", ""),
            }
            events = t.get("events", [])
            events.append(event)
            events.sort(key=lambda e: e["date"])
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
            for key in ("date", "name", "description"):
                if key in fields:
                    event[key] = fields[key]
            events.sort(key=lambda e: e["date"])
            t["events"] = events
            _save_trips(raw)
            return _make_trip(t["id"], t["stays"], t.get("trip_note", ""),
                              t["events"])
    return None


def rename_campground_in_trips(old_name, new_name):
    """Update all stays that reference old_name to use new_name."""
    raw = _load_raw_trips()
    changed = False
    for t in raw:
        for s in t["stays"]:
            if s["place"] == old_name:
                s["place"] = new_name
                changed = True
    if changed:
        _save_trips(raw)
    return changed


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


def _make_trip(trip_id, stays, trip_note="", events=None):
    """Build a trip dict from a list of stays and optional events."""
    if events is None:
        events = []
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

    home_only = all("basset" in s["place"].lower() for s in stays)

    # Build chronological timeline interleaving stays and events.
    # Secondary key: events (0) sort before stays (1) on the same date,
    # so an event on an arrival day appears before the campground card,
    # and an event on a departure day appears after it (since the stay
    # sorts by its earlier start date).
    timeline = []
    for i, s in enumerate(stays):
        timeline.append(dict(s, type="stay", idx=i, sort_date=s["start"],
                             _order=1))
    for i, e in enumerate(events):
        timeline.append(dict(e, type="event", idx=i, sort_date=e["date"],
                             _order=0))
    timeline.sort(key=lambda x: (x["sort_date"], x["_order"]))

    return {
        "id": trip_id,
        "trip_note": trip_note,
        "stays": stays,
        "events": events,
        "timeline": timeline,
        "start": stays[0]["start"],
        "end": stays[-1]["end"],
        "total_nights": total_nights,
        "summary": summary,
        "campers": sorted(all_campers),
        "home_only": home_only,
    }


def _load_campground_locations(json_path="all-campgrounds.json",
                               config_path="config.json"):
    """Load name -> (lat, lng) mapping from campgrounds and family locations."""
    import json
    import os

    base = os.path.dirname(__file__)

    path = os.path.join(base, json_path)
    with open(path) as f:
        cgs = json.load(f)

    by_name = {}
    for c in cgs:
        lat, lng = c["location"].split(",")
        by_name[c["name"]] = (float(lat), float(lng))

    # Include family locations from config so they resolve in trip enrichment.
    # Use driveway coordinates when available so the stay marker doesn't
    # overlap the family house icon on the map.
    cfg_path = os.path.join(base, config_path)
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = json.load(f)
        for fam in cfg.get("family_locations", []):
            lat = fam.get("driveway_lat", fam["lat"])
            lng = fam.get("driveway_lng", fam["lng"])
            by_name[fam["label"]] = (lat, lng)

    return by_name


def _match_location(place, by_name):
    """Try to find coordinates for a place name using exact then substring matching."""
    if place in by_name:
        return by_name[place]

    place_lower = place.lower()
    for name, coords in by_name.items():
        name_lower = name.lower()
        if place_lower in name_lower or name_lower in place_lower:
            return coords

    return None


def _parse_site_coords(site):
    """Try to parse GPS coordinates from the site field (e.g. '43.071924, -89.476718')."""
    if not site:
        return None
    m = re.match(r'^(-?\d+\.\d+),\s*(-?\d+\.\d+)$', site.strip())
    if m:
        return (float(m.group(1)), float(m.group(2)))
    return None


def enrich_trip_locations(trip):
    """Add lat/lng to each stay in a trip where a match is found."""
    by_name = _load_campground_locations()
    for stay in trip["stays"]:
        coords = _match_location(stay["place"], by_name)
        if not coords:
            coords = _parse_site_coords(stay.get("site", ""))
        if coords:
            stay["lat"] = coords[0]
            stay["lng"] = coords[1]


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
