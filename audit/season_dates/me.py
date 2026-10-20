#!/usr/bin/env python3
"""Maine State Parks: campground closing date from the Off Season & Winter Camping page
(read 2026-10-20).

    python3 -I audit/season_dates/me.py [--apply]

"Camping season ends for the year for: ... Campground closes at noon on October 15." The page
and the park pages give no opening date, so only `closes` is written. The December-March winter
camping it describes is primitive walk-in tent camping, not a season for an RV.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SRC = "https://www.maine.gov/dacf/parks/camping/off-season-camping.shtml"
PARKS = {15: "Lily Bay", 16: "Cobscook Bay", 17: "Sebago Lake", 210: "Camden Hills", 613: "Bradbury Mountain", 4177: "Aroostook"}

if __name__ == "__main__":
    run({i: ({"year_round": False, "closes": "10-15", "note": "Campground closes at noon on October 15."},
             f"{SRC} (\"Camping season ends for the year for: ... {p} State Park: Campground closes at noon on October 15.\"), read 2026-10-20")
         for i, p in PARKS.items()})
