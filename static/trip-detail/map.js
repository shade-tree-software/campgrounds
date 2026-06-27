// ── Trip-header height + map column sync ─────────────────────────────────
// Publish the trip-header height as --trip-header-height so the fixed map
// column (two-col layout) can offset itself below the red header bar.
(function() {
  const header = document.querySelector('.trip-header');
  if (!header) return;
  const update = () => {
    document.documentElement.style.setProperty(
      '--trip-header-height', header.offsetHeight + 'px');
    syncMapColumnPosition();
    if (window.tripMap) window.tripMap.invalidateSize();
  };
  update();
  window.addEventListener('resize', update);
})();

// Sync the position:fixed map wrapper to its grid placeholder so it
// occupies exactly the left grid column. Runs on load + resize only;
// scrolling does not move the map (which is the whole point).
function syncMapColumnPosition() {
  const placeholder = document.querySelector('.content.two-col .map-column');
  const fixed = document.querySelector('.content.two-col .map-column-fixed');
  if (!placeholder || !fixed) return;
  if (window.matchMedia('(max-width: 900px)').matches) {
    fixed.style.left = '';
    fixed.style.width = '';
    return;
  }
  const rect = placeholder.getBoundingClientRect();
  fixed.style.left = rect.left + 'px';
  fixed.style.width = rect.width + 'px';
}
window.addEventListener('resize', syncMapColumnPosition);
window.addEventListener('load', syncMapColumnPosition);
syncMapColumnPosition();

// Smooth-scroll a card into view, accounting for the sticky site-top
// and trip-header so the card title doesn't end up hidden behind them.
// Also briefly glow the destination card so it's obvious where the
// scroll landed (used by marker click → card scroll, and any other call site).
function scrollToCard(cardId) {
  const el = document.getElementById(cardId);
  if (!el) return;
  const rs = getComputedStyle(document.documentElement);
  const siteTop = parseFloat(rs.getPropertyValue('--site-top-height')) || 0;
  const tripHdr = parseFloat(rs.getPropertyValue('--trip-header-height')) || 0;
  const target = window.scrollY + el.getBoundingClientRect().top - siteTop - tripHdr - 16;
  window.scrollTo({ top: target, behavior: 'smooth' });

  // Restart the highlight animation by toggling the class.
  el.classList.remove('card-highlight');
  void el.offsetWidth;
  el.classList.add('card-highlight');
  setTimeout(() => el.classList.remove('card-highlight'), 2200);
}

// Briefly pulse the marker associated with a card id (used by card click
// → map zoom). cardMarkers is populated alongside cardTargets when each
// marker is created; for grouped family-visit markers, every event id
// in the group points to the same shared marker.
function highlightMarker(cardId) {
  const marker = window.tripCardMarkers && window.tripCardMarkers[cardId];
  if (!marker) return;
  const el = marker.getElement && marker.getElement();
  if (!el) return;
  el.classList.remove('marker-pulse');
  void el.offsetWidth;
  el.classList.add('marker-pulse');
  setTimeout(() => el.classList.remove('marker-pulse'), 2400);
}

// Click a card → center & zoom the map on its marker, then pulse the marker.
// Copy ids (stay-3-2) resolve to their base stay (stay-3).
document.querySelectorAll('.stay-card, .event-card').forEach(card => {
  card.addEventListener('click', (e) => {
    if (e.target.closest('a, button, img, input, textarea, select, label')) return;
    const id = card.id || '';
    const m = id.match(/^stay-(\d+)-\d+$/);
    const lookupId = m ? 'stay-' + m[1] : id;
    const ll = window.tripCardTargets && window.tripCardTargets[lookupId];
    if (ll && window.tripMap) {
      window.tripMap.setView(ll, 14, { animate: true });
      highlightMarker(lookupId);
    }
  });
});


// ── Map view persistence, GPS track refetch, full Leaflet map init ────
// Point the Calendar/List nav links at this trip's year. The calendar/list
// page reads the year from the URL hash (#YYYY) and clamps it to its valid
// range, so an out-of-range or absent year degrades to that page's default.
(function linkNavToTripYear() {
  const year = (TRIP_START || '').slice(0, 4);
  if (!/^\d{4}$/.test(year)) return;  // empty trips have no date range
  for (const id of ['nav-calendar', 'nav-list']) {
    const a = document.getElementById(id);
    if (a) a.href = a.href.split('#')[0] + '#' + year;
  }
})();

// Per-trip, per-tab map view (center + zoom). Captured on every page unload
// AND consulted on load — but only when the reload was a programmatic one
// (suppress / relocate / set campsite / event from selection / etc.). A
// manual F5 / Cmd-R or a navigation to a different trip falls through to
// the fitBounds default so the user gets a fresh "show the whole trip" view.
//
// The distinction is signalled with a one-shot session flag (`_KEEP_KEY`):
// every programmatic reload routes through `_reloadKeepingMapView()`, which
// sets the flag right before `location.reload()`. `_loadMapView()` consumes
// the flag synchronously on the next load — present → restore the saved
// view; absent → return null and let the caller auto-fit.
//
// Different trips get different `_MAP_VIEW_KEY`s, so cross-trip navigation
// can't pull up a stale view; the keep flag is global within the tab so any
// stray persistence (e.g. tab navigation interrupted mid-reload) gets eaten
// on the very next load and can't poison future visits. sessionStorage is
// per tab so a fresh tab always opens with the auto-fit.
const _MAP_VIEW_KEY = `tripMapView:${TRIP_ID}`;
const _MAP_VIEW_KEEP_KEY = 'tripMapViewKeep';
function _saveMapView() {
  if (!window.tripMap) return;
  try {
    const c = window.tripMap.getCenter();
    sessionStorage.setItem(_MAP_VIEW_KEY, JSON.stringify({
      lat: c.lat, lng: c.lng, zoom: window.tripMap.getZoom(),
    }));
  } catch (_) { /* sessionStorage may be disabled or full — fine, fall back to fitBounds */ }
}
function _loadMapView() {
  try {
    // Consume the keep flag unconditionally so a leftover from an aborted
    // reload can't make the very next load restore a stale view.
    const keep = sessionStorage.getItem(_MAP_VIEW_KEEP_KEY);
    sessionStorage.removeItem(_MAP_VIEW_KEEP_KEY);
    if (!keep) return null;
    const raw = sessionStorage.getItem(_MAP_VIEW_KEY);
    if (!raw) return null;
    const v = JSON.parse(raw);
    if (typeof v.lat !== 'number' || typeof v.lng !== 'number' || typeof v.zoom !== 'number') return null;
    return v;
  } catch (_) { return null; }
}
// Programmatic-reload helper used by every "save → reload" mutation flow on
// this page. Sets the keep flag synchronously so the post-reload load picks
// up the current view; manual F5 / link navigation never goes through here
// and therefore falls back to fitBounds.
function _reloadKeepingMapView() {
  try { sessionStorage.setItem(_MAP_VIEW_KEEP_KEY, '1'); } catch (_) {}
  // NB: `window.location.reload()` (not the bare `location.reload()`) so this
  // line survives any future global rename of the latter.
  window.location.reload();
}
window.addEventListener('beforeunload', _saveMapView);

// Refetch the GPS-track payload and re-render the map's GPS layers in place
// (polyline, per-point markers, suppressed/relocated ghost layers). Used by
// the GPS-only mutation flows — suppress / unsuppress / relocate /
// unrelocate — so they don't trigger a full page reload (and therefore
// don't need the saved-view dance above). Mutations that change stay/event
// data still go through `_reloadKeepingMapView()` because the cards and
// stay markers are server-rendered and would need fresh HTML.
// Sum haversine segments along the polyline → miles → header chip.
// Hidden when the polyline is empty / has only one point (no GPS track
// rendered this load).
function computeAndShowGpsMiles(latlngs) {
  const el = document.getElementById('trip-gps-miles');
  if (!el) return;
  if (!latlngs || latlngs.length < 2) { el.style.display = 'none'; return; }
  const R_KM = 6371;
  const toRad = d => d * Math.PI / 180;
  let km = 0;
  for (let i = 1; i < latlngs.length; i++) {
    const [la1, lo1] = latlngs[i - 1];
    const [la2, lo2] = latlngs[i];
    const dLa = toRad(la2 - la1);
    const dLo = toRad(lo2 - lo1);
    const a = Math.sin(dLa / 2) ** 2
            + Math.cos(toRad(la1)) * Math.cos(toRad(la2)) * Math.sin(dLo / 2) ** 2;
    km += 2 * R_KM * Math.asin(Math.sqrt(a));
  }
  const miles = km * 0.621371;
  el.querySelector('span').textContent = miles >= 100 ? Math.round(miles) : miles.toFixed(1);
  el.style.display = '';
}

function refetchAndRenderTrack() {
  if (!window.__renderGpsTrack) return Promise.resolve();
  // Clear any active ping selection so a freshly-suppressed batch doesn't
  // leave the user with a stale "X pings selected" toolbar referring to
  // markers that no longer exist after re-render.
  const selToggle = document.getElementById('selection-mode-toggle');
  if (selToggle && selToggle.checked) {
    selToggle.checked = false;
    toggleSelectionMode(selToggle);
  }
  const url = `/api/trips/${TRIP_ID}/track${IS_ADMIN ? '?admin=1' : ''}`;
  return fetch(url, { credentials: 'same-origin' })
    .then(r => r.ok ? r.json() : { __error: { status: r.status, statusText: r.statusText } })
    .then(window.__renderGpsTrack)
    .catch(err => console.log(`[trip-track] trip ${TRIP_ID}: refetch threw an error`, err));
}
window.__refetchAndRenderTrack = refetchAndRenderTrack;

// ── Map initialization ─────────────────────────────────────────────────────��
(function() {
  // Attach the original array index so popup actions can address each item
  // (filtering by lat/lng would otherwise lose the position).
  const stays = STAYS_ALL.map((s, i) => Object.assign({}, s, { idx: i }));
  const events = EVENTS_ALL.map((e, i) => Object.assign({}, e, { idx: i }));
  const mapped = stays.filter(s => s.lat && s.lng);
  const mappedEvents = events.filter(e => e.lat && e.lng);
  if (mapped.length === 0 && mappedEvents.length === 0) return;

  const map = L.map('trip-map');
  window.tripMap = map;
  // Dedicated SVG pane for the suppressed/relocated ghost layers so they
  // render above every regular marker (markerPane is zIndex 600; this sits
  // above home/family/stay/event icons so admins can always click through to
  // unsuppress/unrelocate even when an override sits at the same coords as a
  // stay or family location).
  map.createPane('overrides').style.zIndex = 700;
  const streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map);
  const satellite = L.layerGroup([
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: '&copy; Esri',
      maxZoom: 19,
    }),
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
    }),
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
    }),
  ]);
  const baseLayers = { 'Map': streets, 'Satellite': satellite };
  const overlayLayers = {};
  const layerControl = L.control.layers(baseLayers, overlayLayers).addTo(map);

  const HOME = HOME_COORDS;
  const bounds = [HOME];

  // Lookup: card id → [lat, lng] for click-to-focus on the map
  const cardTargets = {};
  const cardMarkers = {};
  window.tripCardTargets = cardTargets;
  window.tripCardMarkers = cardMarkers;
  cardTargets['home-card-start'] = HOME;
  cardTargets['home-card-end'] = HOME;

  // Home marker
  const homeIcon = L.divIcon({
    className: '',
    html: `<div style="
      width:24px;height:24px;border-radius:50%;
      background:#bf0a30;
      display:flex;align-items:center;justify-content:center;
      border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
    "><svg width="14" height="14" viewBox="0 0 20 20" fill="#fff"><path d="M10 2 L2 9 L5 9 L5 17 L9 17 L9 12 L11 12 L11 17 L15 17 L15 9 L18 9 Z"/></svg></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
  const homeMarker = L.marker(HOME, { icon: homeIcon, zIndexOffset: 1000 })
    .addTo(map)
    .on('click', () => scrollToCard('home-card-start'));
  cardMarkers['home-card-start'] = homeMarker;
  cardMarkers['home-card-end'] = homeMarker;

  mapped.forEach((stay, i) => {
    const ll = [stay.lat, stay.lng];
    bounds.push(ll);

    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:24px;height:24px;border-radius:50%;
        background:#002868;color:#fff;
        display:flex;align-items:center;justify-content:center;
        font-size:12px;font-weight:700;
        border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
      ">${i + 1}</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    const stayMarker = L.marker(ll, { icon, zIndexOffset: 800 })
      .addTo(map)
      .on('click', () => scrollToCard('stay-' + stay.idx));
    cardTargets['stay-' + stay.idx] = ll;
    cardMarkers['stay-' + stay.idx] = stayMarker;
  });

  // Build day-by-day chronological route
  // Morning location: stay where start < date <= end (you slept there). Else HOME.
  // Evening location: stay where start <= date < end (you sleep there tonight). Else HOME.
  function morningLocation(dateStr) {
    for (const s of mapped) {
      if (s.start < dateStr && dateStr <= s.end) return [s.lat, s.lng];
    }
    return HOME;
  }
  function eveningLocation(dateStr) {
    for (const s of mapped) {
      if (s.start <= dateStr && dateStr < s.end) return [s.lat, s.lng];
    }
    return HOME;
  }

  // Collect all dates in the trip (stay date ranges + event dates)
  const allDates = new Set();
  mapped.forEach(s => {
    let d = new Date(s.start + 'T00:00:00');
    const end = new Date(s.end + 'T00:00:00');
    while (d <= end) {
      allDates.add(d.toISOString().slice(0, 10));
      d.setDate(d.getDate() + 1);
    }
  });
  mappedEvents.forEach(e => allDates.add(e.date));
  const sortedDates = [...allDates].sort();

  // For each day: morning location → events/waypoints sorted by time → evening location.
  // Skip days in the future so the dashed route never draws connecting lines to
  // not-yet-happened events, stays, or the return-trip-home leg (an upcoming /
  // in-progress trip shows the route only up through today).
  const todayStr = (() => {
    const n = new Date();
    return n.getFullYear() + '-' + String(n.getMonth() + 1).padStart(2, '0') +
      '-' + String(n.getDate()).padStart(2, '0');
  })();
  const routePath = [];
  function pushIfNew(pt) {
    const last = routePath[routePath.length - 1];
    if (!last || pt[0] !== last[0] || pt[1] !== last[1]) {
      routePath.push(pt);
    }
  }
  sortedDates.forEach(dateStr => {
    if (dateStr > todayStr) return;  // future item — draw no connecting line to it
    const morning = morningLocation(dateStr);
    const evening = eveningLocation(dateStr);
    const dayEvents = mappedEvents
      .filter(e => e.date === dateStr)
      .sort((a, b) => (a.time || '12:00').localeCompare(b.time || '12:00'));

    pushIfNew(morning);
    dayEvents.forEach(evt => pushIfNew([evt.lat, evt.lng]));
    pushIfNew(evening);
  });

  // Draw straight-line route; show it immediately as the default while we
  // wait on the GPS track. If the GPS track loads, swap it in (the user can
  // still toggle either via the layer control).
  let straightRouteLayer = null;
  if (routePath.length >= 2) {
    straightRouteLayer = L.layerGroup([
      L.polyline(routePath, { color: '#fff', weight: 5, opacity: 0.6 }),
      L.polyline(routePath, {
        color: '#002868',
        weight: 3,
        opacity: 0.8,
        dashArray: '8,10',
      }),
    ]);
    layerControl.addOverlay(straightRouteLayer, 'Straight route');
    straightRouteLayer.addTo(map);
  }

  // ── Trip window padding ─────────────────────────────────────────────────
  // The trip's home-departure / home-arrival tsts are computed server-side
  // (_find_home_boundary_tsts) and arrive in the track payload; the frontend
  // no longer recomputes them. computeTripWindow() below turns them (or the
  // manual HOME_START_TIME / HOME_END_TIME overrides) into polyline cuts.
  const BOUNDARY_PAD_MAX_S = 90 * 60;        // the leaving/arriving-home pad ping
                                             // (one ping just outside the window)
                                             // is only added when it sits within
                                             // this much time of the cut. With a
                                             // tight manual home window the nearest
                                             // outside ping can be hours/days away
                                             // (trip 87: a 15:51 at-home blip and a
                                             // next-morning 08:34 ping), which is
                                             // not a boundary leg — it's a stale
                                             // jump. Beyond this cap we skip the
                                             // pad and let the HOME/anchor gap-fill
                                             // draw the edge leg instead. Same
                                             // "what counts as a real gap" notion
                                             // as GAP_FILL_MIN_S.
  function distMeters(a, b) {
    const latKm = (a[0] - b[0]) * 111;
    const lngKm = (a[1] - b[1]) * 111 *
                  Math.cos(((a[0] + b[0]) / 2) * Math.PI / 180);
    return Math.sqrt(latKm * latKm + lngKm * lngKm) * 1000;
  }
  function localDateOf(tst) {
    const d = new Date(tst * 1000);
    return d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' +
      String(d.getDate()).padStart(2, '0');
  }
  function formatHM(tst) {
    const d = new Date(tst * 1000);
    const h = d.getHours();
    const suffix = h < 12 ? 'AM' : 'PM';
    const h12 = h % 12 || 12;
    return h12 + ':' + String(d.getMinutes()).padStart(2, '0') + ' ' + suffix;
  }
  // Build a browser-local epoch (seconds) for "YYYY-MM-DD" + "HH:MM".
  // Used to bound the trip window when filtering pings; tz-aware
  // conversion was retired with geo-suppression so we accept the small
  // skew when viewing a far-away trip.
  function localEpoch(dateStr, timeStr) {
    if (!dateStr || !timeStr) return null;
    const [y, m, d] = dateStr.split('-').map(Number);
    const [hh, mm] = timeStr.split(':').map(Number);
    if ([y, m, d, hh, mm].some(isNaN)) return null;
    return new Date(y, m - 1, d, hh, mm, 0).getTime() / 1000;
  }
  function addDaysISO(dateStr, n) {
    const [y, m, d] = dateStr.split('-').map(Number);
    const t = Date.UTC(y, m - 1, d) + n * 86400000;
    const dt = new Date(t);
    return dt.getUTCFullYear() + '-'
         + String(dt.getUTCMonth() + 1).padStart(2, '0') + '-'
         + String(dt.getUTCDate()).padStart(2, '0');
  }
  // Resolve the trip window [lowerCut, upperCut] in epoch seconds. Manual
  // home_start_time / home_end_time win; auto-detected boundaries fill in
  // when no manual override is set; full local days bracket the window
  // when neither is available.
  function computeTripWindow(autoHomeStartTst, autoHomeEndTst) {
    let lowerCut = null, upperCut = null;
    if (TRIP_START) {
      if (HOME_START_TIME) lowerCut = localEpoch(TRIP_START, HOME_START_TIME);
      else if (autoHomeStartTst != null) lowerCut = autoHomeStartTst;
      else lowerCut = localEpoch(TRIP_START, '00:00');
    }
    if (TRIP_END) {
      if (HOME_END_TIME) upperCut = localEpoch(TRIP_END, HOME_END_TIME);
      else if (autoHomeEndTst != null) upperCut = autoHomeEndTst;
      else upperCut = localEpoch(addDaysISO(TRIP_END, 1), '00:00');
    }
    return { lowerCut, upperCut };
  }

  // Populate the home cards' time display: manual override (rendered server-
  // side) wins; otherwise show the GPS-derived time with an "(auto)" suffix
  // so admins know they can override it via Edit if it looks wrong. Stored
  // on window so editHomeTime() can show the auto value as the prompt default.
  function updateHomeTimeDisplay(which, autoTst) {
    const span = document.getElementById(`home-${which}-time-display`);
    if (!span) return;
    const manual = which === 'start' ? HOME_START_TIME : HOME_END_TIME;
    if (manual) return;
    if (autoTst == null) return;
    const hm = formatHM(autoTst);
    span.textContent = IS_ADMIN ? ` · ${hm} (auto)` : ` · ${hm}`;
    if (which === 'start') window.HOME_START_TIME_AUTO = hm;
    else window.HOME_END_TIME_AUTO = hm;
  }

  // Render the GPS track as the raw, unfiltered polyline of every returned
  // ping (sorted by timestamp). Markers for stays/events/home/family are
  // placed independently — the polyline is not anchored to or trimmed
  // against any of them. Spurious cell-tower pings and single jumps are
  // filtered upstream by a separate pre-processing app.
  //
  // Two automatic short-circuits leave the dashed straight-line route as the
  // only polyline: (1) the fetch fails / returns nothing in the trip window,
  // (2) no in-window ping lands within TRACK_NEAR_STAY_KM of any anchor.
  const trackLog = (msg, extra) => console.log(
    `[trip-track] trip ${TRIP_ID}: ${msg}`, extra ?? '');

  // Render (or re-render) the GPS track from a raw-points payload. Idempotent:
  // tears down any previously-rendered GPS layers (polyline, per-point markers,
  // suppressed/relocated ghost layers, sync handlers) before rebuilding, so
  // suppress / unsuppress / relocate / unrelocate flows can refresh the map
  // in place via `window.__refetchAndRenderTrack` instead of doing a full
  // `location.reload()`. Closes over `map`, `layerControl`, `straightRouteLayer`,
  // `mapped`, `mappedEvents`, and the home/window helper functions.
  function renderGpsTrack(rawPoints) {
    // ── Teardown any previously-rendered GPS layers ────────────────────────
    if (window.__gpsRouteLayer) {
      if (map.hasLayer(window.__gpsRouteLayer)) map.removeLayer(window.__gpsRouteLayer);
      layerControl.removeLayer(window.__gpsRouteLayer);
      window.__gpsRouteLayer = null;
    }
    if (window.__gpsPointLayer) {
      if (map.hasLayer(window.__gpsPointLayer)) map.removeLayer(window.__gpsPointLayer);
      window.__gpsPointLayer = null;
    }
    if (window.__suppressedPointLayer && map.hasLayer(window.__suppressedPointLayer)) {
      map.removeLayer(window.__suppressedPointLayer);
    }
    if (window.__relocatedPointLayer && map.hasLayer(window.__relocatedPointLayer)) {
      map.removeLayer(window.__relocatedPointLayer);
    }
    if (window.__syncGpsPoints) {
      map.off('zoomend', window.__syncGpsPoints);
      map.off('overlayadd overlayremove', window.__syncGpsPoints);
      window.__syncGpsPoints = null;
    }
    if (window.__currentLocationMarker) {
      if (map.hasLayer(window.__currentLocationMarker)) map.removeLayer(window.__currentLocationMarker);
      window.__currentLocationMarker = null;
    }
    // The straight-line route is the visible default whenever no GPS polyline
    // is up. A previous GPS render may have removed it; restore it now and
    // let a successful new GPS render re-hide it if appropriate.
    if (straightRouteLayer && !map.hasLayer(straightRouteLayer)) {
      straightRouteLayer.addTo(map);
    }

    if (rawPoints && rawPoints.__error) {
      const e = rawPoints.__error;
      if (e.status != null) trackLog(`track fetch returned non-OK status ${e.status} ${e.statusText} — using straight track`);
      else trackLog('GPS track fetch threw an error — using straight track', e.thrown);
      return;
    }
    // The track endpoint returns { points, home_auto_start_tst,
    // home_auto_end_tst }. Legacy/degenerate responses (no token + no
    // cache, or no trip dates) are still a bare [] array; the __error
    // case above is an object with no `points`. Normalize all three.
    const payloadObj = (rawPoints && !Array.isArray(rawPoints)
      && Array.isArray(rawPoints.points)) ? rawPoints : null;
    const rawAll = Array.isArray(rawPoints) ? rawPoints
      : (payloadObj ? payloadObj.points : []);
    // Suppressed pings are kept out of the polyline / home-boundary detection
    // / regular per-point markers entirely; they're rendered separately as
    // gray "ghost" dots that the admin can toggle on via the "Show suppressed
    // pings" checkbox and click to unsuppress. (For non-admins the server
    // already filtered them out, so `suppressed` is never set.)
    // Bad-window pings (from `bad_track_windows` on the trip — admin-marked
    // ranges where the phone was off-trip with the wrong person) are dropped
    // the same way: filtered out for non-admins by the server, tagged
    // `bad_window: true` for admins and stripped here so they don't pollute
    // the polyline or the home-boundary auto-detection. No ghost layer for
    // them currently — the feature is rare enough that the admin edits
    // trips.json by hand instead of having a UI.
    // Relocated pings, by contrast, ARE in the polyline — at their override
    // coords (the server already rewrote lat/lon). For admins they also
    // carry `original_lat`/`original_lon` so the "Show relocated pings"
    // toggle can mark them and draw a dashed line back to the source.
    const raw = rawAll.filter(p => !p.suppressed && !p.bad_window);
    const rawSuppressed = rawAll.filter(p => p.suppressed);
    const rawRelocated = rawAll.filter(p => p.relocated && !p.suppressed);
    // Trip-start/end times are computed server-side by
    // _find_home_boundary_tsts and returned in the payload — the single
    // source of truth (the frontend used to recompute this and could
    // drift from the Python detector). A bare-array legacy/empty
    // response carries no boundary; leave the server-rendered home-card
    // time untouched in that case.
    const autoHomeStartTst = payloadObj ? payloadObj.home_auto_start_tst : null;
    const autoHomeEndTst = payloadObj ? payloadObj.home_auto_end_tst : null;
    if (payloadObj) {
      if (TRIP_START && !HOME_START_TIME) updateHomeTimeDisplay('start', autoHomeStartTst);
      if (TRIP_END && !HOME_END_TIME) updateHomeTimeDisplay('end', autoHomeEndTst);
    }
    // Filter pings to the trip window so the polyline and per-point
    // markers don't show pre-departure or post-arrival activity.
    const { lowerCut, upperCut } = computeTripWindow(autoHomeStartTst, autoHomeEndTst);
    const inWindow = raw.filter(p =>
      (lowerCut == null || p.tst >= lowerCut) &&
      (upperCut == null || p.tst <= upperCut));

    // Build the suppressed / relocated ghost layers and wire their "Show …"
    // toggles BEFORE the polyline short-circuits below. If the trip has no
    // good in-window pings (or none near a stay), the GPS track is skipped
    // — but the admin still needs a way to surface and undo any suppressed
    // or relocated pings the trip carries.
    //
    // Note: we deliberately pass the UNWINDOWED `rawSuppressed`/`rawRelocated`
    // lists. A suppressed/relocated ping that falls just outside the
    // auto-detected trip window (e.g. the ping tst is a few minutes before
    // `autoHomeStartTst`) would otherwise drop from the ghost layer and
    // leave the toggle disabled, with no way for the admin to undo it.
    // Polyline state is the only thing that needs the window filter.
    trackLog('ping counts',
      { rawAll: rawAll.length, raw: raw.length,
        suppressed: rawSuppressed.length, relocated: rawRelocated.length });
    _buildSuppressedRelocatedLayers(rawSuppressed, rawRelocated);

    if (inWindow.length < 2) {
      trackLog('not enough in-window GPS points to draw a track — using straight track',
        { rawCount: raw.length, inWindowCount: inWindow.length, lowerCut, upperCut });
      return;
    }

    // Auto-fallback: skip the GPS layer (leaving the dashed straight-
    // line route as the only polyline) when the GPS data doesn't
    // actually cover this trip.
    //
    // The strict gate is: at least one in-window ping must land within
    // TRACK_NEAR_STAY_KM (5 km) of a stay/event anchor. If the phone
    // never reached anywhere on the itinerary, the data isn't of this
    // trip — even if it moved around (driving to unrelated places on
    // those dates). That's the trip-61 case: primary roamed away from
    // home on a non-trip errand but never went near the trip's stay.
    //
    // We relax the gate for in-progress trips only: if the trip is
    // still happening (now is on or before TRIP_END's local day) AND
    // at least one in-window ping is more than 5 km from HOME, we let
    // it through. This covers an in-progress drive toward a distant
    // sole anchor (trip 90) — the user can watch the polyline build
    // in real time before reaching the destination. Once the trip's
    // end day is past, the relaxation drops away: if no anchor was
    // ever reached, the data was the wrong device or wrong period.
    const TRACK_NEAR_STAY_KM = 5;
    const radiusM = TRACK_NEAR_STAY_KM * 1000;
    const anchorCoords = [
      ...mapped.map(s => [s.lat, s.lng]),
      ...mappedEvents.map(e => [e.lat, e.lng]),
    ].filter(([la, ln]) => Number.isFinite(la) && Number.isFinite(ln));
    const homeValid = Array.isArray(HOME) &&
      Number.isFinite(HOME[0]) && Number.isFinite(HOME[1]);
    if (anchorCoords.length || homeValid) {
      const nearAnchor = anchorCoords.length > 0 && inWindow.some(p =>
        anchorCoords.some(c => distMeters([p.lat, p.lon], c) <= radiusM));
      const tripInProgress = !!TRIP_END &&
        new Date(TRIP_END + 'T23:59:59').getTime() >= Date.now();
      const movedFromHome = tripInProgress && homeValid && inWindow.some(p =>
        distMeters([p.lat, p.lon], HOME) > radiusM);
      if (!nearAnchor && !movedFromHome) {
        trackLog(
          `no GPS ping reached an anchor (and trip is not in progress) — using straight track`,
          { inWindowCount: inWindow.length, anchorCount: anchorCoords.length,
            tripInProgress });
        return;
      }
    }

    // Pad the polyline by one ping at each boundary so it starts with a
    // "leaving home" leg and ends with an "arriving home" leg instead of
    // snapping in at the locked departure point and out at the locked
    // arrival point. For auto-detected boundaries the extra ping is the
    // last at-home / first back-at-home reading; for manual HOME_START_TIME
    // / HOME_END_TIME overrides it's whatever the user logged just outside
    // that timestamp. We pad *after* the < 2 and near-stay gates so a trip
    // with no real in-window data still falls back to the straight route
    // (boundary pings would be at home, never near a stay, so they can't
    // tip those checks on their own).
    if (lowerCut != null) {
      let beforeLower = null;
      for (const p of raw) {
        if (p.tst < lowerCut && (!beforeLower || p.tst > beforeLower.tst)) {
          beforeLower = p;
        }
      }
      // Only pad when the ping is close enough in time to the cut to be a
      // genuine "leaving home" leg. A far-away nearest-outside ping (tight
      // manual window with at-home gaps) would otherwise draw a long stale
      // jump; the leading HOME/anchor gap-fill covers that edge instead.
      if (beforeLower && lowerCut - beforeLower.tst <= BOUNDARY_PAD_MAX_S) {
        inWindow.push(beforeLower);
      }
    }
    if (upperCut != null) {
      let afterUpper = null;
      for (const p of raw) {
        if (p.tst > upperCut && (!afterUpper || p.tst < afterUpper.tst)) {
          afterUpper = p;
        }
      }
      if (afterUpper && afterUpper.tst - upperCut <= BOUNDARY_PAD_MAX_S) {
        inWindow.push(afterUpper);
      }
    }

    const sorted = inWindow.slice().sort((a, b) => a.tst - b.tst);

    // Gap-fill the polyline with planned stops. When good GPS only covers
    // part of the trip — because of a `bad_track_windows` entry or simply a
    // stretch with no logged geos — the Leaflet polyline would otherwise
    // draw a single straight line across the gap (last good ping → first
    // good ping). Instead, for any period not covered by good pings, route
    // the line through the trip's own anchors (stay nights, events,
    // waypoints, family visits, and HOME at the trip edges) that fall
    // chronologically inside that period, in time order.
    //
    // We reuse the same day-by-day morning→events→evening walk that builds
    // the dashed "Straight route" overlay, but stamp each anchor with a
    // timestamp so it can be sliced into a time gap. Anchors are injected
    // for the leading gap (before the first good ping) and trailing gap
    // (after the last) unconditionally — there the only candidate is
    // usually HOME at the trip edge, which is coincident with the at-home
    // boundary-pad ping for a well-tracked trip, so a normal trip is
    // unaffected. Interior gaps only inject when the gap between two
    // consecutive good pings is at least GAP_FILL_MIN_S, so routine sparse
    // OwnTracks logging (idle hours at a campground, where the only anchors
    // are that same campground location anyway) doesn't add detours.
    const GAP_FILL_MIN_S = 90 * 60;
    const routeStops = [];
    function pushStop(tst, pt) {
      if (tst == null || !pt) return;
      const last = routeStops[routeStops.length - 1];
      // Collapse consecutive same-coord anchors (e.g. a stay's evening and
      // the next morning); keep the earlier tst for ordering.
      if (last && pt[0] === last.ll[0] && pt[1] === last.ll[1]) return;
      routeStops.push({ tst, ll: pt });
    }
    sortedDates.forEach(dateStr => {
      if (dateStr > todayStr) return;  // don't gap-fill toward future (unvisited) anchors
      pushStop(localEpoch(dateStr, '00:00'), morningLocation(dateStr));
      mappedEvents
        .filter(e => e.date === dateStr)
        .sort((a, b) => (a.time || '12:00').localeCompare(b.time || '12:00'))
        .forEach(evt => pushStop(localEpoch(dateStr, evt.time || '12:00'),
                                 [evt.lat, evt.lng]));
      pushStop(localEpoch(dateStr, '23:59'), eveningLocation(dateStr));
    });

    const latlngs = [];
    function pushLL(pt) {
      const last = latlngs[latlngs.length - 1];
      if (last && pt[0] === last[0] && pt[1] === last[1]) return;
      latlngs.push(pt);
    }
    const firstTst = sorted[0].tst;
    const lastTst = sorted[sorted.length - 1].tst;
    routeStops.filter(s => s.tst < firstTst).forEach(s => pushLL(s.ll));
    for (let i = 0; i < sorted.length; i += 1) {
      pushLL([sorted[i].lat, sorted[i].lon]);
      if (i + 1 < sorted.length) {
        const a = sorted[i].tst, b = sorted[i + 1].tst;
        if (b - a >= GAP_FILL_MIN_S) {
          routeStops
            .filter(s => s.tst > a && s.tst < b)
            .forEach(s => pushLL(s.ll));
        }
      }
    }
    routeStops.filter(s => s.tst > lastTst).forEach(s => pushLL(s.ll));

    const gpsRouteLayer = L.layerGroup([
      L.polyline(latlngs, { color: '#fff', weight: 5, opacity: 0.6 }),
      L.polyline(latlngs, { color: '#002868', weight: 3, opacity: 0.9 }),
    ]);
    window.__gpsRouteLayer = gpsRouteLayer;
    layerControl.addOverlay(gpsRouteLayer, 'GPS track');
    if (straightRouteLayer && map.hasLayer(straightRouteLayer)) {
      map.removeLayer(straightRouteLayer);
    }
    gpsRouteLayer.addTo(map);
    // Total polyline length in miles → trip header summary chip. Stays
    // hidden when no GPS layer renders. Recomputed every time the
    // polyline is rebuilt (the chip just gets the latest value).
    computeAndShowGpsMiles(latlngs);

    // Current-location marker: when *now* sits inside the trip window, drop
    // a pulsing green dot at the most recent in-window ping so anyone
    // following the trip can see where the travelers currently are. The
    // window comes from `computeTripWindow` above and respects manual
    // HOME_START_TIME / HOME_END_TIME overrides, auto-detected home
    // boundaries, and date-fallback bounds — so the marker won't appear
    // before the trip's departure time on day 1 or after its arrival time
    // on the last day. `sorted` is ascending by tst; the last entry is the
    // latest reading. The lead-out boundary-pad ping (tst > upperCut) only
    // exists for trips already past `upperCut`, which would fail the
    // `nowInWindow` check below, so for active trips the last entry is
    // always a true in-trip ping.
    const nowTst = Date.now() / 1000;
    const nowInWindow = TRIP_START && TRIP_END && sorted.length &&
      (lowerCut == null || nowTst >= lowerCut) &&
      (upperCut == null || nowTst <= upperCut);
    if (nowInWindow) {
      const latest = sorted[sorted.length - 1];
      const dt = new Date(latest.tst * 1000);
      const fmtOpts = {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
      };
      if (latest.tz) fmtOpts.timeZone = latest.tz;
      const local = dt.toLocaleString(undefined, fmtOpts);
      // Tooltip's "X ago" hint so a stale ping (poor coverage, phone off)
      // doesn't masquerade as a fresh fix without context.
      const ageMin = Math.max(0, (Date.now() / 1000 - latest.tst) / 60);
      const ageLabel = ageMin < 60
        ? `${Math.round(ageMin)} min ago`
        : ageMin < 60 * 24
          ? `${Math.round(ageMin / 60)} hr ago`
          : `${Math.round(ageMin / 60 / 24)} d ago`;
      // Drop the pulse animation when the traveler is parked at one of the
      // trip's campgrounds / campsites. The pulse reads as "live and moving";
      // a still dot reads as "here for now". Vicinity uses each stay's
      // resolved lat/lng — which is the `campsite_location` override when
      // set, else the campground's listed coords — within 300 m (roughly a
      // typical campground footprint, big enough to cover entrance-to-actual-
      // site offsets, small enough that driving past doesn't trigger it).
      const AT_CAMPSITE_RADIUS_M = 300;
      let nearestStay = null;
      let nearestMeters = Infinity;
      mapped.forEach(s => {
        const d = distMeters([latest.lat, latest.lon], [s.lat, s.lng]);
        if (d <= AT_CAMPSITE_RADIUS_M && d < nearestMeters) {
          nearestStay = s;
          nearestMeters = d;
        }
      });
      const atCampsite = !!nearestStay;
      const markerHtml = atCampsite
        ? '<div class="current-location-marker"><div class="dot"></div></div>'
        : '<div class="current-location-marker">' +
          '<div class="pulse"></div><div class="dot"></div></div>';
      const icon = L.divIcon({
        className: '',
        html: markerHtml,
        iconSize: [18, 18],
        iconAnchor: [9, 9],
      });
      // zIndexOffset 950 sits above stays (800) and events (700) so the
      // pulse is never hidden behind a same-coords stay marker, while
      // staying below the home (1000) anchor.
      const m = L.marker([latest.lat, latest.lon], { icon, zIndexOffset: 950 });
      const title = atCampsite && nearestStay.place
        ? `At ${escapeHtml(nearestStay.place)}`
        : 'Current location';
      m.bindTooltip(
        `<strong>${title}</strong><br>${local}<br><em>${ageLabel}</em>`,
        { direction: 'top', offset: [0, -8] }
      );
      m.addTo(map);
      window.__currentLocationMarker = m;

      // Keep the dot fresh while the viewer sits on this page: every
      // POLL_MS, refetch the GPS track and re-render via the existing
      // refetchAndRenderTrack path (which tears down and rebuilds the
      // polyline, per-point markers, and this current-location marker
      // together, so they all stay in sync with the latest payload).
      //
      // One-shot scheduler (guarded by the global handle) so subsequent
      // re-renders triggered by the poll itself can't pile up additional
      // timers. The interval persists until page unload; if the trip ends
      // mid-session the next render will simply not draw a marker, and
      // the poll keeps no-op'ing — minor wasted load on an edge case.
      //
      // Polling pauses (skip the fetch but keep the timer) when:
      //  - tab is backgrounded (no point spending the round trip),
      //  - admin is in selection mode (a refresh would clear it),
      //  - a selection drag is in flight,
      //  - the add/edit modal is open (don't pull the rug under the form).
      if (!window.__currentLocationPollHandle) {
        const POLL_MS = 2 * 60 * 1000;
        window.__currentLocationPollHandle = setInterval(() => {
          if (document.visibilityState !== 'visible') return;
          if (window.__selectionModeActive) return;
          if (window.__selectionDragInProgress) return;
          const modal = document.getElementById('add-modal');
          if (modal && modal.classList.contains('visible')) return;
          refetchAndRenderTrack();
        }, POLL_MS);
      }
    }

    // Per-point click targets: small circles at each GPS ping that pop up
    // coords + local time when clicked. Hidden when zoomed out so they
    // don't crowd the map; auto-revealed at GPS_POINT_MIN_ZOOM and
    // re-hidden when the user zooms back out. Tied to the GPS-track layer
    // in the layer control so toggling the track also toggles the points.
    // When the admin "Select pings" toggle is on, the points are forced
    // visible at any zoom and click toggles selection (see
    // togglePingSelection / createFromSelection below).
    const GPS_POINT_MIN_ZOOM = 14;
    const gpsPointLayer = L.layerGroup();
    const gpsPointMarkers = [];
    sorted.forEach((p, i) => {
      const m = L.circleMarker([p.lat, p.lon], { ...DEFAULT_PING_STYLE });
      m.__ping = p;
      m.__pingIdx = i;
      m.__selected = false;
      const dt = new Date(p.tst * 1000);
      const fmtOpts = {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        timeZoneName: 'short',
      };
      if (p.tz) fmtOpts.timeZone = p.tz;
      const local = dt.toLocaleString(undefined, fmtOpts);
      const coords = `${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`;
      m.bindPopup(
        `<div style="font-size:.85rem;line-height:1.4">` +
        `<div><strong>${local}</strong></div>` +
        `<div style="font-family:monospace">${coords}</div>` +
        `</div>`);
      // Intercept clicks before Leaflet opens the popup when we're in
      // selection mode. The popup-open event itself isn't suppressible
      // cleanly from a popup binding, so we close it after-the-fact.
      m.on('click', () => {
        // A drag-move that just ended fires a click on the dragged marker
        // — swallow it so we don't deselect the ping the user just moved.
        if (window.__selectionDragJustEnded) return;
        if (window.__selectionModeActive) {
          togglePingSelection(i);
          m.closePopup();
        }
      });
      gpsPointLayer.addLayer(m);
      gpsPointMarkers.push(m);
    });
    window.__gpsPings = sorted;
    window.__gpsPointMarkers = gpsPointMarkers;
    window.__gpsPointLayer = gpsPointLayer;

    function syncGpsPoints() {
      const trackVisible = map.hasLayer(gpsRouteLayer);
      const wantVisible = window.__selectionModeActive ||
        (trackVisible && map.getZoom() >= GPS_POINT_MIN_ZOOM);
      if (wantVisible && !map.hasLayer(gpsPointLayer)) gpsPointLayer.addTo(map);
      if (!wantVisible && map.hasLayer(gpsPointLayer)) map.removeLayer(gpsPointLayer);
    }
    window.__syncGpsPoints = syncGpsPoints;
    map.on('zoomend', syncGpsPoints);
    map.on('overlayadd overlayremove', syncGpsPoints);
    syncGpsPoints();
    // Pings are loaded — enable the admin "Select pings" toggle.
    const selToggle = document.getElementById('selection-mode-toggle');
    const selLabel = document.getElementById('selection-mode-label');
    if (selToggle) selToggle.disabled = false;
    if (selLabel) {
      selLabel.classList.remove('disabled');
      selLabel.title = 'Click GPS points to toggle individually, or click-and-drag on the map to lasso every ping inside a circle. Drag a selected ping to move the whole selection to a new location, or use "Center selected" to collapse them onto their centroid.';
    }
    // Wire the click-and-drag "lasso circle" handlers to this map. Both
    // helpers are internally idempotent (`__selectionLassoReady` /
    // `__selectionDragReady` guards), so re-render calls are no-ops after
    // the first.
    _initSelectionLasso(map);
    _initSelectionDrag(map);
    // If selection mode was on when this re-render started (only possible on
    // the very first load — `refetchAndRenderTrack` clears it before
    // refetching), sync the JS-side state so the toolbar/layer/dragging
    // match the checkbox.
    if (selToggle && selToggle.checked) toggleSelectionMode(selToggle);
  }
  // Expose so post-mutation refetch (window.__refetchAndRenderTrack, defined
  // outside the IIFE) can drive a re-render.
  window.__renderGpsTrack = renderGpsTrack;

  // Reuse the early-kicked-off promise from <head> so the network round
  // trip happens in parallel with HTML parsing instead of waiting until
  // this script block runs (after photo <img> tags have queued).
  (window.__trackPromise || fetch(`/api/trips/${TRIP_ID}/track${IS_ADMIN ? '?admin=1' : ''}`, { credentials: 'same-origin' })
    .then(r => r.ok ? r.json() : { __error: { status: r.status, statusText: r.statusText } }))
    .then(renderGpsTrack)
    .catch(err => {
      trackLog('GPS track render threw an error — using straight track', err);
    });

  // Event markers (gold stars, gray diamonds for waypoints, red houses for family visits)
  function eventDateLabel(evt) {
    let s = evt.date;
    if (evt.time) s += ' ' + evt.time + (evt.end_time ? '\u2013' + evt.end_time : '');
    return s;
  }

  // Group family-visit events by location so a shared marker can list them all
  const familyVisitGroups = new Map();
  mappedEvents.forEach(evt => {
    if (!evt.family_visit) return;
    const key = evt.lat + ',' + evt.lng;
    if (!familyVisitGroups.has(key)) familyVisitGroups.set(key, []);
    familyVisitGroups.get(key).push(evt);
  });

  mappedEvents.forEach(evt => {
    if (evt.family_visit) return;
    const ll = [evt.lat, evt.lng];
    bounds.push(ll);

    const isWaypoint = !!evt.waypoint;
    const color = isWaypoint ? '#aaa' : '#c9a84c';
    const size = isWaypoint ? 18 : 24;
    const fontSize = isWaypoint ? 10 : 13;
    // Auto-detected (still-unvetted) items get an amber ring + a
    // double box-shadow halo instead of the default white border, so
    // admins can spot them on the map at a glance — matches the
    // dashed-amber treatment on the timeline card. Non-admins can't
    // act on the flag, so we render them like any other event.
    const needsVetting = IS_ADMIN && !!evt.needs_vetting;
    const borderCss = needsVetting
      ? 'border:2px dashed #e0a020;box-shadow:0 0 0 2px #fff,0 1px 4px rgba(0,0,0,.4);'
      : 'border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);';
    const evtIcon = L.divIcon({
      className: '',
      html: `<div style="
        width:${size}px;height:${size}px;border-radius:50%;
        background:${color};
        display:flex;align-items:center;justify-content:center;
        ${borderCss}box-sizing:border-box;
        color:#fff;font-size:${fontSize}px;line-height:1;
      ">${isWaypoint ? '<span style="display:block;transform:translateY(-1.5px);">&#9670;</span>' : '&#9733;'}</div>`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    });
    const zOffset = isWaypoint ? 100 : 700;
    const labelPrefix = isWaypoint ? '&#9670; ' : '&#9733; ';

    const evtMarker = L.marker(ll, { icon: evtIcon, zIndexOffset: zOffset })
      .addTo(map)
      .on('click', () => scrollToCard('event-' + evt.idx));
    cardTargets['event-' + evt.idx] = ll;
    cardMarkers['event-' + evt.idx] = evtMarker;
  });

  familyVisitGroups.forEach(group => {
    const ll = [group[0].lat, group[0].lng];
    bounds.push(ll);

    const famIcon = L.divIcon({
      className: '',
      html: `<div style="
        width:24px;height:24px;border-radius:50%;
        background:#bf0a30;
        display:flex;align-items:center;justify-content:center;
        border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
      "><svg width="14" height="14" viewBox="0 0 20 20" fill="#fff"><path d="M10 2 L2 9 L5 9 L5 17 L9 17 L9 12 L11 12 L11 17 L15 17 L15 9 L18 9 Z"/></svg></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    const sorted = [...group].sort((a, b) =>
      (a.date + ' ' + (a.time || '')).localeCompare(b.date + ' ' + (b.time || ''))
    );
    // Click scrolls to the first visit's card; every family-visit event now
    // has a card (bare or with-photos), so the lookup is effectively always
    // the earliest visit in the group.
    const scrollTarget = sorted.find(e => document.getElementById('event-' + e.idx));
    const famMarker = L.marker(ll, { icon: famIcon, zIndexOffset: 850 })
      .addTo(map)
      .on('click', () => { if (scrollTarget) scrollToCard('event-' + scrollTarget.idx); });
    group.forEach(evt => {
      cardTargets['event-' + evt.idx] = ll;
      cardMarkers['event-' + evt.idx] = famMarker;
    });
  });

  // Family location markers — only show if a stay or event is nearby
  const FAMILY = FAMILY_LOCATIONS;
  const tripPoints = [...mapped.map(s => [s.lat, s.lng]), ...mappedEvents.map(e => [e.lat, e.lng])];

  function haversineKm(lat1, lng1, lat2, lng2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) * Math.sin(dLng/2)**2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  const NEARBY_KM = 80;
  const visitedFamilyLabels = new Set(events.filter(e => e.family_visit).map(e => e.family_visit));
  FAMILY.forEach(fam => {
    if (visitedFamilyLabels.has(fam.label)) return;
    const nearby = tripPoints.some(p => haversineKm(p[0], p[1], fam.lat, fam.lng) <= NEARBY_KM);
    if (!nearby) return;

    const ll = [fam.lat, fam.lng];
    const famIcon = L.divIcon({
      className: '',
      html: `<div style="
        width:24px;height:24px;border-radius:50%;
        background:#bf0a30;
        display:flex;align-items:center;justify-content:center;
        border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
      "><svg width="14" height="14" viewBox="0 0 20 20" fill="#fff"><path d="M10 2 L2 9 L5 9 L5 17 L9 17 L9 12 L11 12 L11 17 L15 17 L15 9 L18 9 Z"/></svg></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    L.marker(ll, { icon: famIcon, zIndexOffset: 900 }).addTo(map);
  });

  // Use the saved view (center + zoom from the previous unload) when present
  // so reloads after suppress/relocate/etc. keep the user where they were.
  // First-time visits and other trips get the trip-bounds auto-fit.
  const _saved = _loadMapView();
  if (_saved) {
    map.setView([_saved.lat, _saved.lng], _saved.zoom);
  } else {
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
  }
})();


