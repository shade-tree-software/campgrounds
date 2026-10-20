#!/usr/bin/env python3
"""Vermont State Parks: season from each vtstateparks.com park page's "Season" line (read
2026-10-20).

    python3 -I audit/season_dates/vt.py [--apply]

The lines are floating rules ("Friday of Memorial Day Weekend through the second Monday in
October"); opens/closes take the widest span the rule can give (Memorial Day Friday May 22-28 ->
05-22; second Monday in October Oct 8-14 -> 10-14; third weekend in May -> 05-15; Labor Day
Sep 1-7 -> 09-07) and the note keeps the park's own wording.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

P = "https://www.vtstateparks.com/parks/{}"
MEM_COL = "Friday of Memorial Day Weekend through the second Monday in October."
# id: (slug, season line, opens, closes, extra note)
V = {
    204: ("woodford", MEM_COL, "05-22", "10-14", ""),
    297: ("molly-stark", MEM_COL, "05-22", "10-14", ""),
    298: ("lake-st-catherine", MEM_COL, "05-22", "10-14", ""),
    299: ("emerald-lake", MEM_COL, "05-22", "10-14", ""),
    300: ("coolidge", MEM_COL, "05-22", "10-14", ""),
    301: ("jamaica", "Third weekend in May through the second Monday in October.", "05-15", "10-14", ""),
    344: ("grand-isle", "Second weekend in May through the third weekend in October.", "05-08", "10-22", ""),
    359: ("new-discovery", MEM_COL, "05-22", "10-14", ""),
    360: ("little-river", "Third weekend in May through the Third weekend in October.", "05-15", "10-22", " The B side closed Sept 7 in 2026."),
    361: ("smugglers-notch", "Third weekend in May through the second Monday in October.", "05-15", "10-14", ""),
    362: ("elmore", MEM_COL, "05-22", "10-14", ""),
    615: ("fort-dummer", "Friday of Memorial Day Weekend through Labor Day.", "05-22", "09-07", ""),
    675: ("stillwater", "Third weekend in May to Monday, September 14.", "05-15", "09-14", ""),
    13960: ("maidstone", "Friday of Memorial Day Weekend through Labor Day Weekend.", "05-22", "09-07", ""),
}

if __name__ == "__main__":
    D = {i: ({"year_round": False, "opens": o, "closes": c, "note": (line + x).strip()},
             f"{P.format(slug)} (Season: \"{line}\"), read 2026-10-20") for i, (slug, line, o, c, x) in V.items()}
    run(D)
