# EKKO Trips

A Flask web app for documenting family camping trips in an RV called "EKKO" and discovering new campgrounds.

## Tech Stack

- **Backend:** Flask (Python) on port 5001, Flask-Login for auth, Pillow for EXIF
- **Frontend:** Server-side Jinja2 templates, Leaflet.js maps, vanilla JS (no framework)
- **Storage:** JSON files (no database) — `trip_data/trips.json`, `trip_data/captions.json`, `trip_data/photo_order.json`
- **Photos:** Saved to `static/uploads/{trip_id}/{stay_idx}/` (campspots) and `static/uploads/{trip_id}/events/{event_idx}/` (events)
- **External APIs:** Open-Meteo (weather), Open-Elevation, Nominatim (geocoding), Textbelt (SMS)
- **Virtualenv:** `ekko_trips_venv/` (activate before running)

## Key Files

- `ekko_trips_app.py` — Main Flask app: routes, auth, photo endpoints, campground CRUD API, geocode proxy
- `trips.py` — Trip data CRUD, JSON persistence, trip parsing logic, location resolution via `_load_locations_by_id()`, photo index remapping on sort
- `summer_finder.py` — Shared weather search logic (used by CLI and web)
- `home.json` — App config (home coords + altitude only)
- `campgrounds.json` — Unified location database (~813 entries). Each entry has `id` (stable auto-incrementing int), `kind` ("campground" or "family"), `name`, `location` ("lat,lng"), `state`. Campground-kind also carries `elevation_meters`, `waterfront`, `ownership`, `website`, `note`, `phone`, `stays`. Family-kind may carry `driveway_location` ("lat,lng") used instead of `location` for stay-marker placement.
- `static/map-picker.js` — Shared map picker popup factory (`createMapPicker()`) used by campground manage and event location picker
- `static/map-picker.css` — Shared map picker styles (positioning, resize handles, geocode search dropdown)

### Templates

- `templates/base.html` — Base template with sticky header+nav wrapped in `.site-top` container. Sets `--site-top-height` CSS variable via JS for child pages to position their own sticky sub-headers. Nav groups: Trips (Map, Calendar, List), Campgrounds (Proximity to Water, Climate, Manage). Manage link is admin-only. Header shows counts of overnight trips, day trips (events-only trips, excludes empty trips), and nights.
- `templates/trip_detail.html` — Trip detail page (~1800 lines): photo galleries with lightbox (shows EXIF date taken), inline editing on photo-bearing cards, campground autocomplete picker, drag-drop reorder (within and across stays/events), prev/next trip navigation arrows, Leaflet map. Sticky trip header (red bar) positioned below site-top. Map container has `z-index: 0` to create a stacking context so Leaflet controls don't overflow above sticky headers. Shows night, campspot, and event counts in trip header. Date range hidden when trip has no stays or events. Add Campspot/Event buttons are small regular buttons below the map (admin-only). Events with locations show as gold star dots on the map. Event edit form includes optional end date and location with a click-on-map picker. Stay markers have higher z-index than event markers. Family markers only shown when a stay or event is within 80km. Cards below the map are photo frames only — they render exclusively when the stay/event has photos. Page-load globals (`TRIP_ID`, `IS_ADMIN`, `FIRST_STAY_DATE`, `STAYS_ALL`, `EVENTS_ALL`, `FAMILY_LOCATIONS`) are declared at the very top of the inline `<script>` block before the map IIFE so popup helpers can reference them without hitting a `const` TDZ.
- `templates/trips_map.html` — Main page: photo filmstrip slideshow (5 photos visible, slides every 4s, small arrow icon indicates clickability, clicking navigates to trip) + Leaflet map of all camping locations with legend. Navy dots for campspots, gold dots for events, red house icons for home/family. Family markers show a popup listing the union of trips that stayed at that location (matched via coords) and trips that contain a family-visit event for that family (matched via `family_id`), deduped by trip id and sorted by trip start date. No redundant title between slideshow and map.
- `templates/trips_calendar.html` — Calendar and list views of trips. All calendar circles are navy blue. Switching between views is client-side (no page reload), preserving the selected year. Year selector bar is sticky below site-top. List view shows night/campspot/event counts per trip, each omitted when zero. Empty trips (no dates) are excluded from calendar dots and year range calculation but appear at the bottom of every year's list view.
- `templates/campground_map.html` — Campground map with color-coded markers by proximity to water or climate. Family-kind entries are excluded entirely from these maps. Legend is a Leaflet control (bottom-left) with clickable toggles to show/hide categories. Waterfront legend ordered: coastal dunes, coastal woods, bay, lake, lakeview, river, riverview, creek, pond, none. Climate legend ordered coldest to hottest: much cooler through hot, with "similar to home" in the middle. Popups show: name, state, elevation, visit count, note, phone numbers, websites (displayed by domain name), and an "edit" link (admin-only, bottom-right, floated) that navigates to the manage page with `?edit=<id>`. Does not show waterfront/climate fields since they are conveyed by dot color. `is_admin` is passed from both waterfront and climate routes.
- `templates/campground_manage.html` — Admin-only CRUD over campgrounds and family locations (both kinds share the table). Searchable/sortable with inline editing. A kind selector at the top of the name cell toggles between `campground` (shows waterfront/ownership/elevation/website/phone fields) and `family` (shows a driveway-location picker instead). Location, website, phone, and family driveway are sub-fields within the note column during editing. Family-kind rows show a 🏠 prefix on the name and blank cells for the campground-only columns. Leaflet map picker appears when the location or driveway input is focused; auto-fetches elevation via `/api/elevation` only for the main location input. Elevation is displayed in feet (stored as meters internally). Supports `?edit=<id>` query param to auto-open an entry for editing (param is stripped from URL after use via `history.replaceState`).

## Architecture

### Trip ID vs Display Number

Trips have two distinct identifiers:
- **`id`** — Permanent, auto-incrementing integer. Used for URLs (`/trips/42`), photo directory paths, API routes, and all internal references. Never changes once assigned.
- **`number`** — Computed dynamically in `_load_trips_json()` based on chronological sort position. Used only for display ("Trip 5: ..."). Automatically adjusts when trips are added/removed without renumbering stored data.

### Trip Types

- **Empty trips** have no campspots or events. New trips are created empty. Summary defaults to "New Trip". They have no date range and are excluded from calendar dots and header day trip count but appear in the list view.
- **Overnight trips** have at least one campspot. Header stats show overnight trip count and total nights.
- **Day trips** have only events (no campspots). A trip survives deletion of its last campspot if it still has events. Date range is derived from events when no campspots exist. Summary falls back to trip note or "Events Only".

### Data Model

- Trips contain campspots (campground visits) and events. Campspots are sorted by start date, events by date. A timeline merges both chronologically.
- When adding a new campspot or event, dates default to the trip's first campspot start date (not today's date).
- **Campspots** reference a location via `campground_id` (int, null for custom stays). When `campground_id` is null, the free-text `custom_place` field holds the display name (used for Airbnbs, hotels, and other non-campground lodging). `_make_trip()` materializes a display-only `place` string onto each stay from `campground_id` → campgrounds.json name, with `custom_place` fallback.
- Events have optional `end_date` (for multi-day events) and `location` (lat,lng string). Events with a location are plotted as gold star dots on the trip detail map and gold dots on the main trips map. The event location map picker (fixed floating panel, draggable, resizable) lets admins click to set coordinates — similar to the campground manage map picker but without elevation lookup.
- **Family visits** are events with a non-null `family_id` (int, referencing a `kind: "family"` entry in `campgrounds.json`). `_make_trip()` materializes a display-only `family_visit` label string from `family_id`. Location coordinates are auto-set from the family entry (using `driveway_location` when available). They appear as red house icons on the map (z-index 850, between stays and family markers) and have a salmon-toned card with a simplified edit form (family location dropdown, event name, date, time). The event `name` is editable separately from the family location — leaving it blank causes the save path to backfill it with the family label so the card always has a title. `onFamilyVisitChange` only overwrites the name when it looks auto-filled (blank or matches any family label), so a custom name survives a family-location change. The proximity-based family marker is suppressed for locations that have a family visit on the trip.

### Admin Protection

`_require_admin()` helper guards all mutation endpoints (upload, edit, delete, reorder, move, campground CRUD). Templates use `is_admin` Jinja variable and `IS_ADMIN` JS constant to conditionally render edit controls. Drag-drop is fully disabled for non-admins (no draggable attributes, no event listeners).

### Photo System

- Photo metadata (captions, ordering) is stored separately from the files themselves.
- EXIF date taken is extracted via Pillow (`_photo_date_taken()`) and displayed in the lightbox viewer.
- Upload supports both individual image files and zip files containing multiple images. Zip extraction filters out directories, hidden files, and non-image files.
- Drag-and-drop supports both within-grid reorder and cross-grid moves (campspot-to-campspot, campspot-to-event, etc.). Cross-grid moves call `POST /trips/<id>/move-photo` which relocates the file and updates captions/order.
- Upload areas detect whether a drag is an internal photo move or an external file upload and handle accordingly. When the destination grid is empty, the upload area itself serves as the drop target for photo moves (styled with red border instead of showing a separate empty grid indicator).
- When campspots or events are sorted by date (on add/update), photo directories and caption/order JSON keys are remapped to follow the new indices via `_remap_indices_after_sort()`. This uses temporary directory names to avoid collisions during the rename.

### Campground System

- `campgrounds.json` is a unified location database holding both `kind: "campground"` and `kind: "family"` entries, each with a stable `id`. Campspots reference entries by `campground_id`, and events reference family entries by `family_id`. Because references are ID-based, renaming an entry via the management page needs no propagation logic — existing references remain valid automatically.
- Custom stays (e.g. Airbnb, hotel) use `campground_id: null` and a free-text `custom_place` field. The frontend's `stayFieldsToPayload()` decides which fields to send based on whether the place text matches a known entry.
- Campspot edit forms use an autocomplete picker that fetches from `GET /api/campgrounds` (includes both kinds). Selecting an entry stores its `id` in a hidden field and auto-fills the state field. Family-kind entries are shown with a 🏠 prefix in the dropdown. When the user types free text that matches no entry, it's saved as `custom_place`.
- `trips.py:_load_locations_by_id()` is the single source of truth for resolving IDs to coordinates — prefers `driveway_location` for family-kind entries so stay markers don't collide with the red family house marker.

### Sticky Layout

- Header and nav are wrapped in a `.site-top` sticky container (`z-index: 900`).
- A script in `base.html` sets `--site-top-height` CSS variable from the container's actual height (updates on resize).
- Child pages use `top: var(--site-top-height, 0px)` for their own sticky sub-headers (year selector, trip title bar).
- Map containers use `z-index: 0` to contain Leaflet's internal z-indices within a stacking context.

### Map Marker Color Scheme

- **Campspot markers:** Navy (`#002868`) circles/dots with white border across all maps. On trip detail maps, 24px numbered divIcons. On main trips map, circleMarkers sized by visit count.
- **Event markers:** Gold (`#c9a84c`) on all maps. Star divIcons on trip detail maps, circleMarkers on main trips map.
- **Home/family markers:** Red (`#bf0a30`) background with white house SVG icon on all maps (trip detail, trips map, campground maps).
- **Family markers on trip detail:** Only shown when a stay or event from the trip is within 80km (haversine distance).
- **Trip detail route:** Built day-by-day in chronological order. For each date in the trip: morning location (stay you woke at, or HOME) → events/waypoints sorted by time → evening location (stay you sleep at, or HOME). Events/waypoints without a time are assumed to be at noon. This creates loops on days spent at the same stay with excursions, and direct trails on travel days between stays.
- **Z-index layering on trip detail:** Home (1000) > Family (900) > Stays (800) > Events (default).
- **Trip detail popup contents:** Stay popups show place name, locale/state, nights. Event/waypoint popups show name, locale/state (when present), and date/time. Family-visit events at the same family location share one red house marker whose popup lists every visit (sorted by date/time, with custom event names appended after an em dash when distinct from the family label). The map IIFE attaches each item's original array index as `idx` (before lat/lng filtering) so popup actions can address the right slot.

### Trip Detail Layout

- When a trip has any timeline content (at least one stay or event), `.content` gets a `two-col` class and renders as a CSS grid (`minmax(0, 1.1fr) minmax(0, 1fr)`, `max-width: 1600px`): map on the left, cards on the right. Gate is `{% set has_cards = trip.timeline|length > 0 %}` — photo presence no longer matters, because the timeline always renders cards (bare or full) regardless.
- Truly empty trips (no stays, no events) fall back to the original single-column layout.
- The `.map-column` wrapper is a layout placeholder only — its inner `.map-column-fixed` is `position: fixed` so the map is anchored to the viewport (true fixed, not sticky — sticky produced visible jitter while scrolling). `syncMapColumnPosition()` reads the placeholder's `getBoundingClientRect()` and writes inline `left`/`width` on the fixed wrapper; it runs on `load` + `resize` and after `--trip-header-height` updates, but **never on scroll** (that's the whole point).
- `.map-column-fixed` holds the map container *and* the admin add-buttons (logically "where these items exist"); the `.cards-column` wrapper holds only the timeline. Both wrappers exist in single-column mode too but are visually inert.
- The fixed wrapper anchors with **both** `top: calc(var(--site-top-height) + var(--trip-header-height) + 1rem)` and `bottom: 1rem`, so the gutter above and below match. It's a `flex` column: `.map-container` is `flex: 1 1 auto` (with `margin-bottom: 0` to drop its default 1.5rem gap), `#trip-map` inside is `flex: 1 1 auto` with `min-height: 380px`, and `.add-buttons` is `flex-shrink: 0` with `margin-top: 1rem`. The map fills all available vertical space between the two 1rem gutters; on admin pages the add-buttons take their natural height at the bottom and the map shrinks accordingly.
- Single-column mode keeps the fixed 380px map height (overrides set `display: block` on the wrapper and `flex: none` on `#trip-map` so the flex fill doesn't collapse without a defined parent height).
- Below the 900px viewport breakpoint the two-col grid collapses to a single column. CSS resets `.map-column-fixed` to `position: static` (with `display: block`, `left/width: auto !important`) and `#trip-map` to `flex: none; height: 380px`. `syncMapColumnPosition()` checks the same `(max-width: 900px)` media query and clears its inline writes so the CSS reset isn't fought by stale inline styles.
- A small IIFE in the scripts block measures `.trip-header` and publishes its height as `--trip-header-height` on `document.documentElement`, re-measuring on resize. It also re-runs `syncMapColumnPosition()` and calls `window.tripMap.invalidateSize()` so Leaflet repaints when the map's box changes height.

### Trip Detail Map → Card Scrolling

- Clicking a marker on the trip-detail map auto-scrolls the cards column to the corresponding card. The popup still opens (Leaflet's default click behavior is preserved); the scroll runs alongside it via a `.on('click', ...)` handler.
- `scrollToCard(cardId)` computes the card's absolute Y from `getBoundingClientRect()`, subtracts `--site-top-height` and `--trip-header-height` (read from CSSOM with `getComputedStyle(document.documentElement).getPropertyValue(...)`) plus a 16px gap, and calls `window.scrollTo({ behavior: 'smooth' })`. It silently no-ops when the card element doesn't exist (e.g. waypoints with no photos).
- Card IDs follow `stay-{idx}` and `event-{idx}` (matching the Jinja template). For grouped family-visit markers, the click handler picks the first visit in the sorted group whose card actually rendered (`sorted.find(e => document.getElementById('event-' + e.idx))`).
- The home marker click scrolls to `#home-card-start` (the start-of-timeline bare home card), effectively snapping the cards column back to the top.

### Trip Detail Timeline Cards

- Stay cards and regular (non-waypoint, non-family-visit) event cards always render in the timeline, with or without photos — they're the primary narrative frames for the trip.
- **Split multi-night stays**: when a stay spans more than one night AND at least one event/waypoint/family-visit falls on a *strictly interior* day (i.e., `arrival < event_date < departure`), `_make_trip()` emits one timeline copy per night. Each copy carries `copy_num` (1-indexed) and `copy_count`, and sorts at `(arrival + copy_num - 1, _order=1, _time="23:59")` so daytime events on the following day still slot before the next copy. Unsplit stays keep the original `_time="00:00"` sort and get `copy_num=1, copy_count=1`. Single-night stays never split.
- **Per-copy photo bucketing**: the `trip_detail` view attaches `item["photos"]` to each stay timeline item. For copy_count > 1, each copy is represented by `(arrival + copy_num - 1) at 20:00` and every photo's full EXIF timestamp (via `_photo_datetime_taken()`) is compared to every rep time; the closest wins (earlier on ties). Photos without a timestamp fall into copy 1. The existing `date_taken` field on photo dicts (YYYY-MM-DD only) is still exposed to the template for lightbox display; `_photo_datetime_taken()` is a parallel helper returning the full `datetime` for bucketing purposes.
- **Copy-aware template**: the stay card's DOM id is `stay-{idx}` for copy 1 (preserving marker-scroll behavior) and `stay-{idx}-{N}` for copies 2+. The inline edit form + Edit button render only on copy 1 (to avoid duplicate `stay-edit-{idx}` IDs), as do the stay details, campers, notes, and the "Remove All Photos" button. The whole `.stay-body` is omitted on copy 2+ when there are no photos, so later copies collapse down to just the header when they have nothing to show. Photo grids use `id="photos-{idx}"` for copy 1 and `photos-{idx}-{N}` for later copies, plus `data-stay-idx="{idx}"` on every copy so `saveGridOrder()` can concatenate filenames across all of a stay's grids and persist the full photo_order (otherwise saving one copy's reorder would wipe the others from the stored order).
- **Copy display**: the stay-meta line switches from `"{nights} nights ({start} to {end})"` to `"Night {copy_num} of {copy_count} ({sort_date})"` when `copy_count > 1`.
- Stay numbers now use `item.idx + 1` directly (since stays are already chronologically sorted by `parse_trips`), replacing the previous `stay_num` namespace so all copies of the same stay share the same number.
- **Bare cards**: waypoints and family-visits *without* photos render with a `bare` class. Jinja computes `{% set is_bare = (item.waypoint or item.family_visit) and not event_photos[item.idx] %}` and stamps it onto the class list. Bare cards have transparent background, no box-shadow, no border, no body, and the Edit button is hidden — they're just the colored circle and the header text. Admins edit bare items via the map popup's Edit button.
- **Home cards**: a `.event-card.bare.home-card` renders at the start and end of the timeline (only when `trip.timeline` is non-empty). They reuse the event-card markup with the red-house SVG inside `.event-icon.home-icon`. Meta line is `Reston, VA — {date}` using `trip.start` and `trip.end` respectively. They're purely structural — no edit/upload affordances.
- **Vertical axis & timeline line**: every timeline circle (stay-number, event-icon across waypoint/family-visit/regular/home) is 2rem × 2rem and sits inside a header with `padding: 1rem 1.25rem`, so the circle center is always at X=2.25rem and Y=2rem from the card edge. A `.cards-column::before` pseudo-element draws a 2px gray line at `left: calc(2.25rem - 1px)` from `top: 2rem` to `bottom: 2rem` (threading through the first and last circle centers). Stacking: line `z-index: 0` on the cards-column, cards `z-index: 1` (their solid background hides the line), circles `z-index: 2` (paint above the line). Bare cards are transparent so the line passes behind their text area but is broken at each opaque circle. The waypoint-specific size/padding overrides (`1.6rem` icon, `.75rem 1rem` header padding) were removed to achieve this uniform alignment.

### Trip Detail Editing UX

- The timeline acts as the photo-bearing narrative. Admin actions (edit, upload) are also available directly from every map popup — see below — so items that render as bare cards (or have no photos yet) are still fully editable without any inline UI inside the card.
- Map popups are the primary admin control surface. Each stay, event, waypoint, and family-visit popup gets admin-only **Edit** and **Upload Photos** buttons via the `popupAdminActions(editKind, idx, uploadKind)` helper inside the map IIFE. Home and family-only (no events) popups have no admin actions because those aren't trip items.
- Editing flows through a single shared modal. `openAddModal(kind)` and `openEditModal(kind, idx)` both call `_openModal(kind, mode, idx)`, which renders the form via `_modalFormHtml(kind, values)` (pre-filled in edit mode) and toggles a Delete button. `submitAddModal()` switches POST/PUT on `addModalMode`. The modal event/waypoint form includes a Waypoint checkbox so admins can flip event ↔ waypoint without going through a card.
- `uploadFromPopup(kind, idx)` creates a hidden `<input type="file" multiple accept="image/*,.zip">`, posts each file to the existing `/upload` endpoint with field name `photo`, then `location.reload()`s once all complete. After reload the card appears as a frame for the freshly uploaded photos.
- Cards-with-photos retain the original inline edit form (`editStay`/`editEvent` reveal `stay-edit-{idx}` / `event-edit-{idx}` blocks). Both the inline path and the modal path are wired to the same backing API endpoints.

### Map Picker Popup

Shared across campground manage and event location picker via `static/map-picker.js` and `static/map-picker.css`. Features:
- `createMapPicker(opts)` factory returns `{show, hide, panTo}`
- Click-to-pick coordinates with callback
- Draggable by header, resizable via edge/corner handles (min 280x250)
- Geocode search bar using `/api/geocode` (Nominatim proxy) — searches zoom the map but don't auto-set coordinates
- Street/satellite layer toggle

### Map Satellite Views

All Leaflet maps offer a satellite layer that includes three Esri tile layers: World_Imagery (base), World_Boundaries_and_Places (labels), and World_Transportation (roads). This applies to trip detail, trips map, campground map, and campground manage templates.

## API Routes

### Trip/Campspot/Event CRUD
- `POST /api/trips` — create trip (empty, no default campspot)
- `PUT/DELETE /api/trips/<id>` — update/delete trip
- `POST /api/trips/<id>/stays` — add campspot
- `PUT/DELETE /api/trips/<id>/stays/<idx>` — update/delete campspot
- `POST /api/trips/<id>/events` — add event
- `PUT/DELETE /api/trips/<id>/events/<idx>` — update/delete event

### Photo Operations
- `POST /trips/<id>/stays/<idx>/upload` — upload campspot photo or zip file
- `POST /trips/<id>/events/<idx>/upload` — upload event photo or zip file
- `POST /trips/<id>/stays/<idx>/reorder` — reorder campspot photos
- `POST /trips/<id>/events/<idx>/reorder` — reorder event photos
- `POST /trips/<id>/move-photo` — move photo between campspots/events (body: filename, src_type, src_idx, dst_type, dst_idx)
- `POST /trips/<id>/stays/<idx>/caption` — save campspot photo caption
- `POST /trips/<id>/events/<idx>/caption` — save event photo caption
- `DELETE /trips/<id>/stays/<idx>/photos/<file>` — delete campspot photo
- `DELETE /trips/<id>/events/<idx>/photos/<file>` — delete event photo

### Campground CRUD
- `GET /api/campgrounds` — lightweight `{id, name, state, kind}` list (for autocomplete picker; includes both kinds)
- `GET /api/campgrounds/all` — full data (admin, for management page)
- `POST /api/campgrounds` — create entry (auto-assigns next id; accepts `kind`; family entries may carry `driveway_location`)
- `PUT /api/campgrounds/<int:id>` — update entry by id (no name-propagation needed; references are id-based)
- `DELETE /api/campgrounds/<int:id>` — delete entry by id
- `GET /api/elevation?lat=X&lng=Y` — proxy to Open-Elevation API, returns `{elevation_meters}`
- `GET /api/geocode?q=X` — proxy to Nominatim geocoding API, returns `[{name, lat, lon}]`

## Conventions

- Private Python functions prefixed with `_`
- Routes organized by section with comment headers in `ekko_trips_app.py`
- Photo keys use format `{trip_id}/{stay_idx}/{filename}` (campspots) or `{trip_id}/events/{event_idx}/{filename}` (events)
- Photo order keys: `{trip_id}/{stay_idx}` or `{trip_id}/events/{event_idx}`
- Trip IDs are permanent auto-incrementing integers; display numbers are computed from chronological position
- No frontend build step — all JS/CSS is inline in templates except shared map picker (`static/map-picker.js`, `static/map-picker.css`)
- The data model uses "stays" internally (code, JSON keys, API routes) but the user-facing term is "campspot/campspots"
- The waterfront field in data is called "waterfront" but displayed to users as "Proximity to Water"
- Pluralization: all counters use singular when count is exactly 1, plural otherwise (including 0). In JS use `!== 1`, in Jinja use `== 1`. Never use `> 1` as it mishandles zero.
- Jinja `tojson` is configured with `sort_keys: False` to preserve Python dict insertion order (important for legend ordering)
