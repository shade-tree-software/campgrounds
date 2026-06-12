# Desktop UX improvements — status

The 2026-06-12 plan is implemented. Each item landed as its own commit:

1. Slideshow hover-pause — `b3d6fd7`
2. Lightbox desktop zoom (wheel/double-click/drag-pan) + neighbor
   preloading — `5f50d4b`
3. Keyboard nav: ←/→ trips on trip detail, ←/→ years + `/` search on
   calendar — `ac7d292`
4. Campground-map name search (also gets `/` focus) — `4884bc8`
5. Hover prefetch for nav links — `c1b4a16`
6. Prev/next chevron tooltips with destination trip names — `5867092`
7. Calendar polish: today marker on non-trip days (was invisible),
   overlap tooltips + multi-trip day chooser — `1fea2d6`

## Remaining backlog (untouched, in case it's wanted later)

- **Toast helper replacing `alert()`/`confirm()`** — deliberately
  skipped: ~60 call sites across 7 files, and most `confirm()`s guard
  destructive deletes where a blocking prompt is defensible. A real
  refactor, not polish; do it as its own task if the jarring dialogs
  start to grate.
- **Read-only campground map for non-admins** ("places we could go") —
  nav/permission gating change; product call.
- **A11y:** calendar `<td onclick>` / photo `<img onclick>` aren't
  keyboard-reachable; lightbox/modals lack `role="dialog"`/focus trap.
- **Contrast:** caption placeholder `--gray-light` on white; nav links
  `rgba(255,255,255,.75)` on navy-light.
- **Calendar touch tap-preview** (first tap = tooltip, second = open) —
  deliberately rejected earlier; revisit only if asked. Note the new
  multi-trip day chooser already covers overlap days on touch.
