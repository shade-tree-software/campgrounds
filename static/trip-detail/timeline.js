// ── Trip editing ──────────────────────────────────────────────────────────

// ── Campground autocomplete ──────────────────────────────────────────────
let CG_LIST = [];  // [{id, name, state, kind}]
if (IS_ADMIN) {
  fetch('/api/campgrounds')
    .then(r => r.json())
    .then(data => { CG_LIST = data; });
}

let cgActiveIdx = -1;

function cgFilter(input) {
  const dropdown = input.parentElement.querySelector('.cg-dropdown');
  const query = input.value.toLowerCase();
  if (!query || CG_LIST.length === 0) {
    dropdown.classList.remove('open');
    return;
  }
  const matches = CG_LIST.filter(c => c.name.toLowerCase().includes(query)).slice(0, 15);
  if (matches.length === 0) {
    dropdown.classList.remove('open');
    return;
  }
  cgActiveIdx = -1;
  dropdown.innerHTML = matches.map((c, i) => {
    const prefix = c.kind === 'family'
      ? '<span class="cg-family-icon" title="Family location">&#127968;</span>'
      : '';
    return `<div class="cg-option" data-idx="${i}" data-id="${c.id}" data-name="${escapeHtml(c.name)}" data-state="${escapeHtml(c.state)}" onmousedown="cgSelect(this)">${prefix}${escapeHtml(c.name)}<span class="cg-state">${escapeHtml(c.state)}</span></div>`;
  }).join('');
  dropdown.classList.add('open');
}

function cgSelect(optionEl) {
  const wrapper = optionEl.closest('.cg-autocomplete');
  const input = wrapper.querySelector('input[data-field="place"]');
  const idInput = wrapper.querySelector('input[data-field="campground_id"]');
  const dropdown = wrapper.querySelector('.cg-dropdown');
  input.value = optionEl.dataset.name;
  if (idInput) idInput.value = optionEl.dataset.id;
  dropdown.classList.remove('open');
  // Auto-fill state field in the same form
  const form = input.closest('.form-grid');
  if (form) {
    const stateInput = form.querySelector('[data-field="state"]');
    if (stateInput && optionEl.dataset.state) {
      stateInput.value = optionEl.dataset.state;
    }
  }
}

// Clear the hidden campground_id when the user edits the place text directly.
// If they later re-type a name that matches an existing entry exactly, we
// re-resolve it on save so hand-typed existing names still link cleanly.
function cgClearId(input) {
  const idInput = input.parentElement.querySelector('input[data-field="campground_id"]');
  if (idInput) idInput.value = '';
}

// Keyboard navigation for autocomplete
document.addEventListener('keydown', e => {
  const focused = document.activeElement;
  if (!focused || focused.dataset.field !== 'place') return;
  const dropdown = focused.parentElement.querySelector('.cg-dropdown');
  if (!dropdown.classList.contains('open')) return;
  const options = dropdown.querySelectorAll('.cg-option');
  if (options.length === 0) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    cgActiveIdx = Math.min(cgActiveIdx + 1, options.length - 1);
    options.forEach((o, i) => o.classList.toggle('active', i === cgActiveIdx));
    options[cgActiveIdx].scrollIntoView({ block: 'nearest' });
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    cgActiveIdx = Math.max(cgActiveIdx - 1, 0);
    options.forEach((o, i) => o.classList.toggle('active', i === cgActiveIdx));
    options[cgActiveIdx].scrollIntoView({ block: 'nearest' });
  } else if (e.key === 'Enter' && cgActiveIdx >= 0) {
    e.preventDefault();
    cgSelect(options[cgActiveIdx]);
  } else if (e.key === 'Escape') {
    dropdown.classList.remove('open');
  }
});

// Close dropdown when clicking outside
document.addEventListener('click', e => {
  if (!e.target.closest('.cg-autocomplete')) {
    document.querySelectorAll('.cg-dropdown.open').forEach(d => d.classList.remove('open'));
  }
});

// ── Trip-header "Actions ▾" dropdown ────────────────────────────────────────
// Admin-only menu consolidating add-campspot/event/waypoint/family,
// track source, detect stops, delete trip. The element only exists for
// admins (Jinja-gated), so every handler no-ops gracefully otherwise.
function toggleTripActions(e) {
  if (e) e.stopPropagation();
  const menu = document.getElementById('trip-actions');
  if (!menu) return;
  const open = menu.classList.toggle('open');
  const trigger = menu.querySelector('.btn-trip-actions');
  if (trigger) trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
}

function closeTripActions() {
  const menu = document.getElementById('trip-actions');
  if (!menu || !menu.classList.contains('open')) return;
  menu.classList.remove('open');
  const trigger = menu.querySelector('.btn-trip-actions');
  if (trigger) trigger.setAttribute('aria-expanded', 'false');
}

// Close the menu first, then run the chosen action. Closing first keeps
// the menu out of the way of any modal/confirm the action opens, and
// for Detect Stops it leaves the (hidden) #btn-detect-stops element in
// the DOM so detectStops()'s disable/enable logic still works.
function tripAction(fn) {
  closeTripActions();
  if (typeof fn === 'function') fn();
}

// Outside-click and Escape both dismiss the menu. Click handler is
// capture-phase-free (the trigger's onclick stopPropagation prevents
// this from immediately re-closing it on the opening click).
document.addEventListener('click', e => {
  if (!e.target.closest('#trip-actions')) closeTripActions();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeTripActions();
});

function editTripNote() {
  document.getElementById('trip-title').style.display = 'none';
  document.getElementById('trip-note-edit').classList.add('active');
  document.getElementById('trip-note-input').focus();
}

function cancelTripNote() {
  document.getElementById('trip-note-edit').classList.remove('active');
  document.getElementById('trip-title').style.display = '';
}

function saveTripNote() {
  const val = document.getElementById('trip-note-input').value.trim();
  fetch(`/api/trips/${TRIP_ID}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ trip_note: val })
  })
  .then(r => r.json())
  .then(data => {
    if (data.error) { alert(data.error); return; }
    _reloadKeepingMapView();
  });
}

function editHomeTime(which) {
  const manual = which === 'start' ? HOME_START_TIME : HOME_END_TIME;
  const auto = which === 'start' ? window.HOME_START_TIME_AUTO : window.HOME_END_TIME_AUTO;
  const label = which === 'start' ? 'Departure time from home' : 'Arrival time at home';
  const hint = manual
    ? '(currently overriding auto-detection — leave blank to clear and use GPS-derived time)'
    : auto
      ? `(GPS-derived time is ${auto}; set a manual override only if that looks wrong)`
      : '(no GPS data near home — set manually for a sensible boundary)';
  const val = prompt(`${label} (HH:MM, 24-hour) ${hint}`, manual || '');
  if (val === null) return;
  const trimmed = val.trim();
  if (trimmed && !/^\d{1,2}:\d{2}$/.test(trimmed)) {
    alert('Use HH:MM 24-hour format (e.g. 08:30 or 17:45).');
    return;
  }
  const field = which === 'start' ? 'home_start_time' : 'home_end_time';
  fetch(`/api/trips/${TRIP_ID}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ [field]: trimmed })
  })
  .then(r => r.json())
  .then(data => {
    if (data.error) { alert(data.error); return; }
    _reloadKeepingMapView();
  });
}

function deleteTrip() {
  if (!confirm('Delete this entire trip? This cannot be undone.')) return;
  fetch(`/api/trips/${TRIP_ID}`, { method: 'DELETE' })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      window.location.href = '/trips/calendar';
    });
}

// Detect Stops (admin, desktop) — implementation in
// /static/trip-detail/detect-stops.js.

// ── Track Source modal ─────────────────────────────────────────────────────
//
// Admin-only per-day override for which tid (primary / alt phone) the
// GPS-track endpoint uses. The server's _select_track_per_day picks
// automatically; this UI lets the admin override when auto picks
// wrong. Render: one row per trip day, each with the auto pick, raw
// per-tid ping counts, and a radio for [auto / primary / alt]. Save
// PUTs the diff against the saved overrides, then refetches and
// redraws the polyline.

let TRACK_SOURCE_STATE = null;  // { choices, overrides, counts, alt_configured, pending }

function openTrackSource() {
  const modal = document.getElementById('track-source-modal');
  document.getElementById('track-source-loading').style.display = '';
  document.getElementById('track-source-rows').style.display = 'none';
  document.getElementById('track-source-rows').innerHTML = '';
  document.getElementById('track-source-empty').style.display = 'none';
  document.getElementById('track-source-save').disabled = true;
  modal.classList.add('visible');

  fetch(`/api/trips/${TRIP_ID}/tid-choices`, { credentials: 'same-origin' })
    .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
    .then(data => {
      document.getElementById('track-source-loading').style.display = 'none';
      const dates = Object.keys(data.tid_choices || {}).sort();
      if (!dates.length) {
        const emptyEl = document.getElementById('track-source-empty');
        emptyEl.textContent = 'No GPS data cached for this trip yet — visit the page once with the track loaded, then try again.';
        emptyEl.style.display = '';
        return;
      }
      TRACK_SOURCE_STATE = {
        choices: data.tid_choices,
        overrides: data.tid_overrides || {},
        counts: data.counts || {},
        alt_configured: data.alt_configured !== false,
        pending: {},  // {date: 'auto'|'primary'|'alt'} — only entries that differ from saved
      };
      _renderTrackSourceRows(dates);
    })
    .catch(err => {
      document.getElementById('track-source-loading').style.display = 'none';
      const emptyEl = document.getElementById('track-source-empty');
      emptyEl.textContent = 'Failed to load track source info: ' + err.message;
      emptyEl.style.display = '';
    });
}

function _renderTrackSourceRows(dates) {
  const s = TRACK_SOURCE_STATE;
  const rowsEl = document.getElementById('track-source-rows');
  const altWarn = s.alt_configured ? '' : ' (alt tid not configured)';
  rowsEl.innerHTML = dates.map(d => {
    const auto = s.choices[d] || 'primary';
    const savedOverride = s.overrides[d] || null;     // 'primary'|'alt'|null
    const currentChoice = savedOverride || 'auto';    // initial radio state
    const counts = s.counts[d] || { primary: 0, alt: 0 };
    const altDisabled = !s.alt_configured;
    // Each radio's `name` is unique per row so radios don't bleed across days.
    const nm = `ts-${d}`;
    return `
      <div class="ts-row" data-date="${d}">
        <div class="ts-date">${d}</div>
        <div class="ts-counts">primary: ${counts.primary} ping${counts.primary === 1 ? '' : 's'}, alt: ${counts.alt} ping${counts.alt === 1 ? '' : 's'}${altWarn}</div>
        <div class="ts-radios">
          <label><input type="radio" name="${nm}" value="auto"    ${currentChoice === 'auto'    ? 'checked' : ''} onchange="onTrackSourceChange('${d}', this.value)"><span>Auto (${auto})</span></label>
          <label><input type="radio" name="${nm}" value="primary" ${currentChoice === 'primary' ? 'checked' : ''} onchange="onTrackSourceChange('${d}', this.value)"><span>Force primary</span></label>
          <label><input type="radio" name="${nm}" value="alt"     ${currentChoice === 'alt'     ? 'checked' : ''} ${altDisabled ? 'disabled' : ''} onchange="onTrackSourceChange('${d}', this.value)"><span>Force alt</span></label>
        </div>
      </div>
    `;
  }).join('');
  rowsEl.style.display = '';
}

function onTrackSourceChange(date, value) {
  const s = TRACK_SOURCE_STATE;
  if (!s) return;
  const savedOverride = s.overrides[date] || null;
  const savedAsChoice = savedOverride || 'auto';
  if (value === savedAsChoice) {
    delete s.pending[date];
  } else {
    s.pending[date] = value;
  }
  // Visual flag on changed rows so the admin can see at a glance which
  // they've touched before saving.
  const row = document.querySelector(`.ts-row[data-date="${date}"]`);
  if (row) row.classList.toggle('ts-changed', value !== savedAsChoice);
  document.getElementById('track-source-save').disabled =
    Object.keys(s.pending).length === 0;
}

function saveTrackSource() {
  const s = TRACK_SOURCE_STATE;
  if (!s) return;
  const saveBtn = document.getElementById('track-source-save');
  const cancelBtn = document.getElementById('track-source-cancel');
  saveBtn.disabled = true;
  saveBtn.textContent = 'Saving…';
  cancelBtn.disabled = true;

  const entries = Object.entries(s.pending);
  // Sequential PUTs — the override list is short (one per day) and
  // serializing keeps trips.json writes ordered.
  (async () => {
    for (const [date, value] of entries) {
      const body = { date, value: value === 'auto' ? null : value };
      const r = await fetch(`/api/trips/${TRIP_ID}/tid-overrides`, {
        method: 'PUT',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const t = await r.text().catch(() => '');
        throw new Error(`PUT ${date} failed: HTTP ${r.status} ${t}`);
      }
    }
  })()
    .then(() => {
      closeTrackSource();
      // Refresh polyline so the new tid choices are visible immediately.
      if (window.__refetchAndRenderTrack) window.__refetchAndRenderTrack();
    })
    .catch(err => {
      alert(err.message);
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save';
      cancelBtn.disabled = false;
    });
}

function closeTrackSource() {
  const modal = document.getElementById('track-source-modal');
  modal.classList.remove('visible');
  TRACK_SOURCE_STATE = null;
  const saveBtn = document.getElementById('track-source-save');
  saveBtn.textContent = 'Save';
  saveBtn.disabled = true;
  document.getElementById('track-source-cancel').disabled = false;
}

function closeTrackSourceBackdrop(e) {
  if (e.target === e.currentTarget) closeTrackSource();
}

function editStay(idx) {
  document.getElementById('stay-edit-' + idx).classList.add('active');
  document.getElementById('stay-body-' + idx).style.display = 'none';
}

function cancelStay(idx) {
  document.getElementById('stay-edit-' + idx).classList.remove('active');
  document.getElementById('stay-body-' + idx).style.display = '';
}

function saveStay(idx) {
  const form = document.getElementById('stay-edit-' + idx);
  const fields = {};
  form.querySelectorAll('[data-field]').forEach(el => {
    fields[el.dataset.field] = el.value;
  });
  const payload = stayFieldsToPayload(fields);
  fetch(`/api/trips/${TRIP_ID}/stays/${idx}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(data => {
    if (data.error) { alert(data.error); return; }
    _reloadKeepingMapView();
  });
}

// Transform raw stay form fields into the API payload:
//   - If the hidden campground_id was set by autocomplete selection, use it.
//   - Otherwise, if the typed place text exactly matches a known campground,
//     resolve it to that id. This lets hand-typed existing names still link.
//   - Otherwise, send campground_id=null and put the typed text in custom_place.
function stayFieldsToPayload(fields) {
  const payload = Object.assign({}, fields);
  delete payload.place;
  delete payload.campground_id;
  delete payload.custom_place;
  if ('campsite_location' in payload) {
    payload.campsite_location = (payload.campsite_location || '').trim();
  }

  const place = (fields.place || '').trim();
  let cid = fields.campground_id ? parseInt(fields.campground_id, 10) : null;
  if (!cid && place) {
    const match = CG_LIST.find(c => c.name === place);
    if (match) cid = match.id;
  }
  if (cid) {
    payload.campground_id = cid;
    payload.custom_place = '';
  } else {
    payload.campground_id = null;
    payload.custom_place = place;
  }
  return payload;
}

function deleteStay(idx) {
  // Only mention photo deletion when there are photos to delete — the
  // warning is misleading otherwise.
  const grid = document.getElementById('photos-' + idx);
  const photoCount = grid ? grid.querySelectorAll('.photo-item').length : 0;
  const msg = photoCount
    ? 'Delete this campspot? Photos for this campspot will also be removed.'
    : 'Delete this campspot?';
  if (!confirm(msg)) return;
  fetch(`/api/trips/${TRIP_ID}/stays/${idx}`, { method: 'DELETE' })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      if (data.trip_deleted) {
        window.location.href = '/trips/calendar';
      } else {
        _reloadKeepingMapView();
      }
    });
}

function addStay() { openAddModal('stay'); }

// ── Event editing ─────────────────────────────────────────────────────────
function editEvent(idx) {
  document.getElementById('event-edit-' + idx).classList.add('active');
  document.getElementById('event-body-' + idx).style.display = 'none';
}

// ── Nearby-places dropdown (event/waypoint Name field) ──────────────────
// On focus of the Name input, fetch named OSM POIs within 300 m of the
// event's location via /api/nearby-places (Overpass) and show them as a
// click-to-fill dropdown. The user can still type a name freely.
//
// Cached per input element (WeakMap keyed by the input) so reopening the
// dropdown for an unchanged location doesn't re-hit Overpass. Cache is
// invalidated when the location field changes (either via the text input's
// onchange or programmatically after pick-on-map — see the picker onPick
// callback).
const _nearbyCache = new WeakMap();   // input -> {loc, items} or {loc, loading: true}
const _nearbySeq = new WeakMap();     // input -> monotonically increasing request token

function _nearbyFindLocationInput(nameInput) {
  // The location field lives in the same .form-grid as the name input.
  const grid = nameInput.closest('.form-grid');
  return grid ? grid.querySelector('[data-field="location"]') : null;
}

function _nearbyParseLatLng(locStr) {
  if (!locStr) return null;
  const parts = locStr.split(',').map(s => s.trim());
  if (parts.length !== 2) return null;
  const lat = parseFloat(parts[0]);
  const lng = parseFloat(parts[1]);
  if (!isFinite(lat) || !isFinite(lng)) return null;
  return [lat, lng];
}

function nearbyShow(input) {
  const dropdown = input.parentElement.querySelector('.nearby-dropdown');
  if (!dropdown) return;
  const locInput = _nearbyFindLocationInput(input);
  const locStr = locInput ? locInput.value.trim() : '';
  if (!locStr) {
    dropdown.innerHTML = '<div class="nearby-empty">Set a location to see nearby places.</div>';
    dropdown.classList.add('open');
    return;
  }
  const latlng = _nearbyParseLatLng(locStr);
  if (!latlng) {
    dropdown.innerHTML = '<div class="nearby-empty">Invalid location coordinates.</div>';
    dropdown.classList.add('open');
    return;
  }
  const cached = _nearbyCache.get(input);
  if (cached && cached.loc === locStr && !cached.loading) {
    _nearbyRender(dropdown, cached.items);
    dropdown.classList.add('open');
    return;
  }
  // Fresh fetch
  dropdown.innerHTML = '<div class="nearby-empty">Loading nearby places…</div>';
  dropdown.classList.add('open');
  _nearbyCache.set(input, { loc: locStr, loading: true });
  const seq = (_nearbySeq.get(input) || 0) + 1;
  _nearbySeq.set(input, seq);
  fetch(`/api/nearby-places?lat=${latlng[0]}&lng=${latlng[1]}`)
    .then(r => r.ok ? r.json() : [])
    .then(list => {
      if (_nearbySeq.get(input) !== seq) return;  // superseded by a newer fetch
      _nearbyCache.set(input, { loc: locStr, items: list });
      // Only repaint if the dropdown is still open and on this same input.
      if (dropdown.classList.contains('open')) _nearbyRender(dropdown, list);
    })
    .catch(() => {
      if (_nearbySeq.get(input) !== seq) return;
      _nearbyCache.delete(input);
      if (dropdown.classList.contains('open')) {
        dropdown.innerHTML = '<div class="nearby-empty">Couldn’t load nearby places.</div>';
      }
    });
}

function _nearbyRender(dropdown, items) {
  // Dedupe by lowercase name. Overpass often returns both a node and an
  // enclosing way for the same venue; the user only cares about the name.
  const seen = new Set();
  const unique = [];
  for (const p of (items || [])) {
    const k = (p.name || '').toLowerCase();
    if (!k || seen.has(k)) continue;
    seen.add(k);
    unique.push(p);
  }
  if (unique.length === 0) {
    dropdown.innerHTML = '<div class="nearby-empty">No nearby named places found.</div>';
    return;
  }
  const rows = unique.map(p => {
    const kind = p.kind ? `<span class="nearby-kind">${escapeHtml(p.kind)}</span>` : '';
    // mousedown (not click) so the option fires before the input's blur
    // closes the dropdown.
    return `<div class="nearby-option" onmousedown="nearbySelect(this)" data-name="${escapeHtml(p.name)}">`
         + `<span>${escapeHtml(p.name)}</span>${kind}</div>`;
  }).join('');
  dropdown.innerHTML = '<div class="nearby-header">Nearby (from OpenStreetMap)</div>' + rows;
}

function nearbySelect(optionEl) {
  const wrapper = optionEl.closest('.nearby-autocomplete');
  if (!wrapper) return;
  const input = wrapper.querySelector('input[data-field="name"]');
  if (input) input.value = optionEl.dataset.name;
  const dropdown = wrapper.querySelector('.nearby-dropdown');
  if (dropdown) dropdown.classList.remove('open');
}

// Called from the location input's onchange (typed edit) and from the
// map-picker onPick callback (programmatic update) to discard the cached
// nearby list so the next nearbyShow re-fetches for the new coordinates.
function nearbyInvalidateFromLocation(locationInput) {
  const grid = locationInput.closest('.form-grid');
  if (!grid) return;
  const nameInput = grid.querySelector('[data-field="name"]');
  if (nameInput) _nearbyCache.delete(nameInput);
}

// Close the dropdown on any click EXCEPT (a) the Name input itself
// (its own onclick handler just opened it) or (b) an option inside the
// dropdown (option's mousedown already selected and closed). Clicks
// on empty space INSIDE the dropdown panel still count as "outside"
// and close — the panel visually overlays the fields below, so a
// click in that area is the user trying to dismiss it to reach the
// covered field.
//
// Registered in the CAPTURE phase (third arg true) because the add/edit
// modal's panel does `event.stopPropagation()` on bubble to prevent the
// backdrop close from firing for in-panel clicks. A bubble-phase
// document listener would never see clicks inside the modal panel.
// Capture fires on the way down from document to target, before the
// panel's stopPropagation runs.
document.addEventListener('click', e => {
  if (e.target.closest('.nearby-option')) return;
  if (e.target.tagName === 'INPUT'
      && e.target.parentElement
      && e.target.parentElement.classList.contains('nearby-autocomplete')) {
    return;
  }
  document.querySelectorAll('.nearby-dropdown.open').forEach(d => d.classList.remove('open'));
}, true);

function cancelEvent(idx) {
  document.getElementById('event-edit-' + idx).classList.remove('active');
  document.getElementById('event-body-' + idx).style.display = '';
}

function saveEvent(idx) {
  const form = document.getElementById('event-edit-' + idx);
  const fields = {};
  form.querySelectorAll('[data-field]').forEach(el => {
    fields[el.dataset.field] = el.type === 'checkbox' ? el.checked : el.value;
  });
  if ('family_id' in fields) {
    fields.family_id = fields.family_id ? parseInt(fields.family_id, 10) : null;
    // A family-visit event saved with a blank name falls back to the family label
    // so the event card always has a title to display.
    if (fields.family_id != null && !(fields.name || '').trim()) {
      const fam = FAMILY_LOCATIONS.find(f => f.id === fields.family_id);
      if (fam) fields.name = fam.label;
    }
  }
  // Admin save = the act of vetting. Clear the flag every time so
  // detected-stop entries lose their "Needs review" treatment after
  // the admin opens & saves the edit form.
  fields.needs_vetting = false;
  fetch(`/api/trips/${TRIP_ID}/events/${idx}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields)
  })
  .then(r => r.json())
  .then(data => {
    if (data.error) { alert(data.error); return; }
    _reloadKeepingMapView();
  });
}

function deleteEvent(idx) {
  // Only mention photo deletion when there are photos to delete — the
  // warning is misleading otherwise.
  const grid = document.getElementById('event-photos-' + idx);
  const photoCount = grid ? grid.querySelectorAll('.photo-item').length : 0;
  const msg = photoCount
    ? 'Delete this event? Photos for this event will also be removed.'
    : 'Delete this event?';
  if (!confirm(msg)) return;
  fetch(`/api/trips/${TRIP_ID}/events/${idx}`, { method: 'DELETE' })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      _reloadKeepingMapView();
    });
}

function addEvent() { openAddModal('event'); }
function addWaypoint() { openAddModal('waypoint'); }

function familyVisitCoordsById(id) {
  const fam = FAMILY_LOCATIONS.find(f => f.id === id);
  if (!fam) return '';
  const lat = fam.driveway_lat || fam.lat;
  const lng = fam.driveway_lng || fam.lng;
  return lat + ',' + lng;
}

function addFamilyVisit() { openAddModal('family_visit'); }

// ── Add/Edit modal ────────────────────────────────────────────────────────
let addModalKind = null;
let addModalMode = 'add';        // 'add' | 'edit'
let addModalEditIdx = null;

function defaultAddDate() {
  return FIRST_STAY_DATE || _todayLocalISO();
}

// Today / now in *local* components (not UTC). `new Date().toISOString()`
// would shift around midnight in negative-UTC time zones — bad for
// "current date" prefills meant to reflect what's on the user's clock.
function _todayLocalISO() {
  const d = new Date();
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0');
}

function _nowLocalHM() {
  const d = new Date();
  return String(d.getHours()).padStart(2, '0') + ':' +
    String(d.getMinutes()).padStart(2, '0');
}

// Mirrors the 700px mobile breakpoint used throughout the project CSS.
function _isMobileViewport() {
  return window.matchMedia('(max-width: 700px)').matches;
}

// Reverse-geocode a lat/lng and fill the currently-open Add modal's name /
// locale / state fields, only touching fields the user hasn't started
// editing. Shared by `createFromSelection` (post-ping-lasso) and the mobile
// "Add Event/Waypoint" geolocation path. The modal may have been closed
// before the fetch resolves — checks for the body/field presence each time.
function _fillModalFromReverseGeocode(lat, lng) {
  return fetch('/api/reverse-geocode?lat=' + lat + '&lng=' + lng,
               { credentials: 'same-origin' })
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (!data) return;
      const body = document.getElementById('add-modal-body');
      if (!body) return;
      const nameI = body.querySelector('[data-field="name"]');
      const locI = body.querySelector('[data-field="locale"]');
      const stI = body.querySelector('[data-field="state"]');
      if (nameI && data.name) {
        const cur = (nameI.value || '').trim();
        if (!cur || cur === 'New Waypoint') nameI.value = data.name;
      }
      if (locI && data.locale && !locI.value) locI.value = data.locale;
      if (stI && data.state && !stI.value) stI.value = data.state;
    })
    .catch(() => { /* keep what we have if the lookup fails */ });
}

function addDays(isoDate, days) {
  const d = new Date(isoDate + 'T00:00:00');
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

// Build the form HTML for a given kind, pre-filling values from `v` (or empty)
function _modalFormHtml(kind, v) {
  v = v || {};
  if (kind === 'stay') {
    const start = v.start || defaultAddDate();
    const end = v.end || addDays(start, 1);
    const cgId = v.campground_id != null ? v.campground_id : '';
    return `
      <div class="form-grid">
        <div class="full-width">
          <label>Place</label>
          <div class="cg-autocomplete">
            <input type="text" data-field="place" value="${escapeHtml(v.place || '')}" autocomplete="off" oninput="cgFilter(this); cgClearId(this)" onfocus="cgFilter(this)">
            <input type="hidden" data-field="campground_id" value="${cgId}">
            <div class="cg-dropdown"></div>
          </div>
        </div>
        <div><label>Locale</label><input type="text" data-field="locale" value="${escapeHtml(v.locale || '')}" autocomplete="off"></div>
        <div><label>State</label><input type="text" data-field="state" value="${escapeHtml(v.state || '')}" autocomplete="off"></div>
        <div><label>Campsite</label><input type="text" data-field="site" value="${escapeHtml(v.site || '')}" autocomplete="off"></div>
        <div><label>Campers</label><input type="text" data-field="campers" value="${escapeHtml(v.campers || '')}" autocomplete="off"></div>
        <div class="full-width">
          <label>Campsite Location <span style="color:var(--gray);font-weight:normal;font-size:.75rem">(blank = use campground location)</span></label>
          <div class="event-location-field">
            <input type="text" data-field="campsite_location" value="${escapeHtml(v.campsite_location || '')}" placeholder="lat,lng" autocomplete="off">
            <button type="button" class="btn-pick-location" onclick="showAddModalStayLocationMap()">Pick on Map</button>
          </div>
        </div>
        <div><label>Start Date</label><input type="date" data-field="start" value="${start}" autocomplete="off" onchange="syncStayNights(this)"></div>
        <div><label>End Date</label><input type="date" data-field="end" value="${end}" autocomplete="off" onchange="syncStayNights(this)"></div>
        <div><label>Nights</label><input type="number" data-field="nights" value="${v.nights || 1}" min="1" autocomplete="off"></div>
        <div class="full-width"><label>Notes</label><textarea data-field="notes" rows="2" autocomplete="off">${escapeHtml(v.notes || '')}</textarea></div>
      </div>`;
  } else if (kind === 'event' || kind === 'waypoint') {
    const date = v.date || defaultAddDate();
    const nameVal = v.name != null ? v.name : (kind === 'waypoint' ? 'New Waypoint' : '');
    const isWp = v.waypoint != null ? !!v.waypoint : (kind === 'waypoint');
    return `
      <div class="form-grid">
        <div class="full-width">
          <label>Name</label>
          <div class="nearby-autocomplete">
            <input type="text" data-field="name" autocomplete="off" value="${escapeHtml(nameVal)}" onclick="nearbyShow(this)">
            <div class="nearby-dropdown"></div>
          </div>
        </div>
        <div><label>Date</label><input type="date" data-field="date" value="${date}" autocomplete="off"></div>
        <div>
          <label>Time</label>
          <div style="display:flex;gap:.5rem;align-items:center;">
            <input type="time" data-field="time" value="${escapeHtml(v.time || '')}" autocomplete="off">
            <span>&ndash;</span>
            <input type="time" data-field="end_time" value="${escapeHtml(v.end_time || '')}" autocomplete="off">
          </div>
        </div>
        <div><label>Locale</label><input type="text" data-field="locale" value="${escapeHtml(v.locale || '')}" autocomplete="off"></div>
        <div><label>State</label><input type="text" data-field="state" value="${escapeHtml(v.state || '')}" autocomplete="off"></div>
        <div class="full-width">
          <label>Location</label>
          <div class="event-location-field">
            <input type="text" data-field="location" value="${escapeHtml(v.location || '')}" placeholder="lat,lng" autocomplete="off"
                   onchange="nearbyInvalidateFromLocation(this)">
            <button type="button" class="btn-pick-location" onclick="showAddModalLocationMap()">Pick on Map</button>
          </div>
        </div>
        <div class="full-width"><label>Description</label><textarea data-field="description" rows="2" autocomplete="off">${escapeHtml(v.description || '')}</textarea></div>
        <div class="full-width" style="display:flex;align-items:center;justify-content:flex-start;gap:.4rem;">
          <input type="checkbox" data-field="waypoint" id="modal-waypoint-cb"${isWp ? ' checked' : ''}>
          <label for="modal-waypoint-cb" style="display:inline;margin:0;font-weight:500;">Waypoint</label>
        </div>
      </div>`;
  } else if (kind === 'family_visit') {
    const date = v.date || defaultAddDate();
    const opts = FAMILY_LOCATIONS.map(f =>
      `<option value="${f.id}"${f.id === v.family_id ? ' selected' : ''}>${escapeHtml(f.label)}</option>`
    ).join('');
    // For an existing family visit, the auto-filled name equals the family label.
    // Show it as blank in that case so the placeholder hint reads naturally.
    const fam = v.family_id != null ? FAMILY_LOCATIONS.find(f => f.id === v.family_id) : null;
    const nameVal = (v.name && fam && v.name === fam.label) ? '' : (v.name || '');
    return `
      <div class="form-grid">
        <div class="full-width">
          <label>Family Location</label>
          <select data-field="family_id">${opts}</select>
        </div>
        <div class="full-width">
          <label>Event Name <span style="color:var(--gray);font-weight:normal;font-size:.75rem">(blank to use family location name)</span></label>
          <input type="text" data-field="name" value="${escapeHtml(nameVal)}" autocomplete="off">
        </div>
        <div><label>Date</label><input type="date" data-field="date" value="${date}" autocomplete="off"></div>
        <div>
          <label>Time</label>
          <div style="display:flex;gap:.5rem;align-items:center;">
            <input type="time" data-field="time" value="${escapeHtml(v.time || '')}" autocomplete="off">
            <span>&ndash;</span>
            <input type="time" data-field="end_time" value="${escapeHtml(v.end_time || '')}" autocomplete="off">
          </div>
        </div>
      </div>`;
  }
  return '';
}

const MODAL_TITLES = {
  stay:         { add: 'Add Campspot',     edit: 'Edit Campspot' },
  event:        { add: 'Add Event',        edit: 'Edit Event' },
  waypoint:     { add: 'Add Waypoint',     edit: 'Edit Waypoint' },
  family_visit: { add: 'Add Family Visit', edit: 'Edit Family Visit' },
};

function _openModal(kind, mode, idx, prefillValues) {
  const modal = document.getElementById('add-modal');
  if (!modal) return;
  if (kind === 'family_visit' && FAMILY_LOCATIONS.length === 0) {
    alert('No family locations configured.');
    return;
  }

  let values = {};
  if (mode === 'edit') {
    values = (kind === 'stay' ? STAYS_ALL[idx] : EVENTS_ALL[idx]) || {};
  } else if (prefillValues) {
    values = prefillValues;
  }

  addModalKind = kind;
  addModalMode = mode;
  addModalEditIdx = idx;

  document.getElementById('add-modal-title').textContent = MODAL_TITLES[kind][mode];
  document.getElementById('add-modal-body').innerHTML = _modalFormHtml(kind, values);
  document.getElementById('modal-submit-btn').textContent = mode === 'edit' ? 'Save' : 'Add';
  document.getElementById('modal-delete-btn').style.display = mode === 'edit' ? '' : 'none';

  modal.classList.add('visible');
  setTimeout(() => {
    const first = document.querySelector('#add-modal-body input, #add-modal-body select, #add-modal-body textarea');
    if (first) first.focus();
  }, 50);
}

function openAddModal(kind) {
  // On mobile, an Add Event / Add Waypoint is almost always "log what I'm
  // doing right now, right here" — so prefill the date+time from the user's
  // clock and (async) the location + locale + state from Geolocation +
  // reverse-geocode, mirroring `createFromSelection`'s ping-lasso flow.
  // Stay and family-visit adds are typically planned in advance and skip
  // this. Desktop also skips: the user has a keyboard and a map picker
  // right there, and "the current GPS fix" is rarely what they want.
  if (_isMobileViewport() && (kind === 'event' || kind === 'waypoint') &&
      navigator.geolocation) {
    const isWp = (kind === 'waypoint');
    const values = {
      name: isWp ? 'New Waypoint' : '',
      date: _todayLocalISO(),
      time: _nowLocalHM(),
      waypoint: isWp,
    };
    _openModal(kind, 'add', null, values);
    // Geolocation may take a couple seconds (or fail entirely if the user
    // denies the prompt). Fire it after the modal is already on screen so
    // the user isn't staring at a blank tap. Fills only empty fields, so a
    // user who starts typing before the fix lands won't be overwritten.
    navigator.geolocation.getCurrentPosition(pos => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      const body = document.getElementById('add-modal-body');
      if (!body) return;  // modal already closed
      const locInput = body.querySelector('[data-field="location"]');
      if (locInput && !locInput.value) {
        locInput.value = lat.toFixed(6) + ',' + lng.toFixed(6);
      }
      _fillModalFromReverseGeocode(lat, lng);
    }, err => {
      // Permission denied / unavailable / timed out — leave the prefilled
      // date+time in place and let the user fill the rest by hand.
      console.log('Geolocation unavailable for new ' + kind + ':', err.message);
    }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 });
    return;
  }
  _openModal(kind, 'add', null);
}
function openEditModal(kind, idx) {
  if (!IS_ADMIN) return;
  _openModal(kind, 'edit', idx);
}

function syncStayNights(dateInput) {
  const grid = dateInput.closest('.form-grid');
  if (!grid) return;
  const start = grid.querySelector('[data-field="start"]').value;
  const end = grid.querySelector('[data-field="end"]').value;
  const nightsInput = grid.querySelector('[data-field="nights"]');
  if (!start || !end || !nightsInput) return;
  const ms = new Date(end + 'T00:00:00') - new Date(start + 'T00:00:00');
  const nights = Math.max(1, Math.round(ms / 86400000));
  nightsInput.value = nights;
}

function closeAddModal() {
  const modal = document.getElementById('add-modal');
  if (!modal) return;
  modal.classList.remove('visible');
  document.getElementById('add-modal-body').innerHTML = '';
  addModalKind = null;
  addModalMode = 'add';
  addModalEditIdx = null;
  // Drop the "from selection" marker so a later, unrelated modal doesn't
  // accidentally trigger Select-pings to turn off on submit.
  window.__createFromSelection = false;
}

function closeAddModalBackdrop(e) {
  if (e.target.id === 'add-modal') closeAddModal();
}

function submitAddModal() {
  const body = document.getElementById('add-modal-body');
  const fields = {};
  body.querySelectorAll('[data-field]').forEach(el => {
    fields[el.dataset.field] = el.type === 'checkbox' ? el.checked : el.value;
  });

  const isEdit = addModalMode === 'edit';
  const idx = addModalEditIdx;
  let url, payload;
  if (addModalKind === 'stay') {
    url = isEdit ? `/api/trips/${TRIP_ID}/stays/${idx}` : `/api/trips/${TRIP_ID}/stays`;
    payload = stayFieldsToPayload(fields);
  } else if (addModalKind === 'event' || addModalKind === 'waypoint') {
    url = isEdit ? `/api/trips/${TRIP_ID}/events/${idx}` : `/api/trips/${TRIP_ID}/events`;
    payload = fields;
    if (payload.waypoint && !(payload.name || '').trim()) payload.name = 'New Waypoint';
  } else if (addModalKind === 'family_visit') {
    url = isEdit ? `/api/trips/${TRIP_ID}/events/${idx}` : `/api/trips/${TRIP_ID}/events`;
    const fid = fields.family_id ? parseInt(fields.family_id, 10) : null;
    const fam = FAMILY_LOCATIONS.find(f => f.id === fid);
    const typedName = (fields.name || '').trim();
    payload = {
      family_id: fid,
      name: typedName || (fam ? fam.label : ''),
      location: fam ? familyVisitCoordsById(fid) : '',
      date: fields.date,
      time: fields.time,
      end_time: fields.end_time,
    };
  } else {
    return;
  }
  // Admin save on an event/waypoint/family-visit clears any
  // pending needs_vetting flag — same intent as saveEvent() above.
  // For new events POST'd from the modal this is also fine (the
  // server defaults to False anyway, but being explicit costs nothing).
  if (addModalKind === 'event' || addModalKind === 'waypoint' || addModalKind === 'family_visit') {
    payload.needs_vetting = false;
  }

  fetch(url, {
    method: isEdit ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      // If this modal was opened from "+ Event/Waypoint from selection",
      // turn off Select pings so the reloaded page comes up clean.
      if (window.__createFromSelection) {
        window.__createFromSelection = false;
        _disableSelectionToggleBeforeReload();
      }
      _reloadKeepingMapView();
    });
}

function deleteFromModal() {
  if (addModalMode !== 'edit') return;
  if (addModalKind === 'stay') deleteStay(addModalEditIdx);
  else deleteEvent(addModalEditIdx);
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && addModalKind) closeAddModal();
});

function onFamilyVisitChange(select, idx) {
  const form = document.getElementById('event-edit-' + idx);
  const locInput = form.querySelector('[data-field="location"]');
  const nameInput = form.querySelector('[data-field="name"]');
  const fid = parseInt(select.value, 10);
  const fam = FAMILY_LOCATIONS.find(f => f.id === fid);
  if (locInput) locInput.value = familyVisitCoordsById(fid);
  // Only overwrite name if it looks auto-filled — i.e. it's blank or matches
  // any family label (including the previously selected one). A custom name
  // the user has typed is left alone.
  if (nameInput && fam) {
    const current = (nameInput.value || '').trim();
    const isAutoFilled = !current || FAMILY_LOCATIONS.some(f => f.label === current);
    if (isAutoFilled) nameInput.value = fam.label;
  }
}

// ── Location map picker (shared by events and stays) ─────────────────────
// pickerTarget identifies which input the next onPick should fill:
//   { kind: 'event',       idx: <eventIdx> }   → inline event edit form
//   { kind: 'event-modal' }                    → add/edit modal event form
//   { kind: 'stay',        idx: <stayIdx>  }   → inline stay edit form (campsite_location)
//   { kind: 'stay-modal'   }                   → add/edit modal stay form (campsite_location)
let pickerTarget = null;
let eventLocationPicker = null;

if (IS_ADMIN) {
  eventLocationPicker = createMapPicker({
    containerId: 'event-location-map-container',
    mapId: 'event-location-map',
    headerId: 'event-location-map-header',
    searchId: 'event-geo-search-input',
    resultsId: 'event-geo-search-results',
    onPick: function(lat, lng) {
      const value = lat.toFixed(6) + ',' + lng.toFixed(6);
      const locInput = pickerTargetInput();
      if (locInput) {
        locInput.value = value;
        // Programmatic value assignment doesn't fire input events, so
        // invalidate the nearby-places cache directly. No-op for
        // stay-* targets (no Name field with a dropdown nearby).
        if (pickerTarget && (pickerTarget.kind === 'event' || pickerTarget.kind === 'event-modal')) {
          nearbyInvalidateFromLocation(locInput);
        }
      }
    }
  });
}

function pickerTargetInput() {
  if (!pickerTarget) return null;
  switch (pickerTarget.kind) {
    case 'event': {
      const form = document.getElementById('event-edit-' + pickerTarget.idx);
      return form ? form.querySelector('[data-field="location"]') : null;
    }
    case 'event-modal':
      return document.querySelector('#add-modal-body [data-field="location"]');
    case 'stay': {
      const form = document.getElementById('stay-edit-' + pickerTarget.idx);
      return form ? form.querySelector('[data-field="campsite_location"]') : null;
    }
    case 'stay-modal':
      return document.querySelector('#add-modal-body [data-field="campsite_location"]');
  }
  return null;
}

function _showPicker(target, fallbackLoc) {
  pickerTarget = target;
  const input = pickerTargetInput();
  const existing = (input && input.value.trim()) || '';
  // If the user has already chosen a location, zoom in close so they can fine-
  // tune it. The fallback (campground center) gets the looser default zoom.
  if (existing) {
    eventLocationPicker.show(existing, 17);
  } else {
    eventLocationPicker.show(fallbackLoc || '');
  }
}

function showEventLocationMap(eventIdx) {
  _showPicker({ kind: 'event', idx: eventIdx });
}

function showAddModalLocationMap() {
  _showPicker({ kind: 'event-modal' });
}

function showStayLocationMap(stayIdx) {
  // Fall back to the campground's coords so the picker opens zoomed near the
  // stay rather than at the default view.
  const stay = STAYS_ALL[stayIdx];
  let fallback = '';
  if (stay && stay.lat != null && stay.lng != null) {
    fallback = stay.lat + ',' + stay.lng;
  }
  _showPicker({ kind: 'stay', idx: stayIdx }, fallback);
}

function showAddModalStayLocationMap() {
  // When adding/editing via modal, try to seed from the picked campground
  // (resolved through CG_LIST) so the picker opens near the campground.
  let fallback = '';
  const cgIdInput = document.querySelector('#add-modal-body [data-field="campground_id"]');
  const cid = cgIdInput && cgIdInput.value ? parseInt(cgIdInput.value, 10) : null;
  if (cid && typeof CG_LIST !== 'undefined') {
    const cg = CG_LIST.find(c => c.id === cid);
    if (cg && cg.location) fallback = cg.location;
  }
  _showPicker({ kind: 'stay-modal' }, fallback);
}

function hideEventLocationMap() {
  eventLocationPicker.hide();
}
