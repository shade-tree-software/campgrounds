#!/usr/bin/env python3
"""Ontario Parks: season from each park's "Operating Dates" table (2026-10-20).

    python3 -I audit/season_dates/on.py [--apply]

Every ontarioparks.ca park page carries a "2026 Operating Dates" table: one row per park or
campground and use, with icons for the use (Camping, Day Use, Roofed Accommodation, Backcountry
Camping, Winter Operating Dates) and the dates. ontario_parks_operating_dates_2026-10-20.json is
the snapshot this script reads.

Rows flagged Camping count (Backcountry Camping alone does not); an entry named for one
campground (Algonquin's, Agawa Bay, Rossport, Whitesand Lake) takes that campground's rows. A
camping row running Jan 1 - Dec 31 makes the entry year-round. Otherwise the main camping row is
the season (Silent Lake's runs May 8 to March 28 and wraps the new year), and a separate winter
camping row goes in the note.

Not written: the four St. Lawrence Parks Commission campgrounds, whose pages give no dates.
"""
import json, os, re, sys
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = json.load(open(os.path.join(HERE, "ontario_parks_operating_dates_2026-10-20.json"), encoding="utf-8"))
MONTHS = "January February March April May June July August September October November December".split()

# Entries for one campground in a park with several.
CAMPGROUND = {
    8189: "Lake of Two Rivers", 8191: "Canisbay Lake", 8192: "Pog Lake", 8204: "Rock Lake",
    8222: "Achray", 8238: "Kiosk", 8239: "Brent", 8225: "Agawa Bay", 8252: "Rossport",
    8253: "Whitesand Lake",
}


def parse(s):
    m = re.fullmatch(r"(\w+) (\d+), (\d{4}) to (\w+) (\d+), (\d{4})", s)
    a = date(int(m[3]), MONTHS.index(m[1]) + 1, int(m[2]))
    b = date(int(m[6]), MONTHS.index(m[4]) + 1, int(m[5]))
    return a, b


def md(d):
    return d.strftime("%m-%d")


def human(a, b):
    yr = f", {b.year}"
    return f"{a.strftime("%b")} {a.day}{", " + str(a.year) if a.year != b.year else ""} - {b.strftime("%b")} {b.day}{yr}"


def decide(i, v):
    want = CAMPGROUND.get(i)
    rows = []
    for r in v["rows"]:
        if "Camping" not in r["usage"]:
            continue
        name = r["name"].split(" - ", 1)
        if want and (len(name) < 2 or name[1].strip() != want):
            continue
        rows.append((parse(r["dates"]), "Winter Operating Dates" in r["usage"]))
    if not rows:
        return None
    if any(a.month == 1 and a.day == 1 and b.month == 12 and b.day == 31 for (a, b), _ in rows):
        return {"year_round": True}
    main = [(a, b) for (a, b), w in rows if not w] or [(a, b) for (a, b), w in rows if b.year > a.year]
    (a, b) = max(main, key=lambda x: (x[1] - x[0]).days)
    season = {"year_round": False, "opens": md(a), "closes": md(b)}
    winter = [(x, y) for (x, y), w in rows if w and (x, y) != (a, b)]
    if winter:
        upcoming = [r for r in winter if r[1] >= date(2026, 10, 20)] or winter
        x, y = min(upcoming)
        season["note"] = f"Also open for winter camping {human(x, y)}."
    return season


DECISIONS = {}
for k, v in SNAP.items():
    s = decide(int(k), v)
    if s:
        DECISIONS[int(k)] = (s, f"https://www.ontarioparks.ca/park/{v['slug']} (2026 Operating Dates), read 2026-10-20")

if __name__ == "__main__":
    run(DECISIONS)
