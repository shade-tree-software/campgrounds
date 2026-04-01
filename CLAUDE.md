# EKKO Trips

A Flask web app for documenting family camping trips in an RV called "EKKO" and discovering new campgrounds.

## Tech Stack

- **Backend:** Flask (Python) on port 5001, Flask-Login for auth
- **Frontend:** Server-side Jinja2 templates, Leaflet.js maps, vanilla JS (no framework)
- **Storage:** JSON files (no database) — `trip_data/trips.json`, `trip_data/captions.json`, `trip_data/photo_order.json`
- **Photos:** Saved to `static/uploads/{trip_id}/{stay_idx}/` (stays) and `static/uploads/{trip_id}/events/{event_idx}/` (events)
- **External APIs:** Open-Meteo (weather), Open-Elevation, Textbelt (SMS)

## Key Files

- `ekko_trips_app.py` — Main Flask app: routes, auth, photo endpoints
- `trips.py` — Trip data CRUD, JSON persistence, trip parsing logic
- `summer_finder.py` — Shared weather search logic (used by CLI and web)
- `templates/trip_detail.html` — Trip detail page (~1400 lines): photo galleries, inline editing, drag-drop reorder, maps
- `templates/base.html` — Base template with nav and trip stats header
- `config.json` — App config (home location, family locations)
- `all-campgrounds.json` — Campground database (~2000 sites)

## Architecture

- **Data model:** Trips contain stays (campground visits) and events. Stays are sorted by start date, events by date. A timeline merges both chronologically.
- **Admin protection:** `_require_admin()` helper guards all mutation endpoints (upload, edit, delete, reorder). Template uses `is_admin` Jinja variable and `IS_ADMIN` JS constant to conditionally render edit controls.
- **Photo metadata** (captions, ordering) is stored separately from the files themselves.
- **Campground coordinates** are matched from `all-campgrounds.json` by place name, or parsed from the site field.

## Conventions

- Private Python functions prefixed with `_`
- Routes organized by section with comment headers in `ekko_trips_app.py`
- Photo keys use format `{trip_id}/{stay_idx}/{filename}`
- Trip IDs are sequential integers
- No frontend build step — all JS is inline in templates
