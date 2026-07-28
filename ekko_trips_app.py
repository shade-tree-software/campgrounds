import argparse
import gzip
import hashlib
import json
import math
import os
import re
import secrets
import shutil
import sqlite3
import sys
import threading
import time
from datetime import date, datetime, time as dt_time, timedelta, timezone

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, Response, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash, safe_join
from werkzeug.utils import secure_filename

from ridb.fetch_facility import (search_facilities, fetch_facility,
                                 availability_matrix, DEFAULT_FIT_FT)
import weather_finder
from trips import (parse_trips, enrich_trip_locations,
                   create_trip, update_trip, delete_trip,
                   add_stay, update_stay, delete_stay,
                   add_event, update_event, delete_event,
                   get_suppressed_pings, add_suppressed_pings,
                   remove_suppressed_pings,
                   get_relocated_pings, add_relocated_pings,
                   remove_relocated_pings,
                   get_tid_overrides, set_tid_override, raw_trip_records,
                   campground_references, camping_nights, is_day_trip,
                   TRIPS_JSON)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.jinja_env.policies['json.dumps_kwargs'] = {'sort_keys': False}


@app.after_request
def _revalidate_html(resp):
    """Force revalidation of HTML pages.

    Rendered pages are dynamic and ship no Cache-Control (nor ETag/Last-Modified),
    so some mobile browsers / standalone PWAs heuristically cache them and keep
    serving a pre-deploy page — its inline JS never refreshes, so map/UI changes
    don't appear on the phone even after a deploy. `no-cache` means "revalidate
    with the server before reuse", which for validator-less pages is a fresh
    fetch. HTML only: static JS/CSS/images/thumbs keep their own long cache + the
    `?v=<mtime>` busting, and routes that set their own directive (e.g. /sw-reset's
    no-store) are left untouched.
    """
    if resp.mimetype == 'text/html':
        resp.headers.setdefault('Cache-Control', 'no-cache')
        # A share guest's landing page carries `/s/<token>` in the address bar
        # (so bookmarking it works), which makes the URL path a credential the
        # browser could hand to a third party in a Referer header — the map's
        # OpenStreetMap attribution link is right there. `strict-origin-...` is
        # the modern browser default, but stating it explicitly covers older
        # ones and stops a future default change from reopening the hole. Only
        # the ORIGIN is sent cross-site; same-site navigation is unaffected.
        resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    return resp


# Audit-trail fields on a campground entry: the proof strings behind its
# waterfront and inclusion calls. Source of truth in campgrounds.json, but no
# client reads them, so every browser-bound payload strips them.
_AUDIT_EVIDENCE_FIELDS = ("waterfront_evidence", "inclusion_evidence")

# Compress text responses above this size. Below it the CPU cost and the ~20
# bytes of gzip framing aren't worth it.
_COMPRESS_MIN_BYTES = 4096
_COMPRESSIBLE_MIMETYPES = frozenset({
    'text/html', 'text/css', 'text/plain',
    'application/json', 'application/javascript', 'text/javascript',
})


@app.after_request
def _compress_response(resp):
    """gzip large text responses.

    The campground map embeds the whole database inline, so it renders as a
    ~10 MB HTML document; the trips map, calendar and poster are each several
    hundred KB. Over a campground's cell signal that's the difference between
    usable and not — gzip takes the map page to roughly a fifth of its size.

    Browsers decompress transparently, so no client change is needed, and a
    proxy that would have gzipped anyway passes our Content-Encoding through
    untouched (nginx will not re-encode an already-encoded response).

    Deliberately skipped: non-200s, responses already encoded, and
    direct_passthrough responses (send_file — photos and thumbs are JPEGs,
    already compressed, and get_data() on a passthrough response would buffer
    the whole file into memory just to make it bigger).
    """
    try:
        if (resp.status_code != 200
                or resp.direct_passthrough
                or 'Content-Encoding' in resp.headers
                or resp.mimetype not in _COMPRESSIBLE_MIMETYPES
                or 'gzip' not in request.headers.get('Accept-Encoding', '')):
            return resp
        data = resp.get_data()
        if len(data) < _COMPRESS_MIN_BYTES:
            return resp
        resp.set_data(gzip.compress(data, 6))
        resp.headers['Content-Encoding'] = 'gzip'
        resp.headers['Content-Length'] = resp.content_length
        resp.headers.add('Vary', 'Accept-Encoding')
    except Exception:
        # Compression is an optimization; never let it turn a good response
        # into a 500.
        pass
    return resp

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
_static_v_cache = {}


def _static_v(path):
    """Return ``/static/<path>?v=<mtime>`` so a redeploy changes the URL and
    every cache layer (browser HTTP cache, service worker) is forced to
    refetch. Without this the URL is identical across deploys and a phone
    keeps serving the stale file — PythonAnywhere serves /static/ with a
    far-future Cache-Control, and even the SW's network-first fetch() goes
    through that HTTP cache. mtime is cheap and changes whenever the file is
    edited/redeployed; cached per process so we stat each file at most once."""
    rel = path.lstrip("/")
    cached = _static_v_cache.get(rel)
    if cached is None:
        try:
            cached = str(int(os.path.getmtime(os.path.join(_STATIC_DIR, rel))))
        except OSError:
            cached = ""
        _static_v_cache[rel] = cached
    return f"/static/{rel}?v={cached}" if cached else f"/static/{rel}"


app.jinja_env.globals["static_v"] = _static_v


def _load_or_create_secret_key():
    """Secret key: the FLASK_SECRET_KEY env var wins; otherwise persist a
    generated key under trip_data/ (gitignored) so session and remember-me
    cookies survive app restarts. The previous os.urandom fallback minted a
    fresh key every launch, silently logging everyone out on each restart.
    """
    env_key = os.environ.get("FLASK_SECRET_KEY")
    if env_key:
        return env_key
    path = os.path.join(os.path.dirname(__file__), "trip_data", "secret_key")
    try:
        with open(path) as f:
            key = f.read().strip()
        if key:
            return key
    except OSError:
        pass
    key = os.urandom(24).hex()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(key)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return key


app.secret_key = _load_or_create_secret_key()
# Family members shouldn't have to re-type passwords on their phones —
# login_user(remember=True) below sets a long-lived remember-me cookie.
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365)


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


@app.template_filter('daterange')
def _daterange(start, end=None):
    """Format ISO 'YYYY-MM-DD' start/end as a compact human date range.

    'Jun 5, 2025' (single day), 'Jun 5–12, 2025' (same month),
    'Jun 28 – Jul 2, 2025' (same year), 'Dec 30, 2024 – Jan 2, 2025'
    (spans years). Returns the raw input(s) joined with a dash if either
    date doesn't parse, so blank/legacy values pass through harmlessly.
    """
    try:
        s = datetime.strptime(str(start), "%Y-%m-%d").date()
        e = datetime.strptime(str(end), "%Y-%m-%d").date() if end else s
    except (ValueError, TypeError):
        return f"{start} – {end}" if end and end != start else start
    if s == e:
        return f"{s.strftime('%b')} {s.day}, {s.year}"
    if (s.year, s.month) == (e.year, e.month):
        return f"{s.strftime('%b')} {s.day}–{e.day}, {s.year}"
    if s.year == e.year:
        return f"{s.strftime('%b')} {s.day} – {e.strftime('%b')} {e.day}, {s.year}"
    return f"{s.strftime('%b')} {s.day}, {s.year} – {e.strftime('%b')} {e.day}, {e.year}"

@app.template_filter('daylabel')
def _daylabel(value):
    """'Thu, Jun 5' for a timeline day divider. Falls through unchanged if the
    value doesn't parse, so a blank/legacy date can't break the page."""
    try:
        d = datetime.strptime(str(value), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return value
    return f"{d.strftime('%a')}, {d.strftime('%b')} {d.day}"


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

TRIP_DATA_DIR = os.path.join(os.path.dirname(__file__), "trip_data")
# Photo library. Deliberately a SIBLING of static/, not a child.
#
# It used to be static/uploads/, which put it inside whatever the deployment
# maps as its static root — and a front-end web server serving /static/ straight
# from disk never consults Flask, so no amount of app-side gating could protect
# it. On PythonAnywhere, adding a narrower /static/uploads/ mapping pointed at an
# empty directory did NOT take precedence over the broader /static/ one, so the
# photos stayed public. Moving the directory out from under the static root is
# the only fix that holds on every host, because there is simply nothing at
# static/uploads/ left to serve.
#
# Also keep it OUT of trip_data/: sync-from-pa.sh mirrors that directory with an
# optional --delete, and photos are synced separately (--photos), so nesting
# them there would let a data-only sync wipe the library.
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "photo_uploads")
CAPTIONS_FILE = os.path.join(TRIP_DATA_DIR, "captions.json")
PHOTO_ORDER_FILE = os.path.join(TRIP_DATA_DIR, "photo_order.json")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
# Per-photo uploader record. Keyed identically to captions:
#   "{trip_id}/{stay_idx}/{filename}" or "{trip_id}/events/{event_idx}/{filename}".
# Used to gate non-admin (uploader-role) caption edits to their own contributions.
PHOTO_UPLOADERS_FILE = os.path.join(TRIP_DATA_DIR, "photo_uploaders.json")
# Per-photo "hero" mark, keyed identically to captions. There is no heuristic
# for "is this a good photo" — resolution, aspect and EXIF camera model are all
# proxies for "taken with the nice camera" — so the poster's two 2x2 hero cells
# deal from a hand-marked set instead, and the marking IS the feature. Cheap to
# curate because the sheet only needs a couple of dozen good photos, not a
# rating on every one. A dict {key: True} rather than a list, because
# _remap_json_keys (trips.py) rewrites these keys by iterating .items() when a
# stay/event sort shifts indices. Unstarring deletes the key rather than
# storing False, so the file stays the size of the marked set.
PHOTO_FAVORITES_FILE = os.path.join(TRIP_DATA_DIR, "photo_favorites.json")
# Read-only share links (magic links). Maps an unguessable token to
#   {label, next, created}. A token authenticates a synthetic read-only viewer
# (see SHARE_ID_PREFIX / load_user), so a leaked link exposes only viewing.
# Deleting a token here is the revoke: load_user re-checks this file every
# request, so the visitor's session dies immediately.
SHARE_TOKENS_FILE = os.path.join(TRIP_DATA_DIR, "share_tokens.json")
# Append-only access log: one JSON object per line (JSONL), written by
# _log_access. Deliberately NOT a json dict like the files above — those are
# read-modify-write, which on every request would be both slow and a
# corruption risk when two requests land at once. A single O_APPEND write of a
# sub-4KB line is atomic on POSIX, so concurrent requests interleave cleanly.
ACCESS_LOG_FILE = os.path.join(TRIP_DATA_DIR, "access_log.jsonl")
# Entries older than this are dropped by _prune_access_log (same spirit as the
# 7-day photo trash purge: bounded growth without manual maintenance).
ACCESS_LOG_RETENTION_DAYS = 90

os.makedirs(TRIP_DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.context_processor
def inject_trip_stats():
    trips = [t for t in parse_trips() if not t.get("home_only")]
    overnight = sum(1 for t in trips if t["stays"])
    # is_day_trip(), matching the stats page — an empty placeholder trip has
    # no campspots AND no events and counts as neither.
    daytrips = sum(1 for t in trips if is_day_trip(t))
    return {
        "overnight_count": overnight,
        "daytrip_count": daytrips,
        # camping_nights(), matching the stats page — the header's nights
        # figure and the Nights hero/by-year chart must never disagree.
        "night_count": sum(camping_nights(t) for t in trips),
    }


# ── Offline map tiles (USB standalone edition) ──────────────────────────────
# When EKKO_LOCAL_TILES is set AND a local tile store exists (the stick), maps
# are served from the stick via the /tiles routes below; otherwise the online
# CDN URLs are emitted, identical to a normal PythonAnywhere deploy. The switch
# is server-decided and exposed to every page as window.EKKO_TILES; the shared
# static/vendor/tile-layers.js helper builds the Leaflet layers from it. The
# /tiles routes are inert without a store (404), so a store-less host is
# unaffected. See usb/TILE-PIPELINE-DESIGN.md.
LOCAL_TILE_DIR = os.path.join(os.path.dirname(__file__), "tiles")
_ESRI_SAT = [
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
    "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",
]


def _local_tiles_active():
    return bool(os.environ.get("EKKO_LOCAL_TILES")) and os.path.isdir(LOCAL_TILE_DIR)


def _pmtiles_maxzoom(path, default=14):
    """Read the max-zoom byte (offset 101) from a PMTiles v3 header. The client
    passes this to protomaps-leaflet as maxDataZoom so overzoom works: the lib
    defaults maxDataZoom to 15 and would request tiles past the data's real max
    (blank map above that zoom). Reading it here keeps the app correct whether the
    installed street.pmtiles was rendered to z14 (corridor) or z15 (merged/route)
    with no hardcoded coupling to the build's --maxzoom."""
    try:
        with open(path, "rb") as f:
            head = f.read(127)
        if head[:7] == b"PMTiles":
            return head[101]
    except Exception:
        pass
    return default


def _tile_config():
    """Tile-source config emitted to the page as window.EKKO_TILES."""
    if _local_tiles_active():
        # Advertise a local street source ONLY if its store is actually present.
        # The satellite half of the stick can be finished long before the street
        # basemap is (the pmtiles render needs a big machine), and pointing
        # protomaps-leaflet at a missing .pmtiles yields a blank basemap plus a
        # stream of failed range requests. With these null, tile-layers.js falls
        # back to satellite imagery so the map is never blank; dropping
        # street.pmtiles into tiles/ lights up real streets with no code change.
        vec_path = os.path.join(LOCAL_TILE_DIR, "street.pmtiles")
        has_vector = os.path.isfile(vec_path)
        has_raster = os.path.isfile(os.path.join(LOCAL_TILE_DIR, "street.mbtiles"))
        # Same existence gate for satellite, for the mirror-image half-install:
        # the street basemap can equally be finished before the NAIP store is
        # baked (or the store may live only on the real card, as on the dev test
        # rig). Advertising /tiles/sat with no satellite.mbtiles behind it gives
        # every satellite tile a 404 and a blank layer with no way back, so fall
        # through to the same Esri URLs the online build uses — correct when the
        # host has a network, and no worse than 404s when it doesn't.
        has_sat = os.path.isfile(os.path.join(LOCAL_TILE_DIR, "satellite.mbtiles"))
        return {
            "mode": "local",
            "streetVector": "/tiles/street.pmtiles" if has_vector else None,
            # data max zoom of the .pmtiles, so the client overzooms from the right
            # level instead of requesting non-existent deeper tiles (blank map)
            "streetVectorMaxDataZoom": _pmtiles_maxzoom(vec_path) if has_vector else None,
            "street": "/tiles/street/{z}/{x}/{y}.png" if has_raster else None,
            "satellite": ["/tiles/sat/{z}/{x}/{y}.jpg"] if has_sat else _ESRI_SAT,
            "maxZoom": 19,
            # NAIP tops out at z16; the Esri fallback goes deeper, so only cap
            # native zoom when we are actually serving the baked store.
            "maxNativeZoom": 16 if has_sat else 19,
        }
    return {
        "mode": "online",
        "streetVector": None,
        "street": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "satellite": _ESRI_SAT,
        "maxZoom": 19, "maxNativeZoom": 19,
    }


@app.context_processor
def inject_tile_config():
    return {"tile_config": _tile_config()}


_tile_store_local = threading.local()


def _tile_store(layer):
    """Read-only sqlite connection to a layer's MBTiles, or None if absent.
    Connections are thread-local: a single sqlite connection is NOT safe for
    concurrent use, and the browser fires many tile requests at once on the
    threaded dev server, so a shared connection raised SQLITE_MISUSE ("bad
    parameter or other API misuse"). layer is 'street' or 'sat'."""
    fname = {"street": "street.mbtiles", "sat": "satellite.mbtiles"}.get(layer)
    if not fname:
        return None
    cache = getattr(_tile_store_local, "cache", None)
    if cache is None:
        cache = _tile_store_local.cache = {}
    if layer not in cache:
        path = os.path.join(LOCAL_TILE_DIR, fname)
        cache[layer] = (
            sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            if os.path.isfile(path) else None
        )
    return cache[layer]

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "heic"}

# Sent on every outbound API call. Nominatim's usage policy requires a UA that
# identifies the application *and* offers a way to reach its operator, so the
# repo URL rides along — a bare "EkkoTrips/1.0" is the shape of UA they block.
_OUTBOUND_UA = ("EkkoTrips/1.0 "
                "(+https://github.com/shade-tree-software/campgrounds)")
CAMPGROUNDS_JSON = os.path.join(os.path.dirname(__file__), "campgrounds.json")
ROADSIDE_JSON = os.path.join(os.path.dirname(__file__), "roadside.json")
HOME_FILE = os.path.join(os.path.dirname(__file__), "home.json")

WATERFRONT_COLORS = {
    "coastal dunes": "#e6a817",
    "coastal woods": "#6b8e23",
    "bayfront":      "#0d47a1",
    "bayview":       "#5c6bc0",
    "lakefront":     "#1976d2",
    "lakeview":      "#64b5f6",
    "riverfront":    "#00695c",
    "riverview":     "#26a69a",
    "creekside":     "#80cbc4",
    "pond":          "#9acd32",
    "not waterfront": "#795548",
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


# EXIF timestamps are immutable for a given file, but trip detail re-read
# every photo's EXIF on every render (one file open per photo). Cache per
# (path, mtime_ns, size) — a replaced file gets a fresh read; entries for
# deleted files are a few stale dict slots, not worth evicting.
_EXIF_DATE_CACHE = {}
_EXIF_DT_CACHE = {}


def _photo_date_taken(filepath):
    """Extract when a photo was taken from EXIF data.

    Returns 'YYYY-MM-DD HH:MM:SS' when a time is present, 'YYYY-MM-DD' when
    only a date is available, or '' if there's no EXIF timestamp.
    """
    try:
        st = os.stat(filepath)
        key = (filepath, st.st_mtime_ns, st.st_size)
    except OSError:
        return ""
    if key in _EXIF_DATE_CACHE:
        return _EXIF_DATE_CACHE[key]
    result = ""
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
                result = f"{date_str} {time_part}" if time_part else date_str
                break
    except Exception:
        pass
    _EXIF_DATE_CACHE[key] = result
    return result


def _photo_datetime_taken(filepath):
    """Like _photo_date_taken but returns the full datetime or None.

    Used for bucketing photos across multi-copy stay cards.
    """
    try:
        st = os.stat(filepath)
        key = (filepath, st.st_mtime_ns, st.st_size)
    except OSError:
        return None
    if key in _EXIF_DT_CACHE:
        return _EXIF_DT_CACHE[key]
    result = None
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
                result = datetime.strptime(val, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                result = None
            break
    except Exception:
        pass
    _EXIF_DT_CACHE[key] = result
    return result


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
    _invalidate_photo_pool()
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
    if saved:
        _invalidate_photo_pool()
    return saved


# ── Photo thumbnails ─────────────────────────────────────────────────────────
# Grid views render every photo as a small tile, but historically served the
# full-resolution originals (a 30-photo trip pulled them all on page load).
# /thumb/<subpath> serves a lazily-generated, cached JPEG thumbnail instead:
# generated on first request into a .thumbs/ subdir beside the originals
# (its name fails _allowed_file, so photo listings never see it, and
# rmtree-based delete-all sweeps it away with the photo dir). Staleness is
# mtime-keyed, so a photo replaced/moved under the same name regenerates.
# The lightbox still loads originals via the grid imgs' data-full attr.

THUMB_DIRNAME = ".thumbs"
THUMB_MAX_PX = 480     # covers ~200px grid cells at 2-2.5x DPR
THUMB_QUALITY = 80

# The lightbox's middle size. Photos had only two: a 480px thumb and the
# untouched camera original, so opening one pulled several MB to fill a screen
# that can't show a fraction of it — brutal on a campsite's cell signal, and
# the reason the viewer sat on a stretched thumbnail for seconds. 1600px covers
# a 1440-wide window and a phone at 3x DPR; the original stays exactly as
# uploaded and is still what the download button saves.
VIEW_DIRNAME = ".views"
VIEW_MAX_PX = 1600
VIEW_QUALITY = 82

# Regenerable caches that live beside the originals. Both are dot-prefixed,
# which is what keeps them out of `_resolve_photo_request` (it rejects any
# dot-prefixed path component) and out of photo listings.
DERIVATIVE_DIRNAMES = (THUMB_DIRNAME, VIEW_DIRNAME)


def _derivative_path(orig_path, dirname):
    """Cache location for a derivative of orig_path. Keeps the full original
    filename (plus .jpg) so same-stem files with different extensions
    can't collide on one cache entry."""
    photo_dir, fname = os.path.split(orig_path)
    return os.path.join(photo_dir, dirname, fname + ".jpg")


def _ensure_derivative(orig_path, dirname, max_px, quality):
    """Return the path of a fresh cached resize of orig_path, generating it if
    missing or older than the original. Returns None when generation fails
    (corrupt/unsupported image) — caller falls back to serving the original.

    Shared by the 480px thumbnail and the 1600px lightbox view; they differ
    only in cache directory, bound and quality.
    """
    tpath = _derivative_path(orig_path, dirname)
    try:
        if os.path.exists(tpath) and os.path.getmtime(tpath) >= os.path.getmtime(orig_path):
            return tpath
        from PIL import Image, ImageOps
        img = Image.open(orig_path)
        # Bake EXIF rotation in: browsers honor orientation on originals,
        # but re-encoding strips the tag, so the pixels must be upright.
        img = ImageOps.exif_transpose(img)
        img.thumbnail((max_px, max_px))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        os.makedirs(os.path.dirname(tpath), exist_ok=True)
        tmp = f"{tpath}.{os.getpid()}.tmp"
        img.save(tmp, "JPEG", quality=quality, optimize=True)
        os.replace(tmp, tpath)  # atomic — concurrent requests can't clobber
        return tpath
    except Exception:
        return None


def _ensure_thumb(orig_path):
    return _ensure_derivative(orig_path, THUMB_DIRNAME, THUMB_MAX_PX, THUMB_QUALITY)


def _ensure_view(orig_path):
    """1600px lightbox derivative. Never upscales — Pillow's thumbnail() is a
    no-op on an image already within the bound, so a small original just gets
    re-encoded at its own size rather than blown up."""
    return _ensure_derivative(orig_path, VIEW_DIRNAME, VIEW_MAX_PX, VIEW_QUALITY)


# ── Photo trash (toast-Undo for single-photo deletes) ────────────────────────
# Single-photo delete moves the file into a .trash subdir beside the
# originals instead of unlinking, so the client's "Photo deleted — Undo"
# toast can really restore it. Caption/order/uploader metadata is kept on
# delete (listings only show files present, so stale keys are inert) and
# scrubbed when the trash entry is purged after TRASH_TTL_S. The .trash
# dirname fails _allowed_file so listings/counts never see it, and
# "Remove All Photos"'s rmtree (still confirm-gated) sweeps it away.

TRASH_DIRNAME = ".trash"
TRASH_TTL_S = 7 * 86400


def _trash_photo(photo_path):
    trash_dir = os.path.join(os.path.dirname(photo_path), TRASH_DIRNAME)
    os.makedirs(trash_dir, exist_ok=True)
    dest = os.path.join(trash_dir, os.path.basename(photo_path))
    os.replace(photo_path, dest)
    # Stamp trash time — the file's own mtime is its upload time, which
    # would make an old photo purge-eligible the moment it's trashed.
    os.utime(dest)


def _restore_from_trash(photo_dir, filename):
    """Move a trashed photo back. Returns (response, status) on failure,
    None on success."""
    src = os.path.join(photo_dir, TRASH_DIRNAME, filename)
    dst = os.path.join(photo_dir, filename)
    if not os.path.exists(src):
        return jsonify({"error": "Nothing to restore"}), 404
    if os.path.exists(dst):
        return jsonify({"error": "A newer photo with that name exists"}), 409
    os.replace(src, dst)
    _invalidate_photo_pool()
    return None


def _purge_old_trash(photo_dir, meta_prefix, order_key):
    """Drop trash entries older than TRASH_TTL_S and scrub their caption/
    order/uploader/favorite metadata. Called opportunistically on each
    delete."""
    trash_dir = os.path.join(photo_dir, TRASH_DIRNAME)
    if not os.path.isdir(trash_dir):
        return
    cutoff = time.time() - TRASH_TTL_S
    purged = []
    for fname in os.listdir(trash_dir):
        p = os.path.join(trash_dir, fname)
        try:
            if os.path.getmtime(p) < cutoff:
                os.remove(p)
                purged.append(fname)
        except OSError:
            pass
    if not purged:
        return
    captions = _load_json(CAPTIONS_FILE)
    if any(captions.pop(meta_prefix + f, None) is not None for f in purged):
        _save_json(CAPTIONS_FILE, captions)
    photo_order = _load_json(PHOTO_ORDER_FILE)
    if order_key in photo_order:
        kept = [f for f in photo_order[order_key] if f not in set(purged)]
        if kept != photo_order[order_key]:
            photo_order[order_key] = kept
            _save_json(PHOTO_ORDER_FILE, photo_order)
    for fname in purged:
        _remove_uploader(meta_prefix + fname)
        _remove_favorite(meta_prefix + fname)


def _remove_thumb(orig_path):
    """Drop every cached derivative for a deleted/moved photo. Best-effort —
    a missed orphan is harmless (mtime staleness covers regeneration) and
    delete-all's rmtree sweeps the whole cache dir anyway."""
    for dirname in DERIVATIVE_DIRNAMES:
        try:
            os.remove(_derivative_path(orig_path, dirname))
        except OSError:
            pass


def _resolve_photo_request(subpath):
    """Map a /thumb/ or /photo/ subpath to a real file under UPLOAD_DIR, or
    None if it isn't a servable photo.

    Three gates, all needed:
    - `safe_join` contains directory traversal.
    - No path component may start with '.', which is what keeps the private
      `.thumbs/` and `.trash/` subdirs unreachable. `_allowed_file` alone does
      NOT do this: it only inspects the basename's extension, so a request for
      `42/0/.trash/img.jpg` would sail through and hand back a photo the user
      had already deleted.
    - `_allowed_file` restricts the extension to real image types.
    """
    if any(part.startswith('.') for part in subpath.replace('\\', '/').split('/')):
        return None
    path = safe_join(UPLOAD_DIR, subpath)
    if not path or not os.path.isfile(path) or not _allowed_file(os.path.basename(path)):
        return None
    return path


@app.route('/thumb/<path:subpath>')
def photo_thumb(subpath):
    """Thumbnail for a photo under UPLOAD_DIR, e.g. /thumb/42/0/img.jpg or
    /thumb/42/events/1/img.jpg. Covered by the global login requirement
    (only the literal `static` endpoint is exempt)."""
    orig = _resolve_photo_request(subpath)
    if not orig:
        return jsonify({"error": "not found"}), 404
    tpath = _ensure_thumb(orig)
    return send_file(tpath or orig, max_age=30 * 86400, conditional=True)


@app.route('/view/<path:subpath>')
def photo_view(subpath):
    """1600px derivative for the lightbox — the display size between /thumb/
    and /photo/.

    Same three gates as the other two (it goes through `_resolve_photo_request`),
    and the same 30-day cache: the derivative is keyed on the original's mtime,
    so replacing a photo regenerates it. Falls back to the original if Pillow
    can't read the file, which is the pre-existing behavior for thumbnails."""
    orig = _resolve_photo_request(subpath)
    if not orig:
        return jsonify({"error": "not found"}), 404
    vpath = _ensure_view(orig)
    return send_file(vpath or orig, max_age=30 * 86400, conditional=True)


@app.route('/photo/<path:subpath>')
def photo_original(subpath):
    """Full-size original for a photo under UPLOAD_DIR — the login-gated
    counterpart to /thumb/, and the only way to fetch one.

    Photos used to live in static/uploads/ and serve as /static/uploads/...,
    but the `static` endpoint is exempt from `_require_login_globally`, so every
    family photo was world-readable to anyone with the URL — and those exact URLs
    ship in the page HTML as the lightbox's `data-full`. Worse, `.trash/` was
    reachable the same way, so a "deleted" photo stayed retrievable. UPLOAD_DIR
    now sits outside static/ entirely (see its definition), which is what makes
    this route the sole entry point even on hosts that serve /static/ from disk
    without consulting Flask."""
    orig = _resolve_photo_request(subpath)
    if not orig:
        return jsonify({"error": "not found"}), 404
    return send_file(orig, max_age=30 * 86400, conditional=True)


# ── Slideshow photo pool ─────────────────────────────────────────────────────
# The trips-map slideshow and the poster border want every uploaded photo.
# Walking ~500 photo directories per request cost ~280ms of every map-page
# render, so the pool is cached: a short TTL bounds staleness from anything
# missed (stay re-sorts renaming dirs, trip deletion), and the photo
# upload/delete/move paths invalidate explicitly so fresh uploads show up
# on the very next render.

_PHOTO_POOL_CACHE = {"ts": 0.0, "pool": None}
_PHOTO_POOL_TTL_S = 60


def _invalidate_photo_pool():
    _PHOTO_POOL_CACHE["pool"] = None


def _display_order(photo_order, order_key, filenames):
    """(filenames in display order, the deliberately-first one or None).

    The display order is the one the trip page uses — the admin's explicit
    drag order first, then anything not in it alphabetically — mirrored here
    so the photo gallery can't disagree with the page a photo actually lives
    on. Keep the two in step: the trip-detail view builds the same list
    inline.

    The second value is the poster's second-choice hero signal, and it's None
    unless a human actually reordered the grid. Without a photo_order entry
    the grid renders alphabetically, and for camera filenames alphabetical is
    just chronological — the FIRST shot of a stay, not the best one — so
    absence resolves to None rather than to filenames[0]. Putting a photo at
    the front of its grid, on the other hand, is already an act of picking a
    favorite; it just was never labeled as one.
    """
    ordered = photo_order.get(order_key) or []
    existing = set(filenames)
    in_order = [f for f in ordered if f in existing]
    listed = set(ordered)
    display = in_order + sorted(f for f in filenames if f not in listed)
    return display, (in_order[0] if in_order else None)


def _collect_photo_pool():
    """Every uploaded photo across all trips: {key, url, thumb, view, trip_id,
    card, caption, favorite, curated, home_only}. Built from the unfiltered
    trip list; callers filter home_only per viewer and must copy before
    shuffling/mutating (the list and its items are shared across requests).

    `caption` is the same text the trip page shows under the photo (the
    trips-map lightbox displays it). It comes from one captions.json read
    per pool build — cheap, unlike the EXIF date, which would need a Pillow
    open per file and so is deliberately not carried here.

    `favorite` is the hand-set poster mark; `curated` means the photo leads
    its grid (see _curated_first). Together they rank the poster's hero
    candidates. Both are whole-file reads like captions, and every writer
    invalidates this cache, so an edit shows up without waiting out the TTL.

    Deliberately NOT carried: image dimensions. Those need a Pillow open per
    file, same as the EXIF date — the poster probes the aspect of the handful
    of photos it actually considers for a hero cell, client-side, instead."""
    now = time.time()
    if _PHOTO_POOL_CACHE["pool"] is not None and now - _PHOTO_POOL_CACHE["ts"] < _PHOTO_POOL_TTL_S:
        return _PHOTO_POOL_CACHE["pool"]
    captions = _load_json(CAPTIONS_FILE)
    favorites = _load_json(PHOTO_FAVORITES_FILE)
    photo_order = _load_json(PHOTO_ORDER_FILE)
    pool = []
    for trip in parse_trips():
        tid = trip["id"]
        home_only = bool(trip.get("home_only"))
        # Stays and events differ only in the path/key segment between the
        # trip id and the index, so walk them with one body.
        cards = [(f"{tid}/{i}", f"stay-{i}", os.path.join(UPLOAD_DIR, str(tid), str(i)))
                 for i, _stay in enumerate(trip["stays"])]
        cards += [(f"{tid}/events/{i}", f"event-{i}",
                   os.path.join(UPLOAD_DIR, str(tid), "events", str(i)))
                  for i, _event in enumerate(trip.get("events", []))]
        for key_base, card, photo_dir in cards:
            if not os.path.isdir(photo_dir):
                continue
            fnames = [f for f in os.listdir(photo_dir) if _allowed_file(f)]
            display, first = _display_order(photo_order, key_base, fnames)
            for pos, fname in enumerate(display):
                key = f"{key_base}/{fname}"
                pool.append({
                    # The storage subpath, which is both the metadata key and
                    # the tail of every URL below — templates hand it to the
                    # favorites API rather than re-deriving it from a src.
                    "key": key,
                    "url": f"/photo/{key}",
                    "thumb": f"/thumb/{key}",
                    "view": f"/view/{key}",
                    "trip_id": tid,
                    "card": card,
                    "caption": captions.get(key, ""),
                    "favorite": bool(favorites.get(key)),
                    "curated": fname == first,
                    # Position within its own grid, in the order the trip page
                    # shows them — what the gallery sorts photos by inside a
                    # campspot or event.
                    "photo_seq": pos,
                    "home_only": home_only,
                })
    _PHOTO_POOL_CACHE.update(ts=now, pool=pool)
    return pool


def _load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save_json(path, data):
    # ensure_ascii=False keeps em-dashes/accents/unicode in notes literal (— not
    # —) so a UI edit to one campground doesn't rewrite every other entry's
    # note into escaped form — that churn made git diffs/merges noisy. Explicit
    # utf-8 so the literal bytes are written regardless of host locale.
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Keys the app reads out of home.json (gitignored per-machine config).
_HOME_REQUIRED_KEYS = ("home_lat", "home_long", "home_altitude_meters")


def _check_home_config():
    """Startup diagnostic: warn (don't crash) if home.json is absent or missing
    required keys.

    home.json is gitignored per-machine config (home coordinates + altitude) and
    is NOT created by a fresh clone. Without it the campground climate map and the
    home markers can't compute and will 500. Report the problem loudly at startup
    rather than letting it surface as an opaque request-time TypeError.
    """
    if not os.path.exists(HOME_FILE):
        print(f"WARNING: home config not found at {HOME_FILE}. The campground "
              f"climate map and home markers will not work until it exists. "
              f"Create it as JSON with keys: {', '.join(_HOME_REQUIRED_KEYS)}.",
              file=sys.stderr)
        return False
    cfg = _load_json(HOME_FILE)
    missing = [k for k in _HOME_REQUIRED_KEYS if cfg.get(k) is None]
    if missing:
        print(f"WARNING: {HOME_FILE} is missing required key(s): "
              f"{', '.join(missing)}. The campground climate map / home markers "
              f"may error until these are set.", file=sys.stderr)
        return False
    return True


# ── User authentication ────────────────────────────────────────────────────

class User(UserMixin):
    def __init__(self, username, password_hash, is_admin=False, can_upload=False,
                 can_view_campgrounds=True):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        # Admins implicitly carry upload rights — checking can_upload alone is
        # always sufficient for upload-gated endpoints.
        self.can_upload = bool(is_admin) or bool(can_upload)
        # Campground-section access. Defaults on (existing users are unaffected);
        # a "Trips-only" user has this cleared and cannot reach any Campgrounds
        # page or data API. Admins always retain access.
        self.can_view_campgrounds = bool(is_admin) or bool(can_view_campgrounds)


def _load_users():
    return {name: User(name, info["password_hash"],
                       info.get("is_admin", False),
                       info.get("can_upload", False),
                       info.get("can_view_campgrounds", True))
            for name, info in _load_json(USERS_FILE).items()}


def _save_user(username, password, is_admin=False, can_upload=False,
               can_view_campgrounds=True):
    data = _load_json(USERS_FILE)
    data[username] = {
        "password_hash": generate_password_hash(password),
        "is_admin": is_admin,
        "can_upload": can_upload,
        "can_view_campgrounds": can_view_campgrounds,
    }
    _save_json(USERS_FILE, data)


# Share-link (read-only magic-link) sessions carry a synthetic user id
# "share:<token>" that maps to a viewer with neither admin nor upload rights.
SHARE_ID_PREFIX = "share:"


def _make_share_user(token, trips_only=False):
    """Synthetic read-only user backing a share link (no admin, no upload).
    Its username is 'share:<token>', which never matches a photo uploader
    record and is rejected as a real username, so it stays purely a viewer.
    `trips_only` links additionally have Campgrounds-section access cleared."""
    return User(SHARE_ID_PREFIX + token, "", is_admin=False, can_upload=False,
                can_view_campgrounds=not trips_only)


@login_manager.user_loader
def load_user(username):
    # Resolve share-link sessions against share_tokens.json on every request so
    # that revoking (deleting) a token instantly invalidates its sessions — and
    # so a token's trips_only flag takes effect the moment it's edited.
    if username and username.startswith(SHARE_ID_PREFIX):
        token = username[len(SHARE_ID_PREFIX):]
        rec = _load_json(SHARE_TOKENS_FILE).get(token)
        if rec is not None:
            return _make_share_user(token, rec.get("trips_only", False))
        return None
    users = _load_users()
    return users.get(username)


@app.before_request
def _require_login_globally():
    # Public endpoints that must remain accessible without authentication.
    # service_worker/offline: the SW registers from the login page too, and
    # its install step pre-caches /offline — a login redirect there would
    # cache the login screen as the offline fallback.
    # sw_reset: the SW kill-switch must work even when the user can't get past
    # an upstream error (e.g. a stale SW), so it stays reachable logged-out.
    #
    # `static` is exempt because CSS/JS/icons must load on the login page. The
    # photo library used to live under static/uploads/, where that exemption made
    # every photo (and every not-yet-purged .trash/ copy) world-readable to
    # anyone holding the URL. UPLOAD_DIR has since moved out of static/ entirely,
    # so this is now a backstop rather than the primary defence: it refuses the
    # old URL shape if a stale static/uploads/ ever reappears — an old backup
    # restored over the tree, a half-finished migration on a new host — instead
    # of quietly starting to serve photos again.
    if request.endpoint == 'static':
        filename = (request.view_args or {}).get('filename', '')
        if filename.replace('\\', '/').startswith('uploads/'):
            # Refused outright rather than login-gated: /photo/ is the one way
            # in, and it enforces the .thumbs/.trash exclusion that the raw
            # static handler knows nothing about.
            abort(404)
        return None
    # 'logout' is exempt so that hitting it while already signed out (a stale
    # tab, a double-click, a service-worker-cached page) just lands on the clean
    # login page. Gating it instead stashed ?next=/logout, which meant the next
    # successful login redirected straight back into logout — a self-inflicted
    # loop you could never log in through.
    elif request.endpoint in ('login', 'logout', 'service_worker', 'offline',
                              'sw_reset', 'share_login', 'serve_tile',
                              'serve_pmtiles', None):
        return None
    if not current_user.is_authenticated:
        # full_path (not path) so a query string survives the round trip — e.g.
        # /campgrounds/map?color=climate comes back with its mode intact. Flask
        # appends a bare '?' when there's no query, which would otherwise ride
        # along into the post-login redirect.
        return redirect(url_for('login', next=request.full_path.rstrip('?')))
    return None


# ── Access log ──────────────────────────────────────────────────────────────
# Who visited which page, including share-link guests. The server's own request
# log (e.g. PythonAnywhere's) can't answer this: the identity lives only inside
# Flask-Login, so it has to be recorded here.

# Endpoints never worth a log line. Photos/thumbs/tiles/static are the reason
# this list exists at all — one trip page with 40 photos fires 40+ thumb
# requests, which would bury the page views the log is for.
_ACCESS_LOG_SKIP_ENDPOINTS = frozenset({
    'static', 'serve_tile', 'serve_pmtiles', 'service_worker', 'photo_thumb',
    'sw_reset', 'offline', 'logout', None,
})


def _redact_path(path):
    """Blunt the share token in '/s/<token>' before it reaches the log.

    The token IS the credential — anyone holding it is logged in as that
    viewer. Writing it to a file that gets read, screenshotted, or copied
    around would hand out working access, so only a short prefix is kept:
    enough to tell which link was used, useless as a key."""
    if path.startswith('/s/'):
        token = path[3:].split('/', 1)[0]
        if len(token) > 8:
            return '/s/' + token[:8] + '…'
    return path


def _share_label(token):
    """Human label for a share token ('Papa & Bonnie'), falling back to a
    truncated token when the record is gone (revoked after the visit)."""
    rec = _load_json(SHARE_TOKENS_FILE).get(token)
    if rec and rec.get("label"):
        return rec["label"]
    return "share:" + token[:8]


def _access_identity():
    """(kind, who) for the current session.

    kind is 'user' | 'share' | 'anon'. For share links `who` is the token's
    label, so the log reads 'Papa & Bonnie' rather than an opaque token."""
    if not current_user.is_authenticated:
        return "anon", None
    name = getattr(current_user, "id", None) or ""
    if name.startswith(SHARE_ID_PREFIX):
        return "share", _share_label(name[len(SHARE_ID_PREFIX):])
    return "user", name


def _log_access(event, path=None, status=None, extra=None):
    """Append one JSONL entry. Never raises — logging must not break a request.

    `event` is 'page' for ordinary views, or 'login'/'login_failed'/
    'share_login'/'logout' for auth transitions."""
    try:
        kind, who = _access_identity()
        rec = {
            # UTC-aware (carries +00:00) so the browser can convert to the
            # viewer's local tz. A naive datetime.now() has no marker and the
            # browser would wrongly read it as local wall-clock.
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event,
            "kind": kind,
            "who": who,
            "path": _redact_path(path if path is not None else request.path),
            "ip": request.headers.get("X-Forwarded-For", request.remote_addr or ""
                                      ).split(",")[0].strip(),
            # Trimmed: full UA strings are long and the tail is boilerplate.
            "ua": (request.headers.get("User-Agent") or "")[:180],
        }
        if status is not None:
            rec["status"] = status
        if extra:
            rec.update(extra)
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        with open(ACCESS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


@app.after_request
def _log_page_view(response):
    """Log HTML page views only.

    Gated to text/html GETs so the log stays a record of pages a person looked
    at, not of every asset their browser fetched. Redirects are logged too (a
    302 to /login is exactly the 'tried to reach X while logged out' signal)."""
    try:
        if request.method != "GET":
            return response
        if request.endpoint in _ACCESS_LOG_SKIP_ENDPOINTS:
            return response
        if request.path.startswith(('/api/', '/thumb/', '/static/')):
            return response
        ctype = (response.content_type or "")
        if not ctype.startswith("text/html"):
            return response
        _log_access("page", status=response.status_code)
    except Exception:
        pass
    return response


def _read_access_log(limit=None):
    """Parse the JSONL log newest-first. Bad lines are skipped rather than
    failing the page — a torn final line (crash mid-write) must not blind the
    whole log."""
    if not os.path.exists(ACCESS_LOG_FILE):
        return []
    out = []
    with open(ACCESS_LOG_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    out.reverse()
    return out[:limit] if limit else out


def _prune_access_log():
    """Drop entries older than ACCESS_LOG_RETENTION_DAYS. Rewrites via a temp
    file + atomic replace so a crash mid-prune can't truncate the log."""
    if not os.path.exists(ACCESS_LOG_FILE):
        return 0
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ACCESS_LOG_RETENTION_DAYS)).isoformat()
    kept, dropped = [], 0
    with open(ACCESS_LOG_FILE, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                if json.loads(s).get("ts", "") >= cutoff:
                    kept.append(line if line.endswith("\n") else line + "\n")
                else:
                    dropped += 1
            except ValueError:
                dropped += 1
    if dropped:
        tmp = ACCESS_LOG_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(kept)
        os.replace(tmp, ACCESS_LOG_FILE)
    return dropped


def _require_admin():
    """Return an error response if current user is not an admin, else None."""
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    return None


def _require_admin_page():
    """For admin PAGE routes: send a non-admin to the trips map with a notice.

    Emphatically NOT the login page. `_require_login_globally` is a
    before_request, so anyone who reaches one of these views is already
    authenticated — bouncing them to /login is an infinite loop: they log in
    successfully, the ?next= we set sends them straight back here, and we
    bounce them to /login again. From the user's side that is indistinguishable
    from a rejected password, which is exactly how it got reported (a non-admin
    family account landed on /admin/users and re-typed their password four
    times, 2026-07-26 — the access log shows four successful logins and zero
    failures).
    """
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('trips_map', notice='admin_only'))
    return None


def _require_uploader_or_admin():
    """Gate endpoints that uploader-role users may also use (photo POST + own-photo
    caption edits). Admins always pass since User.can_upload is True for them."""
    if not current_user.is_authenticated or not getattr(current_user, "can_upload", False):
        return jsonify({"error": "Upload access required"}), 403
    return None


@app.context_processor
def inject_share_identity():
    """Expose share-link guest identity to every template.

    Two consumers: the nav suppresses Logout for guests (a one-way door — they
    have no password to get back in), and the landing page puts their magic
    link in the address bar so bookmarking works.
    """
    name = (getattr(current_user, "id", "") or "") if current_user.is_authenticated else ""
    if not name.startswith(SHARE_ID_PREFIX):
        return {"is_share_guest": False, "share_guest_url": ""}
    token = name[len(SHARE_ID_PREFIX):]
    # The guest's own magic link. The landing page swaps it into the address bar
    # (see trips_map.html) so that "bookmark this page" saves something that
    # still works on a new device — `/s/<token>` 302s away, so the address bar
    # otherwise only ever held an ordinary path that dies with the cookie.
    #
    # Only ever rendered for the holder of that token — they arrived with it —
    # so this exposes nothing they don't already have.
    return {"is_share_guest": True,
            "share_guest_url": url_for('share_login', token=token)}


def _can_view_campgrounds():
    """True unless the current user is a Trips-only user (campground access cleared)."""
    return (current_user.is_authenticated
            and getattr(current_user, "can_view_campgrounds", True))


def _require_campground_view_page():
    """For Campgrounds-section page routes: redirect Trips-only users away to the
    trips map. Returns a response to short-circuit with, or None to proceed.

    Carries ?notice= so the landing page can say *why* — a silent bounce makes a
    campground link texted by a family member read as a broken link rather than
    a permission boundary. base.html turns the param into a toast and strips it.
    """
    if not _can_view_campgrounds():
        return redirect(url_for('trips_map', notice='campgrounds_restricted'))
    return None


def _require_campground_view_api():
    """For Campgrounds-section data APIs: 403 Trips-only users. Returns a response
    to short-circuit with, or None to proceed."""
    if not _can_view_campgrounds():
        return jsonify({"error": "Campground access required"}), 403
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


# ── Photo favorites (poster heroes) ───────────────────────────────────────
# Admin-only curation, keyed like captions. Read by the poster (its hero cells
# deal from the marked set first) and by the Photos page's Favorites filter.
# Every writer invalidates the photo pool, which carries the flag — otherwise a
# star wouldn't show up until the pool's TTL expired.

def _set_favorite(photo_key, on):
    """Star/unstar one photo. Returns the resulting state."""
    data = _load_json(PHOTO_FAVORITES_FILE)
    if bool(data.get(photo_key)) != bool(on):
        if on:
            data[photo_key] = True
        else:
            data.pop(photo_key, None)
        _save_json(PHOTO_FAVORITES_FILE, data)
        _invalidate_photo_pool()
    return bool(on)


def _remove_favorite(photo_key):
    data = _load_json(PHOTO_FAVORITES_FILE)
    if data.pop(photo_key, None) is not None:
        _save_json(PHOTO_FAVORITES_FILE, data)
        _invalidate_photo_pool()


def _remove_favorites_by_prefix(prefix):
    data = _load_json(PHOTO_FAVORITES_FILE)
    pruned = {k: v for k, v in data.items() if not k.startswith(prefix)}
    if len(pruned) != len(data):
        _save_json(PHOTO_FAVORITES_FILE, pruned)
        _invalidate_photo_pool()


def _rename_favorite_key(old_key, new_key):
    data = _load_json(PHOTO_FAVORITES_FILE)
    if old_key in data:
        data[new_key] = data.pop(old_key)
        _save_json(PHOTO_FAVORITES_FILE, data)
        _invalidate_photo_pool()


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        'error.html', code=404, heading="This trail doesn't exist",
        message="The page you're looking for isn't here — it may have "
                "been moved or the link is off."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template(
        'error.html', code=500, heading="Something broke down",
        message="The app hit an unexpected error. Heading back to the "
                "map usually fixes it; if it keeps happening, tell Andrew."), 500


@app.route('/sw.js')
def service_worker():
    """Serve the service worker from the site root: a worker's maximum
    scope is its script's directory, so /static/sw.js could only control
    /static/. no-cache so browsers re-check it on each load and updates
    (VERSION bumps) propagate promptly."""
    resp = send_file(os.path.join(os.path.dirname(__file__), 'static', 'sw.js'),
                     mimetype='application/javascript')
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/manifest.json')
def web_manifest():
    """The PWA manifest, served dynamically so a share guest's `start_url` is
    their own magic link.

    The static manifest hard-codes `start_url: "/"`, which is right for anyone
    with a password and actively broken for a guest: "Add to Home Screen" gives
    them an icon that launches at `/`, and an installed iOS web app does not
    share Safari's cookie jar — so the app they just installed opens on a login
    form they can never get past. Pointing `start_url` at `/s/<token>` makes the
    installed icon self-authenticating, which is the only thing that fixes the
    home-screen case (a bookmark they can copy doesn't).

    Everyone else gets exactly the static file's contents.
    """
    with open(os.path.join(_STATIC_DIR, 'manifest.json')) as f:
        manifest = json.load(f)
    name = (getattr(current_user, "id", "") or "") if current_user.is_authenticated else ""
    if name.startswith(SHARE_ID_PREFIX):
        manifest['start_url'] = url_for('share_login',
                                        token=name[len(SHARE_ID_PREFIX):])
    resp = jsonify(manifest)
    # Per-user content: never let a shared cache hand one guest's start_url to
    # somebody else.
    resp.headers['Cache-Control'] = 'private, no-cache'
    return resp


@app.route('/offline')
def offline():
    """Offline fallback page, pre-cached by the service worker at install."""
    return render_template('offline.html')


@app.route('/tiles/street.pmtiles')
def serve_pmtiles():
    """Serve the vector street basemap (Option A) as a single .pmtiles file.
    protomaps-leaflet reads it via HTTP Range requests, so conditional=True
    (Werkzeug honors Range) is required. Inert (404) without a local store."""
    path = os.path.join(LOCAL_TILE_DIR, "street.pmtiles")
    if not os.path.isfile(path):
        abort(404)
    return send_file(path, mimetype="application/octet-stream", conditional=True)


@app.route('/tiles/<layer>/<int:z>/<int:x>/<int:y>.<ext>')
def serve_tile(layer, z, x, y, ext):
    """Serve a raster map tile from the stick's MBTiles store (satellite NAIP,
    or a raster street fallback). Inert (404) when the store isn't present, so
    a normal deploy is unaffected. MBTiles rows are TMS (y flipped) vs Leaflet
    XYZ, so flip y on lookup."""
    store = _tile_store(layer)
    if store is None:
        abort(404)
    flipped = (1 << z) - 1 - y
    row = store.execute(
        "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
        (z, x, flipped)).fetchone()
    if not row:
        abort(404)
    mime = "image/png" if ext == "png" else "image/jpeg"
    return Response(row[0], mimetype=mime,
                    headers={"Cache-Control": "public, max-age=31536000"})


@app.route('/sw-reset')
def sw_reset():
    """Kill-switch for a device wedged by a stale/misbehaving service worker:
    a self-contained page whose JS unregisters every SW and deletes its caches,
    then offers a fresh reload. Login-exempt so it stays reachable even when
    something upstream is breaking normal pages (it exposes no data, only
    teardown JS). no-store so the page itself is never cached."""
    return render_template('sw_reset.html'), 200, {'Cache-Control': 'no-store'}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = _load_users()
        user = users.get(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            _log_access("login")
            # Honor ?next= so a deep link survives the login detour.
            # `_require_login_globally` sets it on every redirect here, and the
            # form posts back to this same URL (no action attr), so the param is
            # still present on both the first attempt and any retry after a bad
            # password. `_safe_next` keeps it a same-site path.
            return redirect(_safe_next(request.args.get('next')))
        # Log the attempted username, not the password. A run of these from one
        # IP is the only signal you'd get that someone is guessing.
        _log_access("login_failed", extra={"attempted": username[:64]})
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Explicit sign-out: drop any ?next= and land on a clean login page.

    Login is global here, so after logout *every* path redirects to /login
    anyway — carrying ?next= through accomplishes exactly one thing: it
    pre-loads the DEPARTING user's last page as the ARRIVING user's
    destination. That's the wrong intent (logging out is a deliberate "I'm
    done"), it quietly tells the next person on a shared family device where
    you'd been, and it produced a genuinely bad failure mode: logging out from
    /admin/users handed the next person a login form that bounced them
    straight back to an admin page they couldn't see (see _require_admin_page).

    `next` is ignored here rather than merely dropped from the nav link, so a
    service-worker-cached page still carrying the old ?next= link can't
    resurrect the behavior.
    """
    if current_user.is_authenticated:
        _log_access("logout")      # before logout_user, while identity still resolves
        logout_user()
    return redirect(url_for('login', signed_out=1))


def _safe_next(path, default="/"):
    """Restrict a redirect target to a same-site absolute path so ?next= can't
    be turned into an open redirect (rejects '//host', '/\\host', absolute URLs)."""
    if path and path.startswith("/") and not path.startswith(("//", "/\\")):
        return path
    return default


@app.route('/s/<token>')
def share_login(token):
    """Read-only magic link: an unguessable token logs a guest in as a viewer
    (no admin, no upload) and deep-links to ?next=. Because every mutation route
    is admin/contributor-gated, a leaked link exposes only viewing, so a long
    random token needs no password. Unknown/revoked tokens get an explanatory
    page rather than revealing anything."""
    rec = _load_json(SHARE_TOKENS_FILE).get(token)
    if rec is None:
        # Previously this rendered the LOGIN FORM with an error line, which is
        # the worst possible answer for the audience: a relative who has no
        # account, staring at a password box. Nothing on that page could help
        # them, so it read as "the site is broken" rather than "this link was
        # replaced." Say what happened and what to do about it instead; the
        # sign-in link stays as a quiet hint for family who do have accounts.
        _log_access("share_revoked", extra={"token": token[:8]})
        return render_template(
            'error.html', code="🔗", heading="This link is no longer active",
            message="Share links get replaced from time to time. Ask Andrew "
                    "for a fresh one and it'll work straight away — nothing "
                    "is wrong on your end.",
            cta_href=None,
            hint='Have an account? <a href="/login">Sign in</a>'), 403
    login_user(_make_share_user(token, rec.get("trips_only", False)), remember=True)
    _log_access("share_login", extra={"label": rec.get("label") or ""})
    # ?next= wins when present, but messaging apps routinely strip query strings
    # off a pasted link — so fall back to the destination stored on the link at
    # creation time, which until now was written and then never read.
    return redirect(_safe_next(request.args.get('next') or rec.get('next')))


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


def _file_mtime_ns(path):
    """mtime in ns, or 0 if the file is missing — a cheap cache key component."""
    try:
        return os.stat(path).st_mtime_ns
    except OSError:
        return 0


# campgrounds.json is ~9.5 MB / 10k entries and used to be re-read + full-parsed
# on every map/picker/stats request. These two caches skip the re-parse while the
# file is unchanged, keyed on its mtime so any edit (API save, git pull, manual)
# invalidates automatically. The RAW cache holds the parsed list; callers must
# treat it as READ-ONLY (build new dicts, never mutate in place) — the mutating
# API endpoints deliberately keep their own fresh json.load.
_campgrounds_raw_cache = {"mtime": None, "entries": None}
_campgrounds_derived_cache = {"key": None, "rows": None}


def _read_campgrounds_raw():
    """Return the parsed campgrounds.json list, cached by file mtime.

    READ-ONLY: the returned list/objects are shared across callers, so never
    mutate them (or the cache goes stale). Endpoints that edit + save load their
    own fresh copy instead.
    """
    mtime = _file_mtime_ns(CAMPGROUNDS_JSON)
    if _campgrounds_raw_cache["mtime"] != mtime:
        with open(CAMPGROUNDS_JSON) as f:
            _campgrounds_raw_cache["entries"] = json.load(f)
        _campgrounds_raw_cache["mtime"] = mtime
    return _campgrounds_raw_cache["entries"]


def _load_campgrounds():
    """Load campground-kind entries from JSON with derived climate fields.

    Family-kind entries are excluded so they don't appear on waterfront/climate maps.

    The derived rows are cached and reused while campgrounds.json, home.json, and
    trips.json (the three inputs — the last via the visit index) are all unchanged.
    """
    key = (_file_mtime_ns(CAMPGROUNDS_JSON),
           _file_mtime_ns(HOME_FILE),
           _file_mtime_ns(TRIPS_JSON))
    if _campgrounds_derived_cache["key"] == key:
        return _campgrounds_derived_cache["rows"]

    config = _load_json(HOME_FILE)
    home_lat = config.get("home_lat")
    home_alt = config.get("home_altitude_meters")
    entries = _read_campgrounds_raw()
    visits_by_cg = _campground_visits_index()

    # `waterfront_evidence` / `inclusion_evidence` are the audit trail — the
    # proof strings behind each entry's waterfront and validity calls. They are
    # the source of truth in campgrounds.json, but no template or client script
    # reads them, and at ~12.9k entries they were 4.6 MB of the map page's
    # 14.4 MB. Dropping them here keeps them out of every browser payload while
    # leaving the file untouched (PUT merges from a field whitelist, so a UI
    # save can't clobber what the client never received).
    excluded = {"index", "stays", "elevation_meters",
                "waterfront_evidence", "inclusion_evidence"}
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

    _campgrounds_derived_cache["key"] = key
    _campgrounds_derived_cache["rows"] = rows
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
    entries = _read_campgrounds_raw()
    for e in entries:
        if e.get("kind") != "family" or "location" not in e:
            continue
        flat, flng = (float(x) for x in e["location"].split(","))
        fam = {"id": e["id"], "label": e["name"], "lat": flat, "lng": flng,
               "state": e.get("state") or ""}
        dl = e.get("driveway_location")
        if dl:
            dlat, dlng = (float(x) for x in dl.split(","))
            fam["driveway_lat"] = dlat
            fam["driveway_lng"] = dlng
        family.append(fam)
    return home, family


def _load_roadside_raw():
    """Raw roadside stop list (full stored fields, incl. `id`) for CRUD.

    These are leg-stretch spots (small-town parks, roadside picnic areas, rest
    areas) — distinct from overnight campgrounds, so they live in their own
    `roadside.json`. Returns [] if the file is missing or malformed so the map
    still renders.
    """
    try:
        with open(ROADSIDE_JSON) as f:
            data = json.load(f)
    except (FileNotFoundError, ValueError):
        return []
    return data.get("stops", []) if isinstance(data, dict) else data


def _save_roadside(stops):
    """Persist the raw roadside stop list back to roadside.json.

    Uses ensure_ascii=False so the em-dashes/accents in notes stay literal
    (matching the seed file) instead of churning into \\uXXXX escapes.
    """
    with open(ROADSIDE_JSON, "w", encoding="utf-8") as f:
        json.dump({"stops": stops}, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _roadside_view(s):
    """Map a raw roadside entry to the shape the campground map consumes.

    The seed file carries route-planning artifacts (`highway`,
    `approx_miles_from_start`) from how the list was generated; those aren't
    relevant to a general map and are dropped here. `google_maps_url` is
    surfaced as `maps_url`, and `latitude`/`longitude` as `lat`/`lng`.
    """
    return {
        "id": s.get("id"),
        "name": s.get("name", "Roadside stop"),
        "town": s.get("town"),
        "state": s.get("state"),
        "lat": s.get("latitude"),
        "lng": s.get("longitude"),
        "notes": s.get("notes"),
        "rating": s.get("rating"),
        "rating_count": s.get("rating_count"),
        "website": s.get("website"),
        "phone": s.get("phone"),
        "maps_url": s.get("google_maps_url"),
    }


def _load_roadside():
    """Roadside stops shaped for the campground map (drops coordinate-less rows)."""
    return [_roadside_view(s) for s in _load_roadside_raw()
            if s.get("latitude") is not None and s.get("longitude") is not None]


# Fields the campground map needs on EVERY marker, up front: enough to place the
# dot, color it, filter it, search it, and open a popup header. Everything else
# (note, website, phone, elevation, the visited-trips list) is popup filler —
# real content, but only ever for the one or two entries a user actually clicks.
# At ~12.9k rows the filler dominated the page: `note` alone was 3.88 MB and
# `website` another 1.09 MB of a 7.54 MB inline blob. It now loads on demand from
# `/api/campgrounds/<id>/popup`.
_MAP_MARKER_FIELDS = ("id", "name", "state", "location",
                      "waterfront", "climate", "ownership", "visit_count")
# Popup-only fields, served per-id by the detail endpoint.
_MAP_POPUP_FIELDS = ("elevation_feet", "note", "phone", "website", "trips")


def _map_marker_rows(rows):
    """Project campground rows down to the per-marker essentials.

    Also drops two fields nothing has ever read: `delta_temp` (superseded by the
    `climate` label derived from it) and `kind`, which is the constant
    "campground" here because `_load_campgrounds` already filtered family
    entries out — together ~384 KB of pure padding.
    """
    return [{k: r[k] for k in _MAP_MARKER_FIELDS if k in r} for r in rows]


def _parse_latlng(loc):
    """Parse a 'lat,lng' string into (lat, lng) floats, or None if invalid."""
    try:
        lat, lng = [float(x) for x in (loc or "").split(",")[:2]]
    except (ValueError, IndexError):
        return None
    return lat, lng


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

    # Slideshow photos from the cached pool; non-admins don't see
    # home-only trips' photos. The comprehension copies, so shuffling
    # doesn't disturb the shared cache.
    import random
    all_photos = [p for p in _collect_photo_pool()
                  if is_admin or not p["home_only"]]
    random.shuffle(all_photos)

    # Banner above the map links to the most recently-started visible trip.
    # `parse_trips()` already sorts ascending by start; empty new trips have
    # an empty start string and would otherwise sort first, but we walk in
    # reverse so they're skipped naturally — the banner only appears when
    # there's an actual dated trip to point at. Home-only trips are skipped
    # even for admins (who still see them on the map) — they aren't trips
    # worth surfacing in the banner.
    latest_trip = next((t for t in reversed(trips)
                        if t.get("start") and not t.get("home_only")), None)
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


# Photos per gallery page. Big enough that paging is rare on a normal visit,
# small enough that one page is a bounded number of thumbnail requests.
PHOTOS_PER_PAGE = 60


_PHOTO_INDEX_CACHE = {"pool": None, "items": None}


def _photo_gallery_index():
    """The photo pool enriched with everything the gallery searches, sorts and
    groups by: trip name/date, the campspot/event place, the year, a sort
    position for the trip and the card, and a normalized search haystack.

    Built over the WHOLE library rather than a page slice — search, the year
    filter and the facet counts all have to see every photo, and which 60 the
    page shows is decided only after filtering.

    Cached against the pool OBJECT it was built from, so it rebuilds exactly
    when `_collect_photo_pool()` does — on that pool's 60 s TTL or on any
    explicit invalidation — and inherits the same freshness contract as the
    landing slideshow and the poster. That also covers a trip or campground
    rename, since those reach this page only through `parse_trips()`. Worth
    caching: it costs ~50 us per photo (238 ms for 5,000, measured), which is
    per-request work whose answer only changes when a photo or a trip does,
    and the request that pays for it is already paying for the pool rebuild.

    Includes `home_only` photos; callers filter those per viewer, which is a
    reference filter rather than the dict building done here.
    """
    pool = _collect_photo_pool()
    if _PHOTO_INDEX_CACHE["pool"] is pool:
        return _PHOTO_INDEX_CACHE["items"]

    trips = parse_trips()          # sorted ascending by start
    by_id = {t["id"]: t for t in trips}
    seq = {t["id"]: i for i, t in enumerate(trips)}
    # One timeline lookup per trip rather than per photo.
    timelines = {t["id"]: _timeline_positions(t) for t in trips}
    items = []
    for p in pool:
        trip = by_id.get(p["trip_id"]) or {}
        place, state = _photo_card_meta(trip, p["card"])
        name = (f"Trip {trip['number']}: {trip['summary']}"
                if trip.get("number") else trip.get("summary", ""))
        year = (trip.get("start") or "")[:4]
        # The pool's items are shared across requests, so build new dicts
        # rather than annotating them (see _collect_photo_pool's docstring).
        items.append({
            **p,
            "trip_name": name,
            "trip_date": _short_trip_date(trip.get("start")),
            "place": place,
            "year": year,
            "trip_seq": seq.get(p["trip_id"], -1),
            # Where this photo's campspot/event sits in the trip's timeline.
            # A card the timeline doesn't mention (photos orphaned by a
            # deleted campspot) sorts after everything it does, in a stable
            # order rather than an arbitrary one.
            "card_order": (timelines.get(p["trip_id"], {}).get(p["card"], len(pool)),
                           _photo_card_order(p["card"])),
            # One normalized haystack per photo, so a multi-term query is a
            # handful of substring tests instead of a field-by-field walk.
            "search": _search_haystack(name, place, state, p["caption"], year),
        })
    _PHOTO_INDEX_CACHE.update(pool=pool, items=items)
    return items


@app.route('/trips/photos')
def trips_photos():
    """Every photo across every trip: searchable, filterable, grouped, paged.

    The Stats page counts photos in its hero row and that number led nowhere,
    because there was no cross-trip view of them — the only way to see a photo
    was to already know which trip it was on. Built on the same cached
    `_collect_photo_pool()` the landing slideshow and poster use.

    Every control is a query param — `q`, `year`, `favorites`, `sort`, `page` —
    so a filtered view is bookmarkable and shareable, Back works, and paging
    can't silently drop a filter. Filtering is server-side because the library
    is thousands of photos and only 60 are ever in the DOM; a client-side
    filter would have to ship all of them.
    """
    is_admin = current_user.is_authenticated and current_user.is_admin
    items = [it for it in _photo_gallery_index()
             if is_admin or not it["home_only"]]

    # Facets are counted against the whole library, before any filter, so the
    # year list never loses options and the Favorites chip can show its total
    # while the favorites filter is on.
    library_total = len(items)
    fav_total = sum(1 for it in items if it["favorite"])
    years = sorted({it["year"] for it in items if it["year"]}, reverse=True)

    q = (request.args.get('q') or '').strip()
    year = (request.args.get('year') or '').strip()
    # Favorites are the poster's hero pool, so this page doubles as the place
    # you curate it: mark from the grid, then filter down to review what you
    # marked. Non-admins can't mark, but the filter is a perfectly good
    # "best of" view, so it isn't gated.
    favorites_only = request.args.get('favorites') == '1'
    sort = 'oldest' if request.args.get('sort') == 'oldest' else 'newest'

    if favorites_only:
        items = [it for it in items if it["favorite"]]
    if year:
        items = [it for it in items if it["year"] == year]
    if q:
        # Every term has to match somewhere: "utah lake" narrows rather than
        # widening, which is what a reader typing two words expects.
        terms = [' ' + t for t in _search_terms(q)]
        items = [it for it in items if all(t in it["search"] for t in terms)]

    # Two stable passes rather than one composite key, so a trip's photos read
    # in the trip's own timeline order — campspots and events interleaved by
    # date, then each grid in the order the trip page shows it — whichever way
    # the trips themselves are ordered. Sorting is never reversed WITHIN a
    # trip: "newest trip first" is about which trip you see first, not about
    # reading a trip backwards.
    items.sort(key=lambda it: (it["card_order"], it["photo_seq"], it["url"]))
    items.sort(key=lambda it: it["trip_seq"], reverse=(sort == 'newest'))

    total = len(items)
    pages = max(1, (total + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE)
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    page = max(1, min(page, pages))
    start = (page - 1) * PHOTOS_PER_PAGE

    # Group the page by trip. 60 photos routinely span several trips, and a
    # sticky header naming the trip answers "what am I looking at?" while
    # scrolling much better than repeating the trip under every tile.
    groups = []
    for it in items[start:start + PHOTOS_PER_PAGE]:
        if not groups or groups[-1]["trip_id"] != it["trip_id"]:
            groups.append({"trip_id": it["trip_id"], "trip_name": it["trip_name"],
                           "trip_date": it["trip_date"], "photos": []})
        groups[-1]["photos"].append(it)

    def photos_href(**over):
        """This page's URL with some controls changed. Anything not overridden
        carries through, so changing one filter never silently clears another;
        pass '' to drop one. `page` is absent from the defaults on purpose —
        changing a filter has to land you back on page 1, since the old page
        number usually doesn't exist in the new result set."""
        args = {"q": q, "year": year,
                "favorites": "1" if favorites_only else "",
                "sort": sort if sort != "newest" else ""}
        args.update(over)
        return url_for('trips_photos', **{k: v for k, v in args.items() if v})

    # Numbered links around the current page, first and last always reachable,
    # None where the run of numbers skips (rendered as an ellipsis). With only
    # Newer/Older, reaching 2019 in a 20-page library was a dozen clicks.
    wanted = {1, pages, page} | {page + d for d in (-2, -1, 1, 2)
                                 if 1 <= page + d <= pages}
    page_links, prev_n = [], 0
    for n in sorted(wanted):
        if prev_n and n - prev_n > 1:
            page_links.append(None)
        page_links.append(n)
        prev_n = n

    return render_template('trips_photos.html', title='Photos',
                           groups=groups, page=page, pages=pages, total=total,
                           library_total=library_total, page_links=page_links,
                           photos_href=photos_href, q=q, year=year, years=years,
                           sort=sort, is_admin=is_admin,
                           favorites_only=favorites_only, fav_total=fav_total,
                           filtered=bool(q or year or favorites_only),
                           active_nav='stats')


def _short_trip_date(start):
    """'Jun 2025' for a trip start date, or '' when the trip has no dates."""
    try:
        return date.fromisoformat(start).strftime("%b %Y")
    except (ValueError, TypeError):
        return ""


def _photo_card_meta(trip, card):
    """(place, state) of the campspot/event a pool photo sits under; ('', '')
    if unnamable.

    `card` is the pool's "stay-N" / "event-N" key, which is exactly the index
    into the trip's own lists — the trips-map lightbox derives the same thing
    client-side, this is the server-side twin. The gallery shows `place` on
    the tile and searches both.
    """
    m = re.match(r'^(stay|event)-(\d+)$', card or '')
    if not m or not trip:
        return "", ""
    idx = int(m.group(2))
    if m.group(1) == 'stay':
        stays = trip.get("stays") or []
        if idx >= len(stays):
            return "", ""
        stay = stays[idx]
        return (stay.get("place") or ""), (stay.get("state") or "")
    events = trip.get("events") or []
    if idx >= len(events):
        return "", ""
    e = events[idx]
    # Family visits carry their label separately from the event name.
    return (e.get("name") or e.get("family_visit") or ""), (e.get("state") or "")


_WORD_SPLIT_RE = re.compile(r'[^a-z0-9]+')


def _search_haystack(*parts):
    """Lowercased, punctuation-stripped words joined by single spaces and
    padded with one at each end, so a term matches a WORD PREFIX with a plain
    `' ' + term in hay` — no regex per photo per term.

    Word-prefix rather than raw substring, because short queries are exactly
    where substring search falls apart: typing "acad" should find Acadia, but
    the two-letter state code "ME" matching the middle of "Home" is noise. The
    cost is that "sylvania" no longer finds Pennsylvania, which is how search
    boxes generally behave anyway.
    """
    words = _WORD_SPLIT_RE.split(' '.join(parts).lower())
    return ' ' + ' '.join(w for w in words if w) + ' '


def _search_terms(q):
    """Query split the same way `_search_haystack` splits its input, so a term
    typed with punctuation ("lake," / "PA.") still matches."""
    return [t for t in _WORD_SPLIT_RE.split((q or '').lower()) if t]


def _timeline_positions(trip):
    """{card id: position} from a trip's own `timeline`, which is the app's
    single definition of what order things happened in.

    The gallery orders a trip's photos by this rather than by campspots-then-
    events: a real trip interleaves them heavily (trip 92 is 6 campspots and
    33 events over 8 days), so grouping all the campspots first put day-8
    photos above day-1 ones.

    A campspot split across nights appears in the timeline more than once;
    `setdefault` keeps its FIRST slot, so all of its photos stay together in
    one run instead of being scattered down the page.
    """
    pos = {}
    for n, entry in enumerate(trip.get("timeline") or []):
        pos.setdefault(f'{entry.get("type")}-{entry.get("idx")}', n)
    return pos


def _photo_card_order(card):
    """(kind, index) fallback sort key for a pool card id, used only for a
    card the trip's timeline doesn't mention — photos left behind in a
    directory whose campspot was deleted, say. Campspots before events, each
    by index.

    Parsed rather than compared as a string: "stay-10" sorts before "stay-2"
    lexicographically, which scrambled any trip with ten or more campspots.
    """
    m = re.match(r'^(stay|event)-(\d+)$', card or '')
    if not m:
        return (2, 0)
    return (0 if m.group(1) == 'stay' else 1, int(m.group(2)))


@app.route('/trips/poster')
def trips_poster():
    """Standalone portrait "poster" view of all trips.

    The sheet size is client-side: a `?size=` query param (letter default,
    plus 11×17 / 18×24 / 24×36 poster sizes) that the template resolves —
    this route serves the same data regardless.

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

    # Photo pool — every uploaded image across all trips, shuffled, from
    # the shared cache (the poster just renders many more of them as a
    # densely-tiled border). Copy via the comprehension before shuffling.
    import random
    all_photos = [p for p in _collect_photo_pool()
                  if is_admin or not p["home_only"]]
    random.shuffle(all_photos)

    # Stats footer line. Always excludes home_only trips (even for admins) so
    # the printed numbers match the public site header, and uses
    # camping_nights() like every other nights aggregate. States = anywhere a
    # campspot or a real (non-waypoint) event happened.
    stat_trips = [t for t in trips if not t.get("home_only")]
    states = set()
    for t in stat_trips:
        for s in t["stays"]:
            if s.get("state"):
                states.add(s["state"])
        for e in t.get("events", []):
            if e.get("state") and not e.get("waypoint"):
                states.add(e["state"])
    years = sorted(t["start"][:4] for t in stat_trips if t.get("start"))
    poster_stats = {
        "trips": sum(1 for t in stat_trips
                     if t["stays"] or is_day_trip(t)),
        "nights": sum(camping_nights(t) for t in stat_trips),
        "states": len(states),
        "year_start": years[0] if years else "",
        "year_end": years[-1] if years else "",
    }

    return render_template('trips_poster.html', trips=trips, home=home,
                           family_locations=family,
                           poster_photos=all_photos,
                           poster_stats=poster_stats)


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
    # STATE_NAMES lets the client fold each stay/event's stored 2-letter code
    # into the search haystack alongside its full name, so "Pennsylvania"
    # matches "PA" — the same fix the campground map's search got, and what
    # makes the Stats page's state chips linkable.
    return render_template('trips_calendar.html', trips=trips,
                           initial_view=initial_view, active_nav=initial_view,
                           state_names=STATE_NAMES)


# Everything on the Stats page except the photo count derives from three files,
# so it only has to be recomputed when one of them changes. Before this, every
# visit re-walked all ~13k campgrounds and re-derived every aggregate.
_stats_cache = {"key": None, "data": None}


@app.route('/trips/stats')
def trips_stats():
    """All-time aggregates across every trip. Hero numbers (trips,
    nights, states, photos), most-visited campgrounds, trips-by-year
    bars, and the state list.

    Cached on the mtimes of its three inputs. The photo count is deliberately
    NOT part of that cache: photos are files on disk, and uploading one changes
    no JSON, so a cached count would go stale. It comes from
    `_collect_photo_pool()` instead, which walks the same directories, has its
    own short TTL, and is invalidated explicitly by the upload/delete/move
    paths — so a fresh upload shows up on the next render.
    """
    key = (_file_mtime_ns(TRIPS_JSON), _file_mtime_ns(CAMPGROUNDS_JSON),
           _file_mtime_ns(HOME_FILE))
    if _stats_cache["key"] == key:
        return render_template('trips_stats.html',
                               photo_count=_stats_photo_count(),
                               **_stats_cache["data"])

    trips = parse_trips()
    # Stats aggregate the camping/travel record; home-only trips aren't
    # part of that for any viewer.
    trips = [t for t in trips if not t.get("home_only")]

    total_trips = len(trips)
    total_overnight = sum(1 for t in trips if t.get("stays"))
    total_day_trips = sum(1 for t in trips if is_day_trip(t))
    # camping_nights(), not total_nights: a mixed trip (home for a few nights
    # mid-trip, then back out) would otherwise count those home nights as
    # camping. All-time and per-year use the same rule so they can't disagree.
    total_nights = sum(camping_nights(t) for t in trips)

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

    # Trips- and nights-per-year. Empty-dated trips are excluded (no year to
    # assign). Home-only trips are already gone (filtered above), and
    # camping_nights() drops home stays inside any mixed trip, so neither
    # series counts a night at the house.
    #
    # A multi-night trip spanning New Year lands entirely in its START year —
    # same convention the trip list and calendar year-grouping use, so the bars
    # line up with what those pages show.
    trips_by_year = {}
    nights_by_year = {}
    for t in trips:
        if not t.get("start"):
            continue
        y = int(t["start"][:4])
        trips_by_year[y] = trips_by_year.get(y, 0) + 1
        nights_by_year[y] = nights_by_year.get(y, 0) + camping_nights(t)
    trips_by_year_sorted = sorted(trips_by_year.items())
    # Same year span as the trips chart (a year with trips but zero camping
    # nights still gets a row, rather than silently vanishing from one chart).
    nights_by_year_sorted = [(y, nights_by_year.get(y, 0))
                             for y, _ in trips_by_year_sorted]

    # ── Records ──────────────────────────────────────────────────────
    # All derivable from data already in hand (trips + campgrounds.json
    # coords/elevation) — no GPS-track crunching.
    dated = [t for t in trips if t.get("start")]
    first_trip = min(dated, key=lambda t: t["start"]) if dated else None
    camping_since = ""
    if first_trip:
        d = datetime.strptime(first_trip["start"], "%Y-%m-%d")
        camping_since = d.strftime("%B %Y")

    overnighters = [t for t in trips if t.get("total_nights", 0) > 0]
    longest_trip = max(overnighters, key=lambda t: t["total_nights"]) if overnighters else None
    avg_nights = round(total_nights / total_overnight, 1) if total_overnight else 0

    month_counts = {}
    for t in dated:
        month_counts[int(t["start"][5:7])] = month_counts.get(int(t["start"][5:7]), 0) + 1
    busiest_month = None
    if month_counts:
        m, n = max(month_counts.items(), key=lambda kv: (kv[1], -kv[0]))
        busiest_month = {"name": datetime(2000, m, 1).strftime("%B"), "count": n}

    # Furthest / highest campground actually stayed at, by campground_id.
    home_cfg = _load_json(HOME_FILE)
    home_lat, home_lng = home_cfg.get("home_lat"), home_cfg.get("home_long")
    visited_ids = {s["campground_id"] for t in trips for s in t.get("stays", [])
                   if s.get("campground_id") is not None}
    furthest = None
    highest = None
    if visited_ids:
        cg_entries = {c["id"]: c for c in _read_campgrounds_raw() if "id" in c}
        for cid in visited_ids:
            c = cg_entries.get(cid)
            if not c or "location" not in c:
                continue
            lat, lng = (float(x) for x in c["location"].split(","))
            if home_lat is not None and home_lng is not None:
                miles = _haversine_m(home_lat, home_lng, lat, lng) / 1609.344
                if furthest is None or miles > furthest["miles"]:
                    furthest = {"name": c["name"], "miles": round(miles)}
            elev_ft = round(c.get("elevation_meters", 0) * METERS_TO_FEET)
            if elev_ft and (highest is None or elev_ft > highest["feet"]):
                highest = {"name": c["name"], "feet": elev_ft}

    data = dict(
        total_trips=total_trips,
        total_overnight=total_overnight,
        total_day_trips=total_day_trips,
        total_nights=total_nights,
        states_count=len(states),
        states_list=sorted(states),
        state_names=STATE_NAMES,
        top_campgrounds=top_campgrounds,
        trips_by_year=trips_by_year_sorted,
        nights_by_year=nights_by_year_sorted,
        unique_campgrounds=len(cg_trip_ids),
        camping_since=camping_since,
        longest_trip=longest_trip,
        avg_nights=avg_nights,
        busiest_month=busiest_month,
        furthest=furthest,
        highest=highest,
        active_nav='stats',
    )
    _stats_cache.update(key=key, data=data)
    return render_template('trips_stats.html',
                           photo_count=_stats_photo_count(), **data)


def _stats_photo_count():
    """Photos counted for the Stats hero, from the cached pool.

    Home-only trips are excluded from every other stat on the page, so their
    photos are excluded here too (there are none today, but the rule should
    hold if a mixed trip ever appears)."""
    return sum(1 for p in _collect_photo_pool() if not p["home_only"])


@app.route('/trips/<int:trip_id>')
def trip_detail(trip_id):
    trips = parse_trips()
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        # abort(), not a bare text response: a stale link (a deleted trip, a
        # share guest following an old text message) is the most likely 404 in
        # the app, and it should land on the styled error page with a way back
        # rather than unstyled text with no header.
        abort(404)

    enrich_trip_locations(trip)

    captions = _load_json(CAPTIONS_FILE)

    photo_order = _load_json(PHOTO_ORDER_FILE)

    # Per-photo uploader record so the template can show editable captions on
    # an uploader-role user's own contributions while leaving others read-only.
    photo_uploaders = _load_json(PHOTO_UPLOADERS_FILE)

    # Poster-hero marks, so the lightbox's star opens in the right state.
    favorites = _load_json(PHOTO_FAVORITES_FILE)

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
                    "url": f"/photo/{trip_id}/{i}/{fname}",
                    "thumb_url": f"/thumb/{trip_id}/{i}/{fname}",
                    "view_url": f"/view/{trip_id}/{i}/{fname}",
                    "caption": captions.get(photo_key, ""),
                    "date_taken": _photo_date_taken(os.path.join(photo_dir, fname)),
                    "uploader": photo_uploaders.get(photo_key, ""),
                    "key": photo_key,
                    "favorite": bool(favorites.get(photo_key)),
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
                    "url": f"/photo/{trip_id}/events/{i}/{fname}",
                    "thumb_url": f"/thumb/{trip_id}/events/{i}/{fname}",
                    "view_url": f"/view/{trip_id}/events/{i}/{fname}",
                    "caption": captions.get(photo_key, ""),
                    "date_taken": _photo_date_taken(os.path.join(photo_dir, fname)),
                    "uploader": photo_uploaders.get(photo_key, ""),
                    "key": photo_key,
                    "favorite": bool(favorites.get(photo_key)),
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

    # Find prev/next trips (non-admins skip home-only trips in navigation).
    # Summaries ride along so the chevrons' tooltips can say where they go.
    nav_trips = trips if is_admin else [t for t in trips if not t.get("home_only") or t["id"] == trip_id]
    nav_ids = [t["id"] for t in nav_trips]
    nav_idx = nav_ids.index(trip_id)
    prev_trip = nav_trips[nav_idx - 1] if nav_idx > 0 else None
    next_trip = nav_trips[nav_idx + 1] if nav_idx < len(nav_ids) - 1 else None
    prev_trip_id = prev_trip["id"] if prev_trip else None
    next_trip_id = next_trip["id"] if next_trip else None
    prev_trip_summary = prev_trip["summary"] if prev_trip else ""
    next_trip_summary = next_trip["summary"] if next_trip else ""

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
        prev_trip_summary=prev_trip_summary,
        next_trip_summary=next_trip_summary,
    )


def _render_photo_tile(subpath, filename, p_type, p_idx, trip_id):
    """Render the shared `_photo_item.html` partial for a just-uploaded file so
    the client can splice the tile into the grid in place. Uploads used to end
    with a full page reload to surface new photos, which tore down and redrew
    the whole Leaflet map (tiles, markers, polyline) — a visible, pointless
    flash. Returning the server-rendered tile lets the upload finish without a
    reload. Mirrors the per-photo dict the trip-detail view builds, so the tile
    is byte-identical to one a reload would produce (`p_alt` is left blank — the
    only field the endpoint can't cheaply derive; it's just the img alt-text
    fallback and self-corrects on the next natural reload)."""
    photo_dir = os.path.join(UPLOAD_DIR, *subpath.split('/'))
    is_admin = current_user.is_authenticated and current_user.is_admin
    is_uploader = (current_user.is_authenticated
                   and getattr(current_user, "can_upload", False)
                   and not is_admin)
    username = current_user.username if current_user.is_authenticated else ""
    photo = {
        "filename": filename,
        "url": f"/photo/{subpath}/{filename}",
        "thumb_url": f"/thumb/{subpath}/{filename}",
        "view_url": f"/view/{subpath}/{filename}",
        "caption": "",
        "date_taken": _photo_date_taken(os.path.join(photo_dir, filename)),
        "uploader": username,
        "key": f"{subpath}/{filename}",
        "favorite": False,   # nothing is a favorite the instant it lands
    }
    return render_template("_photo_item.html", photo=photo, trip_id=trip_id,
                           p_idx=p_idx, p_type=p_type, p_alt="",
                           is_admin=is_admin, is_uploader=is_uploader,
                           current_username=username)


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
    url_prefix = f"/photo/{trip_id}/{stay_idx}"
    subpath = f"{trip_id}/{stay_idx}"

    # Zip upload — extract all images
    if file.filename.lower().endswith('.zip'):
        saved = _extract_zip_photos(file, photo_dir)
        if not saved:
            return jsonify({"error": "No image files found in zip"}), 400
        _record_uploaders([f"{trip_id}/{stay_idx}/{f}" for f in saved],
                          current_user.username)
        return jsonify({
            "files": [{"filename": f, "url": f"{url_prefix}/{f}",
                       "html": _render_photo_tile(subpath, f, 'stay', stay_idx, trip_id)}
                      for f in saved],
        })

    # Single image upload
    filename = _save_photo(file, photo_dir)
    if not filename:
        return jsonify({"error": "File type not allowed"}), 400

    _record_uploader(f"{trip_id}/{stay_idx}/{filename}", current_user.username)
    return jsonify({
        "filename": filename,
        "url": f"{url_prefix}/{filename}",
        "html": _render_photo_tile(subpath, filename, 'stay', stay_idx, trip_id),
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
    # The slideshow pool carries captions, so an edit must not wait out the TTL.
    _invalidate_photo_pool()

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/photos/<filename>', methods=['DELETE'])
def delete_photo(trip_id, stay_idx, filename):
    denied = _require_admin()
    if denied:
        return denied
    filename = secure_filename(filename)
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx))
    photo_path = os.path.join(photo_dir, filename)
    if os.path.exists(photo_path):
        _trash_photo(photo_path)
    _remove_thumb(photo_path)
    _invalidate_photo_pool()
    # Caption/order/uploader metadata is kept so Undo restores the photo
    # intact; _purge_old_trash scrubs it when the trash entry ages out.
    _purge_old_trash(photo_dir, f"{trip_id}/{stay_idx}/", f"{trip_id}/{stay_idx}")
    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/photos/<filename>/restore', methods=['POST'])
def restore_photo(trip_id, stay_idx, filename):
    denied = _require_admin()
    if denied:
        return denied
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx))
    err = _restore_from_trash(photo_dir, secure_filename(filename))
    return err if err else jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/stays/<int:stay_idx>/photos', methods=['DELETE'])
def delete_all_stay_photos(trip_id, stay_idx):
    denied = _require_admin()
    if denied:
        return denied
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), str(stay_idx))
    if os.path.isdir(photo_dir):
        shutil.rmtree(photo_dir)
    _invalidate_photo_pool()

    prefix = f"{trip_id}/{stay_idx}/"
    captions = _load_json(CAPTIONS_FILE)
    captions = {k: v for k, v in captions.items() if not k.startswith(prefix)}
    _save_json(CAPTIONS_FILE, captions)

    order_key = f"{trip_id}/{stay_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    photo_order.pop(order_key, None)
    _save_json(PHOTO_ORDER_FILE, photo_order)

    _remove_uploaders_by_prefix(prefix)
    _remove_favorites_by_prefix(prefix)

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
    url_prefix = f"/photo/{trip_id}/events/{event_idx}"
    subpath = f"{trip_id}/events/{event_idx}"

    # Zip upload — extract all images
    if file.filename.lower().endswith('.zip'):
        saved = _extract_zip_photos(file, photo_dir)
        if not saved:
            return jsonify({"error": "No image files found in zip"}), 400
        _record_uploaders([f"{trip_id}/events/{event_idx}/{f}" for f in saved],
                          current_user.username)
        return jsonify({
            "files": [{"filename": f, "url": f"{url_prefix}/{f}",
                       "html": _render_photo_tile(subpath, f, 'event', event_idx, trip_id)}
                      for f in saved],
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
        "html": _render_photo_tile(subpath, filename, 'event', event_idx, trip_id),
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
    # The slideshow pool carries captions, so an edit must not wait out the TTL.
    _invalidate_photo_pool()

    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/photos/<filename>', methods=['DELETE'])
def delete_event_photo(trip_id, event_idx, filename):
    denied = _require_admin()
    if denied:
        return denied
    filename = secure_filename(filename)
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(event_idx))
    photo_path = os.path.join(photo_dir, filename)
    if os.path.exists(photo_path):
        _trash_photo(photo_path)
    _remove_thumb(photo_path)
    _invalidate_photo_pool()
    # Metadata kept for Undo; scrubbed at purge time (see delete_photo).
    _purge_old_trash(photo_dir, f"{trip_id}/events/{event_idx}/", f"{trip_id}/events/{event_idx}")
    return jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/photos/<filename>/restore', methods=['POST'])
def restore_event_photo(trip_id, event_idx, filename):
    denied = _require_admin()
    if denied:
        return denied
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(event_idx))
    err = _restore_from_trash(photo_dir, secure_filename(filename))
    return err if err else jsonify({"ok": True})


@app.route('/trips/<int:trip_id>/events/<int:event_idx>/photos', methods=['DELETE'])
def delete_all_event_photos(trip_id, event_idx):
    denied = _require_admin()
    if denied:
        return denied
    photo_dir = os.path.join(UPLOAD_DIR, str(trip_id), "events", str(event_idx))
    if os.path.isdir(photo_dir):
        shutil.rmtree(photo_dir)
    _invalidate_photo_pool()

    prefix = f"{trip_id}/events/{event_idx}/"
    captions = _load_json(CAPTIONS_FILE)
    captions = {k: v for k, v in captions.items() if not k.startswith(prefix)}
    _save_json(CAPTIONS_FILE, captions)

    order_key = f"{trip_id}/events/{event_idx}"
    photo_order = _load_json(PHOTO_ORDER_FILE)
    photo_order.pop(order_key, None)
    _save_json(PHOTO_ORDER_FILE, photo_order)

    _remove_uploaders_by_prefix(prefix)
    _remove_favorites_by_prefix(prefix)

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
    _delete_track_cache(trip_id)
    _delete_trip_route(trip_id)
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

# Color modes selectable on the combined campground map. `field` is the key on
# each campground row produced by `_load_campgrounds`; `colors` maps category →
# hex. Order here is the order the modes appear in the "Color by" picker.
COLOR_MODES = [
    {"key": "waterfront", "field": "waterfront",
     "label": "Proximity to Water", "colors": WATERFRONT_COLORS},
    {"key": "climate", "field": "climate",
     "label": "Climate", "colors": CLIMATE_COLORS},
]

# Full names for the 2-letter codes stored in each entry's `state`, so the map's
# search box matches "Colorado" as well as "CO" — typing the full name returned
# nothing at all, which is the natural thing to type. US states plus the
# Canadian provinces the database covers; anything unlisted just isn't expanded.
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia",
    "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba",
    "NB": "New Brunswick", "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia", "NT": "Northwest Territories", "NU": "Nunavut",
    "ON": "Ontario", "PE": "Prince Edward Island", "QC": "Quebec",
    "SK": "Saskatchewan", "YT": "Yukon",
}

# Display labels + presentation order for the ownership filter. Values not
# listed (or blank) fall back to a title-cased label and sort to the end.
OWNERSHIP_LABELS = {
    "state": "State",
    "federal": "Federal",
    "local": "Local",
    "private": "Private",
    "hipcamp": "HipCamp",
}


# Everything that can change the rendered map page. The data files are the
# obvious inputs; the templates and this module are in there so a DEPLOY
# invalidates every client's copy — serving a stale page after a code change is
# exactly the bug `_revalidate_html` exists to prevent, and an ETag that ignored
# code would reintroduce it.
_MAP_ETAG_INPUTS = (
    CAMPGROUNDS_JSON, HOME_FILE, TRIPS_JSON, ROADSIDE_JSON,
    os.path.join(os.path.dirname(__file__), "templates", "campground_map.html"),
    os.path.join(os.path.dirname(__file__), "templates", "base.html"),
    os.path.abspath(__file__),
)


def _map_etag(*extra):
    """ETag for the campground map: input mtimes + whatever varies the render.

    The page is ~1.9 MB even gzipped and changes only when the campground data
    or the code does, but it carries no validator — so a back/forward within
    seconds re-downloads the whole thing. With this, the same `no-cache`
    revalidation `_revalidate_html` forces turns into a 304.
    """
    parts = [str(_file_mtime_ns(p)) for p in _MAP_ETAG_INPUTS]
    parts.extend(str(x) for x in extra)
    return '"' + hashlib.sha256("|".join(parts).encode()).hexdigest()[:32] + '"'


@app.route('/campgrounds/map')
def campgrounds_map():
    denied = _require_campground_view_page()
    if denied:
        return denied
    home, family = _map_config()
    is_admin = current_user.is_authenticated and current_user.is_admin
    mode = request.args.get('color')
    if mode not in {m["key"] for m in COLOR_MODES}:
        mode = COLOR_MODES[0]["key"]

    # `mode` and `is_admin` both change the rendered output, so both vary the tag.
    etag = _map_etag(mode, is_admin)
    if request.if_none_match.contains(etag.strip('"')):
        return Response(status=304, headers={"ETag": etag})

    resp = app.make_response(render_template(
        'campground_map.html',
        title='Map',
        campgrounds=_map_marker_rows(_load_campgrounds()),
        roadside=_load_roadside(),
        color_modes=COLOR_MODES,
        default_mode=mode,
        ownership_labels=OWNERSHIP_LABELS,
        state_names=STATE_NAMES,
        home=home,
        family_locations=family,
        active_nav='campmap',
        is_admin=is_admin,
    ))
    resp.headers["ETag"] = etag
    return resp


@app.route('/api/campgrounds/<int:cg_id>/popup')
def api_campground_popup(cg_id):
    """Popup-only detail for one campground (see `_MAP_POPUP_FIELDS`).

    The map ships ~12.9k slim markers and fetches this when a popup opens, so the
    long-tail text is paid for per-click instead of per-page-load. Served off the
    same `_load_campgrounds` cache the page renders from, so it costs a dict
    lookup, and it carries the map's ETag so a revisit revalidates to a 304.
    """
    denied = _require_campground_view_api()
    if denied:
        return denied
    row = next((r for r in _load_campgrounds() if r.get("id") == cg_id), None)
    if row is None:
        return jsonify({"error": "Campground not found"}), 404
    resp = jsonify({k: row[k] for k in _MAP_POPUP_FIELDS if k in row})
    resp.headers["ETag"] = _map_etag("popup", cg_id)
    return resp


# Legacy split-map URLs now redirect to the combined map with the matching mode.
# Both gate first: redirecting a Trips-only user to /campgrounds/map only to have
# that page bounce them again is a pointless double hop.
@app.route('/campgrounds/waterfront')
def campgrounds_waterfront():
    return _require_campground_view_page() or redirect(
        url_for('campgrounds_map', color='waterfront'))


@app.route('/campgrounds/climate')
def campgrounds_climate():
    return _require_campground_view_page() or redirect(
        url_for('campgrounds_map', color='climate'))


# ── Federal campground availability (recreation.gov / RIDB) ───────────────
# Browse real-time availability for any recreation.gov (federal) campground,
# EKKO-friendly sites only. RIDB gives the campsite catalog (for fit); the
# recreation.gov calendar gives live availability. See ridb/fetch_facility.py.

@app.route('/campgrounds/availability')
def campgrounds_availability():
    """Page: search a federal campground + date range, see EKKO-fit openings."""
    denied = _require_campground_view_page()
    if denied:
        return denied
    is_admin = current_user.is_authenticated and current_user.is_admin
    return render_template('campground_availability.html',
                           title='Availability', active_nav='campavail',
                           is_admin=is_admin, default_fit_ft=DEFAULT_FIT_FT)


@app.route('/api/ridb/search')
def api_ridb_search():
    """Search recreation.gov campgrounds by name (for the availability picker)."""
    denied = _require_campground_view_api()
    if denied:
        return denied
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    if not os.environ.get("RIDB_API_KEY"):
        # Viewer-facing copy: "RIDB_API_KEY not configured" named an
        # environment variable the reader has no access to and can't act on. Say
        # what it means for them and who can fix it. The server log still has
        # the specifics.
        return jsonify({"error": "Live availability isn't set up on this server "
                                 "yet — ask Andrew. You can still book directly "
                                 "on recreation.gov."}), 503
    try:
        results = search_facilities(q)
    except Exception:
        return jsonify({"error": "Search failed (RIDB request error)."}), 502
    out = [{"id": f.get("FacilityID"), "name": f.get("FacilityName"),
            "type": f.get("FacilityTypeDescription", "")}
           for f in results
           if f.get("FacilityTypeDescription") == "Campground" and f.get("Reservable", True)]
    return jsonify(out)


@app.route('/api/ridb/availability')
def api_ridb_availability():
    """EKKO-friendly per-night availability for a facility over a date range.

    Query params: facility=<RIDB FacilityID>, start=YYYY-MM-DD, end=YYYY-MM-DD
    (both inclusive — every date is a night), optional fit_ft (default 25).
    """
    denied = _require_campground_view_api()
    if denied:
        return denied
    fid = (request.args.get('facility') or '').strip()
    if not fid.isdigit():
        return jsonify({"error": "Missing or invalid facility id."}), 400
    try:
        start = date.fromisoformat(request.args.get('start', ''))
        end = date.fromisoformat(request.args.get('end', ''))
    except ValueError:
        return jsonify({"error": "start and end must be YYYY-MM-DD dates."}), 400
    if end < start:
        return jsonify({"error": "End date must be on or after the start date."}), 400
    if (end - start).days > 92:
        return jsonify({"error": "Range too large — pick 3 months or less."}), 400
    if not os.environ.get("RIDB_API_KEY"):
        # Viewer-facing copy: "RIDB_API_KEY not configured" named an
        # environment variable the reader has no access to and can't act on. Say
        # what it means for them and who can fix it. The server log still has
        # the specifics.
        return jsonify({"error": "Live availability isn't set up on this server "
                                 "yet — ask Andrew. You can still book directly "
                                 "on recreation.gov."}), 503

    try:
        facility = fetch_facility(fid)
    except Exception:
        return jsonify({"error": "Could not load that facility from RIDB."}), 502
    try:
        # Per-request cache → availability is always live, never stale.
        matrix = availability_matrix(facility, start, end,
                                     fit_ft=request.args.get('fit_ft', type=int) or DEFAULT_FIT_FT,
                                     cache={})
    except Exception:
        return jsonify({"error": "Could not load availability from recreation.gov."}), 502

    # Useful facility context for the page header / booking link.
    lat, lng = facility.get("FacilityLatitude"), facility.get("FacilityLongitude")
    resv = facility.get("FacilityReservationURL") or \
        f"https://www.recreation.gov/camping/campgrounds/{fid}"
    matrix["facility"] = {
        "id": fid, "name": facility.get("FacilityName", ""),
        "lat": lat, "lng": lng, "reservation_url": resv,
        "map_url": facility.get("FacilityMapURL", ""),
    }
    return jsonify(matrix)


# ── Weather Finder ─────────────────────────────────────────────────────────
# Search the 16-day forecast across the campground database for somewhere with
# the weather you want — a comfort band, or cooler/warmer than home is that same
# day, optionally dry. Absorbed from the standalone "Summer Seeker" Flask app
# (summer_seeker_app.py), which shared this repo's campgrounds.json but ran on
# its own port with its own templates. Admin-only: it's a planning tool, and a
# single search spends a real slice of the weather provider's free-tier budget.
# The engine lives in weather_finder.py (shared with the find_summer.py CLI).

# Ceiling on how far out the UI will search. Past this a search can't be covered
# in one pass anyway (see weather_finder.FORECAST_BUDGET) and the result list is
# too long to read.
WEATHER_MAX_MILES = 500


@app.route('/campgrounds/weather')
def campgrounds_weather():
    """Page: find campgrounds whose forecast matches what you're after."""
    denied = _require_admin_page()
    if denied:
        return denied
    home_cfg = _load_json(HOME_FILE)
    return render_template(
        'weather_finder.html', title='Weather', active_nav='campweather',
        is_admin=True,
        home_lat=home_cfg.get("home_lat"), home_lng=home_cfg.get("home_long"),
        max_miles_cap=WEATHER_MAX_MILES,
        forecast_days=weather_finder.FORECAST_DAYS)


@app.route('/api/weather-finder/search', methods=['POST'])
def api_weather_finder_search():
    """Run a forecast search. Body mirrors the form; see weather_finder."""
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}

    mode = data.get("mode", weather_finder.MODE_RANGE)
    if mode not in weather_finder.MODES:
        return jsonify({"error": "Unknown search mode."}), 400
    sort = data.get("sort", "distance")
    if sort not in weather_finder.SORTS:
        return jsonify({"error": "Unknown sort order."}), 400

    def num(key, default, lo, hi):
        try:
            return min(hi, max(lo, float(data.get(key, default))))
        except (TypeError, ValueError):
            return default

    max_miles = num("max_miles", 250, 5, WEATHER_MAX_MILES)
    min_high = num("min_high", 70, -50, 130)
    max_high = num("max_high", 88, -50, 130)
    if min_high > max_high:
        min_high, max_high = max_high, min_high
    delta_f = num("delta_f", 5, 0, 60)

    # Origin: home unless the form supplied somewhere else to search from.
    home_cfg = _load_json(HOME_FILE)
    origin_lat, origin_lng = data.get("lat"), data.get("lng")
    if origin_lat is None or origin_lng is None:
        origin_lat, origin_lng = home_cfg.get("home_lat"), home_cfg.get("home_long")
    if origin_lat is None or origin_lng is None:
        return jsonify({"error": "No search origin — home.json has no coordinates "
                                 "and no place was picked."}), 400

    # `max_precip_in` of 0 is meaningful ("bone dry"), so the filter is switched
    # on by a separate flag rather than by the number being falsy.
    max_precip_in = num("max_precip_in", 0.1, 0, 10) if data.get("dry_only") else None
    max_precip_chance = (num("max_precip_chance", 30, 0, 100)
                         if data.get("dry_only") and data.get("use_precip_chance") else None)

    try:
        result = weather_finder.find_matching_days(
            _load_campgrounds(), (float(origin_lat), float(origin_lng)),
            mode=mode, min_high=min_high, max_high=max_high, delta_f=delta_f,
            max_miles=max_miles, weekends_only=bool(data.get("weekends_only", True)),
            max_precip_in=max_precip_in, max_precip_chance=max_precip_chance,
            waterfront_only=bool(data.get("waterfront_only")),
            sort=sort,
            user_agent=_OUTBOUND_UA)
    except weather_finder.RateLimited as e:
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        app.logger.exception("weather finder search failed")
        return jsonify({"error": f"Search failed: {e}"}), 502

    result["mode"] = mode
    result["origin"] = {"lat": float(origin_lat), "lng": float(origin_lng)}
    return jsonify(result)


@app.route('/api/weather-finder/lookup')
def api_weather_finder_lookup():
    """Campground name search for the by-name forecast lookup.

    Matched server-side rather than by shipping the name list to the browser:
    /api/campgrounds is ~12.9k rows, which is a lot to download to type into.
    """
    denied = _require_admin()
    if denied:
        return denied
    q = (request.args.get('q') or '').strip().lower()
    if len(q) < 2:
        return jsonify([])
    hits = [r for r in _load_campgrounds() if q in (r.get("name") or "").lower()]
    # Names that START with the query first — typing "lake" should offer
    # "Lakeview Campground" before "Beaver Lake Campground".
    hits.sort(key=lambda r: (not (r.get("name") or "").lower().startswith(q),
                             r.get("name") or ""))
    return jsonify([{"id": r.get("id"), "name": r.get("name"),
                     "state": r.get("state")} for r in hits[:20]])


@app.route('/api/weather-finder/forecast')
def api_weather_finder_forecast():
    """Full forecast for one campground by id — no distance limit, no filters."""
    denied = _require_admin()
    if denied:
        return denied
    cg_id = request.args.get('id', type=int)
    row = next((r for r in _load_campgrounds() if r.get("id") == cg_id), None)
    if row is None:
        return jsonify({"error": "No such campground."}), 404
    try:
        lat, lng = (float(x) for x in row["location"].split(","))
    except (KeyError, ValueError, AttributeError):
        return jsonify({"error": "That campground has no usable coordinates."}), 400

    home_cfg = _load_json(HOME_FILE)
    home_lat, home_lng = home_cfg.get("home_lat"), home_cfg.get("home_long")
    home = (home_lat, home_lng) if home_lat is not None and home_lng is not None else None

    try:
        days = weather_finder.forecast_for_point(lat, lng, home, user_agent=_OUTBOUND_UA)
    except weather_finder.RateLimited as e:
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        app.logger.exception("weather finder lookup failed")
        return jsonify({"error": f"Forecast lookup failed: {e}"}), 502
    if days is None:
        return jsonify({"error": "The weather service returned nothing for that "
                                 "location."}), 502

    return jsonify({
        "campground": {
            "id": row.get("id"), "name": row.get("name"), "state": row.get("state"),
            "waterfront": row.get("waterfront") or "not waterfront",
            "ownership": row.get("ownership"),
            "elevation_feet": row.get("elevation_feet"),
            "visit_count": row.get("visit_count", 0),
            "lat": lat, "lng": lng,
            "dist": (None if home is None
                     else round(weather_finder.haversine_miles(home[0], home[1], lat, lng), 1)),
        },
        "days": days,
    })


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
    _remove_thumb(src_path)  # dest thumb regenerates lazily on next view
    _invalidate_photo_pool()

    # Update captions
    captions = _load_json(CAPTIONS_FILE)
    old_cap_key = caption_key(src_type, src_idx, filename)
    new_cap_key = caption_key(dst_type, dst_idx, dst_filename)
    cap = captions.pop(old_cap_key, None)
    if cap:
        captions[new_cap_key] = cap
    _save_json(CAPTIONS_FILE, captions)

    # Update uploader + favorite records (same key shape as captions).
    _rename_uploader_key(old_cap_key, new_cap_key)
    _rename_favorite_key(old_cap_key, new_cap_key)

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


# ── Photo favorites API ────────────────────────────────────────────────────

@app.route('/api/photos/favorite', methods=['POST'])
def api_photo_favorite():
    """Star/unstar one photo as a poster hero. Body: {photo, favorite}.

    `photo` is the "{trip_id}/{idx}/{filename}" (or "…/events/…") subpath the
    photo URLs already carry, so a client derives it by stripping the
    /photo/ | /thumb/ | /view/ prefix off any src it has — no page needs to
    know whether it's looking at a stay or an event, and one endpoint serves
    every surface that shows photos.
    """
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    key = (data.get("photo") or "").strip().lstrip('/')
    # Resolve through the same three gates the /photo/ route uses: traversal,
    # no dot-prefixed component (keeps .trash/ unreachable), real extension.
    # Requiring the file to exist matters because the key indexes a metadata
    # file — a bad one would otherwise sit there forever and the poster would
    # try to deal a missing photo into a hero cell.
    if not key or not _resolve_photo_request(key):
        return jsonify({"error": "Photo not found"}), 404
    on = _set_favorite(key, bool(data.get("favorite")))
    return jsonify({"ok": True, "favorite": on})


# ── Campground CRUD API ────────────────────────────────────────────────────

# ── User management API (admin-only) ────────────────────────────────────────

@app.route('/admin/users')
def users_manage():
    denied = _require_admin_page()
    if denied:
        return denied
    return render_template('users_manage.html', active_nav='users')


# ── Access log (admin-only) ────────────────────────────────────────────────

@app.route('/admin/access-log')
def access_log_page():
    denied = _require_admin_page()
    if denied:
        return denied
    return render_template('access_log.html', active_nav='accesslog',
                           retention_days=ACCESS_LOG_RETENTION_DAYS)


@app.route('/api/access-log')
def api_access_log():
    """Recent entries plus a per-visitor summary. Pruning runs here rather than
    on every request: it rewrites the file, so it belongs on a rare admin read,
    not in the hot path."""
    denied = _require_admin()
    if denied:
        return denied
    _prune_access_log()
    try:
        limit = min(int(request.args.get('limit', 500)), 5000)
    except ValueError:
        limit = 500
    entries = _read_access_log()

    summary = {}
    for e in entries:                      # newest-first, so first seen == last visit
        key = e.get("who") or "(not logged in)"
        s = summary.setdefault(key, {
            "who": key, "kind": e.get("kind", "anon"), "views": 0,
            "last": e.get("ts"), "first": e.get("ts"), "ips": [],
        })
        if e.get("event") == "page":
            s["views"] += 1
        s["first"] = e.get("ts")           # overwritten until the oldest wins
        ip = e.get("ip")
        if ip and ip not in s["ips"]:
            s["ips"].append(ip)
    return jsonify({
        "entries": entries[:limit],
        "summary": sorted(summary.values(), key=lambda s: s["last"] or "", reverse=True),
        "total": len(entries),
        "retention_days": ACCESS_LOG_RETENTION_DAYS,
    })


@app.route('/api/users')
def api_user_list():
    denied = _require_admin()
    if denied:
        return denied
    data = _load_json(USERS_FILE)
    return jsonify([
        {"username": name,
         "is_admin": info.get("is_admin", False),
         "can_upload": info.get("can_upload", False),
         "can_view_campgrounds": info.get("can_view_campgrounds", True)}
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
    # Default new users to campground access unless the caller opts them out.
    can_view_campgrounds = bool(body.get('can_view_campgrounds', True))
    if not username:
        return jsonify({"error": "Username required"}), 400
    if username.startswith(SHARE_ID_PREFIX):
        return jsonify({"error": "Username cannot start with 'share:'"}), 400
    if not password:
        return jsonify({"error": "Password required"}), 400
    data = _load_json(USERS_FILE)
    if username in data:
        return jsonify({"error": "User already exists"}), 400
    data[username] = {
        "password_hash": generate_password_hash(password),
        "is_admin": is_admin,
        "can_upload": can_upload,
        "can_view_campgrounds": can_view_campgrounds,
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
    if 'can_view_campgrounds' in body:
        data[username]['can_view_campgrounds'] = bool(body.get('can_view_campgrounds'))
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


# ── Read-only share links (admin-managed magic links) ─────────────────────────

@app.route('/api/share-links')
def api_share_link_list():
    denied = _require_admin()
    if denied:
        return denied
    links = _load_json(SHARE_TOKENS_FILE)
    out = [{"token": t, "label": i.get("label", ""),
            "next": i.get("next", "/"), "created": i.get("created", ""),
            "trips_only": i.get("trips_only", False)}
           for t, i in links.items()]
    out.sort(key=lambda x: x["created"], reverse=True)
    return jsonify(out)


@app.route('/api/share-links', methods=['POST'])
def api_share_link_create():
    denied = _require_admin()
    if denied:
        return denied
    body = request.get_json() or {}
    label = (body.get('label') or '').strip()
    nxt = _safe_next(body.get('next'), default="/")
    trips_only = bool(body.get('trips_only'))
    token = secrets.token_urlsafe(24)
    links = _load_json(SHARE_TOKENS_FILE)
    links[token] = {"label": label, "next": nxt, "trips_only": trips_only,
                    "created": datetime.now().isoformat(timespec='seconds')}
    _save_json(SHARE_TOKENS_FILE, links)
    return jsonify({"ok": True, "token": token, "label": label, "next": nxt,
                    "trips_only": trips_only})


@app.route('/api/share-links/<token>', methods=['PUT'])
def api_share_link_update(token):
    """Update a share link in place. Currently only the `trips_only` flag is
    editable; load_user re-reads this file each request, so the change takes
    effect on the token's next request (no revoke/recreate needed)."""
    denied = _require_admin()
    if denied:
        return denied
    links = _load_json(SHARE_TOKENS_FILE)
    if token not in links:
        return jsonify({"error": "Share link not found"}), 404
    body = request.get_json() or {}
    if 'trips_only' in body:
        links[token]['trips_only'] = bool(body.get('trips_only'))
    _save_json(SHARE_TOKENS_FILE, links)
    return jsonify({"ok": True, "trips_only": links[token].get("trips_only", False)})


@app.route('/api/share-links/<token>', methods=['DELETE'])
def api_share_link_delete(token):
    """Revoke a share link by removing its token; load_user re-reads this file
    each request, so any live session on the link dies immediately."""
    denied = _require_admin()
    if denied:
        return denied
    links = _load_json(SHARE_TOKENS_FILE)
    if token in links:
        del links[token]
        _save_json(SHARE_TOKENS_FILE, links)
    return jsonify({"ok": True})


@app.route('/api/campgrounds')
def api_campground_list():
    """Return a lightweight list of campground/family entries for pickers."""
    denied = _require_campground_view_api()
    if denied:
        return denied
    entries = _read_campgrounds_raw()
    result = [{"id": e["id"], "name": e["name"],
               "state": e.get("state", ""),
               "kind": e.get("kind", "campground"),
               "location": e.get("location", "")}
              for e in entries if "id" in e and "name" in e]
    result.sort(key=lambda x: x["name"])
    return jsonify(result)


@app.route('/campgrounds/manage')
def campgrounds_manage():
    denied = _require_admin_page()
    if denied:
        return denied
    is_admin = current_user.is_authenticated and current_user.is_admin
    config = _load_json(HOME_FILE)
    home = [config.get("home_lat"), config.get("home_long")]
    return render_template('campground_manage.html', active_nav='manage',
                           is_admin=is_admin, home=home)


@app.route('/api/campgrounds/all')
def api_campground_all():
    """Return full campground data for the management page.

    This is a ~10 MB payload (12,900+ entries), so two size reductions:
    - Drop the audit-trail fields (`waterfront_evidence`, `inclusion_evidence`).
      The manage page never reads them — they're the audit record, written by
      the audit scripts / by hand — and PUT merges from a field whitelist, so
      they survive a save server-side and the client never needs them. Together
      they're ~40% of the payload.
    - gzip the body when the client accepts it (~5x smaller over the wire).
      Browsers decompress transparently, so no client change is needed; a
      proxy that already gzips will pass our Content-Encoding through.
    """
    denied = _require_admin()
    if denied:
        return denied
    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)
    for e in entries:
        for field in _AUDIT_EVIDENCE_FIELDS:
            e.pop(field, None)
    # The gzip itself is handled by the _compress_response after_request hook,
    # which covers every large text response rather than just this one.
    return app.response_class(json.dumps(entries).encode("utf-8"),
                              mimetype="application/json")


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

    # No global name-uniqueness check. Campground names repeat constantly across
    # states — "Lakeview Campground" appears 7 times, "South Fork Campground" 6 —
    # and the file already holds 286 duplicated names across 668 entries, so the
    # constraint was unenforceable on its own data and only blocked legitimate
    # adds. References are by `id`, so duplicate names cost nothing.
    kind = data.get("kind", "campground")
    next_id = max((e["id"] for e in entries if "id" in e), default=0) + 1
    entry = {
        "id": next_id,
        "kind": kind,
        "name": name,
        "location": data.get("location", ""),
        "state": data.get("state", ""),
        # `note` is common to both kinds: the manage form offers it for family
        # entries too, and PUT has always accepted it for them. Keeping it in
        # the campground-only branch meant a note typed while CREATING a family
        # entry was silently dropped, then reappeared as editable afterwards.
        "note": data.get("note", ""),
    }
    if kind == "family":
        if data.get("driveway_location"):
            entry["driveway_location"] = data["driveway_location"]
    else:
        entry["elevation_meters"] = float(data.get("elevation_meters", 0))
        entry["waterfront"] = data.get("waterfront", "not waterfront")
        entry["ownership"] = data.get("ownership", "")
        entry["website"] = data.get("website", "")
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

    # Renames aren't uniqueness-checked either — see api_create_campground.
    new_name = data.get("name", "").strip()
    if new_name and new_name != target["name"]:
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


# ── Roadside stop CRUD (admin) ──────────────────────────────────────────────
# Roadside picnic / stretch-break stops are edited inline on the campground map
# (no dedicated manage page). Each route operates on the raw roadside.json and
# returns the map-shaped view (`_roadside_view`) so the client can re-render the
# affected marker without a reload. Optional string fields cleared in the form
# are removed from the entry so the file stays clean.
_ROADSIDE_OPT_FIELDS = ("town", "state", "notes",
                        "website", "phone", "google_maps_url")


@app.route('/api/roadside', methods=['POST'])
def api_create_roadside():
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    ll = _parse_latlng(data.get("location"))
    if not ll:
        return jsonify({"error": "A valid location (lat,lng) is required"}), 400

    stops = _load_roadside_raw()
    next_id = max((s.get("id", 0) for s in stops if isinstance(s.get("id"), int)),
                  default=0) + 1
    entry = {"id": next_id, "name": name}
    for k in ("town", "state"):
        v = (data.get(k) or "").strip()
        if v:
            entry[k] = v
    entry["latitude"], entry["longitude"] = ll
    for k in ("notes", "website", "phone", "google_maps_url"):
        v = (data.get(k) or "").strip()
        if v:
            entry[k] = v
    stops.append(entry)
    _save_roadside(stops)
    return jsonify({"ok": True, "id": next_id, "stop": _roadside_view(entry)})


@app.route('/api/roadside/<int:stop_id>', methods=['PUT'])
def api_update_roadside(stop_id):
    denied = _require_admin()
    if denied:
        return denied
    data = request.get_json() or {}

    stops = _load_roadside_raw()
    target = next((s for s in stops if s.get("id") == stop_id), None)
    if not target:
        return jsonify({"error": "Roadside stop not found"}), 404

    if "name" in data:
        nm = (data.get("name") or "").strip()
        if not nm:
            return jsonify({"error": "Name cannot be empty"}), 400
        target["name"] = nm
    if "location" in data:
        ll = _parse_latlng(data.get("location"))
        if not ll:
            return jsonify({"error": "Invalid location"}), 400
        target["latitude"], target["longitude"] = ll
    for k in _ROADSIDE_OPT_FIELDS:
        if k in data:
            v = (data.get(k) or "").strip()
            if v:
                target[k] = v
            else:
                target.pop(k, None)

    _save_roadside(stops)
    return jsonify({"ok": True, "stop": _roadside_view(target)})


@app.route('/api/roadside/<int:stop_id>', methods=['DELETE'])
def api_delete_roadside(stop_id):
    denied = _require_admin()
    if denied:
        return denied
    stops = _load_roadside_raw()
    remaining = [s for s in stops if s.get("id") != stop_id]
    if len(remaining) == len(stops):
        return jsonify({"error": "Roadside stop not found"}), 404
    _save_roadside(remaining)
    return jsonify({"ok": True})


@app.route('/api/geocode')
def api_geocode():
    """Proxy geocoding lookup via Nominatim.

    A lookup failure returns 502, not an empty array. Swallowing the exception
    into `[]` made a Nominatim outage (or a blocked User-Agent) indistinguishable
    from "no such place" — the search box just closed its dropdown and the admin
    was left retyping a name that was never going to work.
    """
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    try:
        import urllib.request
        url = f"https://nominatim.openstreetmap.org/search?format=json&limit=8&q={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={"User-Agent": _OUTBOUND_UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return jsonify([{"name": r["display_name"], "lat": r["lat"], "lon": r["lon"]} for r in data])
    except Exception as e:
        return jsonify({"error": f"Geocoding lookup failed: {e}"}), 502


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
        req = urllib.request.Request(url, headers={"User-Agent": _OUTBOUND_UA})
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


# Park-like `leisure=*` kinds guaranteed a place in the nearby-places list
# (parks are the point of the picnic/roadside-stop feature).
_PARK_KINDS = ("leisure=park", "leisure=nature_reserve", "leisure=garden",
               "leisure=recreation_ground", "leisure=common")


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
            headers={"User-Agent": _OUTBOUND_UA},
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
        result = hits[:limit]
        # Parks matter for picnic / roadside stops, but a town's closer shops and
        # restaurants can crowd them out of the distance-capped list. When
        # returning a list (not the single-result reverse-geocode fallback), make
        # sure the nearest few parks surface even if they sorted past the cap;
        # keep the merged list distance-ordered.
        if limit > 1:
            have = {id(h) for h in result}
            extra_parks = [h for h in hits
                           if h["kind"] in _PARK_KINDS and id(h) not in have]
            if extra_parks:
                result = sorted(result + extra_parks[:3],
                                key=lambda h: h["distance_m"])
        return result
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
        req = urllib.request.Request(url, headers={"User-Agent": _OUTBOUND_UA})
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


# --- Track cache I/O (gzip-at-rest) ---------------------------------------
# Track caches are stored gzipped as `<id>.json.gz`. These 4-field pings
# (lat/lon/tst/tid) compress ~6x, and a busy dual-tid trip's raw cache can
# top 2 MB. The `.json.gz` extension keeps restore.sh's `*.json` parse-check
# from choking on gzip bytes (its `\.json$` filter excludes `.json.gz`), and
# backup.sh bundles the whole dir content-agnostically. A legacy plain
# `<id>.json` (pre-gzip) is still read transparently and rewritten as
# `.json.gz` on the next persist, so the migration is automatic. Read is
# gzip-magic sniffed so it doesn't matter which extension a file landed under.
def _track_cache_paths(trip_id):
    """Return (gz_path, legacy_plain_path) for a trip's track cache."""
    return (os.path.join(TRACK_CACHE_DIR, f"{trip_id}.json.gz"),
            os.path.join(TRACK_CACHE_DIR, f"{trip_id}.json"))


def _track_cache_exists(trip_id):
    gz, plain = _track_cache_paths(trip_id)
    return os.path.isfile(gz) or os.path.isfile(plain)


def _read_track_cache(trip_id):
    """Return the cached track points list, or None if no cache exists or
    it can't be parsed. Prefers the gzipped `.json.gz`, falls back to a
    legacy plain `.json`; either way the bytes are gzip-magic sniffed so a
    file's actual encoding — not its extension — decides how it's read."""
    gz, plain = _track_cache_paths(trip_id)
    path = gz if os.path.isfile(gz) else (plain if os.path.isfile(plain) else None)
    if path is None:
        return None
    try:
        with open(path, "rb") as f:
            raw = f.read()
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        return json.loads(raw)
    except Exception:
        return None


def _write_track_cache(trip_id, points):
    """Persist track points gzipped to `<id>.json.gz`, removing any legacy
    plain `<id>.json` so each trip has exactly one cache file."""
    gz, plain = _track_cache_paths(trip_id)
    with open(gz, "wb") as f:
        f.write(gzip.compress(json.dumps(points).encode("utf-8")))
    if os.path.isfile(plain):
        try:
            os.remove(plain)
        except OSError:
            pass


def _delete_track_cache(trip_id):
    """Remove both the gzipped and any legacy plain cache file for a trip."""
    for path in _track_cache_paths(trip_id):
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass


def _sweep_legacy_track_caches():
    """One-time, idempotent migration of any pre-gzip plain `<id>.json`
    track caches to `<id>.json.gz`. Runs once at import so every host
    self-heals — notably PythonAnywhere, whose gitignored cache dir doesn't
    ride along with a `git pull`, and long-settled trips there that only
    ever serve from cache would otherwise never trigger a rewrite. Reads
    each legacy file through `_read_track_cache` and rewrites it via
    `_write_track_cache` (which writes the `.gz` and removes the plain).

    Best-effort: any failure is swallowed so a bad cache file can never
    block app startup. After the first run no plain files remain, so the
    steady-state cost is a single directory glob that matches nothing
    (`*.json` excludes `*.json.gz`)."""
    import glob
    converted = 0
    try:
        legacy = glob.glob(os.path.join(TRACK_CACHE_DIR, "*.json"))
    except Exception:
        return
    for path in legacy:
        stem = os.path.splitext(os.path.basename(path))[0]
        if not stem.isdigit():
            continue
        try:
            pts = _read_track_cache(int(stem))
            if pts is None:
                continue
            _write_track_cache(int(stem), pts)
            converted += 1
        except Exception:
            continue
    if converted:
        print(f"[track_cache] migrated {converted} legacy plain cache(s) to gzip")


_sweep_legacy_track_caches()

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


def _track_override_context(trip):
    """Return `(suppressed, bad_windows, relocate)` — the three admin-override
    lookups every consumer of a trip's track needs.

    Shared so the track endpoint and the overview-map route builder resolve
    overrides identically; a consumer that assembled its own set would drift
    the moment a new override kind is added."""
    trip_id = trip["id"]
    return (set(get_suppressed_pings(trip_id)),
            _bad_track_window_tsts(trip),
            _relocation_lookup(get_relocated_pings(trip_id)))


def _select_chosen_track(trip, all_points, suppressed, bad_windows, relocate):
    """Run per-day tid selection on the cached/fetched raw points
    (tid-tagged) and return only the chosen tid's pings.

    The selector's *decision* runs on a cleaned view (suppressed +
    bad-window pings dropped, relocations applied) so admin-marked-
    untrusted pings can't tip the choice. Then we filter the RAW
    points by the per-day choice so the result still carries original
    coords / admin-mode tags — the track endpoint's `_apply_overrides`
    re-applies relocations and emits the admin annotations.

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
            ov = relocate(p)
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

    # tid_windows force a specific tid for a sub-day time range (a
    # gap on the chosen phone the other phone covered). Filter the RAW
    # points by the per-day choice + window overrides so the result
    # keeps original coords / admin tags for `_apply_overrides`.
    tid_windows = _tid_window_tsts(trip, home)
    return _apply_tid_choice(all_points, tid_choices, tid_windows,
                             drop_pad_days=False)


def _clean_track_points(trip, chosen, suppressed, bad_windows, relocate):
    """The canonical "what the line actually shows" view of a trip's track:
    chosen-tid pings with relocations applied, suppressed + bad-window pings
    dropped, trimmed to the trip's local-date range.

    This is what the home-boundary detector runs on, and what the overview
    map's simplified route is built from — so both maps draw the same track.
    Never mutates the input pings (relocations copy)."""
    cleaned = []
    for p in chosen:
        tst = p.get("tst")
        if tst is None or tst in suppressed:
            continue
        if _in_bad_track_window(tst, bad_windows):
            continue
        ov = relocate(p)
        if ov is not None:
            p = {**p, "lat": ov[0], "lon": ov[1]}
        cleaned.append(p)
    return _filter_points_to_trip_window(cleaned, trip["start"], trip["end"])


@app.route('/api/trips/<int:trip_id>/track')
@login_required
def api_trip_track(trip_id):
    """Return the GPS track for a trip from the timeline API.

    Caches results on disk. For trips that ended >1 day ago, the cache is
    served permanently; recent trips re-fetch every call so newly logged
    points show up.
    """
    trip = next((t for t in parse_trips() if t["id"] == trip_id), None)
    if not trip:
        return jsonify({"error": "trip not found"}), 404
    if not trip.get("start") or not trip.get("end"):
        return jsonify([])

    try:
        end_date = date.fromisoformat(trip["end"])
        is_old = (date.today() - end_date) > timedelta(days=1)
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
    relocation_items = get_relocated_pings(trip_id)
    suppressed, bad_windows, _relocate = _track_override_context(trip)

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
        chosen = _select_chosen_track(trip, all_points, suppressed,
                                      bad_windows, _relocate)
        cleaned = _clean_track_points(trip, chosen, suppressed,
                                      bad_windows, _relocate)
        home, _fam = _map_config()
        hs, he = _find_home_boundary_tsts(
            cleaned, home, anchors=_anchors_for_trip(trip))
        return jsonify({
            "points": _apply_overrides(chosen),
            "home_auto_start_tst": hs,
            "home_auto_end_tst": he,
        })

    def _serve_cache():
        cached = _read_track_cache(trip_id)
        if cached is None:
            return jsonify([])
        migrated = _migrate_track_cache_tids(cached)
        tz_changed = _enrich_with_timezone(cached)
        if migrated or tz_changed:
            _write_track_cache(trip_id, cached)
        return _build_response(cached)

    if is_old and _track_cache_exists(trip_id):
        return _serve_cache()

    token = os.environ.get("TIMELINE_API_TOKEN")
    tid = os.environ.get("TIMELINE_TID")
    alt_tid = os.environ.get("TIMELINE_TID_ALT")
    if not token or not tid:
        # Fall back to cache if we have one, else empty (frontend handles this).
        if _track_cache_exists(trip_id):
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
        if _track_cache_exists(trip_id):
            return _serve_cache()
        return jsonify({"error": str(e)}), 502

    _enrich_with_timezone(all_points)
    _write_track_cache(trip_id, all_points)
    return _build_response(all_points)


# ── Overview-map trip routes (precomputed, simplified GPS lines) ────────────
# The trips map draws every trip's GPS line at once. It can't reuse the trip
# detail page's approach for two reasons:
#
#   1. Volume. The detail page ships every ping and builds a circleMarker per
#      one (`static/trip-detail/map.js`) — fine for one trip, but the whole
#      library is ~100k pings across 92 trips, and the overview map wants none
#      of the per-ping interaction anyway.
#   2. Cost per page load. Turning raw pings into the line that's actually
#      drawn runs per-day tid selection and home-boundary detection; doing
#      that for every trip on every landing-page hit is pure repeated work,
#      since the answer only changes when the trip or its track does.
#
# So the line is precomputed once per trip and cached on disk in
# `trip_data/trip_routes.json`, keyed by a signature over everything that can
# change it (below). Entries rebuild lazily when their signature drifts, so
# there's nothing to remember to run after editing a trip.
#
# Routes are built from `_clean_track_points()` — the same view the detail
# map's polyline and the home-boundary detector use — so the two maps can't
# disagree about where a trip went.
TRIP_ROUTES_FILE = os.path.join(TRIP_DATA_DIR, "trip_routes.json")

# Douglas-Peucker tolerance. The overview map is a zoomed-out national view;
# 100 m of cross-track error is sub-pixel until ~z12 and still slight beyond
# that, and it cuts the stored geometry roughly 2.5x (measured: 102k pings ->
# 42k vertices, ~276 KB gzipped for the whole library).
TRIP_ROUTE_SIMPLIFY_M = 100

# Each trip is ONE continuous polyline — a gap in the pings never breaks it.
# An earlier version split the line across long unreported stretches to avoid
# drawing a road that was never driven, but a trip with a hole punched in it
# reads as broken rather than as honest (AWH 2026-07-27), and the trip detail
# map has always connected straight through. Gaps are filled the same way it
# fills them: route through the trip's own anchors that fall inside the gap
# (see `_trip_route_stops`), and straight-line whatever is left over.
#
# Interior gaps only pull in anchors once they're at least this long, so
# routine sparse OwnTracks logging — idle hours at a campground, where the
# only anchor is that same campground — doesn't add detours. Mirrors
# `GAP_FILL_MIN_S` in `static/trip-detail/map.js`; keep the two in step.
TRIP_ROUTE_GAP_FILL_MIN_S = 90 * 60

# Bump to invalidate every cached route after a change to how they're built
# (a different simplifier, a new window rule, a different payload shape).
# Cheaper than remembering to delete the file on deploy — and required, since
# a host that already has a cache would otherwise keep serving the old shape.
#   2: one continuous line per trip (was: a list of gap-split segments)
TRIP_ROUTE_CACHE_VERSION = 2


def _rdp_keep_mask(xs, ys, eps):
    """Douglas-Peucker over a projected (meters) polyline. Returns a
    per-vertex keep mask. Iterative rather than recursive — a long track is
    thousands of points deep and would blow the stack."""
    n = len(xs)
    keep = [False] * n
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        ax, ay, bx, by = xs[i], ys[i], xs[j], ys[j]
        dx, dy = bx - ax, by - ay
        den = math.hypot(dx, dy)
        dmax, idx = 0.0, -1
        for k in range(i + 1, j):
            px, py = xs[k], ys[k]
            if den == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * (px - ax) - dx * (py - ay)) / den
            if d > dmax:
                dmax, idx = d, k
        if dmax > eps and idx > 0:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return keep


def _simplify_latlon(coords, eps_m):
    """Simplify a [(lat, lon), ...] run to within `eps_m`, returning
    `[[lat, lon], ...]` rounded to 5 decimals (~1 m — well under the
    tolerance, and it roughly halves the JSON).

    Projects to meters with an equirectangular approximation around the
    run's mean latitude first, so the tolerance means the same thing
    east-west as north-south (a degree of longitude is ~0.7x a degree of
    latitude at 45 deg, and RDP on raw degrees would over-simplify one axis)."""
    if len(coords) < 3:
        return [[round(la, 5), round(lo, 5)] for la, lo in coords]
    lat0 = sum(c[0] for c in coords) / len(coords)
    kx = math.cos(math.radians(lat0)) * 111320.0
    xs = [c[1] * kx for c in coords]
    ys = [c[0] * 110540.0 for c in coords]
    keep = _rdp_keep_mask(xs, ys, eps_m)
    return [[round(c[0], 5), round(c[1], 5)]
            for c, k in zip(coords, keep) if k]


def _trip_window_cuts(trip, cleaned, home):
    """Resolve the trip's polyline window as `(lower_tst, upper_tst)`,
    either bound possibly None.

    Mirrors the frontend's `computeTripWindow()` precedence exactly: a
    manual `home_start_time`/`home_end_time` wins, the auto-detected home
    boundary fills in when there's no manual override, and None falls back
    to the full local days `_clean_track_points()` already trimmed to."""
    hs, he = _find_home_boundary_tsts(
        cleaned, home, anchors=_anchors_for_trip(trip))
    tz_name = (_tz_for_coord(home[0], home[1])
               if home and home[0] is not None and home[1] is not None
               else None)
    lower = _trip_local_to_tst(
        trip.get("start"), trip.get("home_start_time"), tz_name)
    if lower is None:
        lower = hs
    upper = _trip_local_to_tst(
        trip.get("end"), trip.get("home_end_time"), tz_name)
    if upper is None:
        upper = he
    return lower, upper


def _trip_route_stops(trip, home, tz_name):
    """The trip's planned anchors as `[(tst, (lat, lng)), ...]` in time order
    — the timestamped day-by-day walk used to fill gaps in the GPS line.

    Port of the `routeStops` builder in `static/trip-detail/map.js` (see the
    `Gap-fill the polyline` comment there), and of the same day-by-day rule
    that draws the detail map's dashed "Straight route": for each date,
    morning location (the stay you woke at, else HOME) → that date's events
    sorted by time (untimed counts as noon) → evening location (the stay you
    sleep at tonight, else HOME).

    Future dates are skipped, so an in-progress trip never draws toward an
    event or a homecoming that hasn't happened yet. Consecutive anchors at
    the same coords collapse (a stay's evening and the next morning are the
    same place), keeping the earlier timestamp for ordering.

    Times are resolved in the home timezone. The detail map uses the
    browser's local time, which is the same thing on the family's own
    machines; anywhere else the skew is far smaller than the gaps this
    slices anchors into."""
    stays = [s for s in trip.get("stays", [])
             if s.get("lat") is not None and s.get("lng") is not None]
    events = [e for e in trip.get("events", [])
              if e.get("lat") is not None and e.get("lng") is not None]

    dates = set()
    for s in stays:
        try:
            d, end = date.fromisoformat(s["start"]), date.fromisoformat(s["end"])
        except (ValueError, TypeError, KeyError):
            continue
        while d <= end:
            dates.add(d.isoformat())
            d += timedelta(days=1)
    for e in events:
        if e.get("date"):
            dates.add(e["date"])

    def morning(date_str):
        for s in stays:
            if s["start"] < date_str <= s["end"]:
                return (s["lat"], s["lng"])
        return home

    def evening(date_str):
        for s in stays:
            if s["start"] <= date_str < s["end"]:
                return (s["lat"], s["lng"])
        return home

    stops = []

    def push(tst, pt):
        if tst is None or not pt or pt[0] is None or pt[1] is None:
            return
        if stops and (pt[0], pt[1]) == stops[-1][1]:
            return
        stops.append((tst, (pt[0], pt[1])))

    today_str = date.today().isoformat()
    for date_str in sorted(dates):
        if date_str > today_str:
            continue
        push(_trip_local_to_tst(date_str, "00:00", tz_name), morning(date_str))
        same_day = [e for e in events if e.get("date") == date_str]
        same_day.sort(key=lambda e: e.get("time") or "12:00")
        for e in same_day:
            push(_trip_local_to_tst(date_str, e.get("time") or "12:00", tz_name),
                 (e["lat"], e["lng"]))
        push(_trip_local_to_tst(date_str, "23:59", tz_name), evening(date_str))
    return stops


def _track_covers_trip(trip, in_window, home):
    """True when the GPS data actually belongs to this trip.

    Port of the trip-detail map's auto-fallback gate (see the
    `Auto-fallback: skip the GPS layer` comment in
    `static/trip-detail/map.js`) — kept deliberately identical, because a
    trip the detail map refuses to draw a GPS line for must not get one on
    the overview map either. There the failing gate leaves the dashed
    straight-line route as the only polyline; here it means no line at all,
    since the overview map deliberately carries no straight-line stand-in.

    Strict gate: at least one in-window ping within `TRACK_NEAR_STAY_KM` of
    a stay/event anchor. A phone that roamed on the trip's dates but never
    reached anywhere on the itinerary was on a different errand (the trip-61
    case). Relaxed only while a trip is still in progress: a ping more than
    that far from home counts, so a drive toward a distant sole anchor
    (trip 90) shows up before it arrives."""
    anchors = _anchors_for_trip(trip)
    home_valid = (home and home[0] is not None and home[1] is not None)
    if not anchors and not home_valid:
        return True
    radius_m = TRACK_NEAR_STAY_KM * 1000
    if any(_haversine_m(p["lat"], p["lon"], a_lat, a_lng) <= radius_m
           for p in in_window for a_lat, a_lng in anchors):
        return True
    try:
        in_progress = date.today() <= date.fromisoformat(trip["end"])
    except (ValueError, TypeError, KeyError):
        in_progress = False
    if in_progress and home_valid:
        return any(_haversine_m(p["lat"], p["lon"], home[0], home[1]) > radius_m
                   for p in in_window)
    return False


def _build_trip_route(trip):
    """Build one trip's overview line as a single simplified polyline
    (`[[lat, lon], ...]`). Empty list when the trip has no dates, no cached
    track, or nothing survives cleaning.

    The line is continuous end to end: a stretch the phone never reported is
    filled by routing through the trip's own anchors and straight-lining the
    remainder, exactly as the detail map does.

    Reads only the on-disk track cache — never the timeline API. A trip
    whose track has never been fetched simply has no line until someone
    opens its detail page, which is the right trade for a page that draws
    every trip at once: one cold trip must not turn the landing page into
    92 upstream requests."""
    if not trip.get("start") or not trip.get("end"):
        return []
    points = _read_track_cache(trip["id"])
    if not points:
        return []
    # In-memory only; persisting the migration is the track endpoint's job.
    _migrate_track_cache_tids(points)

    suppressed, bad_windows, relocate = _track_override_context(trip)
    chosen = _select_chosen_track(trip, points, suppressed, bad_windows,
                                  relocate)
    cleaned = _clean_track_points(trip, chosen, suppressed, bad_windows,
                                  relocate)
    if not cleaned:
        return []
    cleaned.sort(key=lambda p: p.get("tst") or 0)

    home, _fam = _map_config()
    lower, upper = _trip_window_cuts(trip, cleaned, home)
    kept = [p for p in cleaned
            if (lower is None or p["tst"] >= lower)
            and (upper is None or p["tst"] <= upper)]
    if not _track_covers_trip(trip, kept, home):
        return []

    # Gap-fill, mirroring the detail map (`Gap-fill the polyline` in
    # static/trip-detail/map.js): walk the pings in time order, and wherever
    # two consecutive ones are far enough apart in time, splice in the
    # planned anchors that fall between them so the connector follows where
    # the trip actually went rather than cutting a chord across it. Leading
    # and trailing anchors are spliced unconditionally — that's the
    # leaving-home and coming-home leg — but never one whose clock time
    # hasn't arrived yet, so an in-progress trip doesn't draw itself home
    # before it gets there. Anchors are a refinement, not a requirement: a
    # gap with none in it still connects, straight and possibly long.
    tz_name = (_tz_for_coord(home[0], home[1])
               if home and home[0] is not None and home[1] is not None
               else None)
    stops = _trip_route_stops(trip, home, tz_name)
    now_tst = time.time()

    coords = []

    def push(pt):
        if coords and (pt[0], pt[1]) == coords[-1]:
            return
        coords.append((pt[0], pt[1]))

    first_tst, last_tst = kept[0]["tst"], kept[-1]["tst"]
    for tst, ll in stops:
        if tst < first_tst:
            push(ll)
    for i, p in enumerate(kept):
        push((p["lat"], p["lon"]))
        if i + 1 < len(kept):
            a, b = p["tst"], kept[i + 1]["tst"]
            if b - a >= TRIP_ROUTE_GAP_FILL_MIN_S:
                for tst, ll in stops:
                    if a < tst < b:
                        push(ll)
    for tst, ll in stops:
        if last_tst < tst <= now_tst:
            push(ll)

    if len(coords) < 2:
        return []
    return _simplify_latlon(coords, TRIP_ROUTE_SIMPLIFY_M)


def _trip_route_signature(trip, raw_record):
    """Fingerprint everything that can change a trip's line.

    Covers the track cache file itself (mtime + size, so a re-fetch of a
    recent trip's pings is picked up) and the whole raw trip record — which
    is what carries the dates, the anchors the boundary detector and tid
    selector run against, and every admin override (`suppressed_pings`,
    `relocated_pings`, `bad_track_windows`, `tid_overrides`, `tid_windows`).
    Hashing the record wholesale rather than naming fields is deliberate: a
    new override kind can't be forgotten here and silently serve a stale line.

    `in_progress` is in here because `_track_covers_trip`'s gate relaxes for
    a trip that's still happening. Without it, a line admitted under the
    relaxed gate would outlive the trip: once it ends, the track cache stops
    being re-fetched, so nothing else in this fingerprint would ever change
    and the strict gate would never get to re-judge it."""
    try:
        in_progress = date.today() <= date.fromisoformat(trip.get("end"))
    except (ValueError, TypeError):
        in_progress = False
    track_stat = None
    for path in _track_cache_paths(trip["id"]):
        if os.path.isfile(path):
            st = os.stat(path)
            track_stat = [int(st.st_mtime), st.st_size]
            break
    payload = {
        "v": TRIP_ROUTE_CACHE_VERSION,
        "eps": TRIP_ROUTE_SIMPLIFY_M,
        "gap": TRIP_ROUTE_GAP_FILL_MIN_S,
        "track": track_stat,
        "in_progress": in_progress,
        "trip": raw_record,
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def _load_trip_routes_cache():
    """Read the route cache, or `{}` if absent/corrupt. Keys are trip ids
    as strings (JSON object keys)."""
    try:
        with open(TRIP_ROUTES_FILE) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_trip_routes_cache(cache):
    """Persist the route cache via temp-file + atomic replace, so a crash
    mid-write can't leave a half-written file that reads as empty and
    silently drops every line from the map. Best-effort: a failure here
    costs a rebuild next request, never a broken response."""
    tmp = TRIP_ROUTES_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(cache, f, separators=(",", ":"))
        os.replace(tmp, TRIP_ROUTES_FILE)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _trip_routes(trips, force=False, prune=False):
    """Return `{trip_id: [[lat, lon], ...]}` — one continuous polyline per
    trip — rebuilding any entry whose signature drifted and persisting the
    cache if anything changed. Trips with no line are omitted entirely
    rather than carried as empty lists; the client just draws what it's given.

    `prune` drops cached entries for trips not in `trips`, and is only safe
    for a caller passing the *whole* library: the request path passes a
    filtered list (a non-admin doesn't see home-only trips), and pruning
    there would evict routes the caller merely can't see, churning them back
    and forth on every alternating admin/non-admin request."""
    cache = _load_trip_routes_cache()
    raw_by_id = {t["id"]: t for t in raw_trip_records()}
    out, dirty = {}, False

    for trip in trips:
        key = str(trip["id"])
        sig = _trip_route_signature(trip, raw_by_id.get(trip["id"]))
        entry = cache.get(key)
        if force or not entry or entry.get("sig") != sig:
            entry = {"sig": sig, "line": _build_trip_route(trip)}
            cache[key] = entry
            dirty = True
        if entry.get("line"):
            out[trip["id"]] = entry["line"]

    if prune:
        live = {str(t["id"]) for t in trips}
        for stale in [k for k in cache if k not in live]:
            del cache[stale]
            dirty = True

    if dirty:
        _save_trip_routes_cache(cache)
    return out


def _delete_trip_route(trip_id):
    """Drop a trip's cached route (called when the trip is deleted)."""
    cache = _load_trip_routes_cache()
    if cache.pop(str(trip_id), None) is not None:
        _save_trip_routes_cache(cache)


@app.route('/api/trips/routes')
@login_required
def api_trip_routes():
    """Every visible trip's simplified GPS line, for the overview map.

    Fetched after the map has painted rather than embedded in the page: it's
    a few hundred KB gzipped and the map is useful without it, so it must
    not sit in front of first render. Home-only trips are filtered for
    non-admins exactly as `trips_map()` filters them, so a hidden trip can't
    reappear as a line on the map."""
    trips = parse_trips()
    is_admin = current_user.is_authenticated and current_user.is_admin
    if not is_admin:
        trips = [t for t in trips if not t.get("home_only")]
    return jsonify(_trip_routes(trips))


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

    points = _read_track_cache(trip_id)
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
            _write_track_cache(trip_id, points)
        except Exception:
            return []
    else:
        # Cache hit: migrate legacy untagged entries before the selector
        # runs (it groups by tid).
        if _migrate_track_cache_tids(points):
            _write_track_cache(trip_id, points)

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
    chosen, choices = _select_track_per_day(
        p_pts, a_pts, anchors, home, trip["start"], trip["end"],
        tid_overrides=trip.get("tid_overrides") or {},
    )
    # tid_windows (sub-day tid overrides) — re-derive from the cleaned
    # points so detection sees the same window-corrected track the
    # polyline does. No windows → keep the selector's chosen unchanged.
    tid_windows = _tid_window_tsts(trip, home)
    if tid_windows:
        chosen = _apply_tid_choice(points, choices, tid_windows,
                                   drop_pad_days=True)
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


def _tid_window_tsts(trip, home=None):
    """Convert a trip's `tid_windows` JSON into a list of
    `(start_tst, end_tst, tid)` tuples. Each entry is
    `{start: "YYYY-MM-DDTHH:MM", end: "...", tid: "primary"|"alt",
    note: "..."}` with times interpreted in the home timezone — same
    convention as `bad_track_windows` / `home_start_time`, via the shared
    `_trip_local_to_tst` helper.

    A `tid_window` forces the per-day tid selection to a specific device
    for a sub-day time range. Use it when the normally-chosen tid is
    missing pings for a short span that the other tid covers (a gap on the
    primary phone that the alt phone recorded). Unlike `tid_overrides`
    (whole-day), this is time-of-day granular.

    Returns `[]` when the trip has no `tid_windows`, home is unconfigured,
    or no entry parses cleanly with a valid tid. Malformed or unknown-tid
    entries are silently skipped — hand-edited JSON, so one typo costs a
    window, not the trip."""
    windows_raw = trip.get("tid_windows") or []
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
        for sep in ("T", " "):
            if sep in dt_str:
                parts = dt_str.split(sep, 1)
                if len(parts) == 2 and parts[0] and parts[1]:
                    return parts[0], parts[1]
        return None, None

    out = []
    for w in windows_raw:
        tid = (w.get("tid") or "").strip()
        if tid not in ("primary", "alt"):
            continue
        sd, st = _split((w.get("start") or "").strip())
        ed, et = _split((w.get("end") or "").strip())
        if not sd or not ed:
            continue
        s_tst = _trip_local_to_tst(sd, st, home_tz_name)
        e_tst = _trip_local_to_tst(ed, et, home_tz_name)
        if s_tst is None or e_tst is None:
            continue
        if s_tst > e_tst:
            s_tst, e_tst = e_tst, s_tst
        out.append((s_tst, e_tst, tid))
    return out


def _tid_for_window(tst, windows):
    """Return the forced tid ('primary'|'alt') if `tst` falls inside a
    tid_window, else None. Last matching window wins so a later
    hand-edited entry overrides an earlier one on overlap."""
    if tst is None or not windows:
        return None
    found = None
    for s, e, tid in windows:
        if s <= tst <= e:
            found = tid
    return found


def _apply_tid_choice(all_points, tid_choices, tid_windows, drop_pad_days):
    """Filter tid-tagged `all_points` down to the chosen tid per ping.

    For each ping the wanted tid is the `tid_windows` override when the
    ping falls inside one, else the per-day `tid_choices` entry for its
    local date. Pad-day pings (no per-day choice) are dropped when
    `drop_pad_days` is True (detection considers only in-trip pings) or
    passed through primary-only when False (the polyline draws the
    leaving/arriving-home legs from them). Returns pings sorted by `tst`.

    Shared by the polyline path (`api_trip_track`) and the detection path
    (`_load_trip_track_for_detection`) so both honor tid_windows and see
    the same chosen pings. With an empty `tid_windows` and matching
    `drop_pad_days`, this reproduces the prior per-day-only selection."""
    chosen = []
    for p in all_points:
        d = _local_date_of_ping(p)
        if d is None:
            continue
        win_tid = _tid_for_window(p.get("tst"), tid_windows)
        if win_tid is not None:
            wanted = win_tid
        else:
            choice = tid_choices.get(d)
            if choice is None:
                if not drop_pad_days and p.get("tid") == "primary":
                    chosen.append(p)
                continue
            wanted = choice.split(":")[-1]  # 'override:alt' → 'alt'
        if p.get("tid") == wanted:
            chosen.append(p)
    chosen.sort(key=lambda x: x.get("tst", 0))
    return chosen


def _naive_utc(tst):
    """UTC wall-clock for a unix timestamp, as a naive datetime.

    Replaces datetime.utcfromtimestamp(), which is deprecated and scheduled for
    removal. Callers here stamp the tzinfo themselves a line or two later
    (`.replace(tzinfo=ZoneInfo("UTC")).astimezone(...)`), so the naive value is
    what they want — hence the explicit tzinfo strip rather than returning the
    aware datetime.
    """
    return datetime.fromtimestamp(tst, timezone.utc).replace(tzinfo=None)


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
    utc = _naive_utc(tst)
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
            utc = _naive_utc(tst)
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

    cached = _read_track_cache(trip_id)
    if cached is None:
        cached = []
    else:
        _migrate_track_cache_tids(cached)

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
        utc = _naive_utc(tst)
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
    """Proxy elevation lookup via the Open-Meteo DEM.

    Open-Meteo, not Open-Elevation: every one of the ~12.9k entries in
    campgrounds.json was pinned against Open-Meteo by the curation tooling, and
    the two DEMs disagree by several metres at the same coordinate (152 m vs
    145 m at 40.0,-77.0). Elevation feeds the campground map's climate colouring,
    so an entry added through the UI needs to come off the same source as its
    neighbours. Open-Meteo is also the more reliable of the two.
    """
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng required"}), 400
    try:
        import urllib.request
        url = ("https://api.open-meteo.com/v1/elevation"
               f"?latitude={lat}&longitude={lng}")
        req = urllib.request.Request(url, headers={"User-Agent": _OUTBOUND_UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return jsonify({"elevation_meters": data["elevation"][0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route('/api/campgrounds/<int:cg_id>', methods=['DELETE'])
def api_delete_campground(cg_id):
    """Delete a campgrounds.json entry.

    Refuses (409) while any trip still references it. References are by id, so
    a delete doesn't fail loudly — the campspot's `place` quietly falls back to
    `custom_place or ""` and it loses its coordinates, leaving a blank row that
    plots nowhere. `?force=1` overrides for the case where that's genuinely
    intended.
    """
    denied = _require_admin()
    if denied:
        return denied

    refs = campground_references(cg_id)
    if refs and request.args.get("force") != "1":
        trips = sorted({r["trip_id"] for r in refs})
        return jsonify({
            "error": ("In use by {} {} (trip{} {}). Repoint or remove {} first, "
                      "or re-send with ?force=1.").format(
                          len(refs),
                          "reference" if len(refs) == 1 else "references",
                          "" if len(trips) == 1 else "s",
                          ", ".join(str(t) for t in trips),
                          "it" if len(refs) == 1 else "them"),
            "references": refs,
        }), 409

    with open(CAMPGROUNDS_JSON) as f:
        entries = json.load(f)

    before = len(entries)
    entries = [e for e in entries if e.get("id") != cg_id]
    if len(entries) == before:
        return jsonify({"error": "Campground not found"}), 404

    _save_json(CAMPGROUNDS_JSON, entries)
    return jsonify({"ok": True})


def _dev_ssl_context():
    """ssl_context for the dev server's app.run().

    Reuse a persistent self-signed cert under trip_data/ (gitignored) so the
    browser exception you accept keeps working across the debug reloader's
    restarts. `'adhoc'` mints a brand-new cert on every boot, so the accepted
    exception no longer matches and the cert warning returns on every code
    change. Generated once via Werkzeug's make_ssl_devcert; falls back to
    `'adhoc'` if that can't run (e.g. cryptography missing).
    """
    base = os.path.join(TRIP_DATA_DIR, "dev_cert")
    cert_file, key_file = base + ".crt", base + ".key"
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return (cert_file, key_file)
    try:
        from werkzeug.serving import make_ssl_devcert
        os.makedirs(TRIP_DATA_DIR, exist_ok=True)
        make_ssl_devcert(base, host="localhost")
        print(f"Generated a persistent dev cert at {cert_file} — accept it "
              "once in the browser; it survives reloads.")
        return (cert_file, key_file)
    except Exception as e:
        print(f"Could not generate a persistent dev cert ({e}); falling back "
              "to a fresh adhoc cert each restart.")
        return "adhoc"


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
    elif len(sys.argv) >= 2 and sys.argv[1] == "rebuild-routes":
        # The overview map's trip lines rebuild themselves lazily, so this is
        # only ever a warm-up: run it after a deploy (or after restoring track
        # caches) so the first visitor doesn't pay for the whole library.
        force = "--force" in sys.argv[2:]
        t0 = time.time()
        all_trips = parse_trips()
        routes = _trip_routes(all_trips, force=force, prune=True)
        vertices = sum(len(line) for line in routes.values())
        print(f"Built routes for {len(routes)} of {len(all_trips)} trip(s), "
              f"{vertices} vertices, in {time.time() - t0:.1f}s "
              f"-> {TRIP_ROUTES_FILE}")
    else:
        # Pass --http to skip TLS (HTTPS is on by default so mobile devices
        # on the LAN can use Geolocation, which requires a secure origin).
        # HTTPS uses a persistent self-signed cert (see _dev_ssl_context) so the
        # browser exception survives reloads; it requires `cryptography`.
        parser = argparse.ArgumentParser(description="Run the EKKO Trips dev server.")
        parser.add_argument('--port', type=int, default=5001,
                            help="Port to listen on (default: 5001).")
        parser.add_argument('--http', action='store_true',
                            help="Serve plain HTTP instead of the default self-signed HTTPS.")
        args = parser.parse_args()
        # Werkzeug's reloader runs this block in both the watcher (env var unset)
        # and the re-exec'd worker (env var 'true'); warn only in the watcher so
        # the message prints exactly once (and still prints with no reloader).
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            _check_home_config()
        ssl_context = None if args.http else _dev_ssl_context()
        app.run(debug=True, host='0.0.0.0', port=args.port, ssl_context=ssl_context)
