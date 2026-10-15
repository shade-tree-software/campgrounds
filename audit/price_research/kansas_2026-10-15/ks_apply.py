"""The Kansas state-park pass (2026-10-15): python3 -I ks_apply.py [--apply].

KDWP's fee page (kdwp_fees_page.txt, read through the browser: Akamai refuses curl) lists the current fees and the
ones beginning 2026-11-01. AWH 2026-10-15: no Kansas trip before November, so record the new ones as current.

- campground_policies.json gains `state:KS`, the statewide charges every Kansas state park adds on top of a site's
  price: the $2.75 processing fee per stay, the $7 daily vehicle permit, the 14-night limit.
- The 35 KDWP state parks carry their own base rate ($17.75 daily camping permit) and the utility add-ons
  (one utility $11, three $15; a prime site +$2 April-September). An entry with its own price inherits no agency
  surcharges (docs/campground-schema.md §3), so they live on the entry, as South Dakota's electric fee does.
  Two utilities ($13) have no surcharge key and are named in the fee note.
- The 25 state fishing lakes (free camping, outside the park permit system) and the Kansas State Fairgrounds RV
  Park (the State Fair Board's, not KDWP's) take policy_ref "none" so they inherit none of it. The Fairgrounds is
  priced from its own page.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

D = "2026-10-15"
KDWP = "https://ksoutdoors.gov/licenses-permits-fees/kansas-state-park-entrance-and-camping-fees"
QUOTES = ["Beginning November 1, 2026 several Kansas State Park fees will change",
          "Daily Camping Permit ... $12.75 per night $17.75 per night",
          "Utility Fees - Water, Electric, and Sewage ... $11.00 per night for one utility $13.00 per night for two "
          "utilities $15.00 per night for three utilities",
          "Prime Site Fee ... designated sites on stays April 1-September 30 ... $2.00 per night",
          "a $2.75 processing fee will apply to each camping stay",
          "Daily Vehicle Permit ... $5.00 $7.00", "*including transaction fees."]
SRC = f"{KDWP} ({'; '.join(repr(q) for q in QUOTES)}), read {D}; the fees beginning 2026-11-01 recorded as current (AWH {D})"
FEE_NOTE = ("KDWP's statewide schedule from November 1, 2026: a daily camping permit of $17.75 a night per camping "
            "unit, plus utilities at $11 a night for one (electric), $13 for two (water and electric) or $15 for "
            "three (full hookups), and $2 a night more for a designated prime site April-September. A $2.75 "
            "processing fee per stay and a vehicle permit ($7 a day) are charged on top. The add-ons listed are the kinds of site this campground has, per KDWP's park page; water and electric shows as electric +$11 plus water +$2. Read {d}.")
ROW = {
    "booking": {
        "max_stay_nights": 14,
        "min_stay": [{"nights": 3, "applies": "holiday"}],
        "note": ("Verbatim: 'All campers and camping units are limited to a stay of not more than 14 consecutive days "
                 "in one campground although a one-time 14-day extension may be obtained with written permission from "
                 "the park manager. A five-day absence is required before returning to the same campground to camp "
                 "again.' Holiday minimums for campsite reservations (2025, the latest published): Memorial Day "
                 "weekend 4 nights, July 4th and Labor Day weekends 3 nights; min_stay carries the 3."),
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 2.75,
        "entrance": {"resident": 7, "nonresident": 7, "per": "vehicle_day"},
        "checked": "2026",
        "note": ("From November 1, 2026 (all figures include transaction fees): 'A valid State Park Vehicle Permit is "
                 "required at all Kansas State Parks' - $7 a day, sold only at the park's office, or $39 for an annual "
                 "permit ($20.25 senior/disabled); one price for residents and non-residents. A camping permit is "
                 "required in addition, per camping unit, and 'a $2.75 processing fee will apply to each camping "
                 "stay'. Each park's entry carries the nightly camping and utility fees. Kansas has no non-resident "
                 "camping rate. The state fishing lakes are not part of this system: camping there is free."),
    },
    "provenance": {
        "booking": {"source": KDWP, "checked": D, "method": "manual"},
        "fees": {"source": KDWP, "checked": D, "method": "manual"},
    },
}
FAIR = 14530
FAIR_FEES = {"nightly_low": 30, "nightly_high": 30, "currency": "USD", "checked": "2026",
             "note": ("The State Fair's posted rate outside September (the fair): $30 a night or $180 a week; 'rates can "
                      f"vary depending on events going on at the Fairgrounds'. Read {D}.")}
FAIR_SRC = ("https://www.kansasstatefair.gov/p/general-information1/facility-rentals1/rv-park-info ('$30/per night or "
            f"$180 per week'), read {D}")
IE = f"re-check {D} (Kansas pass)"
KP = "https://www.ksoutdoors.gov/about-kdwp/where-we-work/state-parks/"
# Each entry's area on KDWP's park page (parks/*.txt -> areas.json); None = the whole park. Copied page links replace
# the old /State-Parks/Locations/ ones, which now load a blank page.
AREA = {2081: ("cedar-bluff", "Bluffton"), 2082: ("cedar-bluff", "Page Creek"), 2083: ("eisenhower", None),
        2084: ("kanopolis", "Horsethief"), 2085: ("kanopolis", "Langley Point"), 2086: ("perry", None),
        2087: ("webster-state-park", None), 2090: ("cheney", "East Shore"), 2091: ("cheney", "West Shore"),
        2092: ("el-dorado", "Bluestem Point"), 2093: ("el-dorado", "Walnut River"), 13955: ("el-dorado", "Boulder Bluff"),
        2094: ("pomona", None), 2095: ("wilson", None), 2097: ("clinton", None), 2098: ("fall-river", "Fredonia Bay"),
        2100: ("historic-lake-scott", None), 2101: ("prairie-dog", None), 2102: ("elk-city", None),
        2104: ("crawford", None), 2105: ("glen-elder", None), 2106: ("meade", None), 2108: ("lovewell", None),
        2110: ("cross-timbers", "Toronto Point"), 2111: ("cross-timbers", "Holiday Hill"),
        2112: ("cross-timbers", "Mann's Cove"), 2113: ("hillsdale", None), 2114: ("milford", None),
        2115: ("tuttle-creek", "River Pond"), 13952: ("tuttle-creek", "Fancy Creek"),
        13953: ("tuttle-creek", "Cedar Ridge")}
# No area counts on KDWP's page (or a fuller list elsewhere): the site mix from the entry's own record.
OWN = {2099: (6, 0, 6, "ReserveAmerica's Quarry Bay loop: full-hookup sites 401-406 (KDWP's area block counts only "
                        "its 17 primitive sites)"),
       2107: (64, 20, 44, "64 utility sites, 44 full-hookup and 20 water and electric (Hutchinson CVB, ReserveAmerica)"),
       2116: (41, 41, 0, "41 water-and-electric sites (Rocky Ford is not on KDWP's Tuttle Creek page)"),
       13954: (28, 0, 28, "KDWP: 'Twenty-eight utility campsites with water, electrical and sewer service'")}
OLD_LINKS = {"https://www.ksoutdoors.gov/State-Parks/Locations/Cedar-Bluff": KP + "cedar-bluff",
             "https://www.ksoutdoors.gov/State-Parks/Locations/Eisenhower": KP + "eisenhower",
             "https://www.ksoutdoors.gov/State-Parks/Locations/Kanopolis": KP + "kanopolis",
             "https://www.ksoutdoors.gov/State-Parks/Locations/Perry": KP + "perry",
             "https://www.ksoutdoors.gov/State-Parks/Locations/Webster": KP + "webster-state-park"}


def site_mix(i, areas):
    """(sites with electric, of them water-and-electric, of them full hookups, where the counts come from)."""
    if i in OWN:
        return OWN[i]
    park, area = AREA[i]
    blocks = [areas[park][area]] if area else list(areas[park].values())
    e = sum(b.get("Electric", 0) for b in blocks)
    we = sum(b.get("Water, Electric", 0) for b in blocks)
    wse = sum(b.get("Water, Sewer, Electric", 0) for b in blocks)
    where = f"KDWP's {park} page, {area + ' area' if area else 'all areas'}"
    return e + we + wse, we, wse, f"{where}: {e} electric, {we} water and electric, {wse} full hookups"


def surcharges(n, we, wse):
    if not n:
        return {"electric": 0}          # primitive only: KDWP's utility fees do not apply
    sur = {}
    if n - wse:
        sur["electric"] = 11
    if we:
        sur["water"] = 2                # two utilities $13 = electric $11 + $2
    if wse:
        sur["full_hookup"] = 15
    sur["premium_site"] = 2
    return sur


def add_ie(e, line):
    ie = e.get("inclusion_evidence") or ""
    if line not in ie:
        e["inclusion_evidence"] = f"{ie}; {line}" if ie else line


def main():
    apply = "--apply" in sys.argv
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path, encoding="utf-8"))
    ks = [r for r in rows if r["state"] == "KS" and r.get("ownership") == "state"]
    lakes = [r for r in ks if "State Fishing Lake" in r["name"]]
    parks = [r for r in ks if "State Fishing Lake" not in r["name"] and r["id"] != FAIR]
    assert len(lakes) == 25 and len(parks) == 35, (len(lakes), len(parks))
    for r in lakes:
        assert r["fees"] == {"nightly_low": 0, "nightly_high": 0}, r["id"]
        assert not r.get("policy_ref"), r["id"]
        cs.apply_update(r, {"policy_ref": "none"})
    fair = next(r for r in ks if r["id"] == FAIR)
    assert not fair.get("fees") and not fair.get("policy_ref")
    cs.apply_update(fair, {"policy_ref": "none", "fees": FAIR_FEES,
                           cs.PROVENANCE: {"fees": {"source": FAIR_SRC, "checked": D}}})
    add_ie(fair, f"{IE}: priced from the State Fair's RV park page, $30 a night; policy_ref none (the State Fair "
                 "Board runs it, not KDWP)")
    print(FAIR, fair["name"], "$30; policy_ref none")
    areas = json.load(open(os.path.join(HERE, "areas.json"), encoding="utf-8"))
    assert set(AREA) | set(OWN) == {r["id"] for r in parks}
    for r in sorted(parks, key=lambda r: r["id"]):
        assert not r.get("fees") and not r.get("policy_ref"), r["id"]
        prov = (r.get(cs.PROVENANCE) or {}).get("fees") or {}
        assert prov.get("method") not in ("manual", "reported"), r["id"]
        n, we, wse, where = site_mix(r["id"], areas)
        sur = surcharges(n, we, wse)
        links = r["website"].split("\n")
        new = [OLD_LINKS.get(x, x) for x in links]
        if new != links:
            r["website"] = "\n".join(new)
        fees = {"nightly_low": 17.75, "nightly_high": 17.75, "currency": "USD", "surcharges": sur,
                "checked": "2026", "note": FEE_NOTE.format(d=D)}
        cs.apply_update(r, {"fees": fees, cs.PROVENANCE: {"fees": {"source": f"{SRC}; site mix: {where}",
                                                                      "checked": D}}})
        add_ie(r, f"{IE}: priced from KDWP's statewide fee schedule beginning 2026-11-01, $17.75 a night plus "
                  "utilities")
        cs.validate_row(r, f"id {r['id']}")
        if r["id"] == 2112:
            add_ie(r, f"{IE}: KDWP's Cross Timbers page lists Mann's Cove as 15 primitive sites only, so the "
                      "earlier 'with electric/water hookups' above was wrong")
        print(r["id"], r["name"][:44], json.dumps(sur), "|", where[:90])
    for r in lakes + [fair]:
        cs.validate_row(r, f"id {r['id']}")
    ppath = os.path.join(ROOT, "campground_policies.json")
    pol = json.load(open(ppath, encoding="utf-8"))
    assert "state:KS" not in pol or pol["state:KS"] == ROW
    pol["state:KS"] = ROW
    print(f"{len(parks)} parks priced, {len(lakes)} fishing lakes + the Fairgrounds policy_ref none, state:KS row")
    if apply:
        for p, data in ((path, rows), (ppath, pol)):
            tmp = p + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            os.replace(tmp, p)
        print("written")
    else:
        print("(dry run)")


if __name__ == "__main__":
    main()
