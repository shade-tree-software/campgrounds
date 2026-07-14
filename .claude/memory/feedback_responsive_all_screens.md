---
name: feedback_responsive_all_screens
description: "Every UI page must render well on all screen sizes (desktop, iPad/tablet, phone) — a primary design rule for all new UI and all edits to existing pages."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f190f1c-07bb-4e79-9669-7f1ed2fc3d0e
---

**All UI pages must render well on every screen size — desktop, iPad/tablet, AND phone.** This is a PRIMARY design rule for all new UI development and every modification to an existing page, not an afterthought.

**Why:** The app is used across desktop, iPad, and phones; a layout that only works on one is considered broken.

**How to apply:**
- When building or editing any template, verify/adjust the responsive behavior — don't ship a desktop-only layout. The app's single mobile breakpoint is `max-width: 700px` (trips map adds a 900px one; `users_manage.html` uses 600px). Each template owns its own mobile CSS block.
- Data tables with many columns/action buttons don't fit phones as tables — collapse rows into stacked cards (hide `thead`, `display:block` the cells, wrap action buttons). This was the fix for `users_manage.html` (admin Users + Share Links tables had up to 5 action buttons per row overflowing phone width).
- Check the mid-size (iPad/tablet) range too, not just desktop vs phone.
- Established patterns to reuse: hamburger nav + fixed bottom tab bar on phones (`base.html`), `--site-top-height`/`--tab-bar-height` CSS vars, form-grids collapsing to one column, Leaflet popup width overrides ≤700px.

Given per [[feedback_attribute_note_edits.md]]-style standing guidance 2026-07-14.
