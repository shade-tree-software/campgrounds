#!/usr/bin/env python3
"""Oregon State Parks: season from each park's stateparks.oregon.gov profile and its
ReserveAmerica alerts (2026-10-20); fixes five profile links that pointed at other parks.

    python3 -I audit/season_dates/or.py [--apply]

Each OPRD profile tags the park "Year-round Camping" or "Seasonal Camping" and most say which
loops close when; the ReserveAmerica campground page's alert block gives the dates for several
seasonal parks. A park whose seasonal tag comes with no dates is written seasonal with no dates.

Links: five entries carried a profile parkId belonging to a different park (91 = Stonefield
Beach, 125 = Mitchell Point, 141 = Tolovana Beach, 133 = Bob Straub, 211 = no park); the right
ids come from reading the titles of profiles 1-260. Seven entries linked only to ReserveAmerica
and gain their profile link.

Not written: Cape Blanco and Umpqua Lighthouse, whose pages state no season.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run, CG  # noqa: E402

PROFILE = "https://stateparks.oregon.gov/index.cfm?do=park.profile&parkId={}"
FIX = {10615: (91, 76), 10616: (125, 129), 10619: (141, 20), 10629: (133, 142), 10645: (211, 151)}
ADD = {10624: 1, 10625: 155, 10627: 118, 10628: 8, 10631: 79, 10633: 149, 10637: 40}
PARK_OF = {292: 134, 10595: 50, 10597: 34, 10598: 58, 10599: 51, 10600: 75, 10601: 105, 10602: 165,
           10604: 70, 10605: 24, 10607: 65, 10609: 19, 10612: 85, 10617: 123, 10618: 4, 10620: 13,
           10622: 32, 10623: 69, 10632: 164, 10634: 10, 10635: 9, 10639: 26, 10640: 26, 10650: 7,
           10652: 195, 10653: 29, 11141: 16}
PARK_OF.update({i: new for i, (_, new) in FIX.items()})
PARK_OF.update(ADD)

YR, RA = "profile", "ra"
# id: (season, which page, quote)
S = {
    292: ({"year_round": True, "note": "Some loops close in winter."}, YR, "Year-round Camping ... Annual winter closures still in effect."),
    10595: ({"year_round": True, "note": "C loop is open year-round; A loop mid-March to early November, B loop mid-May to mid-October."}, YR, "C-loop is open year-round."),
    10597: ({"year_round": True, "note": "Water to the spigots is shut off and the flush toilets close in winter (a portable toilet stays)."}, YR, "Year-round Camping"),
    10598: ({"year_round": True, "note": "Some loops close for the winter."}, YR, "Year-round Camping ... Some camp loops close for the winter."),
    10599: ({"year_round": True}, YR, "Year-round Camping"),
    10600: ({"year_round": True}, YR, "Year-round Camping"),
    10601: ({"year_round": False, "opens": "03-15", "closes": "10-31"}, YR, "The campground is open mid March through October 31."),
    10602: ({"year_round": False, "opens": "05-01", "closes": "09-30"}, RA, "Park is open seasonally from May 1 - Sept 30"),
    10604: ({"year_round": True, "note": "Most of A Loop has been closed since January 2025 after storm damage (culvert failure); no repair date."}, YR, "Year-round Camping"),
    10605: ({"year_round": True, "note": "Part of the E loop stays open in winter; the whole loop is open March through October."}, RA, "Crooked River campground (E-loop): partial loop open in the winter, whole loop open March through October"),
    10607: ({"year_round": True, "note": "The tent sites close in the off season."}, YR, "Year-round Camping"),
    10609: ({"year_round": False, "note": "Water Memorial Day through September; OPRD publishes no camping dates."}, YR, "Seasonal Camping"),
    10612: ({"year_round": True}, YR, "Year-round Camping ... Tent campers are welcome year-round at campsites in Loops A and B."),
    10615: ({"year_round": True}, YR, "Year-round Camping"),
    10616: ({"year_round": True}, YR, "Year-round Camping"),
    10617: ({"year_round": False, "opens": "03-15", "closes": "10-31"}, YR, "The campground is open mid March through October 31"),
    10618: ({"year_round": False, "opens": "04-08", "closes": "10-31",
             "note": "Open from the second Thursday in April to the last Tuesday in October, weather permitting; limited first-come camping may be available in B loop in winter."},
            YR, "Campground is open from the second Thurs. in April until the last Tues. of Oct., weather permitting."),
    10619: ({"year_round": True, "note": "Several campsites and both yurts stay open all year; water to individual sites is off October to May 18, and winter sites are first-come as plowing allows."}, YR, "The park is open year-round for camping and day use."),
    10620: ({"year_round": False, "note": "First-come, first-served; OPRD publishes no camping dates."}, YR, "Seasonal Camping (first-come, first-served)"),
    10622: ({"year_round": True, "note": "The south loop and cabins stay open all year; the north loop closes Oct 1 and the middle loop Oct 15. Water hookups are off Oct 15 - Apr 30."}, YR, "The park is open-year-round for camping and day-use."),
    10623: ({"year_round": True}, YR, "Year-round Camping"),
    10624: ({"year_round": False, "opens": "04-15", "closes": "10-31"}, RA, "PARK IS CLOSED FROM LATE OCTOBER TO MID APRIL."),
    10625: ({"year_round": False, "opens": "05-01", "closes": "11-30",
             "note": "Closed Dec 1 - May 1 for winter flooding (the park sits on a peat bog); some closures run into June."}, YR, "The campground is closed seasonally from December 1 through May 1 due to winter flooding."),
    10627: ({"year_round": False, "note": "Water may stay off and restrooms closed until mid to late March; OPRD publishes no camping dates."}, YR, "Seasonal Camping"),
    10628: ({"year_round": True, "note": "Water hookups are off from late October through March; electric hookups, restrooms and showers year-round."}, YR, "Year-round Camping"),
    10629: ({"year_round": True}, YR, "Nehalem Bay campground is open year-round"),
    10631: ({"year_round": True, "note": "B Loop is open year-round; A Loop closes seasonally."}, YR, "B Loop, yurts, cabins, and the RV meeting hall are open year-round."),
    10632: ({"year_round": True}, YR, "Year-round Camping"),
    10633: ({"year_round": True}, YR, "Year-round Camping"),
    10634: ({"year_round": True, "note": "Indian Creek Campground is open year-round (first-come Oct 30 - Apr 9); McCormack Campground Apr 1 - Oct 31."}, YR, "Indian Creek Campground (open year-round, first-come first-served Oct. 30-April 9)"),
    10635: ({"year_round": True, "note": "First-come, first-served."}, YR, "Year-round camping (first-come, first-served)"),
    10637: ({"year_round": True}, YR, "Year-round Camping"),
    10639: ({"year_round": False, "opens": "05-01", "closes": "09-30"}, YR, "Jasper Point campground closes Oct. through April."),
    10640: ({"year_round": True}, YR, "The main park campsites and deluxe cabins are open year round"),
    10645: ({"year_round": True, "note": "18 or more of the electric sites stay open year-round; the tent sites are seasonal (May - October)."}, YR, "48 electrical sites with water (18+ sites open year-round)"),
    10650: ({"year_round": False, "note": "OPRD publishes no camping dates."}, YR, "Seasonal Camping"),
    10652: ({"year_round": True, "note": "First-come Nov 1 - Mar 31; reservable April - October."}, YR, "Year-round Camping"),
    10653: ({"year_round": True, "note": "A Loop is open year-round (first-come Nov 1 - Mar 31); B, G and T loops close in winter."}, YR, "A Loop (open year-round, sites are first-come, first-served from Nov. 1 to March 31)"),
    11141: ({"year_round": True, "note": "Only the cabins and four sites stay open in winter; the electric site and tent sites close."}, YR, "All cabins and four sites are open year-round"),
}

EXTRA = {
    292: {"status": {"operating": "temporarily_closed", "reopens": "after spring 2027",
                     "note": "Campground and day-use area closed Aug 3, 2026 for GO Bond work (C and D loop utilities, D loop restroom/shower); work expected through spring 2027."},
          "_sources": {"status": PROFILE.format(134) + " (alert), read 2026-10-20"}},
    10612: {"status": {"operating": "temporarily_closed", "reopens": "not announced",
                       "note": "Closed from Aug 1, 2026 to replace two culverts; reservations are on hold beyond August 2026."},
            "_sources": {"status": PROFILE.format(85) + " (alert), read 2026-10-20"}},
}


def fix_links():
    cg = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in cg}
    for i, (old, new) in FIX.items():
        w = by[i]["website"]
        if PROFILE.format(new) + "\n" in w:
            continue
        assert PROFILE.format(old) + "\n" in w, i
        by[i]["website"] = w.replace(PROFILE.format(old) + "\n", PROFILE.format(new) + "\n")
        print(f"  link {i} {by[i]['name']}: parkId {old} -> {new}")
    for i, p in ADD.items():
        w = by[i]["website"]
        if "stateparks.oregon.gov" not in w:
            by[i]["website"] = PROFILE.format(p) + "\n" + w
            print(f"  link {i} {by[i]['name']}: + profile {p}")
    if "--apply" in sys.argv:
        with open(CG, "w", encoding="utf-8") as f:
            json.dump(cg, f, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    fix_links()
    cg ={e["id"]: e for e in json.load(open(CG, encoding="utf-8"))}
    decisions = {}
    for i, (season, where, quote) in S.items():
        if where == YR:
            src = f"{PROFILE.format(PARK_OF[i])} (\"{quote}\"), read 2026-10-20"
        else:
            ra = next(w for w in cg[i]["website"].split() if "reserveamerica" in w)
            src = f"{ra} (alert: \"{quote}\"), read 2026-10-20"
        decisions[i] = (season, src)
    run(decisions, EXTRA)
