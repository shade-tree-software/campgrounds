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

// Below this width the two-column grid collapses and the map sits stacked
// above the cards (see the .content.two-col media query). That stacking is
// what makes map↔card focus-following jarring: the scroll yanks the page out
// from under the map you just tapped, and a card tap pans a map that's
// scrolled off-screen. On these viewports the map answers in place with a
// popup instead (see `openMarkerPopup`), and card clicks don't move it.
// Checked per interaction, not once at load, so a rotation takes effect
// immediately.
function isSingleColumnLayout() {
  return window.matchMedia('(max-width: 900px)').matches;
}

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
// Skipped on the stacked single-column layout, where the map is off-screen
// while you're reading cards — moving it there is invisible work that only
// shows up later as a mysteriously re-zoomed map.
document.querySelectorAll('.stay-card, .event-card').forEach(card => {
  card.addEventListener('click', (e) => {
    if (isSingleColumnLayout()) return;
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
  // Desktop-only chip: the phone's condensed line drops GPS miles along with
  // the other statistical counts (see the .meta-mobile comment in the template).
  const el = document.getElementById('trip-gps-miles');
  if (!el) return;
  if (!latlngs || latlngs.length < 2) {
    el.style.display = 'none';
    return;
  }
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
  const shown = miles >= 100 ? Math.round(miles) : miles.toFixed(1);
  el.querySelector('span').textContent = shown;
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

  // Wheel zoom stays ON (Leaflet's default): the map is its own half of the
  // page, so the cursor's position already says whether you meant to zoom the
  // map or scroll the timeline.
  //
  // One-finger DRAGGING is off on touch-primary devices only, where the map is
  // a band across the top and a swipe up must scroll the page rather than pan
  // it. Two-finger pan/pinch still works: Leaflet's touchZoom handler moves the
  // center by the pinch midpoint, so it pans as well as zooms. Disabling
  // dragging also drops Leaflet's `leaflet-touch-drag` class, which restores
  // `touch-action: pan-x pan-y` on the container — that's what lets the browser
  // scroll the page normally. No on-screen hint: pinch-to-move is the universal
  // phone gesture, and the corner it would occupy is already taken by the
  // legend, scale bar and attribution (AWH 2026-07-26).
  //
  // `pointer: coarse` (not L.Browser.touch) so a touchscreen LAPTOP, where the
  // real pointer is a mouse, keeps ordinary click-drag panning — L.Browser.touch
  // is true for anything that merely supports touch events.
  const touchPrimary = window.matchMedia('(pointer: coarse)').matches;
  // zoomControl: false app-wide — wheel/pinch/double-click/keyboard all zoom.
  const map = L.map('trip-map', { dragging: !touchPrimary, zoomControl: false });
  // Published so anything that temporarily suppresses dragging (the admin
  // select-pings lasso) restores it to this page's baseline rather than
  // unconditionally enabling it — which on a phone would reinstate the
  // one-finger pan that swallows the timeline scroll.
  window.__tripMapDragDefault = !touchPrimary;
  window.tripMap = map;
  if (window.addMilesScaleBar) map.whenReady(() => window.addMilesScaleBar(map));  // miles scale bar, bottom-right above attribution
  // Dedicated SVG pane for the suppressed/relocated ghost layers so they
  // render above every regular marker (markerPane is zIndex 600; this sits
  // above home/family/stay/event icons so admins can always click through to
  // unsuppress/unrelocate even when an override sits at the same coords as a
  // stay or family location).
  map.createPane('overrides').style.zIndex = 700;
  const streets = window.ekkoStreetLayer().addTo(map);
  const satellite = window.ekkoSatelliteLayer();
  const baseLayers = { 'Map': streets, 'Satellite': satellite };
  // Offered but OFF by default, unlike the two overview maps: one trip is
  // usually framed tight enough that you already know where you are, and the
  // lazy fetch means an unshown layer costs this page nothing.
  const overlayLayers = { '🗺️ State lines': window.ekkoBordersLayer() };
  const layerControl = L.control.layers(baseLayers, overlayLayers).addTo(map);

  const HOME = HOME_COORDS;
  const bounds = [HOME];

  // Marker palette, named once. The legend below draws from the same
  // constants as the markers themselves — when they were separate literals the
  // legend immediately drifted (it showed waypoints in the event's gold).
  const STAY_COLOR = '#002868';
  const EVENT_COLOR = '#c9a84c';
  const WAYPOINT_COLOR = '#aaa';
  const HOME_COLOR = '#bf0a30';
  // The white house glyph inside the home/family markers, shared so the legend
  // shows the same icon rather than an approximation of it.
  const HOUSE_SVG = '<svg width="14" height="14" viewBox="0 0 20 20" fill="#fff">'
    + '<path d="M10 2 L2 9 L5 9 L5 17 L9 17 L9 12 L11 12 L11 17 L15 17 L15 9 L18 9 Z"/></svg>';
  // The waypoint diamond, drawn rather than typed. It was the &#9670; text
  // glyph, whose ink sits high in its line box by an amount that depends on
  // whichever font the stack resolves to — so the flex centering centred the
  // line box while the diamond itself rode high, and the fixed translateY
  // nudge that compensated only ever matched one font. An SVG path is centred
  // by construction on every device (same reason the house is one).
  const DIAMOND_SVG = '<svg width="8" height="8" viewBox="0 0 20 20" fill="#fff">'
    + '<path d="M10 1 L19 10 L10 19 L1 10 Z"/></svg>';
  // The event star, drawn for the same reason as the diamond above.
  // Five-pointed, outer radius 9 and inner 3.44 (the classic ~0.382 ratio),
  // struck about the viewBox centre: a pentagram has 5-fold symmetry, so its
  // area centroid IS that centre — which is why centring the circumcircle in
  // the badge is the optically balanced choice and needs no fudge factor.
  // Sized to match the house in the same 24px badge.
  const STAR_SVG = '<svg width="14" height="14" viewBox="0 0 20 20" fill="#fff">'
    + '<path d="M10 1 L12.02 7.22 L18.56 7.22 L13.27 11.06 L15.29 17.28'
    + ' L10 13.44 L4.71 17.28 L6.73 11.06 L1.44 7.22 L7.98 7.22 Z"/></svg>';

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
      background:${HOME_COLOR};
      display:flex;align-items:center;justify-content:center;
      border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
    ">${HOUSE_SVG}</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
  // On the two-column layout markers carry no popups (a click scrolls to the
  // matching card), which left four different symbols on the map with nothing
  // naming any of them. A hover tooltip is the cheapest fix that doesn't touch
  // the click behavior.
  const TOOLTIP_OPTS = { direction: 'top', offset: [0, -14], opacity: 0.95 };
  function label(marker, text) {
    if (text) marker.bindTooltip(String(text), TOOLTIP_OPTS);
    return marker;
  }

  // ── Marker clicks ────────────────────────────────────────────────────────
  // Two-column: scroll the cards column to the matching card (the map stays
  // put beside it). Single-column: open a popup describing the stop, the way
  // the trips map does — the map is what's on screen, so it answers in place.
  // maxHeight because the stacked map is only ~380px tall (less in phone
  // landscape) — a family location with a long visit list would otherwise
  // make a popup taller than the map it's anchored in.
  const POPUP_OPTS = { maxWidth: 420, maxHeight: 240, autoPanPadding: L.point(20, 20) };

  // Deliberately a standalone popup rather than bindPopup: binding installs
  // its own click handler, which would pop the popup on the two-column layout
  // too, where a click means "scroll to the card".
  function openMarkerPopup(marker, html) {
    if (!html) return;
    // Touch fires the tooltip on this same click (Leaflet binds tooltips to
    // click on touch devices), and it would sit stacked over the popup.
    marker.closeTooltip();
    L.popup(POPUP_OPTS).setLatLng(marker.getLatLng()).setContent(html).openOn(map);
  }

  // `html` is a string built at marker-creation time; `cardId` may be null for
  // markers with no card (proximity family houses).
  //
  // `opts.alwaysPopup` overrides the layout rule for a marker that stands for
  // MORE THAN ONE timeline entry (the same campground stayed at twice, a family
  // location visited several times). There the two-column "scroll to the card"
  // shortcut has no right answer — it silently picked one occurrence and left
  // the others unreachable from the map — so the popup opens on every layout
  // and its rows are the picker.
  function onMarkerClick(marker, html, cardId, opts) {
    const alwaysPopup = !!(opts && opts.alwaysPopup);
    marker.on('click', () => {
      if (alwaysPopup || isSingleColumnLayout()) openMarkerPopup(marker, html);
      else if (cardId) scrollToCard(cardId);
    });
    return marker;
  }

  // Popup "View details" links scroll to the card — the one map→card jump
  // that's fine on mobile, because the reader asked for it. Wired on open
  // rather than inline so the popup HTML stays free of event attributes.
  map.on('popupopen', (e) => {
    const node = e.popup.getElement();
    if (!node) return;
    node.querySelectorAll('a[data-card]').forEach(a => {
      a.addEventListener('click', (ev) => {
        ev.preventDefault();
        map.closePopup();
        scrollToCard(a.dataset.card);
      });
    });
  });

  function fmtDate(iso, opts) {
    if (!iso) return '';
    const d = new Date(iso + 'T00:00:00');
    if (isNaN(d.getTime())) return iso;
    return d.toLocaleDateString('en-US',
      opts || { month: 'short', day: 'numeric', year: 'numeric' });
  }

  // "Jun 5 – Jun 7, 2026" — the year is carried by the right-hand date alone
  // when both ends share it.
  function stayDateRange(stay) {
    if (!stay.start) return '';
    if (!stay.end || stay.end === stay.start) return fmtDate(stay.start);
    const sameYear = stay.start.slice(0, 4) === stay.end.slice(0, 4);
    const left = fmtDate(stay.start, sameYear ? { month: 'short', day: 'numeric' } : null);
    return left + ' – ' + fmtDate(stay.end);
  }

  // Empty string when the card didn't render (e.g. a family visit whose card
  // is filtered out) — a link to nothing is worse than no link.
  function cardLink(cardId, text) {
    if (!cardId || !document.getElementById(cardId)) return '';
    return '<div style="margin-top:6px;font-size:12px;">'
      + `<a href="#" data-card="${cardId}" style="color:#002868;">`
      + `${text || 'View details'} ›</a></div>`;
  }

  function nightsLabel(stay) {
    const nights = Number(stay.nights) || 0;
    return nights ? `${nights} night${nights !== 1 ? 's' : ''}` : '';
  }

  function stayPopupHtml(stay, num) {
    let h = `<strong>${num}. ${escapeHtml(stay.place || 'Campspot')}</strong>`;
    const where = [stay.locale, stay.state].filter(Boolean).join(', ');
    if (where) h += `<br>${escapeHtml(where)}`;
    const when = [stayDateRange(stay), nightsLabel(stay)].filter(Boolean).join(' · ');
    if (when) h += `<br>${when}`;
    // site_label is the server's display form ("Site 67"), blank for the
    // legacy stays that stashed coordinates in `site`.
    if (stay.site_label) h += `<br>${escapeHtml(stay.site_label)}`;
    return h + cardLink('stay-' + stay.idx);
  }

  // Zone label for a time, on trips that span more than one zone. MULTI_TZ and
  // the per-event `tz_abbr` both come from the server (see `_make_trip`), so
  // the map can't disagree with the timeline cards about when to show one.
  function tzSuffix(evt) {
    return (MULTI_TZ && evt.tz_abbr) ? ' ' + evt.tz_abbr : '';
  }

  // Chronological comparator for two events. `time_rank` is the server's
  // minutes-from-UTC-midnight rank, which is what makes a westward zone
  // crossing sort correctly — comparing "HH:MM" strings puts a stop that
  // happened 44 minutes LATER first, because the clock went back an hour in
  // between (trip 95, 2026-08-23). Falls back to the wall clock for an event
  // with no rank, which is also exactly what the rank degrades to when a trip
  // carries no zones at all.
  function byEventTime(a, b) {
    if (a.time_rank != null && b.time_rank != null) return a.time_rank - b.time_rank;
    return (a.time || '12:00').localeCompare(b.time || '12:00');
  }

  function eventWhen(evt) {
    let s = fmtDate(evt.date);
    if (evt.time) {
      s += (s ? ' · ' : '') + evt.time + (evt.end_time ? '–' + evt.end_time : '') + tzSuffix(evt);
    }
    return s;
  }

  function eventPopupHtml(evt) {
    const fallback = evt.waypoint ? 'Stop' : 'Event';   // "waypoint" is internal vocabulary
    let h = `<strong>${escapeHtml(evt.name || fallback)}</strong>`;
    const when = eventWhen(evt);
    if (when) h += `<br>${when}`;
    const where = [evt.locale, evt.state].filter(Boolean).join(', ');
    if (where) h += `<br>${escapeHtml(where)}`;
    // A long description would push the popup past the 60vh cap and turn it
    // into a scroller; the card is one tap away for the rest.
    const desc = (evt.description || '').trim();
    if (desc) {
      const short = desc.length > 160 ? desc.slice(0, 160).trimEnd() + '…' : desc;
      h += `<div style="margin-top:4px;">${escapeHtml(short)}</div>`;
    }
    return h + cardLink('event-' + evt.idx);
  }

  // One marker stands for several timeline entries at the same spot — every
  // visit to a family location, or every separate stay at one campground. The
  // popup lists them the way the trips map lists trips (one line each, linking
  // to its own card) so the reader picks which occurrence to jump to.
  // A row whose card didn't render degrades to plain text: a link to nothing is
  // worse than no link.
  function occurrenceListHtml(title, rows) {
    let h = `<strong>${escapeHtml(title)}</strong>`;
    h += '<div style="margin-top:4px;font-size:12px;">';
    rows.forEach(({ cardId, text }) => {
      h += (cardId && document.getElementById(cardId))
        ? `<a href="#" data-card="${cardId}" style="display:block;color:#002868;">`
          + `${escapeHtml(text)} ›</a>`
        : `<div>${escapeHtml(text)}</div>`;
    });
    return h + '</div>';
  }

  function familyPopupHtml(sorted) {
    const title = sorted[0].family_visit || sorted[0].name || 'Family visit';
    // The event name is appended only when it tells the rows apart. Visits to
    // one family location are usually all named the same thing ("Papa and
    // Bonnie's House" nine times), and repeating it on every row buries the
    // date+time that's actually doing the distinguishing.
    const extras = new Set(sorted.map(evt => (evt.name && evt.name !== title ? evt.name : '')));
    const showExtra = extras.size > 1;
    return occurrenceListHtml(title, sorted.map(evt => ({
      cardId: 'event-' + evt.idx,
      text: (eventWhen(evt) || 'Visit')
        + (showExtra && evt.name && evt.name !== title ? ' — ' + evt.name : ''),
    })));
  }

  // The rows lead with the campspot's number so they match both the numbered map
  // badge and the circle on the card each one scrolls to. Every occurrence is the
  // same campground (that's the grouping key), so the first one's name titles it.
  // The campsite is on each row because the commonest reason one campground has
  // several records in a trip is that the site changed mid-stay — dates alone
  // leave the reader guessing which row is which.
  function stayGroupPopupHtml(group) {
    const title = group[0].stay.place || 'Campspot';
    return occurrenceListHtml(title, group.map(({ stay, num }) => ({
      cardId: 'stay-' + stay.idx,
      text: `${num}. ` + ([stayDateRange(stay), nightsLabel(stay), stay.site_label]
        .filter(Boolean).join(' · ') || 'Campspot'),
    })));
  }

  const homeMarker = label(L.marker(HOME, { icon: homeIcon, zIndexOffset: 1000 })
    .addTo(map), 'Home');
  onMarkerClick(homeMarker, '<strong>Home</strong>', 'home-card-start');
  cardMarkers['home-card-start'] = homeMarker;
  cardMarkers['home-card-end'] = homeMarker;

  // A trip can stay at the same campground on separate legs — trip 60 does it
  // three times, trips 16 and 17 twice — and every one of those repeats sits
  // within 50 m of its twin (0 m unless a per-stay `campsite_location` nudges
  // it), which is sub-pixel at the zoom a whole trip fits in. Stacked like
  // that, only the last marker drawn was really clickable, so the earlier
  // occurrences couldn't be reached from the map at all and the click scrolled
  // to whichever stay happened to be on top.
  //
  // Fix: every marker of a repeated campspot opens a popup listing ALL of its
  // occurrences (see onMarkerClick's alwaysPopup), so whichever pin of the
  // stack the click lands on, the reader gets the full list and picks. The
  // markers themselves are left alone — merging them would move a pin off its
  // own campsite and cost the per-stay badge number.
  //
  // Keyed on campground identity, not on the coordinate: those `campsite_location`
  // offsets give two stays at one campground different coordinates while leaving
  // them visually a single marker.
  // Also how the family-house markers below find the stays parked in their
  // driveway, so the two can't disagree about what counts as the same place.
  function campgroundStayKey(id) { return 'cg:' + id; }

  function stayGroupKey(stay) {
    if (stay.campground_id !== null && stay.campground_id !== undefined) {
      return campgroundStayKey(stay.campground_id);
    }
    // Free-text stays (hotels, Airbnbs) have no id, so name + coordinate is the
    // only identity available. Same name at a different coordinate is a
    // different place and stays ungrouped.
    const name = (stay.custom_place || stay.place || '').trim().toLowerCase();
    return `place:${name}@${stay.lat},${stay.lng}`;
  }

  const stayOccurrences = new Map();
  mapped.forEach((stay, i) => {
    const key = stayGroupKey(stay);
    if (!stayOccurrences.has(key)) stayOccurrences.set(key, []);
    // `num` is the marker badge / card circle number — the stay's own position
    // in the trip, carried along so a grouped popup can name each occurrence.
    stayOccurrences.get(key).push({ stay, num: i + 1 });
  });

  // Give a marker the click behavior of a set of campspot occurrences: one stay
  // behaves like that stay's own pin (two-column scrolls to its card, stacked
  // pops up its details), several always open the occurrence list. Used by the
  // campspot markers and by the family house marker standing over the driveway
  // those stays are parked in. `emptyHtml` covers a marker with no stays at all.
  function wireStayGroupClick(marker, group, emptyHtml) {
    if (!group.length) return onMarkerClick(marker, emptyHtml, null);
    const multi = group.length > 1;
    const { stay, num } = group[0];
    return onMarkerClick(marker,
      multi ? stayGroupPopupHtml(group) : stayPopupHtml(stay, num),
      multi ? null : 'stay-' + stay.idx,
      { alwaysPopup: multi });
  }

  mapped.forEach((stay, i) => {
    const ll = [stay.lat, stay.lng];
    bounds.push(ll);

    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:24px;height:24px;border-radius:50%;
        background:${STAY_COLOR};color:#fff;
        display:flex;align-items:center;justify-content:center;
        font-size:12px;font-weight:700;
        border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
      ">${i + 1}</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    const group = stayOccurrences.get(stayGroupKey(stay)) || [{ stay, num: i + 1 }];
    const stayMarker = label(L.marker(ll, { icon, zIndexOffset: 800 }).addTo(map),
      `${i + 1}. ${stay.place || 'Campspot'}`
      + (group.length > 1 ? ` · ${group.length} stays here` : ''));
    wireStayGroupClick(stayMarker, group);
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
  // The UTC offsets of those same two lookups. A day boundary is read in the
  // zone of the place you were, so "the night of the 26th" ends when the
  // travelers' own midnight arrives, not the reader's. Falls back to home's
  // offset, which is what HOME itself uses.
  function morningOffset(dateStr) {
    for (const s of mapped) {
      if (s.start < dateStr && dateStr <= s.end) {
        return s.tz_offset_min != null ? s.tz_offset_min : HOME_TZ_OFFSET_MIN;
      }
    }
    return HOME_TZ_OFFSET_MIN;
  }
  function eveningOffset(dateStr) {
    for (const s of mapped) {
      if (s.start <= dateStr && dateStr < s.end) {
        return s.tz_offset_min != null ? s.tz_offset_min : HOME_TZ_OFFSET_MIN;
      }
    }
    return HOME_TZ_OFFSET_MIN;
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
      .sort(byEventTime);

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
  // Epoch seconds for a stored date + wall clock. `offsetMin` is the minutes
  // to ADD to that wall clock to reach UTC; pass it whenever the zone the time
  // was written in is known, and the answer is the true instant regardless of
  // where the page is being read. Without it we fall back to the BROWSER's
  // zone, which is what this always did.
  //
  // That fallback is why trip 95 drew a 9.3 km spike out to Roaring Fork and
  // back in the middle of the night: read from Eastern, a 09:11 Mountain
  // waypoint stamped as 07:11 Mountain, landing it inside the PREVIOUS
  // night's gap, where the gap-filler dutifully routed the line through it.
  // Anchors must therefore always pass an offset when one is available —
  // these timestamps decide which gap an anchor falls in, so being two hours
  // out doesn't nudge the line, it teleports the anchor.
  function localEpoch(dateStr, timeStr, offsetMin) {
    if (!dateStr || !timeStr) return null;
    const [y, m, d] = dateStr.split('-').map(Number);
    const [hh, mm] = timeStr.split(':').map(Number);
    if ([y, m, d, hh, mm].some(isNaN)) return null;
    if (offsetMin != null) {
      return Date.UTC(y, m - 1, d, hh, mm, 0) / 1000 + offsetMin * 60;
    }
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
      if (HOME_START_TIME) lowerCut = localEpoch(TRIP_START, HOME_START_TIME, HOME_TZ_OFFSET_MIN);
      else if (autoHomeStartTst != null) lowerCut = autoHomeStartTst;
      else lowerCut = localEpoch(TRIP_START, '00:00', HOME_TZ_OFFSET_MIN);
    }
    if (TRIP_END) {
      if (HOME_END_TIME) upperCut = localEpoch(TRIP_END, HOME_END_TIME, HOME_TZ_OFFSET_MIN);
      else if (autoHomeEndTst != null) upperCut = autoHomeEndTst;
      else upperCut = localEpoch(addDaysISO(TRIP_END, 1), '00:00', HOME_TZ_OFFSET_MIN);
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
    // Home times are in the home zone; on a multi-timezone trip say so, or
    // the trip's start and end become the only unlabelled times on the page.
    // The abbreviation is rendered into the span's data attribute server-side
    // (blank on a single-zone trip), so this doesn't re-derive it.
    const tz = span.dataset.tzAbbr ? ` ${span.dataset.tzAbbr}` : '';
    span.textContent = IS_ADMIN ? ` · ${hm}${tz} (auto)` : ` · ${hm}${tz}`;
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
    // overrides.js is admin-only (see the script tags in trip_detail.html), and
    // suppressed/relocated ghost layers are an admin affordance anyway.
    if (IS_ADMIN) _buildSuppressedRelocatedLayers(rawSuppressed, rawRelocated);

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
      pushStop(localEpoch(dateStr, '00:00', morningOffset(dateStr)),
               morningLocation(dateStr));
      mappedEvents
        .filter(e => e.date === dateStr)
        .sort(byEventTime)
        .forEach(evt => pushStop(
          localEpoch(dateStr, evt.time || '12:00', evt.tz_offset_min),
          [evt.lat, evt.lng]));
      pushStop(localEpoch(dateStr, '23:59', eveningOffset(dateStr)),
               eveningLocation(dateStr));
    });

    const latlngs = [];
    function pushLL(pt) {
      const last = latlngs[latlngs.length - 1];
      if (last && pt[0] === last[0] && pt[1] === last[1]) return;
      latlngs.push(pt);
    }
    const firstTst = sorted[0].tst;
    const lastTst = sorted[sorted.length - 1].tst;
    const nowTst = Date.now() / 1000;
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
    // Trailing gap-fill: route through anchors after the last good ping (a
    // phone that stopped logging mid-trip, or the return-home leg of a
    // completed trip). But never draw toward an anchor whose clock time
    // hasn't arrived yet: on the final day of an *in-progress* trip the
    // evening anchor is HOME stamped at 23:59, and the traveler is still en
    // route — projecting a straight line from the current position to HOME
    // is premature. Gating by `nowTst` suppresses that future home/evening
    // anchor while in progress; for a completed trip every anchor is already
    // in the past, so this is a no-op and the arrive-home leg still draws.
    routeStops
      .filter(s => s.tst > lastTst && s.tst <= nowTst)
      .forEach(s => pushLL(s.ll));

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
    // Admins only — and the gate is on BUILDING them, not just showing them.
    // syncGpsPoints() below has always hidden these from regular users, but
    // the markers were still constructed for everyone, so a non-admin paid
    // the full cost of a layer they could never see. On a long trip that's
    // most of the wait before the dashed route flips to the real line: trip
    // 92 has ~14k in-window pings, and the per-ping date formatting alone
    // measured ~1.4s on a desktop (far worse on a phone) on top of 14k
    // circleMarker allocations. Non-admins now skip all of it.
    //
    // Everything downstream reads the globals published below defensively
    // (`window.__gpsPointMarkers || []` throughout overrides.js), and the
    // select/suppress/relocate tooling those feed is admin-gated anyway, so
    // an empty layer + empty array is a complete answer for a regular user.
    //
    // The gate is also on WHEN they're built. At the tracker's
    // current ~3 s sampling a long trip is tens of thousands of pings (trip
    // 95: 45k), and they are invisible until the admin zooms to
    // GPS_POINT_MIN_ZOOM or turns on selection mode — which on most page
    // views never happens. Building them up front therefore charges every
    // admin page load for a layer that usually stays hidden, delaying the
    // moment the dashed route flips to the real line. `syncGpsPoints()`
    // builds them the first time they're actually wanted; after that the
    // array is stable and this is a no-op.
    let gpsPointsBuilt = false;
    function ensureGpsPointMarkers() {
      if (gpsPointsBuilt || !IS_ADMIN) return;
      gpsPointsBuilt = true;
      sorted.forEach((p, i) => {
        const m = L.circleMarker([p.lat, p.lon], { ...DEFAULT_PING_STYLE });
        m.__ping = p;
        m.__pingIdx = i;
        m.__selected = false;
        // Popup content is built on open, not up front. Formatting a date in a
        // named timezone is ~100us a call, which is nothing once and seconds
        // across every ping on a long trip — and the reader opens at most a
        // handful of these.
        m.bindPopup(() => {
          const fmtOpts = {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            timeZoneName: 'short',
          };
          if (p.tz) fmtOpts.timeZone = p.tz;
          const local = new Date(p.tst * 1000).toLocaleString(undefined, fmtOpts);
          const coords = `${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`;
          return `<div style="font-size:.85rem;line-height:1.4">` +
            `<div><strong>${local}</strong></div>` +
            `<div style="font-family:monospace">${coords}</div>` +
            `</div>`;
        });
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
      // The drag binder attaches to whatever markers exist when it runs, and
      // on a normal load that's now — after `_initSelectionDrag` already ran
      // over an empty array. Re-binding here is what keeps drag-to-relocate
      // working on markers built after the fact; `bindMarker` is guarded, so
      // a marker never gets bound twice.
      if (window.__rebindSelectionDrag) window.__rebindSelectionDrag();
    }
    window.__gpsPings = sorted;
    window.__gpsPointMarkers = gpsPointMarkers;
    window.__gpsPointLayer = gpsPointLayer;

    function syncGpsPoints() {
      const trackVisible = map.hasLayer(gpsRouteLayer);
      // Regular users only see the blue track line — the individual per-ping
      // circles are an admin-only affordance (they feed the select/suppress/
      // relocate tooling). For a non-admin the layer above is empty, so this
      // is belt-and-braces; the IS_ADMIN test is what keeps a future caller
      // from revealing an empty layer and reading it as "the pings vanished".
      const wantVisible = window.__selectionModeActive ||
        (IS_ADMIN && trackVisible && map.getZoom() >= GPS_POINT_MIN_ZOOM);
      if (wantVisible) ensureGpsPointMarkers();
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
    if (IS_ADMIN) {
      _initSelectionLasso(map);
      _initSelectionDrag(map);
    }
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
    if (evt.time) s += ' ' + evt.time + (evt.end_time ? '\u2013' + evt.end_time : '') + tzSuffix(evt);
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
    const color = isWaypoint ? WAYPOINT_COLOR : EVENT_COLOR;
    const size = isWaypoint ? 18 : 24;
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
      ">${isWaypoint ? DIAMOND_SVG : STAR_SVG}</div>`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    });
    const zOffset = isWaypoint ? 100 : 700;

    // "Waypoint" is internal vocabulary; family readers get "Stop".
    const evtMarker = label(L.marker(ll, { icon: evtIcon, zIndexOffset: zOffset })
      .addTo(map), evt.name || (isWaypoint ? 'Stop' : 'Event'));
    onMarkerClick(evtMarker, eventPopupHtml(evt), 'event-' + evt.idx);
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
        background:${HOME_COLOR};
        display:flex;align-items:center;justify-content:center;
        border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
      ">${HOUSE_SVG}</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    const sorted = [...group].sort((a, b) =>
      a.date === b.date ? byEventTime(a, b) : a.date.localeCompare(b.date)
    );
    // A single visit keeps the layout rule (two-column: scroll to its card;
    // stacked: popup). Several visits always open the popup so the reader can
    // pick one — scrolling to the earliest, as this used to, made the later
    // visits unreachable from the map. Every family-visit event now has a card
    // (bare or with-photos), so the lookup is effectively always the earliest.
    const multi = sorted.length > 1;
    const scrollTarget = sorted.find(e => document.getElementById('event-' + e.idx));
    const famLabel = sorted[0].family_visit || sorted[0].name || 'Family visit';
    const famMarker = label(L.marker(ll, { icon: famIcon, zIndexOffset: 850 })
      .addTo(map), multi ? `${famLabel} · ${sorted.length} visits` : famLabel);
    onMarkerClick(famMarker, familyPopupHtml(sorted),
      multi || !scrollTarget ? null : 'event-' + scrollTarget.idx,
      { alwaysPopup: multi });
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
        background:${HOME_COLOR};
        display:flex;align-items:center;justify-content:center;
        border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);box-sizing:border-box;
      ">${HOUSE_SVG}</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    // When the trip PARKED IN THIS DRIVEWAY, the house marker answers for those
    // campspots exactly as the driveway marker does. A family entry's stays are
    // pinned to its `driveway_location` so they don't hide under the house icon,
    // which leaves the two ~19–25 m apart (Svendsens 18.8 m, and 24 trips do
    // this) — one place as far as the reader is concerned, yet only one half of
    // it responded to a click. So: one stay → scroll to its card, several → the
    // same occurrence list the driveway marker shows.
    //
    // With no stays there's no card to scroll to — a family home merely NEAR the
    // trip. There the tooltip names it on two-column and the click does nothing;
    // single-column has no hover, so it gets the name as a popup.
    const drivewayStays = stayOccurrences.get(campgroundStayKey(fam.id)) || [];
    const proxMarker = label(
      L.marker(ll, { icon: famIcon, zIndexOffset: 900 }).addTo(map),
      fam.label + (drivewayStays.length > 1 ? ` · ${drivewayStays.length} stays here` : ''));
    wireStayGroupClick(proxMarker, drivewayStays,
      `<strong>${escapeHtml(fam.label || 'Family')}</strong>`);
  });

  // ── Initial view + "Fit trip" ─────────────────────────────────────────────
  // Fit everything, home included. `bounds` opens with HOME, which is also what
  // the route polyline draws (the drive out and back), so the opening view and
  // the route agree: the trip is the whole loop from the driveway, not just the
  // far end of it. This holds at any distance — a Utah trip opens on a
  // continental view with Virginia in frame, deliberately (AWH 2026-07-27).
  //
  // It used to fit the itinerary alone (`bounds.slice(1)`) and fold home back in
  // only when home happened to land near the frame, to avoid exactly that wide
  // view. Don't reinstate that: "sometimes home, depending how far away it is"
  // made the button's result unpredictable, and the zoom-out to see the drive
  // home was the common next action anyway.
  const FIT_PAD = 40;      // per side
  const FIT_MAX_ZOOM = 12;

  function fitTrip() {
    map.fitBounds(bounds, { padding: [FIT_PAD, FIT_PAD], maxZoom: FIT_MAX_ZOOM });
  }

  // Getting back to the whole trip after a card click (which does setView at
  // zoom 14) or a stray zoom previously meant reloading the page.
  const fitControl = L.control({ position: 'topleft' });
  fitControl.onAdd = function() {
    const div = L.DomUtil.create('div', 'leaflet-bar trip-fit-control');
    const a = L.DomUtil.create('a', '', div);
    a.href = '#';
    a.innerHTML = '&#10064;';
    a.title = 'Fit the whole trip';
    a.setAttribute('aria-label', 'Fit the whole trip');
    L.DomEvent.disableClickPropagation(div);
    L.DomEvent.on(a, 'click', (e) => { L.DomEvent.preventDefault(e); fitTrip(); });
    return div;
  };
  fitControl.addTo(map);

  // ── Legend ────────────────────────────────────────────────────────────────
  // Four marker colours with nothing naming them.
  // Each swatch is a plain colour circle, matching the trips-map legend rather
  // than redrawing each marker in miniature. The four marker kinds are already
  // four distinct hues, so colour alone identifies a row — and the glyphs the
  // swatches used to carry (a "1", a star, a diamond, a house) bought nothing
  // for that while forcing per-row size/shape special-casing.
  // Only the kinds actually on this trip's map are listed, so a plain overnight
  // trip doesn't get a legend row for stops it doesn't have.
  const legendRows = [
    [true, STAY_COLOR, 'Campspot', 'Overnight campspot'],
    [mappedEvents.some(e => !e.waypoint && !e.family_visit),
     EVENT_COLOR, 'Event', 'Event or site of interest'],
    [mappedEvents.some(e => e.waypoint),
     WAYPOINT_COLOR, 'Brief stop', 'Brief stop along the way'],
    [true, HOME_COLOR, 'Home &amp; family', 'Home and family'],
  ].filter(r => r[0]);
  if (legendRows.length) {
    const legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function() {
      const div = L.DomUtil.create('div', 'trip-map-legend');
      L.DomEvent.disableClickPropagation(div);
      // Both label lengths ship; .legend-short / .legend-long (base.html) pick
      // one by viewport width.
      div.innerHTML = legendRows.map(([, bg, short, long]) => `
        <div class="tl-row">
          <span class="tl-dot" style="background:${bg};"></span>
          <span><span class="legend-short">${short}</span><span class="legend-long">${long}</span></span>
        </div>`).join('');
      return div;
    };
    legend.addTo(map);
  }

  // Use the saved view (center + zoom from the previous unload) when present
  // so reloads after suppress/relocate/etc. keep the user where they were.
  // First-time visits and other trips get the trip-bounds auto-fit.
  const _saved = _loadMapView();
  if (_saved) {
    map.setView([_saved.lat, _saved.lng], _saved.zoom);
  } else {
    fitTrip();
  }
})();


