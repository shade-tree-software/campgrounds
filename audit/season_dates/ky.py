#!/usr/bin/env python3
"""Kentucky State Parks: the official year-round campground list and the current campground
closures (parks.ky.gov, read 2026-10-20).

    python3 -I audit/season_dates/ky.py [--apply]

Year-round: Carter Caves ("begins 2026 winter season") and Lake Cumberland; the list warns that
water can't be guaranteed in freezing weather. Kentucky publishes no end date for the ordinary
season (2026 opened March 13), so the other campgrounds are left unset.

Closed for renovation per parks.ky.gov/park-closures: My Old Kentucky Home, Kenlake, Fort
Boonesborough (reopening mid-2027) and Jenny Wiley (April 2027). Green River Lake is open to
primitive and self-contained units only, and Nolin Lake is no longer listed, so neither is marked.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

YR = "https://parks.ky.gov/year-round-campgrounds"
CL = "https://parks.ky.gov/park-closures"
NOTE = "Water is not guaranteed in freezing weather; call the park."
D = {
    1538: ({"year_round": True, "note": "Year-round from the 2026 winter season. " + NOTE},
           f"{YR} (\"Year Round Campgrounds: Carter Caves State Resort Park (begins 2026 winter season)\"), read 2026-10-20"),
    1553: ({"year_round": True, "note": NOTE}, f"{YR} (\"Year Round Campgrounds: ... Lake Cumberland State resort Park\"), read 2026-10-20"),
}


def closed(reopens, quote):
    return {"status": {"operating": "temporarily_closed", "reopens": reopens,
                       "note": f"Campground closed for renovations and repairs (upgraded electric, water connections, parking pads); \"{quote}\" (parks.ky.gov, read 2026-10-20)."},
            "_sources": {"status": f"{CL} (\"{quote}\"), read 2026-10-20"}}


EXTRA = {
    1545: closed("not announced", "My Old Kentucky Home State Park campground opening date TBD"),
    1552: closed("not announced", "Kenlake State Resort Park campground reopening TBD"),
    1554: closed("mid-2027", "Fort Boonesborough State Park campground reopening mid-2027"),
    1555: closed("April 2027", "Jenny Wiley State Resort Park campground reopening April 2027"),
}

if __name__ == "__main__":
    run(D, EXTRA)
