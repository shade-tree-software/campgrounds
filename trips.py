"""Parse EKKO_Trips.csv into trips (consecutive overnight stays)."""

import csv
import re
from datetime import datetime, timedelta


def parse_trips(csv_path="EKKO_Trips.csv"):
    """Parse the CSV and return a list of trips.

    A trip is a consecutive sequence of overnight stays (nights > 0)
    where each stay's start date equals the previous stay's end date.
    Blank rows or gaps break trips apart.

    Returns a list of dicts:
    [
        {
            "id": int,
            "stays": [
                {
                    "start": "YYYY-MM-DD",
                    "end": "YYYY-MM-DD",
                    "nights": int,
                    "place": str,
                    "locale": str,
                    "state": str,
                    "site": str,
                    "campers": str,
                    "notes": str,
                }
            ],
            "start": "YYYY-MM-DD",
            "end": "YYYY-MM-DD",
            "total_nights": int,
            "summary": str,  # e.g. "Acadia National Park & 3 more"
        }
    ]
    """
    stays = _parse_stays(csv_path)
    return _group_into_trips(stays)


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
                "notes": row.get("Notes", "").strip(),
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


def _make_trip(trip_id, stays):
    """Build a trip dict from a list of stays."""
    total_nights = sum(s["nights"] for s in stays)
    places = []
    seen = set()
    for s in stays:
        key = f"{s['place']}, {s['locale']}, {s['state']}"
        if key not in seen:
            seen.add(key)
            places.append(s["place"])

    first_notes = stays[0].get("notes", "").strip()
    description = ""
    if first_notes:
        # Split on first comma, period, or semicolon
        m = re.split(r"[,.;]", first_notes, maxsplit=1)
        summary = m[0].strip()
        if len(m) > 1:
            description = m[1].strip()
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
                # Remove parenthetical notes like "--1st night only"
                if "--" in name:
                    name = name.split("--")[0].strip()
                if name:
                    all_campers.add(name)

    home_only = all("basset" in s["place"].lower() for s in stays)

    return {
        "id": trip_id,
        "stays": stays,
        "start": stays[0]["start"],
        "end": stays[-1]["end"],
        "total_nights": total_nights,
        "summary": summary,
        "description": description,
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

    # Include family locations from config so they resolve in trip enrichment
    cfg_path = os.path.join(base, config_path)
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = json.load(f)
        for fam in cfg.get("family_locations", []):
            by_name[fam["label"]] = (fam["lat"], fam["lng"])

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
    trips = parse_trips()
    for t in trips:
        print(f"Trip {t['id']}: {t['start']} to {t['end']} ({t['total_nights']} nights) - {t['summary']}")
        for s in t["stays"]:
            print(f"  {s['start']} to {s['end']} ({s['nights']}N) {s['place']}, {s['locale']}, {s['state']}")
