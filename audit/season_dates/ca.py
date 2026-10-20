#!/usr/bin/env python3
"""California State Parks: season where the park's own page states one (2026-10-20).

    python3 -I audit/season_dates/ca.py [--apply]

Each parks.ca.gov park page has a free-text "Park Hours" block. Most give day-use hours only
("Campgrounds are open 24 hours a day" is hours, not a season); these six say when camping is
open. The other state-park entries are left unset, among them Grizzly Creek ("Campground during
the summer only", no dates) and Castle Crags (first-come camping, no dates).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

R = "read 2026-10-20"
DECISIONS = {
    11654: ({"year_round": True, "note": "First-come, first-served November to April."},
            f"https://www.parks.ca.gov/?page_id=413 (Park Hours: \"Campground open all year. November-April First Come First Served\"), {R}"),
    11692: ({"year_round": False, "opens": "09-01", "closes": "06-30",
             "note": "Open Friday to Sunday and holiday Mondays, 8 a.m. - 5 p.m.; closed July and August, Christmas Day and New Year's Day."},
            f"https://www.parks.ca.gov/ProvidenceMountains (Park Hours: \"Open: September - June ... Closed: July & August\"), {R}"),
    11695: ({"year_round": True,
             "note": "Huckleberry and Madrone are reservable from a week before Memorial Day weekend; Huckleberry's last night is the Sunday of Labor Day weekend. Madrone stays open off-season (Sep 2 - May 24) as walk-in only with self-registration, cash or check."},
            f"https://www.parks.ca.gov/?page_id=422 (Park Hours), {R}"),
    11697: ({"year_round": True},
            f"https://www.parks.ca.gov/SaddlebackButte (Park Hours: \"Campground: 24 hours, Year-round\"), {R}"),
    11710: ({"year_round": True},
            f"https://www.parks.ca.gov/?page_id=423 (Park Hours: \"Campground open all year.\"), {R}"),
    11715: ({"year_round": False, "opens": "04-01", "closes": "09-30"},
            f"https://www.parks.ca.gov/?page_id=459 (Park Hours: \"Park open seasonally April 1 - September 30\"), {R}"),
}

if __name__ == "__main__":
    run(DECISIONS)
