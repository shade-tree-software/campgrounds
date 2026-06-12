# Desktop UX improvements — agreed plan (2026-06-12)

Reviewed with Claude after the mobile UX pass (commits `20931b8`..`f835083`).
Working agreement from that session: implement one item at a time, verify
(template compile + `node --check`), and commit each item separately to
`master`; Andrew pushes manually.

Suggested order = most user-visible improvement per line of code.

## 1. Trips-map slideshow: hover-pause  (HIGH — real interaction bug)

Slots rotate every 2.5 s with no hover awareness — the photo under the
cursor can swap mid-click, sending the user to a different trip.

- File: `templates/trips_map.html`, the slideshow IIFE near the bottom.
- Fix: a `paused` flag set on `mouseenter` / cleared on `mouseleave` of
  both `.photo-stack` elements; the existing `setInterval` callback
  returns early when paused (same pattern as the `document.hidden` check
  already there).

## 2. Lightbox: desktop zoom parity + adjacent preloading  (HIGH)

Mobile has pinch/double-tap zoom (added this session); desktop has no
zoom at all.

- File: `static/trip-detail/lightbox.js`.
- The transform machinery already exists and is reusable as-is:
  `lbScale`/`lbTx`/`lbTy`, `lbApplyTransform()`, `lbClampPan()`,
  `lbResetZoom()`, `lbToggleZoom(x, y)` (anchored zoom math documented
  inline).
- Add: `wheel` listener on `#lightbox` — zoom anchored at cursor
  (reuse the pinch midpoint-anchor formula: t' = q − C − (q − C − t)·(s'/s)),
  clamp 1x–4x (`MAX_SCALE` exists), `preventDefault` so the page doesn't
  scroll. `dblclick` → `lbToggleZoom(e.clientX, e.clientY)`. Mouse
  drag-to-pan while `lbScale > 1` (mousedown/mousemove/mouseup mirror of
  the touch pan; suppress the click-to-close that follows a drag —
  note `closeLightbox` already ignores clicks on `#lightbox-img`).
- Preloading: in `showLightboxPhoto()`, after setting src, create
  `new Image().src = <data-full of lightboxPhotos[index±1]>` for both
  neighbors so arrow-paging doesn't refetch multi-MB originals on demand.
  (Grids hold thumbs; full-res URL is in `img.dataset.full`.)

## 3. Keyboard navigation  (HIGH, cheap)

Only existing keydown handlers: lightbox (arrows/Esc/F), Escape-closes
for menus/modals, autocomplete arrows. Add, all gated to skip when
`document.activeElement` is an input/textarea/select or contentEditable:

- Trip detail (`static/trip-detail/timeline.js` or a small new block):
  ←/→ navigates to prev/next trip **only when the lightbox is not
  visible** (check `#lightbox.visible`) and no modal is open. The hrefs
  exist in `.trip-nav a` elements (prev = first, next = last); guard for
  their absence on first/last trip.
- Calendar (`templates/trips_calendar.html`): ←/→ page the year
  (`prevYear()`/`nextYear()`; in single-month mobile mode those are
  month functions — desktop-only page width, but simplest is calling
  prevYear/nextYear regardless since the mobile single-month view is
  touch). `/` focuses `#trip-search` (preventDefault so the slash isn't
  typed).

## 4. Campground map: name search  (MEDIUM)

~1,100 markers; no way to find a specific campground except panning or
the Manage page.

- File: `templates/campground_map.html`. Markers are built client-side
  from the full campground list already in the page.
- Add a search input in `.map-header` (next to the color-by select):
  filter-as-you-type dropdown over names (reuse the `.cg-dropdown`
  look from trip detail / the geo-search pattern in
  `static/map-picker.js`); selecting a result pans/zooms to the marker
  (zoom ~12) and opens its popup. Esc clears.

## 5. Hover prefetch for nav  (MEDIUM, optional)

Server render is now ~5 ms warm (caching commit `f835083`), so
perceived nav speed is network-bound. On `mouseenter` of nav/tab/list
links (after ~65 ms hover delay), inject `<link rel="prefetch">` for
the href, once per URL. Small inline script in `base.html`. Skip for
admins' mutation links (all nav links are GET pages — fine).

## 6. Prev/next trip hover tooltips  (MEDIUM-LOW)

Header chevrons just say "Previous trip". Pass `prev_trip_summary` /
`next_trip_summary` from the route (it already computes
`prev_trip_id`/`next_trip_id` — same place in `ekko_trips_app.py`,
trip_detail route) and put them in the anchors' `title` attrs.

## 7. Small polish (batch or skip)

- Calendar days with two overlapping trips: only the "primary" trip is
  clickable; the other is unreachable from the calendar. Tooltip could
  list both; click could offer a choice when >1.
- `alert()`/`confirm()` admin flows → small toast helper (also flagged
  in the mobile review).
- Calendar "today" gold ring is subtle at 3-column density — consider a
  filled accent.

## Backlog from the earlier mobile review (not yet done, lower priority)

- Read-only campground map for non-admins ("places we could go") — nav
  gating change, product call.
- Calendar touch: first-tap preview / second-tap navigate (deliberately
  skipped — single-tap-to-open judged better; revisit only if asked).
- A11y: calendar `<td onclick>` / photo `<img onclick>` not
  keyboard-reachable; dialogs lack `role="dialog"`/focus trap.
- Contrast: caption placeholder `--gray-light` on white; nav links
  `rgba(255,255,255,.75)`.
