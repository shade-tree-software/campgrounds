"""Nearest recognizable town for a coordinate, from a local gazetteer.

WHY THIS EXISTS
---------------
Every located thing in the app carries a `locale` that came from Nominatim's
reverse geocode, which walks city → town → village → hamlet → municipality →
township → county and returns the first admin level whose polygon contains the
point. Out in the country that is the last two, so 29% of the library's 1,116
events say "Braxton County" or "Wharton Township" — 177 townships and 144
counties. Nobody orients that way. A traveller says "Bulltown Campground near
Napier", never "in Braxton County", and on trip 95 every one of Rocky Mountain's
overlooks read "Larimer County, CO".

Worse, a named-place answer is not trustworthy either: Lincoln Trail State Park
reverse-geocodes to "Marshall, IL" and sits 3.4 miles outside it, so the app
says a park is IN a town it is merely near. Containment cannot answer "how far,
in which direction" at all, and that is the part a reader actually wants.

So this does not ask a geocoder anything. It measures: distance and bearing from
the point to every populated place around it, and picks the one a person would
name.

THE RULE, AND WHY IT IS NOT "NEAREST"
-------------------------------------
Nearest is wrong, measurably. The closest dot to Moraine Park Campground is
"Fall River Estates Subdivision"; the answer is Estes Park, twice as far. The
closest to Lincoln Trail State Park is Clark Center, population nil; the answer
is Marshall, the county seat a mile further on. You orient by what the listener
would recognize, so prominence has to trade against distance:

  1. A place is a CANDIDATE only within a radius scaled to its size
     (`_MAX_MI`). A crossroads with no recorded population is meaningful for
     three miles; a city of fifty thousand for twenty-five. This is what makes
     silence possible — for Forest Canyon Overlook, high on Trail Ridge Road,
     nothing qualifies, and naming a town eleven miles away would be worse
     than saying nothing at all.
  2. A place with a RECORDED POPULATION beats one without, unless the
     unpopulated one is BOTH within `_CROSSROADS_MAX_MI` and at least
     `_CROSSROADS_RATIO` times closer. GeoNames is thick with named crossroads
     and developments carrying no population; whether they are the right answer
     turns out to depend entirely on whether a real town is also at hand, and
     the measurement is unambiguous. Suburban: the Wawa in Limerick Township
     has Limerick (pop 18,074) 0.5 mi away against "Lindberg Heights" at 0.2 —
     barely closer, so the town wins. Rural: Bulltown Campground has Burnsville
     (pop 498) 5.8 miles off against Napier at 0.7 — eight times closer, so
     Napier wins, which is what a traveller would actually say.
  3. Within a tier the lowest `distance / (1 + log10(1 + population))` wins, so
     population buys distance with sharply diminishing returns and a village a
     mile off still beats a city twenty miles away.
  4. IN vs NEAR is decided by a second, much tighter radius (`_IN_MI`), also
     size-scaled, since a town's dot is its centre and a big town's edge is
     genuinely far from it. Everything else is "near", with a real distance and
     a bearing measured FROM the town TO the point ("two miles north of
     Shelbina" — the lake is north, the town is the anchor).

Verified against the cases that motivated it: Bulltown → near Napier (0.7 mi);
Shelbina Lake → 2 mi N of Shelbina; Lincoln Trail SP → 4 mi SW of Marshall (not
"in" it, and not Clark Center); Moraine Park → 5 mi W of Estes Park; Rainbow
Park → in Wray; Forest Canyon Overlook → nothing.

THE GAZETTEER
-------------
GeoNames' per-country dumps, feature class P (populated places), cached under
`trip_data/geonames/` — gitignored and re-downloadable, the same arrangement
`detect_people.py` and `process_memos.py` use for their model weights. A live
Overpass query was the obvious alternative and is the wrong shape: 1,100 fixed
coordinates is a gazetteer job, not an API job, and the public endpoint answered
the first probe with a 504. Offline also means this works on the USB build.

Feature codes are filtered to real places: PPLQ and PPLH are abandoned or
historical, PPLX is a neighbourhood *inside* another place, and names ending in
"Subdivision" or containing "Mobile Home Park" are developments rather than
somewhere you would say you were near.

Stdlib only, like `weather_finder.py`.
"""

import math
import os
import io
import urllib.request
import zipfile

GEONAMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "trip_data", "geonames")
GEONAMES_URL = "https://download.geonames.org/export/dump/{country}.zip"
COUNTRIES = ("US", "CA")
_UA = "EKKO-Trips/1.0 (+https://github.com/; contact via repo owner)"

# Real places only. PPLQ/PPLH are abandoned or historical; PPLX is a section of
# another place, so naming it points at a neighbourhood rather than a town.
_KEEP_CODES = {"PPL", "PPLL", "PPLA", "PPLA2", "PPLA3", "PPLA4", "PPLC", "PPLS"}
_JUNK_NAME = ("subdivision", "mobile home", "trailer park",
              "(historical)", "estates")

# How far a place of a given size can still be the thing you name. The pop==0
# tier is the load-bearing one: GeoNames records no population for most
# unincorporated crossroads, and three miles is about as far as one stays
# meaningful.
_MAX_MI = ((50000, 25.0), (10000, 18.0), (2000, 9.0), (250, 8.0), (1, 5.0), (0, 3.0))
# How close you have to be to be IN it rather than near it. A town's record is
# a single point at its centre, so this scales with size too.
_IN_MI = ((50000, 3.0), (10000, 2.0), (2000, 1.2), (250, 0.8), (0, 0.4))
# When an unpopulated crossroads may outrank a real town: it has to be close in
# absolute terms AND overwhelmingly closer. Measured against the library's two
# regimes — suburban Philadelphia (a town within a mile, ratios under 3) and
# rural West Virginia (nearest town five or six miles off, ratios above 6).
_CROSSROADS_MAX_MI = 1.5
_CROSSROADS_RATIO = 5.0

_COMPASS = ("north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest")

_places = None      # [(lat, lng, name, admin1, population)]
_grid = None        # {(half-degree cell): [index, ...]}


def _tier(table, population):
    for floor, value in table:
        if population >= floor:
            return value
    return table[-1][1]


def _haversine_mi(lat1, lng1, lat2, lng2):
    r = math.radians
    a = (math.sin(r(lat2 - lat1) / 2) ** 2
         + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(r(lng2 - lng1) / 2) ** 2)
    return 2 * 3958.7613 * math.asin(math.sqrt(a))


def _bearing(lat1, lng1, lat2, lng2):
    """Compass direction from point 1 to point 2, in words."""
    r = math.radians
    y = math.sin(r(lng2 - lng1)) * math.cos(r(lat2))
    x = (math.cos(r(lat1)) * math.sin(r(lat2))
         - math.sin(r(lat1)) * math.cos(r(lat2)) * math.cos(r(lng2 - lng1)))
    deg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return _COMPASS[int((deg + 22.5) // 45) % 8]


def _dump_path(country):
    return os.path.join(GEONAMES_DIR, f"{country}.zip")


def ensure_gazetteer(countries=COUNTRIES, download=True):
    """Make sure the dumps are on disk. Returns the paths that exist."""
    os.makedirs(GEONAMES_DIR, exist_ok=True)
    have = []
    for country in countries:
        path = _dump_path(country)
        if not os.path.exists(path) and download:
            req = urllib.request.Request(GEONAMES_URL.format(country=country),
                                         headers={"User-Agent": _UA})
            tmp = path + ".part"
            with urllib.request.urlopen(req, timeout=120) as resp, \
                    open(tmp, "wb") as out:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            os.replace(tmp, path)
        if os.path.exists(path):
            have.append(path)
    return have


def load(countries=COUNTRIES, download=True):
    """Parse the dumps into memory and index them. Idempotent."""
    global _places, _grid
    if _places is not None:
        return len(_places)
    places, grid = [], {}
    for path in ensure_gazetteer(countries, download=download):
        with zipfile.ZipFile(path) as zf:
            name = next(n for n in zf.namelist()
                        if n.endswith(".txt") and "readme" not in n.lower())
            with zf.open(name) as fh:
                for line in io.TextIOWrapper(fh, "utf-8"):
                    f = line.rstrip("\n").split("\t")
                    if len(f) < 15 or f[6] != "P" or f[7] not in _KEEP_CODES:
                        continue
                    label = f[1]
                    low = label.lower()
                    if any(j in low for j in _JUNK_NAME):
                        continue
                    try:
                        lat, lng, pop = float(f[4]), float(f[5]), int(f[14] or 0)
                    except ValueError:
                        continue
                    grid.setdefault((int(lat * 2), int(lng * 2)), []).append(len(places))
                    places.append((lat, lng, label, f[10], pop))
    _places, _grid = places, grid
    return len(places)


def nearest_town(lat, lng):
    """The place a person would name for this coordinate, or None.

    Returns {name, state, miles, direction, population, inside} where
    `direction` runs FROM the town TO the point and `inside` says the point is
    within the town rather than near it. None means nothing close enough is
    worth naming — an honest answer, and the right one for a mountain overlook.
    """
    if _places is None:
        load()
    # Two tiers, tried in order: places with a recorded population, then the
    # unpopulated crossroads. See rule 2 in the module docstring — this split
    # is what keeps suburban Pennsylvania from being described by localities
    # nobody has heard of while rural West Virginia still gets "near Napier".
    populated, crossroads = None, None
    # Half-degree cells; the widest radius considered is 25 miles, comfortably
    # inside the 3x3 neighbourhood at any latitude the trips reach.
    cell = (int(lat * 2), int(lng * 2))
    for dla in (-1, 0, 1):
        for dlo in (-1, 0, 1):
            for i in _grid.get((cell[0] + dla, cell[1] + dlo), ()):
                p_lat, p_lng, name, admin1, pop = _places[i]
                miles = _haversine_mi(lat, lng, p_lat, p_lng)
                if miles > _tier(_MAX_MI, pop):
                    continue
                score = miles / (1 + math.log10(1 + pop))
                row = (score, miles, name, admin1, pop, p_lat, p_lng)
                if pop > 0:
                    if populated is None or score < populated[0]:
                        populated = row
                elif crossroads is None or score < crossroads[0]:
                    crossroads = row
    best = populated
    if crossroads is not None and (
            best is None
            or (crossroads[1] <= _CROSSROADS_MAX_MI
                and crossroads[1] * _CROSSROADS_RATIO <= best[1])):
        best = crossroads
    if best is None:
        return None
    _score, miles, name, admin1, pop, p_lat, p_lng = best
    return {
        "name": name,
        "state": admin1,
        "miles": round(miles, 1),
        "direction": _bearing(p_lat, p_lng, lat, lng),
        "population": pop,
        "inside": miles <= _tier(_IN_MI, pop),
    }


def describe(lat, lng):
    """`nearest_town` as the phrase a person would write, or ""."""
    hit = nearest_town(lat, lng)
    if not hit:
        return ""
    where = ", ".join(x for x in (hit["name"], hit["state"]) if x)
    if hit["inside"]:
        return where
    miles = hit["miles"]
    # Under a mile reads as "just outside"; beyond that a whole number is how
    # anyone would say it, and a half-mile of precision is false confidence
    # about a campground pin.
    if miles < 1:
        return f"just outside {where}"
    rounded = int(round(miles))
    return f"{rounded} mile{'s' if rounded != 1 else ''} {hit['direction']} of {where}"
