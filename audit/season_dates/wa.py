#!/usr/bin/env python3
"""Washington State Parks closures from the agency's Winter Schedule and park pages (read
2026-10-20).

    python3 -I audit/season_dates/wa.py [--apply]

Larrabee's campground is closed Sept 15, 2026 to June 15, 2027 for water-line replacement.
Saltwater's campground is closed indefinitely (flood and erosion projects; the agency is
"reevaluat[ing] camping within the park"). No season is written: the schedule gives closures
only, and Osborn Bay (Steamboat Rock) is not among its rows. The DNR campgrounds are not covered.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

WS = "https://parks.wa.gov/find-activities/winter-schedule"
SW = "https://parks.wa.gov/find-parks/state-parks/saltwater-state-park"
EXTRA = {
    10442: {"status": {"operating": "temporarily_closed", "reopens": "June 15, 2027",
                       "note": "Campground closed Sept 15, 2026 to June 15, 2027 while water lines are replaced through the park (Washington State Parks winter schedule, read 2026-10-20)."},
            "_sources": {"status": f"{WS} (Larrabee: \"The Campground will be closed from Sept. 15, 2026 to June 15, 2027 due to water lines being replaced through the park.\"), read 2026-10-20"}},
    14065: {"status": {"operating": "temporarily_closed", "reopens": "not announced",
                       "note": "Campground closed for flood and erosion projects while the agency reevaluates camping in the park (park page, read 2026-10-20)."},
            "_sources": {"status": f"{SW} (\"While the campground is closed, we are taking this opportunity to reevaluate camping within the park.\"), read 2026-10-20"}},
}

if __name__ == "__main__":
    run({}, EXTRA)
