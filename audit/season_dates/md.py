#!/usr/bin/env python3
"""Maryland state parks and forests: season from DNR's own pages (2026-10-20).

    python3 -I audit/season_dates/md.py [--apply]

Source of record is "Camping Seasons and Service Charges For Maryland State Parks
and Forests" (dnr.maryland.gov/publiclands/Pages/oc.aspx), one block per park, plus
the park's own page where that block gives no dates. Read with care: the "Dates:"
lines in that table belong to whatever facility they follow, and three that look like
camping seasons are not (Swallow Falls' "Year-round" is its shelter, Cunningham Falls'
Apr 3 - Oct 25 is the Manor Area shelter, Smallwood's "April to October" is its store).

Approximate edges follow common.py's convention, the agency's wording kept in the note.
Year-specific dates are written as the recurring MM-DD and the year is said in the note.

Not written, nothing on DNR's pages: Greenbrier 652, Susquehanna 827, Smallwood 826,
Swallow Falls 828, Patapsco Hollofield 824 (only a 2025 construction closure), and the
state-forest primitive sites (41-44, 64, 129), whose forest pages give no season.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

OC = "https://dnr.maryland.gov/publiclands/Pages/oc.aspx ('Camping Seasons and Service Charges For Maryland State Parks and Forests'), read 2026-10-20"
PARK = "https://dnr.maryland.gov/publiclands/Pages/{}.aspx, read 2026-10-20"

DECISIONS = {
    63: ({"year_round": True, "note": "Pines and White Oak loops year-round, with limited services off-season; Hemlock Loop closed permanently after October 1, 2024."}, OC),
    82: ({"year_round": False, "opens": "04-15", "closes": "12-15", "note": "Meadow Mountain campground: April 15 to December 15 every year."}, PARK.format("western/deepcreek")),
    87: ({"year_round": True}, OC),
    88: ({"year_round": True}, OC),
    423: ({"year_round": False, "opens": "03-20", "closes": "10-31", "note": "Approximate: DNR says late March through October."}, OC),
    424: ({"year_round": False, "opens": "03-20", "closes": "10-31", "note": "Approximate: DNR says late March through October."}, OC),
    533: ({"year_round": True, "note": "Self-contained rigs year-round; tent camping only from the first Saturday in May to the first Sunday in November. The campground closes during Market Fair in April (call 301-842-2155 for the dates)."}, OC),
    550: ({"year_round": False, "opens": "04-24", "closes": "10-31", "note": "Approximate opening: the campground is closed from November 1 through the third week of April and opens the last week of April."}, PARK.format("eastern/assateague")),
    648: ({"year_round": False, "opens": "03-13", "closes": "10-12", "note": "2026: Ash and Elm loops March 13 to October 12; the other loops May 1 to October 12."}, OC),
    650: ({"year_round": False, "opens": "04-01", "note": "Opens April 1; no closing date posted."}, OC),
    651: ({"year_round": False, "opens": "04-03", "closes": "10-25", "note": "First weekend in April to the last weekend in October (2026: April 3 to October 25), so the edges move a few days each year."}, PARK.format("western/gambrill") + " + " + OC),
    653: ({"year_round": False, "opens": "04-01", "closes": "10-31", "note": "Approximate: DNR says it opens at the beginning of April and closes at the end of October."}, PARK.format("western/cunningham")),
    654: ({"year_round": True}, PARK.format("western/cunningham")),
    659: ({"year_round": True, "note": "North East Loop year-round. 2026, during the cabin and bathhouse renovation: Miles Loop weekends only from April 3, Sassafras Loop only on holiday weekends Memorial Day to Labor Day; DNR's table lists the other loops as closed."}, PARK.format("central/elkneck") + " + " + OC),
    681: ({"year_round": True, "note": "Only four campsites stay open year-round."}, OC),
    825: ({"year_round": True}, PARK.format("eastern/pocomokeriver")),
    829: ({"year_round": False, "opens": "04-01", "closes": "12-15", "note": "Approximate: DNR says April to mid-December."}, PARK.format("eastern/pocomokeriver")),
    830: ({"year_round": False, "opens": "04-04", "closes": "10-26", "note": "2025: April 4 to October 26 (2024: April 5 to October 26); no 2026 dates posted."}, OC),
}

EXTRA = {
    648: {"status": {"operating": "temporarily_closed", "reopens": "2028",
                     "note": "Campground closed for renovation October 13, 2026 through December 31, 2027 (pads, amenities, accessibility, utilities)."},
          "_sources": {"status": PARK.format("western/rockygap")}},
}

if __name__ == "__main__":
    run(DECISIONS, EXTRA)
