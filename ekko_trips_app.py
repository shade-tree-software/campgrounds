import json
import os
import re
import shutil
import sys
from datetime import date, datetime, time as dt_time, timedelta

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from trips import (parse_trips, enrich_trip_locations,
                   create_trip, update_trip, delete_trip,
                   add_stay, update_stay, delete_stay,
                   add_event, update_event, delete_event,
                   get_suppressed_pings, add_suppressed_pings,
                   remove_suppressed_pings,
                   get_relocated_pings, add_relocated_pings,
                   remove_relocated_pings,
                   get_tid_overrides, set_tid_override)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.jinja_env.policies['json.dumps_kwargs'] = {'sort_keys': False}
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())


@app.template_filter('to12h')
def _to12h(value):
    """Format a stored 24-hour 'HH:MM' time string as 12-hour 'h:MM AM/PM'.

    Returns the input unchanged if it isn't a parseable HH:MM string so
    blank/legacy values pass through harmlessly.
    """
    if not value or ":" not in str(value):
        return value
    try:
        h, m = str(value).split(":")[:2]
        h, m = int(h), int(m)
        if not (0 <= h < 24 and 0 <= m < 60):
            return value
    except (ValueError, TypeError):
        return value
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {suffix}"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

TRIP_DATA_DIR = os.path.join(os.path.dirname(__file__), "trip_data")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
CAPTIONS_FILE = os.path.join(TRIP_DATA_DIR, "captions.json")
PHOTO_ORDER_FILE = os.path.join(TRIP_DATA_DIR, "photo_order.json")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
# Per-photo uploader record. Keyed identically to captions:
#   "{trip_id}/{stay_idx}/{filename}" or "{trip_id}/events/{event_idx}/{filename}".
# Used to gate non-admin (uploader-role) caption edits to their own contributions.
PHOTO_UPLOADERS_FILE = os.path.join(TRIP_DATA_DIR, "photo_uploaders.json")

os.makedirs(TRIP_DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.context_processor
def inject_trip_stats():
    trips = [t for t in parse_trips() if not t.get("home_only")]
    overnight = sum(1 for t in trips if t["stays"])
    daytrips = sum(1 for t in trips if not t["stays"])
    return {
        "overnight_count": overnight,
        "daytrip_count": daytrips,
        "night_count": sum(t["total_nights"] for t in trips),
    }

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "heic"}
CAMPGROUNDS_JSON = os.path.join(os.path.dirname(__file__), "campgrounds.json")
HOME_FILE = os.path.join(os.path.dirname(__file__), "home.json")

WATERFRONT_COLORS = {
    "coastal dunes": "#e6a817",
    "coastal woods": "#6b8e23",
    "bay":           "#0d47a1",
    "lake":          "#1976d2",
    "lakeview":      "#64b5f6",
    "river":         "#00695c",
    "riverview":     "#26a69a",
    "creek":         "#80cbc4",
    "pond":          "#9acd32",
    "none":          "#795548",
}

CLIMATE_COLORS = {
    "much cooler":     "#1a237e",
    "cooler":          "#1565c0",
    "slightly cooler": "#42a5f5",
    "similar to home": "#4caf50",
    "slightly warmer": "#fdd835",
    "warmer":          "#fb8c00",
    "much warmer":     "#e53935",
    "hot":             "#b71c1c",
}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _photo_date_taken(filepath):
    """Extract when a photo was taken from EXIF data.

    Returns 'YYYY-MM-DD HH:MM:SS' when a time is present, 'YYYY-MM-DD' when
    only a date is available, or '' if there's no EXIF timestamp.
    """
    try:
        from PIL import Image
        from PIL.ExifTags import Base as ExifBase
        img = Image.open(filepath)
        exif = img.getexif()
        # Try DateTimeOriginal first, then DateTimeDigitized, then DateTime
        for tag in (ExifBase.DateTimeOriginal, ExifBase.DateTimeDigitized, ExifBase.DateTime):
            val = exif.get(tag)
            if val:
                # EXIF timestamps are "YYYY:MM:DD HH:MM:SS"
                date_part, _, time_part = val.partition(" ")
                date_str = date_part.replace(":", "-")
                time_part = time_part.strip()
                return f"{date_str} {time_part}" if time_part else date_str
    except Exception:
        pass
    return ""


def _photo_datetime_taken(filepath):
    """Like _photo_date_taken but returns the full datetime or None.

    Used for bucketing photos across multi-copy stay cards.
    """
    try:
        from PIL import Image
        from PIL.ExifTags import Base as ExifBase
        img = Image.open(filepath)
        exif = img.getexif()
        for tag in (ExifBase.DateTimeOriginal, ExifBase.DateTimeDigitized, ExifBase.DateTime):
            val = exif.get(tag)
            if not val:
                continue
            try:
                return datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                return None
    except Exception:
        pass
    return None


def _save_photo(file_storage, photo_dir):
    """Save an uploaded photo to photo_dir, handling filename collisions.
    Returns (filename, dest_path) or None if the file type is not allowed."""
    filename = secure_filename(file_storage.filename)
    if not filename or not _allowed_file(filename):
        return None
    os.makedirs(photo_dir, exist_ok=True)
    base, ext = os.path.splitext(filename)
    dest = os.path.join(photo_dir, filename)
    if os.path.exists(dest):
        filename = f"{base}_{int(datetime.now().timestamp())}{ext}"
        dest = os.path.join(photo_dir, filename)
    file_storage.save(dest)
    return filename


def _extract_zip_photos(file_storage, photo_dir):
    """Extract image files from a zip archive into photo_dir.
    Returns a list of saved filenames."""
    import zipfile
    import io
    saved = []
    data = io.BytesIO(file_storage.read())
    with zipfile.ZipFile(data) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            basename = os.path.basename(info.filename)
            if not basename or basename.startswith('.') or basename.startswith('__'):
                continue
            if not _allowed_file(basename):
                continue
            os.makedirs(photo_dir, exist_ok=True)
            filename = secure_filename(basename)
            if not filename:
                continue
            base, ext = os.path.splitext(filename)
            dest = os.path.join(photo_dir, filename)
            if os.path.exists(dest):
                filename = f"{base}_{int(datetime.now().timestamp())}{ext}"
                dest = os.path.join(photo_dir, filename)
            with zf.open(info) as src, open(dest, 'wb') as dst:
                dst.write(src.read())
            saved.append(filename)
    return saved


def _load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ── User authentication ────────────────────────────────────────────────────

class User(UserMixin):
    def __init__(self, username, password_hash, is_admin=False, can_upload=False):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        # Admins implicitly carry upload rights — checking can_upload alone is
        # always sufficient for upload-gated endpoints.
        self.can_upload = bool(is_admin) or bool(can_upload)


def _load_users():
    return {name: User(name, info["password_hash"],
                       info.get("is_admin", False),
                       info.get("can_upload", False))
            for name, info in _load_json(USERS_FILE).items()}


def _save_user(username, password, is_admin=False, can_upload=False):
    data = _load_json(USERS_FILE)
    data[username] = {
        "password_hash": generate_password_hash(password),
        "is_admin": is_admin,
        "can_upload": can_upload,
    }
    _save_json(USERS_FILE, data)


@login_manager.user_loader
def load_user(username):
    users = _load_users()
    return users.get(username)


@app.before_request
def _require_login_globally():
    # Public endpoints that must remain accessible without authentication.
    if request.endpoint in ('login', 'static', None):
        return None
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.path))
    return None


def _require_admin():
    """Return an error response if current user is not an admin, else None."""
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    return None


def _require_uploader_or_admin():
    """Gate endpoints that uploader-role users may also use (photo POST + own-photo
    caption edits). Admins always pass since User.can_upload is True for them."""
    if not current_user.is_authenticated or not getattr(current_user, "can_upload", False):
        return jsonify({"error": "Upload access required"}), 403
    return None


# ── Photo upload ownership ────────────────────────────────────────────────
# Each successful photo upload records the uploader's username keyed by
# "{trip_id}/{stay_idx}/{filename}" (or events variant). Uploader-role users
# can edit captions on photos they own; only admins can delete or reorder.

def _record_uploader(photo_key, username):
    data = _load_json(PHOTO_UPLOADERS_FILE)
    data[photo_key] = username
    _save_json(PHOTO_UPLOADERS_FILE, data)


def _record_uploaders(photo_keys, username):
    if not photo_keys:
        return
    data = _load_json(PHOTO_UPLOADERS_FILE)
    for k in photo_keys:
        data[k] = username
    _save_json(PHOTO_UPLOADERS_FILE, data)


def _remove_uploader(photo_key):
    data = _load_json(PHOTO_UPLOADERS_FILE)
    if photo_key in data:
        del data[photo_key]
        _save_json(PHOTO_UPLOADERS_FILE, data)


def _remove_uploaders_by_prefix(prefix):
    data = _load_json(PHOTO_UPLOADERS_FILE)
    pruned = {k: v for k, v in data.items() if not k.startswith(prefix)}
    if len(pruned) != len(data):
        _save_json(PHOTO_UPLOADERS_FILE, pruned)


def _rename_uploader_key(old_key, new_key):
    data = _load_json(PHOTO_UPLOADERS_FILE)
    if old_key in data:
        data[new_key] = data.pop(old_key)
        _save_json(PHOTO_UPLOADERS_FILE, data)


def _can_edit_photo(photo_key):
    """True if current user may edit the caption / metadata of a given photo:
    admins always; uploader-role users only if they recorded the upload."""
    if not current_user.is_authenticated:
        return False
    if current_user.is_admin:
        return True
    if not getattr(current_user, "can_upload", False):
        return False
    return _load_json(PHOTO_UPLOADERS_FILE).get(photo_key) == current_user.username


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = _load_users()
        user = users.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect('/')
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(request.args.get('next', '/'))


# ── Campground data ─────────────────────────────────────────────────────────

METERS_TO_FEET = 3.281
CELSIUS_PER_DEGREE_LATITUDE = -1.0
CELSIUS_PER_METER_ALTITUDE = -0.0065
CELSIUS_TO_FAHRENHEIT = 9.0 / 5.0

CLIMATE_THRESHOLDS = [
    (-14.0, "much cooler"),
    (-9.0,  "cooler"),
    (-4.0,  "slightly cooler"),
    (4.0,   "similar to home"),
    (9.0,   "slightly warmer"),
    (14.0,  "warmer"),
    (19.0,  "much warmer"),
]


def _classify_climate(delta_temp):
    for threshold, label in CLIMATE_THRESHOLDS:
        if delta_temp <= threshold:
            return label
    return "hot"


def _campground_visits_index():
    """Map each campground_id → list of stays referencing it, oldest first.

    Each entry is `{id, number, summary, start, stay_start}` — the shape the
    campground-map popup uses to render `Trip N: Mon YYYY — summary` and link to
    `/trips/<id>`. One entry per stay, so a trip with two stays at the same
    campground appears twice (matching the main trips-map count semantics).
    trips.json is authoritative; the legacy `stays` field on campgrounds.json
    drifts as trips get edited.
    """
    visits = {}
    for trip in parse_trips():
        if trip.get("home_only"):
            continue
        for stay in trip.get("stays", []):
            cg_id = stay.get("campground_id")
            if cg_id is None:
                continue
            visits.setdefault(cg_id, []).append({
                "id": trip["id"],
                "number": trip["number"],
                "summary": trip["summary"],
                "start": trip["start"],
                "stay_start": stay.get("start", ""),
            })
    for items in visits.values():
        items.sort(key=lambda v: v.get("stay_start") or v.get("start") or "")
    return visits


def _load_campgrounds():
    """Load campground-kind entries from JSON with derived climate fields.

    Family-kind entries are excluded so they don't appear on waterfront/climate maps.
    """
    config = _load_json(HOME_FILE)
    home_lat = config.get("home_lat")
    home_alt = config.get("home_altitude_meters")
    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)
    visits_by_cg = _campground_visits_index()

    excluded = {"index", "stays", "elevation_meters"}
    rows = []
    for entry in entries:
        if "location" not in entry:
            continue
        if entry.get("kind") == "family":
            continue
        lat, lng = (float(x) for x in entry["location"].split(","))
        elev = entry.get("elevation_meters", 0)
        delta_lat = lat - home_lat
        delta_alt = elev - home_alt
        delta_celsius = (CELSIUS_PER_DEGREE_LATITUDE * delta_lat
                         + CELSIUS_PER_METER_ALTITUDE * delta_alt)
        delta_temp = delta_celsius * CELSIUS_TO_FAHRENHEIT

        row = {k: v for k, v in entry.items() if k not in excluded}
        row["elevation_feet"] = int(elev * METERS_TO_FEET)
        row["delta_temp"] = delta_temp
        row["climate"] = _classify_climate(delta_temp)
        trips_for_cg = visits_by_cg.get(entry["id"], [])
        row["trips"] = trips_for_cg
        row["visit_count"] = len(trips_for_cg)
        rows.append(row)
    return rows


def _map_config():
    """Return home coords and family locations for map rendering.

    Family entries now live in campgrounds.json with `kind: "family"`; this
    projects them into the legacy shape (`label`, `lat`, `lng`, optional
    `driveway_lat`/`driveway_lng`) consumed by the templates, plus `id`.
    """
    home_cfg = _load_json(HOME_FILE)
    lat = home_cfg.get("home_lat")
    lng = home_cfg.get("home_long")
    home = [lat, lng] if lat is not None and lng is not None else None

    family = []
    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)
    for e in entries:
        if e.get("kind") != "family" or "location" not in e:
            continue
        flat, flng = (float(x) for x in e["location"].split(","))
        fam = {"id": e["id"], "label": e["name"], "lat": flat, "lng": flng}
        dl = e.get("driveway_location")
        if dl:
            dlat, dlng = (float(x) for x in dl.split(","))
            fam["driveway_lat"] = dlat
            fam["driveway_lng"] = dlng
        family.append(fam)
    return home, family


# ── Trip routes ─────────────────────────────────────────────────────────────

@app.route('/')
@app.route('/trips')
@app.route('/trips/map')
def trips_map():
    trips = parse_trips()
    is_admin = current_user.is_authenticated and current_user.is_admin
    if not is_admin:
        trips = [t for t in trips if not t.get("home_only")]
    for trip in trips:
        enrich_trip_locations(trip)
    home, family = _map_config()

    # Collect all photos for the slideshow
    import random
    all_photos = []
    for trip in trips:
        for i, stay in enumerate(trip["stays"]):
            photo_dir = os.path.join(UPLOAD_DIR, str(trip["id"]), str(i))
            if os.path.isdir(photo_dir):
                for fname in os.listdir(photo_dir):
                    if _allowed_file(fname):
                        all_photos.append({
                            "url": f"/static/uploads/{trip['id']}/{i}/{fname}",
                            "trip_id": trip["id"],
                            "card": f"stay-{i}",
                        })
        for i, event in enumerate(trip.get("events", [])):
            photo_dir = os.path.join(UPLOAD_DIR, str(trip["id"]), "events", str(i))
            if os.path.isdir(photo_dir):
                for fname in os.listdir(photo_dir):
                    if _allowed_file(fname):
                        all_photos.append({
                            "url": f"/static/uploads/{trip['id']}/events/{i}/{fname}",
                            "trip_id": trip["id"],
                            "card": f"event-{i}",
                        })
    random.shuffle(all_photos)

    # Banner above the map links to the most recently-started visible trip.
    # `parse_trips()` already sorts ascending by start; empty new trips have
    # an empty start string and would otherwise sort first, but we walk in
    # reverse so they're skipped naturally — the banner only appears when
    # there's an actual dated trip to point at.
    latest_trip = next((t for t in reversed(trips) if t.get("start")), None)
    latest_trip_date = ""
    if latest_trip:
        try:
            latest_trip_date = date.fromisoformat(latest_trip["start"]).strftime("%b %-d, %Y")
        except (ValueError, TypeError):
            latest_trip_date = latest_trip["start"]

    return render_template('trips_map.html', trips=trips, home=home,
                           family_locations=family, active_nav='map',
                           slideshow_photos=all_photos,
                           latest_trip=latest_trip,
                           latest_trip_date=latest_trip_date)


@app.route('/trips/poster')
def trips_poster():
    """Standalone 8.5×11 portrait "poster" view of all trips.

    Intentionally not linked from the site nav — it's a direct-URL artifact for
    printing / sharing. Shares the trips-map data shape (so each trip gets the
    same resolved stay/event coordinates and the same photo pool) but renders
    a print-oriented layout: title at the top, photo thumbnail strips above
    and below, and the main map in the middle with a numbered callout per
    trip pointing to one of its stays or events. Callouts are placed by JS
    along the map perimeter after `fitBounds` settles so they never overlap.
    """
    trips = parse_trips()
    is_admin = current_user.is_authenticated and current_user.is_admin
    if not is_admin:
        trips = [t for t in trips if not t.get("home_only")]
    for trip in trips:
        enrich_trip_locations(trip)
    home, family = _map_config()

    # Photo pool — gather every uploaded image across all trips, shuffled.
    # Same shape as `trips_map`'s slideshow but typically rendered as many
    # more thumbs (the poster wants a densely-tiled border).
    import random
    all_photos = []
    for trip in trips:
        for i, stay in enumerate(trip["stays"]):
            photo_dir = os.path.join(UPLOAD_DIR, str(trip["id"]), str(i))
            if os.path.isdir(photo_dir):
                for fname in os.listdir(photo_dir):
                    if _allowed_file(fname):
                        all_photos.append({
                            "url": f"/static/uploads/{trip['id']}/{i}/{fname}",
                            "trip_id": trip["id"],
                        })
        for i, event in enumerate(trip.get("events", [])):
            photo_dir = os.path.join(UPLOAD_DIR, str(trip["id"]), "events", str(i))
            if os.path.isdir(photo_dir):
                for fname in os.listdir(photo_dir):
                    if _allowed_file(fname):
                        all_photos.append({
                            "url": f"/static/uploads/{trip['id']}/events/{i}/{fname}",
                            "trip_id": trip["id"],
                        })
    random.shuffle(all_photos)

    return render_template('trips_poster.html', trips=trips, home=home,
                           family_locations=family,
                           poster_photos=all_photos)


@app.route('/trips/calendar')
@app.route('/trips/list')
def trips_calendar():
    trips = parse_trips()
    is_admin = current_user.is_authenticated and current_user.is_admin
    if not is_admin:
        trips = [t for t in trips if not t.get("home_only")]
    for trip in trips:
        enrich_trip_locations(trip)
    initial_view = 'list' if request.path == '/trips/list' else 'calendar'
    return render_template('trips_calendar.html', trips=trips, initial_view=initial_view, active_nav=initial_view)


@app.route('/trips/stats')
def trips_stats():
    """All-time aggregates across every trip. Hero numbers (trips,
    nights, states, photos), most-visited campgrounds, trips-by-year
    bars, and the state list. Computed on every request — total
    work is O(trips + photos-on-disk), bounded enough for now."""
    trips = parse_trips()
    # Stats aggregate the camping/travel record; home-only trips aren't
    # part of that for any viewer.
    trips = [t for t in trips if not t.get("home_only")]

    total_trips = len(trips)
    total_overnight = sum(1 for t in trips if t.get("stays"))
    total_day_trips = sum(1 for t in trips if not t.get("stays") and t.get("events"))
    total_nights = sum(t.get("total_nights", 0) for t in trips)

    # Photos: walk every photo directory under each trip. Cheap — just an
    # os.listdir per stay/event index. Avoids loading photo_order.json.
    photo_count = 0
    for t in trips:
        tid = t["id"]
        for i in range(len(t.get("stays", []))):
            d = os.path.join(UPLOAD_DIR, str(tid), str(i))
            if os.path.isdir(d):
                photo_count += sum(1 for f in os.listdir(d) if _allowed_file(f))
        for i in range(len(t.get("events", []))):
            d = os.path.join(UPLOAD_DIR, str(tid), "events", str(i))
            if os.path.isdir(d):
                photo_count += sum(1 for f in os.listdir(d) if _allowed_file(f))

    # Normalize through _US_STATE_ABBR so e.g. "Pennsylvania" and "PA"
    # collapse to one entry. Anything not in the map (already an abbrev,
    # foreign, blank/odd) passes through unchanged.
    states = set()
    for t in trips:
        for s in t.get("stays", []):
            if s.get("state"):
                states.add(_US_STATE_ABBR.get(s["state"], s["state"]))
        for e in t.get("events", []):
            if e.get("state"):
                states.add(_US_STATE_ABBR.get(e["state"], e["state"]))

    # Top campgrounds by unique-trip count, by canonical place name. `place`
    # is materialized by _make_trip from campground_id, so renames don't
    # split a count across two entries. Counting trips (not stay records)
    # matches the trips map popup — a trip with multiple stay records at
    # the same place (left and returned mid-trip) still counts once.
    cg_trip_ids = {}
    for t in trips:
        for s in t.get("stays", []):
            name = (s.get("place") or "").strip()
            if name:
                cg_trip_ids.setdefault(name, set()).add(t["id"])
    top_campgrounds = [
        {"name": name, "count": len(tids)}
        for name, tids in sorted(cg_trip_ids.items(), key=lambda x: (-len(x[1]), x[0]))[:10]
        if len(tids) >= 2  # one-time visits aren't "most visited"
    ]

    # Trips-per-year. Empty-dated trips are excluded (no year to assign).
    trips_by_year = {}
    for t in trips:
        if t.get("start"):
            y = int(t["start"][:4])
            trips_by_year[y] = trips_by_year.get(y, 0) + 1
    trips_by_year_sorted = sorted(trips_by_year.items())

    return render_template(
        'trips_stats.html',
        total_trips=total_trips,
        total_overnight=total_overnight,
        total_day_trips=total_day_trips,
        total_nights=total_nights,
        photo_count=photo_count,
        states_count=len(states),
        states_list=sorted(states),
        top_campgrounds=top_campgrounds,
        trips_by_year=trips_by_year_sorted,
        active_nav='stats',
    )


@app.route('/trips/<int:trip_id>')
def trip_detail(trip_id):
    trips = parse_trips()
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        return "Trip not found", 404

    enrich_trip_locations(trip)

    captions = _load_json(CAPTIONS_FILE)

    photo_order = _load_json(PHOTO_ORDER_FILE)

    # Per-photo uploader record so the template can show editable captions on
    # an uploader-role user's own contributions while leaving others read-only.
    photo_uploaders = _load_json(PHOTO_UPLOADERS_FILE)

    stay_photos = {}
    for i, stay in enumerate(trip["stays"]):
        photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(i))
        photos = []
        if os.path.isdir(photo_dir):
            all_files = [f for f in os.listdir(photo_dir) if _allowed_file(f)]
            order_key = f"{trip_id}/{i}"
            ordered = photo_order.get(order_key)
            if ordered:
                ordered_set = set(ordered)
                fnames = [f for f in ordered if f in set(all_files)]
                fnames += sorted(f for f in all_files if f not in ordered_set)
            else:
                fnames = sorted(all_files)
            for fname in fnames:
                photo_key = f"{trip_id}/{i}/{fname}"
                photos.append({
                    "filename": fname,
                    "url": f"/static/uploads/{trip_id}/{i}/{fname}",
                    "caption": captions.get(photo_key, ""),
                    "date_taken": _photo_date_taken(os.path.join(photo_dir, fname)),
                    "uploader": photo_uploaders.get(photo_key, ""),
                })
        stay_photos[i] = photos

    event_photos = {}
    for i, event in enumerate(trip.get("events", [])):
        photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(i))
        photos = []
        if os.path.isdir(photo_dir):
            all_files = [f for f in os.listdir(photo_dir) if _allowed_file(f)]
            order_key = f"{trip_id}/events/{i}"
            ordered = photo_order.get(order_key)
            if ordered:
                ordered_set = set(ordered)
                fnames = [f for f in ordered if f in set(all_files)]
                fnames += sorted(f for f in all_files if f not in ordered_set)
            else:
                fnames = sorted(all_files)
            for fname in fnames:
                photo_key = f"{trip_id}/events/{i}/{fname}"
                photos.append({
                    "filename": fname,
                    "url": f"/static/uploads/{trip_id}/events/{i}/{fname}",
                    "caption": captions.get(photo_key, ""),
                    "date_taken": _photo_date_taken(os.path.join(photo_dir, fname)),
                    "uploader": photo_uploaders.get(photo_key, ""),
                })
        event_photos[i] = photos

    # Bucket stay photos across per-night copies for split multi-night stays.
    # Each copy is represented by (arrival + copy_num - 1) at 20:00; each photo
    # is assigned to the copy whose representative time is closest to its EXIF
    # timestamp. Photos without a timestamp fall into copy 1.
    stay_photo_times = {}
    for i, stay in enumerate(trip["stays"]):
        photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(i))
        times = {}
        if os.path.isdir(photo_dir):
            for p in stay_photos[i]:
                times[p["filename"]] = _photo_datetime_taken(
                    os.path.join(photo_dir, p["filename"]))
        stay_photo_times[i] = times

    def _bucket_photos(stay_idx, copy_num, copy_count, start_date_str):
        photos = stay_photos[stay_idx]
        if copy_count <= 1 or not start_date_str:
            return photos
        try:
            arrival = date.fromisoformat(start_date_str)
        except ValueError:
            return photos
        rep_times = [datetime.combine(arrival + timedelta(days=n - 1),
                                      dt_time(hour=20))
                     for n in range(1, copy_count + 1)]
        buckets = [[] for _ in range(copy_count)]
        for p in photos:
            t = stay_photo_times[stay_idx].get(p["filename"])
            if t is None:
                buckets[0].append(p)
                continue
            best = 0
            best_dist = abs((t - rep_times[0]).total_seconds())
            for k in range(1, copy_count):
                d = abs((t - rep_times[k]).total_seconds())
                if d < best_dist:
                    best = k
                    best_dist = d
            buckets[best].append(p)
        return buckets[copy_num - 1]

    for item in trip.get("timeline", []):
        if item.get("type") == "stay":
            item["photos"] = _bucket_photos(
                item["idx"],
                item.get("copy_num", 1),
                item.get("copy_count", 1),
                item.get("start", ""),
            )

    home, family = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin
    # Uploader-role users see the upload UI but not delete/reorder/edit
    # controls; admins are always uploaders too via the User model.
    is_uploader = (current_user.is_authenticated
                   and getattr(current_user, "can_upload", False)
                   and not is_admin)
    current_username = current_user.username if current_user.is_authenticated else ""

    # Find prev/next trip IDs (non-admins skip home-only trips in navigation)
    nav_trips = trips if is_admin else [t for t in trips if not t.get("home_only") or t["id"] == trip_id]
    nav_ids = [t["id"] for t in nav_trips]
    nav_idx = nav_ids.index(trip_id)
    prev_trip_id = nav_ids[nav_idx - 1] if nav_idx > 0 else None
    next_trip_id = nav_ids[nav_idx + 1] if nav_idx < len(nav_ids) - 1 else None

    return render_template(
        'trip_detail.html',
        trip=trip,
        stay_photos=stay_photos,
        event_photos=event_photos,
        family_locations=family,
        home=home,
        is_admin=is_admin,
        is_uploader=is_uploader,
        current_username=current_username,
        prev_trip_id=prev_trip_id,
        next_trip_id=next_trip_id,
    )


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/upload', methods=['POST'])
def upload_photo(trip_id, stay_idx):
    denied = _require_uploader_or_admin()
    if denied:
        return denied
    if 'photo' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx))
    url_prefix = f"/static/uploads/{trip_id}/{stay_idx}"

    # Zip upload — extract all images
    if file.filename.lower().endswith('.zip'):
        saved = _extract_zip_photos(file, photo_dir)
        if not saved:
            return jsonify({"error": "No image files found in zip"}), 400
        _record_uploaders([f"{trip_id}/{stay_idx}/{f}" for f in saved],
                          current_user.username)
        return jsonify({
            "files": [{"filename": f, "url": f"{url_prefix}/{f}"} for f in saved],
        })

    # Single image upload
    filename = _save_photo(file, photo_dir)
    if not filename:
        return jsonify({"error": "File type not allowed"}), 400

    _record_uploader(f"{trip_id}/{stay_idx}/{filename}", current_user.username)
    return jsonify({
        "filename": filename,
        "url": f"{url_prefix}/{filename}",
    })


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/caption', methods=['POST'])
def save_caption(trip_id, stay_idx):
    # Logged-in non-admin uploaders may only caption photos they uploaded.
    denied = _require_uploader_or_admin()
    if denied:
        return denied
    data = request.get_json()
    filename = data.get("filename", "")
    caption = data.get("caption", "")

    photo_key = f"{trip_id}/{stay_idx}/{filename}"
    if not _can_edit_photo(photo_key):
        return jsonify({"error": "You can only edit captions on photos you uploaded"}), 403
    captions = _load_json(CAPTIONS_FILE)
    captions[photo_key] = caption
    _save_json(CAPTIONS_FILE, captions)

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/photos/<filename>', methods=['DELETE'])
def delete_photo(trip_id, stay_idx, filename):
    denied = _require_admin()
    if denied:
        return denied
    filename = secure_filename(filename)
    photo_path = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx), filename)
    if os.path.exists(photo_path):
        os.remove(photo_path)

    photo_key = f"{trip_id}/{stay_idx}/{filename}"
    captions = _load_json(CAPTIONS_FILE)
    captions.pop(photo_key, None)
    _save_json(CAPTIONS_FILE, captions)

    order_key = f"{trip_id}/{stay_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    if order_key in photo_order:
        photo_order[order_key] = [f for f in photo_order[order_key] if f != filename]
        _save_json(PHOTO_ORDER_FILE, photo_order)

    _remove_uploader(photo_key)

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/photos', methods=['DELETE'])
def delete_all_stay_photos(trip_id, stay_idx):
    denied = _require_admin()
    if denied:
        return denied
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx))
    if os.path.isdir(photo_dir):
        shutil.rmtree(photo_dir)

    prefix = f"{trip_id}/{stay_idx}/"
    captions = _load_json(CAPTIONS_FILE)
    captions = {k: v for k, v in captions.items() if not k.startswith(prefix)}
    _save_json(CAPTIONS_FILE, captions)

    order_key = f"{trip_id}/{stay_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    photo_order.pop(order_key, None)
    _save_json(PHOTO_ORDER_FILE, photo_order)

    _remove_uploaders_by_prefix(prefix)

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/reorder', methods=['POST'])
def reorder_stay_photos(trip_id, stay_idx):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json()
    filenames = data.get("filenames", [])
    order_key = f"{trip_id}/{stay_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    photo_order[order_key] = filenames
    _save_json(PHOTO_ORDER_FILE, photo_order)
    return jsonify({"ok": True})


# ── Event photo routes ─────────────────────────────────────────────────────

@app.route('/trips/<int:trip_id>/events/<int:event_idx>/upload', methods=['POST'])
def upload_event_photo(trip_id, event_idx):
    denied = _require_uploader_or_admin()
    if denied:
        return denied
    if 'photo' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(event_idx))
    url_prefix = f"/static/uploads/{trip_id}/events/{event_idx}"

    # Zip upload — extract all images
    if file.filename.lower().endswith('.zip'):
        saved = _extract_zip_photos(file, photo_dir)
        if not saved:
            return jsonify({"error": "No image files found in zip"}), 400
        _record_uploaders([f"{trip_id}/events/{event_idx}/{f}" for f in saved],
                          current_user.username)
        return jsonify({
            "files": [{"filename": f, "url": f"{url_prefix}/{f}"} for f in saved],
        })

    # Single image upload
    filename = _save_photo(file, photo_dir)
    if not filename:
        return jsonify({"error": "File type not allowed"}), 400

    _record_uploader(f"{trip_id}/events/{event_idx}/{filename}",
                     current_user.username)
    return jsonify({
        "filename": filename,
        "url": f"{url_prefix}/{filename}",
    })


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/caption', methods=['POST'])
def save_event_caption(trip_id, event_idx):
    # Logged-in non-admin uploaders may only caption photos they uploaded.
    denied = _require_uploader_or_admin()
    if denied:
        return denied
    data = request.get_json()
    filename = data.get("filename", "")
    caption = data.get("caption", "")

    photo_key = f"{trip_id}/events/{event_idx}/{filename}"
    if not _can_edit_photo(photo_key):
        return jsonify({"error": "You can only edit captions on photos you uploaded"}), 403
    captions = _load_json(CAPTIONS_FILE)
    captions[photo_key] = caption
    _save_json(CAPTIONS_FILE, captions)

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/photos/<filename>', methods=['DELETE'])
def delete_event_photo(trip_id, event_idx, filename):
    denied = _require_admin()
    if denied:
        return denied
    filename = secure_filename(filename)
    photo_path = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(event_idx), filename)
    if os.path.exists(photo_path):
        os.remove(photo_path)

    photo_key = f"{trip_id}/events/{event_idx}/{filename}"
    captions = _load_json(CAPTIONS_FILE)
    captions.pop(photo_key, None)
    _save_json(CAPTIONS_FILE, captions)

    order_key = f"{trip_id}/events/{event_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    if order_key in photo_order:
        photo_order[order_key] = [f for f in photo_order[order_key] if f != filename]
        _save_json(PHOTO_ORDER_FILE, photo_order)

    _remove_uploader(photo_key)

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/photos', methods=['DELETE'])
def delete_all_event_photos(trip_id, event_idx):
    denied = _require_admin()
    if denied:
        return denied
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(event_idx))
    if os.path.isdir(photo_dir):
        shutil.rmtree(photo_dir)

    prefix = f"{trip_id}/events/{event_idx}/"
    captions = _load_json(CAPTIONS_FILE)
    captions = {k: v for k, v in captions.items() if not k.startswith(prefix)}
    _save_json(CAPTIONS_FILE, captions)

    order_key = f"{trip_id}/events/{event_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    photo_order.pop(order_key, None)
    _save_json(PHOTO_ORDER_FILE, photo_order)

    _remove_uploaders_by_prefix(prefix)

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/reorder', methods=['POST'])
def reorder_event_photos(trip_id, event_idx):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json()
    filenames = data.get("filenames", [])
    order_key = f"{trip_id}/events/{event_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    photo_order[order_key] = filenames
    _save_json(PHOTO_ORDER_FILE, photo_order)
    return jsonify({"ok": True})


# ── Trip CRUD API ──────────────────────────────────────────────────────────

@app.route('/api/trips', methods=['POST'])
def api_create_trip():
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    trip = create_trip(trip_note=data.get("trip_note", ""))
    return jsonify({"ok": True, "id": trip["id"]})


@app.route('/api/trips/<int:trip_id>', methods=['PUT'])
def api_update_trip(trip_id):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    trip = update_trip(trip_id, data)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify({"ok": True, "summary": trip["summary"]})


@app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
def api_delete_trip(trip_id):
    denied = _require_admin()
    if denied:
        return denied
    if not delete_trip(trip_id):
        return jsonify({"error": "Trip not found"}), 404
    cache_file = os.path.join(TRACK_CACHE_DIR, f"{trip_id}.json")
    if os.path.isfile(cache_file):
        os.remove(cache_file)
    return jsonify({"ok": True})


@app.route('/api/trips/<int:trip_id>/stays', methods=['POST'])
def api_add_stay(trip_id):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    trip = add_stay(trip_id, data)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify({"ok": True, "stay_count": len(trip["stays"])})


@app.route('/api/trips/<int:trip_id>/stays/<int:stay_idx>', methods=['PUT'])
def api_update_stay(trip_id, stay_idx):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    trip = update_stay(trip_id, stay_idx, data)
    if not trip:
        return jsonify({"error": "Trip or stay not found"}), 404
    return jsonify({"ok": True})


@app.route('/api/trips/<int:trip_id>/stays/<int:stay_idx>', methods=['DELETE'])
def api_delete_stay(trip_id, stay_idx):
    denied = _require_admin()
    if denied:
        return denied
    result = delete_stay(trip_id, stay_idx)
    if result is None:
        return jsonify({"error": "Trip or stay not found"}), 404
    if result == "empty":
        return jsonify({"ok": True, "trip_deleted": True})
    return jsonify({"ok": True, "trip_deleted": False})


# ── Event CRUD API ─────────────────────────────────────────────────────────

@app.route('/api/trips/<int:trip_id>/events', methods=['POST'])
def api_add_event(trip_id):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    trip = add_event(trip_id, data)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify({"ok": True, "event_count": len(trip["events"])})


@app.route('/api/trips/<int:trip_id>/events/<int:event_idx>', methods=['PUT'])
def api_update_event(trip_id, event_idx):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    trip = update_event(trip_id, event_idx, data)
    if not trip:
        return jsonify({"error": "Trip or event not found"}), 404
    return jsonify({"ok": True})


@app.route('/api/trips/<int:trip_id>/events/<int:event_idx>', methods=['DELETE'])
def api_delete_event(trip_id, event_idx):
    denied = _require_admin()
    if denied:
        return denied
    trip = delete_event(trip_id, event_idx)
    if not trip:
        return jsonify({"error": "Trip or event not found"}), 404
    return jsonify({"ok": True})


# ── Campground map routes ───────────────────────────────────────────────────

@app.route('/campgrounds/waterfront')
def campgrounds_waterfront():
    home, _ = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin
    return render_template(
        'campground_map.html',
        title='Campgrounds by Proximity to Water',
        campgrounds=_load_campgrounds(),
        color_field='waterfront',
        color_map=WATERFRONT_COLORS,
        home=home,
        family_locations=[],
        active_nav='waterfront',
        is_admin=is_admin,
    )


@app.route('/campgrounds/climate')
def campgrounds_climate():
    home, _ = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin
    return render_template(
        'campground_map.html',
        title='Campgrounds by Climate',
        campgrounds=_load_campgrounds(),
        color_field='climate',
        color_map=CLIMATE_COLORS,
        home=home,
        family_locations=[],
        active_nav='climate',
        is_admin=is_admin,
    )


# ── Photo move between stays/events ───────────────────────────────────────

@app.route('/trips/<int:trip_id>/move-photo', methods=['POST'])
def move_photo(trip_id):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    filename = data.get("filename", "")
    src_type = data.get("src_type", "")   # "stay" or "event"
    src_idx = data.get("src_idx")
    dst_type = data.get("dst_type", "")
    dst_idx = data.get("dst_idx")

    if not all([filename, src_type, dst_type,
                src_idx is not None, dst_idx is not None]):
        return jsonify({"error": "Missing fields"}), 400

    # Build source and destination paths
    def photo_dir(ptype, idx):
        if ptype == "event":
            return os.path.join(UPLOAD_DIR, str(trip_id), "events", str(idx))
        return os.path.join(UPLOAD_DIR, str(trip_id), str(idx))

    def order_key(ptype, idx):
        if ptype == "event":
            return f"{trip_id}/events/{idx}"
        return f"{trip_id}/{idx}"

    def caption_key(ptype, idx, fname):
        if ptype == "event":
            return f"{trip_id}/events/{idx}/{fname}"
        return f"{trip_id}/{idx}/{fname}"

    src_dir = photo_dir(src_type, src_idx)
    dst_dir = photo_dir(dst_type, dst_idx)
    src_path = os.path.join(src_dir, secure_filename(filename))

    if not os.path.exists(src_path):
        return jsonify({"error": "Source photo not found"}), 404

    os.makedirs(dst_dir, exist_ok=True)

    # Handle filename collision in destination
    dst_filename = secure_filename(filename)
    dst_path = os.path.join(dst_dir, dst_filename)
    if os.path.exists(dst_path):
        base, ext = os.path.splitext(dst_filename)
        dst_filename = f"{base}_{int(datetime.now().timestamp())}{ext}"
        dst_path = os.path.join(dst_dir, dst_filename)

    os.rename(src_path, dst_path)

    # Update captions
    captions = _load_json(CAPTIONS_FILE)
    old_cap_key = caption_key(src_type, src_idx, filename)
    new_cap_key = caption_key(dst_type, dst_idx, dst_filename)
    cap = captions.pop(old_cap_key, None)
    if cap:
        captions[new_cap_key] = cap
    _save_json(CAPTIONS_FILE, captions)

    # Update uploader record (same key shape as captions).
    _rename_uploader_key(old_cap_key, new_cap_key)

    # Update photo order — remove from source
    photo_order = _load_json(PHOTO_ORDER_FILE)
    src_ok = order_key(src_type, src_idx)
    if src_ok in photo_order:
        photo_order[src_ok] = [f for f in photo_order[src_ok] if f != filename]

    # Add to destination order
    dst_ok = order_key(dst_type, dst_idx)
    if dst_ok not in photo_order:
        photo_order[dst_ok] = []
    photo_order[dst_ok].append(dst_filename)

    _save_json(PHOTO_ORDER_FILE, photo_order)

    return jsonify({"ok": True, "filename": dst_filename})


# ── Campground CRUD API ────────────────────────────────────────────────────

# ── User management API (admin-only) ────────────────────────────────────────

@app.route('/admin/users')
def users_manage():
    denied = _require_admin()
    if denied:
        return redirect(url_for('login', next=request.path))
    return render_template('users_manage.html', active_nav='users')


@app.route('/api/users')
def api_user_list():
    denied = _require_admin()
    if denied:
        return denied
    data = _load_json(USERS_FILE)
    return jsonify([
        {"username": name,
         "is_admin": info.get("is_admin", False),
         "can_upload": info.get("can_upload", False)}
        for name, info in sorted(data.items())
    ])


@app.route('/api/users', methods=['POST'])
def api_user_create():
    denied = _require_admin()
    if denied:
        return denied
    body = request.get_json() or {}
    username = body.get('username', '').strip()
    password = body.get('password', '')
    is_admin = bool(body.get('is_admin'))
    can_upload = bool(body.get('can_upload'))
    if not username:
        return jsonify({"error": "Username required"}), 400
    if not password:
        return jsonify({"error": "Password required"}), 400
    data = _load_json(USERS_FILE)
    if username in data:
        return jsonify({"error": "User already exists"}), 400
    data[username] = {
        "password_hash": generate_password_hash(password),
        "is_admin": is_admin,
        "can_upload": can_upload,
    }
    _save_json(USERS_FILE, data)
    return jsonify({"ok": True})


@app.route('/api/users/<username>', methods=['PUT'])
def api_user_update(username):
    denied = _require_admin()
    if denied:
        return denied
    data = _load_json(USERS_FILE)
    if username not in data:
        return jsonify({"error": "User not found"}), 404
    body = request.get_json() or {}
    if 'password' in body:
        password = body.get('password') or ''
        if not password:
            return jsonify({"error": "Password cannot be empty"}), 400
        data[username]['password_hash'] = generate_password_hash(password)
    if 'is_admin' in body:
        new_admin = bool(body.get('is_admin'))
        if username == current_user.username and not new_admin:
            return jsonify({"error": "Cannot remove admin from your own account"}), 400
        data[username]['is_admin'] = new_admin
    if 'can_upload' in body:
        data[username]['can_upload'] = bool(body.get('can_upload'))
    _save_json(USERS_FILE, data)
    return jsonify({"ok": True})


@app.route('/api/users/<username>', methods=['DELETE'])
def api_user_delete(username):
    denied = _require_admin()
    if denied:
        return denied
    if username == current_user.username:
        return jsonify({"error": "Cannot delete your own account"}), 400
    data = _load_json(USERS_FILE)
    if username not in data:
        return jsonify({"error": "User not found"}), 404
    del data[username]
    _save_json(USERS_FILE, data)
    return jsonify({"ok": True})


@app.route('/api/campgrounds')
def api_campground_list():
    """Return a lightweight list of campground/family entries for pickers."""
    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)
    result = [{"id": e["id"], "name": e["name"],
               "state": e.get("state", ""),
               "kind": e.get("kind", "campground"),
               "location": e.get("location", "")}
              for e in entries if "id" in e and "name" in e]
    result.sort(key=lambda x: x["name"])
    return jsonify(result)


@app.route('/campgrounds/manage')
def campgrounds_manage():
    denied = _require_admin()
    if denied:
        return redirect(url_for('login', next=request.path))
    is_admin = current_user.is_authenticated and current_user.is_admin
    config = _load_json(HOME_FILE)
    home = [config.get("home_lat"), config.get("home_long")]
    return render_template('campground_manage.html', active_nav='manage',
                           is_admin=is_admin, home=home)


@app.route('/api/campgrounds/all')
def api_campground_all():
    """Return full campground data for the management page."""
    denied = _require_admin()
    if denied:
        return denied
    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)
    return jsonify(entries)


@app.route('/api/campgrounds', methods=['POST'])
def api_create_campground():
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)

    if any(e["name"] == name for e in entries):
        return jsonify({"error": "A campground with that name already exists"}), 409

    kind = data.get("kind", "campground")
    next_id = max((e["id"] for e in entries if "id" in e), default=0) + 1
    entry = {
        "id": next_id,
        "kind": kind,
        "name": name,
        "location": data.get("location", ""),
        "state": data.get("state", ""),
    }
    if kind == "family":
        if data.get("driveway_location"):
            entry["driveway_location"] = data["driveway_location"]
    else:
        entry["elevation_meters"] = float(data.get("elevation_meters", 0))
        entry["waterfront"] = data.get("waterfront", "none")
        entry["ownership"] = data.get("ownership", "")
        entry["website"] = data.get("website", "")
        entry["note"] = data.get("note", "")
        entry["phone"] = data.get("phone", "")
    entries.append(entry)
    _save_json(CAMPGROUNDS_JSON, entries)
    return jsonify({"ok": True, "id": next_id})


@app.route('/api/campgrounds/<int:cg_id>', methods=['PUT'])
def api_update_campground(cg_id):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}

    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)

    target = next((e for e in entries if e.get("id") == cg_id), None)
    if not target:
        return jsonify({"error": "Campground not found"}), 404

    new_name = data.get("name", "").strip()
    if new_name and new_name != target["name"]:
        if any(e["name"] == new_name and e is not target for e in entries):
            return jsonify({"error": "A campground with that name already exists"}), 409
        target["name"] = new_name

    for key in ("location", "elevation_meters", "waterfront", "state",
                "ownership", "website", "note", "phone",
                "kind", "driveway_location"):
        if key in data:
            val = data[key]
            if key == "elevation_meters":
                val = float(val) if val not in ("", None) else 0.0
            target[key] = val

    _save_json(CAMPGROUNDS_JSON, entries)
    return jsonify({"ok": True})


@app.route('/api/geocode')
def api_geocode():
    """Proxy geocoding lookup via Nominatim."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    try:
        import urllib.request
        url = f"https://nominatim.openstreetmap.org/search?format=json&limit=8&q={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={"User-Agent": "EkkoTrips/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return jsonify([{"name": r["display_name"], "lat": r["lat"], "lon": r["lon"]} for r in data])
    except Exception as e:
        return jsonify([])


# Full state/territory name → USPS two-letter abbreviation. Used by
# /api/reverse-geocode to normalize Nominatim's full state name to the
# 2-letter form that the rest of the project stores. Includes DC and the
# inhabited US territories so Nominatim hits in those regions also map.
_US_STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS", "Guam": "GU",
    "Northern Mariana Islands": "MP", "Puerto Rico": "PR",
    "U.S. Virgin Islands": "VI", "United States Virgin Islands": "VI",
}


_BARE_NUMBER_NAME_RE = re.compile(r'\d[\d\-\s]*[A-Za-z]?')


def _looks_like_bare_number(s):
    """True for strings that are essentially just a street-address number
    with no street name — e.g. "1234", "123 45", "1234-A". These come up
    when Nominatim reverse-resolves onto a numbered building footprint
    whose only name tag is its house number; the result is unhelpful as
    a stop label so we'd rather use a nearby POI."""
    s = (s or "").strip()
    if not s or not s[0].isdigit():
        return False
    return bool(_BARE_NUMBER_NAME_RE.fullmatch(s))


def _nominatim_nearest_poi(lat, lng):
    """Reverse-geocode restricted to POI features (Nominatim `layer=poi`).
    Returns {name, lat, lng, distance_m} for the nearest named POI or
    None when Nominatim has no real POI name in range or the call fails.

    Falls through to None — rather than to display_name — when the hit
    has no namedetails/name: an unnamed bench or sign on a highway has
    `display_name` start with the highway, and substituting that for a
    real POI just relabels the stop as the road. Leaving it None lets
    the caller try the next fallback tier (Overpass)."""
    try:
        import urllib.request
        url = (
            "https://nominatim.openstreetmap.org/reverse"
            f"?format=json&lat={lat}&lon={lng}"
            "&zoom=18&namedetails=1&layer=poi"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "EkkoTrips/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if "error" in data:
            return None
        names = data.get("namedetails", {}) or {}
        name = (names.get("name") or data.get("name") or "").strip()
        if not name:
            return None
        try:
            poi_lat = float(data.get("lat"))
            poi_lng = float(data.get("lon"))
        except (TypeError, ValueError):
            return None
        return {
            "name": name,
            "lat": poi_lat,
            "lng": poi_lng,
            "distance_m": _haversine_m(lat, lng, poi_lat, poi_lng),
        }
    except Exception:
        return None


# Max distance (meters) a POI fallback hit can be from the stop centroid
# for us to substitute it for the primary reverse-geocode name. Sized for
# a typical strip-mall / gas-station parking lot: the centroid lands a
# few dozen meters from the building, occasionally further. Tighter
# values miss real cases; looser risks picking a neighboring business
# instead of the one the user actually visited.
POI_FALLBACK_MAX_M = 150


# OSM `highway=*` values that count as "on a real road" for the
# detect-stops on-road signal — i.e. a cluster centroid snapping here is
# almost certainly a traffic jam / stop light, not a parked vehicle.
# Excludes `service` (driveways, parking aisles), `track` (forest/farm
# roads), `pedestrian`/`footway`/`path`/`cycleway`/`steps` (not driveable),
# and `construction`/`proposed` (not real). Link variants are included —
# on-ramps and off-ramps are also normal traffic-stop territory.
_ON_ROAD_HIGHWAY_TYPES = {
    "motorway", "motorway_link",
    "trunk", "trunk_link",
    "primary", "primary_link",
    "secondary", "secondary_link",
    "tertiary", "tertiary_link",
    "residential",
    "unclassified",
    "living_street",
    "road",
}


def _overpass_named_pois(lat, lng, radius_m, limit=20):
    """Query Overpass for named non-road OSM features within `radius_m`
    of (lat,lng). Returns up to `limit` results sorted by distance, each
    `{name, lat, lng, distance_m, kind}`, where `kind` is e.g.
    "amenity=restaurant" / "tourism=museum" — useful as a hint when
    multiple results share a name.

    Filters to named features that are plausibly visit-worthy:
      - amenity / tourism / shop / leisure (standard POI classes)
      - historic (monuments, memorials, ruins, archaeological sites)
      - natural (peaks, waterfalls, caves, beaches, springs — and any
        other named natural feature; the `name` requirement keeps
        anonymous woods/water polygons out)
      - landuse=cemetery (cemeteries are areas, not amenities, so they
        wouldn't surface under amenity= — added for the trip-8
        Riverside Cemetery case)
      - building (catches undertagged venues — e.g., trip-9 Rocky
        Point Creamery is `building=yes` + name only, no amenity/shop
        tag at all. Surfaces any named building, including the
        occasional named apartment complex / private home; that's
        worth the tradeoff to recover data-quality-gap cases)
      - highway=rest_area / services (the named highway subtypes)
    Excludes plain roads, anonymous landuse polygons, benches, and
    other infrastructure without a destination character.

    Shared by `_overpass_nearest_named_poi` (the reverse-geocode
    final-tier fallback — takes the first result) and the
    `/api/nearby-places` endpoint backing the name dropdown on
    event/waypoint edit forms (takes the whole list). Returns [] on
    miss or HTTP error."""
    try:
        import urllib.request
        import urllib.parse
        query = (
            "[out:json][timeout:15];"
            "("
            f"  nwr['name']['amenity'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['tourism'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['shop'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['leisure'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['historic'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['natural'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['landuse'='cemetery'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['building'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['highway'='rest_area'](around:{radius_m},{lat},{lng});"
            f"  nwr['name']['highway'='services'](around:{radius_m},{lat},{lng});"
            ");"
            "out center tags;"
        )
        data = urllib.parse.urlencode({"data": query}).encode()
        req = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=data,
            headers={"User-Agent": "EkkoTrips/1.0"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read())
        hits = []
        for e in result.get("elements", []):
            if e.get("type") == "node":
                e_lat = e.get("lat")
                e_lng = e.get("lon")
            elif "center" in e:
                e_lat = e["center"].get("lat")
                e_lng = e["center"].get("lon")
            else:
                continue
            if e_lat is None or e_lng is None:
                continue
            tags = e.get("tags") or {}
            name = (tags.get("name") or "").strip()
            if not name:
                continue
            # Pick the most specific POI-class tag for the kind hint.
            # Order matches the query above so the strongest signal wins
            # (e.g., a feature tagged both leisure=park and landuse=*
            # surfaces as leisure=park). `building` is last so a venue
            # tagged amenity=ice_cream + building=yes shows as
            # "amenity=ice_cream", not "building=yes".
            kind = ""
            for k in ("amenity", "tourism", "shop", "leisure",
                      "historic", "natural", "landuse", "highway",
                      "building"):
                if tags.get(k):
                    kind = f"{k}={tags[k]}"
                    break
            hits.append({
                "name": name,
                "lat": e_lat,
                "lng": e_lng,
                "distance_m": _haversine_m(lat, lng, e_lat, e_lng),
                "kind": kind,
            })
        hits.sort(key=lambda h: h["distance_m"])
        return hits[:limit]
    except Exception:
        return []


def _overpass_nearest_named_poi(lat, lng, radius_m=POI_FALLBACK_MAX_M):
    """Nearest named non-road OSM feature within `radius_m` of (lat,lng),
    or None on miss. Final-tier fallback in `_reverse_geocode` — see the
    `_reverse_geocode` docstring for when it fires and the trip-17 8/24
    (South Mountain Welcome Center) calibration case for why it exists.
    Thin wrapper over `_overpass_named_pois`."""
    hits = _overpass_named_pois(lat, lng, radius_m, limit=1)
    return hits[0] if hits else None


def _reverse_geocode(lat, lng):
    """Reverse-geocode coords via Nominatim. Returns
    {name, locale, state, display_name} or an empty-strings dict on failure.
    Shared by /api/reverse-geocode and the stop-detection endpoint.

    Name selection runs in three tiers, each only invoked when the
    previous one yielded a useless name:
      1. Nominatim reverse. Returns a real POI name (e.g. "Starbucks")
         in the common case and stops here.
      2. Nominatim layer=poi reverse. Fires when tier 1 hit a road
         (class=highway), a bare house number, or an unnamed feature
         whose name we had to extract from display_name (the centroid
         landed on an unnamed bench/sign/etc. — display_name's first
         segment is then the road it sits on).
      3. Overpass nearest-named-POI. Fires when tier 2 also returned
         nothing useful. Catches `highway=rest_area` / `services` and
         tourism/amenity features that Nominatim's layer=poi reverse
         can't surface because a closer unnamed feature outranks them.
         See trip-17 8/24 (South Mountain Welcome Center) in the
         `_overpass_nearest_named_poi` docstring.

    Locale and state always come from tier 1 — Overpass returns raw
    OSM without an admin hierarchy, so even Overpass-named results
    inherit the Nominatim addressdetails. Each tier's network call is
    paced with a 1-second sleep against the previous Nominatim call to
    stay under their 1 req/sec policy; Overpass is a separate service,
    but we still pace it to be polite under detection's loop cadence."""
    try:
        import urllib.request
        # zoom=18 ≈ building-level; addressdetails surfaces the
        # admin hierarchy; namedetails gives us the canonical short name
        # of whatever feature was hit (poi, road, etc.).
        url = (
            "https://nominatim.openstreetmap.org/reverse"
            f"?format=json&lat={lat}&lon={lng}"
            "&zoom=18&addressdetails=1&namedetails=1"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "EkkoTrips/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        addr = data.get("address", {}) or {}
        names = data.get("namedetails", {}) or {}
        # Prefer a real POI/feature name; fall back to display_name's first
        # comma-segment so we always return *something* useful (e.g. for a
        # ping in the middle of nowhere this becomes a road name).
        primary_name = (names.get("name") or data.get("name") or "").strip()
        name = primary_name
        if not name:
            disp = (data.get("display_name") or "").split(",", 1)[0].strip()
            name = disp
        primary_class = (data.get("class") or "").strip()
        primary_type = (data.get("type") or "").strip()
        # On-road signal for detect-stops: a cluster whose centroid snaps
        # to a real road is almost always a traffic jam / stop light
        # rather than a legitimate stop (those land in parking lots,
        # which OSM tags as amenity=parking / amenity=fuel / etc.).
        # `service` and `track` are excluded because they cover driveways
        # and parking aisles — the legitimate-stop case.
        on_road = (primary_class == "highway"
                   and primary_type in _ON_ROAD_HIGHWAY_TYPES)
        # Trigger the fallback chain when the primary hit is a road, a
        # bare house number, or had no real POI name (display_name
        # fallthrough — typically yields the road of an unnamed
        # adjacent feature like a bench or traffic sign).
        if (primary_class == "highway"
                or _looks_like_bare_number(name)
                or not primary_name):
            # Stay under Nominatim's 1 req/sec policy when the fallback
            # fires — the caller's loop throttles to 1 req/sec between
            # stops, so without an internal pause two back-to-back hits
            # could come in under a second.
            import time
            time.sleep(1.0)
            poi = _nominatim_nearest_poi(lat, lng)
            if (poi and poi["name"]
                    and not _looks_like_bare_number(poi["name"])
                    and poi["distance_m"] <= POI_FALLBACK_MAX_M):
                name = poi["name"]
            else:
                time.sleep(1.0)
                op = _overpass_nearest_named_poi(lat, lng)
                if (op and op["name"]
                        and not _looks_like_bare_number(op["name"])
                        and op["distance_m"] <= POI_FALLBACK_MAX_M):
                    name = op["name"]
        # Locale: drop down the admin hierarchy until something matches.
        locale = (addr.get("city") or addr.get("town") or addr.get("village")
                  or addr.get("hamlet") or addr.get("municipality")
                  or addr.get("township") or addr.get("county") or "")
        # State: project convention is the 2-letter USPS abbreviation
        # (campgrounds.json stores "CA", "NY", …). Prefer Nominatim's
        # ISO 3166-2 subdivision code (e.g. "US-CA"); fall back to mapping
        # the full state name; finally fall back to the raw value.
        state_full = (addr.get("state") or "").strip()
        iso = (addr.get("ISO3166-2-lvl4") or "").strip()
        state = ""
        if iso and "-" in iso:
            state = iso.split("-", 1)[1].upper()
        if not state:
            state = _US_STATE_ABBR.get(state_full, state_full)
        return {
            "name": name,
            "locale": locale,
            "state": state,
            "display_name": data.get("display_name", ""),
            "on_road": on_road,
        }
    except Exception:
        return {"name": "", "locale": "", "state": "", "display_name": "", "on_road": False}


@app.route('/api/reverse-geocode')
def api_reverse_geocode():
    """Reverse-geocode lat/lng via Nominatim. Returns the nearest named entity
    (`name`), the enclosing locale (city/town/village/hamlet — `locale`), and
    the enclosing state (`state`). Used by the trip-detail map's
    "create event from selected GPS points" feature to suggest a name and
    administrative context for the centroid of a selection."""
    try:
        lat = float(request.args.get('lat', ''))
        lng = float(request.args.get('lng', ''))
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lng required"}), 400
    return jsonify(_reverse_geocode(lat, lng))


# Default radius (metres) for /api/nearby-places. Wider than detect-stops'
# 150 m fallback radius because an admin manually placing a pin may land
# in a parking lot or on a nearby road, not on top of the building.
# 300 m covers most strip-mall / campus / large-venue cases without
# dragging in unrelated neighbors.
NEARBY_PLACES_DEFAULT_RADIUS_M = 300
NEARBY_PLACES_MAX_RADIUS_M = 1000


@app.route('/api/nearby-places')
def api_nearby_places():
    """Return up to ~20 named OSM POIs within `radius` (default 300 m,
    capped at 1000 m) of (lat,lng), sorted by distance. Backs the
    name-field dropdown on event/waypoint edit forms.

    Shares its underlying Overpass query with `_reverse_geocode`'s
    final-tier fallback, so the same tag filter set (amenity/tourism/
    shop/leisure + rest_area/services) decides what counts as a POI on
    both surfaces."""
    try:
        lat = float(request.args.get('lat', ''))
        lng = float(request.args.get('lng', ''))
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lng required"}), 400
    try:
        radius = int(request.args.get('radius', NEARBY_PLACES_DEFAULT_RADIUS_M))
    except (TypeError, ValueError):
        radius = NEARBY_PLACES_DEFAULT_RADIUS_M
    radius = max(50, min(radius, NEARBY_PLACES_MAX_RADIUS_M))
    return jsonify(_overpass_named_pois(lat, lng, radius))


TRACK_CACHE_DIR = os.path.join(TRIP_DATA_DIR, "track_cache")
os.makedirs(TRACK_CACHE_DIR, exist_ok=True)

# Frontend's auto-fallback near-anchor radius (templates/trip_detail.html
# uses the same 5 km). Promoted to a Python constant so the per-day tid
# selector (_select_track_per_day) can use the same threshold for deciding
# whether a tid's pings "encountered" a stay/event on a given day.
TRACK_NEAR_STAY_KM = 5


# Resolves lat/lng to an IANA timezone name (e.g. "America/New_York"). The
# library carries ~50 MB of polygon data; first import is slow, but the
# instance is reused. Optional dependency: if `timezonefinder` is missing
# (or fails to import on a constrained host), we silently skip enrichment
# and the frontend falls back to the browser's timezone.
_tz_finder = None
def _tz_for_coord(lat, lng):
    """Return an IANA timezone name for the given coords, or None if the
    library is unavailable / lookup fails."""
    global _tz_finder
    if _tz_finder is None:
        try:
            from timezonefinder import TimezoneFinder
            _tz_finder = TimezoneFinder()
        except Exception:
            _tz_finder = False  # sentinel: don't retry
    if not _tz_finder:
        return None
    if lat is None or lng is None:
        return None
    try:
        return _tz_finder.timezone_at(lat=lat, lng=lng)
    except Exception:
        return None


def _enrich_with_timezone(points):
    """Add an IANA `tz` field to each ping that lacks one. Returns True if
    any ping was updated (so callers can re-write the cache file)."""
    changed = False
    for p in points:
        if p.get("tz"):
            continue
        tz = _tz_for_coord(p.get("lat"), p.get("lon"))
        if tz is None and _tz_finder is False:
            return False  # library unavailable; nothing to stamp
        p["tz"] = tz or "UTC"
        changed = True
    return changed


def _relocation_lookup(items):
    """Build a precise relocation matcher from `get_relocated_pings(...)`.

    Returns a callable `lookup(ping) -> (new_lat, new_lon) | None`. Newer
    entries carry the ping's raw `orig_lat`/`orig_lon` so we can pick the
    exact one of several pings sharing a `tst`; legacy entries (no orig
    coords) match any ping with that `tst` as a wildcard — preserves the
    pre-disambiguator behavior for relocations recorded before the schema
    grew the originals.

    Bug context: OwnTracks emits duplicate-`tst` pings routinely (sometimes
    hundreds per trip, several hundred meters apart). Matching on `tst`
    alone meant dragging one ping silently dragged every sibling to the
    same coords."""
    EPS = 1e-6
    by_tst = {}
    for it in items:
        tst = int(it["tst"])
        new_pt = (float(it["lat"]), float(it["lon"]))
        if it.get("orig_lat") is not None and it.get("orig_lon") is not None:
            orig = (float(it["orig_lat"]), float(it["orig_lon"]))
        else:
            orig = None
        by_tst.setdefault(tst, []).append((orig, new_pt))

    def lookup(p):
        matches = by_tst.get(p.get("tst"))
        if not matches:
            return None
        wildcard = None
        for orig, new_pt in matches:
            if orig is None:
                wildcard = new_pt
            elif (abs(p.get("lat", 0) - orig[0]) < EPS
                  and abs(p.get("lon", 0) - orig[1]) < EPS):
                return new_pt
        return wildcard

    return lookup


def _fetch_timeline_points(tid, token, from_ts, to_ts):
    """Page through the timeline API for a single tid across a UTC range."""
    import urllib.request
    from urllib.parse import urlencode
    points = []
    cursor = from_ts
    for _ in range(20):  # hard ceiling to avoid runaway loops
        qs = urlencode({"tid": tid, "from": cursor, "to": to_ts, "limit": 10000})
        url = f"https://timeline-shadetreesoftware.pythonanywhere.com/api/v1/locations?{qs}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            page = json.loads(resp.read())
        if not page:
            break
        points.extend(page)
        if len(page) < 10000:
            break
        cursor = page[-1]["tst"] + 1
    return points


@app.route('/api/trips/<int:trip_id>/track')
@login_required
def api_trip_track(trip_id):
    """Return the GPS track for a trip from the timeline API.

    Caches results on disk. For trips that ended >7 days ago, the cache is
    served permanently; recent trips re-fetch every call so newly logged
    points show up.
    """
    trip = next((t for t in parse_trips() if t["id"] == trip_id), None)
    if not trip:
        return jsonify({"error": "trip not found"}), 404
    if not trip.get("start") or not trip.get("end"):
        return jsonify([])

    cache_file = os.path.join(TRACK_CACHE_DIR, f"{trip_id}.json")
    try:
        end_date = date.fromisoformat(trip["end"])
        is_old = (date.today() - end_date) > timedelta(days=7)
    except ValueError:
        is_old = False

    # `?admin=1` is the "include admin annotations" flag — used by the trip
    # detail page when an admin is viewing it. With the flag, suppressed
    # pings are returned tagged (so they can be revealed by the "Show
    # suppressed pings" toggle), and relocated pings are tagged with their
    # original lat/lon so the "Show relocated pings" toggle can offer undo
    # plus draw a from-here-to-there dashed line. Without the flag,
    # suppressed pings are dropped and relocations are applied silently.
    include_admin = request.args.get("admin") == "1"
    suppressed = set(get_suppressed_pings(trip_id))
    relocation_items = get_relocated_pings(trip_id)
    _relocate = _relocation_lookup(relocation_items)
    bad_windows = _bad_track_window_tsts(trip)

    def _apply_overrides(points):
        # Relocations rewrite lat/lon in place. Always applied (the polyline
        # should follow the override). Original coords are preserved only for
        # admin clients so the undo UI can draw the provenance line.
        if relocation_items:
            for p in points:
                ov = _relocate(p)
                if ov is not None:
                    if include_admin:
                        p["original_lat"] = p["lat"]
                        p["original_lon"] = p["lon"]
                        p["relocated"] = True
                    p["lat"] = ov[0]
                    p["lon"] = ov[1]
                elif include_admin:
                    p["relocated"] = False
        # Bad-track windows: pings inside an admin-marked window are known
        # to come from the wrong device (the phone was briefly with someone
        # not on the trip). Filter them out for non-admin clients; tag-and-
        # keep for admin clients so the trip-detail frontend can drop them
        # from the polyline (parallel to `suppressed`) and a future UI
        # could surface them.
        if bad_windows:
            if include_admin:
                for p in points:
                    p["bad_window"] = _in_bad_track_window(p.get("tst"), bad_windows)
            else:
                points = [p for p in points
                          if not _in_bad_track_window(p.get("tst"), bad_windows)]
        # Suppressions filter the polyline / regular markers entirely; admin
        # clients still see them tagged so the suppressed-pings ghost layer
        # has data to render.
        if not suppressed:
            return points
        if include_admin:
            for p in points:
                p["suppressed"] = (p.get("tst") in suppressed)
            return points
        return [p for p in points if p.get("tst") not in suppressed]

    def _select_chosen(all_points):
        """Run per-day tid selection on the cached/fetched raw points
        (tid-tagged) and return only the chosen tid's pings.

        The selector's *decision* runs on a cleaned view (suppressed +
        bad-window pings dropped, relocations applied) so admin-marked-
        untrusted pings can't tip the choice. Then we filter the RAW
        points by the per-day choice so the response still carries
        original coords / admin-mode tags — `_apply_overrides` below
        will re-apply relocations and emit the admin annotations.

        Pings on pad days (the ±1 day fetch overage outside the trip's
        own date range) keep today's behavior: primary-only pass-through,
        no per-day selection. They're only used by the frontend to draw
        the "leaving home" / "arriving home" boundary leg of the polyline."""
        enrich_trip_locations(trip)
        home, _fam = _map_config()
        anchors = _anchors_for_trip(trip)

        def _split_clean(want_tid):
            out = []
            for p in all_points:
                if p.get("tid") != want_tid:
                    continue
                tst = p.get("tst")
                if tst is None or tst in suppressed:
                    continue
                if _in_bad_track_window(tst, bad_windows):
                    continue
                ov = _relocate(p)
                if ov is not None:
                    p = dict(p)
                    p["lat"], p["lon"] = ov[0], ov[1]
                out.append(p)
            return out

        _, tid_choices = _select_track_per_day(
            _split_clean("primary"), _split_clean("alt"),
            anchors, home, trip["start"], trip["end"],
            tid_overrides=trip.get("tid_overrides") or {},
        )

        chosen = []
        for p in all_points:
            d = _local_date_of_ping(p)
            if d is None:
                continue
            choice = tid_choices.get(d)
            if choice is None:
                # Outside trip date range (pad day) — primary only.
                if p.get("tid") == "primary":
                    chosen.append(p)
                continue
            wanted = choice.split(":")[-1]  # 'override:alt' → 'alt'
            if p.get("tid") == wanted:
                chosen.append(p)
        chosen.sort(key=lambda x: x.get("tst", 0))
        return chosen

    def _build_response(all_points):
        """Build the track JSON: the chosen/override-applied pings plus
        the auto-detected home-boundary tsts.

        The boundary is the single source of truth for the trip window
        (polyline cuts) and the home-card "(auto)" time — the frontend
        used to recompute it in JS, which risked drifting from the
        Python detector. It's computed here on the same point view the
        old client used: chosen pings with relocations applied,
        suppressed + bad-window pings dropped, trimmed to the trip's
        local-date range, then the shared `_find_home_boundary_tsts`
        with the trip's anchors. Independent of `?admin=1` so every
        viewer sees the same window."""
        chosen = _select_chosen(all_points)
        cleaned = []
        for p in chosen:
            tst = p.get("tst")
            if tst is None or tst in suppressed:
                continue
            if _in_bad_track_window(tst, bad_windows):
                continue
            ov = _relocate(p)
            if ov is not None:
                p = {**p, "lat": ov[0], "lon": ov[1]}
            cleaned.append(p)
        cleaned = _filter_points_to_trip_window(
            cleaned, trip["start"], trip["end"])
        home, _fam = _map_config()
        hs, he = _find_home_boundary_tsts(
            cleaned, home, anchors=_anchors_for_trip(trip))
        return jsonify({
            "points": _apply_overrides(chosen),
            "home_auto_start_tst": hs,
            "home_auto_end_tst": he,
        })

    def _serve_cache():
        with open(cache_file) as f:
            cached = json.load(f)
        migrated = _migrate_track_cache_tids(cached)
        tz_changed = _enrich_with_timezone(cached)
        if migrated or tz_changed:
            with open(cache_file, "w") as f:
                json.dump(cached, f)
        return _build_response(cached)

    if is_old and os.path.isfile(cache_file):
        return _serve_cache()

    token = os.environ.get("TIMELINE_API_TOKEN")
    tid = os.environ.get("TIMELINE_TID")
    alt_tid = os.environ.get("TIMELINE_TID_ALT")
    if not token or not tid:
        # Fall back to cache if we have one, else empty (frontend handles this).
        if os.path.isfile(cache_file):
            return _serve_cache()
        return jsonify([])

    try:
        # Date-only trip range; widen by ~1 day on each side to absorb timezone
        # offsets (the trip is stored in local dates, the API speaks UTC).
        start_dt = datetime.fromisoformat(trip["start"]) - timedelta(days=1)
        end_dt = datetime.fromisoformat(trip["end"]) + timedelta(days=2)
        from_ts = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        to_ts = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        primary_pts = _fetch_timeline_points(tid, token, from_ts, to_ts)
        for p in primary_pts:
            p["tid"] = "primary"

        alt_pts = []
        if alt_tid:
            # Always fetch the full alt range now (was: only gap days),
            # since the per-day selector wants to weigh both phones on
            # every day to pick the trip phone, not just to fill holes.
            alt_pts = _fetch_timeline_points(alt_tid, token, from_ts, to_ts)
            for p in alt_pts:
                p["tid"] = "alt"

        all_points = primary_pts + alt_pts
        all_points.sort(key=lambda p: p["tst"])
    except Exception as e:
        if os.path.isfile(cache_file):
            return _serve_cache()
        return jsonify({"error": str(e)}), 502

    _enrich_with_timezone(all_points)
    with open(cache_file, "w") as f:
        json.dump(all_points, f)
    return _build_response(all_points)


# ── GPS-track stop detection ────────────────────────────────────────────────
# Admin-only feature reachable from the trip-detail page: scans the trip's
# GPS pings for dwell-time clusters that don't already correspond to a
# stay/event/family location and proposes them as new waypoints (short
# stops) or events (longer stops). The admin reviews suggestions in a
# modal and accepts the ones to create; everything created carries
# `needs_vetting: true` until the admin opens & saves the edit form.

# Tunables. Conservative defaults — adjust if detection is too noisy or
# misses real stops.
STOP_CLUSTER_RADIUS_M = 200       # max distance from a cluster's running
                                  # centroid for a ping to join the cluster.
                                  # Sized for stationary-GPS jitter rather
                                  # than the geometric extent of a stop:
                                  # two consecutive at-rest pings can land
                                  # 100–200 m apart (parking lot near a
                                  # building, urban canyon, indoor/garage
                                  # fix), and the first two pings of a
                                  # would-be cluster have no centroid
                                  # averaging yet to absorb that gap — so
                                  # the bootstrap check effectively requires
                                  # pairwise distance ≤ this. Tighter values
                                  # (tried 150) miss real ~9-minute parking
                                  # stops; wider values risk merging
                                  # genuinely-separate close stops, but the
                                  # consecutive-in-time constraint plus the
                                  # 4-minute minimum keep that risk low.
STOP_MIN_MINUTES = 4              # cluster span must reach this to qualify
STOP_BRIEF_MIN_MINUTES = 3        # relaxed floor for clusters bracketed
                                  # by fast-moving pings on both sides
                                  # (see STOP_BRIEF_BOUNDARY_KMH). Trip
                                  # 17, 8/24: a real ~3 min rest-stop
                                  # surfaced only two pings 138 m apart,
                                  # so the cluster's measured span sits
                                  # right at the floor; without the
                                  # brief-cluster carve-out the floor
                                  # had to be raised across the board
                                  # to catch it, which surfaced lots of
                                  # slow-traffic noise. The carve-out
                                  # keeps the 4 min default for ambient
                                  # clusters and only relaxes when the
                                  # surrounding speed evidence makes the
                                  # stop unambiguous.
STOP_BRIEF_BOUNDARY_KMH = 30      # min km/h between the cluster centroid
                                  # and the immediately adjacent prev/
                                  # next out-of-cluster pings for a
                                  # brief (<STOP_MIN_MINUTES) cluster to
                                  # qualify. 30 km/h is comfortably
                                  # above urban-creep / heavy-traffic
                                  # speeds (which can produce 3 min,
                                  # 2 ping clusters at red lights) but
                                  # well below normal driving — any real
                                  # arrival from / departure to a road
                                  # clears it easily. Clusters at the
                                  # very start or end of the trip have
                                  # no neighbor on one side; that side
                                  # is treated as passing (a 3 min stop
                                  # at the trip's first ping is still a
                                  # real stop).
STOP_DWELL_GAP_RADIUS_M = 600     # secondary join radius, applied only
                                  # when the next ping arrives
                                  # ≥STOP_MIN_MINUTES after the cluster's
                                  # last ping. OwnTracks may emit a ping
                                  # on arrival, sleep for many minutes
                                  # while the device is stationary, then
                                  # emit on departure — and the two
                                  # readings can jitter or drift farther
                                  # apart than STOP_CLUSTER_RADIUS_M
                                  # even though the device never moved
                                  # in any meaningful way. Calibration
                                  # cases: trip 17, 8/29 (12:31+13:19
                                  # at the same parking lot, 214 m
                                  # apart — split by the 200 m walker);
                                  # trip 16, 8/11 (18:03+18:04 dwell
                                  # followed by an 18:09 ping 525 m
                                  # away as the user pulled out of the
                                  # lot at town-driving speed — needed
                                  # the radius wider than 500 m). The
                                  # min-minutes time gap blocks this
                                  # from looser-clustering moving pings:
                                  # at 25+ mph the next ping after
                                  # 4 min is well past 600 m, so the
                                  # gap+cap pair fires only at actual
                                  # dwells. Long standstill traffic can
                                  # surface here; admin can dismiss in
                                  # the modal.
STOP_WAYPOINT_MAX_MINUTES = 30    # ≤ this → waypoint; longer → event
STOP_NEAR_ANCHOR_M = 300          # drop clusters within this of any
                                  # existing stay/event/family location
STOP_NEAR_HOME_M = 1500           # "near HOME" radius used by
                                  # _find_home_boundary_tsts: a ping
                                  # inside this radius is *eligible* to
                                  # be tagged at-home (subject to the
                                  # centroid test below). Outside this
                                  # radius is always not-at-home. Used
                                  # only to infer the trip's real
                                  # departure / arrival moments — NOT
                                  # applied as a drop-anchor on cluster
                                  # centroids, so a stop 800 m from home
                                  # that happens mid-trip (after
                                  # departure, before arrival) is still
                                  # a valid suggestion.
STOP_AT_HOME_CENTROID_M = 600     # consecutive within-NEAR_HOME pings
                                  # are grouped into a "near-home run"
                                  # and tagged at-home iff the run's
                                  # centroid is within this radius of
                                  # home. Runs whose centroid sits
                                  # farther out (e.g., a coffee shop
                                  # 1.2 km from home that happens to be
                                  # inside the 1.5 km near-home radius)
                                  # are near-home *stops*, not home
                                  # arrivals — they never bound the
                                  # trip regardless of duration. The
                                  # 600 m value matches the start of
                                  # the commercial zone around home;
                                  # the full 0–600 m residential band
                                  # is at-home, ≥600 m is eligible to
                                  # be a near-home stop. Re-tune if
                                  # the host home's neighborhood
                                  # geography differs.
STOP_HOME_BOUNDARY_LOCK_S = 3600  # sustained-away duration that confirms
                                  # a not-at-home streak is "the trip."
                                  # A brief at-Starbucks errand on trip
                                  # morning doesn't qualify; the actual
                                  # departure (where the user stays away
                                  # from home for >=1 hr) does.


def _haversine_m(lat1, lng1, lat2, lng2):
    """Great-circle distance between two coords in meters."""
    import math
    R = 6371000.0
    a1 = math.radians(lat1)
    a2 = math.radians(lat2)
    da = math.radians(lat2 - lat1)
    do = math.radians(lng2 - lng1)
    h = math.sin(da/2)**2 + math.cos(a1) * math.cos(a2) * math.sin(do/2)**2
    return 2 * R * math.asin(math.sqrt(h))


def _load_trip_track_for_detection(trip_id):
    """Return the trip's GPS pings with admin overrides honored:
    suppressed and bad-track-window pings are dropped entirely;
    relocated pings have their coords rewritten to the override target
    (same as api_trip_track) so they contribute dwell signal at the
    corrected location. Returns [] if neither cache nor API is available.

    The relocation behavior supports the workflow where an admin first
    relocates obviously-errant pings (cell-tower fixes, single jumps)
    back onto the actual trip path and then runs detect-stops, expecting
    it to credit the dwell at the corrected coords. Suppressed pings
    stay dropped (they're outright noise), and bad-window pings come
    from a phone that was off-trip for that period — neither should
    contribute to dwell clustering.

    Prefers the on-disk cache (the trip detail page's loadTrack() will
    have populated it on load) and only falls back to a fresh fetch
    when the cache is missing.

    Per-day tid selection (`_select_track_per_day`) runs after the
    admin-overrides drop, so detection sees only the chosen tid's pings
    for each day — matches what the polyline shows and avoids stop
    suggestions seeded by the wrong phone."""
    trip = next((t for t in parse_trips() if t["id"] == trip_id), None)
    if not trip or not trip.get("start") or not trip.get("end"):
        return []

    cache_file = os.path.join(TRACK_CACHE_DIR, f"{trip_id}.json")
    points = None
    if os.path.isfile(cache_file):
        try:
            with open(cache_file) as f:
                points = json.load(f)
        except Exception:
            points = None
    if points is None:
        token = os.environ.get("TIMELINE_API_TOKEN")
        tid = os.environ.get("TIMELINE_TID")
        alt_tid = os.environ.get("TIMELINE_TID_ALT")
        if not token or not tid:
            return []
        try:
            start_dt = datetime.fromisoformat(trip["start"]) - timedelta(days=1)
            end_dt = datetime.fromisoformat(trip["end"]) + timedelta(days=2)
            from_ts = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            to_ts = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            primary_pts = _fetch_timeline_points(tid, token, from_ts, to_ts)
            for p in primary_pts:
                p["tid"] = "primary"
            alt_pts = []
            if alt_tid:
                alt_pts = _fetch_timeline_points(alt_tid, token, from_ts, to_ts)
                for p in alt_pts:
                    p["tid"] = "alt"
            points = primary_pts + alt_pts
            points.sort(key=lambda p: p["tst"])
            _enrich_with_timezone(points)
            with open(cache_file, "w") as f:
                json.dump(points, f)
        except Exception:
            return []
    else:
        # Cache hit: migrate legacy untagged entries before the selector
        # runs (it groups by tid).
        if _migrate_track_cache_tids(points):
            with open(cache_file, "w") as f:
                json.dump(points, f)

    suppressed = set(get_suppressed_pings(trip_id))
    _relocate = _relocation_lookup(get_relocated_pings(trip_id))
    # Drop suppressed pings outright. For relocated pings, rewrite lat/lon
    # to the override coords (same as api_trip_track) so they contribute
    # dwell signal at the corrected location. Siblings sharing a tst whose
    # specific (tst, orig_lat, orig_lon) wasn't relocated are untouched.
    cleaned = []
    for p in points:
        if p.get("tst") in suppressed:
            continue
        ov = _relocate(p)
        if ov is not None:
            p["lat"] = ov[0]
            p["lon"] = ov[1]
        cleaned.append(p)
    points = cleaned
    bad_windows = _bad_track_window_tsts(trip)
    if bad_windows:
        points = [p for p in points
                  if not _in_bad_track_window(p.get("tst"), bad_windows)]

    # Per-day tid selection. `_select_track_per_day` already returns
    # only chosen-tid pings within [start, end] — pad days are dropped,
    # which is correct for detection (we only consider clusters inside
    # the trip itself).
    enrich_trip_locations(trip)
    home, _fam = _map_config()
    anchors = _anchors_for_trip(trip)
    p_pts = [p for p in points if p.get("tid") == "primary"]
    a_pts = [p for p in points if p.get("tid") == "alt"]
    chosen, _choices = _select_track_per_day(
        p_pts, a_pts, anchors, home, trip["start"], trip["end"],
        tid_overrides=trip.get("tid_overrides") or {},
    )
    return chosen


def _detect_stops(points,
                  cluster_radius_m=STOP_CLUSTER_RADIUS_M,
                  min_stop_minutes=STOP_MIN_MINUTES,
                  brief_min_minutes=STOP_BRIEF_MIN_MINUTES,
                  brief_boundary_kmh=STOP_BRIEF_BOUNDARY_KMH,
                  dwell_gap_radius_m=STOP_DWELL_GAP_RADIUS_M):
    """Walk pings in time order, group them into clusters where every
    ping is within `cluster_radius_m` of the cluster's running centroid.
    Clusters whose time span >= `min_stop_minutes` are returned.

    Dwell-gap exception: when the next ping arrives ≥`min_stop_minutes`
    after the cluster's last ping, the join radius widens to
    `dwell_gap_radius_m`. OwnTracks suspends reporting at a stationary
    device, so a real dwell may produce only an arrival ping and a
    departure ping — and those two can sit beyond `cluster_radius_m`
    even though nothing moved. The time-gap requirement keeps the wider
    radius from absorbing moving pings: at any drivable speed, the next
    ping after `min_stop_minutes` is well past `dwell_gap_radius_m`.

    Brief-cluster exception: clusters whose span is in
    `[brief_min_minutes, min_stop_minutes)` still qualify if both
    adjacent out-of-cluster pings imply ≥`brief_boundary_kmh` of travel
    from the cluster centroid. A real ~3 min rest-stop is bracketed by
    fast highway pings; an apparent ~3 min "stop" in stop-and-go
    traffic is bracketed by slow nearby pings and fails the gate. At
    the very first/last cluster of the trip there's no neighbor on one
    side; that side passes by default.

    Snap-back exception: a single ping that fails the join test is
    treated as an outlier — skipped, not folded in, not used to break
    the cluster — when the *next* ping would itself rejoin the current
    cluster. This defends against a momentary noisy fix (a cell-tower
    hit, a one-off jitter just past dwell_gap_radius_m) mid-dwell
    splitting a real stop into fragments too small to qualify. The
    "next ping rejoins" check is the regular join test against the
    unchanged centroid, so the snap-back is strictly more discriminating
    than widening dwell_gap_radius_m: when the device is genuinely in
    transit between two stops, no later ping snaps back and the cluster
    closes as before. Calibration case: trip 10, 4/9 19:21 (a 696 m
    drift between two 1-min-apart anchor pings at the actual stop
    location, just past the 600 m dwell radius — collapsed the dwell
    into three single-ping clusters under the old logic).

    Consecutive-in-time only: the same physical location visited twice
    on the same trip produces two clusters, which is the right behavior
    for trip-stop suggestions (one suggestion per visit)."""
    pts = sorted(
        (p for p in points
         if p.get("lat") is not None
         and p.get("lon") is not None
         and p.get("tst") is not None),
        key=lambda p: p["tst"],
    )
    # Collapse same-tst pings into one representative. Two readings
    # sharing one second — typically a phone emitting a stationary fix
    # and a stale "still moving" fix at the same wall-clock instant —
    # used to break the cluster walker: each ping must be within
    # cluster_radius_m of the running centroid, so a noisy duplicate
    # offset by a few hundred meters reset the cluster and isolated
    # the good neighbors on either side in time.
    #
    # Selection rule: pick the ping in the group whose distance to its
    # nearest unique-tst neighbor (previous or next) is smallest.
    # When duplicates straddle a stop boundary, one reading is close
    # to the surrounding stationary cluster and the other is the "in
    # transit" outlier; min-distance-to-neighbor picks the one that
    # aligns with the cluster. Arithmetic mean was tried first but
    # landed the centroid in between the two readings — for trip 19's
    # 14:39 stop that meant 264 m from the actual stop position, just
    # outside the 200 m radius, and the cluster still didn't form.
    if pts:
        deduped = []
        i = 0
        while i < len(pts):
            j = i
            while j + 1 < len(pts) and pts[j + 1]["tst"] == pts[i]["tst"]:
                j += 1
            group = pts[i:j + 1]
            if len(group) == 1:
                deduped.append(group[0])
            else:
                prev_p = deduped[-1] if deduped else None
                next_p = pts[j + 1] if j + 1 < len(pts) else None
                best = group[0]
                best_d = float("inf")
                for p in group:
                    d = float("inf")
                    if prev_p is not None:
                        d = min(d, _haversine_m(p["lat"], p["lon"],
                                                prev_p["lat"], prev_p["lon"]))
                    if next_p is not None:
                        d = min(d, _haversine_m(p["lat"], p["lon"],
                                                next_p["lat"], next_p["lon"]))
                    if d < best_d:
                        best_d = d
                        best = p
                deduped.append(best)
            i = j + 1
        pts = deduped
    stops = []
    cur = None

    def _boundary_speed_ok(c):
        c_lat = c["sum_lat"] / c["count"]
        c_lng = c["sum_lng"] / c["count"]

        def _ok(neighbor_idx, neighbor_tst):
            if neighbor_idx is None:
                return True
            n = pts[neighbor_idx]
            dt = abs(neighbor_tst - n["tst"])
            if dt <= 0:
                return False
            dm = _haversine_m(c_lat, c_lng, n["lat"], n["lon"])
            return (dm / dt) * 3.6 >= brief_boundary_kmh

        prev_idx = c["start_idx"] - 1 if c["start_idx"] > 0 else None
        next_idx = c["end_idx"] + 1 if c["end_idx"] + 1 < len(pts) else None
        return _ok(prev_idx, c["start_tst"]) and _ok(next_idx, c["end_tst"])

    def _close(c):
        if not c:
            return
        dur_min = (c["end_tst"] - c["start_tst"]) / 60.0
        qualifies = dur_min >= min_stop_minutes
        if (not qualifies
                and dur_min >= brief_min_minutes
                and _boundary_speed_ok(c)):
            qualifies = True
        if qualifies:
            stops.append({
                "center_lat": c["sum_lat"] / c["count"],
                "center_lng": c["sum_lng"] / c["count"],
                "start_tst": c["start_tst"],
                "end_tst": c["end_tst"],
                "duration_minutes": round(dur_min, 1),
                "ping_count": c["count"],
                "tz": c["tz"] or "UTC",
                # Per-ping coords retained so downstream anchor-proximity
                # tests (_drop_stops_at_known_locations) can ask "did any
                # ping in this cluster sit near a known location?" — the
                # centroid alone is a poor proxy for an asymmetric cluster
                # (long dwell + slow approach/depart pulls the centroid
                # off the actual dwell location, as on trip 9's
                # Mountain Top campsite arrival).
                "coords": list(c["coords"]),
            })

    for idx, p in enumerate(pts):
        lat, lng, tst = p["lat"], p["lon"], p["tst"]
        if cur is None:
            cur = {"sum_lat": lat, "sum_lng": lng, "count": 1,
                   "start_tst": tst, "end_tst": tst, "tz": p.get("tz"),
                   "start_idx": idx, "end_idx": idx,
                   "coords": [(lat, lng)]}
            continue
        c_lat = cur["sum_lat"] / cur["count"]
        c_lng = cur["sum_lng"] / cur["count"]

        def _joins(plat, plng, ptst):
            pd = _haversine_m(plat, plng, c_lat, c_lng)
            pgap = ptst - cur["end_tst"]
            return (pd <= cluster_radius_m
                    or (pgap >= min_stop_minutes * 60
                        and pd <= dwell_gap_radius_m))

        if _joins(lat, lng, tst):
            cur["sum_lat"] += lat
            cur["sum_lng"] += lng
            cur["count"] += 1
            cur["end_tst"] = tst
            cur["end_idx"] = idx
            cur["coords"].append((lat, lng))
        elif (idx + 1 < len(pts)
              and _joins(pts[idx + 1]["lat"],
                         pts[idx + 1]["lon"],
                         pts[idx + 1]["tst"])):
            # Snap-back: skip this lone outlier and keep the cluster
            # open; the next ping confirms the dwell didn't end here.
            continue
        else:
            _close(cur)
            cur = {"sum_lat": lat, "sum_lng": lng, "count": 1,
                   "start_tst": tst, "end_tst": tst, "tz": p.get("tz"),
                   "start_idx": idx, "end_idx": idx,
                   "coords": [(lat, lng)]}
    _close(cur)
    return stops


def _find_home_boundary_tsts(points, home,
                             home_radius_m=STOP_NEAR_HOME_M,
                             at_home_centroid_m=STOP_AT_HOME_CENTROID_M,
                             lock_seconds=STOP_HOME_BOUNDARY_LOCK_S,
                             anchors=None,
                             anchor_radius_m=TRACK_NEAR_STAY_KM * 1000):
    """Return (home_departure_tst, home_arrival_tst) — when the user
    left HOME for the trip and when they returned. Either may be None
    when home isn't configured, no pings exist, or no away period meets
    `lock_seconds`.

    SINGLE SOURCE OF TRUTH. This is the only home-boundary detector.
    The trip-detail frontend used to recompute it in JS and could
    drift from this; it now consumes the result instead. `api_trip_track`
    calls this and returns `home_auto_start_tst` / `home_auto_end_tst`
    in the track payload, which the frontend uses for both the polyline
    window cuts and the home card's "(auto)" time. Detect-stops calls
    it directly. If you change the algorithm, every consumer follows
    automatically — there is no second implementation to keep in sync.

    Algorithm:

      1. Group consecutive within-`home_radius_m` pings into near-home
         runs. Pings outside the radius break the run.
      2. Tag each run AT_HOME iff its centroid is within
         `at_home_centroid_m` of HOME. Runs that fail the centroid test
         are *near-home stops* (e.g., a coffee shop 1.2 km from home
         inside the 1.5 km radius). Per the user rule, a near-home
         stop is never a home arrival/departure, regardless of how
         long the user dwells there.
      3. Build maximal NOT_AT_HOME streaks (these include near-home
         stops). Filter to streaks lasting `lock_seconds` (1 hr) or
         longer — a brief out-and-back errand doesn't qualify as the
         trip.
      4. Anchor-aware selection. If any qualifying streak has a ping
         within `anchor_radius_m` of a trip anchor (a stay/event/
         family location, passed in `anchors`), restrict the candidate
         set to those near-anchor streaks and pick the one whose
         closest approach to an anchor is smallest (ties → longest).
         Otherwise — no anchors given, or no streak ever reached the
         itinerary — fall back to the LONGEST qualifying streak, which
         is the original behavior, byte-for-byte. `home_departure_tst`
         = the chosen streak's first NOT_AT_HOME ping;
         `home_arrival_tst` = the first AT_HOME ping immediately after
         it (the moment the user got home). If no AT_HOME pings follow
         the streak, fall back to the streak's last ping.

    The anchor step exists because "longest streak" alone mistakes a
    long same-day errand that never went to the itinerary for the
    trip, while the real trip is a shorter excursion that does reach
    an anchor (trip 87: an ~8.5 hr daytime errand ~9 km from home vs.
    the ~4 hr evening drive to a fireworks event 39 km out). It is a
    strict superset: when no anchor discriminates, output is identical
    to the old longest-streak rule.

    Any AT_HOME run — even a single ping — bounds the streak. There is
    no merge-across-brief-at-home-dwell step (a previous version
    merged streaks separated by <30 min at-home time; that caused a
    real arrival home followed by an afternoon errand to be missed
    because the algorithm picked the errand instead of the trip).

    The longest-streak fallback (vs. first or last) still handles the
    workday-before-trip case (the workday is shorter than the trip)
    and the errand-after-arrival case (the errand is shorter than the
    trip) without time-window heuristics; the anchor step in 4 sits in
    front of it for the case those size assumptions don't hold."""
    if not home or home[0] is None or home[1] is None:
        return None, None
    home_lat, home_lng = home[0], home[1]
    pts = sorted(
        (p for p in points
         if p.get("lat") is not None
         and p.get("lon") is not None
         and p.get("tst") is not None),
        key=lambda p: p["tst"],
    )
    n = len(pts)
    if n == 0:
        return None, None

    # 1-2. Classify each ping. Group consecutive within-radius pings
    # into a run, compute its centroid, and tag the whole run AT_HOME
    # only if the centroid passes the at-home test. Pings outside
    # home_radius_m are NOT_AT_HOME by default.
    at_home = [False] * n
    i = 0
    while i < n:
        if _haversine_m(pts[i]["lat"], pts[i]["lon"],
                        home_lat, home_lng) > home_radius_m:
            i += 1
            continue
        j = i
        sum_lat = 0.0
        sum_lng = 0.0
        while j < n and _haversine_m(pts[j]["lat"], pts[j]["lon"],
                                     home_lat, home_lng) <= home_radius_m:
            sum_lat += pts[j]["lat"]
            sum_lng += pts[j]["lon"]
            j += 1
        cnt = j - i
        c_dist = _haversine_m(sum_lat / cnt, sum_lng / cnt,
                              home_lat, home_lng)
        if c_dist <= at_home_centroid_m:
            for k in range(i, j):
                at_home[k] = True
        i = j

    # 3. NOT_AT_HOME streaks.
    streaks = []
    cur_start = None
    for k in range(n):
        if at_home[k]:
            if cur_start is not None:
                streaks.append((cur_start, k - 1))
                cur_start = None
        else:
            if cur_start is None:
                cur_start = k
    if cur_start is not None:
        streaks.append((cur_start, n - 1))

    qualified = [(s, e) for s, e in streaks
                 if pts[e]["tst"] - pts[s]["tst"] >= lock_seconds]
    if not qualified:
        return None, None

    # 4. Anchor-aware selection. For each qualifying streak, find its
    # closest approach (in metres) to any trip anchor. If at least one
    # streak comes within anchor_radius_m of an anchor, restrict the
    # candidate set to those and pick the closest (ties → longest);
    # otherwise fall back to the longest qualifying streak, which is
    # exactly the original behavior. Degrades to longest-streak when
    # `anchors` is empty/None, so callers that don't care are unaffected.
    anchor_list = [(a[0], a[1]) for a in (anchors or [])
                   if a and a[0] is not None and a[1] is not None]

    def _streak_min_anchor_m(se):
        if not anchor_list:
            return float("inf")
        best = float("inf")
        for k in range(se[0], se[1] + 1):
            for a_lat, a_lng in anchor_list:
                d = _haversine_m(pts[k]["lat"], pts[k]["lon"], a_lat, a_lng)
                if d < best:
                    best = d
        return best

    def _dur(se):
        return pts[se[1]]["tst"] - pts[se[0]]["tst"]

    near = [se for se in qualified
            if _streak_min_anchor_m(se) <= anchor_radius_m]
    if near:
        # Closest approach wins; ties broken by longer duration.
        main_s, main_e = min(
            near, key=lambda se: (_streak_min_anchor_m(se), -_dur(se))
        )
    else:
        main_s, main_e = max(qualified, key=_dur)
    home_departure_tst = pts[main_s]["tst"]
    home_arrival_tst = (pts[main_e + 1]["tst"]
                        if main_e + 1 < n else pts[main_e]["tst"])
    return home_departure_tst, home_arrival_tst


def _trip_local_to_tst(date_str, time_str, tz_name):
    """Convert a `YYYY-MM-DD` date + `HH:MM` time (interpreted in the
    given IANA timezone) to a UTC epoch second. Returns None when any
    input is missing/malformed or `zoneinfo` is unavailable.

    Used to interpret a trip's manual `home_start_time` /
    `home_end_time` overrides against the trip's date — the home card
    treats those as the authoritative trip window edges, so detection
    should too."""
    if not date_str or not time_str:
        return None
    try:
        from zoneinfo import ZoneInfo
        y, m, d = (int(x) for x in date_str.split('-'))
        hh, mm = (int(x) for x in time_str.split(':'))
        tz = ZoneInfo(tz_name) if tz_name else None
        return int(datetime(y, m, d, hh, mm, 0, tzinfo=tz).timestamp())
    except Exception:
        return None


def _bad_track_window_tsts(trip, home=None):
    """Convert a trip's `bad_track_windows` JSON into a list of
    `(start_tst, end_tst)` tuples. Each entry in the source list is
    `{start: "YYYY-MM-DDTHH:MM", end: "...", note: "..."}` with times
    interpreted in the home timezone — same convention as
    `home_start_time` / `home_end_time`, and the same `_trip_local_to_tst`
    helper does the conversion.

    Returns `[]` when the trip has no `bad_track_windows`, when home is
    unconfigured, or when no entry parses cleanly. Malformed entries
    are silently skipped: a bad-window list is admin-edited JSON, so a
    typo costs one window but doesn't break the rest of the trip's
    track rendering.

    Pass a pre-loaded `home = (lat, lng)` to avoid the `_map_config()`
    call on hot paths; default lazy-loads it."""
    windows_raw = trip.get("bad_track_windows") or []
    if not windows_raw:
        return []
    if home is None:
        home, _ = _map_config()
    home_tz_name = (
        _tz_for_coord(home[0], home[1])
        if home and home[0] is not None and home[1] is not None
        else None
    )

    def _split(dt_str):
        # Accept either "YYYY-MM-DDTHH:MM" or "YYYY-MM-DD HH:MM" — both
        # natural to type by hand.
        for sep in ("T", " "):
            if sep in dt_str:
                parts = dt_str.split(sep, 1)
                if len(parts) == 2 and parts[0] and parts[1]:
                    return parts[0], parts[1]
        return None, None

    out = []
    for w in windows_raw:
        s_raw = (w.get("start") or "").strip()
        e_raw = (w.get("end") or "").strip()
        sd, st = _split(s_raw)
        ed, et = _split(e_raw)
        if not sd or not ed:
            continue
        s_tst = _trip_local_to_tst(sd, st, home_tz_name)
        e_tst = _trip_local_to_tst(ed, et, home_tz_name)
        if s_tst is None or e_tst is None:
            continue
        if s_tst > e_tst:
            s_tst, e_tst = e_tst, s_tst
        out.append((s_tst, e_tst))
    return out


def _in_bad_track_window(tst, windows):
    """True iff `tst` falls inside any `(start, end)` window."""
    if tst is None or not windows:
        return False
    for s, e in windows:
        if s <= tst <= e:
            return True
    return False


def _local_date_of_ping(p):
    """Return the local-date (YYYY-MM-DD) of a single ping, using its
    `tz` field stamped by `_enrich_with_timezone`. Falls back to UTC
    if the field is missing or zoneinfo is unavailable. Returns None
    if the ping has no `tst`.

    Shared by `_filter_points_to_trip_window` (date-range gate) and
    `_select_track_per_day` (per-day bucketing) so both agree on which
    day a midnight-adjacent ping belongs to."""
    tst = p.get("tst")
    if tst is None:
        return None
    try:
        from zoneinfo import ZoneInfo
    except Exception:
        ZoneInfo = None
    utc = datetime.utcfromtimestamp(tst)
    tz_name = p.get("tz") or "UTC"
    if ZoneInfo and tz_name != "UTC":
        try:
            return utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(
                ZoneInfo(tz_name)).date().isoformat()
        except Exception:
            pass
    return utc.date().isoformat()


def _anchors_for_trip(trip):
    """Stay coords + event coords for a trip, suitable as anchor input
    to `_select_track_per_day`. HOME is intentionally excluded (a day
    where one phone stayed home would otherwise wrongly "encounter"
    home all day and win). Trip must be `enrich_trip_locations`-ed."""
    anchors = []
    for s in trip.get("stays", []):
        if s.get("lat") is not None and s.get("lng") is not None:
            anchors.append((s["lat"], s["lng"]))
    for e in trip.get("events", []):
        if e.get("lat") is not None and e.get("lng") is not None:
            anchors.append((e["lat"], e["lng"]))
    return anchors


def _migrate_track_cache_tids(points):
    """Stamp legacy untagged cached pings with `tid: "primary"`.
    Returns True if anything changed (so the caller can rewrite the
    cache file). Safe because the alt tid had zero pings before this
    change shipped (verified empirically across all production trips);
    every cached point was sourced from primary."""
    changed = False
    for p in points:
        if "tid" not in p:
            p["tid"] = "primary"
            changed = True
    return changed


def _filter_points_to_trip_window(points, trip_start, trip_end):
    """Drop pings whose *local* date falls outside the trip's
    [trip_start, trip_end] inclusive range. The track loader pads the
    API fetch by ~1 day on each side for timezone slop; this tightens
    back to the trip's real window so pre-/post-trip home stops don't
    become suggestions."""
    out = []
    for p in points:
        d = _local_date_of_ping(p)
        if d is not None and trip_start <= d <= trip_end:
            out.append(p)
    return out


def _select_track_per_day(primary_points, alt_points, anchors, home,
                          trip_start, trip_end, tid_overrides=None,
                          near_radius_km=TRACK_NEAR_STAY_KM):
    """Pick the right tid (primary or alt) for each day of the trip and
    return only that tid's pings.

    Inputs:
      primary_points, alt_points: lists of ping dicts with `lat`, `lon`,
        `tst`, and ideally `tz` (used to bucket by local date).
      anchors: iterable of (lat, lng) tuples — the trip's stay coords
        and event coords. HOME is intentionally NOT an anchor (a day
        where one phone stayed home would otherwise wrongly "encounter"
        home all day and win every comparison).
      home: (home_lat, home_lng) or None. Used only by case E (day-1
        fallback when neither tid has hit any anchor yet).
      trip_start, trip_end: 'YYYY-MM-DD' strings, inclusive.
      tid_overrides: dict {'YYYY-MM-DD': 'primary'|'alt'} from the trip
        record. Empty/missing keys defer to the heuristic.
      near_radius_km: anchor-encounter radius (default
        TRACK_NEAR_STAY_KM = 5 km).

    Algorithm per day in chronological order:
      A. tid_overrides[date] set → use that tid.
      B. Exactly one tid has pings today → use it (subsumes the
         existing alt-tid gap-fill).
      C. Neither has pings → record the previous day's choice for
         continuity, contribute nothing.
      D. Both have pings:
         - For each tid, count the number of distinct anchors that
           have at least one ping within `near_radius_km` today.
         - Higher count wins. This is a proxy for "which phone
           actually followed the trip today" — a phone that shared
           a morning at the campground and then diverged hits only
           that one anchor, while the trip phone goes on to hit the
           day's other events too.
         - Tied at any positive count → primary wins. (Both phones
           visited the same anchor set; no signal to distinguish.)
         - Tied at zero (neither encountered any anchor today):
             previous day has a locked-in choice → inherit it.
             else, day-1 fallback: tid with greater max-distance-
               from-home today wins; tie → primary. If home not
               configured → primary.

    Returns (chosen_points, tid_choices):
      chosen_points: list of pings sorted by `tst`, the chosen tid's
        pings concatenated across all days in the trip window.
      tid_choices: {'YYYY-MM-DD': 'primary'|'alt'|'override:primary'|
        'override:alt'} — full per-day record for admin visibility,
        including days where no pings exist.
    """
    near_radius_m = near_radius_km * 1000.0

    def _bucket(pts):
        out = {}
        for p in pts:
            d = _local_date_of_ping(p)
            if d is None:
                continue
            out.setdefault(d, []).append(p)
        return out

    primary_by_day = _bucket(primary_points or [])
    alt_by_day = _bucket(alt_points or [])

    try:
        start = date.fromisoformat(trip_start)
        end = date.fromisoformat(trip_end)
    except (TypeError, ValueError):
        return [], {}

    anchor_list = [(a[0], a[1]) for a in (anchors or [])
                   if a is not None and a[0] is not None and a[1] is not None]
    home_lat = home[0] if home and home[0] is not None else None
    home_lng = home[1] if home and home[1] is not None else None
    overrides = tid_overrides or {}

    def _distinct_anchor_count(pts):
        """Number of distinct anchors with at least one within-
        near_radius_m ping in `pts`. The per-day primary/alt
        discriminator: a phone that diverged from the trip after a
        shared morning encounter will hit fewer subsequent anchors
        than the phone that stayed on the trip."""
        n = 0
        for a_lat, a_lng in anchor_list:
            for p in pts:
                lat, lon = p.get("lat"), p.get("lon")
                if lat is None or lon is None:
                    continue
                if _haversine_m(lat, lon, a_lat, a_lng) <= near_radius_m:
                    n += 1
                    break
        return n

    def _max_dist_from_home(pts):
        if home_lat is None or home_lng is None:
            return 0.0
        best = 0.0
        for p in pts:
            lat, lon = p.get("lat"), p.get("lon")
            if lat is None or lon is None:
                continue
            d = _haversine_m(lat, lon, home_lat, home_lng)
            if d > best:
                best = d
        return best

    tid_choices = {}
    chosen = []
    prev_choice = None

    cur = start
    while cur <= end:
        date_iso = cur.isoformat()
        p_pts = primary_by_day.get(date_iso, [])
        a_pts = alt_by_day.get(date_iso, [])

        ov = overrides.get(date_iso)
        if ov in ("primary", "alt"):
            chosen.extend(p_pts if ov == "primary" else a_pts)
            tid_choices[date_iso] = "override:" + ov
            prev_choice = ov
        elif p_pts and not a_pts:
            chosen.extend(p_pts)
            tid_choices[date_iso] = "primary"
            prev_choice = "primary"
        elif a_pts and not p_pts:
            chosen.extend(a_pts)
            tid_choices[date_iso] = "alt"
            prev_choice = "alt"
        elif not p_pts and not a_pts:
            # No data either way — record prev for inheritance continuity,
            # but contribute nothing. (Default to "primary" if we haven't
            # made any decision yet; doesn't affect output since both
            # buckets are empty.)
            tid_choices[date_iso] = prev_choice or "primary"
        else:
            p_count = _distinct_anchor_count(p_pts)
            a_count = _distinct_anchor_count(a_pts)
            if p_count > a_count:
                choice = "primary"
            elif a_count > p_count:
                choice = "alt"
            elif p_count > 0:
                # Tied at >0 → primary. Both phones visited the same
                # set of anchors today; no good signal to distinguish.
                choice = "primary"
            elif prev_choice is not None:
                # Tied at 0 (neither encountered an anchor) → inherit.
                choice = prev_choice
            else:
                # Day-1 fallback: farthest from home, tie → primary.
                pd = _max_dist_from_home(p_pts)
                ad = _max_dist_from_home(a_pts)
                choice = "primary" if pd >= ad else "alt"
            chosen.extend(p_pts if choice == "primary" else a_pts)
            tid_choices[date_iso] = choice
            prev_choice = choice

        cur += timedelta(days=1)

    chosen.sort(key=lambda p: p.get("tst", 0))
    return chosen, tid_choices


def _drop_stops_at_known_locations(stops, trip, family_locations, home=None,
                                   near_radius_m=STOP_NEAR_ANCHOR_M,
                                   home_radius_m=STOP_AT_HOME_CENTROID_M):
    """Filter out clusters where any ping in the cluster falls within
    `near_radius_m` of an existing stay (campsite_location override or
    campground coords), event (waypoints included), or family location
    (listed coords + driveway coords). `trip` must be enriched via
    `enrich_trip_locations` so stays/events carry lat/lng.

    "Any ping in the cluster" — not just the centroid — is the
    discriminator. An asymmetric cluster (long dwell at anchor + slow
    approach pings tailing off toward a highway) has its centroid
    pulled away from the anchor by the off-anchor pings; a centroid-
    only test misses the case (trip 9 Mountain Top: centroid 314 m
    from anchor but pings inside the cluster sat 0 m and 49 m from
    it).

    Stay and event anchors are *date-bounded*: a cluster is only
    suppressed by a stay/event whose own date range overlaps the
    cluster's local-date range. This lets the same physical location
    surface as a separate suggestion when it's visited on two
    different days of the trip and only one of those visits has an
    event recorded — e.g., trip 19 stopped near "Lake Rowena" on Sept
    29 and again on Oct 1; the Oct 1 visit is captured as an event,
    so the Sept 29 cluster used to be dropped by the same anchor
    even though it represents an unrecorded stop. Cluster local
    dates are derived from `start_tst`/`end_tst` via the cluster's
    `tz` (IANA zone at the recording location). Stay range is
    `[start, end]` inclusive; event range is `[date, end_date or
    date]` inclusive.

    Family locations have no inherent date (they live in
    campgrounds.json, not on the trip), so they remain date-agnostic
    anchors — a near-pass to a family house always suppresses the
    cluster regardless of which day it happened.

    HOME is treated specially: clusters whose centroid is within
    `home_radius_m` (default `STOP_AT_HOME_CENTROID_M` = 600 m) of HOME
    are dropped. That's the same residential-band threshold the
    boundary detector uses to classify pings as at-home, so any
    cluster centered there is a home-arrival/departure dwell, not a
    real stop. This catches the edge case where the manual
    `home_start_time` / `home_end_time` override is rounded a minute
    or two off the true arrival, so a cluster centered at home that
    starts just inside the trip window (start_tst <= home_arrival_tst)
    survives the boundary-tst filter. Clusters between
    `home_radius_m` and `STOP_NEAR_HOME_M` — e.g., a coffee shop 1.2
    km from home that's inside the 1.5 km near-home radius — are
    still fair game when they fall inside the inferred trip window;
    those are near-home stops, not home dwell."""
    def _iso_to_date(s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s).date()
        except Exception:
            return None

    dated_anchors = []  # (lat, lng, start_date, end_date) — inclusive
    for s in trip.get("stays", []):
        if s.get("lat") is None or s.get("lng") is None:
            continue
        sd = _iso_to_date(s.get("start"))
        if sd is None:
            continue
        ed = _iso_to_date(s.get("end")) or sd
        if ed < sd:
            ed = sd
        dated_anchors.append((s["lat"], s["lng"], sd, ed))
    for e in trip.get("events", []):
        if e.get("lat") is None or e.get("lng") is None:
            continue
        sd = _iso_to_date(e.get("date"))
        if sd is None:
            continue
        ed = _iso_to_date(e.get("end_date")) or sd
        if ed < sd:
            ed = sd
        dated_anchors.append((e["lat"], e["lng"], sd, ed))

    date_agnostic_anchors = []
    for fam in family_locations:
        if fam.get("lat") is not None and fam.get("lng") is not None:
            date_agnostic_anchors.append((fam["lat"], fam["lng"]))
        if fam.get("driveway_lat") is not None and fam.get("driveway_lng") is not None:
            date_agnostic_anchors.append((fam["driveway_lat"], fam["driveway_lng"]))

    home_lat = home[0] if home and home[0] is not None else None
    home_lng = home[1] if home and home[1] is not None else None

    try:
        from zoneinfo import ZoneInfo
    except Exception:
        ZoneInfo = None

    def _cluster_date_range(c):
        tz_name = c.get("tz") or "UTC"
        tz = None
        if ZoneInfo:
            try:
                tz = ZoneInfo(tz_name)
            except Exception:
                tz = None

        def _to_local_date(tst):
            utc = datetime.utcfromtimestamp(tst)
            if tz is not None:
                try:
                    return utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz).date()
                except Exception:
                    pass
            return utc.date()

        sd = _to_local_date(c["start_tst"])
        ed = _to_local_date(c["end_tst"])
        if ed < sd:
            ed = sd
        return sd, ed

    # Anchor proximity is tested against ANY ping in the cluster, not
    # just the centroid. An asymmetric cluster (long dwell at anchor +
    # several slow approach/departure pings drifting toward the highway)
    # has its centroid pulled off the anchor — far enough to clear
    # `near_radius_m` even when the dwell itself sat directly on top of
    # it. Trip 9, Mountain Top campsite: the overnight dwell + 5
    # arrival pings + 2 departure pings formed one cluster whose
    # centroid was 314 m from the stay's campsite_location anchor (just
    # past STOP_NEAR_ANCHOR_M = 300), but two pings inside the cluster
    # were 0 m and 49 m from it. Cached cluster coords (`coords`) cost
    # ~5–15 lat/lng pairs per cluster; trivial.
    #
    # HOME is still tested against the centroid — the semantic is
    # different. The home drop is "this whole cluster is at home"
    # (catches arrival/departure jitter when the manual home_*_time
    # override is a minute off), not "this cluster passed through
    # home". A real stop near home should NOT be dropped just because
    # a single ping wandered close to the home centroid.
    def _any_ping_within(c, a_lat, a_lng, radius_m):
        for p_lat, p_lng in c.get("coords") or [(c["center_lat"], c["center_lng"])]:
            if _haversine_m(p_lat, p_lng, a_lat, a_lng) < radius_m:
                return True
        return False

    out = []
    for c in stops:
        if home_lat is not None and home_lng is not None:
            if _haversine_m(c["center_lat"], c["center_lng"],
                            home_lat, home_lng) < home_radius_m:
                continue
        too_close = False
        for a_lat, a_lng in date_agnostic_anchors:
            if _any_ping_within(c, a_lat, a_lng, near_radius_m):
                too_close = True
                break
        if not too_close and dated_anchors:
            c_start, c_end = _cluster_date_range(c)
            for a_lat, a_lng, a_start, a_end in dated_anchors:
                if a_end < c_start or a_start > c_end:
                    continue
                if _any_ping_within(c, a_lat, a_lng, near_radius_m):
                    too_close = True
                    break
        if not too_close:
            out.append(c)
    return out


@app.route('/api/trips/<int:trip_id>/suppress-pings', methods=['POST'])
def api_suppress_pings(trip_id):
    """Mark a list of GPS-ping timestamps as suppressed for this trip."""
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    tsts = data.get("tst") or []
    if not isinstance(tsts, list):
        return jsonify({"error": "tst must be a list of integers"}), 400
    result = add_suppressed_pings(trip_id, tsts)
    if result is None:
        return jsonify({"error": "trip not found"}), 404
    return jsonify({"ok": True, "suppressed_pings": result})


@app.route('/api/trips/<int:trip_id>/suppress-pings', methods=['DELETE'])
def api_unsuppress_pings(trip_id):
    """Remove a list of GPS-ping timestamps from this trip's suppressed list."""
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    tsts = data.get("tst") or []
    if not isinstance(tsts, list):
        return jsonify({"error": "tst must be a list of integers"}), 400
    result = remove_suppressed_pings(trip_id, tsts)
    if result is None:
        return jsonify({"error": "trip not found"}), 404
    return jsonify({"ok": True, "suppressed_pings": result})


@app.route('/api/trips/<int:trip_id>/relocate-pings', methods=['POST'])
def api_relocate_pings(trip_id):
    """Override the lat/lon for a list of GPS pings. Body:
    {items: [{tst, lat, lon, orig_lat, orig_lon}, ...]}. The orig coords
    are the ping's raw OwnTracks position at drag-start; they disambiguate
    duplicate-tst pings so a single drag only moves the picked one.
    Re-relocating an existing (tst, orig_lat, orig_lon) replaces its target."""
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    items = data.get("items") or []
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list of {tst, lat, lon}"}), 400
    cleaned = []
    for it in items:
        if not isinstance(it, dict):
            return jsonify({"error": "each item must be an object"}), 400
        try:
            entry = {
                "tst": int(it["tst"]),
                "lat": float(it["lat"]),
                "lon": float(it["lon"]),
            }
            if it.get("orig_lat") is not None and it.get("orig_lon") is not None:
                entry["orig_lat"] = float(it["orig_lat"])
                entry["orig_lon"] = float(it["orig_lon"])
            cleaned.append(entry)
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "each item needs integer tst and numeric lat/lon"}), 400
    result = add_relocated_pings(trip_id, cleaned)
    if result is None:
        return jsonify({"error": "trip not found"}), 404
    return jsonify({"ok": True, "relocated_pings": result})


@app.route('/api/trips/<int:trip_id>/relocate-pings', methods=['DELETE'])
def api_unrelocate_pings(trip_id):
    """Remove relocations. Either body shape works:
      {items: [{tst, orig_lat, orig_lon}, ...]}  — precise removal
      {tst: [...]}                                — coarse (removes every
                                                    entry with that tst)
    The next /track call returns the original OwnTracks coords."""
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    items = data.get("items")
    tsts = data.get("tst")
    if items is not None:
        if not isinstance(items, list):
            return jsonify({"error": "items must be a list"}), 400
        cleaned = []
        for it in items:
            if not isinstance(it, dict):
                return jsonify({"error": "each item must be an object"}), 400
            try:
                entry = {"tst": int(it["tst"])}
                if it.get("orig_lat") is not None and it.get("orig_lon") is not None:
                    entry["orig_lat"] = float(it["orig_lat"])
                    entry["orig_lon"] = float(it["orig_lon"])
                cleaned.append(entry)
            except (KeyError, TypeError, ValueError):
                return jsonify({"error": "each item needs integer tst"}), 400
        result = remove_relocated_pings(trip_id, items=cleaned)
    elif tsts is not None:
        if not isinstance(tsts, list):
            return jsonify({"error": "tst must be a list of integers"}), 400
        result = remove_relocated_pings(trip_id, tsts=tsts)
    else:
        return jsonify({"error": "must provide items or tst"}), 400
    if result is None:
        return jsonify({"error": "trip not found"}), 404
    return jsonify({"ok": True, "relocated_pings": result})


@app.route('/api/trips/<int:trip_id>/tid-overrides', methods=['PUT'])
def api_set_tid_override(trip_id):
    """Set or clear one day's per-day tid override. Body:
    {date: 'YYYY-MM-DD', value: 'primary'|'alt'|null}. null clears.

    The override forces `_select_track_per_day` to use that tid for
    the day regardless of the heuristic — admin escape hatch when
    auto picks the wrong phone. Returns the resulting overrides
    dict (omitted from trips.json entirely when empty)."""
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    day = (data.get("date") or "").strip()
    value = data.get("value")
    if not day:
        return jsonify({"error": "date is required (YYYY-MM-DD)"}), 400
    try:
        date.fromisoformat(day)
    except ValueError:
        return jsonify({"error": "date must be YYYY-MM-DD"}), 400
    if value is not None and value not in ("primary", "alt"):
        return jsonify({"error": "value must be 'primary', 'alt', or null"}), 400
    result = set_tid_override(trip_id, day, value)
    if result is None:
        return jsonify({"error": "trip not found"}), 404
    return jsonify({"ok": True, "tid_overrides": result})


@app.route('/api/trips/<int:trip_id>/tid-choices', methods=['GET'])
def api_tid_choices(trip_id):
    """Admin-only: return what the per-day tid selector would pick for
    each trip day ignoring overrides, plus the current saved overrides,
    plus per-tid ping counts per day. The Track Source UI uses this
    to render "auto would pick X" alongside the override radios.

    Computes against the cached track (same source the track endpoint
    serves). Returns:
      {
        "tid_choices":  {"YYYY-MM-DD": "primary"|"alt", ...},  # auto only
        "tid_overrides":{"YYYY-MM-DD": "primary"|"alt", ...},  # saved
        "counts":       {"YYYY-MM-DD": {"primary": N, "alt": M}, ...},
        "alt_configured": bool,
      }
    No `?include_admin=1` flag — this endpoint is admin-only and the
    track endpoint's bare-array response shape stays unchanged."""
    denied = _require_admin()
    if denied:
        return denied
    trip = next((t for t in parse_trips() if t["id"] == trip_id), None)
    if not trip:
        return jsonify({"error": "trip not found"}), 404
    if not trip.get("start") or not trip.get("end"):
        return jsonify({"tid_choices": {}, "tid_overrides": {},
                        "counts": {}, "alt_configured": False})

    cache_file = os.path.join(TRACK_CACHE_DIR, f"{trip_id}.json")
    cached = []
    if os.path.isfile(cache_file):
        try:
            with open(cache_file) as f:
                cached = json.load(f)
            _migrate_track_cache_tids(cached)
        except Exception:
            cached = []

    enrich_trip_locations(trip)
    home, _fam = _map_config()
    anchors = _anchors_for_trip(trip)
    # Clean pings (drop suppressed/bad-window, apply relocations) to
    # match what the wired selector actually decides on. Without this
    # the UI's "auto" preview can diverge from the polyline's choice.
    suppressed = set(get_suppressed_pings(trip_id))
    _relocate = _relocation_lookup(get_relocated_pings(trip_id))
    bad_windows = _bad_track_window_tsts(trip)

    def _clean(want_tid):
        out = []
        for p in cached:
            if p.get("tid") != want_tid:
                continue
            tst = p.get("tst")
            if tst is None or tst in suppressed:
                continue
            if _in_bad_track_window(tst, bad_windows):
                continue
            ov = _relocate(p)
            if ov is not None:
                p = dict(p)
                p["lat"], p["lon"] = ov[0], ov[1]
            out.append(p)
        return out

    # Force-empty overrides so the response shows what auto WOULD pick;
    # the UI uses this alongside the saved overrides to render the
    # "Auto (would be X)" label on unforced rows.
    _, choices = _select_track_per_day(
        _clean("primary"), _clean("alt"),
        anchors, home, trip["start"], trip["end"],
        tid_overrides={},
    )

    # Per-tid per-day raw counts (informational; lets the UI tell the
    # admin "alt has 0 pings today, forcing alt will leave a gap").
    counts = {}
    for p in cached:
        d = _local_date_of_ping(p)
        if d is None:
            continue
        bucket = counts.setdefault(d, {"primary": 0, "alt": 0})
        tid_field = p.get("tid") or "primary"
        if tid_field in bucket:
            bucket[tid_field] += 1

    return jsonify({
        "tid_choices": choices,
        "tid_overrides": get_tid_overrides(trip_id),
        "counts": counts,
        "alt_configured": bool(os.environ.get("TIMELINE_TID_ALT")),
    })


@app.route('/api/trips/<int:trip_id>/detect-stops', methods=['POST'])
def api_detect_stops(trip_id):
    """Scan the trip's GPS track for dwell-time clusters that don't already
    correspond to a stay, event, or family location, and propose them as
    new waypoints (≤30 min) or events (>30 min). Each suggestion's
    `event.name` defaults to the placeholder `"Detected stop"` and its
    `locale` / `state` / `display_name` come back empty — reverse-
    geocoding runs client-side after this returns, hitting
    `/api/reverse-geocode` once per stop with a 1 s throttle (Nominatim's
    usage policy). That lets the modal render the full list immediately
    and show progress as each row fills in, instead of blocking on a
    long server-side loop. The frontend disables "Create selected" until
    every row finishes geocoding so the admin doesn't accept un-named
    suggestions.

    The response is advisory only — no events are persisted here. The
    admin reviews the list in the modal and POSTs the accepted subset to
    /accept-stops.
    """
    denied = _require_admin()
    if denied:
        return denied
    trip = next((t for t in parse_trips() if t["id"] == trip_id), None)
    if not trip:
        return jsonify({"error": "trip not found"}), 404
    enrich_trip_locations(trip)
    home, family = _map_config()

    points = _load_trip_track_for_detection(trip_id)
    if not points:
        return jsonify({"stops": [], "warning": "no track data available"})

    # Tighten the window to the trip's own local-date range before
    # detection runs. The track loader pads by ~1 day on each side for
    # timezone slop; this drops anything that falls on a date outside
    # the trip itself. Same-day at-home dwell (e.g., morning of day 1
    # before leaving) is also handled — but via the at-home anchor
    # filter below, since it's still within the date range.
    points = _filter_points_to_trip_window(points, trip["start"], trip["end"])
    if not points:
        return jsonify({"stops": [], "warning": "no track data within trip window"})

    raw_stops = _detect_stops(points)

    # Tighten the time window further by inferring the *real* trip
    # start and end. Auto-detected sustained-away boundaries first
    # (longest qualifying not-at-home streak via
    # _find_home_boundary_tsts), then manual `home_start_time` /
    # `home_end_time` overrides win if the admin set them — those are
    # what the home card displays as the trip's authoritative edges,
    # so detection treats them the same way. Without this, a pre-
    # departure quick errand (e.g. a 7-min Starbucks at 8:22 a.m. when
    # the actual trip departure isn't until the evening) or a post-
    # arrival afternoon errand would fall inside the trip's date range
    # and slip through. Clusters fully before departure or fully after
    # arrival are dropped: end_tst < departure → pre-trip;
    # start_tst > arrival → post-trip.
    home_departure_tst, home_arrival_tst = _find_home_boundary_tsts(
        points, home, anchors=_anchors_for_trip(trip))
    home_tz_name = None
    if home and home[0] is not None and home[1] is not None:
        home_tz_name = _tz_for_coord(home[0], home[1])
    manual_start = (trip.get("home_start_time") or "").strip()
    manual_end = (trip.get("home_end_time") or "").strip()
    if manual_start:
        t = _trip_local_to_tst(trip["start"], manual_start, home_tz_name)
        if t is not None:
            home_departure_tst = t
    if manual_end:
        t = _trip_local_to_tst(trip["end"], manual_end, home_tz_name)
        if t is not None:
            home_arrival_tst = t
    if home_departure_tst is not None:
        raw_stops = [s for s in raw_stops if s["end_tst"] >= home_departure_tst]
    if home_arrival_tst is not None:
        raw_stops = [s for s in raw_stops if s["start_tst"] <= home_arrival_tst]

    # Anything inside the boundary-tst window is a candidate even if
    # it happens near home (e.g., a real coffee-shop stop 1.2 km out
    # on the way back). But clusters centered *at* home — within
    # STOP_AT_HOME_CENTROID_M — are dropped by
    # _drop_stops_at_known_locations using HOME as a spatial anchor at
    # the at-home radius. That guards the case where a manual
    # home_start_time / home_end_time override is rounded a minute or
    # two off the true arrival, so an at-home dwell straddles the
    # boundary-tst and slips through the time-window filter above.
    raw_stops = _drop_stops_at_known_locations(raw_stops, trip, family, home)

    # Defer ZoneInfo import — pre-3.9 hosts (or stripped runtimes) may
    # not have it. Fall back to UTC formatting if it's missing.
    try:
        from zoneinfo import ZoneInfo
        _HAS_ZONEINFO = True
    except Exception:
        ZoneInfo = None
        _HAS_ZONEINFO = False

    def _local(tst, tz_name):
        utc = datetime.utcfromtimestamp(tst)
        if _HAS_ZONEINFO and tz_name and tz_name != "UTC":
            try:
                return utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(tz_name))
            except Exception:
                pass
        return utc

    # Reverse-geocoding deliberately runs on the client (one call per
    # stop, throttled to 1 req/sec) so the modal can render immediately
    # and report progress. `event.name` carries a placeholder; the
    # frontend overwrites it with the geocoded name when each row's
    # geocode completes, and disables "Create selected" until the whole
    # list has been geocoded.
    enriched = []
    for s in raw_stops:
        start_local = _local(s["start_tst"], s["tz"])
        end_local = _local(s["end_tst"], s["tz"])
        classification = "waypoint" if s["duration_minutes"] <= STOP_WAYPOINT_MAX_MINUTES else "event"
        # The "event" sub-dict is the exact payload format that
        # /accept-stops feeds into add_event(), so the frontend can just
        # forward through the rows it kept (after the client-side
        # reverse-geocoding fills in name/locale/state). needs_vetting
        # is hard-coded True so the admin sees the flag on the created
        # event.
        enriched.append({
            "display": {
                "duration_minutes": s["duration_minutes"],
                "ping_count": s["ping_count"],
                "start_local": start_local.strftime("%Y-%m-%d %H:%M"),
                "end_local": end_local.strftime("%H:%M"),
                "classification": classification,
                "center_lat": s["center_lat"],
                "center_lng": s["center_lng"],
                # Per-ping (lat, lng) pairs for the frontend's row-level
                # mini-map. The cluster's `coords` is internal Python
                # tuples; serialize as lists for clean JSON.
                "coords": [[lat, lng] for (lat, lng) in s["coords"]],
                "display_name": "",
            },
            "event": {
                "date": start_local.strftime("%Y-%m-%d"),
                "time": start_local.strftime("%H:%M"),
                "end_time": end_local.strftime("%H:%M"),
                "name": "Detected stop",
                "description": (
                    f"Auto-detected from GPS track: "
                    f"{s['duration_minutes']:.0f} min, {s['ping_count']} pings."
                ),
                "location": f"{s['center_lat']:.6f},{s['center_lng']:.6f}",
                "locale": "",
                "state": "",
                "waypoint": classification == "waypoint",
                "family_id": None,
                "needs_vetting": True,
            },
        })
    return jsonify({"stops": enriched})


@app.route('/api/trips/<int:trip_id>/accept-stops', methods=['POST'])
def api_accept_stops(trip_id):
    """Create events/waypoints from a list of accepted stop suggestions.
    Body: {events: [<add_event payload>, ...]}. Each payload should be a
    `display`-stripped object from /detect-stops, optionally tweaked by
    the admin in the modal. Returns the count created.
    """
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    events_payload = data.get("events") or []
    if not isinstance(events_payload, list):
        return jsonify({"error": "events must be a list"}), 400
    created = 0
    last_trip = None
    for evt in events_payload:
        # Hard-set needs_vetting True so a tampered client can't smuggle in
        # already-vetted entries. The flag's whole purpose is to mark
        # auto-created events.
        evt = dict(evt)
        evt["needs_vetting"] = True
        result = add_event(trip_id, evt)
        if result is None:
            return jsonify({"error": "trip not found"}), 404
        last_trip = result
        created += 1
    return jsonify({"ok": True, "created": created,
                    "event_count": len(last_trip["events"]) if last_trip else 0})


@app.route('/api/elevation')
def api_elevation():
    """Proxy elevation lookup via Open-Elevation API."""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng required"}), 400
    try:
        import urllib.request
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        elev = data["results"][0]["elevation"]
        return jsonify({"elevation_meters": elev})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route('/api/campgrounds/<int:cg_id>', methods=['DELETE'])
def api_delete_campground(cg_id):
    denied = _require_admin()
    if denied:
        return denied

    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)

    before = len(entries)
    entries = [e for e in entries if e.get("id") != cg_id]
    if len(entries) == before:
        return jsonify({"error": "Campground not found"}), 404

    _save_json(CAMPGROUNDS_JSON, entries)
    return jsonify({"ok": True})


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == "create-admin":
        import getpass
        username = input("Admin username: ").strip()
        if not username:
            print("Username cannot be empty.")
            sys.exit(1)
        password = getpass.getpass("Password: ")
        if not password:
            print("Password cannot be empty.")
            sys.exit(1)
        _save_user(username, password, is_admin=True)
        print(f"Admin user '{username}' created.")
    else:
        # Pass --http to skip TLS (HTTPS is on by default so mobile devices
        # on the LAN can use Geolocation, which requires a secure origin).
        # `ssl_context='adhoc'` requires `pyopenssl`.
        use_https = '--http' not in sys.argv
        ssl_context = 'adhoc' if use_https else None
        app.run(debug=True, host='0.0.0.0', port=5001, ssl_context=ssl_context)
