# EKKO Trips

A Flask web app for documenting family camping trips in an RV called "EKKO" and discovering new campgrounds.

## Project Memory (versioned, travels with the repo)

Claude Code's auto-memory normally lives outside the repo (under `~/.claude/projects/<encoded-path>/memory/`) and is per-machine — it does NOT follow a clone. This project keeps its memory **in-repo and git-tracked** so a fresh `git clone`/`pull` + starting Claude brings it down automatically, with no manual setup:

- **`.claude/memory/`** — the committed memory files (`MEMORY.md` index + per-fact `*.md`). This is the source of truth; commit changes to it like any other code.
- **`.claude/settings.json`** sets `autoMemoryDirectory` to a fixed `~/` path (`~/.claude/memory-links/ekko-campgrounds`). That setting only accepts an absolute/`~/` path (no repo-relative/`$VAR`), so it can't name the repo directly.
- **`.claude/sync-memory.sh`**, run from a committed `SessionStart` hook (which gets `$CLAUDE_PROJECT_DIR`), symlinks that fixed path to `<repo>/.claude/memory` — bridging the fixed `autoMemoryDirectory` to wherever the repo is cloned. It's idempotent, migrates any stray memory written before first wiring, and prints `MEMORY.md` to stdout on the wiring event (recall insurance, since hook-vs-load order isn't guaranteed).

Net effect: clone/pull + start Claude wires memory automatically; new memories Claude writes land in `.claude/memory/`, ready to commit. The only one-time, per-machine step is accepting Claude Code's folder-trust dialog (the security gate that lets committed hooks/settings run at all) — unavoidable for any repo.

## Tech Stack

- **Backend:** Flask (Python) on port 5001, Flask-Login for auth, Pillow for EXIF
- **Frontend:** Server-side Jinja2 templates, Leaflet.js maps, vanilla JS (no framework)
- **Storage:** JSON files (no database) — `trip_data/trips.json`, `trip_data/captions.json`, `trip_data/photo_order.json`, `trip_data/photo_uploaders.json`, `trip_data/photo_favorites.json`, `trip_data/photo_people.json`, `trip_data/share_tokens.json`, `trip_data/access_log.jsonl`, `trip_data/campground_views.jsonl` (one line per campground-map popup any logged-in viewer opens — the use signal for schema phase 7)
- **Photos:** Saved to `photo_uploads/{trip_id}/{stay_idx}/` (campspots) and `photo_uploads/{trip_id}/events/{event_idx}/` (events) — a **sibling of `static/`, deliberately not inside it**. Served only through the login-gated `/photo/` and `/thumb/` routes (see "Photo System").
- **External APIs:** Open-Meteo (forecast + elevation), Nominatim (geocoding), Overpass (POI lookup), OSRM (driving routes, browser-side), RIDB + recreation.gov (federal availability), Textbelt (SMS)
- **Virtualenv:** `ekko_trips_venv/` (activate before running)

## Key Files

Nine bodies of detail that outgrew this file live in `docs/` — treat them as part of these
instructions and read them before touching that code or data: **`docs/poster.md`** (the
print/PNG poster), **`docs/gps-track.md`** (GPS tracks, trip routes, ping overrides),
**`docs/campground-curation.md`** (what earns an entry in `campgrounds.json`, the waterfront
evidence gate, the per-state sweep pipeline), and **`docs/campground-schema.md`** (the
structured amenity/booking/fee/season fields, the provenance model, the policy registry, and
the deep-merge rules the manage page's PUT must obey), and **`docs/rollups.md`** (the per-day
write-up drafter and its dossier/prose/scheduling rules), **`docs/trip-timeline.md`** (the trip detail page: timeline cards,
map↔card interaction, event time zones, driving figures, Detect Stops, times from GPS), **`docs/photos.md`** (photo
storage, serving, metadata and the people scan), **`docs/pages.md`** (per-template detail for the landing map, campground
map, photo gallery, Weather Finder and roadside stops), and **`docs/hosting.md`** (local HTTPS, backups, deploying to PA).

- `ekko_trips_app.py` — Main Flask app: routes, auth, photo endpoints, campground CRUD API, geocode proxy
- `trips.py` — Trip data CRUD, JSON persistence, trip parsing logic, location resolution via `_load_locations_by_id()`, photo index remapping on sort
- `weather_finder.py` — Forecast search engine behind the Weather Finder page and the `find_summer.py` CLI. Stdlib-only. Batches Open-Meteo requests, snaps coordinates to a ~11 km grid and caches per-cell forecasts for an hour — **the cache is load-bearing**: the free tier meters 600 LOCATIONS/minute and one 400-mile search spends most of that. Detail: `docs/pages.md`.
- **`ekko_trips_requirements.txt` / `tools_requirements.txt` — two files, deliberately.** The first is *only* what the running web app can reach (18 packages, from walking the imports of `ekko_trips_app.py` / `trips.py` / `weather_finder.py` / `ridb/`); the second adds the offline batch tools and starts with `-r ekko_trips_requirements.txt`, so one `pip install -r tools_requirements.txt` provisions everything. The split is what makes "the web app never imports cv2 / faster_whisper" checkable — never add those to the app's file. `click` must stay >= 8.4.2 because `huggingface_hub` requires it.
- `home.json` — Gitignored per-machine config. Required: `home_lat`, `home_long`, `home_altitude_meters`. Optional: `home_place_names` (see "Home Stays").
- `campgrounds.json` — The campground half of the location database (~14,300 entries), tracked in git. Each entry has `id` (stable auto-incrementing int), `kind` ("campground" or "family"), `name`, `location` ("lat,lng"), `state`. Campground-kind also carries `elevation_meters`, `waterfront`, `waterfront_evidence`, `inclusion_evidence`, `ownership`, `website`, `note`, `phone`, `stays`, plus the structured groups of `docs/campground-schema.md` (`rating`, `hookups`, `sites`, `facilities`, `season`, `booking`, `fees`, `discounts`) with their `provenance` and a `note_scan` audit record. **Read that doc before writing any of them** — absent means unknown and must never be filled with a placeholder, and the browser-bound payloads strip `waterfront_evidence` / `inclusion_evidence` / `note_scan` (`_AUDIT_EVIDENCE_FIELDS`).

- `extract_fields.py` — Reads the structured groups out of note prose via `claude-opus-5` (doc §7 phase 3). **Chunked and resumable by design:** batches of 12, four in flight, written in waves, `--limit` capping a run and SIGINT finishing the wave in flight, so a kill costs at most 48 entries and the fix is to run it again. Progress is `note_scan` on the entry — the hash of the note a scan read — **written even when the note yielded nothing**, which is what stops the ~70% of notes holding no structured fact from being re-billed every pass, and what makes editing one note requeue exactly that entry. `--report` shows what is left for free; `--dry-run` calls the model and prints proposals without writing. A group whose `provenance` says `manual`/`reported` is never overwritten, and the note itself is never edited (doc §6).
- `recgov_hookups.py` — Fills `hookups` (electric amps / water / sewer) for recreation.gov-linked campgrounds from RIDB's per-campsite catalog (doc §7). `--fetch` caches every facility's campsites to gitignored `trip_data/ridb_campsites.json` (resumable, written per facility, needs `RIDB_API_KEY`); a plain run is a free dry run, `--apply` writes. **The catalog replaces a note-derived value it disagrees with** (AWH: trust current rec.gov over the auto-generated sweep notes; `--conflicts` lists them) but never a `manual`/`reported` one, and a missing attribute is never read as "no": `electric: 0` only when every RV-bookable site is typed NONELECTRIC. **Only sites the public can use count** (AWH: a lone electric site may be the camp host's): sites named host are dropped, a few unbookable hookup sites at a bookable campground are staff pads, amperage comes from bookable sites, water/sewer need 3+ public yeses, and a catalog under 3 RV sites is a placeholder. `--retract <ref>` undoes earlier RIDB values a tightened rule no longer supports, restoring the note's. Details and the named cases: doc §7.
- `goodsam_discounts.py` — Fills `discounts.good_sam` / `discounts.military` from the Good Sam campground directory (doc §7 phase 5). `--fetch` caches the whole directory (14,993 campgrounds) to gitignored `trip_data/goodsam_parks.json` via the Algolia index behind goodsam.com; every later run matches and derives from it for free. **`isGsPark` is the flag, not presence in the index** — the index is the whole directory including national forests, and a Good Sam Park is the designation carrying the stated 10% member discount. Matching is name + coordinate with a **whole-name requirement past 800 m**: a subset name (`Camp Eagle Nest` vs `Eagle Nest Lake State Park`, 1.7 km apart) scores 1.00 and is a different place. **A `false` is written only on private/hipcamp entries** — the directory answers for public campgrounds too, but "no Good Sam discount" on a national forest is noise (AWH 2026-09-20); a `true` is written wherever found. `military` is true-only (absent is unknown). `--retract` undoes values a tightened rule no longer derives.
- `trip_data/family.json` — The family half, **gitignored** (see "Family Locations"). Same schema, `kind: "family"`; may carry `driveway_location` ("lat,lng") used instead of `location` for stay-marker placement. Merged with the above into one list by `_read_campgrounds_raw()` / `trips._load_locations_by_id()`, so readers see a single database.
- `roadside.json` — Leg-stretch stops (small-town parks, picnic areas, rest areas), deliberately separate from overnight campgrounds: their own toggleable overlay on the campground map, with admin CRUD inline there; `_roadside_view()` projects the record into the map shape. `visitor_center: true` (stored only when true) marks a **staffed travel-information point** and draws a blue ℹ marker. **Read the qualification rules in `docs/pages.md` before setting it** (a museum only if free AND handing out travel info; a fee-charging park visitor center only with the fee named in the note).
- `detect_people.py` — Batch scanner writing `trip_data/photo_people.json` (OpenCV YuNet face counts; 0 = scanned and nobody there, absent = not scanned). The web app never imports cv2 — it runs this as a subprocess on upload (`--only <keys>`). Run full scans where the whole library lives (PA); `--prune` is off by default because this machine holds a partial mirror. Detail: `docs/photos.md`.
- `process_rollups.py` — Drafts a short (≤35-word, impersonal) write-up per trip-day from a **dossier** of facts via `claude-opus-5`, writing `trip_data/day_rollups.json` (PA holds the authoritative copy; push local redrafts up). Few-shot examples are the family's own `day_notes`, chosen per day. A typed day note always outranks a draft. **Read `docs/rollups.md` before touching it** — the dossier's refusals, absent-is-not-zero mileage, the ten prose rules, terrain/elevation fields, bed-anchored clock and heading, `inputs_sig`/settle scheduling, and `audit_rollup_figures.py` all live there. Start with `--dry-run`.
- `ridb/fetch_facility.py` — recreation.gov / RIDB client: `search_facilities`, `fetch_facility`, `availability_matrix`, `DEFAULT_FIT_FT`. RIDB supplies the campsite catalog (so sites can be filtered to ones EKKO fits); the recreation.gov calendar supplies live availability. Needs `RIDB_API_KEY`.
- `static/vendor/tile-layers.js` — Shared Leaflet base-layer factory (`ekkoStreetLayer`, `ekkoSatelliteLayer`) driven by the server's `window.EKKO_TILES`, plus **`ekkoBordersLayer()`**: a state/province border overlay drawn from `static/vendor/na-borders.json` (Natural Earth 1:10m, US+Canada state lines + the US/Canada/Mexico international lines, simplified to 200 m — 172 KB, 55 KB gzipped). OSM's raster style draws admin boundaries almost invisibly at trip-planning zooms, which matters because the campground database is organized BY STATE. A static extract rather than another tile source because it costs no third-party requests, keeps the styling ours, and **works on the offline USB build**. It renders in its own `bordersPane` at z-index 350 — above tiles, below `overlayPane` (400) and `markerPane` (600) — and is `interactive: false`, so a border can never obscure or steal the click of a campground dot, route line or stay marker. The GeoJSON is fetched **lazily on first display**, so a map whose borders start off pays nothing — which is why the overlay is **offered in the layer control but OFF by default on every map** (AWH 2026-09-01). It was on by default on the campground map and trips map; the reasoning for that (this map is searched BY STATE / the lines place a trip fastest at continental framing) still holds and is why it stays offered, but the default view reads cleaner without them. `window.EKKO_BORDERS` in `base.html` carries the fingerprinted URL.
- `static/map-picker.js` — Shared map picker popup factory (`createMapPicker()`) used by campground manage and event location picker
- `static/map-picker.css` — Shared map picker styles (positioning, resize handles, geocode search dropdown)

### Templates

- `templates/base.html` — Sticky header+nav in `.site-top`, publishing `--site-top-height` for child pages' sticky sub-headers. Nav groups: Trips (Map, Calendar, List, Stats), Campgrounds (Map, Availability — hidden from Trips-only users; Weather — contributors only; Manage — admin-only), Admin (Users, Access Log). On phones a fixed bottom tab bar is primary nav, publishing `--tab-bar-height`. Defines `window.toast(message, kind, opts)` (used instead of `alert()` app-wide; `confirm()` stays for destructive actions), hover-prefetch (skips `/campgrounds/map`; off under Save-Data or 2g/3g) and service-worker registration. Detail: `docs/pages.md`.
- `templates/trip_detail.html` — Trip detail (~3,550 lines; the bulk of its JS now lives in `static/trip-detail/`). Photo galleries + lightbox with EXIF date, inline + modal editing, drag-drop reorder (within and across stays/events), Leaflet map with route polyline + GPS track, prev/next nav. Sticky trip-header below site-top. Family proximity markers only render when within 80 km of a stay or event. Page-load globals (`TRIP_ID`, `IS_ADMIN`, `FIRST_STAY_DATE`, `STAYS_ALL`, `EVENTS_ALL`, `FAMILY_LOCATIONS`) are declared at the top of the inline script block so popup helpers can reference them without `const` TDZ errors.
- `templates/trips_map.html` — Landing page: photo filmstrip slideshow (a click opens the shared lightbox; the slot stays a real link) + Leaflet map of all locations and every trip's GPS route line, with the "All N Trips" reframe pill. Family-marker popups list trips that stayed there or visited by `family_id`. Detail: `docs/pages.md`.
- `templates/trips_stats.html` — All-time aggregates, mostly from `_stats_cache` (keyed on the trips/campgrounds/home JSON mtimes). The photo count, "Most miles driven" and the contributor-only **Longest Driving Days** are computed outside it on purpose. Those driving figures and the trip page's per-day driving chip must agree; both are specified in `docs/trip-timeline.md` — read it before touching either.
- `templates/trips_calendar.html` — Calendar + list views, client-side toggle preserves selected year. Empty trips (no dates) are excluded from calendar dots / year-range but listed at the bottom of every year.
- `templates/campground_map.html` — Colored by proximity-to-water or climate; family entries draw as red house markers. A read-only legend (Color-by picker, colours + counts, shown total), a quick-filter chip row along the top above the search box (the layer icon drops below it when the row needs the width; chevrons mark chips scrolled out of view), and a **Filters** panel (side panel / phone bottom sheet: nightly rate, RV Life `$`, rating, hookups, water, climate, ownership with `wma`/`hipcamp` off by default, show temporarily closed), all synced through `applyVisibility()`. **An entry a filter can't evaluate is faded, never dropped** (schema doc §2.2). Only the rating pair, three hookup booleans and the base `rate` (+ `cad`) ride in the inline marker payload; everything else comes in the per-id popup fetch. Also hosts the 🚗 OSRM route tool. **Read `docs/pages.md` before changing its filters, popups or marker payload**; `tests/test_rating_filter.py` and `tests/test_closures.py` pin the rules.
- `templates/campground_manage.html` — Admin CRUD; searchable/sortable inline editing. Kind selector toggles campground/family field sets. Map picker auto-fetches elevation from `/api/elevation` only for the main location input. Elevation displayed in feet, stored as meters. `?edit=<id>` query param auto-opens for editing then strips itself via `history.replaceState`. Fed by `/api/campgrounds/all`, which strips the audit-evidence fields — a save can't clobber them because PUT merges from a field whitelist. That route also stamps `visit_count` (from `_campground_visits_index()`, one per visit, only on entries that have one) for the **Visited only** checkbox beside the search box; it's never saved back, since the whitelist doesn't list it.
- `templates/campground_availability.html` — Search a federal (recreation.gov) campground + date range and see which EKKO-fitting sites are open. Backed by `/api/ridb/search` and `/api/ridb/availability`; site-length filtering defaults to `DEFAULT_FIT_FT`. Campground-map popups deep-link here for `ownership: federal` entries, passing `?cg=<name>&state=<ST>` — the state is what tells the prefill which reused name it meant, and it only auto-selects on the server's `exact` flag (one result whose normalized name matches), never on a guess between two states' Big Bends.
- `templates/trips_photos.html` — The whole photo library in one gallery. **Every control is a query param**, built by `photos_href(**over)`; filtering is server-side, search matches word prefixes, photos run in the trip's own `timeline` order, and `_photo_gallery_index()` is cached against the pool object. Detail: `docs/pages.md`.
- `templates/trips_poster.html` — Print-oriented poster view of all trips (map + photo border), built from the same photo pool as the trips map. Fixed-size sheet chosen by `?size=` (standard frame sizes), all geometry computed in JS at load time against an 816px baseline, PNG export via vendored html-to-image, ranked hero deck (favorites → people → curated). **Its layout, print and export rules are full of hard-won invariants — read `docs/poster.md` before touching it.**
- `templates/users_manage.html` — Admin user CRUD **and share-link management** (create/label/revoke, plus the Trips-only toggle), backed by `/api/users` and `/api/share-links`.
- `templates/access_log.html` — Admin view of who visited which page, including share-link guests, rendered from `/api/access-log`.
- `templates/error.html` — Shared 404/500 page. Deliberately self-contained (no `base.html` extend) so it still renders when the data layer is what broke — extending base would re-run the trip-stats context processor.
- `templates/offline.html`, `templates/sw_reset.html` — Service-worker offline fallback and the SW kill-switch page; both login-exempt.
- `templates/weather_finder.html` — Contributor-only Weather Finder page (three modes, rain/waterfront filters, a by-name lookup outside the form, and a forecast map of every campground checked). **Sorting re-runs the search**, because results are capped server-side. Detail: `docs/pages.md`.

## Architecture

### Trip ID vs Display Number

Trips have two distinct identifiers:
- **`id`** — Permanent, auto-incrementing integer. Used for URLs (`/trips/42`), photo directory paths, API routes, and all internal references. Never changes once assigned.
- **`number`** — Computed dynamically in `_load_trips_json()` based on chronological sort position. Used only for display ("Trip 5: ..."). Automatically adjusts when trips are added/removed without renumbering stored data.

### Trip Types

- **Empty trips** have no campspots or events. New trips are created empty. Summary defaults to "New Trip". They have no date range and are excluded from calendar dots and header day trip count but appear in the list view.
- **Overnight trips** have at least one campspot. Header stats show overnight trip count and total nights.
- **Day trips** have only events (no campspots). A trip survives deletion of its last campspot if it still has events. Date range is derived from events when no campspots exist. Summary falls back to trip note or "Events Only".

### Home Stays

A **home stay** is a night at the family's own house rather than a campsite. Home is not a `campgrounds.json` entry — it's recorded like a hotel would be: `campground_id: null` plus a free-text `custom_place`. A trip whose campspots are *all* home stays gets `home_only: true` and is hidden from the trips map, calendar, list and landing-page photos (admins still see it), and dropped from the stats entirely.

`trips.is_home_stay(stay)` is the single rule, and `trips.camping_nights(trip)` (`total_nights` minus home stays) is how any nights aggregate must be computed — the stats hero, the Nights-by-Year chart, and the site header all go through it so they can't disagree. A mixed trip (home for a few nights mid-trip, then back out) is the only case where the two differ; there are none in the data today, which is exactly why the distinction is easy to lose.

**Because a false positive is expensive and silent** — it makes a real trip vanish from every public surface — matching is deliberately conservative:
1. **A stay with a non-null `campground_id` is never home.** Home is always free text, so this rules out every campground-name collision. It matters: the marker below is a *substring* test, and `"basset"` is a substring of **"Bassett City Park"** (id 2771, a real municipal campground in NE). Without this guard, camping there would silently bury the trip.
2. If `home.json` defines `home_place_names` (a list of strings), the free-text place must match one **exactly** (case- and whitespace-insensitive). This also closes free-text collisions (an Airbnb named "Bassett Inn").
3. Otherwise it falls back to the legacy `"basset"` substring. The fallback exists so a host whose `home.json` hasn't been updated keeps working — **if matching silently stopped, the home trips would become publicly visible**, which is the failure mode worth guarding.

The names live in gitignored config rather than in code because **this repo is public and the home place name is a street address** — hardcoding it would publish it. Adding `home_place_names` to a host's `home.json` is optional and per-machine; without it that host just runs the legacy path.

### Family Locations

`kind: "family"` entries are relatives' houses — a name next to a `driveway_location`, which is a street address for someone who isn't you. **They live in the gitignored `trip_data/family.json`, never in the tracked `campgrounds.json`** (split out 2026-07-30; the same reasoning that keeps `home.json` out of git, applied to the people in the trips). This is orthogonal to who may *see* them in the app: every logged-in user sees family markers by design — the app is family-only. The rule is only about what gets published to a public GitHub repo.

**One database, two files.** Ids are unique across both and references (`campground_id`, `family_id`) don't record which file they point into, so the split is invisible above the loaders:

- **Reads merge**, at exactly two points: `_read_campgrounds_raw()` in `ekko_trips_app.py` (cached on *both* mtimes) and `trips._load_locations_by_id()`. Every other reader was left alone. `/api/campgrounds/all` loads the file directly and merges explicitly.
- **Writes route by `kind`** via `_location_file_for_kind()` / `_find_location_entry()` / `_next_location_id()`. The last one reads **both** files: family currently holds the highest id in the database, so a max over `campgrounds.json` alone re-issues a live id (this also bit `append_state.py`, fixed there too).
- **A PUT that flips `kind` MOVES the entry between files.** The manage page's kind selector can do this, and getting it wrong is the leak the split exists to prevent — an entry switched to family but left in `campgrounds.json` publishes an address on the next commit.
- **It travels by `backup.sh` / `sync-from-pa.sh`, not git.** That is why it sits under `trip_data/` rather than at the repo root beside `home.json`: `sync-from-pa.sh` already mirrors that whole directory, so a family entry edited in the live manage UI on PA comes home automatically. `capture-pa-edits.sh` handles the *tracked* location file (`campgrounds.json`) over git and deliberately knows nothing about this one.
- A missing `family.json` is normal, not an error (a fresh clone has `campgrounds.json` from git and nothing else) — both loaders treat absent as `[]`.

**Note the history caveat:** these entries were in the public repo until 2026-07-30 and remain in its git history. Removing them from HEAD stops further publication; it does not unpublish what is already there.

### Data Model

- Trips contain campspots and events. Campspots sort by start date, events by date; the timeline merges both. New campspots/events default their date to the trip's first campspot start date.
- **Campspots** reference a location via `campground_id` (int, or null with free-text `custom_place` for hotels/Airbnbs). `_make_trip()` materializes a display-only `place` string from `campground_id` → name (with `custom_place` fallback). Optional `campsite_location` ("lat,lng") overrides the campground's listed coords when the listed coords are the office/entrance and the actual campsite is meaningfully offset. `enrich_trip_locations()` prefers `campsite_location` when set.
- **Visits vs stay records.** A campspot record is one *campsite*, not one visit: moving from site 67 to site 36 mid-stay is recorded as two records at the same campground (trip 93 does this; trip 60 has three in a row). `trips.visit_runs(stays)` is the single definition of a **visit** — a run of *consecutive* stays at the same place (same `campground_id`, or the same normalized free-text place) with **no gap in dates**, so leaving and coming back later in the trip still counts twice (trip 16 does that at two campgrounds). Every per-campground count goes through it: the trips-map dot size + popup list, the poster's dots, `_campground_visits_index()` (campground-map popup and `visit_count`), and the stats page's most-visited list. `_make_trip()` stamps each stay with `visit_num` (1 == starts the visit), `visit_stays`, `visit_nights` and `visit_night_offset`; the map templates group client-side off `visit_num > 1`, guarded by the marker key so grouping can't swallow a stay that landed on a different marker.
- **Events** have optional `end_date` and `location` (lat,lng). Plotted as gold stars on trip detail / gold dots on the main map. The event-location picker is the shared map picker without elevation lookup; the trip-detail stay edit form reuses it via `pickerTarget` for the "Pick on Map" button.
- **Events carry an IANA `tz`, and event ordering is by true instant, not by wall clock** (driving west sets the clock back, so trip 95 showed two stops backwards). `trips.event_time_rank()` is the one ranking function; the app layer stamps `tz` (`_stamp_event_timezone()`) and `trips.py` only reads it; a day stays the LOCAL date. Gap-fill anchors must be timestamped in their own zone — **always pass an offset when adding a new anchor**. Full rules: `docs/trip-timeline.md`.
- **Family visits** are events with a non-null `family_id` (referencing a `kind: "family"` entry in `trip_data/family.json`). `_make_trip()` materializes a `family_visit` label from `family_id`. Location auto-set from the family entry (preferring `driveway_location`). Rendered as red house icons (z-index 850) with salmon-toned cards and a simplified edit form. `onFamilyVisitChange` only overwrites the event `name` when it looks auto-filled (blank or matches any family label), so a custom name survives a family-location change. Proximity family markers are suppressed for locations that already have a family-visit on the trip.

### Auth & Admin Protection

Login is global via `_require_login_globally()` (registered as `before_request`). Exempt endpoints: `login`, `service_worker`, `offline`, `sw_reset`, `share_login`, `serve_tile`, `serve_pmtiles`, and `static` — **except** `static` requests under `uploads/`, which are refused outright (see "Photo System"). `_require_admin()` guards all mutation endpoints. Templates condition edit controls on the `is_admin` Jinja var / `IS_ADMIN` JS constant; drag-drop is fully disabled for non-admins.

`?next=` survives the login detour: `_require_login_globally()` sets it from `request.full_path` (so a query string like `?color=climate` is preserved), the login form posts back to that same URL, and the POST handler redirects through `_safe_next()`, which restricts the target to a same-site path so it can't become an open redirect.

**Roles.** Accounts live in `users.json` (`{username: {password_hash, is_admin, can_upload, can_view_campgrounds}}`, hashed via `werkzeug.security.generate_password_hash`). Beyond admin there are two narrower capabilities:
- `can_upload` — may POST photos and edit captions on photos they uploaded (ownership tracked in `trip_data/photo_uploaders.json`, keyed identically to captions). Gated by `_require_uploader_or_admin()` + `_can_edit_photo()`. Deleting and reordering stay admin-only. Admins always pass. `can_upload` is also the whole test for **contributor** (`_is_contributor()` / `_require_contributor()` / `_require_contributor_page()`) — the people who plan and record the trips, as opposed to everyone who reads about them. That's what unlocks the stats page's Longest Driving Days and the Weather Finder page.
- `can_view_campgrounds` — defaults true; clearing it makes a **Trips-only** user. `_require_campground_view_page()` redirects them off Campgrounds-section pages and `_require_campground_view_api()` 403s the matching APIs; the nav group and the phone tab both disappear.

Admins manage users at `/admin/users` (`templates/users_manage.html`) backed by the `/api/users` JSON API. Self-protection rules: cannot delete your own account, cannot remove admin from your own account. CLI bootstrap: `python ekko_trips_app.py create-admin`. Logins persist: `login_user(remember=True)` with a 365-day cookie, and when `FLASK_SECRET_KEY` is unset the generated key persists at `trip_data/secret_key` (gitignored) so restarts don't invalidate sessions.

### Share Links (read-only magic links)

`/s/<token>` logs a guest in as a synthetic viewer — user id `share:<token>`, never admin, never uploader — so relatives can see trips without an account. Because every mutation route is admin/contributor-gated, a leaked link exposes only viewing, which is why a long random token needs no password. Records live in `trip_data/share_tokens.json` (`{token: {label, trips_only}}`) and are managed from the Users page via `/api/share-links`.

- `load_user()` re-reads that file **on every request**, so deleting a token kills its live sessions instantly and flipping `trips_only` takes effect immediately.
- `trips_only` links additionally have `can_view_campgrounds` cleared.
- Unknown/revoked tokens render the login page with an explanatory error (403) rather than revealing anything.
- The token IS the credential, so `_redact_path()` truncates it to an 8-char prefix before it reaches the access log.

### Access Log

Who visited which page, including share-link guests — the identity lives only inside Flask-Login, so the host's own request log can't answer it. `_log_page_view` (an `after_request`) appends one JSONL record per **HTML GET** to `trip_data/access_log.jsonl`; assets, APIs, thumbs, tiles and static are skipped so one photo-heavy trip page doesn't bury the page views the log exists for. Auth transitions (`login`, `login_failed`, `share_login`, `share_revoked`, `logout`) are logged explicitly. Failed logins record the attempted username (never the password) — a run of them from one IP is the only signal that someone is guessing. Timestamps are UTC-aware so the browser can localize. `_log_access` never raises. `_prune_access_log()` drops entries past `ACCESS_LOG_RETENTION_DAYS` via temp-file + atomic replace. Viewed at `/admin/access-log`.

### Offline (Service Worker)

`/sw.js` (Flask route serving `static/sw.js` from root scope; login-exempt along with the `/offline` fallback page — a login redirect during SW install would cache the login screen as the offline page). Photos/thumbs (`/photo/`, `/thumb/`) are cache-first; pages/static/API GETs are network-first (online behavior identical to no-SW; cache is fallback only, so admins always edit fresh data). Redirected responses are never cached. Map tiles (OSM `*.tile.openstreetmap.org` + Esri `server.arcgisonline.com`) are cache-first in their own `ekko-tiles-*` cache (capped at 1000) — revisited tiles are instant and maps render offline; these are cross-origin no-cors so the responses are opaque and cached via a dedicated `tileCacheFirst` (the same-origin `cacheable()` guard rejects opaque). Other cross-origin (leaflet CDN) is still not intercepted. On install the SW also **precaches the landing map's opening view** — z3+z4 over a padded bounding box of the trips (16 tiles, ~350 KB, `TILE_PRECACHE` / `precacheTiles`), fetched sequentially, outside `waitUntil`, skipping anything already cached. That's what lets the map draw from a cold tile cache (after an eviction, offline, or when the SW installed from a non-map page); it is deliberately NOT a fix for a hard refresh, which bypasses the SW entirely. Bump `VERSION` in `sw.js` to flush caches after incompatible deploys. iOS standalone via `apple-mobile-web-app-*` metas + `static/manifest.json` + `static/icons/`.

### Photo System — see `docs/photos.md`

**Read `docs/photos.md` before touching photo storage, serving, metadata, favorites or the people scan.** The headlines:

- **`UPLOAD_DIR` (`photo_uploads/`) lives OUTSIDE `static/` and outside `trip_data/`, and both placements are load-bearing.** `static` is login-exempt and PA serves `/static/` straight from disk, so photos there were public; `sync-from-pa.sh` can `--delete` inside `trip_data/`. Originals serve only from login-gated `/photo/`; `/thumb/` (480px) and `/view/` (1600px, the lightbox) are lazily generated derivatives.
- **Photo directories and the five metadata stores are keyed by POSITION**, so every renumbering of campspots/events goes through `trips._apply_photo_index_mapping`. `trips.UPLOAD_DIR` must equal `ekko_trips_app.UPLOAD_DIR` (`tests/test_photo_index_remap.py`).
- **Adding a per-photo metadata file** means touching `trips._PHOTO_METADATA_FILES`, `move-photo`, `_purge_old_trash`, the delete-all prefix sweeps and `backup.sh`/`restore.sh`.
- Deletes move to `.trash/` with an Undo toast; favorites (poster heroes) are hand-marked by an admin ★; `people` is written only by `detect_people.py`.

### Campground System

- The location database holds both `kind: "campground"` and `kind: "family"` entries, each with a stable `id`, split across two files — tracked `campgrounds.json` and gitignored `trip_data/family.json` (see "Family Locations"), merged on read. Campspots reference entries by `campground_id`, and events reference family entries by `family_id`. Because references are ID-based, renaming an entry via the management page needs no propagation logic — existing references remain valid automatically.
- Custom stays (e.g. Airbnb, hotel) use `campground_id: null` and a free-text `custom_place` field. The frontend's `stayFieldsToPayload()` decides which fields to send based on whether the place text matches a known entry.
- Campspot edit forms use an autocomplete picker that fetches from `GET /api/campgrounds` (includes both kinds). Selecting an entry stores its `id` in a hidden field and auto-fills the state field. Family-kind entries are shown with a 🏠 prefix in the dropdown. When the user types free text that matches no entry, it's saved as `custom_place`.
- `trips.py:_load_locations_by_id()` is the single source of truth for resolving IDs to coordinates (reading BOTH location files) — prefers `driveway_location` for family-kind entries so stay markers don't collide with the red family house marker.
- **Deletes are reference-guarded.** `DELETE /api/campgrounds/<id>` returns 409 while any trip still points at the entry, listing the offending trips; `?force=1` overrides. Because references are by id, an unguarded delete fails *silently* — the campspot's `place` falls back to `custom_place or ""` and it loses its coordinates, leaving a blank row that plots nowhere. `trips.campground_references(id)` is the checker (covers both stay `campground_id` and event `family_id`).
- **Names are not unique and are not checked.** Campground names repeat constantly across states (7× "Lakeview Campground", 6× "South Fork Campground"; 286 duplicated names across 668 entries). An earlier uniqueness check on create/rename was unenforceable against the file's own data and only blocked legitimate adds. References are by `id`, so duplicates cost nothing.
- **The audit-evidence fields never reach the browser.** `waterfront_evidence` / `inclusion_evidence` are the source of truth in `campgrounds.json`, but no template or client script reads them and together they were ~4.6 MB of the map page. Both `_load_campgrounds()` and `/api/campgrounds/all` strip them. Safe because `PUT /api/campgrounds/<id>` merges from a **field whitelist**, so a UI save can't clobber a field the client never received. Keep that whitelist in mind before adding a new editable field — a field absent from it silently won't save.
- **Large text responses are gzipped** by the `_compress_response` `after_request` (HTML/JSON/CSS/JS over 4 KB). The campground map embeds the whole database inline, so it renders as ~9 MB of HTML that goes out at ~1.9 MB. Skips non-200s, already-encoded responses, and `direct_passthrough` (send_file) responses.

### Campground Curation — see `docs/campground-curation.md`

**Inclusion criteria, the waterfront evidence gate, and the state-by-state sweep pipeline live in `docs/campground-curation.md`. Read it before adding, editing, removing or auditing ANY entry in `campgrounds.json`, a single one-off add included** — the rules are deliberately asymmetric and each one is there because it was got wrong once. The headlines, so you know when you need it:

- **An entry must be a real, publicly-bookable, drive-in RV campground a 23-ft rig fits**, with a live web presence. No horse/tent-only/hike-in/boat-in/cabin-only/group-only; no seasonal-residential, workforce, membership or casino-lot parks. The doc has the full list and the judgement calls.
- **`waterfront` defaults DOWN and must be *earned*.** "Couldn't confirm" resolves to `*view` or `not waterfront`, never up. A name, marketing prose, a boat ramp or an aggregator snippet can never be the basis; a satellite look is mandatory but can only veto, not confirm under canopy. The vocabulary, the open-apron rule, the coastal-dunes/woods exceptions and the distance bound are all in the doc.
- **Two evidence fields are the audit record, and non-empty means audited:** `waterfront_evidence` (the proof for the waterfront call) and `inclusion_evidence` (the proof it's a valid campground). Absent == NOT audited. The commit message is not the record — that proved too easy to skip.
- **Mechanics that bite:** ids come from `max(id) + 1` across BOTH location files and are never reused; append entries rather than re-dumping the file (a full `json.dump` churns the whole diff); pin `location` to the campground, not the park entrance; URLs go in `website`, not `note`; keep someone else's `--AWH`-style note attribution intact and append your own marker.
- **Run sweep agents sequentially**, one at a time — parallel batches exhaust the session limit and lose in-flight work.

### Git & GitHub Auth

- **Git:** commit campground edits directly to `master` (solo data repo; no feature branch unless asked); push only when asked.
- **GitHub auth (HTTPS push):** auth is automated via `git-ask-pass-pat.sh` (tracked) + a `GITHUB_PAT` in the gitignored `.env` at the repo root. The askpass script loads `GITHUB_PAT` from that `.env` if it isn't already in the environment, so `git push` needs no manual `source`. One-time per clone, point Git at it (writes machine-local `.git/config`, an absolute path, so it isn't committed):
  ```
  git config core.askPass "$(pwd)/git-ask-pass-pat.sh"
  ```
  Then create `.env` with `export GITHUB_PAT=<token>`. After that, `git push origin master` authenticates with no prompt. When the PAT expires, just update it in `.env`. (If `core.askPass` is unset or `.env`/PAT is missing, push falls back to failing on credentials — the user runs `! git push origin master` themselves.)

### Asset & Payload Caching

- **Static assets are fingerprinted and long-cached.** `static_v()` appends `?v=<mtime>`, and `_cache_static` (an `after_request`) answers those requests with `public, max-age=31536000, immutable`; un-fingerprinted static (icons, manifest) gets a day. Flask's default is `no-cache`, which cost a revalidation round trip per asset per page load — leaflet.js alone is 144 KB. **On PythonAnywhere this header does not apply:** the host maps `/static/` straight to disk and never consults Flask (the same property that forced photos out of `static/` — see "Photo System"), so the live site falls back to heuristic `Last-Modified` caching. Removing that mapping in the PA Web tab would hand static back to Flask and make the header real.
- **The landing slideshow ships a capped pool.** `SLIDESHOW_POOL_MAX` (200) slices `_collect_photo_pool()` *after* the shuffle, so each load draws a different subset and the library still feels whole. Before the cap the whole library rode inline — 492 KB of the page's 1.41 MB — and it had to arrive and parse before Leaflet could request its first tile. The rotator shows one new photo per 2.5 s, so 200 is ~8 minutes of unique photos.

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
- **Auto-fallback to straight track:** when the GPS data doesn't actually cover the trip, the GPS layer is silently skipped and the dashed straight-line route stays as the only polyline. Triggered when the `/track` fetch fails/returns nothing in-window, or a strict (completed trips) / relaxed (in-progress trips) anchor-proximity gate fails. There is no manual "force straight" toggle — these heuristics are the only mechanism. Full gate logic and the trip-61 / trip-90 rationale are in the comment above the gate in `trip_detail.html` (search `Auto-fallback: skip the GPS layer`).
- **GPS tracks, trip routes and ping overrides live in `docs/gps-track.md`** — driving-time measurement (`_moving_seconds` + the long-leg clamp), the `/api/trips/<id>/track` endpoint and its gzipped per-trip cache, per-day tid selection (`_select_track_per_day`) with the admin `tid_overrides` and sub-day `tid_windows`, `_AnchorProximityIndex`, the manual `suppressed_pings` / `relocated_pings` / `bad_track_windows` overrides, frontend polyline windowing + gap-fill, the precomputed overview "Trip routes" overlay, and the admin-only per-point markers. **Read that file before changing any of it** — most of its rules exist to fix a specific observed failure.
- **Z-index layering on trip detail:** the suppressed/relocated override ghost layers render in a dedicated `overrides` pane (zIndex 700) above Leaflet's markerPane (zIndex 600) so the admin can always click through to unsuppress/unrelocate even when the override sits at the same coords as a stay or family marker. Within markerPane the divIcon ordering is Home (1000) > Family (900) > Stays (800) > Events (default).
- **Trip detail marker clicks are layout-dependent** (see "Trip Detail Map ↔ Card Interaction"): on the two-column layout they scroll to the corresponding card and carry no popup (a hover tooltip names them); on the stacked single-column layout they open a popup instead. **A marker standing for more than one timeline entry — a campground stayed at on separate legs, a family location visited several times — opens its occurrence-list popup on BOTH layouts instead** (`onMarkerClick`'s `alwaysPopup`), because scrolling can only pick one occurrence. Family-visit events at the same family location collapse into one shared marker via `familyVisitGroups`; repeated campspots keep one marker per stay (they sit ≤50 m apart, so they're a single marker visually) and every one of them opens the same list.

### Trip Detail page — see `docs/trip-timeline.md`

Layout, map↔card interaction, timeline cards, campspot comings and goings, day dividers, the day's write-up, editing UX, Detect Stops and ⏱ From GPS are specified in **`docs/trip-timeline.md`. Read it before touching `trip_detail.html`, `static/trip-detail/`, or the timeline/route/stop helpers in `ekko_trips_app.py`.** The rules that bite from elsewhere:

- **Never fold or hide low-content timeline items** — waypoints are how AWH orients in a trip. Compact one-line rows replaced folding (`WAYPOINT_FOLDING_ENABLED = False`), and there is deliberately no per-day filter or picker.
- **A typed day note always outranks a drafted rollup.** Notes live on the trip record (`day_notes` in `trips.json`); **`parse_trips()` does NOT carry them — read them with `get_day_notes(trip_id)`**, or a check reports zero notes however many exist.
- **`_find_home_boundary_tsts()` is the only trip-boundary detector**; the frontend displays its answer and never recomputes it. Don't reintroduce a JS version.
- Marker clicks are layout-dependent (two columns: scroll to the card; one column: popup; a repeated location: occurrence list on both). `isSingleColumnLayout()` is the single breakpoint check.
- Detect Stops suggestions are created with `needs_vetting: true`, cleared by any PUT to the event.

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

**Terrain** (Esri World_Topo_Map — shaded relief, contours, public land shaded) is a third base layer between Map and Satellite. Same host and terms as the satellite stack, so `sw.js`'s tile cache already covers it. Online only: `_tile_config()` sends `terrain: null` in local (USB) mode and `ekkoTerrainLayer()` returns null, so the layer control just doesn't list it. Every interactive map builds its base-layer set through `ekkoBaseLayers(streets, satellite)` so they can't drift on which basemaps they offer; the poster stays street-only.

**The trip-detail and trips maps pass `zoomSnap: 0`** so `fitBounds` can land on a FRACTIONAL zoom. Integer zoom levels double the visible area each step, so missing one by a hair costs the entire doubling: trip 95 spans 27.3° of longitude, needs zoom 5.04, snapped down to 4, and opened on a 63°-wide view — the trip in a thin band with two-thirds of the frame ocean. It is also why the landing map framed the trips correctly on one desktop and opened on Oregon, Mexico and most of Canada on another: two window sizes falling either side of an integer boundary. The cost is that tiles are CSS-scaled at fractional zooms and read slightly softer. Tile REQUESTS stay at integer zoom (Leaflet rounds for the URL), so the service worker's `ekko-tiles-*` cache and the offline PMTiles build are unaffected. **The poster does NOT do this** — it needs crisp tiles for print, and solves the same problem by fitting at `ceil(zoom)` and scaling the div back down (see `docs/poster.md`); don't unify them.

**No map anywhere carries Leaflet's +/− zoom control** — every `L.map()` call passes `zoomControl: false`. Wheel, pinch, double-click and the keyboard +/− all zoom, so the buttons only spent map area (worst on the small map-picker popup and on phones). Keep new maps consistent.

### Responsive / Mobile Design

Single mobile breakpoint at `max-width: 700px`; trips map has an extra `max-width: 900px` breakpoint for filmstrip reflow. Each template owns its own mobile rules — see those CSS blocks for specifics. Notable behaviors:

- **Header:** `☰` hamburger toggles `.open` on `<nav>` ≤ 700 px; toggle handler re-publishes `--site-top-height` so sticky sub-headers reflow. Header stats stack vertically on mobile.
- **Trip detail map gestures (touch):** one finger scrolls the PAGE, two fingers pinch/pan the MAP — the Google-Maps-embed convention, chosen so a swipe over the map band at the top of a phone doesn't trap the reader (AWH 2026-07-26). Getting there took three tries and the current one is the only one that holds: Leaflet dragging is off (`dragging: !touchPrimary`), the container declares **`touch-action: none`**, and the one-finger page scroll it gives up is re-implemented in `enableMapPageScroll` (`static/trip-detail/map.js`) — delta-tracked scroll plus a decaying fling. **The `touch-action` is the load-bearing part:** the compositor decides whether a touch may pan the page when the FIRST finger lands, before any JS runs, so nothing done later can take that back — Leaflet's `preventDefault` on the second finger is too late once the first has drifted past the scroll slop (the timeline slid under a pinch), and freezing the page mid-gesture froze the content but not Firefox's address bar, which had already been handed the gesture. Don't "simplify" this back to letting the browser scroll the map's touches.
- **Trip detail header:** on mobile, `.meta` is hidden and the `<h1>` itself is tappable to edit (with a viewport check so desktop text-selection still works). `.trip-nav` (prev/next trip chevrons) stays visible at reduced size, flanking the title.
- **Modal form-grid items:** carry `min-width: 0` so `<input type="time">` and time-range pairs don't overflow. ≤ 600 px collapses to one column. The waypoint checkbox is excluded from the global `width: 100%` input rule.
- **Leaflet popups:** ≤ 700 px forces popup content to near-viewport width via `!important` overrides on `.leaflet-popup-content` (Leaflet caps content at its measured width otherwise). Desktop popup `maxWidth` is 420 on trips/campground maps so trip-link rows fit on one line.

### Local HTTPS, Backups, Deploying — see `docs/hosting.md`

- The dev runner serves HTTPS with a persistent self-signed cert at `trip_data/dev_cert.{crt,key}` (geolocation needs a secure origin); `--http` falls back. PA handles TLS itself.
- `backup.sh` / `restore.sh` bundle and restore the gitignored data (never `campgrounds.json`, which travels by git); `sync-from-pa.sh` is the usual incremental path. **Stop the app before restoring.**
- `./deploy-to-pa.sh` = `git pull` on PA + touch the ekko WSGI file — **the reload is not optional**. SSH to PA is key-only via two restricted keys (forced-command deploy, read-only rrsync); a new machine gets its OWN keys, appended with `>>`.
- `./capture-pa-edits.sh` brings live admin-UI edits on PA down, commits, pushes, reconciles and deploys; it refuses when both sides could be right (deploy first, then capture).
- **The one real hazard:** `campgrounds.json` and `roadside.json` are tracked in git AND written by the live admin UI, so PA's tree is legitimately dirty and those edits exist nowhere else. Bring them **down**; never `git checkout --` on PA, and never auto-roll-back with `git reset --hard`.

## API Routes

### Trip/Campspot/Event CRUD
- `POST /api/trips` — create trip (empty, no default campspot)
- `PUT/DELETE /api/trips/<id>` — update/delete trip
- `POST /api/trips/<id>/stays` — add campspot
- `PUT/DELETE /api/trips/<id>/stays/<idx>` — update/delete campspot
- `POST /api/trips/<id>/events` — add event. The route stamps the event's IANA `tz` from its `location` before storing (see "Events carry an IANA `tz`")
- `PUT/DELETE /api/trips/<id>/events/<idx>` — update/delete event. A PUT carrying a `location` re-derives `tz`; one that omits the key leaves it untouched
- `GET /api/trips/<id>/track[?admin=1]` — returns `{points: [...], home_auto_start_tst, home_auto_end_tst}`. `points` is the GPS track; the two tsts are the auto-detected trip boundary from `_find_home_boundary_tsts` (single source of truth for the polyline window + home-card "(auto)" time; either may be `null`). Degenerate cases (trip has no dates, or no API token and no cache) still return a bare `[]` array, which the frontend treats as no points + no boundary. Admin pages pass `admin=1` so each ping carries `suppressed`/`relocated` flags + `original_lat`/`original_lon` for relocated pings (instead of being filtered/silently rewritten); the boundary is computed on the cleaned view regardless of the flag, so every viewer gets the same window
- `GET /api/trips/routes` — every visible trip's precomputed, simplified GPS line for the overview map: `{trip_id: [[lat, lng], ...]}` (one continuous polyline per trip; trips with no drawable line are omitted rather than returned empty). Home-only trips are filtered for non-admins. See `docs/gps-track.md`
- `POST/DELETE /api/trips/<id>/suppress-pings` — mark / unmark `tst`s as suppressed (body `{tst: [...]}`); idempotent
- `POST /api/trips/<id>/relocate-pings` — set lat/lon overrides (body `{items: [{tst, lat, lon}, ...]}`); replaces existing entries by `tst`
- `DELETE /api/trips/<id>/relocate-pings` — clear overrides (body `{tst: [...]}`)
- `PUT /api/trips/<id>/tid-overrides` — admin-only; body `{date: "YYYY-MM-DD", value: "primary"|"alt"|null}`. `null` clears that day's override. Returns the resulting overrides dict.
- `PUT /api/trips/<id>/day-note` — admin-only; body `{date: "YYYY-MM-DD", text}`. The day's own write-up, stored on the trip record; empty text clears it. Outranks any drafted rollup for that day (see "The Day's Write-Up")
- `PUT /api/trips/<id>/camp-note` — admin-only; body `{stay_idx, key: "YYYY-MM-DD#N", text}`. The note on one Arrived / Back at row, stored on that stay's `camp_notes`; empty text clears it
- `PUT /api/trips/<id>/road-place` — admin-only; body `{key: "YYYY-MM-DD/filename", text}`. A place typed over a road card's GPS label, stored on the trip record's `road_places` against one of the card's photos (the card has no record of its own, and a photo stays with its leg when a new stop re-splits the day); the first photo of a card carrying one wins. Empty text clears it and the GPS label returns. If that photo is deleted or moved off the card, the place goes with it
- `GET /api/trips/<id>/tid-choices` — admin-only; returns `{tid_choices, tid_overrides, counts, alt_configured}` where `tid_choices` is what the per-day selector would pick **ignoring overrides** (so the Track Source UI can render "Auto (would pick X)"). `counts` is per-day per-tid raw ping counts.
- `POST /api/trips/<id>/detect-stops` — admin-only; scan the trip's GPS track for dwell-time clusters not already represented by a stay/event/family location. Returns a list of suggestions, each with a `display` block (for the modal) and an `event` block (the exact payload `/accept-stops` will feed into `add_event`). Reverse-geocodes one stop per second so the call can take tens of seconds.
- `POST /api/trips/<id>/accept-stops` — admin-only; body `{events: [<event payload>, ...]}`. Creates each as a new event/waypoint with `needs_vetting: true` (server always forces the flag on, regardless of payload) and retires any `dismissed_stops` entry it re-creates.
- `GET /api/trips/<id>/gps-times?lat=&lng=[&date=&time=&exclude_event=&radius_m=]` — admin-only; the GPS arrival and departure for ONE place, as `{found, date, time, end_time, tz, tz_abbr, duration_minutes, ping_count, radius_m, visit_count, gap_minutes}`. `{found: false, reason}` when the trip has no track or the track never came near the place — neither is an error. Advisory only: nothing is persisted, the answer fills the open edit form (see "Times from GPS")

### Photo Operations
- `POST /trips/<id>/stays/<idx>/upload` — upload campspot photo or zip file
- `POST /trips/<id>/events/<idx>/upload` — upload event photo or zip file
- `POST /trips/<id>/stays/<idx>/reorder` — reorder campspot photos
- `POST /trips/<id>/events/<idx>/reorder` — reorder event photos
- `POST /trips/<id>/move-photo` — move photo between campspots/events (body: filename, src_type, src_idx, dst_type, dst_idx)
- `POST /trips/<id>/stays/<idx>/caption` — save campspot photo caption
- `POST /trips/<id>/events/<idx>/caption` — save event photo caption
- `DELETE /trips/<id>/stays/<idx>/photos/<file>` — trash campspot photo (undo-able)
- `DELETE /trips/<id>/events/<idx>/photos/<file>` — trash event photo (undo-able)
- `POST /trips/<id>/stays/<idx>/photos/<file>/restore` — restore from trash (404 if absent, 409 if name retaken)
- `POST /trips/<id>/events/<idx>/photos/<file>/restore` — restore from trash
- `GET /thumb/<subpath>` — cached 480px thumbnail of the photo at `<subpath>` under `photo_uploads/`
- `GET /photo/<subpath>` — full-size original (login-gated; the ONLY way to fetch one)
- `POST /api/photos/favorite` — admin-only; body `{photo: "<trip_id>/<idx>/<file>", favorite: bool}`. Star/unstar a poster hero. `photo` is the storage subpath every photo URL already carries, so one endpoint covers stays and events on every surface; the key is resolved through `_resolve_photo_request` so a nonexistent photo 404s rather than accumulating a dead metadata entry

### Campground CRUD
- `GET /api/campgrounds` — lightweight `{id, name, state, kind}` list (for autocomplete picker; includes both kinds, merged from both files)
- `GET /api/campgrounds/all` — full data (admin, for management page); strips `waterfront_evidence` / `inclusion_evidence`
- `POST /api/campgrounds` — create entry (auto-assigns next id from BOTH files; accepts `kind`, which routes the write to `campgrounds.json` or `family.json`; family entries may carry `driveway_location`). No name-uniqueness check
- `PUT /api/campgrounds/<int:id>` — update entry by id in whichever file holds it, merging from a **field whitelist** (so audit-evidence fields survive); a changed `kind` MOVES the entry between files; no name-propagation needed, references are id-based
- `DELETE /api/campgrounds/<int:id>[?force=1]` — delete entry by id; **409 while any trip references it** (body carries `references`), `force=1` overrides
- `GET /api/elevation?lat=X&lng=Y` — proxy to the Open-Meteo DEM, returns `{elevation_meters}` (matches the source every existing entry was pinned against; 502 on failure)
- `GET /api/geocode?q=X` — proxy to Nominatim geocoding API, returns `[{name, lat, lon}]`; **502 on a failed lookup** (never an empty array — that made an outage look like "no such place")
- `GET /api/reverse-geocode?lat=X&lng=Y` — nearest named entity + enclosing `locale`/`state`, plus the `on_road` flag detect-stops uses to auto-uncheck traffic pauses
- `GET /api/nearby-places?lat=X&lng=Y[&radius=]` — up to ~20 named OSM POIs (Overpass; default 300 m, capped at 1000 m), backing the name-field dropdown on event/waypoint forms

### Roadside Stops (admin CRUD, edited inline on the campground map)
- `POST /api/roadside` — create a stop
- `PUT /api/roadside/<int:id>` — update a stop
- `DELETE /api/roadside/<int:id>` — delete a stop

### Users, Share Links, Access Log (admin)
- `GET/POST /api/users`, `PUT/DELETE /api/users/<username>` — user CRUD (`is_admin`, `can_upload`, `can_view_campgrounds`)
- `GET/POST /api/share-links`, `PUT/DELETE /api/share-links/<token>` — create/label/revoke read-only magic links (`trips_only` toggle)
- `GET /api/access-log` — page-view + auth-transition history
- `GET /s/<token>` — share-link login (login-exempt; honors `?next=` through `_safe_next`)

### Weather Finder (Open-Meteo forecast search)
- `GET /campgrounds/weather` — the page (contributor-only via `_require_campground_view_page()` + `_require_contributor_page()`)
- `GET /api/weather-finder/lookup?q=<name>` — contributor-only campground name search backing the by-name forecast lookup. Matched server-side and capped at 20, prefix matches first; `/api/campgrounds` would mean shipping ~12.9k rows to the browser to type into
- `GET /api/weather-finder/forecast?id=<id>` — contributor-only. **Every forecast day for one campground, no distance limit and no filters** — you named it, so you want its forecast rather than a verdict on it. Shares the search's grid cells and cache both ways, so a lookup inside an already-searched area is free and also warms that cell
- `POST /api/weather-finder/search` — contributor-only. Body: `mode` (`range`/`cooler`/`warmer`), `max_miles`, `min_high`/`max_high` (range mode), `delta_f` (relative modes), `weekends_only`, `dry_only` + `max_precip_in`, `waterfront_only`, `sort` (`distance`/`temp`/`rain`/`waterfront`), optional `lat`/`lng` origin (defaults to `home.json`). Returns campgrounds grouped with their matching days, plus `map` (every checked campground, compact, for the forecast map), `criteria` (the clamped thresholds that ran, for the map's colour scale), and `eligible` / `considered` / `fetched` / `from_cache` so the page can say what was actually checked — "no matches" and "no matches in the part we looked at" are different answers. **429 is passed through** as the provider's rate limit, not swallowed: a partly-fetched search returns fewer matches, which reads exactly like "there aren't any"

### Federal Availability (recreation.gov / RIDB)
- `GET /api/ridb/search?q=X[&state=ST]` — search federal campgrounds by name (campground-view gated). **RIDB's own `query` matches the facility DESCRIPTION as well as its name**, so a campground on the "big bend" of some river outranks the one actually named Big Bend — WV's Big Bend was #16 of 16 results and the picker draws 12. So the route over-fetches (`RIDB_SEARCH_FETCH`) and re-sorts by how well the NAME matches (`_ridb_match_rank`: same name → starts-with → every query word → description-only), stably, so RIDB's relevance still breaks ties. `_ridb_name_key` normalizes away RIDB's disambiguating parenthetical ("BIG BEND (WV)") and a generic "Campground" tail so the local name matches. `state` narrows the RIDB query and falls back to nationwide when it finds nothing. Each result carries `exact` — set only when a SINGLE result has the name, which is the picker's licence to auto-select.
- `GET /api/ridb/availability?facility=<RIDB FacilityID>&start=YYYY-MM-DD&end=YYYY-MM-DD[&fit_ft=]` — per-night availability for sites EKKO fits (both dates inclusive; `fit_ft` defaults to `DEFAULT_FIT_FT`). Campground-view gated

## Conventions

- Private Python functions prefixed with `_`
- Routes organized by section with comment headers in `ekko_trips_app.py`
- Photo keys use format `{trip_id}/{stay_idx}/{filename}` (campspots) or `{trip_id}/events/{event_idx}/{filename}` (events)
- Photo order keys: `{trip_id}/{stay_idx}` or `{trip_id}/events/{event_idx}`
- Trip IDs are permanent auto-incrementing integers; display numbers are computed from chronological position
- No frontend build step — all JS/CSS is inline in templates except the shared map picker (`static/map-picker.js`, `static/map-picker.css`), the shared campground-field formatters (`static/campground-schema.js`, used by the manage form's collapsed sections and the map popup), the shared photo lightbox (`static/lightbox.js`, `static/lightbox.css`, markup partial `templates/_lightbox.html`), `static/photo-favorite.js`, and the `static/trip-detail/` modules
- The lightbox is shared by trip detail and the trips map. A page opts in by including `_lightbox.html` plus that CSS/JS pair. `openLightbox(img)` alone pages through the clicked img's `.photo-grid` siblings; `openLightbox(img, {photos, onClose})` lets a caller supply its own set. Per-photo extras are read off the img: `data-full` (original to swap in for the thumb), `data-caption` (fallback when the photo isn't in a `.photo-item` carrying a `.caption-text` span), `data-trip-href`/`data-trip-name`/`data-trip-date` (shows the trip card — omit on pages already scoped to one trip), `data-place-name` (the card's second line — the campspot/event/waypoint name alone; the kind is deliberately not labeled). The trip card is styled to match the landing page's `.latest-trip-banner` / `.on-this-day` cards (white card, colored left rule, right-justified CTA pill) — keep them in sync. It centers along the top via auto margins (leaving `transform` free for the hover lift), capped at `min(720px, 100vw - 200px)` so a centered box can't reach the close/download cluster; ≤700px it drops below those buttons at full width and sheds the date to protect the names. `trips_map.html` derives the place from the pool's `card` index against `TRIPS` — no extra server data
- `_collect_photo_pool()` carries each photo's `caption` (one `captions.json` read per build, and the caption endpoints invalidate the pool so edits show up immediately). It deliberately does NOT carry the EXIF date taken — that needs a Pillow open per file, which is why the trips-map lightbox shows no date badge
- The data model uses "stays" internally (code, JSON keys, API routes) but the user-facing term is "campspot/campspots"
- The waterfront field in data is called "waterfront" but displayed to users as "Proximity to Water"
- Pluralization: all counters use singular when count is exactly 1, plural otherwise (including 0). In JS use `!== 1`, in Jinja use `== 1`. Never use `> 1` as it mishandles zero.
- Jinja `tojson` is configured with `sort_keys: False` to preserve Python dict insertion order (important for legend ordering)
