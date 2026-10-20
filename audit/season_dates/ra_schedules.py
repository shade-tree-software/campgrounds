#!/usr/bin/env python3
"""Georgia, New Mexico and Oklahoma state parks: season from ReserveAmerica's Season Schedule
(2026-10-20), plus TravelOK for two Lake Murray campgrounds that are not on ReserveAmerica.

    python3 -I audit/season_dates/ra_schedules.py [--apply]

Each park's campgroundSeasonDates.do page lists the season segments the booking engine runs
(Peak / Off Peak / Shoulder / Walk In ...), snapshotted in ra_season_schedules_2026-10-20.json.
A schedule that runs without a gap for (about) a year is year-round; "Walk In" segments (New
Mexico's first-come off season) count as open, and the reservable span goes in the note.

A schedule WITH a gap is not written: a gap only says the engine stops selling nights, and
New Mexico parks with gaps (Fenton Lake turns off its winter water "for the remainder of the
winter season") are camped through them. Left unset: Heron, Fenton, El Vado, Manzano, Hyde,
Eagle Nest (NM) and Black Mesa (OK). Indiana's pages carry no schedule.
"""
import datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "ra_season_schedules_2026-10-20.json")
MD = lambda s: dt.date.fromisoformat(s).strftime("%b %-d")

TRAVELOK = {
    673: "https://www.travelok.com/state-parks/lake-murray-state-park",
    6575: "https://www.travelok.com/state-parks/lake-murray-state-park",
}


def continuous_year(segs):
    s = sorted(segs, key=lambda x: x[1])
    for a, b in zip(s, s[1:]):
        if dt.date.fromisoformat(b[1]) - dt.date.fromisoformat(a[2]) > dt.timedelta(days=1):
            return False
    return dt.date.fromisoformat(s[-1][2]) - dt.date.fromisoformat(s[0][1]) >= dt.timedelta(days=360)  # a booking horizon can stop a day or two short


def decisions():
    cg = {e["id"]: e for e in json.load(open(CG, encoding="utf-8"))}
    out = {}
    for i, segs in json.load(open(SNAP)).items():
        i = int(i)
        if not segs or not continuous_year(segs):
            continue
        ra = next(w for w in cg[i]["website"].split() if "reserveamerica" in w)
        url = ra.replace("campgroundDetails.do", "campgroundSeasonDates.do")
        season = {"year_round": True}
        walk = [g for g in segs if g[0] == "Walk In"]
        if walk:
            res = [g for g in segs if g[0] != "Walk In" and g[1] > walk[0][2]] or [g for g in segs if g[0] != "Walk In"]
            season["note"] = f"Reservable {MD(res[0][1])} - {MD(res[0][2])}; first-come (walk-in) the rest of the year."
        span = "; ".join(f"{n} {a} to {b}" for n, a, b in sorted(segs, key=lambda x: x[1]))
        out[i] = (season, f"{url} (Season Schedule: {span}), read 2026-10-20")
    for i, url in TRAVELOK.items():
        out[i] = ({"year_round": True}, f"{url} (Hours: \"Open daily for entry 7am-11pm; camping available all year.\"), read 2026-10-20")
    return out


if __name__ == "__main__":
    run(decisions())
