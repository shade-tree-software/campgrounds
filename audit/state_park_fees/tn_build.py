"""TN findings: each park's reservation calendar on reserve.tnstateparks.com, read 2026-10-12.

    python3 -I tn_build.py SUMMARY.json OUT

SUMMARY is tn_parse.py's digest (tn_calendar_summary_2026-10-12.json): every bookable night's price for
two weeks from 2026-10-13 and from 2027-06-15, read with a Tennessee zip, per campground of the park.
Tennessee prices by site and night (demand pricing) and publishes no table; the quoted rate leaves out tax
and the 'non-refundable $5.00 Advanced Reservation Fee per campsite' (the calendar page's policies). No
registry row covers Tennessee, so the fee goes on each entry. Where the park's campground page makes some
of the calendar's sites tent or primitive sites (tn_parse.py SITE_KIND), the range is the RV sites' and the
others are named in the note."""
import json, os, sys
summary, out_path = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
S = json.load(open(summary))
D = "2026-10-12"


def rng(slug, keys):
    vals = [w[k] for w in S[slug].values() for k in keys if k in w]
    return (min(v["min"] for v in vals), max(v["max"] for v in vals)) if vals else None


def say(slug, key):
    lo, hi = rng(slug, [key])
    return f"${lo}" if lo == hi else f"${lo}-{hi}"


# id: (slug, [campground keys from the summary], extra sentence)
M = {191: ("reelfoot-lake", ["South|rv"], ""), 4410: ("reelfoot-lake", ["Airpark|rv"], ""),
     700: ("harrison-bay", ["|rv"], f" The primitive tent-only sites (D loop) are {say('harrison-bay', '|tent')}."),
     4386: ("pickwick-landing", ["Bruton Branch Primitive|primitive"],
            " Pickwick Landing's Main Campground is closed; Bruton Branch is open."),
     4387: ("t-o-fuller", ["|rv"], f" One site (19) is {say('t-o-fuller', '|odd')}."),
     4388: ("south-cumberland", ["Foster Falls|rv"], ""),
     4389: ("tims-ford", ["Fairview|rv"], ""), 4390: ("tims-ford", ["Main|rv"], ""),
     4391: ("hiwassee-ocoee", ["|rv"], " The calendar says the campground closes for renovation from early spring 2027 "
                                       "until summer 2028, and it listed no sites for June 2027."),
     4392: ("david-crockett", ["Campground 1|rv", "Campground 2|rv"], ""), 4393: ("chickasaw", ["RV Area|rv"], ""),
     4394: ("old-stone-fort", ["|rv"], ""), 4395: ("henry-horton", ["RV|rv"], ""),
     4396: ("fort-pillow", ["|rv"], f" Sites 18-20, 31 and 32 are {say('fort-pillow', '|lowamp')} (the park says some of its "
                                     f"sites have only 20-amp electric, with water nearby) and the nine primitive tent sites "
                                     f"{say('fort-pillow', '|tent')}."),
     4397: ("fall-creek-falls", ["Area A|rv", "Area B|rv", "Area C|rv", "Area D|rv", "Area E|rv"], ""),
     4398: ("mousetail-landing", ["Main|rv"], f" The Spring Creek campground's primitive sites are "
                                              f"{say('mousetail-landing', 'SpringCrk|rv')}."),
     4399: ("natchez-trace", ["Pin Oak|rv"], ""),
     4400: ("natchez-trace", ["Campground One|rv"], " The calendar calls it Campground One (camping units 25 ft and under) "
                                                   "and listed none of its sites for June 2027."),
     4401: ("rock-island", ["|rv"], ""),
     4402: ("cumberland-mountain", ["Area 1|rv", "Area 2|rv", "Area 3|rv", "Area 4|rv", "Area 5|rv"], ""),
     4403: ("edgar-evins", ["|rv"], f" The nine primitive walk-in sites are {say('edgar-evins', '|tent')}."),
     4404: ("cedars-of-lebanon", ["Area 1|rv", "Area 2|rv", "Area 3|rv"], ""),
     4405: ("roan-mountain", ["|rv"], f" The tent sites (water, no electric) are {say('roan-mountain', '|tent')}."),
     4406: ("panther-creek", ["|rv"], ""), 4407: ("big-ridge", ["|rv"], ""), 4408: ("bledsoe-creek", ["|rv"], ""),
     4409: ("paris-landing", ["|rv"], f" The 18 primitive sites are {say('paris-landing', '|tent')}."),
     4411: ("warriors-path", ["|rv"], ""), 4412: ("indian-mountain", ["|rv"], ""),
     13721: ("nathan-bedford-forrest", ["Happy Hollow|rv"], " Closed for renovation through 2026; its sites are on the "
                                                            "calendar again for June 2027."),
     13724: ("pickett", ["|rv", "|water"], f" Sites with water only {say('pickett', '|water')}, with electric too "
                                           f"{say('pickett', '|rv')}. Closed for renovation; its sites are on the calendar "
                                           f"again for June 2027.")}
out = []
for eid, (slug, keys, extra) in sorted(M.items()):
    r = rng(slug, keys)
    if not r:
        print("no prices", eid, slug, keys)
        continue
    lo, hi = r
    what = "primitive campsite" if keys[0].endswith("|primitive") else "campsite"
    price = f"${lo}" if lo == hi else f"${lo}-{hi}"
    text = (f"{price} a night for a {what}, plus tax and a $5 reservation fee per site." + extra +
            (" The price changes by site and night, higher on weekends and busy dates." if lo != hi else "") +
            f" Every bookable night on the park's reservation calendar for two weeks from 2026-10-13 and from "
            f"2027-06-15, read {D}.")
    out.append({"id": eid, "name": rows[eid]['name'],
                "fees": {"nightly_low": lo, "nightly_high": hi, "currency": "USD", "reservation_fee": 5,
                         "checked": "2026", "note": text},
                "source": f"https://reserve.tnstateparks.com/{slug}/campsites (Calendar View, every site's price for the two "
                          f"weeks from 2026-10-13 and from 2027-06-15 with a Tennessee zip, read {D}; '$5.00 Advanced "
                          f"Reservation Fee per campsite' in its policies)"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'TN findings')
for x in out:
    print(x['id'], x['name'][:40], x['fees']['nightly_low'], x['fees']['nightly_high'], '|', x['fees']['note'][:300])
