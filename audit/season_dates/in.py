#!/usr/bin/env python3
"""Indiana state parks and recreation areas: year-round from DNR's "Winter Camping at Indiana
State Parks" page (2025-26 winter season, read 2026-10-20), plus Morgan-Monroe State Forest.

    python3 -I audit/season_dates/in.py [--apply]

The page opens "Camping is available year-round at Indiana State Parks" and gives each property's
winter line; in winter most properties cut back to one or two loops, water may be a single
source, and most dump stations close, which every entry's note says.

Not written: Quakertown SRA (Brookville Lake's winter line covers only Mounds SRA) and the state
forests whose pages give no season. Charlestown's Nov 7, 2025 - Mar 1, 2026 paving closure is
over. Morgan-Monroe: "Mason Ridge Campground is open year-round."
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

WINTER = "https://www.in.gov/dnr/state-parks/publications-and-brochures/winter-camping/"
BASE = "In winter only one or two loops stay open, water may be a single source, and most dump stations close."
# id: (property line on the page, extra note)
P = {
    283: ("Monroe Lake", ""), 563: ("Pokagon", "Campground 3 stays open all winter."),
    565: ("Indiana Dunes", ""), 792: ("Patoka Lake", ""), 800: ("Mississinewa Lake", ""),
    1064: ("Brown County", "In winter only Buffalo Ridge campground has a comfort station and water."),
    1065: ("Chain O'Lakes", ""), 1066: ("Charlestown", ""), 1067: ("Clifty Falls", ""),
    1068: ("Harmonie", ""), 1069: ("Lincoln", ""), 1070: ("Mounds", ""), 1071: ("O'Bannon Woods", ""),
    1072: ("Ouabache", "Loop A (sites 1-75) closes November through January for the Wonderland of Lights."),
    1073: ("Potato Creek", ""), 1074: ("Prophetstown", ""), 1076: ("Spring Mill", ""),
    1077: ("Summit Lake", ""), 1078: ("Tippecanoe River", ""), 1079: ("Turkey Run", ""),
    1080: ("Versailles", ""), 1081: ("Whitewater Memorial", ""), 1082: ("Brookville Lake (Mounds SRA)", ""),
    1084: ("Lieber SRA (Cagles Mill Lake)", ""), 1085: ("Raccoon SRA (Cecil M. Harden Lake)", ""),
    1086: ("Hardy Lake", ""), 1087: ("Salamonie Lake", ""), 1088: ("Deam Lake SRA", ""),
    1089: ("Starve Hollow SRA", ""), 13405: ("Shakamak", ""),
}

D = {i: ({"year_round": True, "note": f"{BASE} {extra}".strip()},
         f"{WINTER} (2025-26 winter season: \"Camping is available year-round at Indiana State Parks\"; {line} listed), read 2026-10-20")
     for i, (line, extra) in P.items()}
D[1095] = ({"year_round": True, "note": "Water is shut off Oct 31 until March; a year-round hydrant is southeast of the forest office."},
           "https://www.in.gov/dnr/forestry/properties/morgan-monroe-state-forest/ (\"Mason Ridge Campground is open year-round.\"), read 2026-10-20")

if __name__ == "__main__":
    run(D)
