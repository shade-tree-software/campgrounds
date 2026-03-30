import csv
import json
import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from werkzeug.utils import secure_filename
import requests

from summer_finder import find_summer_days
from trips import parse_trips, enrich_trip_locations

app = Flask(__name__)

TRIP_DATA_DIR = os.path.join(os.path.dirname(__file__), "trip_data")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
COMMENTS_FILE = os.path.join(TRIP_DATA_DIR, "comments.json")
CAPTIONS_FILE = os.path.join(TRIP_DATA_DIR, "captions.json")

os.makedirs(TRIP_DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "heic"}
CAMPGROUNDS_CSV = os.path.join(os.path.dirname(__file__), "all-campgrounds.csv")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

WATERFRONT_COLORS = {
    "lake":          "#1976d2",
    "river":         "#00897b",
    "creek":         "#26a69a",
    "pond":          "#9acd32",
    "bay":           "#0d47a1",
    "coastal dunes": "#e6a817",
    "coastal woods": "#6b8e23",
    "lakeview":      "#64b5f6",
    "riverview":     "#80cbc4",
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


# ── Existing routes ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/geocode', methods=['GET'])
def geocode():
    """Geocoding API for city autocomplete using Open-Meteo Geocoding API"""
    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify([])

    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        results = []
        if 'results' in data:
            for item in data['results']:
                results.append({
                    'name': item['name'],
                    'country': item.get('country', ''),
                    'admin1': item.get('admin1', ''),
                    'latitude': item['latitude'],
                    'longitude': item['longitude']
                })

        return jsonify(results)
    except requests.RequestException as e:
        return jsonify({'error': f'Geocoding request failed: {str(e)}'})
    except Exception as e:
        return jsonify({'error': f'Geocoding error: {str(e)}'})


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    max_miles = float(data.get('max_miles', 400))
    min_high_temp = float(data.get('min_high_temp', 70))
    max_high_temp = float(data.get('max_high_temp', 88))
    prefer_waterfront = data.get('prefer_waterfront', False)
    all_days = data.get('all_days', False)
    weekends_only = not all_days

    form_home_lat = data.get('home_lat')
    form_home_long = data.get('home_long')

    def generate():
        try:
            from summer_finder import load_campgrounds, check_campground_weather, get_day_of_week
            from geopy.distance import great_circle

            home_lat = form_home_lat
            home_long = form_home_long

            if home_lat and home_long:
                home = (float(home_lat), float(home_long))
            else:
                return "ERROR: Home coordinates are required. Please select a city from the search."

            campgrounds = load_campgrounds()
            all_summer_days = []

            eligible_campgrounds = []
            for campground in campgrounds:
                lat, long = campground["location"].split(",")
                point = (float(lat), float(long))
                dist = great_circle(home, point).miles if home else 0
                if dist < max_miles:
                    eligible_campgrounds.append((campground, dist))

            total_campgrounds = len(eligible_campgrounds)

            yield f"data: Considering {total_campgrounds} campgrounds within {max_miles} miles of home {home if home else 'any location'}.\n\n"

            for i, (campground, dist) in enumerate(eligible_campgrounds):
                name = campground["name"]

                yield f"data: Checking {name} ({i+1}/{total_campgrounds})\n\n"

                try:
                    summer_days = check_campground_weather(
                        campground, min_high_temp, max_high_temp, home, max_miles, weekends_only, progress_callback
                    )

                    for summer_day in summer_days:
                        waterfront = campground.get("waterfront", "none")
                        summer_day["waterfront"] = waterfront

                        waterfront_label = f" ({waterfront} waterfront)" if waterfront != "none" else ""
                        yield f"data: Found summer day at {name}{waterfront_label} - {summer_day['day']} {summer_day['date']} ({summer_day['temp']}°F)\n\n"
                        all_summer_days.append(summer_day)

                except Exception as e:
                    yield f"data: {str(e)}\n\n"
                    continue

            if all_summer_days:
                if prefer_waterfront:
                    sorted_summer_days = sorted(
                        all_summer_days,
                        key=lambda d: (d.get('waterfront', 'none') == 'none', d['dist'])
                    )
                else:
                    sorted_summer_days = sorted(all_summer_days, key=lambda d: d['dist'])

                yield f"data: SEARCH_COMPLETE:{json.dumps(sorted_summer_days)}\n\n"
            else:
                yield f"data: SEARCH_COMPLETE:[]\n\n"

        except Exception as e:
            yield f"data: ERROR:{str(e)}\n\n"

    return Response(generate(), mimetype='text/plain')


# ── Trip calendar routes ─────────────────────────────────────────────────────

@app.route('/trips')
def trips_calendar():
    trips = parse_trips()
    for trip in trips:
        enrich_trip_locations(trip)
    _, family = _map_config()
    return render_template('trips_calendar.html', trips=trips, family_locations=family)


@app.route('/trips/<int:trip_id>')
def trip_detail(trip_id):
    trips = parse_trips()
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        return "Trip not found", 404

    enrich_trip_locations(trip)

    # Load photos for each stay
    comments = _load_json(COMMENTS_FILE)
    captions = _load_json(CAPTIONS_FILE)
    trip_comments = comments.get(str(trip_id), [])

    # Build photo list per stay (keyed by stay index)
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
    return render_template(
        'trip_detail.html',
        trip=trip,
        stay_photos=stay_photos,
        trip_comments=trip_comments,
        family_locations=family,
    )


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/upload', methods=['POST'])
def upload_photo(trip_id, stay_idx):
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
    # Avoid overwriting: append timestamp if exists
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
    comments = _load_json(COMMENTS_FILE)
    trip_comments = comments.get(str(trip_id), [])
    if 0 <= comment_idx < len(trip_comments):
        trip_comments.pop(comment_idx)
        comments[str(trip_id)] = trip_comments
        _save_json(COMMENTS_FILE, comments)
    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/photos/<filename>', methods=['DELETE'])
def delete_photo(trip_id, stay_idx, filename):
    filename = secure_filename(filename)
    photo_path = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx), filename)
    if os.path.exists(photo_path):
        os.remove(photo_path)

    # Remove caption too
    photo_key = f"{trip_id}/{stay_idx}/{filename}"
    captions = _load_json(CAPTIONS_FILE)
    captions.pop(photo_key, None)
    _save_json(CAPTIONS_FILE, captions)

    return jsonify({"ok": True})


# ── Campground map routes ───────────────────────────────────────────────────

def _load_campgrounds_csv():
    with open(CAMPGROUNDS_CSV, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _map_config():
    """Return home coords and family locations from config.json."""
    config = _load_json(CONFIG_FILE)
    lat = config.get("home_lat")
    lng = config.get("home_long")
    home = [lat, lng] if lat is not None and lng is not None else None
    family = config.get("family_locations", [])
    return home, family


@app.route('/campgrounds/waterfront')
def campgrounds_waterfront():
    home, family = _map_config()
    return render_template(
        'campground_map.html',
        title='Campgrounds by Waterfront',
        campgrounds=_load_campgrounds_csv(),
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
        campgrounds=_load_campgrounds_csv(),
        color_field='climate',
        color_map=CLIMATE_COLORS,
        home=home,
        family_locations=family,
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
