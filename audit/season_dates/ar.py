#!/usr/bin/env python3
"""Arkansas State Parks: season from each park page's hours list on arkansasstateparks.com
(read 2026-10-20), whose "Campground/Picnic Area" line reads "Open all year" at 25 parks.

    python3 -I audit/season_dates/ar.py [--apply]

The water / restroom months the same list gives go in the note. Not written: Woolly Hollow,
Daisy and Lake Sylvia, whose pages give no campground hours.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

# id: (quote from the hours list, note or "")
Q = {
    5126: ("Campground/Picnic Area: Open all year. Bathhouses are open all year. Restrooms are open from March - November", ""),
    5127: ("Campground / Picnic Area: Open all year", ""),
    5128: ("Campground/Picnic Area: Open all year", ""),
    5129: ("Campground/Picnic Area: Open all year. Restrooms are open March - December", "Restrooms open March - December."),
    5130: ("Campground/Picnic Area: Open all year. All Campground bathhouses are open year-round", ""),
    5131: ("Campground/Picnic Area: Open all year. Restrooms are open all year", ""),
    5132: ("Campground / Picnic Area: Open all year", ""),
    5133: ("Campground/Picnic Area: Open all year. Bathhouses are open from March - November", "Bathhouses open March - November."),
    5134: ("Campground/Picnic Area: Open all year", ""),
    5135: ("Campground/Picnic Area: Open all year. Restrooms are open March - November", "Restrooms open March - November."),
    5136: ("Campgrounds: Open all year. No water December, January, & February", "No water December - February."),
    5137: ("Campground/Picnic Area Open all year. Restrooms are open year-round", ""),
    5138: ("Campground / Picnic Area: Open Year-Round. Restrooms Open Year-Round", ""),
    5140: ("Campground / Picnic Area: Open all year. Restrooms open March 1 - Nov. 30. NOTE: No water is available at campsites Dec., Jan. & Feb.",
           "Restrooms open March 1 - November 30; no water at campsites December - February."),
    5141: ("Campground/Picnic Area: Open all year", ""),
    5142: ("Campground/Picnic Area: Open all year. Restrooms are open year-round", ""),
    5144: ("Campground/Picnic Area: Open all year. Restrooms are open all year", ""),
    5145: ("Campground/Picnic Area: Open all year", ""),
    5146: ("Campground/Picnic Area: Open all year", ""),
    5147: ("Campground/Picnic Area: Open all year. Restrooms open March-November", "Restrooms open March - November."),
    5149: ("Campground/ Picnic Area: Open all year", ""),
    5150: ("Campground/Picnic Area: Open all year", ""),
    5151: ("Campground/Picnic Area: Open year-round. Bathhouse open year-round", ""),
    5152: ("Campground Open all year", ""),
    5153: ("Campground/Picnic Area: Open all year", ""),
    5154: ("Campground/Picnic Area: Open all year", ""),
}

if __name__ == "__main__":
    cg = {e["id"]: e for e in json.load(open(CG, encoding="utf-8"))}
    D = {}
    for i, (quote, note) in Q.items():
        season = {"year_round": True, **({"note": note} if note else {})}
        D[i] = (season, f"{cg[i]['website'].split()[0]} (hours: \"{quote}\"), read 2026-10-20")
    run(D)
