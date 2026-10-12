#!/usr/bin/env python3
"""Per-park 2026 camping rates for the 40 Missouri State Parks entries (2026-10-12).

    python3 -I audit/mo_registry/build.py            # print the proposals
    python3 -I audit/mo_registry/build.py --json OUT # also write them

rates_2026_on.json / rates_2026_off.json are the agency's 2026 on- and off-season rate charts
(mostateparks.com/media/pdf/2026-season-camping-fees and -0), read with `pdftotext -bbox` and each
price assigned to the column whose header sits over it. A few chart rows wrap (a sub-campground,
a weekday band, a value on its own line), so the row names below are fixed by hand against the
chart's text layout before the per-park figures are built. Base rate = the basic site, as for the
other agencies (docs/campground-schema.md 4.2); hookup prices go in the note.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ID = {"Arrow Rock SHS": 1824, "Babler Memorial, Dr. Edmund A. SP": 1830, "Baker, Sam A. SP": 1850,
      "Battle of Athens SHS": 1825, "Bennett Spring SP": 1826, "Big Lake SP": 1827, "Crowder SP": 1828,
      "Cuivre River SP": 1829, "Echo Bluff SP": 1831, "Finger Lakes SP": 1832, "Graham Cave SP": 1833,
      "Hawn SP": 1835, "Johnson’s Shut-Ins SP": 1836, "Knob Noster SP": 1837, "Lake of the Ozarks SP": 1839,
      "Lake Wappapello SP": 1838, "Lewis and Clark SP": 1840, "Long Branch SP": 13730, "Meramec SP": 1842,
      "Montauk SP": 1843, "Onondaga Cave SP": 1844, "Pershing SP": 1845, "Pomme de Terre SP": (1846, 1847),
      "Roaring River SP": 1848, "Robertsville SP": 1849, "St. Francois SP": 1851, "St. Joe SP": 1852,
      "Stockton SP": 1853, "Table Rock SP": 1854, "Thousand Hills SP": 1855, "Trail of Tears SP": 1856,
      "Truman, Harry S SP": 1834, "Twain, Mark SP": 1841, "Van Meter, Annie and Abel SP": 1857,
      "Wakonda SP": 1858, "Wallace SP": 1859, "Washington SP": 1861, "Watkins Mill SP": 1860,
      "Weston Bend SP": 1862}


def fix(rows, season):
    """(park, days, vals) with the wrapped rows put back under their park."""
    out, seen = [], {}
    for r in rows:
        name, days, vals = r["park"], r["days"], r["vals"]
        seen[name] = seen.get(name, 0) + 1
        if name in ("Asher Creek Camground", "Ridge Campground"):
            loop = "Ridge" if (season == "off" or name.startswith("Ridge")) else "Asher Creek"
            name, days = "Lake Wappapello SP", f"{loop} loop"
        elif name in ("Puma Camground", "Badger and Coyote Campgrounds"):
            days = ("Puma loop " if name.startswith("Puma") else "Badger/Coyote loops ") + days
            name = "Twain, Mark SP"
        elif name == "Holiday":
            name, days = "Echo Bluff SP", "Holiday wknds"
        elif name.startswith("(applicable to Fri./Sat./Sun."):
            name, days = "Truman, Harry S SP", "Holiday wknds (Fri/Sat/Sun nights)"
        elif season == "on" and name == "Echo Bluff SP" and days == "all":
            days = "Sun. – Thurs."                    # the weeknight E/W price, wrapped onto its own line
        elif season == "on" and name == "Stockton SP" and days == "all":
            name = "Table Rock SP"                     # Table Rock's name sits on the line below its prices
        elif season == "off" and name == "Crowder SP" and seen[name] == 2:
            name = "Cuivre River SP"
        elif season == "off" and name == "Lewis and Clark SP" and seen[name] == 2:
            name = "Long Branch SP"                    # Long Branch's sewer price wrapped above its name
        elif season == "off" and name == "Roaring River SP" and seen[name] == 2:
            name = "Robertsville SP"
        out.append((name, days, vals))
    return out


def merged(rows):
    """park -> {days: vals}, merging a wrapped value into its row."""
    parks = {}
    for name, days, vals in rows:
        parks.setdefault(name, {}).setdefault(days, {}).update(vals)
    return parks


LABEL = [("basic", "basic"), ("e30", "electric 30A"), ("e50", "electric 50A"), ("ew30", "electric/water 30A"),
         ("ew50", "electric/water 50A"), ("sew30", "sewer/electric/water 30A"), ("sew50", "sewer/electric/water 50A")]


def describe(bands):
    parts = []
    for days, v in bands.items():
        items = [f"{lab} ${v[k]:g}" for k, lab in LABEL if k in v]
        if items:
            parts.append(("" if days == "all" else days.replace("Sun. – Thurs.", "Sun-Thu").replace("Fri. – Sat.", "Fri-Sat") + ": ") + ", ".join(items))
    return "; ".join(parts)


def build():
    on = merged(fix(json.load(open(os.path.join(HERE, "rates_2026_on.json"), encoding="utf-8")), "on"))
    off = merged(fix(json.load(open(os.path.join(HERE, "rates_2026_off.json"), encoding="utf-8")), "off"))
    props = []
    for park, ids in ID.items():
        ids = ids if isinstance(ids, tuple) else (ids,)
        bon, boff = on.get(park, {}), off.get(park, {})
        basics = [v["basic"] for b in (bon, boff) for v in b.values() if "basic" in v]
        if not basics:
            raise SystemExit(f"no basic rate for {park}")
        # the on-season weekend (or all-week) band is the reference for the hookup surcharges
        ref = next((bon[d] for d in bon if d in ("all", "Fri. – Sat.")), None) or next(iter(bon.values()))
        sur = {}
        if "basic" in ref:
            e = ref.get("e30", ref.get("e50"))
            if e:
                sur["electric"] = e - ref["basic"]
            full = ref.get("sew50", ref.get("sew30"))
            if full:
                sur["full_hookup"] = full - ref["basic"]
        note = (f"Missouri State Parks 2026 rates. On-season: {describe(bon)}. Off-season: {describe(boff) or 'closed'}. "
                "Charged by the site's utilities, used or not; $6.50 online reservation fee per site.")
        fees = {"nightly_low": min(basics), "nightly_high": max(basics), "currency": "USD", "checked": "2026"}
        if sur:
            fees["surcharges"] = sur
        fees["note"] = note
        for i in ids:
            props.append({"id": i, "park": park, "fees": fees})
    return props


if __name__ == "__main__":
    props = build()
    for p in props:
        f = p["fees"]
        print(p["id"], p["park"], f["nightly_low"], f["nightly_high"], f.get("surcharges"), "|", f["note"][27:260])
    if "--json" in sys.argv:
        json.dump(props, open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
