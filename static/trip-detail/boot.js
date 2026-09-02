// Boot module: lift everything from `window.TRIP_BOOT` (a small inline
// Jinja-rendered <script> sets it just before this file loads) into
// script-scoped `const`s with the same names the rest of the JS
// already uses. Keeps the module-level extraction minimally invasive —
// no module file needs `window.TRIP_BOOT.x` everywhere; they just use
// TRIP_ID / IS_ADMIN / STAYS_ALL / etc. as before.

const _BOOT = window.TRIP_BOOT || {};
const TRIP_ID = _BOOT.trip_id;
const IS_ADMIN = !!_BOOT.is_admin;
// Uploader-role users may POST photos and edit captions on their own uploads;
// they cannot delete, reorder, move, or otherwise edit the trip. Admins also
// satisfy the upload checks but use the full IS_ADMIN paths everywhere else.
const IS_UPLOADER = !!_BOOT.is_uploader;
const CURRENT_USERNAME = _BOOT.current_username || '';
const FIRST_STAY_DATE = _BOOT.first_stay_date || '';
const STAYS_ALL = _BOOT.stays_all || [];
const EVENTS_ALL = _BOOT.events_all || [];
// True when this trip's events span more than one timezone abbreviation, so
// the map's popups label their times the way the timeline cards do. Decided
// server-side (`_make_trip`) so the two surfaces can't disagree.
const MULTI_TZ = !!_BOOT.multi_timezone;
const FAMILY_LOCATIONS = _BOOT.family_locations || [];
const TRIP_START = _BOOT.trip_start || '';
const TRIP_END = _BOOT.trip_end || '';
const HOME_START_TIME = _BOOT.home_start_time || '';
const HOME_END_TIME = _BOOT.home_end_time || '';
// `[lat, lng]` of EKKO's home base, used as the trip-map's start/end anchor
// and as the route fallback when GPS coverage is missing.
const HOME_COORDS = _BOOT.home_coords || null;

// Base style for the per-ping GPS circle markers. Lives in boot, not in
// overrides.js, because map.js draws those markers for EVERY viewer while
// overrides.js only loads for admins — defining it there left viewers with a
// ReferenceError that killed the whole GPS track. overrides.js layers its
// selected/suppressed/relocated variants on top.
const DEFAULT_PING_STYLE = { radius: 5, color: '#002868', weight: 1, fillColor: '#ffffff', fillOpacity: 1 };

// HTML-escape via a detached <div> — the browser does the work and we
// read it back. Lives in boot so every later module (lightbox, detect-
// stops, photos, …) sees it at parse time without an ordering dance.
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Reveal the rest of a phone-collapsed photo grid (see .photo-grid.collapsible).
// Lives in boot rather than photos.js because that module only loads for admins
// and uploaders, and this button is for every viewer.
function expandPhotoGrid(btn) {
  const grid = btn.previousElementSibling;
  if (grid) grid.classList.add('expanded');
  btn.remove();   // one-way: nothing left for it to do
}
