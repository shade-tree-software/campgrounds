import json
import os
import sys
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from trips import (parse_trips, enrich_trip_locations,
                   create_trip, update_trip, delete_trip,
                   add_stay, update_stay, delete_stay,
                   add_event, update_event, delete_event,
                   rename_campground_in_trips)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

TRIP_DATA_DIR = os.path.join(os.path.dirname(__file__), "trip_data")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
CAPTIONS_FILE = os.path.join(TRIP_DATA_DIR, "captions.json")
PHOTO_ORDER_FILE = os.path.join(TRIP_DATA_DIR, "photo_order.json")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

os.makedirs(TRIP_DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.context_processor
def inject_trip_stats():
    trips = parse_trips()
    overnight = sum(1 for t in trips if t["stays"])
    daytrips = sum(1 for t in trips if not t["stays"])
    return {
        "overnight_count": overnight,
        "daytrip_count": daytrips,
        "night_count": sum(t["total_nights"] for t in trips),
    }

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "heic"}
CAMPGROUNDS_JSON = os.path.join(os.path.dirname(__file__), "campgrounds.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "family_locations.json")

WATERFRONT_COLORS = {
    "lake":          "#1976d2",
    "river":         "#00695c",
    "creek":         "#80cbc4",
    "pond":          "#9acd32",
    "bay":           "#0d47a1",
    "coastal dunes": "#e6a817",
    "coastal woods": "#6b8e23",
    "lakeview":      "#64b5f6",
    "riverview":     "#26a69a",
    "none":          "#795548",
}

CLIMATE_COLORS = {
    "much cooler":     "#1a237e",
    "cooler":          "#1565c0",
    "slightly cooler": "#42a5f5",
    "similar":         "#4caf50",
    "slightly warmer": "#fdd835",
    "warmer":          "#fb8c00",
    "much warmer":     "#e53935",
    "hot":             "#b71c1c",
}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
    def __init__(self, username, password_hash, is_admin=False):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin


def _load_users():
    data = _load_json(USERS_FILE)
    return {name: User(name, info["password_hash"], info.get("is_admin", False))
            for name, info in data.items()}


def _save_user(username, password, is_admin=False):
    data = _load_json(USERS_FILE)
    data[username] = {
        "password_hash": generate_password_hash(password),
        "is_admin": is_admin,
    }
    _save_json(USERS_FILE, data)


@login_manager.user_loader
def load_user(username):
    users = _load_users()
    return users.get(username)


def _require_admin():
    """Return an error response if current user is not an admin, else None."""
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = _load_users()
        user = users.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next', '/')
            return redirect(next_page)
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
    (4.0,   "similar"),
    (9.0,   "slightly warmer"),
    (14.0,  "warmer"),
    (19.0,  "much warmer"),
]


def _classify_climate(delta_temp):
    for threshold, label in CLIMATE_THRESHOLDS:
        if delta_temp <= threshold:
            return label
    return "hot"


def _load_campgrounds():
    """Load campgrounds from JSON and compute derived fields."""
    config = _load_json(CONFIG_FILE)
    home_lat = config.get("home_lat")
    home_alt = config.get("home_altitude_meters")
    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)

    excluded = {"index", "stays", "elevation_meters"}
    rows = []
    for entry in entries:
        if "location" not in entry:
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
        row["visit_count"] = len(entry["stays"]) if "stays" in entry else 0
        rows.append(row)
    return rows


def _map_config():
    """Return home coords and family locations from family_locations.json."""
    config = _load_json(CONFIG_FILE)
    lat = config.get("home_lat")
    lng = config.get("home_long")
    home = [lat, lng] if lat is not None and lng is not None else None
    family = config.get("family_locations", [])
    return home, family


# ── Trip routes ─────────────────────────────────────────────────────────────

@app.route('/')
@app.route('/trips')
@app.route('/trips/map')
def trips_map():
    trips = parse_trips()
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

    return render_template('trips_map.html', trips=trips, home=home,
                           family_locations=family, active_nav='map',
                           slideshow_photos=all_photos)


@app.route('/trips/calendar')
@app.route('/trips/list')
def trips_calendar():
    trips = parse_trips()
    for trip in trips:
        enrich_trip_locations(trip)
    initial_view = 'list' if request.path == '/trips/list' else 'calendar'
    return render_template('trips_calendar.html', trips=trips, initial_view=initial_view, active_nav=initial_view)


@app.route('/trips/<int:trip_id>')
def trip_detail(trip_id):
    trips = parse_trips()
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        return "Trip not found", 404

    enrich_trip_locations(trip)

    captions = _load_json(CAPTIONS_FILE)

    photo_order = _load_json(PHOTO_ORDER_FILE)

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
                })
        event_photos[i] = photos

    _, family = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin

    # Find prev/next trip IDs
    trip_ids = [t["id"] for t in trips]
    idx = trip_ids.index(trip_id)
    prev_trip_id = trip_ids[idx - 1] if idx > 0 else None
    next_trip_id = trip_ids[idx + 1] if idx < len(trip_ids) - 1 else None

    return render_template(
        'trip_detail.html',
        trip=trip,
        stay_photos=stay_photos,
        event_photos=event_photos,
        family_locations=family,
        is_admin=is_admin,
        prev_trip_id=prev_trip_id,
        next_trip_id=next_trip_id,
    )


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/upload', methods=['POST'])
def upload_photo(trip_id, stay_idx):
    denied = _require_admin()
    if denied:
        return denied
    if 'photo' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx))
    os.makedirs(photo_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    base, ext = os.path.splitext(filename)
    dest = os.path.join(photo_dir, filename)
    if os.path.exists(dest):
        filename = f"{base}_{int(datetime.now().timestamp())}{ext}"
        dest = os.path.join(photo_dir, filename)

    file.save(dest)

    return jsonify({
        "filename": filename,
        "url": f"/static/uploads/{trip_id}/{stay_idx}/{filename}",
    })


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/caption', methods=['POST'])
def save_caption(trip_id, stay_idx):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json()
    filename = data.get("filename", "")
    caption = data.get("caption", "")

    photo_key = f"{trip_id}/{stay_idx}/{filename}"
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
    denied = _require_admin()
    if denied:
        return denied
    if 'photo' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(event_idx))
    os.makedirs(photo_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    base, ext = os.path.splitext(filename)
    dest = os.path.join(photo_dir, filename)
    if os.path.exists(dest):
        filename = f"{base}_{int(datetime.now().timestamp())}{ext}"
        dest = os.path.join(photo_dir, filename)

    file.save(dest)

    return jsonify({
        "filename": filename,
        "url": f"/static/uploads/{trip_id}/events/{event_idx}/{filename}",
    })


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/caption', methods=['POST'])
def save_event_caption(trip_id, event_idx):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json()
    filename = data.get("filename", "")
    caption = data.get("caption", "")

    photo_key = f"{trip_id}/events/{event_idx}/{filename}"
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
    home, family = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin
    return render_template(
        'campground_map.html',
        title='Campgrounds by Proximity to Water',
        campgrounds=_load_campgrounds(),
        color_field='waterfront',
        color_map=WATERFRONT_COLORS,
        home=home,
        family_locations=family,
        active_nav='waterfront',
        is_admin=is_admin,
    )


@app.route('/campgrounds/climate')
def campgrounds_climate():
    home, family = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin
    return render_template(
        'campground_map.html',
        title='Campgrounds by Climate',
        campgrounds=_load_campgrounds(),
        color_field='climate',
        color_map=CLIMATE_COLORS,
        home=home,
        family_locations=family,
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

@app.route('/api/campgrounds')
def api_campground_list():
    """Return a lightweight list of campground names and states for pickers."""
    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)
    result = [{"name": e["name"], "state": e.get("state", "")}
              for e in entries if "name" in e]
    result.sort(key=lambda x: x["name"])
    return jsonify(result)


@app.route('/campgrounds/manage')
def campgrounds_manage():
    denied = _require_admin()
    if denied:
        return redirect(url_for('login', next=request.path))
    is_admin = current_user.is_authenticated and current_user.is_admin
    config = _load_json(CONFIG_FILE)
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

    entry = {
        "name": name,
        "location": data.get("location", ""),
        "elevation_meters": float(data.get("elevation_meters", 0)),
        "waterfront": data.get("waterfront", "none"),
        "state": data.get("state", ""),
        "ownership": data.get("ownership", ""),
        "website": data.get("website", ""),
        "note": data.get("note", ""),
        "phone": data.get("phone", ""),
    }
    entries.append(entry)
    _save_json(CAMPGROUNDS_JSON, entries)
    return jsonify({"ok": True})


@app.route('/api/campgrounds/<path:name>', methods=['PUT'])
def api_update_campground(name):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}

    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)

    target = None
    for e in entries:
        if e["name"] == name:
            target = e
            break
    if not target:
        return jsonify({"error": "Campground not found"}), 404

    new_name = data.get("name", "").strip()
    if new_name and new_name != name:
        if any(e["name"] == new_name for e in entries if e is not target):
            return jsonify({"error": "A campground with that name already exists"}), 409
        rename_campground_in_trips(name, new_name)
        target["name"] = new_name

    for key in ("location", "elevation_meters", "waterfront", "state",
                "ownership", "website", "note", "phone"):
        if key in data:
            val = data[key]
            if key == "elevation_meters":
                val = float(val)
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


@app.route('/api/campgrounds/<path:name>', methods=['DELETE'])
def api_delete_campground(name):
    denied = _require_admin()
    if denied:
        return denied

    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)

    before = len(entries)
    entries = [e for e in entries if e["name"] != name]
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
        app.run(debug=True, host='0.0.0.0', port=5001)
