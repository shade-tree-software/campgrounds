#!/usr/bin/env python3
"""West Virginia State Parks: season from each park page's "Campground Season And Dates" (2026-10-20).

    python3 -I audit/season_dates/wv.py [--apply]

Most wvstateparks.com pages answer "Spring through fall, weather permitting", which names no
month and is left unset. These five say year-round or give dates.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

R = "read 2026-10-20"
P = "https://wvstateparks.com/parks/{}/ (Campground Season And Dates: \"{}\"), " + R
DECISIONS = {
    715: ({"year_round": True}, P.format("beech-fork-state-park", "The campgrounds are open year-round")),
    870: ({"year_round": True, "note": "Weather permitting."},
          P.format("camp-creek-state-park-and-forest", "Camp Creek campgrounds are open year-round, weather permitting.")),
    872: ({"year_round": True}, P.format("twin-falls-resort-state-park", "The campground is open year-round.")),
    877: ({"year_round": True, "note": "Weather permitting."},
          P.format("panther-state-forest", "The campground is open year-round, weather permitting.")),
    873: ({"year_round": False, "opens": "04-01", "closes": "10-31",
           "note": "Some camping is available in November by calling the park (304-722-3450), as a courtesy to hunters."},
          P.format("moncove-lake-state-park", "Camping is available April 1st through end of October.")),
}

if __name__ == "__main__":
    run(DECISIONS)
