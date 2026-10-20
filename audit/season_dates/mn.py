#!/usr/bin/env python3
"""Minnesota State Parks: season from each park's "Seasonal update" (2026-10-20).

    python3 -I audit/season_dates/mn.py [--apply]

The park pages on dnr.state.mn.us render a "Seasonal update" (campgrounds, electric sites)
from the DNR's own feature service
(maps.dnr.state.mn.us/cgi-bin/compass/feature_detail.cgi?id=<park id>), read 2026-10-20.
It's this year's operating news, so a park gets a season only where it states one: winter
camping or plowed sites (year-round), or this year's dates. Where only one edge is posted
the other is left out. Holiday-anchored edges take the widest date (common.py).

Not written: parks whose update gives no dates (Lake Carlos, Lake Shetek "until the first
significant snowfall", Lake Bronson (construction), Monson Lake, Moose Lake, Nerstrand,
Savanna Portage, Lake Vermilion), Lake Beatrice (only "closed for the season"), and the 39
state-forest and ReserveMN-linked entries, whose pages carry no update.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SRC = "https://www.dnr.state.mn.us/state_parks/park.html?id={} ('Seasonal update': {}), read 2026-10-20"
YR = {"year_round": True}

DECISIONS = {
    5371: ({"year_round": False, "opens": "04-20", "note": "Approximate: the DNR says it reopens late April 2027, weather permitting."},
           SRC.format("spk00136", "Campgrounds")),
    5375: ({"year_round": False, "closes": "11-30", "note": "2026: electric sites April 10 - October 18; rustic non-electric sites through November 30."},
           SRC.format("spk00148", "Campgrounds, Electric sites")),
    5405: (dict(YR, note="In winter, several electric sites in Big Island campground; call to check they're accessible."),
           SRC.format("spk00175", "Campgrounds")),
    5394: ({"year_round": False, "opens": "05-22", "closes": "10-18", "note": "Approximate: the DNR says Memorial Day weekend through October 18, 2026."},
           SRC.format("spk00214", "Campgrounds")),
    5399: ({"year_round": False, "closes": "10-20", "note": "2026: closes for the season October 20."},
           SRC.format("spk00226", "Campgrounds")),
    5397: (dict(YR, note="Electric sites 13-19 are reservable year-round."), SRC.format("spk00229", "Electric sites")),
    5400: (dict(YR, note="In winter, three plowed pull-through sites (41, 43, 46)."), SRC.format("spk00232", "Electric sites")),
    5401: (dict(YR, note="In winter, B-loop sites including 30-amp electric."), SRC.format("spk00235", "Campgrounds")),
    5407: ({"year_round": False, "opens": "05-22", "closes": "10-21", "note": "Approximate: the DNR says Memorial weekend through MEA weekend in mid-October."},
           SRC.format("spk00247", "Campgrounds")),
    5408: (dict(YR, note="Camping, including electric sites, is available year-round."), SRC.format("spk00253", "Campgrounds")),
    5414: ({"year_round": False, "closes": "11-01", "note": "2026: Chase Point closes November 1, the Lodge campground September 7; water off from October 12."},
           SRC.format("spk00262", "Campgrounds")),
    5418: ({"year_round": False, "closes": "10-26", "note": "2026: tentative close date October 26, when the water is shut off."},
           SRC.format("spk00266", "Campgrounds")),
    5421: (dict(YR, note="In winter only a handful of drive-in sites are plowed (typically 4, 13, 14, 17, 22, 26, 31, 32)."),
           SRC.format("spk00269", "Campgrounds")),
    5425: ({"year_round": False, "closes": "11-03", "note": "2026: camping closes November 3."}, SRC.format("spk00284", "Campgrounds")),
}

if __name__ == "__main__":
    run(DECISIONS)
