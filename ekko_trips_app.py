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
                   add_stay, update_stay, delete_stay)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

TRIP_DATA_DIR = os.path.join(os.path.dirname(__file__), "trip_data")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
COMMENTS_FILE = os.path.join(TRIP_DATA_DIR, "comments.json")
CAPTIONS_FILE = os.path.join(TRIP_DATA_DIR, "captions.json")
USERS_FILE = os.path.join(TRIP_DATA_DIR, "users.json")

os.makedirs(TRIP_DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.context_processor
def inject_trip_stats():
    trips = parse_trips()
    return {
        "trip_count": len(trips),
        "night_count": sum(t["total_nights"] for t in trips),
    }

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "heic"}
CAMPGROUNDS_JSON = os.path.join(os.path.dirname(__file__), "all-campgrounds.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

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
    return redirect('/')


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
        row["visited"] = "yes" if "stays" in entry else "no"
        rows.append(row)
    return rows


def _map_config():
    """Return home coords and family locations from config.json."""
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
    return render_template('trips_map.html', trips=trips, home=home, family_locations=family)


@app.route('/trips/calendar')
def trips_calendar():
    trips = parse_trips()
    for trip in trips:
        enrich_trip_locations(trip)
    return render_template('trips_calendar.html', trips=trips)


@app.route('/trips/<int:trip_id>')
def trip_detail(trip_id):
    trips = parse_trips()
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        return "Trip not found", 404

    enrich_trip_locations(trip)

    comments = _load_json(COMMENTS_FILE)
    captions = _load_json(CAPTIONS_FILE)
    trip_comments = comments.get(str(trip_id), [])

    stay_photos = {}
    for i, stay in enumerate(trip["stays"]):
        photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(i))
        photos = []
        if os.path.isdir(photo_dir):
            for fname in sorted(os.listdir(photo_dir)):
                if _allowed_file(fname):
                    photo_key = f"{trip_id}/{i}/{fname}"
                    photos.append({
                        "filename": fname,
                        "url": f"/static/uploads/{trip_id}/{i}/{fname}",
                        "caption": captions.get(photo_key, ""),
                    })
        stay_photos[i] = photos

    _, family = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin
    return render_template(
        'trip_detail.html',
        trip=trip,
        stay_photos=stay_photos,
        trip_comments=trip_comments,
        family_locations=family,
        is_admin=is_admin,
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


@app.route('/trips/<int:trip_id>/comments', methods=['GET'])
def get_comments(trip_id):
    comments = _load_json(COMMENTS_FILE)
    return jsonify(comments.get(str(trip_id), []))


@app.route('/trips/<int:trip_id>/comments', methods=['POST'])
def add_comment(trip_id):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty comment"}), 400

    comments = _load_json(COMMENTS_FILE)
    trip_comments = comments.get(str(trip_id), [])
    trip_comments.append({
        "text": text,
        "timestamp": datetime.now().isoformat(),
    })
    comments[str(trip_id)] = trip_comments
    _save_json(COMMENTS_FILE, comments)

    return jsonify({"ok": True, "comment": trip_comments[-1]})


@app.route('/trips/<int:trip_id>/comments/<int:comment_idx>', methods=['DELETE'])
def delete_comment(trip_id, comment_idx):
    denied = _require_admin()
    if denied:
        return denied
    comments = _load_json(COMMENTS_FILE)
    trip_comments = comments.get(str(trip_id), [])
    if 0 <= comment_idx < len(trip_comments):
        trip_comments.pop(comment_idx)
        comments[str(trip_id)] = trip_comments
        _save_json(COMMENTS_FILE, comments)
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


# ── Campground map routes ───────────────────────────────────────────────────

@app.route('/campgrounds/waterfront')
def campgrounds_waterfront():
    home, family = _map_config()
    return render_template(
        'campground_map.html',
        title='Campgrounds by Waterfront',
        campgrounds=_load_campgrounds(),
        color_field='waterfront',
        color_map=WATERFRONT_COLORS,
        home=home,
        family_locations=family,
    )


@app.route('/campgrounds/climate')
def campgrounds_climate():
    home, family = _map_config()
    return render_template(
        'campground_map.html',
        title='Campgrounds by Climate',
        campgrounds=_load_campgrounds(),
        color_field='climate',
        color_map=CLIMATE_COLORS,
        home=home,
        family_locations=family,
    )


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
