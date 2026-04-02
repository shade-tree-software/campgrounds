# EKKO Trips

A Flask web app for documenting family camping trips in an RV called "EKKO" and discovering new campgrounds.

## Tech Stack

- **Backend:** Flask (Python) on port 5001, Flask-Login for auth
- **Frontend:** Server-side Jinja2 templates, Leaflet.js maps, vanilla JS (no framework)
- **Storage:** JSON files (no database) — `trip_data/trips.json`, `trip_data/captions.json`, `trip_data/photo_order.json`
- **Photos:** Saved to `static/uploads/{trip_id}/{stay_idx}/` (campspots) and `static/uploads/{trip_id}/events/{event_idx}/` (events)
- **External APIs:** Open-Meteo (weather), Open-Elevation, Textbelt (SMS)
- **Virtualenv:** `ekko_trips_venv/` (activate before running)

## Key Files

- `ekko_trips_app.py` — Main Flask app: routes, auth, photo endpoints, campground CRUD API
- `trips.py` — Trip data CRUD, JSON persistence, trip parsing logic, `rename_campground_in_trips()`
- `summer_finder.py` — Shared weather search logic (used by CLI and web)
- `config.json` — App config (home location, family locations)
- `all-campgrounds.json` — Campground database (~808 sites with name, location, elevation_meters, waterfront, state, ownership, website, note, phone, stays)

### Templates

- `templates/base.html` — Base template with nav and trip stats header. Nav groups: Trips (Map, Calendar, List), Campgrounds (Proximity to Water, Climate, Manage). Manage link is admin-only. Header shows counts of overnight trips, day trips, and nights.
- `templates/trip_detail.html` — Trip detail page (~1600 lines): photo galleries, inline editing, campground autocomplete picker, drag-drop reorder (within and across stays/events), prev/next trip navigation arrows, Leaflet map. Shows night, campspot, and event counts in trip header.
- `templates/trips_map.html` — Main page: photo filmstrip slideshow (5 photos visible, slides every 4s, clicking navigates to trip) + Leaflet map of all camping locations. No redundant title between slideshow and map.
- `templates/trips_calendar.html` — Calendar and list views of trips. Switching between views is client-side (no page reload), preserving the selected year. List view shows night/campspot/event counts per trip, each omitted when zero.
- `templates/campground_map.html` — Campground map with color-coded markers by proximity to water or climate. Popups show: name, state, elevation, visit count, note, phone numbers, websites (displayed by domain name). Does not show waterfront/climate fields since they are conveyed by dot color.
- `templates/campground_manage.html` — Admin-only campground CRUD: searchable/sortable table with inline editing. Location, website, and phone are sub-fields within the note column during editing. Leaflet map picker appears below the table during add/edit for click-to-set location; auto-fetches elevation via `/api/elevation`. Elevation is displayed in feet (stored as meters internally).

## Architecture

### Trip ID vs Display Number

Trips have two distinct identifiers:
- **`id`** — Permanent, auto-incrementing integer. Used for URLs (`/trips/42`), photo directory paths, API routes, and all internal references. Never changes once assigned.
- **`number`** — Computed dynamically in `_load_trips_json()` based on chronological sort position. Used only for display ("Trip 5: ..."). Automatically adjusts when trips are added/removed without renumbering stored data.

### Trip Types

- **Overnight trips** have at least one campspot. Header stats show overnight trip count and total nights.
- **Day trips** have only events (no campspots). A trip survives deletion of its last campspot if it still has events. Date range is derived from events when no campspots exist. Summary falls back to trip note or "Events Only".

### Data Model

- Trips contain campspots (campground visits) and events. Campspots are sorted by start date, events by date. A timeline merges both chronologically.
- When adding a new campspot or event, dates default to the trip's first campspot start date (not today's date).

### Admin Protection

`_require_admin()` helper guards all mutation endpoints (upload, edit, delete, reorder, move, campground CRUD). Templates use `is_admin` Jinja variable and `IS_ADMIN` JS constant to conditionally render edit controls. Drag-drop is fully disabled for non-admins (no draggable attributes, no event listeners).

### Photo System

- Photo metadata (captions, ordering) is stored separately from the files themselves.
- Drag-and-drop supports both within-grid reorder and cross-grid moves (campspot-to-campspot, campspot-to-event, etc.). Cross-grid moves call `POST /trips/<id>/move-photo` which relocates the file and updates captions/order.
- Upload areas detect whether a drag is an internal photo move or an external file upload and handle accordingly. When the destination grid is empty, the upload area itself serves as the drop target for photo moves (styled with red border instead of showing a separate empty grid indicator).

### Campground System

- Campspots reference campgrounds by name (no IDs). The `place` field in a campspot must match a `name` in `all-campgrounds.json` for coordinates to resolve. Renaming a campground via the management page propagates to all trips via `rename_campground_in_trips()`.
- Campspot edit forms use an autocomplete picker that fetches from `GET /api/campgrounds`. Selecting a campground auto-fills the state field. Custom (non-campground) values are still allowed for non-campground campspots (family homes, hotels).

## API Routes

### Trip/Campspot/Event CRUD
- `POST /api/trips` — create trip
- `PUT/DELETE /api/trips/<id>` — update/delete trip
- `POST /api/trips/<id>/stays` — add campspot
- `PUT/DELETE /api/trips/<id>/stays/<idx>` — update/delete campspot
- `POST /api/trips/<id>/events` — add event
- `PUT/DELETE /api/trips/<id>/events/<idx>` — update/delete event

### Photo Operations
- `POST /trips/<id>/stays/<idx>/upload` — upload campspot photo
- `POST /trips/<id>/events/<idx>/upload` — upload event photo
- `POST /trips/<id>/stays/<idx>/reorder` — reorder campspot photos
- `POST /trips/<id>/events/<idx>/reorder` — reorder event photos
- `POST /trips/<id>/move-photo` — move photo between campspots/events (body: filename, src_type, src_idx, dst_type, dst_idx)
- `POST /trips/<id>/stays/<idx>/caption` — save campspot photo caption
- `POST /trips/<id>/events/<idx>/caption` — save event photo caption
- `DELETE /trips/<id>/stays/<idx>/photos/<file>` — delete campspot photo
- `DELETE /trips/<id>/events/<idx>/photos/<file>` — delete event photo

### Campground CRUD
- `GET /api/campgrounds` — lightweight name+state list (for autocomplete picker)
- `GET /api/campgrounds/all` — full data (admin, for management page)
- `POST /api/campgrounds` — create campground (enforces unique names)
- `PUT /api/campgrounds/<name>` — update campground (name changes propagate to trips)
- `DELETE /api/campgrounds/<name>` — delete campground
- `GET /api/elevation?lat=X&lng=Y` — proxy to Open-Elevation API, returns `{elevation_meters}`

## Conventions

- Private Python functions prefixed with `_`
- Routes organized by section with comment headers in `ekko_trips_app.py`
- Photo keys use format `{trip_id}/{stay_idx}/{filename}` (campspots) or `{trip_id}/events/{event_idx}/{filename}` (events)
- Photo order keys: `{trip_id}/{stay_idx}` or `{trip_id}/events/{event_idx}`
- Trip IDs are permanent auto-incrementing integers; display numbers are computed from chronological position
- No frontend build step — all JS/CSS is inline in templates
- The data model uses "stays" internally (code, JSON keys, API routes) but the user-facing term is "campspot/campspots"
- The waterfront field in data is called "waterfront" but displayed to users as "Proximity to Water"
- Pluralization: all counters use singular when count is exactly 1, plural otherwise (including 0). In JS use `!== 1`, in Jinja use `== 1`. Never use `> 1` as it mishandles zero.
