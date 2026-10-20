#!/usr/bin/env python3
"""Wyoming and Nevada state parks: year-round where the park page says camping (or the
campground) is open all year (read 2026-10-20).

    python3 -I audit/season_dates/wy_nv.py [--apply]

Only a statement about camping counts. A page that gives only park hours ("Open seven days a
week, 365 days a year", "Park grounds are open year-round") is not read as a campground season,
so most Nevada parks, Boysen, Medicine Lodge and Hawk Springs are left unset, as is Buffalo Bill's
North Fork, which the park's winter notice lists as closed.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

GLENDO = "The park is open year-round for day use and camping."
Q = {
    6350: ("Park is open 365 days, 24hrs (with camping permit)", "No dump station in the park; potable water stays on at the visitor center year-round."),
    6351: ("Our site is open year-round. Camping reservation season is May 15th - September 15th. All campsites are first come, first served outside of this time period.",
           "Reservable May 15 - September 15; first-come the rest of the year."),
    6352: (GLENDO, ""), 13968: (GLENDO, ""), 13969: (GLENDO, ""), 13976: (GLENDO, ""), 13977: (GLENDO, ""),
    6353: ("Electric Sites Available During Winter Season at: Skyline, Sandy Beach and Sandy Point Campgrounds", ""),
    6359: ("Sites 12 and 15 in the Popo Agie Campground are first come first-served year round.", "In winter only Popo Agie sites 12 and 15 stay open (first-come)."),
    6360: ("Park is open 24/7 - 365 days a year. Fee kiosks at each entrance for day use and winter camping", ""),
    6369: ("Open year round. Access Year Round on the Public Access Area. Camping in designated areas only.", ""),
    11199: ("Silver Springs Beach #7 offers developed campground facilities open year-round", "Silver Springs Beach #7 is the year-round campground."),
    11210: ("Silver Springs Beach #7 offers developed campground facilities open year-round", ""),
    11200: ("Big Bend boasts a 24-unit campground that is accesible year-round.", ""),
    11203: ("The campground is open year round and available by reservation.", ""),
    11205: ("Park Hours: Open seven days a week, 365 days a year. The park is open from sunrise to sunset unless camping in campgrounds or a group camping area.", ""),
}

if __name__ == "__main__":
    cg = {e["id"]: e for e in json.load(open(CG, encoding="utf-8"))}
    D = {i: ({"year_round": True, **({"note": n} if n else {})},
             f"{cg[i]['website'].split()[0]} (\"{q}\"), read 2026-10-20") for i, (q, n) in Q.items()}
    run(D)
