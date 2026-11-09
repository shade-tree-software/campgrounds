---
name: feedback-high-elevation-mentions
description: "AWH 2026-11-08 - notes never repeat the elevation figure; \"high elevation\" only when well above the local terrain, and in the East only at 3000 ft+"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 63033443-99f7-4b5a-af4e-d10daf222e24
  modified: 2026-11-09T01:48:47.341Z
---

AWH 2026-11-08: a note never carries an elevation figure that repeats `elevation_meters` (1011 were cut). A "high elevation" mention, or a variant like high-alpine, stays only when the campground sits clearly above its own area. In the East it also needs 3000 ft+ (914 m).

**Why:** Watchman, Apgar, Cherry Creek and Many Glacier were all called "high-elevation" while sitting at the bottom of their valleys. The figure is already in a field, the same rule as [[feedback-clean-up-notes]].

**How to apply:** the test used was a 7x7 Open-Meteo DEM grid over ±20 km around the pin. Keep the mention if the campground is at the 75th percentile or above and ~150 m+ over the grid median. Scripts and data: session scratch `elev/` (relief.py, land2.py); commit 769defa3. This drops some absolutely high western sites that are only mid-slope for their area (Weston Pass 10,256 ft, Molas Lake, Spirit Lake), which is AWH's stated rule. Positional phrases ("high on the Blue Mountains ridge", "high country") were left alone.
