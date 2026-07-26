---
name: project_weather_finder
description: Summer Seeker was folded into EKKO as the admin-only Weather Finder page (2026-07-26); the standalone app is gone.
metadata: 
  node_type: memory
  type: project
  originSessionId: b6db6beb-b1b9-4a96-a514-02501f5f8005
  modified: 2026-07-26T19:35:32.748Z
---

**Summer Seeker no longer exists as a standalone app** (folded in 2026-07-26, at AWH's request). It is now EKKO's admin-only **Weather Finder** at `/campgrounds/weather`, backed by `POST /api/weather-finder/search` and the `weather_finder.py` engine (shared with the `find_summer.py` CLI). Deleted: `summer_seeker_app.py`, `summer_finder.py`, `templates/index.html`, `README-shared-core.md`.

**Why:** it shared `campgrounds.json` with EKKO but ran on its own port with its own Bootstrap-CDN templates — and it had quietly stopped working. It made one Open-Meteo call *per campground, sequentially*; fine at a few hundred entries, but the database reached 12,872, so a 400-mile search meant 1,289 sequential calls. Scope was broadened in the same pass: as well as the original absolute comfort band it now searches for **cooler than home** or **warmer than home** on the same day, with an optional **little-or-no-rain** filter.

**How to apply / what's load-bearing:**
- The **per-cell forecast cache (1 h TTL) is what makes the page usable**, not an optimization. See [[reference_open_meteo_limits]] — the provider meters locations at 600/min, so without it, tweaking a threshold and re-searching would 429 nearly every time. Measured: 8.57 s cold → 0.10 s warm.
- Cached cells deliberately **don't compete for `FORECAST_BUDGET`**, so a too-wide radius fills in over successive searches instead of being clipped to the same points forever.
- Over budget, the spend splits **half nearest / half by climate direction** (`delta_temp`, the app's latitude+elevation estimate). Proximity-only would systematically discard the far, high places that are exactly what "cooler than home" is asking for; climate-only would ignore the radius the user set.
- Results are **grouped one card per campground** with a chip per matching day. Flat campground-day rows are tens of thousands for a wide search.
- Three bugs were fixed on the way in that the old app had: it read `campgrounds.json` raw with **no `kind` filter** (family entries — relatives' houses — would have appeared as results), it pulled in `geopy` for one haversine, and its streaming `data: `-prefixed progress protocol existed only because the search was slow.
