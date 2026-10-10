#!/usr/bin/env python3
"""Nightly fees for recreation.gov campgrounds from rec.gov's own rate table (2026-10-09).

    python3 audit/price_research/recgov_rates.py --fetch [--limit N]   # fill the cache (1.2 s/request)
    python3 audit/price_research/recgov_rates.py --build OUT.json      # findings for apply.py, free

`GET https://www.recreation.gov/api/camps/campgrounds/<id>/rates` (keyless) returns every
season the facility has ever priced, each with a `price_map` of nightly price per site type
("PeakSTANDARD NONELECTRIC": 29). Rules, each chosen so the number answers "what does a
night cost us in an RV":

- **Current seasons only.** The list holds a decade of history; only seasons ending today or
  later count, and if none do, the most recent year's seasons (a campground whose 2027
  calendar is not loaded yet still says what it charged this year).
- **Drive-in RV-usable site types only**: STANDARD / RV, electric or not. Doubles ("-DBL" in
  `name_map`), group, tent-only, walk-to, hike-to, boat-in, cabins, yurts, lookouts,
  equestrian and management sites price something else.
- **The type's own rate, not per-site overrides**: keys suffixed "u52-00p0-00..." price a few
  individual sites (often doubles at twice the rate) and count only when no plain key does.
- A price over twice the facility's median is a multi-unit or long-term rate typed as a
  standard site and is dropped.
- A 0 price is kept only when EVERY counted price is 0 (a genuinely free campground);
  otherwise a stray 0 is a placeholder, not a free season.
- nightly_low / nightly_high = min / max of what survives.

Entries: kind campground, a recreation.gov campground URL in `website`, no `fees` yet.
Cache: trip_data/recgov_rates.json (gitignored), written after every facility.
"""
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, "trip_data", "recgov_rates.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0"
TODAY = date(2026, 10, 9).isoformat()
KEEP = re.compile(r"^(STANDARD|RV) (NON)?ELECTRIC$|^STANDARD FULL HOOKUP$|^RV FULL HOOKUP$")
DROP_NAME = re.compile(r"DBL|DOUBLE|GROUP|TENT|WALK|HIKE|BOAT|CABIN|YURT|LOOKOUT|EQUEST|HORSE|MANAGEMENT|SHELTER|GLAMP|TRIPLE|LONG TERM|MONTHLY|SEASONAL",
                       re.I)

# "PeakSTANDARD ELECTRICu52-00p0-00..." prices a handful of individual sites, often a double
# pad at twice the rate; the plain "PeakSTANDARD ELECTRIC" key is the campground's own rate.
OVERRIDE_KEY = re.compile(r"u\d+-\d\dp\d")


def facility_id(entry):
    m = re.search(r"recreation\.gov/camping/campgrounds/(\d+)", entry.get("website") or "")
    return m.group(1) if m else None


def targets():
    rows = json.load(open(os.path.join(ROOT, "campgrounds.json")))
    return [(r, facility_id(r)) for r in rows
            if r.get("kind") != "family" and not r.get("fees") and facility_id(r)]


def fetch(limit):
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [fid for _, fid in targets() if fid not in cache]
    todo = list(dict.fromkeys(todo))[:limit] if limit else list(dict.fromkeys(todo))
    for i, fid in enumerate(todo, 1):
        req = urllib.request.Request(f"https://www.recreation.gov/api/camps/campgrounds/{fid}/rates",
                                     headers={"User-Agent": UA})
        try:
            cache[fid] = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print("ERR", fid, str(e)[:80])
            if "429" in str(e):
                time.sleep(30)
            continue
        with open(CACHE + ".tmp", "w") as fh:
            json.dump(cache, fh)
        os.replace(CACHE + ".tmp", CACHE)
        if i % 25 == 0:
            print(i, "of", len(todo))
        time.sleep(1.2)
    print("cached", len(cache))


def price_range(rates):
    seasons = rates.get("rates_list") or []
    current = [s for s in seasons if (s.get("season_end") or "")[:10] >= TODAY]
    if not current and seasons:
        last = max((s.get("season_end") or "")[:4] for s in seasons)
        current = [s for s in seasons if (s.get("season_end") or "")[:4] == last]
    base, override = [], []
    for s in current:
        for key, price in (s.get("price_map") or {}).items():
            stype = (s.get("site_type_map") or {}).get(key, "")
            name = (s.get("name_map") or {}).get(key, "")
            if KEEP.match(stype) and not DROP_NAME.search(name) and isinstance(price, (int, float)):
                (override if OVERRIDE_KEY.search(key) else base).append(price)
    vals = base or override
    if not vals:
        return None
    if any(v > 0 for v in vals):
        vals = sorted(v for v in vals if v > 0)
        med = vals[len(vals) // 2]
        vals = [v for v in vals if v <= 2 * med]     # a mislabelled multi-unit or monthly rate
    return min(vals), max(vals)


def build(out):
    cache = json.load(open(CACHE))
    F, none = [], 0
    for r, fid in targets():
        if fid not in cache:
            continue
        pr = price_range(cache[fid])
        if not pr:
            none += 1
            continue
        lo, hi = (int(v) if float(v).is_integer() else v for v in pr)
        F.append({"id": r["id"], "fees": {"nightly_low": lo, "nightly_high": hi, "currency": "USD"},
                  "source": f"https://www.recreation.gov/api/camps/campgrounds/{fid}/rates "
                            f"(recreation.gov rate table, current seasons, standard/RV sites)"})
    json.dump(F, open(out, "w"), indent=1)
    print(len(F), "findings;", none, "facilities with no standard/RV rate")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0
        fetch(lim)
    elif "--build" in sys.argv:
        build(sys.argv[sys.argv.index("--build") + 1])
