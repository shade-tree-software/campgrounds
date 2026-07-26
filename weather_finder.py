"""Forecast search over the campground database — the Weather Finder engine.

Replaces summer_finder.py, which asked Open-Meteo for one campground at a time.
That was fine when campgrounds.json held a few hundred entries; at ~12.9k (1,289
of them within 400 miles of home) a default search meant 1,289 sequential HTTP
calls — minutes of wall time and a near-certain rate limit. The forecast API
accepts comma-separated coordinate lists and returns one object per location, so
the same search is a handful of calls and a few seconds.

Deliberately stdlib-only (urllib, no `requests`/`geopy`): it's imported by both
the Flask app and the find_summer.py CLI, and dropping those left the repo with
no geopy dependency at all — the app already had its own haversine.

Three search modes, all against the same fetched forecast:
  range   — an absolute comfort band (the original "summer day" behaviour)
  cooler  — at least N °F cooler than home is that same day
  warmer  — at least N °F warmer than home is that same day
The relative modes need home's own forecast, which costs almost nothing: home is
prepended to the coordinate list and rides along in the first batch, and after
the first search of the hour it comes straight out of the cache below.
"""

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Locations per request. 400 was measured working (URL ~7 KB, ~2 s); 200 keeps
# the URL near 3.5 KB, comfortably inside any proxy's request-line limit, and
# still turns a 1,289-campground search into 7 calls.
BATCH_SIZE = 200

# Open-Meteo's free forecast horizon.
FORECAST_DAYS = 16

# Cap on campgrounds returned. A 400-mile search can match well over a thousand
# campgrounds across 16 days; past a couple of hundred the list is unreadable
# and the JSON is megabytes. Callers get `truncated` so they can say so.
MAX_RESULTS = 200

# Coordinates are snapped to this grid before asking for a forecast, and every
# campground in a cell shares that cell's answer. 0.1° is ~11 km, which is the
# resolution of the models Open-Meteo blends — two campgrounds inside one cell
# are reading the same model grid point, so the second request would return a
# near-identical answer at full price. Worth ~1.2x on a 400-mile search.
GRID_DEG = 0.1

# Ceiling on forecast points per search. Open-Meteo's free tier bills per
# LOCATION, not per HTTP call, and allows 600 a minute — so an unbudgeted
# 400-mile search (1,289 campgrounds) doesn't half-work, it 429s outright.
# Searches under ~250 miles fit inside this and are unaffected; beyond that the
# budget picks which points to spend on (see _select_cells) and the caller is
# told the coverage rather than being quietly given a thinner answer.
FORECAST_BUDGET = 500

MODE_RANGE = "range"
MODE_COOLER = "cooler"
MODE_WARMER = "warmer"
MODES = (MODE_RANGE, MODE_COOLER, MODE_WARMER)

SORTS = ("distance", "temp", "rain", "waterfront")

# Ranking for the waterfront sort — best first. The tiers follow the curation
# vocabulary's own hierarchy rather than sorting the strings alphabetically,
# which would put "bayview" above "lakefront".
#
# `coastal woods` sits between the at-the-water types and the view-only ones on
# purpose. It's an earned on-water designation (you walk through the
# campground's own undeveloped shore forest to the beach) but it has no
# sightline, which is exactly why the campground map's "On the water" quick
# filter excludes it. Ranking it below the water's-edge types honours that
# exclusion; ranking it above view-only reflects that access beats a view.
_WATERFRONT_RANKS = {
    "bayfront": 0, "lakefront": 0, "riverfront": 0,
    "creekside": 0, "pond": 0, "coastal dunes": 0,
    # Legacy one-off, not part of the vocabulary: campgrounds.json id 1366
    # (Sycamore Springs Park, IN) says "riverside". Its --AWH evidence has sites
    # on the Little Blue River, so it belongs in this tier — without the alias
    # it would silently sort as "not waterfront". Drop this line once the entry
    # is normalised to "riverfront".
    "riverside": 0,
    "coastal woods": 1,
    "lakeview": 2, "riverview": 2, "bayview": 2,
    "not waterfront": 3,
}


def waterfront_rank(value):
    """Sort rank for a `waterfront` value; anything unrecognised sorts last."""
    return _WATERFRONT_RANKS.get((value or "not waterfront").strip().lower(), 3)


_DAILY_VARS = ("temperature_2m_max", "temperature_2m_min",
               "precipitation_sum", "precipitation_probability_max")


def haversine_miles(lat1, lng1, lat2, lng2):
    """Great-circle distance in statute miles."""
    r = 3958.7613
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lng2 - lng1) * p / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


# ── Forecast cache ─────────────────────────────────────────────────────────
# Keyed by grid cell, so it is shared across searches AND across users. This is
# what makes the feature usable at all: the provider allows 600 locations a
# minute (measured — 600 succeeds, 800 gives 429), and a single 400-mile search
# spends most of that. Without a cache, adjusting a threshold and searching
# again — the obvious way to use the page — would rate-limit almost every time.
# With it, only the first search of the hour costs anything; re-filtering is
# free and instant, because the filtering is all local anyway.
#
# An hour matches how often the upstream models actually refresh, so this
# doesn't serve anything staler than the API would.
FORECAST_TTL_S = 3600
_forecast_cache = {}


def _cache_get(key, now):
    hit = _forecast_cache.get(key)
    if hit is None:
        return None
    fetched_at, daily = hit
    if now - fetched_at > FORECAST_TTL_S:
        _forecast_cache.pop(key, None)
        return None
    return daily


def _cache_put(key, daily, now):
    # Cheap bounded-growth guard: when the cache gets large, drop what's expired
    # before adding more. Entries are small (16 days × 5 arrays), so this only
    # needs to stop unbounded accumulation over a long uptime.
    if len(_forecast_cache) > 20000:
        for k, (t, _) in list(_forecast_cache.items()):
            if now - t > FORECAST_TTL_S:
                _forecast_cache.pop(k, None)
    _forecast_cache[key] = (now, daily)


class RateLimited(RuntimeError):
    """Open-Meteo refused the batch because the free tier's budget is spent.

    Raised rather than swallowed: a partly-fetched search returns fewer matches,
    which is indistinguishable to the reader from "there aren't any" — the one
    failure mode worth being loud about.
    """


def fetch_daily_forecasts(points, *, forecast_days=FORECAST_DAYS, batch_size=BATCH_SIZE,
                          timeout=30, user_agent=None, progress=None):
    """Daily forecast for each (lat, lng) in `points`, in the same order.

    Returns a list the same length as `points`; an entry is None where the API
    gave us nothing usable for that location. An ordinary failed batch degrades
    to Nones for its members rather than sinking the whole search, but a 429 is
    raised — see RateLimited.
    """
    out = [None] * len(points)
    if not points:
        return out
    headers = {"User-Agent": user_agent} if user_agent else {}
    done = 0

    for offset in range(0, len(points), batch_size):
        batch = points[offset:offset + batch_size]
        query = urllib.parse.urlencode({
            "latitude": ",".join(f"{lat:.4f}" for lat, _ in batch),
            "longitude": ",".join(f"{lng:.4f}" for _, lng in batch),
            "daily": ",".join(_DAILY_VARS),
            "timezone": "auto",
            "forecast_days": forecast_days,
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
        })
        try:
            req = urllib.request.Request(f"{FORECAST_URL}?{query}", headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise RateLimited(
                    "The weather service is rate-limited right now — it allows "
                    "600 locations a minute and this search asked for a big "
                    "slice of that. Wait a minute and try again, or narrow the "
                    "distance.") from e
            data = []
        except Exception:
            data = []
        # A single-location request returns a bare object rather than a
        # one-element list — which the last batch hits whenever the point count
        # is one past a multiple of batch_size.
        if isinstance(data, dict):
            data = [data]
        for i, loc in enumerate(data[:len(batch)]):
            daily = (loc or {}).get("daily") or {}
            if daily.get("time"):
                out[offset + i] = daily
        done += len(batch)
        if progress:
            progress(done, len(points))
    return out


def _select_cells(cells, mode, budget):
    """Choose which of the not-yet-cached cells to spend the forecast budget on.

    Under budget, everything is fetched and this is a no-op — the usual case for
    searches inside ~250 miles. Over budget, the spend is split in half:

      • half on the NEAREST cells, because the user set a radius and silently
        ignoring the near half of it would be indefensible; and
      • half on the cells whose climate estimate points the way they asked
        (coolest first for `cooler`, warmest for `warmer`), because for those
        modes the answer usually lives at the far, high end — proximity-only
        selection would systematically discard exactly what was asked for.

    The climate half uses `delta_temp`, the app's per-campground estimate from
    latitude and elevation. It's only a prior, not the answer: the actual
    forecast still decides. Entries without it (the CLI reads campgrounds.json
    raw) fall back to distance, which just collapses this to nearest-first.
    """
    if len(cells) <= budget:
        return cells

    half = budget // 2
    by_distance = sorted(cells, key=lambda c: c["dist"])
    chosen = {id(c): c for c in by_distance[:half]}

    if mode in (MODE_COOLER, MODE_WARMER):
        sign = 1 if mode == MODE_COOLER else -1
        by_climate = sorted(cells, key=lambda c: sign * c["delta_temp"])
    else:
        by_climate = by_distance
    for cell in by_climate:
        if len(chosen) >= budget:
            break
        chosen.setdefault(id(cell), cell)
    return list(chosen.values())


def _day_rows(daily):
    """Flatten one location's parallel daily arrays into per-date dicts."""
    times = daily.get("time") or []
    highs = daily.get("temperature_2m_max") or []
    lows = daily.get("temperature_2m_min") or []
    precip = daily.get("precipitation_sum") or []
    chance = daily.get("precipitation_probability_max") or []

    def at(seq, i):
        return seq[i] if i < len(seq) else None

    rows = []
    for i, date in enumerate(times):
        rows.append({
            "date": date,
            "high": at(highs, i),
            "low": at(lows, i),
            "precip": at(precip, i),
            "precip_chance": at(chance, i),
        })
    return rows


def _weekday(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")


def find_matching_days(campgrounds, home, *, mode=MODE_RANGE,
                       min_high=70.0, max_high=88.0, delta_f=5.0,
                       max_miles=400.0, weekends_only=True,
                       max_precip_in=None, max_precip_chance=None,
                       sort="distance",
                       max_results=MAX_RESULTS, forecast_budget=FORECAST_BUDGET,
                       forecast_days=FORECAST_DAYS, progress=None, **fetch_kw):
    """Find campgrounds whose forecast matches, grouped one entry per campground.

    `campgrounds` is any iterable of dicts carrying `name` and `location`
    ("lat,lng") — the rows from the app's _load_campgrounds() are exactly right
    and already exclude family-kind entries. `home` is (lat, lng).

    Results are grouped rather than flattened: a campground that matches on six
    days is one result with six days attached, not six results. Flat rows put
    the same campground on screen over and over and made the payload enormous.
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")
    if sort not in SORTS:
        raise ValueError(f"unknown sort {sort!r}")
    home_lat, home_lng = float(home[0]), float(home[1])
    needs_home = mode in (MODE_COOLER, MODE_WARMER)

    # ── Narrow by distance before asking about weather ──────────────────────
    eligible = []
    for cg in campgrounds:
        loc = cg.get("location")
        if not loc:
            continue
        try:
            lat, lng = (float(x) for x in loc.split(","))
        except (ValueError, AttributeError):
            continue
        dist = haversine_miles(home_lat, home_lng, lat, lng)
        if dist <= max_miles:
            eligible.append((cg, lat, lng, dist))

    # ── Collapse onto the forecast grid, then spend the budget ──────────────
    cells = {}
    for item in eligible:
        cg, lat, lng, dist = item
        key = (round(lat / GRID_DEG), round(lng / GRID_DEG))
        cell = cells.get(key)
        if cell is None:
            cell = cells[key] = {"key": key, "lat": lat, "lng": lng, "dist": dist,
                                 "delta_temp": cg.get("delta_temp") or 0.0,
                                 "members": []}
        elif dist < cell["dist"]:
            # Represent the cell by its nearest member, so the coordinate we
            # ask about is the one a reader is most likely to care about.
            cell.update(lat=lat, lng=lng, dist=dist)
        cell["delta_temp"] = min(cell["delta_temp"], cg.get("delta_temp") or 0.0) \
            if mode == MODE_COOLER else max(cell["delta_temp"], cg.get("delta_temp") or 0.0)
        cell["members"].append(item)

    # ── Take everything already cached; ration only the new fetches ─────────
    # Cached cells are free, so they never compete for the budget. That gives
    # the budget a useful property: a radius too big to cover in one search
    # fills in over the next couple of searches instead of being permanently
    # truncated to the same 500 points every time.
    now = time.time()
    ck = lambda key: (key, forecast_days)
    cached, uncached = [], []
    for cell in cells.values():
        cell["daily"] = _cache_get(ck(cell["key"]), now)
        (cached if cell["daily"] is not None else uncached).append(cell)

    need = _select_cells(uncached, mode, forecast_budget)
    selected = cached + need
    covered = sum(len(c["members"]) for c in selected)

    home_key = (round(home_lat / GRID_DEG), round(home_lng / GRID_DEG))
    home_daily = _cache_get(ck(home_key), now) if needs_home else None
    fetch_home = needs_home and home_daily is None

    points = [(c["lat"], c["lng"]) for c in need]
    if fetch_home:
        points.insert(0, (home_lat, home_lng))

    fetched = fetch_daily_forecasts(points, forecast_days=forecast_days,
                                    progress=progress, **fetch_kw)
    offset = 0
    if fetch_home:
        home_daily = fetched[0]
        offset = 1
        if home_daily is not None:
            _cache_put(ck(home_key), home_daily, now)
    for cell, daily in zip(need, fetched[offset:]):
        cell["daily"] = daily
        if daily is not None:
            _cache_put(ck(cell["key"]), daily, now)

    home_by_date = {}
    if needs_home:
        if home_daily is None:
            # Every cooler/warmer comparison is against home, so without it
            # there is no honest answer — say so rather than silently returning
            # an empty list the caller would report as "no matches".
            raise RuntimeError("Could not fetch the forecast for home, so there's "
                               "nothing to compare against.")
        for row in _day_rows(home_daily):
            if row["high"] is not None:
                home_by_date[row["date"]] = row["high"]

    # ── Test each cell's days, then attach to its campgrounds ──────────────
    # Day matching is per CELL, not per campground: everything in a cell shares
    # one forecast, so testing it once and fanning the result out is both the
    # obvious reading and the cheap one.
    results = []
    for cell in selected:
        daily = cell["daily"]
        if daily is None:
            continue
        matches = []
        for row in _day_rows(daily):
            high = row["high"]
            if high is None:
                continue
            if weekends_only and _weekday(row["date"]) not in ("Saturday", "Sunday"):
                continue

            home_high = home_by_date.get(row["date"])
            if mode == MODE_RANGE:
                if not (min_high <= high <= max_high):
                    continue
                delta = None if home_high is None else round(high - home_high, 1)
            else:
                if home_high is None:
                    continue  # home's forecast doesn't reach this date
                delta = high - home_high
                if mode == MODE_COOLER and delta > -delta_f:
                    continue
                if mode == MODE_WARMER and delta < delta_f:
                    continue
                delta = round(delta, 1)

            # Rain filters. A missing value is treated as "unknown, don't
            # exclude" — dropping a campground because the API omitted a number
            # would quietly shrink the results for a reason nobody could see.
            if max_precip_in is not None and (row["precip"] or 0) > max_precip_in:
                continue
            if (max_precip_chance is not None and row["precip_chance"] is not None
                    and row["precip_chance"] > max_precip_chance):
                continue

            matches.append({
                "date": row["date"],
                "day": _weekday(row["date"])[:3],
                "high": round(high, 1),
                "low": None if row["low"] is None else round(row["low"], 1),
                "precip": row["precip"],
                "precip_chance": row["precip_chance"],
                "home_high": None if home_high is None else round(home_high, 1),
                "delta": delta,
            })

        if not matches:
            continue
        # Per-cell "best day" figures, which are what the sorts rank on. A
        # campground with six matching days is judged on its best one — sorting
        # a list of campgrounds by an average of days nobody asked about would
        # bury the standout weekend among the mediocre midweek ones.
        deltas = [m["delta"] for m in matches if m["delta"] is not None]
        best_delta = (min(deltas) if mode == MODE_COOLER else max(deltas)) if deltas else None
        highs = [m["high"] for m in matches if m["high"] is not None]
        best_high = (max(highs) if mode == MODE_WARMER else min(highs)) if highs else None
        rains = [m["precip"] for m in matches if m["precip"] is not None]
        min_precip = min(rains) if rains else None

        for cg, lat, lng, dist in cell["members"]:
            results.append({
                "id": cg.get("id"),
                "name": cg.get("name"),
                "state": cg.get("state"),
                "waterfront": cg.get("waterfront") or "not waterfront",
                "ownership": cg.get("ownership"),
                "elevation_feet": cg.get("elevation_feet"),
                "website": cg.get("website"),
                "note": cg.get("note"),
                "visit_count": cg.get("visit_count", 0),
                "lat": lat,
                "lng": lng,
                "dist": round(dist, 1),
                "days": matches,
                "best_delta": best_delta,
                "best_high": best_high,
                "min_precip": min_precip,
                "waterfront_rank": waterfront_rank(cg.get("waterfront")),
            })

    # ── Order ───────────────────────────────────────────────────────────────
    # Distance is always the tiebreaker: whatever you sorted on, among equals
    # the nearer one is the better trip.
    def key(r):
        if sort == "temp":
            if mode == MODE_RANGE:
                # No home temperature to differ from, so rank the actual high:
                # coolest first, which is what "too hot" searching wants.
                primary = r["best_high"] if r["best_high"] is not None else 999
            else:
                # Cooler wants the most negative delta first, warmer the most
                # positive — negate the latter so both read as "best first".
                d = r["best_delta"]
                primary = (999 if d is None
                           else (d if mode == MODE_COOLER else -d))
        elif sort == "rain":
            # Driest first. Unknown sorts last rather than first — an absent
            # number is not evidence of a dry day.
            primary = r["min_precip"] if r["min_precip"] is not None else 999
        elif sort == "waterfront":
            primary = r["waterfront_rank"]
        else:
            primary = r["dist"]
        return (primary, r["dist"], r["name"] or "")

    results.sort(key=key)
    total = len(results)
    return {
        # Everything inside the radius...
        "eligible": len(eligible),
        # ...of which this many actually had their forecast fetched. Equal to
        # `eligible` unless the budget bit; the UI says so when they differ,
        # because "no matches" means something different when only part of the
        # radius was checked.
        "considered": covered,
        "cells": len(cells),
        "fetched": len(need) + (1 if fetch_home else 0),
        "from_cache": len(cached),
        "matched": total,
        "truncated": total > max_results,
        "results": results[:max_results],
    }


def send_sms_notification(phone, message):
    """Send an SMS via textbelt (used by the find_summer.py CLI)."""
    body = urllib.parse.urlencode({
        "phone": phone, "message": message, "key": "textbelt",
    }).encode()
    try:
        with urllib.request.urlopen("https://textbelt.com/text", body, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"success": False, "error": str(e)}


def load_config(config_file="home.json"):
    """Read home.json (gitignored per-machine config). Missing file → {}."""
    try:
        with open(config_file, "rt", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_campgrounds(input_file="campgrounds.json"):
    """Campground-kind entries only.

    The `kind` filter is the point: campgrounds.json is a unified database that
    also holds `kind: "family"` records (relatives' houses). summer_finder.py
    predated that and read the file raw, so once family entries landed it would
    have reported the weather at your relatives' homes as search results.
    """
    with open(input_file, "rt", encoding="utf-8") as f:
        return [e for e in json.load(f) if e.get("kind") != "family"]
