#!/usr/bin/env python3
"""Delaware State Parks: every campground is open year-round (2026-10-20).

    python3 -I audit/season_dates/de.py [--apply]

The park pages on destateparks.com carry one sentence for all five: "Campgrounds at Cape
Henlopen, Killens Pond, Lums Pond and Trap Pond State Park are open year-round ... the
campground at Delaware Seashore State Park is open year-round, although during the winter
months, it is open for self-contained units only."
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SRC = "https://www.destateparks.com/park/{}/ (the campgrounds sentence), read 2026-10-20"

DECISIONS = {
    670: ({"year_round": True}, SRC.format("cape-henlopen")),
    215: ({"year_round": True}, SRC.format("killens-pond")),
    649: ({"year_round": True}, SRC.format("lums-pond")),
    867: ({"year_round": True}, SRC.format("trap-pond")),
    868: ({"year_round": True, "note": "Self-contained rigs only in the winter months."}, SRC.format("delaware-seashore")),
}

if __name__ == "__main__":
    run(DECISIONS)
