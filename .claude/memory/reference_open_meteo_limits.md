---
name: reference_open_meteo_limits
description: "Open-Meteo free tier bills per LOCATION, not per HTTP call — 600/minute, measured. Shapes any bulk forecast/elevation work."
metadata: 
  node_type: memory
  type: reference
  originSessionId: b6db6beb-b1b9-4a96-a514-02501f5f8005
  modified: 2026-07-26T19:35:15.333Z
---

Open-Meteo's free tier meters **locations, not HTTP calls**. Measured 2026-07-26 from a cold start, 200 locations at a time:

```
cumulative= 600  n=200 OK   (200 locs, 1.0s)
cumulative= 800  n=200 HTTP 429: Minutely API request limit exceeded.
```

So the per-minute budget is **600 locations**, whether that's 600 single-location calls or 3 calls of 200.

**The batching that makes bulk work possible:** both `/v1/forecast` and `/v1/elevation` accept comma-separated `latitude`/`longitude` lists and return one object per location (a *bare object*, not a 1-element list, when only one location is asked for — handle that). 400 locations in one call is ~7 KB of URL and ~2 s. Daily vars that come back together in one request: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `precipitation_probability_max`, with `temperature_unit=fahrenheit` and `precipitation_unit=inch`. Free forecast horizon is 16 days.

**Why it matters here:** 1,289 campgrounds sit within 400 miles of home, so one wide search spends most of a minute's budget. See [[project_weather_finder]] for how the app copes (grid snapping + an hour-long per-cell cache). Model resolution is ~11 km, so requesting points closer together than ~0.1° is paying twice for the same grid cell.

Applies to any future bulk elevation/forecast job too — the state-sweep elevation fetches use the same API and the same meter.
