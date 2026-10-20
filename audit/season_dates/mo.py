#!/usr/bin/env python3
"""Missouri Department of Conservation: season for the MDC conservation-area campgrounds (2026-10-20).

    python3 -I audit/season_dates/mo.py [--apply]

The rule: 3 CSR 10-11.115(1) opens department areas 4 a.m. - 10 p.m., but "camping ... [is]
permitted at any time in areas where these activities are authorized, except as otherwise
provided in this chapter" (Code of State Regulations, current through 7/31/26). The chapter's
exceptions are high-water closures (11.115(4)) and the waterfowl-refuge and hunting-only zones of
named wetland areas (11.115(5)-(6)), which close PORTIONS of those areas from Oct 15. Each area's
mdc.mo.gov page prints that area's own closure lines; all 235 were read on 2026-10-20 and only
Bootleg Access limits its camping season. So: year-round, with the area's closure line in the note.

Not written: Busiek (13827) and 13903, whose pages describe walk-in tent sites / permit-only
camping (both in audit/registry_asks_2026-10-20.md), and Robert M. White II (13778), whose lake
road is open to vehicles only May 10 - Aug 31 and may be the way to its campsites.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

RULE = "3 CSR 10-11.115(1) (camping permitted at any time where authorized)"
SKIP = {13827, 13903, 13778}
BOOTLEG = 13911
HIGH_WATER = {13734, 14001}  # Donaldson Point, Girvin: 3 CSR 10-11.115(4)
REFUGE = {  # 3 CSR 10-11.115(5): portions closed to protect waterfowl
    13742: "October 15 through March 1", 13765: "October 15 through March 1",
    13772: "October 15 through March 1", 13789: "October 15 through March 1",
    13822: "October 15 through March 1", 13823: "October 15 through March 1",
    13857: "October 15 through March 1", 13862: "October 15 through March 1",
    13881: "October 15 through March 1", 13926: "October 15 through March 1",
    13794: "October 15 through March 31 (Cypress Lake to the end of duck season)",
    13815: "October 15 through the end of duck season (Pool 1 South) or Canada goose season (Pool 1 North, Dark Cypress Swamp)",
}


def decisions():
    out = {}
    for e in json.load(open(CG, encoding="utf-8")):
        if e.get("state") != "MO" or e.get("ownership") != "state" or e["id"] in SKIP:
            continue
        url = next((w for w in (e.get("website") or "").split() if "mdc.mo.gov" in w), None)
        if not url:
            continue
        i = e["id"]
        src = f"{RULE}; {url} (area regulations and Things to Do), read 2026-10-20"
        if i == BOOTLEG:
            out[i] = ({"year_round": False, "opens": "09-15", "closes": "05-15"},
                      f"{url} (\"several primitive camping sites that are available Sept. 15-May 15\"), read 2026-10-20")
        elif i in HIGH_WATER:
            out[i] = ({"year_round": True, "note": "The whole area closes during high water on the Mississippi (3 CSR 10-11.115(4))."}, src)
        elif i in REFUGE:
            out[i] = ({"year_round": True, "note": f"Portions of the area are closed to protect waterfowl, {REFUGE[i]}."}, src)
        else:
            out[i] = ({"year_round": True}, src)
    return out


if __name__ == "__main__":
    run(decisions())
