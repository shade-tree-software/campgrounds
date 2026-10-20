#!/usr/bin/env python3
"""Idaho state parks whose own page states a camping season (parksandrecreation.idaho.gov, read
2026-10-20).

    python3 -I audit/season_dates/id.py [--apply]

Most Idaho park pages give only day-use hours and water status; only these two say the
campground stays open. Lake Walcott's campground will close for a water-system project from
fall 2026 but the page gives no dates yet, so it is not marked.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

P = "https://parksandrecreation.idaho.gov/state-park/{}/"
D = {
    9709: ({"year_round": True, "note": "Mountain Fawn Campground; potable water is off in the off season and reservations are required."},
           P.format("bear-lake-state-park") + " (\"Potable water has been turned OFF for the season at the Mountain Fawn Campground. Sites are available year round, Reservations are required.\"), read 2026-10-20"),
    9720: ({"year_round": True, "note": "Wagon Wheel Campground is reservable all year."},
           P.format("three-island-crossing-state-park") + " (\"Wagon Wheel Campground is reservable all year long.\"), read 2026-10-20"),
}

if __name__ == "__main__":
    run(D)
