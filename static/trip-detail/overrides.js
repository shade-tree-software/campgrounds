// ── GPS-ping selection (admin) ────────────────────────────────────────────
// "Select pings" mode lets admins click GPS points on the trip-detail map to
// pick out a contiguous set, then create an event or waypoint whose location
// is the centroid of the selection and whose start/end times are the oldest
// and newest pings. Name/locale/state are filled by reverse-geocoding the
// centroid via /api/reverse-geocode (Nominatim).
//
// In addition to single-clicking individual ping markers, the user can press
// and drag on the map to draw a circle (mousedown = center, drag = radius)
// and on release every ping inside the circle is added to the selection.
// Multiple circles add cumulatively; clicking an already-selected ping
// deselects just that one; unchecking the toggle clears the whole selection.
const DEFAULT_PING_STYLE = { radius: 5, color: '#002868', weight: 1, fillColor: '#ffffff', fillOpacity: 1 };
const SELECTED_PING_STYLE = { radius: 6, color: '#1b5e20', weight: 2, fillColor: '#66bb6a', fillOpacity: 1 };
const SUPPRESSED_PING_STYLE = { radius: 6, color: '#444', weight: 2, fillColor: '#888', fillOpacity: 0.85, dashArray: '3,2' };
const RELOCATED_PING_STYLE = { radius: 5, color: '#e65100', weight: 2, fillColor: '#ffb74d', fillOpacity: 0.9 };
const RELOCATION_LINE_STYLE = { color: '#e65100', weight: 1, dashArray: '3,4', opacity: 0.7, interactive: false };
const LASSO_SELECT_STYLE  = { color: '#1b5e20', weight: 2, fillColor: '#66bb6a', fillOpacity: 0.18, dashArray: '4,4', interactive: false };
window.__selectionModeActive = false;

// Build the gray suppressed-pings ghost layer and the amber relocated-pings
// ghost layer (with provenance lines), publish them on `window.__…`, then
// enable/disable the two "Show …" toggles based on whether the trip actually
// has any. Called from the GPS-track .then() before any short-circuit, so the
// admin can still surface and undo overrides on trips whose polyline is
// skipped (too few in-window pings, or none near a stay/event).
function _buildSuppressedRelocatedLayers(suppressedInWindow, relocatedInWindow) {
  // Suppressed pings: gray dashed dots, click → unsuppress.
  const suppressedSorted = suppressedInWindow.slice().sort((a, b) => a.tst - b.tst);
  const suppressedPointLayer = L.layerGroup();
  suppressedSorted.forEach(p => {
    const m = L.circleMarker([p.lat, p.lon], { ...SUPPRESSED_PING_STYLE, pane: 'overrides' });
    m.__ping = p;
    const dt = new Date(p.tst * 1000);
    const fmtOpts = {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      timeZoneName: 'short',
    };
    if (p.tz) fmtOpts.timeZone = p.tz;
    const local = dt.toLocaleString(undefined, fmtOpts);
    const coords = `${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`;
    m.bindTooltip(`Suppressed · ${local}<br><span style="font-family:monospace">${coords}</span><br><em>click to unsuppress</em>`, { sticky: true });
    m.on('click', () => unsuppressPing(p.tst));
    suppressedPointLayer.addLayer(m);
  });
  window.__suppressedPointLayer = suppressedPointLayer;
  window.__suppressedCount = suppressedSorted.length;

  // Relocated pings: amber dots at the override coords + dashed line back to
  // the original OwnTracks coords, click → unrelocate (restores every ping
  // sharing this clicked one's override coords; see `unrelocatePing`).
  const relocatedSorted = relocatedInWindow.slice().sort((a, b) => a.tst - b.tst);
  const relocatedPointLayer = L.layerGroup();
  // Pre-tally the cluster size at each override (lat,lon) so the per-marker
  // tooltip can hint when a single click will restore the whole cluster (the
  // common shape after "Center selected" collapses many pings onto one point).
  const _coordKey = (lat, lon) => `${lat},${lon}`;
  const clusterCounts = new Map();
  relocatedSorted.forEach(p => {
    const k = _coordKey(p.lat, p.lon);
    clusterCounts.set(k, (clusterCounts.get(k) || 0) + 1);
  });
  relocatedSorted.forEach(p => {
    const dt = new Date(p.tst * 1000);
    const fmtOpts = {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      timeZoneName: 'short',
    };
    if (p.tz) fmtOpts.timeZone = p.tz;
    const local = dt.toLocaleString(undefined, fmtOpts);
    const newCoords = `${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`;
    const origCoords = (p.original_lat != null && p.original_lon != null)
      ? `${p.original_lat.toFixed(5)}, ${p.original_lon.toFixed(5)}`
      : '(unknown)';
    const m = L.circleMarker([p.lat, p.lon], { ...RELOCATED_PING_STYLE, pane: 'overrides' });
    m.__ping = p;
    const clusterN = clusterCounts.get(_coordKey(p.lat, p.lon)) || 1;
    const restoreHint = clusterN > 1
      ? `<em>click to restore all ${clusterN} pings at this location</em>`
      : '<em>click to restore</em>';
    m.bindTooltip(
      `Relocated · ${local}<br>` +
      `<span style="font-family:monospace">from ${origCoords}<br>to&nbsp;&nbsp;${newCoords}</span><br>` +
      restoreHint,
      { sticky: true });
    m.on('click', () => unrelocatePing(p.tst));
    relocatedPointLayer.addLayer(m);
    if (p.original_lat != null && p.original_lon != null) {
      relocatedPointLayer.addLayer(L.polyline(
        [[p.original_lat, p.original_lon], [p.lat, p.lon]],
        { ...RELOCATION_LINE_STYLE, pane: 'overrides' }));
    }
  });
  window.__relocatedPointLayer = relocatedPointLayer;
  window.__relocatedCount = relocatedSorted.length;

  // Enable/disable the "Show suppressed pings" / "Show relocated pings"
  // toggles. Stay disabled when the trip has nothing of that kind — no UI
  // to reveal — but otherwise become clickable regardless of polyline state.
  const showSupToggle = document.getElementById('show-suppressed-toggle');
  const showSupLabel = document.getElementById('show-suppressed-label');
  const supN = suppressedSorted.length;
  if (showSupToggle) showSupToggle.disabled = (supN === 0);
  if (showSupLabel) {
    showSupLabel.classList.toggle('disabled', supN === 0);
    showSupLabel.title = supN
      ? `Reveal ${supN} previously-suppressed ping${supN === 1 ? '' : 's'} as gray dots; click one to unsuppress`
      : 'No pings are currently suppressed for this trip';
  }
  const showRelToggle = document.getElementById('show-relocated-toggle');
  const showRelLabel = document.getElementById('show-relocated-label');
  const relN = relocatedSorted.length;
  if (showRelToggle) showRelToggle.disabled = (relN === 0);
  if (showRelLabel) {
    showRelLabel.classList.toggle('disabled', relN === 0);
    showRelLabel.title = relN
      ? `Reveal ${relN} relocated ping${relN === 1 ? '' : 's'} (amber, with provenance lines); click one to restore its original location`
      : 'No pings are currently relocated for this trip';
  }
  // Re-apply pre-checked state across location.reload(): if the toggle came
  // up checked (browser form-state restoration), add the ghost layer now so
  // the dots appear without needing a click.
  if (showSupToggle && showSupToggle.checked && !showSupToggle.disabled) {
    toggleShowSuppressed(showSupToggle);
  }
  if (showRelToggle && showRelToggle.checked && !showRelToggle.disabled) {
    toggleShowRelocated(showRelToggle);
  }
}

// Shared bookkeeping for select-pings mode: keeps the cursor crosshair, the
// map-drag suppression, and the per-point markers' visibility consistent.
function _syncLassoModes() {
  const sel = window.__selectionModeActive;
  if (window.tripMap) {
    if (sel) window.tripMap.dragging.disable();
    else window.tripMap.dragging.enable();
  }
  document.body.classList.toggle('map-selection-mode', sel);
  if (window.__syncGpsPoints) window.__syncGpsPoints();
}

function toggleSelectionMode(checkbox) {
  window.__selectionModeActive = !!checkbox.checked;
  const tb = document.getElementById('selection-toolbar');
  if (tb) tb.classList.toggle('visible', window.__selectionModeActive);
  if (!window.__selectionModeActive) clearPingSelection();
  _syncLassoModes();
}

// Wire up the click-and-drag lasso circle on the trip map. Called once from
// the GPS-track-loaded callback so it has access to `map` and the per-ping
// markers — it's a no-op until "Select pings" mode is on.
//
// On mouseup every ping inside the circle is added to the selection. Bulk
// relocation lives on the toolbar's "Center selected" button now (collapses
// the selection onto its centroid via /api/trips/<id>/relocate-pings); the
// drag-a-selected-ping gesture still does freeform translation.
function _initSelectionLasso(map) {
  if (window.__selectionLassoReady) return;
  window.__selectionLassoReady = true;

  const PIXEL_THRESHOLD = 4;  // ignore micro-movements so plain clicks still toggle pings
  let dragStartLatLng = null;
  let dragStartPoint = null;
  let lassoCircle = null;

  function cleanup() {
    if (lassoCircle) {
      map.removeLayer(lassoCircle);
      lassoCircle = null;
    }
    dragStartLatLng = null;
    dragStartPoint = null;
  }

  map.on('mousedown', (e) => {
    if (!window.__selectionModeActive) return;
    // The selection-drag gesture (mousedown on a SELECTED ping in select
    // mode) sets this flag in its marker handler before the event bubbles
    // up; bail so we don't also start a lasso underneath the drag.
    if (window.__selectionDragInProgress) return;
    dragStartLatLng = e.latlng;
    dragStartPoint = e.containerPoint;
  });

  map.on('mousemove', (e) => {
    if (!window.__selectionModeActive || !dragStartPoint) return;
    const dx = e.containerPoint.x - dragStartPoint.x;
    const dy = e.containerPoint.y - dragStartPoint.y;
    if (Math.hypot(dx, dy) < PIXEL_THRESHOLD) return;
    const radiusMeters = dragStartLatLng.distanceTo(e.latlng);
    if (!lassoCircle) {
      lassoCircle = L.circle(dragStartLatLng, { ...LASSO_SELECT_STYLE, radius: radiusMeters }).addTo(map);
    } else {
      lassoCircle.setRadius(radiusMeters);
    }
  });

  map.on('mouseup', () => {
    // Capture the circle data and clean the visual *before* any synchronous
    // confirm() so the user isn't staring at the lasso while answering.
    let circleData = null;
    if (lassoCircle) {
      circleData = { center: lassoCircle.getLatLng(), radius: lassoCircle.getRadius() };
    }
    cleanup();
    if (!window.__selectionModeActive || !circleData) return;
    const inside = (window.__gpsPointMarkers || []).filter(m =>
      circleData.center.distanceTo(m.getLatLng()) <= circleData.radius);
    inside.forEach(m => {
      if (m.__selected) return;
      m.__selected = true;
      m.setStyle(SELECTED_PING_STYLE);
      if (m.bringToFront) m.bringToFront();
    });
    updateSelectionToolbar();
  });

  // Cancel a half-drawn circle if the cursor leaves the map mid-drag.
  map.on('mouseout', (e) => {
    if (e.originalEvent && map.getContainer().contains(e.originalEvent.relatedTarget)) return;
    if (lassoCircle || dragStartPoint) cleanup();
  });
}

// Wire mousedown-on-selected-ping → drag the entire selection by the cursor
// delta. Preserves each ping's offset relative to the dragged one so the
// shape of the cluster is kept; on drop, every selected ping is POSTed to
// /api/trips/<id>/relocate-pings at its new lat/lon. A stationary mousedown
// (under PIXEL_THRESHOLD) is left alone so the existing click-toggle still
// fires; the same threshold gates the post-drag click suppression so an
// accidental nudge doesn't pop a confirm dialog the user can't escape from.
// Two-phase init:
//   Phase 1 (once per page load): set up the closure-scoped `dragState`,
//   `onMouseMove`, `onMouseUp` plus a `__rebindSelectionDrag` window-exposed
//   binder that attaches `mousedown` handlers to the *current* per-ping
//   marker objects.
//   Phase 2 (every renderGpsTrack): call `__rebindSelectionDrag` to wire the
//   handlers onto the freshly-built `__gpsPointMarkers`. Without this, a
//   suppress/relocate-driven re-render would leave drag handlers stuck on
//   the previous render's marker objects (now orphaned), so dragging a
//   selection would do nothing.
function _initSelectionDrag(map) {
  if (window.__selectionDragReady) {
    if (window.__rebindSelectionDrag) window.__rebindSelectionDrag();
    return;
  }
  window.__selectionDragReady = true;

  const PIXEL_THRESHOLD = 4;
  let dragState = null;

  function onMouseMove(e) {
    if (!dragState) return;
    const dx = e.clientX - dragState.startClientX;
    const dy = e.clientY - dragState.startClientY;
    if (!dragState.dragging && Math.hypot(dx, dy) < PIXEL_THRESHOLD) return;
    if (!dragState.dragging) {
      dragState.dragging = true;
      document.body.classList.add('selection-dragging');
    }
    const cur = map.containerPointToLatLng(map.mouseEventToContainerPoint(e));
    const dLat = cur.lat - dragState.startLatLng.lat;
    const dLng = cur.lng - dragState.startLatLng.lng;
    dragState.markers.forEach(({marker, origLat, origLng}) => {
      marker.setLatLng([origLat + dLat, origLng + dLng]);
    });
  }

  function snapBack(ds) {
    ds.markers.forEach(({marker, origLat, origLng}) => {
      marker.setLatLng([origLat, origLng]);
    });
  }

  function onMouseUp(e) {
    if (!dragState) return;
    document.removeEventListener('mousemove', onMouseMove, true);
    document.removeEventListener('mouseup', onMouseUp, true);
    document.body.classList.remove('selection-dragging');

    const wasDragged = dragState.dragging;
    const ds = dragState;
    dragState = null;
    // Always release the lasso-suppression flag on the next tick (after the
    // map's mousedown handler — which is already past — has had its turn).
    setTimeout(() => { window.__selectionDragInProgress = false; }, 0);

    if (!wasDragged) return;  // pure click — let the existing toggle fire.

    // Suppress the click event Leaflet fires on the dragged marker right
    // after this mouseup, so we don't deselect it under the user's cursor.
    window.__selectionDragJustEnded = true;
    setTimeout(() => { window.__selectionDragJustEnded = false; }, 0);

    const cur = map.containerPointToLatLng(map.mouseEventToContainerPoint(e));
    const dLat = cur.lat - ds.startLatLng.lat;
    const dLng = cur.lng - ds.startLatLng.lng;
    // `orig_lat`/`orig_lon` are the ping's RAW OwnTracks coords — sent so
    // the server can disambiguate duplicate-tst pings (OwnTracks emits
    // these routinely). For an already-relocated marker the admin-mode
    // response tags the raw coords on __ping; for a never-touched ping
    // the drag-start position IS the raw coord.
    const items = ds.markers.map(({marker, origLat, origLng}) => {
      const p = marker.__ping;
      const trueOrigLat = (p.original_lat != null) ? p.original_lat : origLat;
      const trueOrigLng = (p.original_lon != null) ? p.original_lon : origLng;
      return {
        tst: p.tst,
        lat: origLat + dLat,
        lon: origLng + dLng,
        orig_lat: trueOrigLat,
        orig_lon: trueOrigLng,
      };
    });
    const ok = confirm(
      `Move ${items.length} GPS ping${items.length === 1 ? '' : 's'} to a new ` +
      `location? Use the "Show relocated pings" toggle to review or undo.`
    );
    if (!ok) { snapBack(ds); return; }

    fetch(`/api/trips/${TRIP_ID}/relocate-pings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items }),
    })
      .then(r => r.json())
      .then(data => {
        if (data.error) { alert(data.error); snapBack(ds); return; }
        // Drag-relocate is GPS-only; refetch the track and re-render in
        // place rather than reloading the whole page.
        refetchAndRenderTrack();
      })
      .catch(err => { snapBack(ds); alert('Failed to move pings: ' + err); });
  }

  function bindMarker(marker) {
    // Guard against double-binding the same marker if `__rebindSelectionDrag`
    // is ever invoked twice with the same array (cheap belt-and-braces).
    if (marker.__selectionDragBound) return;
    marker.__selectionDragBound = true;
    marker.on('mousedown', ev => {
      if (!window.__selectionModeActive) return;
      if (!marker.__selected) return;
      // Tell the lasso's map.on('mousedown') to skip — set BEFORE the event
      // bubbles up. Cleared in onMouseUp's timeout.
      window.__selectionDragInProgress = true;
      L.DomEvent.stop(ev.originalEvent || ev);

      const cursor = map.containerPointToLatLng(
        map.mouseEventToContainerPoint(ev.originalEvent || ev));
      const allSelected = (window.__gpsPointMarkers || [])
        .filter(m => m.__selected);
      dragState = {
        startClientX: (ev.originalEvent || ev).clientX,
        startClientY: (ev.originalEvent || ev).clientY,
        startLatLng: cursor,
        dragging: false,
        markers: allSelected.map(m => {
          const ll = m.getLatLng();
          return { marker: m, origLat: ll.lat, origLng: ll.lng };
        }),
      };
      document.addEventListener('mousemove', onMouseMove, true);
      document.addEventListener('mouseup', onMouseUp, true);
    });
  }

  // Expose so renderGpsTrack can re-bind to the freshly-built marker objects
  // on every refetch. The closure above (dragState/onMouseMove/onMouseUp) is
  // shared across all renders.
  window.__rebindSelectionDrag = function() {
    (window.__gpsPointMarkers || []).forEach(bindMarker);
  };
  window.__rebindSelectionDrag();
}

function togglePingSelection(i) {
  const markers = window.__gpsPointMarkers;
  if (!markers || !markers[i]) return;
  const m = markers[i];
  m.__selected = !m.__selected;
  m.setStyle(m.__selected ? SELECTED_PING_STYLE : DEFAULT_PING_STYLE);
  if (m.__selected && m.bringToFront) m.bringToFront();
  updateSelectionToolbar();
}

function getSelectedPings() {
  const markers = window.__gpsPointMarkers || [];
  // Sort by tst so the first/last are well-defined.
  return markers.filter(m => m.__selected).map(m => m.__ping)
    .sort((a, b) => a.tst - b.tst);
}

function clearPingSelection() {
  (window.__gpsPointMarkers || []).forEach(m => {
    if (m.__selected) {
      m.__selected = false;
      m.setStyle(DEFAULT_PING_STYLE);
    }
  });
  updateSelectionToolbar();
}

function updateSelectionToolbar() {
  const tb = document.getElementById('selection-toolbar');
  if (!tb) return;
  const n = getSelectedPings().length;
  // .sel-count lives on the checkbox row, not inside the toolbar — look it
  // up by id rather than scoping under tb.
  const count = document.getElementById('sel-count');
  if (count) count.textContent = n + ' ping' + (n === 1 ? '' : 's') + ' selected';
  tb.querySelectorAll('button[data-needs-selection]').forEach(b => { b.disabled = n === 0; });
}

// Uncheck the "Select pings" toggle so the upcoming location.reload() comes
// back with selection mode off — the user just consumed their selection by
// creating an event/waypoint or setting a campsite location.
function _disableSelectionToggleBeforeReload() {
  const selToggle = document.getElementById('selection-mode-toggle');
  if (selToggle) selToggle.checked = false;
}

// Format a ping's timestamp as YYYY-MM-DD in the ping's local timezone.
function _pingLocalDate(p) {
  const opts = { year: 'numeric', month: '2-digit', day: '2-digit' };
  if (p.tz) opts.timeZone = p.tz;
  // en-CA gives ISO-style YYYY-MM-DD ordering.
  const parts = new Intl.DateTimeFormat('en-CA', opts).formatToParts(new Date(p.tst * 1000));
  const get = t => (parts.find(x => x.type === t) || {}).value || '';
  return get('year') + '-' + get('month') + '-' + get('day');
}
function _pingLocalTime(p) {
  const opts = { hour: '2-digit', minute: '2-digit', hour12: false };
  if (p.tz) opts.timeZone = p.tz;
  // en-GB gives 24-hour HH:MM.
  return new Date(p.tst * 1000).toLocaleTimeString('en-GB', opts).slice(0, 5);
}

function createFromSelection(kind) {
  const pings = getSelectedPings();
  if (!pings.length) return;
  const avgLat = pings.reduce((s, p) => s + p.lat, 0) / pings.length;
  const avgLng = pings.reduce((s, p) => s + p.lon, 0) / pings.length;
  const first = pings[0];
  const last = pings[pings.length - 1];
  const startDate = _pingLocalDate(first);
  const endDate = _pingLocalDate(last);
  const startTime = _pingLocalTime(first);
  const endTime = _pingLocalTime(last);
  // Events are single-date in this app's data model; if the selection spans
  // multiple days, use the start date and let the time range carry the rest.
  if (startDate !== endDate) {
    console.warn('Ping selection spans multiple days (' + startDate + ' → ' + endDate +
                 '); using start date with full time range.');
  }
  const isWp = (kind === 'waypoint');
  const values = {
    name: isWp ? 'New Waypoint' : '',
    date: startDate,
    time: startTime,
    end_time: endTime,
    location: avgLat.toFixed(6) + ',' + avgLng.toFixed(6),
    locale: '',
    state: '',
    description: '',
    waypoint: isWp,
  };
  // Tell submitAddModal to turn off selection mode after a successful save.
  // Cleared in closeAddModal so a canceled modal doesn't poison a later one.
  window.__createFromSelection = true;
  _openModal(kind, 'add', null, values);

  // Reverse-geocode the centroid to suggest name/locale/state. Run async so
  // the modal opens immediately; the helper only fills fields the user
  // hasn't started editing.
  _fillModalFromReverseGeocode(avgLat, avgLng);
}

// Set the campsite_location override on whichever campspot is currently
// closest to the selection's centroid. Useful when the campground's listed
// coordinates point to the office/entrance and the GPS pings reveal where
// EKKO actually parked.
function _haversineKm(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) * Math.sin(dLng/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function setCampsiteFromSelection() {
  const pings = getSelectedPings();
  if (!pings.length) return;
  const avgLat = pings.reduce((s, p) => s + p.lat, 0) / pings.length;
  const avgLng = pings.reduce((s, p) => s + p.lon, 0) / pings.length;

  // Only campspots with a real campground reference are eligible — custom
  // places (Airbnb/hotel) already represent specific locations, and stays
  // without resolved coordinates can't be ranked.
  const candidates = STAYS_ALL
    .map((s, i) => ({ stay: s, idx: i }))
    .filter(({ stay }) => stay.campground_id != null && stay.lat != null && stay.lng != null);
  if (!candidates.length) {
    alert('No campspots with a campground reference are available on this trip.');
    return;
  }

  let best = null;
  candidates.forEach(c => {
    const d = _haversineKm(avgLat, avgLng, c.stay.lat, c.stay.lng);
    if (!best || d < best.d) best = { ...c, d };
  });

  const newLoc = avgLat.toFixed(6) + ',' + avgLng.toFixed(6);
  const distKm = best.d.toFixed(2);
  const place = best.stay.place || '(unnamed)';
  const existing = (best.stay.campsite_location || '').trim();
  const existingLine = existing ? `\nReplaces existing override: ${existing}` : '';
  const ok = confirm(
    `Set campsite location for "${place}" to ${newLoc}?\n\n` +
    `Nearest campspot is ${distKm} km from the selection centroid.` +
    existingLine
  );
  if (!ok) return;

  fetch(`/api/trips/${TRIP_ID}/stays/${best.idx}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ campsite_location: newLoc }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      _disableSelectionToggleBeforeReload();
      _reloadKeepingMapView();
    })
    .catch(err => alert('Failed to update campsite location: ' + err));
}

// ── GPS-ping suppression ──────────────────────────────────────────────────
// Server keeps a per-trip list of `tst` values to filter out of the GPS
// track. Suppressing is a "consume the selection" action just like
// creating an event/waypoint, so it auto-uncheck Select pings on success.

function suppressFromSelection() {
  const pings = getSelectedPings();
  if (!pings.length) return;
  const tsts = pings.map(p => p.tst);
  const ok = confirm(
    `Suppress ${tsts.length} GPS ping${tsts.length === 1 ? '' : 's'}? ` +
    `They'll be hidden from the polyline and per-point markers on every load. ` +
    `Use the "Show suppressed pings" toggle to review or undo.`
  );
  if (!ok) return;
  fetch(`/api/trips/${TRIP_ID}/suppress-pings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tst: tsts }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      // refetchAndRenderTrack() clears the selection toggle internally.
      refetchAndRenderTrack();
    })
    .catch(err => alert('Failed to suppress pings: ' + err));
}

function toggleShowSuppressed(checkbox) {
  const layer = window.__suppressedPointLayer;
  if (!layer || !window.tripMap) return;
  if (checkbox.checked) {
    if (!window.tripMap.hasLayer(layer)) layer.addTo(window.tripMap);
  } else {
    if (window.tripMap.hasLayer(layer)) window.tripMap.removeLayer(layer);
  }
}

// ── GPS-ping relocation ───────────────────────────────────────────────────
// "Center selected" toolbar action: collapse every selected ping onto the
// arithmetic centroid of their current positions and POST {tst, lat, lon}
// overrides for the whole batch. The polyline on the next render flows
// through the new positions instead of the OwnTracks-reported ones.
//
// Re-relocating an already-moved ping: the override entry is keyed by
// `tst`, so a second center pass simply replaces the previous target — no
// need to undo first. The selection may include a mix of fresh and
// previously-moved pings; both end up at the new centroid.
//
// Undo: turn on "Show relocated pings" and click any amber dot.
//
// (Freeform translation — preserving the cluster's shape — still lives on
// the mousedown-drag-a-selected-ping gesture in `_initSelectionDrag`.)

function centerSelectedPings() {
  const pings = getSelectedPings();
  if (!pings.length) return;
  const center = {
    lat: pings.reduce((s, p) => s + p.lat, 0) / pings.length,
    lng: pings.reduce((s, p) => s + p.lon, 0) / pings.length,
  };
  // See the drag-relocate item builder above for why orig_lat/orig_lon
  // are sent: it lets the server pick the exact ping among duplicate-tst
  // siblings instead of relocating all of them.
  const items = pings.map(p => ({
    tst: p.tst,
    lat: center.lat,
    lon: center.lng,
    orig_lat: (p.original_lat != null) ? p.original_lat : p.lat,
    orig_lon: (p.original_lon != null) ? p.original_lon : p.lon,
  }));
  const ok = confirm(
    `Center ${items.length} selected GPS ping${items.length === 1 ? '' : 's'} on ` +
    `${center.lat.toFixed(5)}, ${center.lng.toFixed(5)}? ` +
    `Use the "Show relocated pings" toggle to review or undo.`
  );
  if (!ok) return;
  fetch(`/api/trips/${TRIP_ID}/relocate-pings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      // refetchAndRenderTrack() clears the selection toggle internally.
      refetchAndRenderTrack();
    })
    .catch(err => alert('Failed to center pings: ' + err));
}

function toggleShowRelocated(checkbox) {
  const layer = window.__relocatedPointLayer;
  if (!layer || !window.tripMap) return;
  if (checkbox.checked) {
    if (!window.tripMap.hasLayer(layer)) layer.addTo(window.tripMap);
  } else {
    if (window.tripMap.hasLayer(layer)) window.tripMap.removeLayer(layer);
  }
}

function unrelocatePing(tst) {
  // Restoring just the clicked ping's tst would leave any siblings collapsed
  // onto the same override coords (typical after "Center selected") stranded
  // at a now-orphaned point — the user almost always wants the whole cluster
  // back. Walk the relocated layer for every ping that shares the clicked
  // one's override lat/lon and DELETE the lot in one call. Float equality is
  // fine here: every member of a cluster gets the identical centroid value
  // assigned at creation time and survives JSON roundtrip bit-exactly.
  //
  // Sends precise (tst, orig_lat, orig_lon) items so a sibling ping that
  // happens to share this tst but was relocated *separately* (different
  // override coords) is left alone. Falls back to the by-tst legacy shape
  // for ghost-layer entries that lack the originals (older trips.json
  // entries written before the disambiguator).
  const layer = window.__relocatedPointLayer;
  let target = null;
  if (layer) {
    layer.eachLayer(m => {
      if (m.__ping && m.__ping.tst === tst) target = m.__ping;
    });
  }
  const items = [];
  if (target && layer) {
    layer.eachLayer(m => {
      if (!m.__ping) return;
      if (m.__ping.lat === target.lat && m.__ping.lon === target.lon) {
        const it = { tst: m.__ping.tst };
        if (m.__ping.original_lat != null && m.__ping.original_lon != null) {
          it.orig_lat = m.__ping.original_lat;
          it.orig_lon = m.__ping.original_lon;
        }
        items.push(it);
      }
    });
  }
  if (!items.length) items.push({ tst });  // fallback: just the clicked one
  const msg = items.length > 1
    ? `Restore ${items.length} GPS pings (all sharing this override location) to their original positions?`
    : 'Restore this GPS ping to its original location?';
  if (!confirm(msg)) return;
  fetch(`/api/trips/${TRIP_ID}/relocate-pings`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      refetchAndRenderTrack();
    })
    .catch(err => alert('Failed to restore ping: ' + err));
}

// Click handler bound to each suppressed-ping marker. Single ping at a
// time — bulk un-suppress via Select-pings + lasso isn't supported here
// because the lasso targets `__gpsPointMarkers` (non-suppressed only) by
// design.
function unsuppressPing(tst) {
  if (!confirm('Restore this GPS ping?')) return;
  fetch(`/api/trips/${TRIP_ID}/suppress-pings`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tst: [tst] }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      // Re-render so the polyline + regular markers pick the restored ping
      // back up. Leave the "Show suppressed" toggle as-is — if the user
      // had it on, they're probably reviewing more — `_buildSuppressedRelocatedLayers`
      // re-applies the checked state to the freshly-built layer.
      refetchAndRenderTrack();
    })
    .catch(err => alert('Failed to unsuppress ping: ' + err));
}
