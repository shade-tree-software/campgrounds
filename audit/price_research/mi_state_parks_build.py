#!/usr/bin/env python3
"""Build mi_state_parks.json from the parsed DNR park rate table (2026-10-09).

    python3 audit/price_research/mi_state_parks_build.py TABLES.json

TABLES.json comes from mi_dnr_tables.py. An entry gets nightly_low/high = the
min/max campsite rate (lodging, group and walk/hike-in rows excluded) across the
DNR campground rows it covers. A whole-park entry covers all of the park's
drive-in campgrounds; a named campground covers just its own row. Entries are
matched by park name when the park has one campground, else by MAP below.
"""
import json
import re
import sys

MAP = {
 188: [('Ludington', 'Beechwood'), ('Ludington', 'Cedar'), ('Ludington', 'Pines')],
 189: [('Tahquamenon Falls', 'Lower Falls-Portage')],
 415: [('Tahquamenon Falls', 'Lower Falls-Hemlock')],
 410: [('Tahquamenon Falls', 'Rivermouth Campground')],
 411: [('Tahquamenon Falls', 'Rivermouth Pines Semi-Modern/Rustic')],
 460: [('Holland', 'Lake Macatawa Pines and Woodstock loops'), ('Holland', 'Beach campground')],
 562: [('Wilderness', 'Full Hook-up'), ('Wilderness', 'Pines Campground'),
       ('Wilderness', 'Lakeshore Campground - East and West')],
 566: [('Straits', 'Straits Campground'), ('Straits', 'Straits Semi-Modern (No Electric)')],
 571: [('Warren Dunes', 'Hildebrandt Campground - Semi Modern'), ('Warren Dunes', 'Mount Randall Campground')],
 780: [('Porcupine Mountains', 'Union Bay')],
 786: [('Indian Lake', 'South Unit - Campground'), ('Indian Lake', 'West Shore Campground')],
 788: [('Young', 'Oak Campground'), ('Young', 'Spruce Campground'), ('Young', 'Terrace Campground')],
 793: [('Interlochen', 'Green Lake Rustic'), ('Interlochen', 'North Campground'), ('Interlochen', 'South Campground')],
 794: [('South Higgins Lake', 'East Campground'), ('South Higgins Lake', 'West Campground')],
 3644: [('North Higgins Lake', 'East Campground'), ('North Higgins Lake', 'West Campground')],
 3600: [('Baraga', 'South Camp (sites 1-40)'), ('Baraga', 'North Camp (sites 41-95)')],
 3601: [('Bay City Recreation Area', 'Bay City Campground')],
 3604: [('Van Riper', 'Modern Campground Loops 1 and 2'), ('Van Riper', 'Rustic Campground Loop')],
 3607: [('Waterloo', 'Sugarloaf Lake Campground')],
 3608: [('Waterloo', 'Portage Lake Campground')],
 3609: [('Waterloo', 'Green Lake Campground')],
 3611: [('Proud Lake', 'campground')],
 3619: [('Holly', 'Hickory & Trillium Loops'), ('Holly', 'Aspen, Maple, & Oak Loops')],
 3621: [('Ionia', 'Modern Campground')],
 3622: [('Sleepy Hollow', 'Sleepy Hollow Campground')],
 3625: [('Rifle River', 'Grousehaven Lake')],
 3626: [('Rifle River', 'Rustic Campgrounds (Spruce, Ranch, & Devoe)')],
 14043: [('Rifle River', 'Rustic Campgrounds (Spruce, Ranch, & Devoe)')],
 14044: [('Rifle River', 'Rustic Campgrounds (Spruce, Ranch, & Devoe)')],
 3627: [('Algonac', 'Riverfront')],
 3628: [('Algonac', 'Wagon Wheel')],
 3630: [('Yankee Springs', 'Gun Lake Campground')],
 3631: [('Yankee Springs', 'Deep Lake')],
 3633: [('Muskegon', 'Lake Michigan Campground')],
 3634: [('Muskegon', 'Channel Campground')],
 3642: [('Petoskey', 'Dunes')],
 3643: [('Pinckney', 'Bruin Lake')],
 14042: [('Pinckney', 'Crooked Lake')],
 3647: [('Highland', 'Rustic Campground')],
 14037: [('Traverse City', 'Central Loop'), ('Traverse City', 'East Loop'), ('Traverse City', 'West Loop')],
 14038: [('Brighton', 'Bishop Lake')],
 14039: [('Brighton', 'Appleton Lake')],
 14040: [('Brighton', 'Murray Lake Campground')],
 14045: [('Porcupine Mountains', 'Presque Isle')],
}
COLS = ['Modern camping full-hookup rate', 'Modern camping 50 AMP rate', 'Modern camping 20/30 AMP rate',
        'Semi-modern camping 50 AMP rate', 'Semi-modern (either 20/30 AMP or toilets) rate', 'Rustic camping rate']
SRC = ("https://www.michigan.gov/dnr/things-to-do/camping-and-lodging/"
       "camping-and-lodging-rates-and-operating-dates (DNR camping rates table)")


def n(s):
    s = s.lower().replace('&', 'and').replace('.', '')
    return ' '.join(re.sub(r"[^a-z0-9]+", ' ', s).split())


def main():
    P = json.load(open(sys.argv[1]))['parks']
    camp = [r for r in P if r['Location type'] == 'campground']
    parks = sorted({r['Park name'] for r in camp})

    def row(park, cg):
        c = [r for r in P if r['Park name'] == park and r['Campground or overnight lodging name'] == cg]
        assert len(c) == 1, (park, cg)
        return c[0]

    rows = [r for r in json.load(open('campgrounds.json'))
            if r.get('kind') != 'family' and r['state'] == 'MI' and r.get('ownership') == 'state'
            and not r.get('policy_ref')]
    out, skip = [], []
    for r in rows:
        if r.get('fees'):
            continue
        if r['id'] in MAP:
            src = [row(*x) for x in MAP[r['id']]]
        else:
            nm = n(r['name'])
            ps = sorted([p for p in parks if re.search(r'\b' + re.escape(n(p)) + r'\b', nm)], key=len, reverse=True)[:1]
            src = [x for x in camp if ps and x['Park name'] == ps[0]]
            if len(src) != 1:
                skip.append((r['id'], r['name']))
                continue
        vals = [int(v) for s in src for col in COLS if '/group' not in s[col]
                for v in re.findall(r'\$(\d+)', s[col])]
        if not vals:
            skip.append((r['id'], 'no campsite rate'))
            continue
        out.append({"id": r['id'],
                    "fees": {"nightly_low": min(vals), "nightly_high": max(vals), "currency": "USD"},
                    "source": SRC + ": " + "; ".join(s['Park name'] + ' / ' + s['Campground or overnight lodging name']
                                                     for s in src)})
    json.dump(out, open('audit/price_research/mi_state_parks.json', 'w'), indent=1, ensure_ascii=False)
    print(len(out), 'findings; skipped', skip)


if __name__ == '__main__':
    main()
