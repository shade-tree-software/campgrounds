#!/usr/bin/env python3
"""Illinois DNR: season where the park's camping page states one (2026-10-20).

    python3 -I audit/season_dates/il.py [--apply]

Each park has a camping page at dnr.illinois.gov/parks/camp/park.<name>.html. These seven say
when the campground is open; most of the rest only give shower-building dates, which are not the
campground's season, and are left unset.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

P = "https://dnr.illinois.gov/parks/camp/park.{}.html (\"{}\"), read 2026-10-20"
DECISIONS = {
    570: ({"year_round": False, "opens": "04-01", "closes": "11-15"},
          P.format("adelinejaygeo-karisillinoisbeach", "The campground is open from April 1 through Nov. 15.")),
    779: ({"year_round": True, "note": "Water and the shower buildings are shut off from the Monday before Thanksgiving through March 31."},
          P.format("sangchrislake", "Hickory Point and Deer Run are open all year.")),
    799: ({"year_round": True, "note": "Closed the full week before the first firearm deer season."},
          P.format("clintonlake", "The campground is open year-round with the exception of the full week prior to the first firearm deer season.")),
    1648: ({"year_round": False, "opens": "05-01", "closes": "10-31"},
           P.format("prophetstown", "The campground at Prophetstown is open from May 1st through October 31st annually.")),
    1678: ({"year_round": True, "note": "The West Loop is open all year; the East Loop closes from the weekend before Thanksgiving through April 1."},
           P.format("starvedrock", "The West Loop is open all year round, but the East Loop closes the weekend before Thanksgiving through April 1st.")),
    1681: ({"year_round": True, "note": "Reservable May 1 - Oct 31, first-come the rest of the year; water, showers and the dump station are winterized and closed Dec 15 - Mar 31, depending on weather."},
           P.format("kickapoo", "any camping outside of this timeframe will be on a first-come, first-served basis")),
    1687: ({"year_round": False, "opens": "04-15", "closes": "11-01"},
           P.format("jubileecollege", "Campground facilities, open from April 15 to November 1")),
}

if __name__ == "__main__":
    run(DECISIONS)
