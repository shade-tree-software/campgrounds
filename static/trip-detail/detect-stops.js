// ── Detect Stops (admin, desktop) ─────────────────────────────────────────
// One-shot scan of the trip's GPS track for clusters of consecutive pings
// in close proximity that aren't already represented by a stay, event,
// waypoint, or family location. Server proposes them as waypoints (short
// stops) or events (longer stops); the client then reverse-geocodes each
// suggestion sequentially (1 s throttle per Nominatim policy) so the
// modal can render immediately and show progress. Admin picks which to
// keep. Created entries are flagged needs_vetting so the admin can see
// at a glance which still need attention.
let DETECT_STOPS_DATA = [];
let DETECT_STOPS_ABORT = null;          // AbortController for the current run
let DETECT_STOPS_GEOCODING = false;     // true while the reverse-geocoding loop is running
// Per-row Leaflet mini-map instances keyed by stop idx. Tracked so we
// can `.remove()` the old map before re-init on geocoding re-render
// (re-rendering the row's outerHTML orphans the previous instance) and
// to tear everything down when the modal closes.
const DETECT_STOPS_MAPS = {};
let DETECT_STOPS_MAP_OBSERVER = null;   // IntersectionObserver for lazy-init

// Initialize a small satellite map inside a row's .stop-mini-map slot,
// fit to the cluster's ping coords. Replaces any prior map at that
// idx (geocoding re-render destroys + recreates the slot, so the old
// instance must be cleaned up explicitly). Drawn:
//  - Esri satellite tile layer
//  - Navy polyline of the ping path (matches main map convention)
//  - Tiny per-ping dots
//  - Red centroid marker
// All interactions disabled — the slot is a static preview, not a
// usable map.
function _initStopMiniMap(stopIdx) {
  const s = DETECT_STOPS_DATA[stopIdx];
  if (!s) return;
  const slot = document.querySelector(`.stop-mini-map[data-stop-map="${stopIdx}"]`);
  if (!slot) return;
  const prior = DETECT_STOPS_MAPS[stopIdx];
  if (prior) {
    try { prior.remove(); } catch (e) { /* already torn down */ }
    delete DETECT_STOPS_MAPS[stopIdx];
  }
  const d = s.display;
  const coords = Array.isArray(d.coords)
    ? d.coords.filter(c => Array.isArray(c) && c.length === 2 && Number.isFinite(c[0]) && Number.isFinite(c[1]))
    : [];
  const center = [d.center_lat, d.center_lng];
  const map = L.map(slot, {
    attributionControl: false,
    zoomControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    touchZoom: false,
    boxZoom: false,
    keyboard: false,
    tap: false,
    fadeAnimation: false,
    zoomAnimation: false,
  });
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
  }).addTo(map);
  if (coords.length >= 2) {
    L.polyline(coords, { color: '#ffffff', weight: 3, opacity: 0.55 }).addTo(map);
    L.polyline(coords, { color: '#002868', weight: 2, opacity: 0.95 }).addTo(map);
    coords.forEach(c => {
      L.circleMarker(c, {
        radius: 2, color: '#ffffff', weight: 1,
        fillColor: '#002868', fillOpacity: 1,
      }).addTo(map);
    });
    map.fitBounds(L.latLngBounds(coords), { padding: [8, 8], maxZoom: 18, animate: false });
  } else if (coords.length === 1) {
    map.setView(coords[0], 18);
    L.circleMarker(coords[0], {
      radius: 2, color: '#ffffff', weight: 1,
      fillColor: '#002868', fillOpacity: 1,
    }).addTo(map);
  } else {
    map.setView(center, 18);
  }
  L.circleMarker(center, {
    radius: 4, color: '#ffffff', weight: 1,
    fillColor: '#bf0a30', fillOpacity: 1,
  }).addTo(map);
  DETECT_STOPS_MAPS[stopIdx] = map;
}

// Lazy-init via IntersectionObserver. Detect-stops modals can have
// 20+ rows; only ~5–8 are visible at once. Wiring an observer means
// off-screen rows don't pay the tile-fetch + Leaflet init cost until
// the admin scrolls to them.
function _observeStopMiniMaps() {
  if (DETECT_STOPS_MAP_OBSERVER) {
    DETECT_STOPS_MAP_OBSERVER.disconnect();
    DETECT_STOPS_MAP_OBSERVER = null;
  }
  DETECT_STOPS_MAP_OBSERVER = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const idx = +entry.target.dataset.stopMap;
      _initStopMiniMap(idx);
      // One-shot per slot — once initialized, stop watching.
      DETECT_STOPS_MAP_OBSERVER.unobserve(entry.target);
    });
  }, {
    root: document.getElementById('detect-stops-list'),
    rootMargin: '120px 0px',
  });
  document.querySelectorAll('#detect-stops-list .stop-mini-map').forEach(el => {
    DETECT_STOPS_MAP_OBSERVER.observe(el);
  });
}

function _destroyAllStopMiniMaps() {
  if (DETECT_STOPS_MAP_OBSERVER) {
    DETECT_STOPS_MAP_OBSERVER.disconnect();
    DETECT_STOPS_MAP_OBSERVER = null;
  }
  Object.keys(DETECT_STOPS_MAPS).forEach(k => {
    try { DETECT_STOPS_MAPS[k].remove(); } catch (e) { /* ignore */ }
    delete DETECT_STOPS_MAPS[k];
  });
}

function _renderDetectStopRow(s, i) {
  const d = s.display;
  const dur = d.duration_minutes < 60
    ? `${Math.round(d.duration_minutes)} min`
    : `${(d.duration_minutes / 60).toFixed(1)} hr`;
  // A row is "pending" until its reverse-geocode lookup resolves; in
  // that state we replace the locale/state line with a "(reverse-
  // geocoding…)" badge so the admin can see which rows are still being
  // looked up. Once name has been overwritten from its placeholder OR
  // locale/state arrive, the row is no longer pending.
  const pending = (s.event.name === 'Detected stop'
                   && !s.event.locale && !s.event.state);
  // On-road rows default to unchecked (centroid snapped to a real road
  // — almost always traffic, not a stop). The badge + dim styling let
  // the admin opt back in for a legit roadside stop.
  const onRoad = d.on_road === true;
  const name = s.event.name || '(unnamed)';
  const place = [d.start_local, dur].filter(Boolean).join(' · ');
  const loc = [s.event.locale, s.event.state].filter(Boolean).join(', ');
  const coords = `${d.center_lat.toFixed(4)}, ${d.center_lng.toFixed(4)}`;
  const tail = pending
    ? '<span style="opacity:.6;font-style:italic;">reverse-geocoding…</span>'
    : (loc ? escapeHtml(loc) : '<span style="opacity:.5;">(no locale found)</span>');
  const trafficTag = onRoad
    ? ' <span class="stop-traffic-tag" title="Cluster centroid snapped to a real road — usually a traffic jam or stop light, not a real stop. Check the box if this was actually a roadside stop.">on road · likely traffic</span>'
    : '';
  return `
    <label class="stop-row${onRoad ? ' on-road' : ''}" data-stop-idx="${i}">
      <input type="checkbox" data-idx="${i}" ${onRoad ? '' : 'checked'} onchange="updateDetectStopsCount()">
      <div>
        <div class="stop-name">${escapeHtml(name)}${trafficTag}</div>
        <div class="stop-meta">${escapeHtml(place)} — ${tail}</div>
        <div class="stop-meta" style="font-size:.72rem;opacity:.7;">${escapeHtml(coords)}${d.ping_count ? ' · ' + d.ping_count + ' pings' : ''}</div>
      </div>
      <div class="stop-mini-map" data-stop-map="${i}"></div>
      <span class="stop-kind ${d.classification}">${d.classification === 'event' ? 'Event' : 'Waypoint'}</span>
    </label>
  `;
}

function detectStops() {
  const btn = document.getElementById('btn-detect-stops');
  if (!btn) return;
  // Cancel any prior in-flight run (detect-stops POST or reverse-
  // geocode loop) before starting fresh.
  if (DETECT_STOPS_ABORT) DETECT_STOPS_ABORT.abort();
  DETECT_STOPS_ABORT = new AbortController();
  const signal = DETECT_STOPS_ABORT.signal;
  DETECT_STOPS_GEOCODING = false;

  const modal = document.getElementById('detect-stops-modal');
  document.getElementById('detect-stops-loading').style.display = '';
  document.getElementById('detect-stops-progress').style.display = 'none';
  document.getElementById('detect-stops-list').style.display = 'none';
  document.getElementById('detect-stops-list').innerHTML = '';
  document.getElementById('detect-stops-empty').style.display = 'none';
  const submitBtn = document.getElementById('detect-stops-submit');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Create selected';
  // Reset to visible at the start of every run — a prior "no stops"
  // run may have hidden it, and the empty/warning/error branches below
  // hide it again only when applicable.
  submitBtn.style.display = '';
  // The cancel button doubles as the "OK" acknowledgment in the
  // terminal no-stops / warning / error branches (where there's
  // nothing to submit). Reset to "Cancel" at the start of every run;
  // those branches flip it to "OK" when they hide the submit button.
  const cancelBtn = document.getElementById('detect-stops-cancel');
  cancelBtn.textContent = 'Cancel';
  modal.classList.add('visible');
  btn.disabled = true;

  fetch(`/api/trips/${TRIP_ID}/detect-stops`, { method: 'POST', signal })
    .then(r => r.json())
    .then(data => {
      if (signal.aborted) return;
      btn.disabled = false;
      document.getElementById('detect-stops-loading').style.display = 'none';
      DETECT_STOPS_DATA = data.stops || [];
      const listEl = document.getElementById('detect-stops-list');
      const emptyEl = document.getElementById('detect-stops-empty');
      if (data.warning) {
        emptyEl.textContent = data.warning;
        emptyEl.style.display = '';
        submitBtn.style.display = 'none';
        cancelBtn.textContent = 'OK';
        return;
      }
      if (!DETECT_STOPS_DATA.length) {
        emptyEl.textContent = 'No unaccounted stops detected on this trip.';
        emptyEl.style.display = '';
        submitBtn.style.display = 'none';
        cancelBtn.textContent = 'OK';
        return;
      }
      // Render rows with placeholders; reverse-geocoding fills them in
      // asynchronously. Default-checked so once geocoding finishes the
      // admin can hit "Create selected" without clicking each one.
      listEl.innerHTML = DETECT_STOPS_DATA.map((s, i) => _renderDetectStopRow(s, i)).join('');
      listEl.style.display = '';
      updateDetectStopsCount();
      _observeStopMiniMaps();
      _runDetectStopsGeocoding(signal);
    })
    .catch(err => {
      if (err.name === 'AbortError') return;
      btn.disabled = false;
      document.getElementById('detect-stops-loading').style.display = 'none';
      const emptyEl = document.getElementById('detect-stops-empty');
      emptyEl.textContent = 'Stop detection failed: ' + err.message;
      emptyEl.style.display = '';
      submitBtn.style.display = 'none';
      cancelBtn.textContent = 'OK';
    });
}

// Sequentially reverse-geocode every row in DETECT_STOPS_DATA, updating
// the row in place as each lookup resolves. Throttles to 1 req/sec to
// stay inside Nominatim's usage policy. The progress banner counts
// completed lookups; "Create selected" stays disabled until the whole
// loop finishes or the user closes the modal.
async function _runDetectStopsGeocoding(signal) {
  if (!DETECT_STOPS_DATA.length) return;
  DETECT_STOPS_GEOCODING = true;
  updateDetectStopsCount();  // force the disabled-state recompute
  const total = DETECT_STOPS_DATA.length;
  const progressEl = document.getElementById('detect-stops-progress');
  function showProgress(done) {
    progressEl.style.display = '';
    progressEl.textContent =
      done >= total
        ? `Reverse-geocoded ${total} of ${total} stops.`
        : `Reverse-geocoding ${done} of ${total} stops… (${total - done} remaining)`;
  }
  showProgress(0);
  for (let i = 0; i < DETECT_STOPS_DATA.length; i++) {
    if (signal.aborted) return;
    const s = DETECT_STOPS_DATA[i];
    try {
      const url = `/api/reverse-geocode?lat=${s.display.center_lat}&lng=${s.display.center_lng}`;
      const resp = await fetch(url, { signal });
      const info = await resp.json();
      if (signal.aborted) return;
      // Only overwrite fields we got something useful for; leave the
      // "Detected stop" placeholder otherwise so a failed lookup still
      // produces an acceptable event.
      if (info.name) s.event.name = info.name;
      if (info.locale) s.event.locale = info.locale;
      if (info.state) s.event.state = info.state;
      if (info.display_name) s.display.display_name = info.display_name;
      // on_road is a UI-only hint (lives on display, not event) — when
      // true, _renderDetectStopRow emits an unchecked box + traffic tag.
      s.display.on_road = !!info.on_road;
      // Re-render the row in place. Preserve checkbox state EXCEPT for
      // freshly-discovered on-road rows, which should land unchecked
      // even though they were checked on first render.
      const row = document.querySelector(`.stop-row[data-stop-idx="${i}"]`);
      if (row) {
        const wasChecked = row.querySelector('input[type="checkbox"]').checked;
        // The re-render replaces the .stop-mini-map slot. Track whether
        // a map was already live in this row — if so we need to re-init
        // after the replace (the observer would otherwise only fire on
        // the next intersect, which doesn't happen for already-visible
        // rows).
        const hadMap = !!DETECT_STOPS_MAPS[i];
        if (hadMap) {
          try { DETECT_STOPS_MAPS[i].remove(); } catch (e) { /* ignore */ }
          delete DETECT_STOPS_MAPS[i];
        }
        row.outerHTML = _renderDetectStopRow(s, i);
        const newRow = document.querySelector(`.stop-row[data-stop-idx="${i}"]`);
        if (newRow) {
          newRow.querySelector('input[type="checkbox"]').checked =
            s.display.on_road ? false : wasChecked;
          const slot = newRow.querySelector('.stop-mini-map');
          if (slot) {
            if (hadMap) {
              // Already-initialized rows get re-initialized immediately
              // so the visible map doesn't blink out and stay empty.
              _initStopMiniMap(i);
            } else if (DETECT_STOPS_MAP_OBSERVER) {
              // Not yet initialized — re-observe the new slot so it'll
              // init when it next scrolls into view.
              DETECT_STOPS_MAP_OBSERVER.observe(slot);
            }
          }
        }
      }
    } catch (e) {
      if (e.name === 'AbortError') return;
      // Network/server failure for this row — leave the placeholder
      // in place and keep going so other rows can still get names.
    }
    showProgress(i + 1);
    // Throttle to Nominatim's 1 req/sec policy. Skip after the final
    // call to avoid an unnecessary trailing wait before enabling the
    // submit button.
    if (i < DETECT_STOPS_DATA.length - 1) {
      try {
        await new Promise((resolve, reject) => {
          const tid = setTimeout(resolve, 1050);
          signal.addEventListener('abort',
            () => { clearTimeout(tid); reject(new DOMException('aborted', 'AbortError')); },
            { once: true });
        });
      } catch (e) {
        if (e.name === 'AbortError') return;
      }
    }
  }
  if (signal.aborted) return;
  DETECT_STOPS_GEOCODING = false;
  // Hide the banner once the loop's done; the row content already
  // reflects the final state.
  progressEl.style.display = 'none';
  updateDetectStopsCount();
}

function updateDetectStopsCount() {
  const checked = document.querySelectorAll('#detect-stops-list input[type="checkbox"]:checked');
  const btn = document.getElementById('detect-stops-submit');
  // Stay disabled while reverse-geocoding is still running, regardless
  // of how many rows the admin has checked — an un-geocoded row would
  // be created with the literal placeholder name "Detected stop", which
  // is rarely what they want.
  if (DETECT_STOPS_GEOCODING) {
    btn.disabled = true;
    btn.textContent = 'Create selected';
    return;
  }
  btn.disabled = checked.length === 0;
  btn.textContent = checked.length ? `Create ${checked.length} selected` : 'Create selected';
}

function submitDetectStops() {
  if (DETECT_STOPS_GEOCODING) return;  // belt-and-braces; the button should be disabled anyway
  const checked = document.querySelectorAll('#detect-stops-list input[type="checkbox"]:checked');
  if (!checked.length) return;
  const events = Array.from(checked).map(cb => DETECT_STOPS_DATA[+cb.dataset.idx].event);
  const btn = document.getElementById('detect-stops-submit');
  btn.disabled = true;
  btn.textContent = 'Creating…';
  fetch(`/api/trips/${TRIP_ID}/accept-stops`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ events }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); btn.disabled = false; updateDetectStopsCount(); return; }
      // Refresh the page so the new flagged events/waypoints render in
      // the timeline and on the map.
      window.location.reload();
    })
    .catch(err => {
      alert('Failed to create events: ' + err.message);
      btn.disabled = false;
      updateDetectStopsCount();
    });
}

function closeDetectStops() {
  // Aborting the controller cancels the detect-stops POST (if still in
  // flight) AND the sequential reverse-geocoding loop AND any open
  // /api/reverse-geocode fetch — so closing the modal doesn't leave a
  // background loop hitting Nominatim for stops the admin no longer
  // cares about.
  if (DETECT_STOPS_ABORT) {
    DETECT_STOPS_ABORT.abort();
    DETECT_STOPS_ABORT = null;
  }
  DETECT_STOPS_GEOCODING = false;
  _destroyAllStopMiniMaps();
  document.getElementById('detect-stops-modal').classList.remove('visible');
}
function closeDetectStopsBackdrop(e) {
  if (e.target.id === 'detect-stops-modal') closeDetectStops();
}
