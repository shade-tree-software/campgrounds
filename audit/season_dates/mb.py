#!/usr/bin/env python3
"""Manitoba Parks: season from "2026 Operating Dates - Campgrounds, Group Use Areas, Cabins & Yurts".

    python3 -I audit/season_dates/mb.py [--apply]

The province's operating-dates sheet (https://gov.mb.ca/sd/pubs/parks-protected-spaces/operating_dates.pdf,
read 2026-10-20) lists each campground's opening date, its reservation window and the date the
campground is "open until". The Campsites row is used: opens = opening date, closes = open until.
Where the campground stays open first-come after reservations end, or the sheet's notes close part
of it early, the note says so.

Not written: Falcon Creek (Whiteshell), which the sheet does not list.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SRC = ("https://gov.mb.ca/sd/pubs/parks-protected-spaces/operating_dates.pdf (2026 Operating Dates, "
       "{} Campsites row), read 2026-10-20")

# id: (row name, opens, closes, note)
ROWS = {
    9319: ("Asessippi", "05-08", "09-13", None),
    9322: ("Bell Lake", "05-15", "09-20", None),
    9323: ("Birch Point", "05-08", "09-07", None),
    9324: ("Birds Hill", "05-08", "10-12", "The east side of the campground is open May 15 - Sep 7. Services after Sep 30 depend on the weather."),
    9326: ("Campers Cove", "05-15", "09-07", None),
    9328: ("Blue Lakes", "05-15", "10-12", None),
    9329: ("Childs Lake", "05-15", "09-20", None),
    9330: ("Wellman Lake", "05-15", "09-20", None),
    9331: ("Singush", "05-15", "10-12", None),
    9333: ("Grand Beach", "05-15", "09-07", None),
    9343: ("Beresford Lake", "05-15", "10-12", "Reservable through Sep 6; open to Oct 12."),
    9344: ("Bird Lake", "05-15", "10-12", None),
    9345: ("Tulabi Falls", "05-15", "10-12", None),
    9346: ("Norris Lake", "05-08", "09-13", None),
    9347: ("Paint Lake and Paint Lake-Lakeview", "05-15", "10-12", "The main campground closes Sep 20; the Lakeview loop stays open to Oct 12."),
    9350: ("Kiche Manitou", "05-08", "10-12", "Bays 1 to 7 close Sep 20."),
    9352: ("St. Malo", "05-08", "09-13", None),
    9354: ("Adam Lake", "05-08", "09-13", None),
    9355: ("Max Lake", "05-08", "09-13", None),
    9356: ("Watchorn", "05-15", "09-07", None),
    9359: ("Betula Lake", "05-08", "09-07", None),
    9360: ("Big Whiteshell", "05-08", "10-12", None),
    9362: ("Caddy Lake", "05-08", "10-12", "Reservable through Sep 26; open to Oct 12."),
    9364: ("Nutimik Lake", "05-08", "10-12", None),
    9365: ("Opapiskaw", "05-08", "09-07", None),
    9366: ("Otter Falls", "05-08", "10-12", None),
    9367: ("White Lake", "05-08", "09-07", None),
    9368: ("Falcon Beach", "05-08", "10-12", None),
    9369: ("Falcon Lakeshore", "05-15", "09-07", None),
    9370: ("West Hawk Lake", "05-08", "10-12", None),
    9371: ("William Lake", "05-08", "09-13", None),
    9372: ("Winnipeg Beach", "05-15", "10-12", None),
}

DECISIONS = {}
for i, (row, o, c, note) in ROWS.items():
    season = {"year_round": False, "opens": o, "closes": c}
    if note:
        season["note"] = note
    DECISIONS[i] = (season, SRC.format(row))

if __name__ == "__main__":
    run(DECISIONS)
