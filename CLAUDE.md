# EKKO Trips

A Flask web app for documenting family camping trips in an RV called "EKKO" and discovering new campgrounds.

## Tech Stack

- **Backend:** Flask (Python) on port 5001, Flask-Login for auth
- **Frontend:** Server-side Jinja2 templates, Leaflet.js maps, vanilla JS (no framework)
- **Storage:** JSON files (no database) — `trip_data/trips.json`, `trip_data/captions.json`, `trip_data/photo_order.json`
- **Photos:** Saved to `static/uploads/{trip_id}/{stay_idx}/` (stays) and `static/uploads/{trip_id}/events/{event_idx}/` (events)
- **External APIs:** Open-Meteo (weather), Open-Elevation, Textbelt (SMS)
- **Virtualenv:** `ekko_trips_venv/` (activate before running)

## Key Files

- `ekko_trips_app.py` — Main Flask app: routes, auth, photo endpoints, campground CRUD API
- `trips.py` — Trip data CRUD, JSON persistence, trip parsing logic, `rename_campground_in_trips()`
- `summer_finder.py` — Shared weather search logic (used by CLI and web)
- `config.json` — App config (home location, family locations)
- `all-campgrounds.json` — Campground database (~808 sites with name, location, elevation_meters, waterfront, state, ownership, website, note, phone, stays)

### Templates

- `templates/base.html` — Base template with nav and trip stats header. Nav groups: Trips (Map, Calendar, List), Campgrounds (Proximity to Water, Climate, Manage). Manage link is admin-only.
- `templates/trip_detail.html` — Trip detail page (~1580 lines): photo galleries, inline editing, campground autocomplete picker, drag-drop reorder (within and across stays/events), Leaflet map
- `templates/trips_map.html` — Main page: photo filmstrip slideshow (clicking a photo navigates to its trip) + Leaflet map of all camping locations
- `templates/trips_calendar.html` — Calendar and list views of trips
- `templates/campground_map.html` — Campground map with color-coded markers by waterfront type or climate. Popups show: name, state, elevation, visit count, note, phone numbers, websites (displayed by domain name)
- `templates/campground_manage.html` — Admin-only campground CRUD: searchable/sortable table with inline editing. Location, website, and phone are sub-fields within the note column during editing.

## Architecture

- **Data model:** Trips contain stays (campground visits) and events. Stays are sorted by start date, events by date. A timeline merges both chronologically.
- **Admin protection:** `_require_admin()` helper guards all mutation endpoints (upload, edit, delete, reorder, move, campground CRUD). Templates use `is_admin` Jinja variable and `IS_ADMIN` JS constant to conditionally render edit controls. Drag-drop is fully disabled for non-admins (no draggable attributes, no event listeners).
- **Photo metadata** (captions, ordering) is stored separately from the files themselves.
- **Campground references:** Stays reference campgrounds by name (no IDs). The `place` field in a stay must match a `name` in `all-campgrounds.json` for coordinates to resolve. Renaming a campground via the management page propagates to all trips via `rename_campground_in_trips()`.
- **Campground autocomplete:** Stay edit forms use an autocomplete picker that fetches from `GET /api/campgrounds`. Selecting a campground auto-fills the state field. Custom (non-campground) values are still allowed.
- **Photo drag-and-drop:** Supports both within-grid reorder and cross-grid moves (stay-to-stay, stay-to-event, etc.). Cross-grid moves call `POST /trips/<id>/move-photo` which relocates the file and updates captions/order. Upload areas detect whether a drag is an internal photo move or an external file upload and handle accordingly.
- **Trip date defaults:** When adding a new stay or event, dates default to the trip's first stay start date (not today's date).

## API Routes

### Trip/Stay/Event CRUD
- `POST /api/trips` — create trip
- `PUT/DELETE /api/trips/<id>` — update/delete trip
- `POST /api/trips/<id>/stays` — add stay
- `PUT/DELETE /api/trips/<id>/stays/<idx>` — update/delete stay
- `POST /api/trips/<id>/events` — add event
- `PUT/DELETE /api/trips/<id>/events/<idx>` — update/delete event

### Photo Operations
- `POST /trips/<id>/stays/<idx>/upload` — upload stay photo
- `POST /trips/<id>/events/<idx>/upload` — upload event photo
- `POST /trips/<id>/stays/<idx>/reorder` — reorder stay photos
- `POST /trips/<id>/events/<idx>/reorder` — reorder event photos
- `POST /trips/<id>/move-photo` — move photo between stays/events (body: filename, src_type, src_idx, dst_type, dst_idx)
- `POST /trips/<id>/stays/<idx>/caption` — save stay photo caption
- `POST /trips/<id>/events/<idx>/caption` — save event photo caption
- `DELETE /trips/<id>/stays/<idx>/photos/<file>` — delete stay photo
- `DELETE /trips/<id>/events/<idx>/photos/<file>` — delete event photo

### Campground CRUD
- `GET /api/campgrounds` — lightweight name+state list (for autocomplete picker)
- `GET /api/campgrounds/all` — full data (admin, for management page)
- `POST /api/campgrounds` — create campground (enforces unique names)
- `PUT /api/campgrounds/<name>` — update campground (name changes propagate to trips)
- `DELETE /api/campgrounds/<name>` — delete campground

## Conventions

- Private Python functions prefixed with `_`
- Routes organized by section with comment headers in `ekko_trips_app.py`
- Photo keys use format `{trip_id}/{stay_idx}/{filename}` (stays) or `{trip_id}/events/{event_idx}/{filename}` (events)
- Photo order keys: `{trip_id}/{stay_idx}` or `{trip_id}/events/{event_idx}`
- Trip IDs are sequential integers
- No frontend build step — all JS/CSS is inline in templates
- The waterfront field in data is called "waterfront" but displayed to users as "Proximity to Water"
