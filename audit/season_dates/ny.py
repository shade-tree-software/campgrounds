#!/usr/bin/env python3
"""New York: season from each campground's ReserveAmerica page (2026-10-20).

    python3 -I audit/season_dates/ny.py [--apply]

parks.ny.gov and dec.ny.gov sit behind a bot wall, so the source is the booking site both agencies
use, newyorkstateparks.reserveamerica.com.

State parks (OPRHP): each page's "Season Dates" block gives campsite dates by year and loop. The
2027 campsite dates are used (2026 where 2027 is not posted, which the note says): opens is the
earliest loop's first night, closes the latest loop's last night, and the note gives the loops
that differ. Cabin, cottage, yurt, pavilion and marina dates are ignored, and so is the page's
"Status" line, which follows the cabins (Heckscher's status opens in April, its campsites in May;
Fahnestock's reads "Open year round" for a pavilion).

DEC campgrounds: the page's 2027 season schedule (Core / Peak / Non Peak). The first night opens
the season. The last is the close only when it runs past Labor Day weekend; a schedule that ends
Sep 5 says when reservations end, not that the gate shuts, so closes is left unset.

Lake Erie posts no Season Dates block and takes its 2027 schedule (May 21 - Oct 10).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

READ = "read 2026-10-20"

DEC = {
    20: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/mongaup%20pond/r/campgroundDetails.do?contractCode=NY&parkId=100"),  # Mongaup Pond
    21: ("05-14", "10-23", "https://newyorkstateparks.reserveamerica.com/camping/north-south%20lake%20campground/r/campgroundDetails.do?contractCode=NY&parkId=5"),  # North-South Lake Campground
    287: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/cranberry-lake-campground/r/campgroundDetails.do?contractCode=NY&parkId=706"),  # Cranberry Lake Campground
    309: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/lake-george-battleground/r/campgroundDetails.do?contractCode=NY&parkId=122"),  # Lake George Battleground
    341: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/lake-harris-campground/r/campgroundDetails.do?contractCode=NY&parkId=593"),  # Lake Harris Campground
    342: ("05-07", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/wilmington-notch/r/campgroundDetails.do?contractCode=NY&parkId=561"),  # Wilmington Notch
    343: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/meadowbrook-public-campground/r/campgroundDetails.do?contractCode=NY&parkId=618"),  # Meadowbrook Public Campground
    345: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/scaroon-manor/r/campgroundDetails.do?contractCode=NY&parkId=3386"),  # Scaroon Manor
    346: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/putnam-pond/r/campgroundDetails.do?contractCode=NY&parkId=540"),  # Putnam Pond
    348: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/lake-eaton-campground/r/campgroundDetails.do?contractCode=NY&parkId=594"),  # Lake Eaton Campground
    350: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/nicks-lake-campground/r/campgroundDetails.do?contractCode=NY&parkId=699"),  # Nicks Lake Campground
    351: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/moffitt-beach-campground/r/campgroundDetails.do?contractCode=NY&parkId=673"),  # Moffitt Beach Campground
    353: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/lewey-lake/r/campgroundDetails.do?contractCode=NY&parkId=657"),  # Lewey Lake
    354: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/lake-durant/r/campgroundDetails.do?contractCode=NY&parkId=653"),  # Lake Durant
    355: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/golden-beach-campground/r/campgroundDetails.do?contractCode=NY&parkId=642"),  # Golden Beach Campground
    356: ("06-28", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/eighth-lake-campground/r/campgroundDetails.do?contractCode=NY&parkId=636"),  # Eighth Lake Campground
    357: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/meacham-lake-campground/r/campgroundDetails.do?contractCode=NY&parkId=608"),  # Meacham Lake Campground
    358: ("05-24", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/fish-creek-pond-campground/r/campgroundDetails.do?contractCode=NY&parkId=574"),  # Fish Creek Pond Campground
    363: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/crown-point-campground/r/campgroundDetails.do?contractCode=NY&parkId=573"),  # Crown Point Campground
    364: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/northampton-beach-campground/r/campgroundDetails.do?contractCode=NY&parkId=681"),  # Northampton Beach Campground
    365: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/buck-pond-campground/r/campgroundDetails.do?contractCode=NY&parkId=572"),  # Buck Pond Campground
    366: ("05-14", "09-11", "https://newyorkstateparks.reserveamerica.com/camping/rollins-pond-campground/r/campgroundDetails.do?contractCode=NY&parkId=547"),  # Rollins Pond Campground
    1390: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/sacandaga-campground/r/campgroundDetails.do?contractCode=NY&parkId=716"),  # Sacandaga Campground
    1402: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/woodland-valley/r/campgroundDetails.do?contractCode=NY&parkId=489"),  # Woodland Valley
    1403: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/bear-spring-mountain/r/campgroundDetails.do?contractCode=NY&parkId=13"),  # Bear Spring Mountain
    1407: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/frontier-town-campground/r/campgroundDetails.do?contractCode=NY&parkId=6235"),  # Frontier Town Campground
    1409: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/limekiln-lake/r/campgroundDetails.do?contractCode=NY&parkId=661"),  # Limekiln Lake
    1410: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/caroga-lake-campground/r/campgroundDetails.do?contractCode=NY&parkId=627"),  # Caroga Lake Campground
    1416: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/paradox-lake-campground/r/campgroundDetails.do?contractCode=NY&parkId=619"),  # Paradox Lake Campground
    1419: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/piseco-lake-campground/r/campgroundDetails.do?contractCode=NY&parkId=11135"),  # Piseco Lake Campground
    1422: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/kenneth-l-wilson/r/campgroundDetails.do?contractCode=NY&parkId=117"),  # Kenneth L. Wilson
    1423: ("05-14", "09-11", "https://newyorkstateparks.reserveamerica.com/camping/hearthstone-point/r/campgroundDetails.do?contractCode=NY&parkId=505"),  # Hearthstone Point
    1424: ("05-14", "09-11", "https://newyorkstateparks.reserveamerica.com/camping/eagle-point/r/campgroundDetails.do?contractCode=NY&parkId=500"),  # Eagle Point
    1425: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/sharp-bridge/r/campgroundDetails.do?contractCode=NY&parkId=560"),  # Sharp Bridge
    1426: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/beaverkill/r/campgroundDetails.do?contractCode=NY&parkId=90"),  # Beaverkill (John And Patricia Adams Campground At)
    1427: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/brown-tract-pond-campground/r/campgroundDetails.do?contractCode=NY&parkId=625"),  # Brown Tract Pond Campground
    1429: ("05-14", "10-11", "https://newyorkstateparks.reserveamerica.com/camping/devils-tombstone-campground/r/campgroundDetails.do?contractCode=NY&parkId=27"),  # Devils Tombstone Campground
    1430: ("05-14", "10-10", "https://newyorkstateparks.reserveamerica.com/camping/little-pond-campground/r/campgroundDetails.do?contractCode=NY&parkId=495"),  # Little Pond Campground
    1433: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/lincoln-pond-campground/r/campgroundDetails.do?contractCode=NY&parkId=602"),  # Lincoln Pond Campground
    1434: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/taylor-pond-campground/r/campgroundDetails.do?contractCode=NY&parkId=537"),  # Taylor Pond Campground
    13727: ("05-14", "09-05", "https://newyorkstateparks.reserveamerica.com/camping/rogers-rock-campground/r/campgroundDetails.do?contractCode=NY&parkId=515"),  # Rogers Rock Campground
    13728: ("05-14", "09-11", "https://newyorkstateparks.reserveamerica.com/camping/luzerne/r/campgroundDetails.do?contractCode=NY&parkId=529"),  # Luzerne
}

URLS = {
    143: "https://newyorkstateparks.reserveamerica.com/camping/sampson-state-park/r/campgroundDetails.do?contractCode=NY&parkId=232",
    214: "https://newyorkstateparks.reserveamerica.com/camping/letchworth-state-park/r/campgroundDetails.do?contractCode=NY&parkId=375",
    310: "https://newyorkstateparks.reserveamerica.com/camping/robert-moses-state-park/r/campgroundDetails.do?contractCode=NY&parkId=427",
    311: "https://newyorkstateparks.reserveamerica.com/camping/coles-creek-state-park/r/campgroundDetails.do?contractCode=NY&parkId=361",
    312: "https://newyorkstateparks.reserveamerica.com/camping/keewaydin-state-park/r/campgroundDetails.do?contractCode=NY&parkId=456",
    313: "https://newyorkstateparks.reserveamerica.com/camping/kring-point-state-park/r/campgroundDetails.do?contractCode=NY&parkId=459",
    314: "https://newyorkstateparks.reserveamerica.com/camping/jacques-cartier-state-park/r/campgroundDetails.do?contractCode=NY&parkId=452",
    316: "https://newyorkstateparks.reserveamerica.com/camping/wellesley-island-state-park/r/campgroundDetails.do?contractCode=NY&parkId=240",
    317: "https://newyorkstateparks.reserveamerica.com/camping/grass-point-state-park/r/campgroundDetails.do?contractCode=NY&parkId=447",
    318: "https://newyorkstateparks.reserveamerica.com/camping/southwick-beach-state-park/r/campgroundDetails.do?contractCode=NY&parkId=474",
    319: "https://newyorkstateparks.reserveamerica.com/camping/fair-haven-beach-state-park/r/campgroundDetails.do?contractCode=NY&parkId=175",
    321: "https://newyorkstateparks.reserveamerica.com/camping/four-mile-creek-state-park/r/campgroundDetails.do?contractCode=NY&parkId=336",
    322: "https://newyorkstateparks.reserveamerica.com/campgroundDetails.do?contractCode=NY&parkId=302#sr_a",
    323: "https://newyorkstateparks.reserveamerica.com/camping/macomb-reservation/r/campgroundDetails.do?contractCode=NY&parkId=433",
    324: "https://newyorkstateparks.reserveamerica.com/camping/bowman-lake-state-park/r/campgroundDetails.do?contractCode=NY&parkId=19",
    325: "https://newyorkstateparks.reserveamerica.com/camping/selkirk-shores-state-park/r/campgroundDetails.do?contractCode=NY&parkId=82",
    326: "https://newyorkstateparks.reserveamerica.com/camping/oquaga-creek-state-park/r/campgroundDetails.do?contractCode=NY&parkId=72",
    327: "https://newyorkstateparks.reserveamerica.com/camping/gilbert-lake-state-park/r/campgroundDetails.do?contractCode=NY&parkId=64",
    328: "https://newyorkstateparks.reserveamerica.com/camping/glimmerglass-state-park/r/campgroundDetails.do?contractCode=NY&parkId=78",
    329: "https://newyorkstateparks.reserveamerica.com/camping/delta-lake-state-park/r/campgroundDetails.do?contractCode=NY&parkId=56",
    330: "https://newyorkstateparks.reserveamerica.com/camping/chenango-valley-state-park/r/campgroundDetails.do?contractCode=NY&parkId=44",
    331: "https://newyorkstateparks.reserveamerica.com/camping/green-lakes-state-park/r/campgroundDetails.do?contractCode=NY&parkId=165",
    332: "https://newyorkstateparks.reserveamerica.com/camping/lake-erie-state-park/r/campgroundDetails.do?contractCode=NY&parkId=368",
    333: "https://newyorkstateparks.reserveamerica.com/camping/verona-beach-state-park/r/campgroundDetails.do?contractCode=NY&parkId=170",
    335: "https://newyorkstateparks.reserveamerica.com/camping/cedar-point-state-park/r/campgroundDetails.do?contractCode=NY&parkId=347",
    336: "https://newyorkstateparks.reserveamerica.com/camping/burnham-point-state-park/r/campgroundDetails.do?contractCode=NY&parkId=343",
    338: "https://newyorkstateparks.reserveamerica.com/camping/westcott-beach-state-park/r/campgroundDetails.do?contractCode=NY&parkId=468",
    339: "https://newyorkstateparks.reserveamerica.com/camping/lakeside-state-park/r/campgroundDetails.do?contractCode=NY&parkId=280",
    340: "https://newyorkstateparks.reserveamerica.com/camping/golden-hill-state-park/r/campgroundDetails.do?contractCode=NY&parkId=317",
    349: "https://newyorkstateparks.reserveamerica.com/camping/cumberland-bay-state-park/r/campgroundDetails.do?contractCode=NY&parkId=439",
    466: "https://newyorkstateparks.reserveamerica.com/camping/clarence-fahnestock-state-park/r/campgroundDetails.do?contractCode=NY&parkId=409",
    641: "https://newyorkstateparks.reserveamerica.com/camping/wildwood-state-park/r/campgroundDetails.do?contractCode=NY&parkId=288",
    1391: "https://newyorkstateparks.reserveamerica.com/camping/watkins-glen-state-park/r/campgroundDetails.do?contractCode=NY&parkId=254",
    1392: "https://newyorkstateparks.reserveamerica.com/camping/allegany-state-park/r/campgroundDetails.do?contractCode=NY&parkId=31",
    1394: "https://newyorkstateparks.reserveamerica.com/camping/keuka-lake-state-park/r/campgroundDetails.do?contractCode=NY&parkId=228",
    1395: "https://newyorkstateparks.reserveamerica.com/camping/taughannock-falls-state-park/r/campgroundDetails.do?contractCode=NY&parkId=218",
    1397: "https://newyorkstateparks.reserveamerica.com/camping/allegany-state-park/r/campgroundDetails.do?contractCode=NY&parkId=31",
    1399: "https://newyorkstateparks.reserveamerica.com/camping/schodack-island-state-park/r/campgroundDetails.do?contractCode=NY&parkId=4335",
    1400: "https://newyorkstateparks.reserveamerica.com/camping/thompsons-lake-campground-at-thacher-state-park/r/campgroundDetails.do?contractCode=NY&parkId=322",
    1401: "https://newyorkstateparks.reserveamerica.com/camping/taconic-state-park-copake-falls/r/campgroundDetails.do?contractCode=NY&parkId=410",
    1404: "https://newyorkstateparks.reserveamerica.com/camping/darien-lakes-state-park/r/campgroundDetails.do?contractCode=NY&parkId=386",
    1405: "https://newyorkstateparks.reserveamerica.com/camping/long-point-state-park--thousand-islands/r/campgroundDetails.do?contractCode=NY&parkId=484",
    1406: "https://newyorkstateparks.reserveamerica.com/camping/moreau-lake-state-park/r/campgroundDetails.do?contractCode=NY&parkId=311",
    1408: "https://newyorkstateparks.reserveamerica.com/camping/higley-flow-state-park/r/campgroundDetails.do?contractCode=NY&parkId=420",
    1411: "https://newyorkstateparks.reserveamerica.com/camping/stony-brook-state-park/r/campgroundDetails.do?contractCode=NY&parkId=261",
    1412: "https://newyorkstateparks.reserveamerica.com/camping/max-v-shaul-state-park/r/campgroundDetails.do?contractCode=NY&parkId=308",
    1414: "https://newyorkstateparks.reserveamerica.com/camping/cayuga-lake-state-park/r/campgroundDetails.do?contractCode=NY&parkId=210",
    1418: "https://newyorkstateparks.reserveamerica.com/camping/beaver-pond-state-park/r/campgroundDetails.do?contractCode=NY&parkId=392",
    1420: "https://newyorkstateparks.reserveamerica.com/camping/newtown-battlefield-state-park/r/campgroundDetails.do?contractCode=NY&parkId=1835",
    1428: "https://newyorkstateparks.reserveamerica.com/camping/heckscher-state-park/r/campgroundDetails.do?contractCode=NY&parkId=277",
}

# id: (opens, closes, note or None) from the page's 2027 campsite dates.
STATE = {
    1391: ("05-07", "10-10", "The Cayuga and Mohawk loops open May 7; the rest of the campground May 14."),
    1392: ("05-21", "10-30", None),
    1394: ("05-14", "10-10", None),
    1395: ("05-14", "10-10", None),
    1397: ("05-21", "10-30", None),
    1399: ("05-07", "11-14", "Creekside Loop and the overflow sites May 7 - Nov 14; Riverside Loop May 7 - Oct 10."),
    1400: ("04-30", "10-10", "Loop A Apr 30 - Oct 10; Loop B May 29 - Sep 5."),
    1401: ("05-07", "11-13", None),
    1404: ("05-21", "10-10", None),
    1405: ("05-14", "09-05", None),
    1406: ("05-17", "10-31", "Loops A-E May 17 - Oct 31; Loops F and G May 17 - Sep 5."),
    1408: ("05-21", "09-05", None),
    1411: ("05-14", "10-10", None),
    1412: ("05-28", "10-10", None),
    1414: ("05-14", "10-11", "The park says some loops may open later or close earlier."),
    1418: ("04-16", "10-10", "Section A May 21 - Sep 5."),
    1420: ("05-21", "10-10", "The North Loop opens May 28."),
    1428: ("05-22", "09-06", "2026 dates; 2027's are not posted yet."),
    143: ("05-21", "10-10", None),
    214: ("05-21", "10-10", None),
    310: ("05-21", "10-10", "Barnhart Loop May 21 - Sep 5."),
    311: ("05-21", "09-11", None),
    312: ("05-28", "09-05", None),
    313: ("05-07", "10-10", None),
    314: ("05-21", "09-11", "Lower Loop May 21 - Sep 11; Upper Loop May 28 - Sep 5."),
    316: ("05-07", "10-10", "Areas D and F May 7 - Oct 10; Area E May 14 - Oct 10; Area C May 21 - Oct 10; Areas A and B May 21 - Sep 11; Area H May 7 - Oct 7."),
    317: ("05-21", "09-18", None),
    318: ("05-07", "10-10", None),
    319: ("05-14", "10-10", "Drumlin A closes Sep 5; Drumlin B, Bluff and Lakeview Oct 10."),
    321: ("05-07", "10-10", "The 300 Area closes Sep 5."),
    322: ("05-14", "10-11", None),
    323: ("05-28", "09-05", None),
    324: ("05-14", "09-05", None),
    325: ("05-14", "10-23", "Acorn and Bird loops to Oct 23; Chipmunk and Dragonfly loops to Oct 16."),
    326: ("05-14", "09-05", None),
    327: ("05-14", "10-10", "Sites 1-76 and 80-89 May 14 - Oct 10; the non-electric Deer Run sites (77-79, 90-135) close Sep 5."),
    328: ("05-14", "10-10", None),
    329: ("05-14", "10-10", None),
    330: ("05-14", "10-10", "Chipmunk 1-3 to Oct 10; Chipmunk 4, Pine Bluff and Sunrise to Sep 5."),
    331: ("05-14", "10-10", None),
    332: ("05-21", "10-10", None),
    333: ("05-28", "10-10", "The park says the spring weather may let the campground open in mid-May."),
    335: ("05-07", "10-10", None),
    336: ("05-28", "09-05", None),
    338: ("05-14", "10-10", "Most campsites close Sep 5; the Plateau Loop stays open to Oct 10."),
    339: ("05-21", "10-10", None),
    340: ("05-14", "10-10", None),
    349: ("05-21", "10-10", "100, 200 and 300 loops May 21 - Oct 10; 400 Loop May 28 - Sep 5."),
    466: ("05-07", "11-13", "Sites 1-28 May 7 - Nov 13; sites 29-79 May 7 - Oct 16."),
    641: ("04-16", "10-10", "Loops T, B and D open Apr 16; loops A, C and E May 28."),
}

DECISIONS = {}
for i, (o, c, url) in DEC.items():
    season = {"year_round": False, "opens": o}
    if c > "09-06":
        season["closes"] = c
    else:
        season["note"] = "Reservable through Sep 5, 2027 (Labor Day weekend); DEC posts no later date."
    DECISIONS[i] = (season, f"{url} (2027 season schedule), {READ}")
for i, (o, c, note) in STATE.items():
    season = {"year_round": False, "opens": o, "closes": c}
    if note:
        season["note"] = note
    what = "2027 season schedule" if i == 332 else "Season Dates: campsites"
    DECISIONS[i] = (season, f"{URLS[i]} ({what}), {READ}")

if __name__ == "__main__":
    run(DECISIONS)
