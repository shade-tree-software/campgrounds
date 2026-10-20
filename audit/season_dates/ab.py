#!/usr/bin/env python3
"""Alberta Parks: season from each campground's Alberta Parks page (2026-10-20).

    python3 -I audit/season_dates/ab.py [--apply]

Every campground page on albertaparks.ca heads its camping table "Season: Apr 30 - Oct 12" (or
"Season: Year-round"); park-level entries take the park's one campground page. That line is the
season; where the reservable dates in the table run a day past it, the wider span is kept. Where
the page says more than the line (winter loops, first-come winter camping, a loop closed for a
road failure), NOTES carries it.

Not written: 20 small recreation areas whose pages post no camping season, and Pinehurst Lake's
year-round line is overridden: its page says the campground itself is closed in winter.
Elkwater's "Jan 1 - Oct 11" is read as year-round: Loop C stays open all year.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

MON = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}

# id: (the page's "Season:" line, the page)
PAGES = {
    8817: ("Apr 30 - Oct 12", "https://www.albertaparks.ca/parks/kananaskis/bow-valley-pp/information-facilities/camping/bow-valley/"),
    8818: ("Apr 30 - Oct 12", "https://www.albertaparks.ca/parks/kananaskis/bow-valley-pp/information-facilities/camping/bow-river/"),
    8819: ("Jun 18 - Sep 7", "https://www.albertaparks.ca/parks/kananaskis/spray-valley-pp/information-facilities/camping/eau-claire/"),
    8820: ("Apr 30 - Sep 27", "https://www.albertaparks.ca/parks/kananaskis/bow-valley-pp/information-facilities/camping/willow-rock/"),
    8821: ("May 7 - Oct 12", "https://www.albertaparks.ca/parks/kananaskis/peter-lougheed-pp/information-facilities/camping/elkwood/"),
    8822: ("Apr 30 - Oct 12", "https://www.albertaparks.ca/parks/kananaskis/bow-valley-pp/information-facilities/camping/lac-des-arcs/"),
    8823: ("May 7 - Oct 12", "https://www.albertaparks.ca/parks/kananaskis/peter-lougheed-pp/information-facilities/camping/boulton-creek/"),
    8824: ("May 7 - Sep 13", "https://www.albertaparks.ca/parks/kananaskis/peter-lougheed-pp/information-facilities/camping/lower-lake/"),
    8826: ("Apr 30 - Oct 12", "https://www.albertaparks.ca/parks/kananaskis/bow-valley-pp/information-facilities/camping/three-sisters/"),
    8827: ("Jun 5 - Sep 12", "https://www.albertaparks.ca/parks/kananaskis/peter-lougheed-pp/information-facilities/camping/canyon/"),
    8830: ("Year-round", "https://www.albertaparks.ca/parks/south/beauvais-lake-pp/information-facilities/camping/beauvais-lake/"),
    8831: ("Apr 24 - Oct 12", "https://www.albertaparks.ca/parks/south/little-bow-pp/information-facilities/camping/little-bow/"),
    8833: ("May 15 - Sep 30", "https://www.albertaparks.ca/parks/south/park-lake-pp/information-facilities/camping/park-lake/"),
    8835: ("Apr 30 - Oct 13", "https://www.albertaparks.ca/parks/kananaskis/sheep-river-pp/information-facilities/camping/sandy-mcnabb/"),
    8838: ("May 15 - Sep 12", "https://www.albertaparks.ca/parks/kananaskis/little-elbow-pra/information-facilities/camping/little-elbow/"),
    8842: ("May 15 - Sep 30", "https://www.albertaparks.ca/parks/south/chinook-pra/information-facilities/camping/chinook/"),
    8849: ("May 15 - Sep 12", "https://www.albertaparks.ca/parks/kananaskis/elbow-falls-pra/information-facilities/camping/beaver-flats/"),
    8850: ("May 15 - Oct 12", "https://www.albertaparks.ca/parks/south/wyndham-carseland-pp/information-facilities/camping/wyndham-carseland/"),
    8851: ("May 14 - Sep 13", "https://www.albertaparks.ca/parks/kananaskis/sibbald-lake-pra/information-facilities/camping/sibbald-lake/"),
    8853: ("May 15 - Sep 14", "https://www.albertaparks.ca/parks/kananaskis/sheep-river-pp/information-facilities/camping/bluerock/"),
    8855: ("May 14 - Sep 12", "https://www.albertaparks.ca/parks/kananaskis/cataract-creek-pra/information-facilities/camping/cataract-creek/"),
    8856: ("May 8 - Oct 1", "https://www.albertaparks.ca/parks/south/dutch-creek-pra/information-facilities/camping/dutch-creek/"),
    8857: ("May 14 - Sep 12", "https://www.albertaparks.ca/parks/kananaskis/etherington-creek-pra/information-facilities/camping/etherington-creek/"),
    8858: ("Apr 24 - Oct 12", "https://www.albertaparks.ca/parks/south/little-bow-reservoir-pra/information-facilities/camping/little-bow-reservoir/"),
    8860: ("Year-round", "https://www.albertaparks.ca/parks/kananaskis/fisher-creek-pra/information-facilities/camping/fisher-creek/"),
    8863: ("May 12 - Sep 30", "https://www.albertaparks.ca/parks/south/castle-pp/information-facilities/camping/lynx-creek/"),
    8864: ("May 8 - Nov 14", "https://www.albertaparks.ca/parks/south/maycroft-pra/information-facilities/camping/maycroft/"),
    8865: ("May 15 - Oct 1", "https://www.albertaparks.ca/parks/south/oldman-river-north-pra/information-facilities/camping/oldman-river-north/"),
    8866: ("May 15 - Oct 1", "https://www.albertaparks.ca/parks/south/racehorse-pra/information-facilities/camping/racehorse/"),
    8867: ("May 14 - Sep 6", "https://www.albertaparks.ca/parks/kananaskis/north-fork-pra/information-facilities/camping/north-fork/"),
    8872: ("Year-round", "https://www.albertaparks.ca/parks/south/dinosaur-pp/information-facilities/camping/dinosaur/"),
    8873: ("May 1 - Nov 2", "https://www.albertaparks.ca/parks/south/tillebrook-pp/information-facilities/camping/tillebrook/"),
    8875: ("Year-round", "https://www.albertaparks.ca/parks/south/kinbrook-island-pp/information-facilities/camping/kinbrook-island/"),
    8876: ("Jan 1 - Oct 11", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/elkwater/"),
    8877: ("Jun 1 - Oct 11", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/beaver-creek/"),
    8878: ("May 13 - Oct 11", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/firerock/"),
    8879: ("May 13 - Nov 30", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/lakeview/"),
    8880: ("May 13 - Oct 11", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/old-baldy/"),
    8881: ("May 13 - Sep 6", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/ferguson-hill/"),
    8882: ("May 13 - Sep 6", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/lodgepole/"),
    8883: ("May 13 - Oct 11", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/reesor-lake/"),
    8884: ("Jun 1 - Sep 6", "https://www.albertaparks.ca/parks/south/cypress-hills-pp/information-facilities/camping/battle-creek/"),
    8887: ("Year-round", "https://www.albertaparks.ca/parks/central/crimson-lake-pp/information-facilities/camping/crimson-lake/"),
    8888: ("May 8 - Oct 3", "https://www.albertaparks.ca/parks/central/kootenay-plains-pra/information-facilities/camping/two-o-clock-creek/"),
    8890: ("May 8 - Oct 3", "https://www.albertaparks.ca/parks/central/thompson-creek-pra/information-facilities/camping/thompson-creek/"),
    8891: ("May 8 - Sep 19", "https://www.albertaparks.ca/parks/central/brazeau-reservoir-pra/information-facilities/camping/reservoir/"),
    8901: ("May 8 - Oct 4", "https://www.albertaparks.ca/parks/central/crescent-falls-pra/information-facilities/camping/crescent-falls/"),
    8903: ("Year-round", "https://www.albertaparks.ca/parks/central/elk-creek-pra/information-facilities/camping/elk-creek/"),
    8905: ("May 1 - Oct 31", "https://www.albertaparks.ca/parks/central/fairfax-lake-pra/information-facilities/camping/fairfax-lake/"),
    8906: ("May 1 - Oct 31", "https://www.albertaparks.ca/parks/kananaskis/fallen-timber-south-pra/information-facilities/camping/fallen-timber-south/"),
    8908: ("May 8 - Oct 3", "https://www.albertaparks.ca/parks/central/jackfish-lake-pra/information-facilities/camping/jackfish-lake/"),
    8915: ("Jun 1 - Sep 8", "https://www.albertaparks.ca/parks/central/ram-falls-pp/information-facilities/camping/ram-falls/"),
    8930: ("May 14 - Sep 21", "https://www.albertaparks.ca/parks/central/buck-lake-pra/information-facilities/camping/buck-lake/"),
    8932: ("May 1 - Oct 13", "https://www.albertaparks.ca/parks/kananaskis/ghost-reservoir-pra/information-facilities/camping/ghost-reservoir/"),
    8937: ("May 14 - Sep 21", "https://www.albertaparks.ca/parks/central/calhoun-bay-pra/information-facilities/camping/calhoun-bay/"),
    8940: ("May 14 - Sep 21", "https://www.albertaparks.ca/parks/central/gleniffer-reservoir-pra/information-facilities/camping/south-dyke/"),
    8945: ("May 1 - Oct 14", "https://www.albertaparks.ca/parks/kananaskis/waiparous-creek-pra/information-facilities/camping/waiparous-creek/"),
    8948: ("May 15 - Sep 7", "https://www.albertaparks.ca/parks/central/dillberry-lake-pp/information-facilities/camping/dillberry-lake/"),
    8951: ("May 13 - Sep 30", "https://www.albertaparks.ca/parks/central/big-knife-pp/information-facilities/camping/big-knife/"),
    8954: ("May 14 - Sep 7", "https://www.albertaparks.ca/parks/north/saskatoon-island-pp/information-facilities/camping/saskatoon-island/"),
    8956: ("May 13 - Sep 15", "https://www.albertaparks.ca/parks/central/pierre-grey-s-lakes-pp/information-facilities/camping/pierre-grey-s-lakes/"),
    8957: ("Year-round", "https://www.albertaparks.ca/parks/central/william-a-switzer-pp/information-facilities/camping/gregg-lake/"),
    8958: ("Year-round", "https://www.albertaparks.ca/parks/central/william-a-switzer-pp/information-facilities/camping/jarvis-lake/"),
    8959: ("May 14 - Sep 27", "https://www.albertaparks.ca/parks/north/williamson-pp/information-facilities/camping/williamson/"),
    8960: ("Year-round", "https://www.albertaparks.ca/parks/central/sulphur-gates-pra/information-facilities/camping/hikers-canyon/"),
    8961: ("May 15 - Oct 13", "https://albertaparks.ca/parks/north/kakwa-river-pra/information-facilities/camping/kakwa-river/"),
    8962: ("May 14 - Sep 28", "https://www.albertaparks.ca/parks/north/musreau-lake-pra/information-facilities/camping/musreau-lake/"),
    8963: ("May 1 - Oct 31", "https://www.albertaparks.ca/parks/central/rock-lake-pp/information-facilities/camping/rock-lake/"),
    8967: ("May 14 - Sep 28", "https://www.albertaparks.ca/parks/north/simonette-river-pra/information-facilities/camping/simonette-river/"),
    8973: ("May 5 - Oct 31", "https://www.albertaparks.ca/parks/central/nojack-pra/information-facilities/camping/nojack/"),
    8977: ("May 14 - Oct 12", "https://www.albertaparks.ca/parks/north/hilliard-s-bay-pp/information-facilities/camping/hilliard-s-bay/"),
    8982: ("May 14 - Sep 28", "https://www.albertaparks.ca/parks/north/waskahigan-river-pra/information-facilities/camping/waskahigan-river/"),
    8983: ("Apr 24 - Oct 30", "https://www.albertaparks.ca/parks/central/wabamun-lake-pp/information-facilities/camping/wabamun-lake/"),
    8984: ("May 14 - Oct 12", "https://www.albertaparks.ca/parks/north/lesser-slave-lake-pp/information-facilities/camping/marten-river/"),
    8986: ("May 14 - Sep 8", "https://www.albertaparks.ca/parks/north/cross-lake-pp/information-facilities/camping/cross-lake/"),
    8988: ("May 14 - Oct 13", "https://www.albertaparks.ca/parks/north/long-lake-pp/information-facilities/camping/long-lake/"),
    8990: ("May 15 - Oct 11", "https://www.albertaparks.ca/parks/north/chain-lakes-pra/information-facilities/camping/chain-lakes/"),
    8991: ("May 14 - Oct 11", "https://www.albertaparks.ca/parks/north/fawcett-lake-pra/information-facilities/camping/fawcett-lake/"),
    8992: ("May 15 - Oct 11", "https://www.albertaparks.ca/parks/north/lawrence-lake-pra/information-facilities/camping/lawrence-lake/"),
    8993: ("May 15 - Sep 15", "https://www.albertaparks.ca/parks/central/thunder-lake-pp/information-facilities/camping/thunder-lake/"),
    8995: ("May 14 - Sep 7", "https://www.albertaparks.ca/parks/north/whitney-lakes-pp/information-facilities/camping/ross-lake/"),
    8996: ("May 14 - Sep 8", "https://www.albertaparks.ca/parks/north/garner-lake-pp/information-facilities/camping/garner-lake/"),
    8997: ("May 14 - Oct 12", "https://www.albertaparks.ca/parks/north/sir-winston-churchill-pp/information-facilities/camping/sir-winston-churchill/"),
    8999: ("Year-round", "https://www.albertaparks.ca/parks/north/lakeland-pra/information-facilities/camping/pinehurst-lake/"),
    9000: ("May 14 - Sep 8", "https://www.albertaparks.ca/parks/north/beaver-lake-pra/information-facilities/camping/beaver-lake/"),
    9001: ("May 14 - Sep 8", "https://www.albertaparks.ca/parks/north/franchere-bay-pra/information-facilities/camping/franchere-bay/"),
    9003: ("Year-round", "https://www.albertaparks.ca/parks/north/lakeland-pra/information-facilities/camping/ironwood-lake/"),
    9004: ("Jun 3 - Sep 7", "https://www.albertaparks.ca/parks/north/kehiwin-pra/information-facilities/camping/kehiwin/"),
    9007: ("May 14 - Sep 28", "https://www.albertaparks.ca/parks/north/dunvegan-pp/information-facilities/camping/dunvegan/"),
    9008: ("May 14 - Oct 13", "https://www.albertaparks.ca/parks/north/queen-elizabeth-pp/information-facilities/camping/queen-elizabeth/"),
    9010: ("May 14 - Sep 28", "https://www.albertaparks.ca/parks/north/figure-eight-lake-pra/information-facilities/camping/figure-eight-lake/"),
    9011: ("May 14 - Oct 13", "https://www.albertaparks.ca/parks/north/moonshine-lake-pp/information-facilities/camping/moonshine-lake/"),
    9013: ("May 14 - Sep 28", "https://www.albertaparks.ca/parks/north/twin-lakes-pra/information-facilities/camping/twin-lakes/"),
    9014: ("May 14 - Sep 7", "https://www.albertaparks.ca/parks/north/notikewin-pp/information-facilities/camping/notikewin/"),
}

# Where the reservable dates in the table start earlier than the Season line.
WIDER_OPEN = {8879: "05-12", 8906: "04-30"}

NOTES = {
    8830: "Reservable May 8 - Sep 29; from Sep 30 first-come winter camping. Sites 1-15 stay open with power all winter; sites 16-77 close Oct 12.",
    8872: "Power hookups all year; the sani-dump has no rinse water from late October to early May.",
    8873: "Water, showers and flush toilets are off from early October until May; vault toilets all year.",
    8887: "Reservable May 13 - Sep 20; from Sep 21 first-come winter camping in Loop A only, with 13 sites ploughed and powered.",
    8957: "Reservable May 14 - Sep 7; Lakeside Loop (Loop L) stays open all year, first-come and unserviced.",
    8958: "Reservable May 14 - Sep 7.",
    9003: "Services are reduced after the September long weekend; the campground stays open after Thanksgiving with no snow removal or services.",
    9007: "Reservation-only camping until Sep 27.",
    9008: "Loop C stays open for reservation-only camping until Oct 12.",
    9014: "The lower loop and the boat launch are closed until further notice after a road failure; the upper loop is open first-come.",
}

# Pinehurst Lake: the Season line says Year-round, the page says "This campground is closed in
# winter" (6 first-come sites at the Pinehurst Lake A group-use area stay available, unserviced).
OVERRIDE = {
    # Elkwater's Season line runs "Jan 1 - Oct 11", but its table lists Loop C as reservable
    # Year-Round and the page says Loop C "remains open year-round (weather permitting)".
    8876: {"year_round": True, "note": "Loop C stays open year-round (weather permitting); the other loops close Oct 11. Water is shut off for the winter."},
    8999: {"year_round": False, "opens": "05-15",
           "note": "Reservable May 15 - Sep 7. Alberta Parks says the campground is closed in winter; 6 first-come sites at the Pinehurst Lake A group-use area stay available, unserviced, with no snow removal."},
}


def md(s):
    m, d = s.split()
    return f"{MON[m]:02d}-{int(d):02d}"


DECISIONS = {}
for i, (line, url) in PAGES.items():
    if i in OVERRIDE:
        season = dict(OVERRIDE[i])
    elif line.lower() == "year-round":
        season = {"year_round": True}
    else:
        a, b = (x.strip() for x in line.split(" - "))
        season = {"year_round": False, "opens": WIDER_OPEN.get(i, md(a)), "closes": md(b)}
    if i in NOTES and "note" not in season:
        season["note"] = NOTES[i]
    DECISIONS[i] = (season, f"{url} (the camping table's 'Season' line and notes), read 2026-10-20")

if __name__ == "__main__":
    run(DECISIONS)
