#!/usr/bin/env python3
"""Michigan DNR state parks and state forest campgrounds: season from DNR's two tables
(read 2026-10-20, snapshot in mi_dnr_tables_2026-10-20.json).

    python3 -I audit/season_dates/mi.py [--apply]

State parks: "Camping and lodging rates and operating dates" gives each campground's reservation
season (and, in its notes, any camping outside it). A park entry covering several campgrounds
takes the widest span, or year-round when one of them is, and names the others in the note.

State forest campgrounds: the amenity table's "Seasonal closure dates" column ("open all year",
or the closed span: "Nov 1 to May 1" = open May 1 - Oct 31). Its footnote: "SFCG campground roads
may not be plowed in the winter."

Not written: Traverse City (no dates posted), Pontiac Lake (2026 construction dates), Ely Lake
(Allegan SGA, in neither table), and forest rows reading "weather dependent", "contact manager"
or "Managed by Colfax Twp"; Bass Lake (Marquette), Garnet Lake and Little Brevort Lake-South are
not in the forest table.
"""
import datetime as dt, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = json.load(open(os.path.join(HERE, "mi_dnr_tables_2026-10-20.json"), encoding="utf-8"))
RATES = "https://www.michigan.gov/dnr/things-to-do/camping-and-lodging/camping-and-lodging-rates-and-operating-dates"
SFC = "https://www.michigan.gov/dnr/things-to-do/camping-and-lodging/state-forest-campgrounds/amenity-table"
MON = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

# Park entry -> its campgrounds in the operating-dates table, as (park, campground).
PARKS = {
    188: [("Ludington", "Beechwood"), ("Ludington", "Cedar"), ("Ludington", "Pines")],
    189: [("Tahquamenon Falls", "Lower Falls-Portage")],
    289: [("Orchard Beach", "Campground")],
    407: [("Silver Lake", "Silver Lake")],
    410: [("Tahquamenon Falls", "Rivermouth Campground")],
    411: [("Tahquamenon Falls", "Rivermouth Pines Semi-Modern/Rustic")],
    415: [("Tahquamenon Falls", "Lower Falls-Hemlock")],
    460: [("Holland", "Lake Macatawa Pines and Woodstock loops"), ("Holland", "Beach campground")],
    562: [("Wilderness", "Full Hook-up"), ("Wilderness", "Pines Campground"), ("Wilderness", "Lakeshore Campground - East and West")],
    566: [("Straits", "Straits Campground")],
    569: [("Van Buren", "Van Buren Campground")],
    571: [("Warren Dunes", "Hildebrandt Campground - Semi Modern"), ("Warren Dunes", "Mount Randall Campground")],
    575: [("Hoeft", "Hoeft Campground")],
    581: [("Harrisville", "campground")],
    582: [("Muskallonge", "campground")],
    583: [("Tawas Point", "Tawas Point Campground")],
    676: [("Grand Haven", "Grand Haven Campground")],
    780: [("Porcupine Mountains", "Union Bay")],
    781: [("Port Crescent", "campground")],
    783: [("Lake Gogebic", "campground")],
    784: [("Burt Lake", "East and West Loops")],
    785: [("Mitchell", "campground")],
    786: [("Indian Lake", "South Unit - Campground"), ("Indian Lake", "West Shore Campground")],
    788: [("Young", "Oak Campground"), ("Young", "Spruce Campground"), ("Young", "Terrace Campground")],
    789: [("Clear Lake", "Upper and Lower Campgrounds")],
    790: [("Otsego Lake", "North and South Loops")],
    793: [("Interlochen", "North Campground"), ("Interlochen", "South Campground")],
    794: [("South Higgins Lake", "East Campground"), ("South Higgins Lake", "West Campground")],
    796: [("McLain", "campground")],
    797: [("Aloha", "North, Middle and South Sections")],
    798: [("Wells", "Wells Campground")],
    3601: [("Bay City Recreation Area", "Bay City Campground")],
    3602: [("Brimley", "Brimley Campground")],
    3603: [("Sleeper", "Sleeper Campground")],
    3604: [("Van Riper", "Modern Campground Loops 1 and 2")],
    3606: [("Cheboygan", "Cheboygan Campground")],
    3609: [("Waterloo", "Green Lake Campground")],
    3614: [("Bewabic", "A, B, C Loops")],
    3623: [("Lakeport", "North and South Loops")],
    3624: [("Lakeport", "North and South Loops")],
    3625: [("Rifle River", "Grousehaven Lake")],
    3626: [("Rifle River", "Rustic Campgrounds (Spruce, Ranch, & Devoe)")],
    3627: [("Algonac", "Riverfront")],
    3628: [("Algonac", "Wagon Wheel")],
    3630: [("Yankee Springs", "Gun Lake Campground")],
    3631: [("Yankee Springs", "Deep Lake")],
    3632: [("Sterling", "Campground (includes full hook-up)")],
    3633: [("Muskegon", "Lake Michigan Campground")],
    3634: [("Muskegon", "Channel Campground")],
    3639: [("Hayes", "East and West Loops")],
    3641: [("Mears", "East and West Loops")],
    3642: [("Petoskey", "Dunes")],
    3644: [("North Higgins Lake", "East Campground"), ("North Higgins Lake", "West Campground")],
    14038: [("Brighton", "Bishop Lake")],
    14039: [("Brighton", "Appleton Lake")],
    14040: [("Brighton", "Murray Lake Campground")],
    14042: [("Pinckney", "Crooked Lake")],
    14043: [("Rifle River", "Rustic Campgrounds (Spruce, Ranch, & Devoe)")],
    14044: [("Rifle River", "Rustic Campgrounds (Spruce, Ranch, & Devoe)")],
    14045: [("Porcupine Mountains", "Presque Isle")],
}
YEAR_ROUND = {3627}  # Algonac Riverfront: semi-modern camping outside the reservation season
PARK_NOTE = {
    3627: "Reservable Mar 22 - Nov 29; semi-modern sites are first-come the rest of the year. Full-hookup sites have no water Oct 22 - Apr 15.",
    789: "DNR warns 2026 construction may affect reservable dates.",
    14038: "Reservable on weekends only December - March.",
    14040: "Reservable on weekends only.",
}

# Forest entry -> its row name in the amenity table (only where the names differ).
FOREST = {414: "Reed & Green Bridge State Forest Campground", 417: "Blind Sucker #2 State Forest Campground",
          419: "Mouth of Two Hearted River State Forest Campground", 3656: ("Long Lake State Forest Campground", "Wexford"),
          3657: "Twin Lake State Forest Campground", 3667: "Old US 131 State Forest Campground",
          3669: "Upper Manistee State Forest Campground", 3684: "Anderson Lake State Forest Campground",
          3695: ("Pickerel Lake State Forest Campground", "Kalkaska"), 3698: ("Long Lake State Forest Campground", "Missaukee"),
          3699: "Little Wolf State Forest Campground", 3712: "Hog Island State Forest Campground",
          3715: "Blind Sucker #1 State Forest Campground", 3726: "East Branch Fox River State Forest Campground",
          3736: ("Pickerel Lake State Forest Campground", "Otsego"),
          3802: "Canoe Harbor State Forest Campground and Canoe Camp", 14033: "Pigeon River Bridge State Forest Campground"}
NO_FOREST = {3685}  # Bass Lake (Marquette): the table's Bass Lake is the Luce County one


def md(text, part):
    """'Nov. 30' / 'early Nov.' / 'late April' -> MM-DD (approximate words per common.py's convention)."""
    t = text.lower().replace(".", "").strip()
    m = re.match(r"(early|mid|late)?\s*([a-z]+)\s*(\d+)?", t)
    q, mon, day = m.group(1), MON[m.group(2)[:3]], m.group(3)
    if day:
        return dt.date(2027, mon, int(day))
    if q == "early":
        return dt.date(2027, mon, 1 if part == "opens" else 7)
    if q == "late":
        return dt.date(2027, mon, 20) if part == "opens" else dt.date(2027, mon % 12 + 1, 1) - dt.timedelta(days=1)
    return dt.date(2027, mon, 15)


def park_decision(i, rows):
    by = {(r["park"], r["campground"]): r for r in SNAP["state_parks"]}
    rs = [by[k] for k in rows]
    yr = [r for r in rs if r["starts"] == "Year-round"]
    others = [r for r in rs if r["starts"] != "Year-round"]
    span = lambda r: f"{r['starts'][:3]} {r['starts'].split()[1]} - {r['ends'][:3]} {r['ends'].split()[1]}"
    if yr:
        season = {"year_round": True}
        if others:
            season["note"] = f"{', '.join(r['campground'] for r in yr)} is open year-round; " + "; ".join(f"{r['campground']} {span(r)}" for r in others) + "."
    else:
        o = min(others, key=lambda r: md(r["starts"], "opens"))
        c = max(others, key=lambda r: md(r["ends"], "closes"))
        season = {"year_round": False, "opens": md(o["starts"], "opens").strftime("%m-%d"), "closes": md(c["ends"], "closes").strftime("%m-%d")}
        if len({span(r) for r in others}) > 1:
            season["note"] = "; ".join(f"{r['campground']} {span(r)}" for r in others) + "."
    if i in YEAR_ROUND:
        season = {"year_round": True}
    if i in PARK_NOTE:
        season["note"] = (season.get("note", "") + " " + PARK_NOTE[i]).strip()
    quote = "; ".join(f"{r['park']} / {r['campground']}: {r['starts']} - {r['ends']}" for r in rs)
    return season, f"{RATES} (reservation season starts/ends: {quote}), read 2026-10-20"


def norm(s):
    s = re.sub(r"state forest campground|campground|state forest|sfc|\bsf\b", "", s.lower().replace("&", "and"))
    return " ".join(re.sub(r"[^a-z0-9 ]", "", s).split())


def forest_decision(row):
    c = row["closure"]
    if c == "open all year":
        note = "Campground roads may not be plowed in winter."
        if "winter" in row["special"].lower():
            note += f" {row['special'].strip().rstrip('.').capitalize()}."
        season = {"year_round": True, "note": note}
    else:
        m = re.match(r"(.+?)\s+(?:to|–)\s+(.+)$", c)
        if not m or not re.match(r"(early |mid |late )?[A-Za-z]{3}", m.group(1)) or m.group(1).split()[0].lower() in ("weather", "contact", "permanently"):
            return None
        try:
            start, end = md(m.group(1), "closes"), md(m.group(2), "opens")
        except (KeyError, AttributeError):
            return None
        last = start - dt.timedelta(days=1) if re.search(r"\d", m.group(1)) else start
        season = {"year_round": False, "opens": end.strftime("%m-%d"), "closes": last.strftime("%m-%d")}
    return season, f"{SFC} ({row['name']}, {row['county']} Co.: \"Seasonal closure dates: {c}\"), read 2026-10-20"


def decisions():
    out = {i: park_decision(i, rows) for i, rows in PARKS.items()}
    rows = {}
    for r in SNAP["state_forest"]:
        rows.setdefault(norm(r["name"]), []).append(r)
    for e in json.load(open(CG, encoding="utf-8")):
        if e["state"] != "MI" or e.get("ownership") != "state" or e.get("season") or e["id"] in out or e["id"] in NO_FOREST:
            continue
        want = FOREST.get(e["id"])
        if isinstance(want, tuple):
            cand = [r for r in SNAP["state_forest"] if r["name"] == want[0] and r["county"] == want[1]]
        elif want:
            cand = [r for r in SNAP["state_forest"] if r["name"] == want]
        else:
            cand = rows.get(norm(e["name"]), [])
        if len(cand) != 1:
            continue
        d = forest_decision(cand[0])
        if d:
            out[e["id"]] = d
    return out


if __name__ == "__main__":
    run(decisions())
