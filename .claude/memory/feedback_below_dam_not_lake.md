---
name: feedback-below-dam-not-lake
description: AWH 2026-10-21 - a campground behind a dam's berm or below the lake's elevation gets no lake value; overhead imagery hides berms, so compare DEM elevation to pool
metadata:
  type: feedback
---

AWH 2026-10-21: "be careful of labeling any campground as waterfront/waterview if it sits near a
reservoir or a dammed lake but is located behind the berm of the dam or below the elevation of the
lake. Sometimes it's hard to see berms and elevation differences on overhead photography."

**Why:** satellite flattens relief; a pad 30 m from open water across an earthen embankment looks
lakefront from above but has neither access nor a view.

**How to apply:** for any lake value near a dam, find the dam and compare the campground's
Open-Meteo DEM elevation with the lake's normal pool (agency figure, else DEM on the water).
Meaningfully below pool or downstream of the dam axis → no lake value; judge it against the
tailwater river on its own evidence. Written into docs/campground-curation.md (waterfront bullet)
and audit/waterfront_audit_instructions.md. Part of the gate in [[feedback-reaudit-contrary-waterfront-claims]]
and [[feedback-waterfront-evidence-in-json]].
