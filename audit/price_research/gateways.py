"""Gateway test for the private price gate (AWH 2026-10-14).

AWH: "drop if over price limit unless very close to major gateway points (major cities, major tourist attractions,
National Parks, etc.)". Working definition, applied to every over-gate private entry:

  A gateway is within RADIUS_KM (40 km, ~25 miles, straight line) of
    - the downtown of a metro area of 1 million or more (US MSAs, 2020 census; Canadian CMAs, 2021 census),
    - an entrance or main visitor center of a US national park or a Parks Canada national park
      (Alaska, Hawaii and the territories are out of scope), or
    - one of a short list of nationally known destinations (ATTRACTIONS).

Points are approximate (a few km); the radius is generous enough that this doesn't matter. National recreation
areas, monuments and seashores count only where they are on the attractions list.

python3 -I gateways.py LAT,LNG [...]   prints the gateways within reach of each point.
"""
import math, sys

RADIUS_KM = 40

METROS = {  # downtowns; two-center metros list both
    "New York": (40.7128, -74.0060), "Newark": (40.7357, -74.1724), "Los Angeles": (34.0522, -118.2437),
    "Long Beach": (33.7701, -118.1937), "Anaheim": (33.8366, -117.9143), "Chicago": (41.8781, -87.6298),
    "Dallas": (32.7767, -96.7970), "Fort Worth": (32.7555, -97.3308), "Houston": (29.7604, -95.3698),
    "Washington": (38.9072, -77.0369), "Philadelphia": (39.9526, -75.1652), "Miami": (25.7617, -80.1918),
    "Fort Lauderdale": (26.1224, -80.1373), "West Palm Beach": (26.7153, -80.0534), "Atlanta": (33.7490, -84.3880),
    "Boston": (42.3601, -71.0589), "Phoenix": (33.4484, -112.0740), "Mesa": (33.4152, -111.8315),
    "San Francisco": (37.7749, -122.4194), "Oakland": (37.8044, -122.2712), "Riverside": (33.9806, -117.3755),
    "San Bernardino": (34.1083, -117.2898), "Detroit": (42.3314, -83.0458), "Seattle": (47.6062, -122.3321),
    "Tacoma": (47.2529, -122.4443), "Minneapolis": (44.9778, -93.2650), "St. Paul": (44.9537, -93.0900),
    "San Diego": (32.7157, -117.1611), "Tampa": (27.9506, -82.4572), "St. Petersburg": (27.7676, -82.6403),
    "Denver": (39.7392, -104.9903), "Baltimore": (39.2904, -76.6122), "St. Louis": (38.6270, -90.1994),
    "Orlando": (28.5383, -81.3792), "Charlotte": (35.2271, -80.8431), "San Antonio": (29.4241, -98.4936),
    "Portland OR": (45.5152, -122.6784), "Sacramento": (38.5816, -121.4944), "Pittsburgh": (40.4406, -79.9959),
    "Austin": (30.2672, -97.7431), "Las Vegas": (36.1699, -115.1398), "Cincinnati": (39.1031, -84.5120),
    "Kansas City": (39.0997, -94.5786), "Columbus": (39.9612, -82.9988), "Indianapolis": (39.7684, -86.1581),
    "Cleveland": (41.4993, -81.6944), "San Jose": (37.3382, -121.8863), "Nashville": (36.1627, -86.7816),
    "Norfolk": (36.8508, -76.2859), "Virginia Beach": (36.8529, -75.9780), "Providence": (41.8240, -71.4128),
    "Jacksonville": (30.3322, -81.6557), "Milwaukee": (43.0389, -87.9065), "Raleigh": (35.7796, -78.6382),
    "Oklahoma City": (35.4676, -97.5164), "Memphis": (35.1495, -90.0490), "Richmond": (37.5407, -77.4360),
    "Louisville": (38.2527, -85.7585), "New Orleans": (29.9511, -90.0715), "Salt Lake City": (40.7608, -111.8910),
    "Hartford": (41.7658, -72.6734), "Buffalo": (42.8864, -78.8784), "Birmingham": (33.5186, -86.8104),
    "Rochester NY": (43.1566, -77.6088), "Grand Rapids": (42.9634, -85.6681), "Tucson": (32.2226, -110.9747),
    "Tulsa": (36.1540, -95.9928), "Fresno": (36.7378, -119.7871), "Worcester": (42.2626, -71.8023),
    "Toronto": (43.6532, -79.3832), "Montreal": (45.5017, -73.5673), "Vancouver": (49.2827, -123.1207),
    "Calgary": (51.0447, -114.0719), "Edmonton": (53.5461, -113.4938), "Ottawa": (45.4215, -75.6972),
}

NATIONAL_PARKS = {  # entrances / main visitor centers
    "Acadia NP": [(44.4093, -68.2470)], "Arches NP": [(38.6166, -109.6197)],
    "Badlands NP": [(43.7497, -101.9420), (43.8963, -102.2362)],
    "Big Bend NP": [(29.3275, -103.2064), (29.6600, -103.1700), (29.3200, -103.5300)],
    "Biscayne NP": [(25.4645, -80.3349)], "Black Canyon of the Gunnison NP": [(38.5422, -107.6865)],
    "Bryce Canyon NP": [(37.6402, -112.1696)], "Canyonlands NP": [(38.4598, -109.8210), (38.1667, -109.7591)],
    "Capitol Reef NP": [(38.2913, -111.2618)], "Carlsbad Caverns NP": [(32.1757, -104.4442)],
    "Channel Islands NP": [(34.2484, -119.2671)], "Congaree NP": [(33.8295, -80.8237)],
    "Crater Lake NP": [(42.9116, -122.1457), (42.8686, -122.1690)], "Cuyahoga Valley NP": [(41.2635, -81.5590)],
    "Death Valley NP": [(36.4617, -116.8656), (36.6062, -117.1453)], "Dry Tortugas NP": [(24.5551, -81.8001)],
    "Everglades NP": [(25.3956, -80.5832), (25.7617, -80.7663), (25.8460, -81.3870)],
    "Gateway Arch NP": [(38.6247, -90.1848)],
    "Glacier NP": [(48.4950, -113.9800), (48.7457, -113.4374), (48.7969, -113.6580)],
    "Grand Canyon NP": [(36.0592, -112.1092), (36.1979, -112.0528)],
    "Grand Teton NP": [(43.6547, -110.7186), (43.4799, -110.7624)], "Great Basin NP": [(39.0054, -114.2203)],
    "Great Sand Dunes NP": [(37.7329, -105.5121)],
    "Great Smoky Mountains NP": [(35.6853, -83.5367), (35.5136, -83.3063), (35.6754, -83.7557)],
    "Guadalupe Mountains NP": [(31.8916, -104.8608)], "Hot Springs NP": [(34.5137, -93.0539)],
    "Indiana Dunes NP": [(41.6339, -87.0545)],
    "Isle Royale NP": [(47.1211, -88.5694), (47.9636, -89.6848), (47.4696, -87.8892)],
    "Joshua Tree NP": [(34.1356, -116.3131), (34.1356, -116.0397), (33.7477, -115.8247)],
    "Kings Canyon NP": [(36.7392, -118.9631)], "Lassen Volcanic NP": [(40.4378, -121.5338), (40.5386, -121.5633)],
    "Mammoth Cave NP": [(37.1870, -86.1009)], "Mesa Verde NP": [(37.3367, -108.4086)],
    "Mount Rainier NP": [(46.7398, -121.9150), (46.7860, -121.7353), (46.9152, -121.6419)],
    "New River Gorge NP": [(38.0700, -81.0758)], "North Cascades NP": [(48.6730, -121.2453)],
    "Olympic NP": [(48.0995, -123.4256), (47.8606, -123.9347), (47.4660, -123.8492), (48.0600, -123.8000)],
    "Petrified Forest NP": [(35.0654, -109.7826), (34.8152, -109.8653)],
    "Pinnacles NP": [(36.4935, -121.1460), (36.4766, -121.2251)],
    "Redwood NP": [(41.7559, -124.2024), (41.2840, -124.0912)],
    "Rocky Mountain NP": [(40.3664, -105.5609), (40.2667, -105.8318)],
    "Saguaro NP": [(32.1800, -110.7365), (32.2489, -111.1680)], "Sequoia NP": [(36.4917, -118.8248)],
    "Shenandoah NP": [(38.9047, -78.1931), (38.6630, -78.3210), (38.3576, -78.5476), (38.0328, -78.8580)],
    "Theodore Roosevelt NP": [(46.9142, -103.5246), (47.5964, -103.2626)],
    "Voyageurs NP": [(48.5845, -93.1617), (48.4447, -93.0310), (48.4342, -92.8475)],
    "White Sands NP": [(32.7797, -106.1717)], "Wind Cave NP": [(43.5567, -103.4785)],
    "Yellowstone NP": [(44.6621, -111.1041), (45.0294, -110.7079), (45.0202, -109.9354), (44.4889, -110.0028),
                       (44.1347, -110.6658)],
    "Yosemite NP": [(37.6747, -119.7769), (37.8007, -119.8742), (37.5059, -119.6312), (37.9105, -119.2575)],
    "Zion NP": [(37.2001, -112.9871), (37.2341, -112.8774)],
    # Parks Canada
    "Banff NP": [(51.1784, -115.5708), (51.4254, -116.1773)], "Jasper NP": [(52.8737, -118.0814)],
    "Yoho NP": [(51.3955, -116.4880)], "Kootenay NP": [(50.6203, -116.0716)],
    "Glacier NP (BC)": [(51.3014, -117.5194)], "Mount Revelstoke NP": [(51.0098, -118.1957)],
    "Waterton Lakes NP": [(49.0516, -113.9118)], "Pacific Rim NP": [(49.1530, -125.9066), (48.9420, -125.5466)],
    "Elk Island NP": [(53.6058, -112.8645)], "Prince Albert NP": [(53.9200, -106.0800)],
    "Grasslands NP": [(49.2394, -107.7311)], "Riding Mountain NP": [(50.6533, -99.9724)],
    "Bruce Peninsula NP": [(45.2554, -81.6649)], "Georgian Bay Islands NP": [(44.8738, -79.8130)],
    "Thousand Islands NP": [(44.4797, -75.8669)], "Point Pelee NP": [(41.9625, -82.5181)],
    "Pukaskwa NP": [(48.5964, -86.2950)], "La Mauricie NP": [(46.6380, -72.7520), (46.5900, -72.9600)],
    "Forillon NP": [(48.8316, -64.4869), (48.8601, -64.2050)], "Mingan Archipelago NPR": [(50.2420, -63.5987)],
    "Fundy NP": [(45.6000, -64.9500)], "Kouchibouguac NP": [(46.8086, -64.9300)],
    "Prince Edward Island NP": [(46.4917, -63.3800), (46.4200, -63.2000), (46.4300, -62.6800)],
    "Kejimkujik NP": [(44.3994, -65.2167)], "Cape Breton Highlands NP": [(46.6650, -60.3733), (46.6369, -60.9497)],
    "Terra Nova NP": [(48.5150, -53.9725)], "Gros Morne NP": [(49.6586, -57.9128), (49.3800, -57.6300)],
}

ATTRACTIONS = {
    "Niagara Falls": (43.0896, -79.0849), "Walt Disney World": (28.3852, -81.5639),
    "Kennedy Space Center": (28.5729, -80.6490), "Mount Rushmore": (43.8791, -103.4591),
    "Branson": (36.6437, -93.2185), "Myrtle Beach": (33.6891, -78.8867), "Colonial Williamsburg": (37.2707, -76.7075),
    "Gettysburg": (39.8309, -77.2311), "Cape Cod (Hyannis)": (41.6526, -70.2881),
    "Cape Cod (Provincetown)": (42.0584, -70.1786), "Outer Banks (Kill Devil Hills)": (36.0307, -75.6760),
    "Cape Hatteras": (35.2510, -75.5290), "Mackinac (Mackinaw City)": (45.7775, -84.7278),
    "Wisconsin Dells": (43.6275, -89.7710), "Key West": (24.5551, -81.7800), "Sedona": (34.8697, -111.7610),
    "Lake George": (43.4262, -73.7123), "Lake Placid": (44.2795, -73.9799), "Lake Tahoe (South)": (38.9399, -119.9772),
    "Lake Tahoe (North)": (39.1677, -120.1452), "St. Augustine": (29.9012, -81.3124), "Savannah": (32.0809, -81.0912),
    "Charleston SC": (32.7765, -79.9311), "Asheville": (35.5951, -82.5515), "Santa Fe": (35.6870, -105.9378),
    "Monument Valley": (36.9980, -110.0985), "Sleeping Bear Dunes": (44.8111, -86.0598),
    "Pictured Rocks (Munising)": (46.4111, -86.6479), "Ocean City MD": (38.3365, -75.0849),
    "Chincoteague (Assateague)": (37.9332, -75.3788), "Quebec City": (46.8139, -71.2080),
    "Whistler": (50.1163, -122.9574),
}


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def gateways(lat, lng, radius=RADIUS_KM):
    """[(km, kind, name)] within radius, nearest first."""
    p = (lat, lng)
    out = [(km(p, c), "metro", n) for n, c in METROS.items()]
    out += [(min(km(p, c) for c in cs), "national park", n) for n, cs in NATIONAL_PARKS.items()]
    out += [(km(p, c), "attraction", n) for n, c in ATTRACTIONS.items()]
    return sorted(x for x in out if x[0] <= radius)


def nearest(lat, lng, n=3):
    """The n nearest gateway points of any kind, for a report line."""
    return sorted([(km((lat, lng), c), "metro", k) for k, c in METROS.items()]
                  + [(min(km((lat, lng), c) for c in cs), "national park", k) for k, cs in NATIONAL_PARKS.items()]
                  + [(km((lat, lng), c), "attraction", k) for k, c in ATTRACTIONS.items()])[:n]


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        la, lo = map(float, arg.split(","))
        g = gateways(la, lo)
        print(arg, "->", "; ".join(f"{n} ({k}, {d:.0f} km)" for d, k, n in g) if g else
              "none within %d km; nearest: %s" % (RADIUS_KM, "; ".join(f"{n} {d:.0f} km" for d, k, n in nearest(la, lo))))
