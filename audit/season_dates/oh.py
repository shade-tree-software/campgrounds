#!/usr/bin/env python3
"""Ohio State Parks: the three park pages that say the campground stays open in winter (2026-10-20).

    python3 -I audit/season_dates/oh.py [--apply]

ohiodnr.gov's park pages rarely state a camping season, and ODNR's camping pages have no
statewide statement. Grand Lake St Marys gives an off-peak season (Nov 1 - Apr 1, first loop);
Mohican and Rocky Fork describe a "winter camping season". The other 52 Ohio state entries
are left unknown; Jackson Lake says only "open seasonally".
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

P = "https://ohiodnr.gov/go-and-do/plan-a-visit/find-a-property/{} ({}), read 2026-10-20"
WINTER = "In the winter camping season facilities may be limited, and full-service sites have no water at the site."

DECISIONS = {
    1000: ({"year_round": True, "note": "Off-peak season November 1 to April 1: electric in the first loop, dump station open, water hydrant near the main office."},
           P.format("grand-lake-st-marys-state-park", "'Off-Peak Season'")),
    186: ({"year_round": True, "note": WINTER}, P.format("mohican-state-park", "'Overnight Options'")),
    1023: ({"year_round": True, "note": WINTER}, P.format("rocky-fork-state-park", "'Camping'")),
}

if __name__ == "__main__":
    run(DECISIONS)
