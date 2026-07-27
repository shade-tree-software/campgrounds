---
name: project-poster-redesign
description: "Trip poster spiffing-up — selectable size SHIPPED 2026-07-27; design-pass backlog (map style, routes, photos, type) still open"
metadata: 
  node_type: memory
  type: project
  originSessionId: d819e4d9-e823-4ed8-86c8-76237003c80c
  modified: 2026-07-27T22:03:22.839Z
---

AWH wants `/trips/poster` to look less amateurish, printed on large poster paper for a wall.

**Done (2026-07-27, template-only + docs):** selectable sheet size via `?size=` + toolbar dropdown (letter default, 11×17, 18×24, 24×36). Size change RELOADS (all geometry is load-time). Key mechanics: sheet sized in CSS inches via `--sheet-w/-h`; one `SCALE = sheetWidth/816` multiplies every letter-tuned pixel constant (callout pills/font/strokes via `--callout-*` vars, marker sizes, fitBounds padding); strip row percentages recomputed per aspect to hold ~1.07 cell aspect; `/view/` derivatives replace `/thumb/` when SCALE > 1; `@page` size injected by JS (can't read CSS vars). Larger sheet ⇒ Leaflet fetches higher-zoom tiles ⇒ sharper print for free.

**NOT yet visually verified** — this machine has no `ekko_trips_venv/` (no Flask), so the four sizes + a 24×36 print preview still need an eyeball check on a machine that can run the app.

**Open design backlog** (assessment AWH heard, in impact order — implement on ask):
1. Muted poster-palette map cartography (loudest "amateur" signal is default OSM street tiles; protomaps-leaflet + omt-style already vendored for local mode).
2. Draw driven trip routes from `GET /api/trips/routes` (~200 KB, precomputed) — thin navy lines radiating from home.
3. Photo treatment: white "print borders" per cell / 2×2 hero cells / curate count down.
4. Display typeface (self-hosted woff2, no build step) + double-rule sheet frame + stats footer ("N trips · N nights · N states · years").
5. Softer callouts: small-caps labels or numbered dots + legend column instead of white pills.

Print-shop workflow: open at target size, print → Save as PDF → hand off.
