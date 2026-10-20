#!/usr/bin/env python3
"""Iowa and Virginia state park campgrounds from each agency's statewide statement (read
2026-10-20).

    python3 -I audit/season_dates/ia_va.py [--apply]

Iowa DNR, "State park campgrounds getting ready for winter 2025": water is shut off and shower
houses close from mid-October and dump stations close for the winter, but "visitors are
encouraged to continue camping". Every Iowa DNR campground is therefore year-round; Honey Creek
Resort (concession-run) is left out.

Virginia DCR camping page: "Full-service campgrounds (with bathhouses) are open from the first
Friday in March through the first Monday in December with the exception of Douthat, Hungry
Mother, Pocahontas and Shenandoah River state parks which have full-service campgrounds open
year-round." Widest span: 03-01 to 12-07. Breaks Interstate Park is not DCR and is left out.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

IA_SRC = "https://www.iowadnr.gov/news-release/2025-10-21/state-park-campgrounds-getting-ready-winter-2025"
IA_Q = ("State parks winterize their facilities starting in mid-October, including shutting off water in campgrounds "
        "and closing shower houses. ... RV campers are reminded that dump stations are closed during the winter. ... "
        "While water may be shut off, visitors are encouraged to continue camping")
VA_SRC = "https://www.dcr.virginia.gov/state-parks/camping"
VA_Q = ("Full-service campgrounds (with bathhouses) are open from the first Friday in March through the first Monday in "
        "December with the exception of Douthat, Hungry Mother, Pocahontas and Shenandoah River state parks which have "
        "full-service campgrounds open year-round.")
VA_YR = {647, 668, 694}
SKIP = {2905, 1104}

if __name__ == "__main__":
    D = {}
    for e in json.load(open(CG, encoding="utf-8")):
        if e.get("ownership") != "state" or e.get("season") or e["id"] in SKIP:
            continue
        if e["state"] == "IA":
            D[e["id"]] = ({"year_round": True, "note": "Water and showers are off from mid-October and the dump station closes for the winter."},
                          f"{IA_SRC} (\"{IA_Q}\"), read 2026-10-20")
        elif e["state"] == "VA":
            s = {"year_round": True} if e["id"] in VA_YR else {
                "year_round": False, "opens": "03-01", "closes": "12-07",
                "note": "First Friday in March through the first Monday in December."}
            D[e["id"]] = (s, f"{VA_SRC} (\"{VA_Q}\"), read 2026-10-20")
    run(D)
