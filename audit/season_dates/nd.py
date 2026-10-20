#!/usr/bin/env python3
"""North Dakota state park campgrounds: year-round, from NDPRD's "Limited Service Season" page
(read 2026-10-20).

    python3 -I audit/season_dates/nd.py [--apply]

"While North Dakota state park campgrounds are open year-round, the department shifts to limited
services fall through the spring." The page's per-park shut-off dates are marked tentative and
change yearly, so each note gives the month rather than the day. Little Missouri (closes Nov 1)
is not in the database; Strawberry Lake (5900) is a state forest campground and is left out.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SRC = "https://www.parkrec.nd.gov/limited-service-season"
Q = ("While North Dakota state park campgrounds are open year-round, the department shifts to limited services "
     "fall through the spring. The availability of services is weather and staffing-dependent.")
BASE = "Limited services fall through spring."
N = {
    5880: "Campground water and the comfort station close in mid-October.",
    5881: "Full-service season ends Sept 30; campsite water is off from Oct 1.",
    5882: "The comfort station closes and water is off from early October.",
    5883: "",
    5884: "The dump station and water close in early October.",
    5885: "Campground water is shut off in early October.",
    5886: "Campground winterization begins in early October.",
    5887: "Water is off in the West, South and North loops from early October; the Primitive Loop has water year-round.",
    5888: "The Washegum comfort station closes and water is off from early October.",
    5890: "Comfort and dump stations close and modern-campground water is off from Oct 1.",
    5893: "",
    5894: "Water is off from Nov 1 and the vault toilet closes Dec 1.",
    13958: "",
}

if __name__ == "__main__":
    run({i: ({"year_round": True, "note": f"{BASE} {n}".strip()}, f"{SRC} (\"{Q}\"), read 2026-10-20") for i, n in N.items()})
