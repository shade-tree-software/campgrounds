---
name: ux-review-2026-07
description: "Full UX review (2026-07-26) of the non-admin/viewer experience — prioritized backlog of share-guest dead ends, page-weight, discoverability, a11y, and map issues, with file:line refs"
metadata: 
  node_type: memory
  type: project
  originSessionId: e29cc85c-749a-4093-92ca-f238308f5729
  modified: 2026-07-26T11:43:03.143Z
---

# UX review — EKKO Trips for non-admin users (2026-07-26)

Three-agent review of the viewer experience: regular logged-in viewers, share-link guests (`share:<token>`), and Trips-only users (`can_view_campgrounds=false`). Work off this backlog in future sessions; check items off (`[x]`) as they land and note the commit.

**Scope decision (AWH):** this is a private family app — see [[app-is-private-family-only]]. Family home locations SHOULD be visible to all users; do not treat that as a privacy issue. Privacy-flavored findings from the original review were removed accordingly.

**Overall:** permission gating itself is in excellent shape — all three reviews independently verified that edit affordances, admin modals, and mutation routes are cleanly hidden or blocked, with no broken-but-visible controls in the viewer path. The real problems are **share-guest dead ends**, **page weight paid by viewers for admin features they can't use**, and **missing feedback/discoverability** on the read-only surfaces.

## Top issues by impact

**1. Share-link guests can strand themselves permanently.** The nav renders a normal Logout link for `share:` sessions (`templates/base.html:433`). A guest who taps it is logged out and dumped on a password form they have no credentials for — their only way back is re-finding the magic link in an old text message. Related: a revoked link renders the login form with a terse error (`ekko_trips_app.py:1301-1304`), which reads as "broken site" rather than "ask Andrew for a new link"; and the per-link `next` stored at share-link creation is never read server-side (`ekko_trips_app.py:2757` vs `:1307`), so a messaging app that strips the query string silently loses the intended deep link. There's also no indicator anywhere that a guest is a guest — no "viewing as guest (read-only)" chip, even though `_share_label()` already exists to supply the name.

**2. The most likely 404 is a plain-text dead end.** `trip_detail` returns a bare `return "Trip not found", 404` (`ekko_trips_app.py:1797`) instead of `abort(404)` — so a guest following a link to a deleted trip gets unstyled text with no header and no way back, bypassing the styled `error.html` handler that exists for exactly this.

**3. The calendar marks the wrong day every evening.** `trips_calendar.html:558` builds "today" from `toISOString()` (UTC), so from ~7pm ET onward the today-ring sits on tomorrow. The same UTC formatting on local-midnight dates (`:530-531`) shifts every trip's highlighted days one day early for any viewer east of UTC — i.e., relatives abroad following a share link. (`renderOnThisDay` at `:702-706` already does it correctly with local components — the two widgets disagree.)

**4. Viewers pay for ~100 KB of admin-only JS plus hidden edit forms on every trip page.** `timeline.js` (51 KB), `overrides.js` (31 KB), `detect-stops.js` (18 KB), and `map-picker.js` load unconditionally (`trip_detail.html:2312-2318`), and every stay/event's hidden edit form renders into the viewer DOM (`:1626-1630`, `:1802-1857`, `:1934-2016`). Wrapping those scripts/blocks in `{% if is_admin %}` is cheap and high-value. (Page-weight rationale only — shipping `family_locations` etc. to viewers is fine per the scope decision above.)

**5. The campground map re-downloads 1.7 MB on every visit, and 65% of it is popup filler.** Measured: 12,872 rows → 7.54 MB inline JSON. The `note` field alone is 3.88 MB and `website` another 1.09 MB — content that exists only to fill the one popup a user opens. Two dead fields (`delta_temp`, the constant `kind` — `ekko_trips_app.py:1439-1441`) add ~384 KB more. And because the app sets `Cache-Control: no-cache` with no ETag anywhere, even a back-and-forward within seconds re-fetches the full gzip. Two fixes stack: an ETag keyed on the existing `_campgrounds_derived_cache` mtimes (→ 304 on the common case), and a slim marker payload with a per-id `/api/campgrounds/<id>/popup` fetch. There's also no loading indicator at all during the multi-second parse and 12,872-marker build.

**6. Photo originals: no loading feedback, and the download button can save the wrong file.** The lightbox has exactly two sizes — 480px thumb and untouched multi-MB camera original. While the original loads, the viewer sees a blurry stretched thumb with no spinner, and the download button reads the live `img.src` (`static/lightbox.js:252-264`), so tapping it before the original lands silently saves the 480px thumbnail under the original's filename (fix: download `dataset.full` instead). It also preloads two full originals per page-turn (`lightbox.js:149-152`) with no `Save-Data` check — tens of MB on a campsite cell connection. Consider a mid-size (~1600px) derivative for the lightbox with the original reserved for download.

## Discoverability and dead ends

- **The Stats page has one link on it.** Year bars, most-visited campspots, and state chips are all inert text (`trips_stats.html:255`, `:265-273`, `:300`) — each is an obvious jump to the calendar or a search. The "1,204 photos" hero number leads nowhere because no cross-trip gallery exists (candidate feature: `/trips/photos` paginated over `_collect_photo_pool()`).
- **`/trips/poster` is unreachable.** It's login-gated, correctly filters `home_only` for non-admins, and is the most shareable artifact in the app — and zero templates link to it (`ekko_trips_app.py:1595-1599`). It also lacks an on-page Print button and any way back (`trips_poster.html` doesn't extend base).
- **Trips-only users get silent redirects.** `_require_campground_view_page` (`ekko_trips_app.py:1112-1118`) bounces them to the trips map with no message, so a campground link texted by a family member reads as a broken link rather than a permission boundary. A one-line toast fixes the confusion. Legacy `/campgrounds/waterfront|climate` routes (`:2401-2413`) redirect before gating → double-hop.
- **Trip search is hidden.** It exists only on the calendar page (`trips_calendar.html:491-494`), unadvertised; a guest wanting "the Acadia trip" from the landing page has to guess it's there. The `/`-to-focus shortcut (`:1058`) is unhinted; no "All years" list view.
- **Campground map search only matches 2-letter state codes** (`campground_map.html:1958-1964`) — typing "Colorado" returns nothing — and there's no state filter, no "showing N of 12,872" count, unranked substring match hard-sliced to 12. Persisted filter state can leave a returning mobile user staring at a map with pins mysteriously missing — the master 🏕️ toggle persists off with the legend hidden entirely (`:887-897`, `:1088-1101`), and the "Color by" picker is invisible inside the collapsed mobile legend (`:1288-1291`).
- **Campground popups lack the single most-wanted action: a Directions link.** Roadside-stop popups have one (`campground_map.html:868`); the 12,872 campground popups don't, despite having lat/lng in hand (`:1075`). Also: no `maxHeight` on popups (long notes overflow phone screens); "Check availability →" only for federal; no "Visited" filter despite `visit_count` being shipped.
- **Lightbox photo sets fragment.** Paging is scoped per grid (`static/lightbox.js:85-87`), and split multi-night stays render one grid per night — so a 4-night campspot's photos are four separate lightbox sets and there's no "all trip photos" view. Also missing: "N of M" position indicator; place-name context line on trip detail (the trips map passes `data-place-name`, trip detail doesn't).

## Trip detail map (viewer-facing)

- **No marker labels, no legend.** Numbered navy circles, gold stars, gray diamonds, red houses — nothing names them, no tooltips (`static/trip-detail/map.js:275-279`, `:1000-1004`; dead `labelPrefix` at `:998`), and "waypoint" is admin vocabulary surfaced to family viewers (suggest "stops"). Family/home house markers should get a tooltip naming the location (they stay visible to everyone per the scope decision).
- **Scroll traps on both form factors.** On phones, the map sits at the top with default one-finger drag enabled (`map.js:215`), so swiping up pans the map instead of scrolling. On desktop, the fixed map covers the left half and wheel-scroll zooms it instead of scrolling the timeline.
- **No "fit trip" reset** after a click or accidental zoom (`map.js:74-86` jumps to `setView(ll, 14)` with no way back), and initial bounds always include HOME (`map.js:231`) — so a Utah trip opens as a continental view with the itinerary a few pixels wide.
- **Card→map is silent on mobile** (the map is off-screen above; tapping a card appears to do nothing — `scrollIntoView` the map first). Card click also has no cursor/hover/keyboard affordance.
- Layer control names are internal vocabulary ("Straight route" / "GPS track"); per-ping timestamp popups are admin-only (`map.js:902-912`) — read-only ping popups would be the most interesting viewer feature of having a track. Live-trip polling refetches/rebuilds the whole track every 2 min for viewers too (`map.js:840-850`).
- Timeline: no day dividers on a 10-day trip; mobile header drops photo count / GPS miles / campers (`trip_detail.html:648`, `:1661-1666`); prev/next chevrons ~24px touch targets with `title`-only destinations; a trip with no timeline renders header + blank space (no empty state, `:1697-1699`); photo grids are one column on phones with no "+N more" expander; portrait photos center-cropped 4/3 (crops faces).

## Accessibility (recurring across all pages)

The same few gaps repeat: empty `alt` on the lightbox image (`_lightbox.html:16`) and the landing-page slideshow imgs (`trips_map.html:849-850`); glyph-only buttons ("×", "‹", "›") with no `aria-label`; toasts with no `aria-live` (`base.html:319`); the auto-rotating 2.5s carousel with no pause control or `prefers-reduced-motion` check (WCAG 2.2.2 failure; also doesn't pause on keyboard focus, and downloads 6 slots on phones that show 3); legend/filter rows as bare `<div>`s with no keyboard operability (`campground_map.html:1226-1240`); availability status with no `aria-live` on a 5-15s request; availability conveyed by color alone (`font-size: 0` hides the ✓, `campground_availability.html:106-108`); circleMarkers unreachable by keyboard/SR on the trips map. Sub-44px touch targets on the mobile hamburger links (`base.html:94-98`, `:221-228`) and the prev/next trip chevrons — while the touch-target CSS bump explicitly targets admin buttons viewers never see (`trip_detail.html:788-790`). Also: no skip link; `nav-toggle` lacks `aria-expanded`; `.nav-label` contrast ~4.4:1 (borderline); `#999` empty-state text on `#f7f8fc` ≈ 2.6:1 (fails).

## Smaller but worth knowing

- Header day-trip count and the Stats page compute "day trip" differently (`ekko_trips_app.py:259` vs `:1653`) — the numbers can disagree; use one helper.
- Home-only trips are reachable by direct URL for non-admins (`trip_detail` never checks `home_only`, `:1794-1797`) — a one-way door into content deliberately hidden from every other viewer surface; either 404 them for non-admins or label clearly.
- The service worker caches `/api/ridb/availability` responses and replays them on network failure with no staleness marker (`static/sw.js:216-217`) — showing last week's campsite openings as current, contradicting the server's own "always live" comment. Also: one campground-map entry (~7-9 MB decoded) can evict 20+ trip pages from the 80-entry PAGE_CACHE; photos are cache-first forever (caption edits never reach a viewer who cached the trip).
- Several pages lack empty states: calendar year (list view has one, calendar view doesn't), stats (wall of zeros), landing map with no trips (gray broken box if bounds empty — needs `setView` fallback + message).
- No Open Graph / meta description tags, so a share link pasted into iMessage/WhatsApp renders as a bare URL — the guest's literal first impression.
- Availability page: shows raw "RIDB_API_KEY not configured on the server" to viewers; lets users pick a 4-month range the server rejects after the round trip (client should cap at 92 nights); results not deep-linkable and `?cg=` prefill doesn't auto-run; search dropdown is mouse-only (the map's search has keyboard nav — inconsistent); jargon copy ("EKKO-friendly", three different length numbers on one screen); 93-column table unusable on phones (needs per-night summary + mobile list view); returned `facility.lat/lng/map_url` all unused (no locator map / layout-map link).
- Error/offline pages: `offline.html` has no links at all (only reload — add `/` and `/sw-reset`); `error.html` 500 recovery points only at `/` (the heaviest page, possibly the one that broke — add `/trips/list`); photo 404s return full HTML into `<img>` tags.
- Calendar view-switch uses `replaceState` so Back exits the page; all calendar dots are the same color (kind-coloring loop is a no-op, `trips_calendar.html:539-541`); rich hover tooltip has no touch equivalent.
- Landing page: `leaflet.js` and `tile-layers.js` load render-blocking in `<head>` (no `defer`) on the app's default route; no map loading skeleton.
- Login page: no help/recovery text, no password-visibility toggle; `inject_trip_stats` runs a full `parse_trips()` even for unauthenticated requests (`ekko_trips_app.py:257`); SW registers on the login page for users who never get in.
- Stats page recomputes from scratch per request (per-stay `os.listdir` + full campground scan, `ekko_trips_app.py:1660-1669`, `:1774-1789`) — cache keyed on trip-data mtime like `_collect_photo_pool`.
- Share-guest onboarding: nothing tells a first-time guest what this is or how to browse — a one-time dismissible welcome card would cover it.
- Dead code/bytes: admin-only CSS block ships to viewers on the campground map (`campground_map.html:~336-470`); unused `is_admin` arg to `campground_availability.html` (`ekko_trips_app.py:2424`).

## What's working well (calibration — don't regress these)

- The hand-rolled lightbox gesture engine (pinch/pan/double-tap/swipe with mouse parity, correct dblclick suppression and pan-release click swallowing).
- Staged thumbnail pipeline (lazy 480px thumbs over aspect-ratio skeletons, EXIF rotation baked in) and graceful GPS-track fallback to the straight-line route.
- The gzip `after_request` hook and Save-Data-aware prefetch skipping (`PREFETCH_SKIP` + frugal check).
- The OSRM route tool's two-stage real-detour ranking of roadside stops; mobile aim-pin flow.
- "Latest trip" / "On this day" landing banners (answer the primary viewer intent above the fold, kept on phones).
- Prev/next trip navigation that filters `home_only` for non-admins so chevrons never land on a hidden page.
- 12,872-marker rendering discipline (preferCanvas, zoom-tier resize, percentile-trimmed mobile fit).

## Prioritized backlog

### Batch 1 — quick wins, big effect
- [ ] `abort(404)` in `trip_detail` instead of bare text 404 (`ekko_trips_app.py:1797`)
- [ ] Hide/replace Logout for `share:` sessions (`base.html:433`); add "viewing as guest" chip via `_share_label()`
- [ ] Fix the two UTC date bugs in the calendar (`trips_calendar.html:558`, `:530-531`)
- [ ] Lightbox download from `dataset.full`, not live `img.src` (`static/lightbox.js:252-264`)
- [ ] Gate the four admin JS files + hidden edit forms on `is_admin` (`trip_detail.html:2312-2318` etc.)
- [ ] Toast/notice on the Trips-only redirect (`ekko_trips_app.py:1112-1118`); gate legacy campground routes
- [ ] Unify the day-trip count helper (header vs stats)

### Batch 2 — one afternoon each
- [ ] ETag/304 for `/campgrounds/map` keyed on `_campgrounds_derived_cache` mtimes
- [ ] Slim campground-map marker payload + `/api/campgrounds/<id>/popup` lazy fetch (drop `note`/`website`/`delta_temp`/`kind` from the inline blob)
- [ ] Revoked-share-link page that isn't a login form; fall back to stored `rec["next"]` in `share_login`
- [ ] Loading indicators: campground map build, availability check (spinner + `aria-live`), landing map skeleton
- [ ] Directions links in campground popups; popup `maxHeight` for phones
- [ ] Lightbox: loading spinner for originals, `N / M` counter, alt from caption, Save-Data-aware preloading
- [ ] Trip-detail map: tooltips/legend for markers, "Fit trip" reset button, itinerary-only initial bounds, mobile scroll-trap fix
- [ ] Full-state-name search + state filter + "showing N of M" on the campground map; un-persist master-toggle-off trap
- [ ] Link `/trips/poster` from Stats; add Print button + back link to the poster
- [ ] a11y sweep: aria-labels on glyph buttons, aria-live on toasts, carousel pause + reduced-motion, keyboard-operable legend rows, touch-target padding on nav links/chevrons

### Batch 3 — bigger features worth considering
- [ ] Cross-trip photo gallery (`/trips/photos` over `_collect_photo_pool()`), linked from the Stats photo count
- [ ] Trip search surfaced on the landing page (haystack machinery already exists); "All years" list view
- [ ] Day dividers in the trip timeline; photo "+N more" expander; mobile header stat restoration
- [ ] Guest welcome card on first share-session page load; Open Graph tags for link previews
- [ ] Mid-size (~1600px) photo derivative for the lightbox
- [ ] Availability page overhaul: client-side range cap, deep-linkable results, auto-run on `?cg=`, mobile summary view, keyboard dropdown, de-jargoned copy
- [ ] Stats-page links (year bars → calendar, campspots/states → search) + stats caching
