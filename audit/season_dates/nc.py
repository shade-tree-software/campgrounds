#!/usr/bin/env python3
"""North Carolina State Parks: the 2026 "Operating Season Schedule" on each park's ncparks.gov
home page (read 2026-10-20).

    python3 -I audit/season_dates/nc.py [--apply]

Only Jordan Lake and Falls Lake publish a schedule table with campground dates; both entries
stand for several campgrounds, so the widest span applies and the note names the year-round one.
Other NC park pages state no camping season (Stone Mountain's says only that tents-only Loop A
closes November-February), so they are left unset.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

P = "https://www.ncparks.gov/state-parks/{}"
D = {
    146: ({"year_round": True, "note": "Crosswinds Campground is open all year; the other campgrounds open in March or April and close between September and November."},
          P.format("jordan-lake-state-recreation-area") + " (Operating Season Schedule 2026: \"Crosswinds Campground ... Camping areas A to C | Jan. 1, 2026 | Dec. 31, 2026\"), read 2026-10-20"),
    258: ({"year_round": True, "note": "Rolling View's Loop A is open all year; its Loops B and C, Holly Point and B.W. Wells are seasonal and partly closed for construction in 2026."},
          P.format("falls-lake-state-recreation-area") + " (Operating Season Schedule 2026: \"Rolling View Access ... Campground Loop A | Open year-round\"), read 2026-10-20"),
}

if __name__ == "__main__":
    run(D)
