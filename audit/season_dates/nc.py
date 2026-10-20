#!/usr/bin/env python3
"""North Carolina State Parks: season from each park's "Operating Season Schedule 2026" (2026-10-20).

    python3 -I audit/season_dates/nc.py [--apply]

ncparks.gov/state-parks/<park> carries a per-campground, per-loop opens/closes table for the
year; most parks have none and say nothing. Kerr Lake's 2026 table has three campgrounds
"closed for the season" from August 1 for improvements, so their usual closing date is not
on it; the note says so rather than writing August as the season's end.

Three campgrounds are temporarily closed (status), from the parks' home-page alerts:
Hanging Rock (10-12 months of construction), Merchants Millpond (until further notice),
Pettigrew (renovation through 2026).

Not written: Jordan Lake 146 and Falls Lake 258 (several campgrounds each, and the pin
does not settle which; Falls Lake's 2026 schedule is mostly construction closures), and
every park whose pages give no campground season.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

PARK = "https://www.ncparks.gov/state-parks/{} ('Operating Season Schedule 2026' / alerts), read 2026-10-20"
KERR = PARK.format("kerr-lake-state-recreation-area")
EARLY = "Closed for the season from August 1, 2026 for campground and restroom improvements, so its usual closing date is not posted."

DECISIONS = {
    104: ({"year_round": False, "opens": "03-23", "closes": "10-25", "note": "2026: March 23 to October 25."}, KERR),
    103: ({"year_round": False, "opens": "03-23", "closes": "09-27", "note": "2026: March 23 to September 27."}, KERR),
    108: ({"year_round": False, "opens": "03-23", "closes": "09-27", "note": "2026: March 23 to September 27."}, KERR),
    105: ({"year_round": False, "opens": "03-23", "closes": "10-25", "note": "2026: March 23 to October 25."}, KERR),
    107: ({"year_round": False, "opens": "03-23", "note": "2026: most sites from March 23, sites 1-55 and Area 3 from May 18. " + EARLY}, KERR),
    102: ({"year_round": True, "note": "Area 3 (sites 51-61, 83-109) is open year-round with 24-hour gate access; in 2026 Area 1 opened March 23 and Area 4 May 18. All areas closed for the season from August 1, 2026 for campground and restroom improvements."}, KERR),
    106: ({"year_round": True, "note": "Area 1 (sites 1-41D, 80-104) is open year-round with 24-hour gate access; in 2026 Area 2 opened March 23 and Area 3 May 18. All areas closed for the season from August 1, 2026 for campground and restroom improvements."}, KERR),
    13970: ({"year_round": True}, PARK.format("william-b-umstead-state-park")),
}


def closed(slug, reopens, note):
    return {"status": {"operating": "temporarily_closed", "reopens": reopens, "note": note},
            "_sources": {"status": PARK.format(slug)}}


EXTRA = {
    4209: closed("hanging-rock-state-park", "not announced",
                 "Family campground closed about 10-12 months for two new shower houses and campsite improvements (alert read 2026-10-20)."),
    13972: closed("merchants-millpond-state-park", "not announced",
                  "Family (tent and trailer) campground closed for construction until further notice (alert read 2026-10-20)."),
    13973: closed("pettigrew-state-park", "after 2026",
                  "Campgrounds and office closed for renovation; the park stays open for day use while the work runs through 2026 (alert read 2026-10-20)."),
    102: closed("kerr-lake-state-recreation-area", "2027 season",
                "Closed for the season from August 1, 2026 to improve the campground and restrooms; Area 3 is normally open year-round."),
    106: closed("kerr-lake-state-recreation-area", "2027 season",
                "Closed for the season from August 1, 2026 to improve the campground and restrooms; Area 1 is normally open year-round."),
    107: closed("kerr-lake-state-recreation-area", "2027 season",
                "Closed for the season from August 1, 2026 to improve the campground and restrooms."),
}

if __name__ == "__main__":
    run(DECISIONS, EXTRA)
