#!/usr/bin/env python3
"""Pennsylvania state parks: season from each park's DCNR "Stay the Night" page (2026-10-20).

    python3 -I audit/season_dates/pa.py [--apply]

pa.gov/agencies/dcnr/recreation/where-to-go/state-parks/find-a-park/<park>/stay. The
park's main page only says "contact the park office for facility seasons"; the stay page
says it in a sentence or a "Season:" line. Its HTML is escaped twice, so a search that
unescapes once finds a third of them. Edges are mostly month-level ("mid-April through
mid-December") and follow common.py's approximation convention, wording in the note.

Two seasons hang on game seasons: Caledonia opens the day before trout season (the first
Saturday in April) and Colonel Denning on its opening day; both close with rifle deer
season in mid-December.

Nothing on the stay page: Locust Lake 305, Keystone 619, Clear Creek 729, Simon B. Elliott
866, Denton Hill 1061, Pine Grove Furnace 302 (only the store and group area). State-forest
sites are not here; their district pages are another source.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

URL = "https://www.pa.gov/agencies/dcnr/recreation/where-to-go/state-parks/find-a-park/{}-state-park/stay, read 2026-10-20"


def s(opens, closes, wording, extra=""):
    return {"year_round": False, "opens": opens, "closes": closes,
            "note": f"Approximate: DCNR says {wording}.{(' ' + extra) if extra else ''}"}


MID_APR_MID_OCT = ("04-15", "10-15", "mid-April through mid-October")
MID_APR_MID_DEC = ("04-15", "12-15", "mid-April through mid-December")

DECISIONS = {
    78: (s(*MID_APR_MID_DEC), "kooser"),
    109: (s("04-08", "10-15", "the second Friday in April to mid-October"), "blue-knob"),
    113: (s("04-15", "10-31", "mid-April to late October"), "gifford-pinchot"),
    126: ({"year_round": True, "note": "Most of the campground is open April to December; a small number of sites stay open year-round for winter camping."}, "ricketts-glen"),
    127: (s(*MID_APR_MID_OCT), "tobyhanna"),
    128: ({"year_round": True, "note": "Pickerel Point: limited sites stay open year-round."}, "promised-land"),
    203: (s(*MID_APR_MID_OCT), "leonard-harrison"),
    273: (s("04-08", "10-31", "the second Friday in April to the last weekend in October"), "cherry-springs"),
    306: (s(*MID_APR_MID_OCT), "frances-slocum"),
    307: (s(*MID_APR_MID_OCT), "lackawanna"),
    534: (s("03-01", "01-07", "March through the first weekend in January"), "french-creek"),
    557: (s("04-01", "12-15", "April to mid-December"), "ohiopyle"),
    558: (s(*MID_APR_MID_OCT), "laurel-hill"),
    620: (s("04-15", "12-31", "mid-April to late December"), "shawnee"),
    655: (s("03-31", "12-15", "the day before trout season (the first Saturday in April) to the end of deer season in December"), "caledonia"),
    656: (s("04-15", "11-01", "mid-April through November 1"), "codorus"),
    678: (s(*MID_APR_MID_OCT, "All three camping areas."), "pymatuning"),
    689: (s("04-15", "10-31", "mid-April to late October"), "prince-gallitzin"),
    692: (s("04-01", "12-15", "the first weekend in April to mid-December"), "little-pine"),
    834: (s(*MID_APR_MID_DEC), "chapman"),
    835: (s(*MID_APR_MID_OCT), "hills-creek"),
    836: (s("04-01", "12-15", "early April to mid-December for the Lower Campground", "The Upper Campground closes in mid-October."), "kettle-creek"),
    837: ({"year_round": True}, "ole-bull"),
    838: (s(*MID_APR_MID_DEC), "parker-dam"),
    839: (s("04-15", "12-07", "mid-April through early December"), "poe-valley"),
    840: (s(*MID_APR_MID_DEC), "raymond-b-winter"),
    841: (s("04-08", "12-15", "the second Friday of April to mid-December"), "bald-eagle"),
    844: (s(*MID_APR_MID_DEC), "sinnemahoning"),
    845: (s(*MID_APR_MID_DEC), "poe-paddy"),
    846: (s(*MID_APR_MID_OCT, "Ridge Campground."), "cook-forest"),
    848: (s("04-01", "10-15", "early April to mid-October for the E and F loops", "The A-D loops open late May to mid-September; the rustic Sioux campground is open year-round."), "raccoon-creek"),
    849: ({"year_round": True}, "ryerson-station"),
    851: (s("04-08", "12-15", "the second Friday in April to the end of deer season in mid-December"), "black-moshannon"),
    852: (s("04-01", "12-15", "the opening day of trout season (the first Saturday in April) to the day after rifle deer season in December"), "colonel-denning"),
    853: (s(*MID_APR_MID_DEC), "cowans-gap"),
    854: (s("04-15", "11-15", "mid-April until mid-November"), "greenwood-furnace"),
    858: (s(*MID_APR_MID_DEC), "hickory-run"),
    860: (s("03-20", "12-15", "late March to mid-December"), "fowlers-hollow"),
    861: (s(*MID_APR_MID_DEC), "hyner-run"),
    862: (s(*MID_APR_MID_DEC), "lyman-run"),
    863: (s(*MID_APR_MID_DEC), "sizerville"),
    864: (s(*MID_APR_MID_DEC), "trough-creek"),
    865: ({"year_round": False, "note": "Closed in the winter; no dates posted."}, "worlds-end"),
    1059: (s(*MID_APR_MID_OCT), "little-buffalo"),
    1060: (s("05-01", "10-15", "early May until mid-October"), "colton-point"),
}

if __name__ == "__main__":
    run({i: (season, URL.format(slug)) for i, (season, slug) in DECISIONS.items()})
