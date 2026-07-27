---
name: project-poster-redesign
description: "Trip poster — selectable size + full design pass SHIPPED & visually verified 2026-07-27; only optional polish left"
metadata: 
  node_type: memory
  type: project
  originSessionId: d819e4d9-e823-4ed8-86c8-76237003c80c
  modified: 2026-07-27T23:25:03.170Z
---

AWH wants `/trips/poster` printed on large poster paper for a wall.

**Done 2026-07-27 (size selection):** `?size=` + toolbar dropdown (letter / 11×17 / 18×24 / 24×36), reload-on-change, `SCALE = sheetWidth/816` carries every letter-tuned constant, `/view/` derivatives when SCALE > 1, JS-injected `@page`.

**Done 2026-07-27 (design pass — the whole backlog shipped in one session):**
1. Muted map: per-tile CSS filter (grayscale .65 + sepia .14 + saturate 1.15). **Print gotcha (the real root cause): Leaflet's translate3d compositing makes Chromium's print rasterizer DROP the base map on large sheets** — fixed with `window.L_DISABLE_3D = true` before leaflet.js. That forces integer zoom, so tight fractional framing is rebuilt by the `MAP_M` trick: enlarge the map div by 2^(ceil(zf)−zf), let integer fitBounds land on ceil(zf), scale back down with a plain 2d transform (print-safe, verified); in-map ink sized by `MK = SCALE×MAP_M`, callout SVG on the unscaled wrap divides points by MAP_M.
2. Driven routes from `/api/trips/routes` — canvas renderer, own pane z 350, navy weight 1.1×SCALE opacity .38.
3. Photo treatment: white mattes (background+padding so they print) + soft shadow; two 2×2 hero cells in the bottom strip (grid-area, auto-flow fills around them).
4. Playfair Display masthead + stats footer (self-hosted variable woff2, `static/vendor/fonts/`, latin subset ~60 KB); double-rule navy frame; paper margin via `--sx` (= SCALE px) var; `poster_stats` computed server-side (excludes home_only, `camping_nights()`).
5. Callouts: boxless italic-Georgia labels with paper halo (`paint-order: stroke`); leaders hairline at opacity .26 — at full ink ~60 leaders converging on the home cluster read as spaghetti.

**Visual verification method (worked well, reusable):** no venv needed — `~/.virtualenvs/ekko` has Flask; auth stayed untouched (classifier blocks share-token creation and login-gate removal — don't retry those). Instead: offline-render the template via the app's own helpers into `~/poster-preview-tmp/` (symlink static + photo_uploads, rewrite URLs relative, inline the routes JSON), then Playwright chromium (installed in the ekko venv) screenshots + `page.pdf(prefer_css_page_size=True)` per size. All four sizes + print PDFs eyeballed. 24×36 PDF takes ~5 min to generate.

Remaining (optional, unranked): curate hero-cell photo choice (currently just pool order), consider trimming base-map label density at large sizes. Print-shop workflow: open at target size, Print → Save as PDF → hand off.
