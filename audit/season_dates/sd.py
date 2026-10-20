#!/usr/bin/env python3
"""South Dakota GFP: season from each park's gfp.sd.gov page (2026-10-20).

    python3 -I audit/season_dates/sd.py [--apply]

Every gfp.sd.gov park page has an "Open:" line; these 44 say "Year-round". Where it adds that
showers, flush toilets and water may be shut off in winter, the note says so (vault toilets
usually stay open).

Not written: Walkers Point and Foster Bay (their detail URLs return the generic page), Dude Ranch
(its website is the general camping page) and Amsden Lakeside Use Area, whose "Open:" line is
about toilets and water, not the season.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

# id: (the park's page, its "Open:" line)
PAGES = {
    5710: ("https://gfp.sd.gov/parks/detail/big-sioux-recreation-area/", "Year-round."),
    5712: ("https://gfp.sd.gov/parks/detail/lake-vermillion-recreation-area/", "Year-round."),
    5714: ("https://gfp.sd.gov/parks/detail/angostura-recreation-area/", "Year-round."),
    5716: ("https://gfp.sd.gov/parks/detail/lewis-and-clark-recreation-area/", "Year-round."),
    5717: ("https://gfp.sd.gov/parks/detail/rocky-point-recreation-area/", "Year-round."),
    5718: ("https://gfp.sd.gov/parks/detail/farm-island-recreation-area/", "Year-round."),
    5720: ("https://gfp.sd.gov/parks/detail/snake-creek-recreation-area/", "Year-round."),
    5724: ("https://gfp.sd.gov/parks/detail/union-grove-state-park/", "Year-round."),
    5725: ("https://gfp.sd.gov/parks/detail/shadehill-recreation-area/", "Year-round. Between November 30 and April 30, showers, flush toilets, and other water systems may be closed. Contact the park for current status. Vault toilets usually remain open."),
    5728: ("https://gfp.sd.gov/parks/detail/newton-hills-state-park/", "Year-round."),
    5730: ("https://gfp.sd.gov/parks/detail/lake-thompson-recreation-area/", "Year-round."),
    5731: ("https://gfp.sd.gov/parks/detail/oakwood-lakes-state-park/", "Year-round."),
    5733: ("https://gfp.sd.gov/parks/detail/lake-herman-state-park/", "Year-round."),
    5734: ("https://gfp.sd.gov/parks/detail/mina-lake-recreation-area/", "Year-round."),
    5735: ("https://gfp.sd.gov/parks/detail/pelican-lake-recreation-area/", "Year-round."),
    5737: ("https://gfp.sd.gov/parks/detail/west-bend-recreation-area/", "Year-round."),
    5738: ("https://gfp.sd.gov/parks/detail/west-whitlock-recreation-area/", "Year-round."),
    5740: ("https://gfp.sd.gov/parks/detail/hartford-beach-state-park/", "Year-round."),
    5742: ("https://gfp.sd.gov/parks/detail/roy-lake-state-park/", "Year-round."),
    5743: ("https://gfp.sd.gov/parks/detail/west-pollock-recreation-area/", "Year-round."),
    5744: ("https://gfp.sd.gov/parks/detail/llewellyn-johns-recreation-area/", "Year-round."),
    5745: ("https://gfp.sd.gov/parks/detail/bear-butte-state-park/", "Year-round."),
    5746: ("https://gfp.sd.gov/parks/detail/lake-poinsett-recreation-area/", "Year-round."),
    5747: ("https://gfp.sd.gov/parks/detail/springfield-recreation-area/", "Year-round. Between Oct. 1 and April 30, showers, flush toilets and other water systems may be closed. Please contact the park directly for current status. Vault toilets usually remain open."),
    5748: ("https://gfp.sd.gov/parks/detail/-fisher-grove-state-park/", "Year-round."),
    5749: ("https://gfp.sd.gov/parks/detail/lake-louise-recreation-area/", "Year-round."),
    5750: ("https://gfp.sd.gov/parks/detail/north-wheeler-recreation-area/", "Year-round."),
    5751: ("https://gfp.sd.gov/parks/detail/pickerel-lake-recreation-area/", "Year-round."),
    5752: ("https://gfp.sd.gov/parks/detail/cow-creek-recreation-area-/", "Year-round."),
    5753: ("https://gfp.sd.gov/parks/detail/richmond-lake-recreation-area/", "Year-round."),
    5755: ("https://gfp.sd.gov/parks/detail/north-point-recreation-area/", "Year-round."),
    5757: ("https://gfp.sd.gov/parks/detail/pease-creek-recreation-area/", "Year-round."),
    5758: ("https://gfp.sd.gov/parks/detail/sandy-shore-recreation-area/", "Year-round."),
    5759: ("https://gfp.sd.gov/parks/detail/fort-sisseton-historic-state-park/", "Open year-round. Between Oct. 1 and April 30, showers, flush toilets and other water systems may be closed. Please contact the park directly for current status. Vault toilets usually remain open."),
    5760: ("https://gfp.sd.gov/parks/detail/lake-hiddenwood-recreation-area/", "Year-round."),
    5761: ("https://gfp.sd.gov/parks/detail/pierson-ranch-recreation-area/", "Year-round."),
    5763: ("https://gfp.sd.gov/parks/detail/little-moreau-recreation-area/", "Year-round."),
    5764: ("https://gfp.sd.gov/parks/detail/swan-creek-recreation-area/", "Year-round."),
    5765: ("https://gfp.sd.gov/parks/detail/sica-hollow-state-park/", "Year-round"),
    5766: ("https://gfp.sd.gov/parks/detail/lake-cochrane-recreation-area/", "Year-round."),
    13153: ("https://gfp.sd.gov/parks/detail/buryanek-recreation-area/", "Year-round."),
    13154: ("https://gfp.sd.gov/parks/detail/platte-creek-recreation-area/", "Year-round."),
    13155: ("https://gfp.sd.gov/parks/detail/sheps-canyon-recreation-area/", "Year-round."),
    13156: ("https://gfp.sd.gov/parks/detail/lake-carthage-lakeside-use-area/", "Year-round. Between Oct. 1 and April 30, water hydrants may be closed. Please contact the park directly for current status. Vault toilets usually remain open."),
}

DECISIONS = {}
for i, (url, line) in PAGES.items():
    season = {"year_round": True}
    m = re.search(r"Between (.+?) and (.+?), (showers, flush toilets,? and other water systems|water hydrants) may be closed", line)
    if m:
        what = "Showers, flush toilets and water" if m[3].startswith("showers") else "Water hydrants"
        season["note"] = f"{what} may be shut off between {m[1]} and {m[2]}; vault toilets usually stay open."
    DECISIONS[i] = (season, f"{url} (\"Open: {line[:60]}\"), read 2026-10-20")

if __name__ == "__main__":
    run(DECISIONS)
