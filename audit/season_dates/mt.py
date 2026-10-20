#!/usr/bin/env python3
"""Montana FWP: season from Fishing Access Site and state park pages (2026-10-20).

    python3 -I audit/season_dates/mt.py [--apply]

Fishing Access Sites (myfwp.mt.gov/fishMT/fas/<id>) carry an "Open:" date range whose year
is a placeholder (2005, 2011...); the month-day is the site's open period, and 01-01 to
12-31 is year-round. None of these pages lists a closure or winter line. State park pages
(fwp.mt.gov) have a "Seasons & Hours" block; the campground line is used.

Skipped: Lewis & Clark Caverns and Bannack (no campground season stated), Fish Creek and
Painted Rocks ("Park Open daily all year", with dawn-to-dusk hours that leave camping unclear).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

FAS_SRC = "https://myfwp.mt.gov/fishMT/fas/{} (\"Open: {} to {}\", placeholder year), read 2026-10-20"
FAS = {
    6088: ("39754131", "05-01", "11-30"),
    6098: ("39753456", "01-01", "12-31"),
    6163: ("39754195", "01-01", "12-31"),
    14104: ("39753642", "01-01", "12-31"),
    14105: ("39753822", "01-01", "12-31"),
    14106: ("39754401", "01-01", "12-31"),
    14107: ("39753810", "01-01", "12-31"),
    14108: ("39753828", "01-01", "12-31"),
    14109: ("39754662", "01-01", "12-31"),
    14110: ("39753684", "01-01", "12-31"),
    14111: ("39753836", "01-01", "12-31"),
    14112: ("39753838", "01-01", "12-31"),
    14113: ("39754449", "01-01", "12-31"),
    14114: ("39753840", "01-01", "12-31"),
    14115: ("39754309", "01-01", "12-31"),
    14116: ("39754247", "01-01", "12-31"),
    14117: ("39753704", "01-01", "12-31"),
    14118: ("39753414", "01-01", "12-31"),
    14119: ("39753422", "01-01", "12-31"),
    14120: ("39754263", "01-01", "12-31"),
    14121: ("39753674", "01-01", "12-31"),
    14122: ("39754383", "01-01", "12-31"),
    14123: ("39754407", "01-01", "12-31"),
    14124: ("39753538", "01-01", "12-31"),
    14125: ("39754159", "01-01", "12-31"),
    14126: ("39754315", "01-01", "12-31"),
    14127: ("39753842", "01-01", "12-31"),
    14128: ("39754325", "01-01", "12-31"),
    14129: ("39753546", "01-01", "12-31"),
    14130: ("39753844", "01-01", "12-31"),
    14131: ("39753468", "01-01", "12-31"),
    14132: ("39754135", "01-01", "12-31"),
    14133: ("39754115", "01-01", "12-31"),
    14134: ("39753406", "01-01", "12-31"),
    14135: ("39754161", "01-01", "12-31"),
    14136: ("39753848", "01-01", "12-31"),
    14137: ("39754381", "01-01", "12-31"),
    14138: ("39753710", "01-01", "12-31"),
    14139: ("39753424", "01-01", "12-31"),
    14140: ("39753860", "01-01", "12-31"),
    14141: ("39753566", "01-01", "12-31"),
    14142: ("39753862", "01-01", "12-31"),
    14143: ("39753678", "01-01", "12-31"),
    14144: ("39753410", "01-01", "12-31"),
    14145: ("39754181", "01-01", "12-31"),
    14146: ("39753864", "01-01", "12-31"),
    14147: ("39754391", "01-01", "12-31"),
    14148: ("39754461", "01-01", "12-31"),
    14149: ("39753690", "01-01", "12-31"),
    14150: ("39754245", "01-01", "12-31"),
    14151: ("39753854", "01-01", "12-31"),
    14152: ("39753866", "01-01", "12-31"),
    14153: ("39753672", "01-01", "12-31"),
    14154: ("39753750", "01-01", "12-31"),
    14155: ("39753714", "01-01", "12-31"),
    14156: ("39753440", "01-01", "12-31"),
    14157: ("39754125", "01-01", "12-31"),
    14158: ("39754327", "01-01", "12-31"),
    14159: ("39753808", "01-01", "12-31"),
    14160: ("39754581", "01-01", "12-31"),
    14161: ("39754621", "01-01", "12-31"),
    14162: ("39754405", "01-01", "12-31"),
    14163: ("39753720", "01-01", "12-31"),
    14164: ("39754543", "01-01", "12-31"),
    14165: ("39754387", "01-01", "12-31"),
    14166: ("39753876", "01-01", "12-31"),
    14167: ("39754103", "01-01", "12-31"),
    14168: ("39753404", "01-01", "12-31"),
    14169: ("39753858", "01-01", "12-31"),
    14170: ("39753878", "01-01", "12-31"),
    14171: ("39753880", "01-01", "12-31"),
    14172: ("39753628", "01-01", "12-31"),
    14173: ("39753728", "01-01", "12-31"),
    14174: ("39753472", "01-01", "12-31"),
}

SP = "https://fwp.mt.gov/{} (Seasons & Hours: \"{}\"), read 2026-10-20"
PARKS = {
    6055: ({"year_round": True, "note": "First-come after the reservation period ends; fees year-round. Potable water is shut off for the winter."},
           SP.format("missouri-headwaters", "Park Open all year ... Fees are required year-round.")),
    6056: ({"year_round": False, "opens": "05-01", "closes": "10-31",
            "note": "Winter (Nov 1 to the Wednesday before Memorial Day): closed to motor vehicles, walk-in day use only, no overnight camping."},
           SP.format("stateparks/beavertail-hill", "Park Open May 1 through October 31 for vehicles")),
    6059: ({"year_round": False, "opens": "04-01", "closes": "10-31", "note": "Potable water May through September."},
           SP.format("stateparks/west-shore", "Campgrounds Open April through October")),
    6062: ({"year_round": True, "note": "B-loop is open year-round; A-loop, water and showers close in late September and reopen in May."},
           SP.format("logan", "B-loop open year-round")),
    6064: ({"year_round": True, "note": "Drinking water and flush toilets May 15 - Sep 27."},
           SP.format("stateparks/cooney", "Park Open 24 hours/day all year.")),
    6066: ({"year_round": True, "note": "From about Oct 1 to May 1 only 11 sites have electricity."},
           SP.format("stateparks/tongue-river-reservoir", "Campgrounds Open year round")),
    6070: ({"year_round": False, "opens": "04-01", "closes": "10-31", "note": "Water mid-May through September."},
           SP.format("stateparks/finley-point", "Campgound Open April through October")),
    6072: ({"year_round": True, "note": "The lower loop (sites 12-24) stays open year-round; the upper loop, water and showers close in early October and reopen in early May."},
           SP.format("whitefish-lake", "Park Open year-round, including ... the lower loop of campsites 12-24")),
    6073: ({"year_round": True, "note": "Electric hookups May 1 - Nov 30, limited facilities Dec 1 - May 1; potable water about May 15 - Oct 10."},
           SP.format("black-sandy", "Campground Open all year")),
    6076: ({"year_round": False, "opens": "04-01", "closes": "10-31", "note": "Water, showers and flush toilets mid-May to mid-September."},
           SP.format("stateparks/big-arm", "Campground Open April through October")),
    6077: ({"year_round": False, "opens": "05-01", "closes": "10-30", "note": "Opens May 1, earlier if conditions allow."},
           SP.format("lake-mary-ronan", "Campground Opens May 1 (earlier if conditions allow until October 30th).")),
    6081: ({"year_round": False, "opens": "05-01", "closes": "10-31", "note": "Opens May 1, earlier if conditions allow."},
           SP.format("thompson-falls", "Campground May 1 (earlier if conditions allow) through October")),
    6090: ({"year_round": True, "note": "No potable water."},
           SP.format("stateparks/ackley-lake", "Campground Open year-round")),
    6091: ({"year_round": True}, SP.format("stateparks/medicine-rocks", "Camping Open year-round.")),
}

DECISIONS = {}
for i, (fid, o, c) in FAS.items():
    season = {"year_round": True} if (o, c) == ("01-01", "12-31") else {"year_round": False, "opens": o, "closes": c}
    DECISIONS[i] = (season, FAS_SRC.format(fid, o, c))
DECISIONS.update(PARKS)

if __name__ == "__main__":
    run(DECISIONS)
