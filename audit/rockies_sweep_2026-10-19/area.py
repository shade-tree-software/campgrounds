"""The mini-sweep's study area (AWH 2026-10-19): Glacier, Waterton, Banff,
Lake Louise and Jasper, in or near the parks and their tourist towns.

A point is IN when it lies within RADIUS_KM of any anchor: each park's
entrances and visitor centres, the tourist towns, and points along the park
roads (Going-to-the-Sun, the Icefields Parkway) so the interiors are covered.
40 km is the gateway radius of audit/price_research/gateways.py."""
import math

RADIUS_KM = 40
ANCHORS = {
    # Glacier NP
    "West Glacier": (48.4950, -113.9800), "St. Mary": (48.7457, -113.4374),
    "Many Glacier": (48.7969, -113.6580), "Two Medicine / East Glacier": (48.4920, -113.3650),
    "Logan Pass": (48.6966, -113.7183), "Polebridge": (48.7830, -114.2800),
    "Essex / Walton": (48.2780, -113.6100), "Columbia Falls": (48.3722, -114.1810),
    "Whitefish": (48.4111, -114.3376), "Babb": (48.8600, -113.4500), "Goat Haunt": (48.9600, -113.8900),
    # Waterton Lakes NP
    "Waterton townsite": (49.0516, -113.9118),
    # Banff NP + Canmore + Lake Louise
    "Banff": (51.1784, -115.5708), "Canmore": (51.0891, -115.3580), "Lake Louise": (51.4254, -116.1773),
    "Castle Junction": (51.2660, -115.9180), "Saskatchewan Crossing": (51.9660, -116.7200),
    "Bow Summit": (51.7110, -116.5000),
    # Jasper NP
    "Columbia Icefield": (52.2200, -117.2250), "Sunwapta Falls": (52.5320, -117.6440),
    "Jasper": (52.8737, -118.0814), "Jasper East Gate / Pocahontas": (53.1970, -117.9200),
}

# (s, w, n, e) boxes enclosing every anchor's circle, for directory queries.
BOXES = [(47.9, -114.9, 49.4, -112.9),     # Glacier + Waterton
         (50.7, -116.9, 52.3, -114.8),     # Canmore, Banff, Lake Louise, Icefields south
         (52.0, -118.7, 53.6, -117.0)]     # Icefields north, Jasper, Hinton


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(h))


def nearest(pt):
    name = min(ANCHORS, key=lambda n: km(pt, ANCHORS[n]))
    return name, km(pt, ANCHORS[name])


def inside(pt):
    return nearest(pt)[1] <= RADIUS_KM
