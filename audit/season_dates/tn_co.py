#!/usr/bin/env python3
"""Tennessee State Parks campgrounds: season and renovation closures from each tnstateparks.com
park page; one Colorado park from its CPW page (read 2026-10-20).

    python3 -I audit/season_dates/tn_co.py [--apply]

Tennessee publishes no statewide season, so only a page that says a campground (or part of it)
is open year-round, or describes its winter service, gets a season. Six campgrounds the pages
list as closed for renovation are marked temporarily closed.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

Q = {
    4392: ("Campground #1 sits along Shoal Creek and is open March 1 - November 3. ... Campground #2 is open year-round.",
           "Campground #2 is open year-round; Campground #1 March 1 - November 3."),
    4403: ("Approximately 20 sites and one bathhouse are open year-round.", "About 20 sites and one bathhouse stay open in winter."),
    4394: ("A dump station is open year-round. ... that building is not open during the off-season, so showers are not available in December, January, and February.",
           "No showers December - February."),
    13725: ("The beautiful wooded campground sites are each equipped with ... Open year-round.", ""),
    2284: ("The Fruita section is open year-round for camping, but facilities are available in the winter (November-March) on a limited basis",
           "Facilities are limited November - March."),
}


def closed(i, reopens, quote):
    return {"status": {"operating": "temporarily_closed", "reopens": reopens, "note": quote},
            "_sources": {"status": "{} (alert), read 2026-10-20"}}


EXTRA = {
    13717: closed(13717, "not announced", "Campground closed for renovations (park alert, read 2026-10-20)."),
    13718: closed(13718, "2027", "Campground closed through 2026 for a renovation project (park alert, read 2026-10-20)."),
    13722: closed(13722, "not announced", "Norris Dam's campgrounds are closed for renovations (park alert, read 2026-10-20)."),
    13723: closed(13723, "not announced", "Norris Dam's campgrounds are closed for renovations (park alert, read 2026-10-20)."),
    13724: closed(13724, "not announced", "Campground closed for renovations to the bathhouse and campground (park alert, read 2026-10-20)."),
    13725: closed(13725, "not announced", "Main Campground closed after weather damage, ahead of renovations; Bruton Branch Campground is open (park alert, read 2026-10-20)."),
    13726: closed(13726, "late 2026", "Campground closed for renovations from July 7, 2025, expected to last until late 2026 (park alert, read 2026-10-20)."),
}

if __name__ == "__main__":
    cg = {e["id"]: e for e in json.load(open(CG, encoding="utf-8"))}
    for i, g in EXTRA.items():
        g["_sources"]["status"] = g["_sources"]["status"].format(cg[i]["website"].split()[0])
    D = {i: ({"year_round": True, **({"note": n} if n else {})},
             f"{cg[i]['website'].split()[0]} (\"{q}\"), read 2026-10-20") for i, (q, n) in Q.items()}
    run(D, EXTRA)
