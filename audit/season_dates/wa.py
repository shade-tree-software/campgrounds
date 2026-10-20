#!/usr/bin/env python3
"""Washington State Parks: season from the statewide Winter Schedule (2026-10-20).

    python3 -I audit/season_dates/wa.py [--apply]

parks.wa.gov/find-activities/winter-schedule is one table for every park: when the
campground closes and reopens for 2026-27, or "Open"/"Partial" with a list of the loops
that close. A park whose campground closes gets those dates. A park with any loop open
all winter is year-round, and the note names the loops that close. Where an entry is pinned
to one campground of a park (Deception Pass's Cranberry Lake loops, Fort Worden's Upper
Forest, Bowl and Pitcher, Jones Bay), it gets that campground's dates.

A "closed X - Y" range means the campground's last night is the day before X and its first
night is the day after Y. The note quotes the schedule wherever the dates need a caveat
("weather dependent").

Larrabee is closed Sept. 15, 2026 to June 15, 2027 for water-line work: status only, since
that is not its usual season. Saltwater's campground is closed while the park re-evaluates
camping: status only. Not written: Osborn Bay (14066), which the schedule doesn't mention.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SRC = "https://parks.wa.gov/find-activities/winter-schedule ({} row), read 2026-10-20"


def yr(note=None):
    return {"year_round": True, "note": note} if note else {"year_round": True}


def sea(opens, closes, note=None):
    d = {"year_round": False, "opens": opens, "closes": closes}
    if note:
        d["note"] = note
    return d


T = {  # id: (row name, season)
    294: ("Deception Pass", sea("03-01", "10-31", "Cranberry Lake's Lower Loop A is open March 1 to October 31; Lower Loop B and the Forest Loop close from October or November to March 31. Quarry Pond, at Cornet Bay, is open all year.")),
    10369: ("Cape Disappointment", yr("Water and sewer stay on all winter.")),
    10370: ("Seaquest", yr("Sites 32-54 and 57-76 are closed Oct. 1 - May 1. Water may be off in freezing weather Nov. 1 - April 1.")),
    10371: ("Paradise Point", yr("Sites 1-43 are open all year; the back loop and walk-in sites close Oct. 16 - April 14.")),
    10372: ("Battle Ground Lake", yr("Drive-in sites 1-34 are open all year with limited water.")),
    10373: ("Beacon Rock", yr("Woodard Creek Campground is open all year; the Upper Campground is closed Oct. 1 - March 31.")),
    10374: ("Maryhill", yr("Sites 51-71 are closed Oct. 31 - March 15, and the restrooms close in winter. Water is off Oct. 31 - April 1.")),
    10375: ("Brooks Memorial", sea("04-16", "10-31", "Campground closed Nov. 1 - April 15.")),
    10377: ("Lewis and Clark Trail", sea("04-01", "10-31", "Opening date weather dependent.")),
    10378: ("Fields Spring", yr("First come, first served Sept. 15 - May 15.")),
    10379: ("Grayland Beach", yr("Some sites may flood in winter.")),
    10380: ("Pacific Beach", yr()),
    10381: ("Ocean City", yr("Loops 2 and 3 are closed Oct. 1 - May 14.")),
    10382: ("Schafer", yr("Sites 15-18 are closed Oct. 1 - March 31; the east campground is first come, first served then. Water may be off in freezing weather.")),
    10383: ("Twin Harbors", yr("The Eastside loop and Westside sites 232-299 are closed from November to May 31 for seasonal flooding; the dump station closes November to April.")),
    10385: ("Ike Kinswa", yr("Loop B is open all year; Loops A and D from May to the end of September.")),
    10386: ("Millersylvania", yr("Sites 1-7 and 226-248 are open all year. Water is off about Nov. 1 - March 31, except at hookup sites.")),
    10387: ("Lewis and Clark", sea("05-01", "09-30", "Campground closed Oct. 1 - April 30.")),
    10389: ("Rainbow Falls", yr("Sites 33-38 are closed Sept. 15 - May 15.")),
    10392: ("Yakima Sportsman", sea("04-16", "09-30", "Campground closed Oct. 1 - April 15.")),
    10397: ("Wanapum Recreation Area", sea("03-01", "10-31", "Sites 1-31 open March 1 and sites 32-49 April 1.")),
    10398: ("Potholes", yr("Water is off Oct. 24 - April 1.")),
    10400: ("Bogachiel", yr("Sites 1-25 are open all year; sites 32-40 close Nov. 1 - March 31. Water is off Nov. 1 - March 31.")),
    10403: ("Dosewallips", yr("Sites 106-113 and 115-130 are closed Nov. 1 - March 31. Water is off Nov. 15 - March 31.")),
    10404: ("Dash Point", yr("The upper loop is closed Sept. 15 - May 15.")),
    10405: ("Fort Casey Historical", yr("Water is off November to March.")),
    10406: ("Belfair", yr("The Tree Loop is closed Sept. 15 - May 15.")),
    10407: ("Manchester", yr("Lower Loop sites 25-49 are closed Nov. 1 - March 31. Water is off Nov. 1 - March 1.")),
    10408: ("Fort Flagler Historical", yr("The upper campground is closed Oct. 1 - April 30. Water is off mid-November to March.")),
    10409: ("Fort Worden Historical", sea("03-16", "10-30", "Upper Forest loop closed Oct. 31 - March 15; the Beach Campground is open all year.")),
    10410: ("Kanaskat-Palmer", yr("Water is off November to April 1, weather dependent.")),
    10411: ("Sequim Bay", yr("Sites 5-25 are open all year; sites 65-86 close Sept. 16 - May 15.")),
    10414: ("Scenic Beach", yr("Upper Loop sites 26-50 are closed Nov. 1 - March 31.")),
    10415: ("Potlatch", yr("Sites 1-27 are open all year; sites 36-93 close Nov. 15 - March 31. No water and no dump station in the off-season.")),
    10416: ("Illahee", yr("Water is off Nov. 1 - March 1.")),
    10417: ("Fort Townsend Historical", sea("04-01", "09-30", "Campground closed Oct. 1 - March 31.")),
    10418: ("Jarrell Cove", yr()),
    10419: ("Twanoh", yr("The upper campground is closed Sept. 16 - May 15.")),
    10420: ("Camano Island", yr("The Lower Loop is open all year; the Upper Loop closes Sept. 30 - May 1.")),
    10421: ("Penrose Point", yr("Sites 1-22 are open all year; sites 23-51 May 15 - Oct. 1 and 53-83 May 15 - Sept. 15.")),
    10422: ("Wenatchee Confluence", yr("Loop 2 is open all year (first come, first served Oct. 16 - March 31); Loop 1 is closed from Oct. 16, 2026 until a construction project is finished.")),
    10423: ("Lincoln Rock", sea("04-03", "10-31", "Reservations through Oct. 31; first come, first served April 3 - 14.")),
    10426: ("Lake Chelan", yr("Trailer Loop sites 8-17 are open all year; the other loops April 15 to mid- or late September.")),
    10428: ("Twenty-Five Mile Creek", sea("04-01", "10-31", "Opening date weather dependent.")),
    10429: ("Steamboat Rock", yr("The Dune and Bay loops are open all year (first come, first served Nov. 1 - March 31); the Sage and Cove loops close Nov. 1 - March 31.")),
    10431: ("Sun Lakes-Dry Falls", yr("Sites 1-31 may close Oct. 31 - March 16, weather depending.")),
    10432: ("Bridgeport", yr("First come, first served Nov. 1 - April 30. Water may be off in winter.")),
    10433: ("Alta Lake", sea("04-15", "10-30", "Loops 1 and 3 close earlier, from Sept. 30 and Sept. 10.")),
    10437: ("Riverside", yr("Sites 15-33 are open all year; sites 1-14 April 1 - Oct. 15. Water and the dump station are off Oct. 15 to mid-April.")),
    10439: ("Bay View", yr("Sites 39-76 are closed Oct. 15 - May 15. Water is off Nov. 1 - April 1.")),
    10440: ("Rasar", yr("Water is off Nov. 1 - April 1.")),
    10441: ("Birch Bay", yr("Loop B is open all year; Loop A closes Sept. 16 - May 14.")),
    10443: ("Fort Ebey", sea("03-01", "10-31", "Campground closed Nov. 1 - Feb. 28.")),
    10444: ("Moran", yr("The Mountain Lake and Midway loops (sites 18-40) are open all year; the Northend, Southend and upper Midway loops close for the winter.")),
    10445: ("Spencer Spit", yr("Sites 1-42 are closed Nov. 1 - March 1; the walk-in sites stay open. Water and dump station off Nov. 1 - March 1.")),
    10446: ("Pearrygin Lake", sea("04-06", "10-30", "East campground closed Oct. 31 - April 5, the West campground Oct. 25 - April 20. Opening dates weather dependent.")),
    10447: ("Curlew Lake", sea("04-06", "10-24", "Most sites closed Oct. 25 - April 5 (sites 73-80 Sept. 30 - May 1); three sites stay open first come, first served Dec. 1 - March 15 with no utilities. Opening dates weather dependent.")),
    10448: ("Conconully", sea("04-06", "10-30", "Opening date weather dependent.")),
    14067: ("Steamboat Rock", sea("04-02", "09-30", "Jones Bay campground closed Oct. 1 - April 1.")),
}

DECISIONS = {i: (s, SRC.format(f"'{n} State Park'" if n != "Wanapum Recreation Area" else f"'{n}'"))
             for i, (n, s) in T.items()}


def closed(row, reopens, note):
    return {"status": {"operating": "temporarily_closed", "reopens": reopens, "note": note},
            "_sources": {"status": SRC.format(f"'{row} State Park'")}}


EXTRA = {
    10442: closed("Larrabee", "2027-06-15",
                  "Campground closed Sept. 15, 2026 to June 15, 2027 while water lines are replaced through the park."),
    14065: closed("Saltwater", "not announced",
                  "Campground and trailer dump closed after flood and erosion damage; State Parks is re-evaluating camping in the park."),
}

if __name__ == "__main__":
    run(DECISIONS, EXTRA)
