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
- `campgrounds.json` — Unified location database (~1,100 entries). Each entry has `id` (stable auto-incrementing int), `kind` ("campground" or "family"), `name`, `location` ("lat,lng"), `state`. Campground-kind also carries `elevation_meters`, `waterfront`, `ownership`, `website`, `note`, `phone`, `stays`. Family-kind may carry `driveway_location` ("lat,lng") used instead of `location` for stay-marker placement.
- `static/map-picker.js` — Shared map picker popup factory (`createMapPicker()`) used by campground manage and event location picker
- `static/map-picker.css` — Shared map picker styles (positioning, resize handles, geocode search dropdown)

### Templates

- `templates/base.html` — Sticky header+nav in `.site-top`. Publishes `--site-top-height` for child pages' sticky sub-headers. Nav groups: Trips (Map, Calendar, List), Campgrounds (Map, Manage — admin-only). Header shows overnight-trip / day-trip / nights counts.
- `templates/trip_detail.html` — Trip detail (~1800 lines). Photo galleries + lightbox with EXIF date, inline + modal editing, drag-drop reorder (within and across stays/events), Leaflet map with route polyline + GPS track, prev/next nav. Sticky trip-header below site-top. Family proximity markers only render when within 80 km of a stay or event. Page-load globals (`TRIP_ID`, `IS_ADMIN`, `FIRST_STAY_DATE`, `STAYS_ALL`, `EVENTS_ALL`, `FAMILY_LOCATIONS`) are declared at the top of the inline script block so popup helpers can reference them without `const` TDZ errors.
- `templates/trips_map.html` — Photo filmstrip slideshow + Leaflet map of all locations. Family-marker popups list the union of trips that stayed at that location (coord match) and trips that contain a family-visit event there (`family_id` match), deduped and sorted by trip start.
- `templates/trips_calendar.html` — Calendar + list views, client-side toggle preserves selected year. Empty trips (no dates) are excluded from calendar dots / year-range but listed at the bottom of every year.
- `templates/campground_map.html` — Color-coded by proximity-to-water or climate. Family entries excluded. Legend is a Leaflet control with clickable toggles. Popups show name/state/elevation/visit-count/note/phone/websites + admin-only edit link to `?edit=<id>` on the manage page.
- `templates/campground_manage.html` — Admin CRUD; searchable/sortable inline editing. Kind selector toggles campground/family field sets. Map picker auto-fetches elevation from `/api/elevation` only for the main location input. Elevation displayed in feet, stored as meters. `?edit=<id>` query param auto-opens for editing then strips itself via `history.replaceState`.

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

- Trips contain campspots and events. Campspots sort by start date, events by date; the timeline merges both. New campspots/events default their date to the trip's first campspot start date.
- **Campspots** reference a location via `campground_id` (int, or null with free-text `custom_place` for hotels/Airbnbs). `_make_trip()` materializes a display-only `place` string from `campground_id` → name (with `custom_place` fallback). Optional `campsite_location` ("lat,lng") overrides the campground's listed coords when the listed coords are the office/entrance and the actual campsite is meaningfully offset. `enrich_trip_locations()` prefers `campsite_location` when set.
- **Events** have optional `end_date` and `location` (lat,lng). Plotted as gold stars on trip detail / gold dots on the main map. The event-location picker is the shared map picker without elevation lookup; the trip-detail stay edit form reuses it via `pickerTarget` for the "Pick on Map" button.
- **Family visits** are events with a non-null `family_id` (referencing a `kind: "family"` entry in `campgrounds.json`). `_make_trip()` materializes a `family_visit` label from `family_id`. Location auto-set from the family entry (preferring `driveway_location`). Rendered as red house icons (z-index 850) with salmon-toned cards and a simplified edit form. `onFamilyVisitChange` only overwrites the event `name` when it looks auto-filled (blank or matches any family label), so a custom name survives a family-location change. Proximity family markers are suppressed for locations that already have a family-visit on the trip.

### Auth & Admin Protection

Login is global via `_require_login_globally()` (registered as `before_request`); only `login` and `static` endpoints are exempt. `_require_admin()` guards all mutation endpoints. Templates condition edit controls on the `is_admin` Jinja var / `IS_ADMIN` JS constant; drag-drop is fully disabled for non-admins.

Accounts live in `users.json` (`{username: {password_hash, is_admin}}`, hashed via `werkzeug.security.generate_password_hash`). Admins manage users at `/admin/users` (`templates/users_manage.html`) backed by the `/api/users` JSON API. Self-protection rules: cannot delete your own account, cannot remove admin from your own account. CLI bootstrap: `python ekko_trips_app.py create-admin`.

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

### Campground Inclusion Criteria

Entries must be a real, publicly-bookable, drive-in RV campground usable by the family's 23-ft RV ("EKKO"). Before adding one:
- **Access:** drive-in, passable by a normal vehicle (decent dirt/gravel is fine; hardcore offroad / 4WD-required disqualifies). No pad needed (grass is fine); hookups never required.
- **RV size:** at least some drive-in sites must fit a 23-ft rig. If the largest sites cap around 20 ft, exclude — EKKO can occasionally squeeze into a 20-ft spot but we don't rely on it (barring a genuinely special case).
- **Never add:** horse/equestrian campgrounds (a general campground that merely *offers* horse sites is OK); hike-in / tent-only / boat-in / cabin-only / group-only; fairgrounds that only allow camping during events.
- **Not a real transient campground — exclude even if it technically takes overnighters:** parks that are mostly seasonal/full-timer, residential / mobile-home-park, or workforce/long-term (e.g. gas-field worker housing); membership / club / sales-pitch parks (Thousand Trails, Encore, Bluegreen, Coast-to-Coast; Elks/Moose/Airstream-club lodges; timeshare "buy-in" resorts); casino/racetrack overnight lots.
- **Dead/missing official website is a strike** — treat a campground with no working official site as suspect, especially combined with thin/no reviews; don't add unless it's otherwise well-confirmed as currently operating.
- **Unrated / thinly-reviewed needs firsthand confirmation, not a guess.** An RV Life `star_rating` of 0 means *unrated*, and few/no reviews — not automatically excluded (public/government sites are legitimately lightly reviewed), but it removes your safety net. Before adding such an entry you must confirm the basics — fee/reservation model, drive-in RV access, RV-fitting site length, amenities, currently-operating — from a firsthand or authoritative source (official/agency page, campground map/photos, a dated trip report, or a directory with real specifics). If you can't confirm those facts, **skip it** rather than inserting a placeholder you'll have to walk back.
- **Every `note` claim must be sourced — never copy aggregator boilerplate.** Listing aggregators (snoflo, camping.org, campingroadtrip, mobilerving, etc.) auto-generate generic prose like "clean restrooms, hot showers, picnic tables, fire pits… reservations are required… popular among campers." That is filler, not data — do not lift it into a `note`. Prefer the operator's own page, the reservation system, campground photos/site maps, and firsthand reports. When an aggregator's prose disagrees with its own structured fields (e.g. prose says "reservations required" but the data field says "Reservations: No"), the structured field wins.
- **First-come-first-served:** always add a `note` saying so when there's no reservation system. **Consistency gate:** if a `note` asserts "reservations required," the record must carry a real booking channel — a reservation `website` (recreation.gov / reserveamerica / a state/agency portal) or a verified `phone`. A "reservations required" claim with no booking channel is self-contradictory and almost always wrong (it's usually a free FCFS site); resolve it before inserting, don't ship the contradiction. Many USACE / federal river and reservoir areas are free, primitive, and FCFS by default — assume FCFS unless a booking channel actually exists.
- **Dispersed sites:** drive-in dispersed sites may be added when encountered, but don't go out of the way to hunt them.
- **Ownership values:** `state` (state parks, state forests/SRAs/WMAs, state-DNR areas, and interstate-compact parks like Breaks), `federal` (USACE / USFS / NPS / BLM / Reclamation), `local` (county / town / city / regional or municipal authority), `private`, `hipcamp`. State-forest campgrounds are `state`, distinct from state parks. County land run by a private concessionaire is still `local`; a utility-run campground (e.g. Brookfield/PPL) is `private`.
- **Waterfront reflects RV-accessible sites only, and an on-water value must be *earned* with site-level proof.** Riverfront/lakefront cabins or tent-only/shelter sites do NOT qualify. The standard is a burden of proof, not a vibe — follow it exactly:
  - **Default down.** The value is `not waterfront` unless positive, named evidence upgrades it. "Couldn't confirm" always resolves *down* (to `*view` or `not waterfront`), never up. Absence of confirmation is never permission.
  - **Evidence that COUNTS** (any one promotes to an on-water value): an official per-site campground map/PDF showing pads at the shoreline; a rec.gov per-site `SHORELINE SITE: Y` flag; **satellite imagery at the pinned campground coordinate showing RV pads within ~1 pad-depth of the waterline**; or a dated firsthand photo of an RV site on the water.
  - **Evidence that is FORBIDDEN as the sole basis**: marketing prose ("on the lake," "lakeside resort"); aggregator boilerplate or vague review snippets ("some sites near the water"); a brochure *overview* map (an icon merely *near* water); the campground's **name** ("Lakeview"/"Creekside"/"Riverbend"); or the mere presence of "lake/river access," a boat ramp, or a marina. A marina park whose pads sit uphill is `lakeview`/`not waterfront`, not `lakefront`.
  - **The satellite look is MANDATORY but its authority is ASYMMETRIC — it can veto, but it cannot be the sole confirmer in canopy.** Always pull the coordinate and look, but weigh it correctly: (a) when the imagery is *legible*, it is decisive and **overrides prose/brochure maps** — pads visibly set back from the water → downgrade (this is where it catches marinas, brochure-map pins, and "lake access" parks); (b) when the imagery is *illegible* — dense forest canopy, low-resolution/old base tiles, deep shade (common for Adirondack/boreal/remote sites where individual pads simply can't be resolved) — it can neither confirm nor deny, and "I couldn't see pads" is **NOT** grounds to downgrade. In that case defer to the higher-authority source: an **official per-site campground map** or **per-site reservation/`waterfront` data** is primary and a canopy-blind satellite does not override it. For established agency campgrounds (DEC/COE/USFS/NPS/state parks) that official per-site map almost always exists and is the authority — satellite is the cross-check, not the verdict. Still required: SOME qualifying source (legible-and-positive satellite, OR official per-site map, OR per-site reservation flag, OR dated firsthand photo) must confirm shoreline sites; if none does, default down.
  - **`*view` needs the same rigor** — only if some **RV** sites actually overlook water (confirmed, not assumed); else `not waterfront`.
  - **Record the proof.** Any on-water (or `*view`) designation must carry a one-line `waterfront_evidence` justification naming the artifact (e.g. "rec.gov site map: sites 12–15 on shore" / "satellite at 36.57,-93.30: pads at waterline"). In agent workflows this is a required structured-output field; a designation with no evidence string is written as `not waterfront`. Keep the evidence in the commit message / curation sidecar so a later audit is a grep, not a re-research.

### Campground Data Curation (state-by-state audit)

An ongoing effort adds campgrounds missing from `campgrounds.json`, worked systematically by state and by ownership/operator. **Git log is the progress record** — read recent commits to see which states/categories are done before continuing. Typical order per state: state (parks → forests/SRAs/WMAs) → federal (USACE / USFS / NPS) → private → local. (State + federal are largely done for VA / MD / DE / PA / WV.)

**Detection data sources (RV Life is the workhorse):**
- **RV Life** (`campgrounds.rvlife.com`) — Algolia app `H0LPZK92QJ` (search key is inline in any park page's HTML: `algoliasearch('H0LPZK92QJ', '<key>')`), index `park`. Useful fields: `price_level` (int 0–4 = number of `$` signs), `star_rating` (0–5 user rating — note `avg_rate` is the nightly price, NOT a rating), `park_type` (`commercial`/`state`/`county`/`city`/`regional`/`dnr`/`coe`/`usfs`/`national`/`military`), `cg_name`, `city_name`, `region_abbvr`, `_geoloc`. `region_abbvr` is NOT facetable — pull a state via `insideBoundingBox=[[minLat,minLng,maxLat,maxLng]]` then keep `region_abbvr == <ST>`.
- **Good Sam** — Algolia index `gs-ml-cb-assets-prod` (app `VT01MNVCP5`); search key is a 2-hour secret fetched from an AppSync `getCampgroundSearchAuthSecret` query (use Python `urllib` for the POST — the sandbox blocks `curl` POST). Carries triple ratings and a `campground.type` `MEMBERSHIP_PARK` flag (unreliable — confirm membership independently).

**Private (commercial) campgrounds:** add only if RV Life `price_level` ≤ 2 ($ or $$) AND `star_rating` ≥ 4 AND not a membership park; then vet each per the inclusion criteria (real transient RV campground, not seasonal/residential/workforce/club; dead-website strike) and set waterfront from the RV sites via the evidence gate (default `not waterfront`; on-water only with a satellite/site-map confirmation, never from a "lakeside"/"riverfront" name or marketing).

**Local campgrounds:** detect via RV Life `park_type` in {county, city, regional} PLUS a name-scan of the commercial/state buckets for government keywords (county / township / municipal / regional / borough) to catch mislabels (RV Life mis-tags some county/authority parks as commercial). `park_type == dnr` is a state DNR area (state, not local). Do NOT apply the ≥4★/≤$$ gate to local — public government campgrounds are inherently cheap and lightly reviewed; include any confirmed local-government drive-in RV campground and just record the RV Life star/price in the note. Confirm the operator is genuinely local government.

Mechanics:
- **id:** `max(existing id) + 1`; ids are permanent and never reused.
- **Append, don't re-dump:** append entries preserving the file's 2-space indentation; never rewrite the whole file (a full `json.dump` reorders keys / reformats floats / re-escapes unicode and churns the diff). Validate with `json.load` after each batch. To remove an entry, excise just its `{ }` block by id (no braces appear inside values).
- **Fields:** `id`, `kind: "campground"`, `name`, `location` ("lat,lng"), `elevation_meters`, `state`, `ownership`, `waterfront`, `website`, `phone`, `note`.
- **Coordinates:** pin `location` to the actual campground, not the park HQ/entrance — verify via allstays / recreation.gov / reserveamerica / campsitephotos / official campground-map PDFs (RV Life `_geoloc` is often off by several km).
- **Elevation:** Open-Meteo DEM — `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lng>` (comma-separated lists for batch); store meters in `elevation_meters`.
- **`waterfront` vocabulary:** on-water `lakefront`/`riverfront`/`creekside`/`pond`/`bayfront` (+ `coastal woods`/`coastal dunes`); view-only `lakeview`/`riverview`/`bayview`; else `not waterfront`. Any non-`not waterfront` value must clear the **evidence gate** in the inclusion-criteria "Waterfront" bullet above (default-down, forbidden sources, mandatory satellite look, recorded `waterfront_evidence`) — never assign from name/marketing/reviews alone.
- **Confirm the campground & operator:** reservation directories also list day-use, cabin-only, group, and boat-in/hike-in facilities — verify a drive-in RV campground before adding. Many reservoirs have a USACE dam but state- or USFS-run campgrounds — credit the actual operator, not the dam owner. Don't fabricate phone numbers — verify or omit.
- **Note attribution:** the `note` is a shared record. When editing a note already tagged with someone's initials (e.g. `--AWH`), keep their text intact and append your change as a distinct segment with your own marker (`--Claude`); don't fold your edits into theirs.
- **URLs belong in `website`, not `note`.** The reservation/official site (recreation.gov, reserveamerica, a state/agency portal, the campground's own domain) goes in the `website` field — newline-separated if several, deduped by domain. Keep website URLs out of `note` prose: write "Reservable online" rather than "Reservable via recreation.gov". Two exceptions stay as prose: a *negative* reservation fact ("FCFS — not on recreation.gov", "book via Campspot, not recreation.gov") and a dead/suspect official domain recorded as a caveat. Source citations (a blog/listicle/video the recommendation came from, e.g. a `campingprepper.com` page) are attributions, not the campground's site — don't move them into `website`; de-URL to a bare name if practical.
- **Prefer deep, campground-specific URLs** over generic portal homepages, and ideally carry BOTH the official park page AND a direct deep reservation link (so booking is one click, no hunting). Deep formats: recreation.gov → `/camping/campgrounds/<id>`; ReserveAmerica → `.../campgroundDetails.do?contractCode=XX&parkId=<id>` or `/explore/<park>/<ST>/<id>/<unit>/campsite-booking`; **US eDirect portals (ReserveOhio, ReserveFlorida, ReserveCalifornia)** → `<frontend>/#!park/<PlaceId>` where PlaceId comes from the citypark API: ReserveOhio `https://ohiordr.usedirect.com/Ohiordr/rdr/fd/citypark`, ReserveFlorida `https://floridardr.usedirect.com/FloridaRDR/rdr/fd/citypark` (each record has `Name`/`Latitude`/`Longitude`/`PlaceId`; match by name+geo). Frontends: ReserveOhio `https://reserveohio.com/OhioCampWeb/#!park/<id>`, ReserveFlorida `https://reserve.floridastateparks.org/Web/#!park/<id>`. Note: `camp.in.gov` redirects to ReserveAmerica (`indianastateparks.reserveamerica.com`), and `goingtocamp` (WI) is Aspira — neither has the clean US eDirect API. **Illinois (ExploreMoreIL)** migrated to a Tyler backend and its OLD `camp.exploremoreil.com/location/<id>` deep links are DEAD (every path 302-redirects to the homepage — don't use them, and fix any you find). Current working format: `https://recreation.exploremoreil.com/IllinoisWeb/Default.aspx#!park/<PlaceId>` (hash route, no redirect). The citypark API is `https://il-rdr.recreation-management.tylerapp.com/IllinoisRDR/rdr/fd/citypark` (`EntityType=="Park"` records carry `Name`/`PlaceId`/geo; its `apiurl` base is inline in the `camp.exploremoreil.com/` HTML). **Verify per-park, not just via the API:** the API lists a park if ANYTHING there is reservable (camping/cabin/shelter), and its place-info URLs have collisions — confirm by fetching the park's own DNR page (`dnr.illinois.gov/parks/camp/park.<slug>.html` or the `dnrhistoric.illinois.gov` site page) and reading the real `#!park/<id>` it links. A DNR camp page that shows only the boilerplate `#!park/3` (Illinois Beach, present on every page) means that park's camping is FCFS (e.g. Pyramid, Cave-in-Rock, Big River SF, the Illinois-River-backwater SFWAs). See [[reference_usedirect_deep_reservation_links]].
- **Git:** commit campground edits directly to `master` (solo data repo; no feature branch unless asked); push only when asked — the user typically runs `! git push origin master` themselves.

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
- **Trip detail straight-line route:** built day-by-day. For each date: morning location (stay you woke at, or HOME) → events/waypoints sorted by time (untimed = noon) → evening location (stay you sleep at, or HOME). Loops on excursion days, direct trails on travel days. Drawn as the dashed `#002868` "Straight route" overlay; removed from the map automatically when the GPS track renders.
- **Auto-fallback to straight track:** when the GPS data doesn't actually cover the trip, the GPS layer is silently skipped and the dashed straight-line route stays as the only polyline. Triggered when the `/track` fetch fails/returns nothing in-window, or a strict (completed trips) / relaxed (in-progress trips) anchor-proximity gate fails. There is no manual "force straight" toggle — these heuristics are the only mechanism. Full gate logic and the trip-61 / trip-90 rationale are in the comment above the gate in `trip_detail.html` (search `Auto-fallback: skip the GPS layer`). (Older `trips.json` entries may still carry a vestigial `force_straight_route: true`; it is read by nothing and survives only until the trip is next saved.)
- **GPS track overlay:** `/api/trips/<id>/track` fetches OwnTracks-style points from a timeline service (`TIMELINE_API_TOKEN` + primary `TIMELINE_TID`, optional `TIMELINE_TID_ALT`). When alt is configured, the endpoint fetches BOTH tids over the trip window and stamps each ping with `tid: "primary"|"alt"`; `_select_track_per_day` then picks one tid per day (see "Per-day tid selection" below). Cached on disk at `trip_data/track_cache/<id>.json`; trips ended >7 days ago serve from cache permanently. Legacy untagged caches stamp `tid: "primary"` on read (one-shot migration). Spurious pings (cell-tower fixes, single jumps) are filtered upstream by a separate pre-processing app. Server-side `_enrich_with_timezone()` (optional `timezonefinder` dep, idempotent on cache read) attaches per-ping IANA `tz` so the per-point markers' popups can show local-at-recording-location time.
- **Per-day tid selection (`_select_track_per_day`):** when both tids are configured, the endpoint picks one tid per day for the trip window (anchor-encounter count as the proxy for "which phone traced the trip today", with override / single-tid / continuity / day-1 fallbacks). The full per-day algorithm (cases A–E), the cleaned-view-decides / raw-points-filter split, and the pad-day handling are documented in the `_select_track_per_day` docstring. Shared with `_load_trip_track_for_detection` so detect-stops and the polyline see the same chosen pings.
- **Admin tid override (`tid_overrides`):** trip-level dict `{"YYYY-MM-DD": "primary"|"alt"}` that forces the selector's choice for that day regardless of the heuristic. The Track Source modal on trip detail (admin-only desktop button next to Detect Stops) lists each trip day with the auto pick + per-tid ping counts + a radio for [auto / force primary / force alt]; Save PUTs diffs to `/api/trips/<id>/tid-overrides` and refetches the polyline. The "Force alt" radio is disabled when `TIMELINE_TID_ALT` is unset.
- **Manual ping overrides (admin):** trips carry three optional override lists, all applied server-side in `_apply_overrides` inside `api_trip_track` (see that function's comments for exact behavior): `suppressed_pings: [tst,...]` (dropped from the track; gray dashed ghost layer for admins), `relocated_pings: [{tst,lat,lon},...]` (lat/lon rewritten so the polyline follows; amber ghost layer with a line back to the original), and `bad_track_windows: [{start,end,note},...]` (off-trip time ranges as local-time `"YYYY-MM-DDTHH:MM"` strings interpreted in the home tz via `_trip_local_to_tst`, whose pings are dropped). Admin clients pass `?admin=1` to get pings tagged (`suppressed`/`relocated`/`bad_window` + `original_lat`/`original_lon`) instead of filtered/rewritten silently, powering the click-to-undo ghost layers; cache stays raw, overrides computed on serve. Detect-stops applies the same overrides via `_load_trip_track_for_detection`. The suppress/relocate UI (Select-pings toolbar: Suppress, Center selected, drag-to-move) lives in `trip_detail.html`; `bad_track_windows` has no UI — edit trips.json by hand. The polyline gap-fills the resulting holes through the trip's anchors (see "Frontend track rendering") rather than drawing a straight line across. Endpoints under API Routes.
- **Frontend track rendering:** the GPS overlay is the polyline of every returned ping inside the trip window (sorted by timestamp). The window's lower bound is `HOME_START_TIME` (manual) / the server-provided `home_auto_start_tst` (from `_find_home_boundary_tsts`, in the `/track` payload) / start of `TRIP_START` local day, in that order; upper bound mirrors with `HOME_END_TIME` / `home_auto_end_tst` / start of the day after `TRIP_END`. Pings outside that window are dropped from both the polyline and the per-point markers. No blackout/radius suppression. Markers for stays, events, home, and family render independently of the polyline. The polyline also gap-fills uncovered periods with the day-by-day route anchors (`routeStops`, gated by `GAP_FILL_MIN_S` for interior gaps) and pads one ping outside each cut for the "leaving/arriving home" legs (gated by `BOUNDARY_PAD_MAX_S`); the mechanics and the trip-87 rationale live in the `Gap-fill the polyline` / boundary-pad comments in `trip_detail.html`. When the GPS track loads, the dashed straight-line route is removed from the map (still toggleable via the layer control).
- **Per-point GPS markers:** each ping also gets a small clickable circle (radius 3) inside `gpsPointLayer`, hidden until zoom ≥ `GPS_POINT_MIN_ZOOM` (14). Click shows local-at-ping time and lat/lng. Toggling the GPS track in the layer control also toggles the dots.
- **Z-index layering on trip detail:** the suppressed/relocated override ghost layers render in a dedicated `overrides` pane (zIndex 700) above Leaflet's markerPane (zIndex 600) so the admin can always click through to unsuppress/unrelocate even when the override sits at the same coords as a stay or family marker. Within markerPane the divIcon ordering is Home (1000) > Family (900) > Stays (800) > Events (default).
- **Trip detail markers have no popups.** Clicks scroll to the corresponding card (see "Trip Detail Map → Card Scrolling"). Family-visit events at the same family location collapse into one shared marker via `familyVisitGroups`; its click scrolls to the earliest visit's card.

### Trip Detail Layout

Two-column grid (map left, cards right) when `trip.timeline` is non-empty; single-column when truly empty. The map column uses `position: fixed` (not sticky — sticky jitters during scroll); `syncMapColumnPosition()` mirrors the placeholder's `left`/`width` onto the fixed wrapper on load/resize/header-height-change but **never on scroll**. A `.trip-header`-measuring IIFE publishes `--trip-header-height` so the fixed map can anchor below it. Below the 900 px breakpoint the grid collapses to one column and `syncMapColumnPosition()` clears its inline writes so CSS resets aren't fought.

### Trip Detail Map → Card Scrolling

Clicking a marker scrolls the cards column to the corresponding card via `scrollToCard(cardId)`, which subtracts `--site-top-height` and `--trip-header-height` plus a 16 px gap from the card's `getBoundingClientRect()` Y. Card IDs: `stay-{idx}`, `event-{idx}`, `#home-card-start` (home start). Grouped family-visit markers pick the first sorted visit whose card actually rendered.

### Trip Detail Timeline Cards

- Stay cards always render with a body. Event cards (regular events, waypoints, family-visits) go `.bare` whenever there's nothing to put in the body — i.e., the card has no photos AND either it's a waypoint/family-visit OR its description is empty. Bare cards render as just the colored circle + header, transparent background, no body. The "Upload Photos" button stays visible; admins also get an Edit button that opens the shared modal. The body still exists in the DOM for admins so the photo-grid can serve as a cross-card drop target — `body.photo-dragging .event-card.bare .event-body` reveals it absolutely-positioned during a drag without shifting layout. **The cross-grid drop handler keeps `.bare` in sync with the photo count on both sides of the move**: when a photo lands on a bare card the handler removes `.bare` (and reveals the previously-hidden "Remove All Photos" button) so the body stays visible after `dragend` clears `photo-dragging`; symmetrically, when the source card is left with no photos it re-applies `.bare` (and re-hides the button) using the same predicate the Jinja template uses on initial render — waypoint/family-visit OR no description. Without that pairing a dragged-out last photo would leave the source body sitting open and empty, and a dropped-in photo would disappear the moment the drag ended.
- **Split multi-night stays**: when a stay spans multiple nights AND at least one event falls on a *strictly interior* day (`arrival < date < departure`), `_make_trip()` emits one timeline copy per night. Each copy carries `copy_num`/`copy_count`. Photo bucketing assigns each photo to the closest-by-EXIF-time copy (rep time = `(arrival + copy_num - 1) at 20:00`); photos without EXIF time fall into copy 1. Copy 1 keeps DOM id `stay-{idx}`; copies 2+ use `stay-{idx}-{N}`. Inline edit form, stay details, campers, notes, and "Remove All Photos" render only on copy 1. Photo grids carry `data-stay-idx="{idx}"` on every copy so `saveGridOrder()` can concatenate filenames across all grids belonging to one stay.
- **Home cards**: `.event-card.bare.home-card` renders at the start and end of the timeline. The `.home-time-display` span shows the manual `home_start_time`/`home_end_time` (server-rendered) when set, else the GPS-derived time appended client-side as `· HH:MM (auto)` for admins or `· HH:MM` otherwise. The auto time is the `home_auto_start_tst`/`home_auto_end_tst` the `/track` response carries (computed by the Python `_find_home_boundary_tsts`); the client only formats and displays it, it doesn't recompute it. Admin Edit prompts are framed as overrides ("GPS-derived time is X; set a manual override only if that looks wrong").
- **Vertical timeline axis**: all timeline circles are 2 rem × 2 rem inside a header with `padding: 1rem 1.25rem`, so the circle center is always at X = 2.25 rem. A `.cards-column::before` pseudo draws a 2 px gray line through those centers; cards (`z-index: 1`) hide the line behind their backgrounds, circles (`z-index: 2`) paint above. Bare cards are transparent so the line shows through.

### Trip Detail Editing UX

- Admin **Edit** and **Upload Photos** buttons live in `.card-actions` (flex sibling of `.stay-info` / `.event-info` in the card header). Desktop: top-right; mobile: drop to row 2 via grid-area `actions`. **Remove All Photos** sits inside `.photos-section` with `align-self: flex-end`. Stay cards render these buttons on copy 1 only.
- Editing paths:
  - Non-bare cards (with photos) use inline edit: `editStay(idx)` / `editEvent(idx)` reveals the `stay-edit-{idx}` / `event-edit-{idx}` block.
  - Bare cards (waypoints / family-visits without photos) and Add buttons use a shared modal: `openAddModal(kind)` / `openEditModal(kind, idx)` → `_openModal(kind, mode, idx)` → form via `_modalFormHtml()`. The event/waypoint form includes a Waypoint checkbox so admins can flip event ↔ waypoint without going through a card.
  - Home cards are structural — no edit/upload controls (manual override is set via the home-card time prompt).
- Both inline and modal paths hit the same backing API endpoints.

### Stop Detection (Admin)

Admin + desktop-only feature on the trip detail page. The **Detect Stops** button in `.trip-header` scans the trip's GPS track for dwell-time clusters not already represented by a stay/event/family location, classifies each as a waypoint (≤30 min) or event (longer), and returns them as advisory suggestions; the admin's selection is POSTed to `/api/trips/<id>/accept-stops`, which creates each via `add_event` with `needs_vetting: true` forced on server-side. Reverse-geocoding runs client-side (1 req/sec, Nominatim policy) with a progress banner and the "Create selected" button disabled until it finishes; closing the modal aborts the run via `AbortController`.

**On-road auto-uncheck:** `_reverse_geocode` returns `on_road: true` when Nominatim's primary hit is `class=highway` with `type in _ON_ROAD_HIGHWAY_TYPES` (motorway/trunk/primary/secondary/tertiary/residential/unclassified/living_street/road + `_link` variants — excludes `service`, `track`, footways). Detect-stops rows tagged this way render dimmed with an "on road · likely traffic" tag and the checkbox defaults to unchecked; the centroid being in the roadway is almost always a traffic jam / stop light rather than a real stop. The signal is free — read off the existing reverse-geocode response, no extra request. Admin can still opt-in by re-checking the box.

**Per-row mini-map:** each detect-stops row carries a small satellite-imagery preview (Esri World_Imagery, 110×80 px) fit to the cluster's ping polyline with a red centroid marker, so the admin can see at a glance whether the cluster sits in a parking lot, at a pull-off, or on a road. The endpoint returns `display.coords` (per-ping lat/lng list) for the cluster; `_initStopMiniMap` in `trip_detail.html` draws the Leaflet map. Lazy-init via IntersectionObserver — 20+ rows would otherwise spin up 20 maps at once for the ~5–8 visible at a time. Re-init on geocoding re-render (rows whose map was already live get an immediate re-init so the visible map doesn't blink empty); not-yet-initialized rows get re-observed. All instances are `.remove()`-d in `closeDetectStops`.

The full pipeline — cluster radius/duration tunables and their calibration, suppressed/relocated exclusion, trip-window narrowing, at-home/near-home classification, anchor-aware streak selection, manual-override precedence, and the known-location/at-home drops (incl. the trip-61/62/87 rationale) — is documented in code, not duplicated here: see the constant comments (`STOP_*`) and the docstrings/comments on `_detect_stops`, `_load_trip_track_for_detection`, `_find_home_boundary_tsts`, `_drop_stops_at_known_locations`, and `api_detect_stops` in `ekko_trips_app.py`.

`needs_vetting` is a boolean field on events. `true` items render with a dashed amber outline and a "Needs review" badge on the timeline card, plus a dashed amber ring on the map marker — mirroring on every surface so the admin can find them. The flag is cleared by *any* PUT to the event: both the inline and modal save handlers inject `needs_vetting: false` into the payload, so simply opening + saving the edit form is the act of vetting. The field defaults to `false` in `_make_trip()` for older trip records that predate the field, so existing data renders unchanged. Tunables (radius/duration constants) live at module level in `ekko_trips_app.py` near the helpers.

**Trip-boundary calculation has one implementation.** `_find_home_boundary_tsts()` in `ekko_trips_app.py` is the sole home-boundary detector (its docstring carries the full algorithm and the SINGLE-SOURCE-OF-TRUTH contract). It feeds two consumers: (1) `api_trip_track` returns `home_auto_start_tst` / `home_auto_end_tst` in the `/track` payload, which the frontend uses for both the polyline window cuts (`computeTripWindow`) and the home card's "(auto)" time — the frontend never recomputes; (2) detect-stops calls it directly. Manual `trip.home_start_time` / `trip.home_end_time` win over the auto values on both. **Do not reintroduce a JS reimplementation** — a prior one (`findHomeBoundaryTimes`) drifted and was deleted. The constants (`STOP_NEAR_HOME_M`, `STOP_AT_HOME_CENTROID_M`, `STOP_HOME_BOUNDARY_LOCK_S`, `TRACK_NEAR_STAY_KM`) live only on the Python side.

### Map Picker Popup

Shared across campground manage and event location picker via `static/map-picker.js` and `static/map-picker.css`. Features:
- `createMapPicker(opts)` factory returns `{show, hide, panTo}`
- Click-to-pick coordinates with callback
- Draggable by header, resizable via edge/corner handles (min 280x250)
- Geocode search bar using `/api/geocode` (Nominatim proxy) — selecting a result places a marker, fires `onPick`, and zooms to level 16
- 📍 Current-location button (auto-injected next to the search input by `createMapPicker`) calls `navigator.geolocation.getCurrentPosition`, places a marker, fires `onPick`, and zooms to level 17. Geolocation requires a secure origin — see "Local HTTPS" below.
- Street/satellite layer toggle
- On viewports `≤ 700px`, the picker fills the screen (`top/left/right/bottom: .5rem !important`) and drag/resize affordances are disabled — touch UX, not draggable.

### Map Satellite Views

All Leaflet maps offer a satellite layer that includes three Esri tile layers: World_Imagery (base), World_Boundaries_and_Places (labels), and World_Transportation (roads). This applies to trip detail, trips map, campground map, and campground manage templates.

### Responsive / Mobile Design

Single mobile breakpoint at `max-width: 700px`; trips map has an extra `max-width: 900px` breakpoint for filmstrip reflow. Each template owns its own mobile rules — see those CSS blocks for specifics. Notable behaviors:

- **Header:** `☰` hamburger toggles `.open` on `<nav>` ≤ 700 px; toggle handler re-publishes `--site-top-height` so sticky sub-headers reflow. Header stats stack vertically on mobile.
- **Trip detail header:** on mobile, `.meta` is hidden and the `<h1>` itself is tappable to edit (with a viewport check so desktop text-selection still works). `.trip-nav` (prev/next trip chevrons) stays visible at reduced size, flanking the title.
- **Modal form-grid items:** carry `min-width: 0` so `<input type="time">` and time-range pairs don't overflow. ≤ 600 px collapses to one column. The waypoint checkbox is excluded from the global `width: 100%` input rule.
- **Leaflet popups:** ≤ 700 px forces popup content to near-viewport width via `!important` overrides on `.leaflet-popup-content` (Leaflet caps content at its measured width otherwise). Desktop popup `maxWidth` is 420 on trips/campground maps so trip-link rows fit on one line.

### Local HTTPS

`ekko_trips_app.py`'s dev runner defaults to `app.run(ssl_context='adhoc')`, which generates a fresh self-signed cert each launch. This is required for browser features that need a secure origin — most importantly the Geolocation API used by the map picker's 📍 button. Pass `--http` on the command line to fall back to plain HTTP. The `adhoc` context requires `pyopenssl` in the venv. Production hosts (PythonAnywhere) handle TLS at the platform level and ignore this code path.

## API Routes

### Trip/Campspot/Event CRUD
- `POST /api/trips` — create trip (empty, no default campspot)
- `PUT/DELETE /api/trips/<id>` — update/delete trip
- `POST /api/trips/<id>/stays` — add campspot
- `PUT/DELETE /api/trips/<id>/stays/<idx>` — update/delete campspot
- `POST /api/trips/<id>/events` — add event
- `PUT/DELETE /api/trips/<id>/events/<idx>` — update/delete event
- `GET /api/trips/<id>/track[?admin=1]` — returns `{points: [...], home_auto_start_tst, home_auto_end_tst}`. `points` is the GPS track; the two tsts are the auto-detected trip boundary from `_find_home_boundary_tsts` (single source of truth for the polyline window + home-card "(auto)" time; either may be `null`). Degenerate cases (trip has no dates, or no API token and no cache) still return a bare `[]` array, which the frontend treats as no points + no boundary. Admin pages pass `admin=1` so each ping carries `suppressed`/`relocated` flags + `original_lat`/`original_lon` for relocated pings (instead of being filtered/silently rewritten); the boundary is computed on the cleaned view regardless of the flag, so every viewer gets the same window
- `POST/DELETE /api/trips/<id>/suppress-pings` — mark / unmark `tst`s as suppressed (body `{tst: [...]}`); idempotent
- `POST /api/trips/<id>/relocate-pings` — set lat/lon overrides (body `{items: [{tst, lat, lon}, ...]}`); replaces existing entries by `tst`
- `DELETE /api/trips/<id>/relocate-pings` — clear overrides (body `{tst: [...]}`)
- `PUT /api/trips/<id>/tid-overrides` — admin-only; body `{date: "YYYY-MM-DD", value: "primary"|"alt"|null}`. `null` clears that day's override. Returns the resulting overrides dict.
- `GET /api/trips/<id>/tid-choices` — admin-only; returns `{tid_choices, tid_overrides, counts, alt_configured}` where `tid_choices` is what the per-day selector would pick **ignoring overrides** (so the Track Source UI can render "Auto (would pick X)"). `counts` is per-day per-tid raw ping counts.
- `POST /api/trips/<id>/detect-stops` — admin-only; scan the trip's GPS track for dwell-time clusters not already represented by a stay/event/family location. Returns a list of suggestions, each with a `display` block (for the modal) and an `event` block (the exact payload `/accept-stops` will feed into `add_event`). Reverse-geocodes one stop per second so the call can take tens of seconds.
- `POST /api/trips/<id>/accept-stops` — admin-only; body `{events: [<event payload>, ...]}`. Creates each as a new event/waypoint with `needs_vetting: true` (server always forces the flag on, regardless of payload).

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
