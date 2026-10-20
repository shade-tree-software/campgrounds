#!/usr/bin/env python3
"""Missouri State Parks: season from each park's camping page (2026-10-20).

    python3 -I audit/season_dates/mo.py [--apply]

mostateparks.com/park/<park>/camping has a table per campground: "Available Dates",
"Showers/Water Available", "Reservations". Available Dates is the season. Most campgrounds
stay open all year with water and showers off in winter, so the note carries the
showers/water window. Where one entry covers a park with several campgrounds, the season
is the widest of them and the note names the ones that close.

Not written: none of the 38 park entries lacked a table. The 235 Missouri Department of
Conservation areas (mdc.mo.gov) post no camping season; MDC's rule (3 CSR 10-11.140)
allows camping in designated areas, not a season.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

SRC = "https://mostateparks.com/park/{}/camping (campground table, 'Available Dates' column), read 2026-10-20"
YR = {"year_round": True}


def yr(note=None):
    return dict(YR, note=note) if note else dict(YR)


def sw(window):
    return f"Showers and water {window}."


T = {  # id: (slug, season)
    1824: ("arrow-rock-hs", yr(sw("Apr 1-Oct 31"))),
    1825: ("battle-of-athens-hs", yr(sw("Apr 15-Oct 31"))),
    1826: ("bennett-spring", yr("Campground #1 (full hookups) is open year-round; #2 and #3 Apr 15-Oct 31, #4 and #5 Feb 25-Oct 31. Showers and water at #1 Apr 15-Oct 15.")),
    1827: ("big-lake", yr(sw("Apr 15-Oct 31"))),
    1828: ("crowder", {"year_round": False, "opens": "03-01", "closes": "11-30", "note": sw("Apr 15-Oct 31")}),
    1829: ("cuivre-river", yr(sw("Apr 15-Oct 31"))),
    1830: ("dr-edmund-babler-memorial", yr(sw("Apr 1-Oct 31"))),
    1831: ("echo-bluff", yr(sw("Apr 1-Oct 31"))),
    1832: ("finger-lakes", yr(sw("Apr 1-Oct 31"))),
    1833: ("graham-cave", yr(sw("Apr 1-Oct 31"))),
    1834: ("harry-s-truman", yr("Devil's Backbone is open year-round; Bobcat Run, Raccoon Ridge and Thorny Ridge Mar 1-Oct 31, Buck Ridge and Wild Turkey Ridge Apr 1-Oct 31. Showers and water Apr 1-Oct 31.")),
    1835: ("hawn", yr(sw("Apr 1-Oct 31"))),
    1836: ("johnsons-shut-ins", yr("Showers and water Apr 1-Oct 31, except Loop 3 all year.")),
    1837: ("knob-noster", yr(sw("Apr 15-Oct 31"))),
    1838: ("lake-wappapello", yr("Ridge is open year-round (sites 37-47 closed November through March); Asher Creek Apr 1-Oct 31. Showers and water Apr 1-Oct 31.")),
    1839: ("lake-of-the-ozarks", yr(sw("Apr 1-Oct 31"))),
    1840: ("lewis-and-clark", yr(sw("Apr 15-Oct 31"))),
    1841: ("mark-twain", yr(sw("Apr 15-Oct 31"))),
    1842: ("meramec", yr(sw("Apr 1-Oct 31"))),
    1843: ("montauk", yr(sw("Feb 25-Oct 31"))),
    1844: ("onondaga-cave", yr(sw("Apr 1-Oct 31"))),
    1845: ("pershing", yr(sw("Apr 15-Oct 31"))),
    1846: ("pomme-de-terre", yr("Loops 200 and 300 are open March through November only. Showers and water Apr 1-Oct 31.")),
    1848: ("roaring-river", yr("Campground #1 is open year-round, with showers and water; #2 and #3 Feb 25-Oct 31.")),
    1849: ("robertsville", yr(sw("Apr 1-Oct 31"))),
    1850: ("sam-baker", yr("Campground 2 is open year-round; Campground 1 Apr 1-Oct 31. Showers and water Apr 1-Oct 31.")),
    1851: ("st-francois", yr(sw("Apr 1-Oct 31"))),
    1852: ("st-joe", yr(sw("Apr 1-Oct 31"))),
    1853: ("stockton", yr(sw("Apr 1-Oct 31"))),
    1854: ("table-rock", yr(sw("Mar 1-Nov 30"))),
    1855: ("thousand-hills", yr("Campground 2 (electric) is open year-round; Campground 1 Apr 1-Oct 31. Showers and water Apr 1-Oct 31.")),
    1856: ("trail-of-tears", yr("The Mississippi River Campground is open year-round; the basic Lake Boutin Campground May 1-Oct 31. Showers and water Apr 1-Oct 31.")),
    1857: ("van-meter", yr(sw("Apr 15-Oct 31"))),
    1859: ("wallace", yr(sw("Apr 15-Oct 31"))),
    1860: ("watkins-woolen-mill", yr("Sites 1-34, 98 and 99 are open year-round; sites 35-97 Apr 15-Oct 31. Showers and water Apr 15-Oct 31.")),
    1861: ("washington", yr(sw("Apr 1-Oct 31"))),
    1862: ("weston-bend-state-park/weston-bend-state-park", yr(sw("Apr 15-Oct 31"))),
    13730: ("long-branch", yr("Normally year-round (showers and water Apr 1-Oct 31); closed for all of 2026 for construction.")),
}

# Source = the mostateparks.com page the entry itself links (Weston Bend's link was the park
# home page; its camping page sits one level deeper).
import json as _json
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SITE = {e["id"]: e.get("website") or "" for e in _json.load(open(os.path.join(_ROOT, "campgrounds.json"), encoding="utf-8"))}
DECISIONS = {}
for i, (slug, season) in T.items():
    urls = [w for w in _SITE[i].split() if "mostateparks.com" in w and w.endswith("/camping")]
    src = f"{urls[0]} (campground table, 'Available Dates' column), read 2026-10-20" if urls else SRC.format(slug)
    DECISIONS[i] = (season, src)

# 1855's note had the two campgrounds the wrong way round.
NOTE_1855_OLD = "(CG1 year-round electric loop, CG2 seasonal)"
NOTE_1855_NEW = "(CG2's electric loop open year-round, CG1 April-October)"

if __name__ == "__main__":
    import json
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if "--apply" in sys.argv:
        p = os.path.join(root, "campgrounds.json")
        cg = json.load(open(p, encoding="utf-8"))
        for e in cg:
            if e["id"] == 1855 and NOTE_1855_OLD in e["note"]:
                e["note"] = e["note"].replace(NOTE_1855_OLD, NOTE_1855_NEW)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(cg, f, ensure_ascii=False, indent=2)
                    f.write("\n")
                print("1855 note corrected")
    run(DECISIONS)
