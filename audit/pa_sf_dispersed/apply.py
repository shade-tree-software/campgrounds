#!/usr/bin/env python3
"""Append the PA state forest candidates (candidates.json + waterfront.json) to
campgrounds.json as new entries (AWH 2026-10-10: one entry per 1 km cluster).

    python3 audit/pa_sf_dispersed/apply.py [--dry-run]

waterfront.json maps a candidate's first site_id to {"waterfront", "evidence"};
a candidate missing from it must have no mapped water within 300 m, and is
written `not waterfront` with that as the evidence. Ids are max(id)+1 across
both location files.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402

CHECKED = "2026-10-10"
RA = "https://pennsylvaniastateparks.reserveamerica.com"
FEES = {"nightly_low": 10, "nightly_high": 10, "currency": "USD",
        "nonresident": {"type": "surcharge", "amount": 5, "per": "night"},
        "note": "State forest motorized roadside campsite (a DCNR state FOREST program, not a state park): "
                "$10/night PA residents, $15/night non-residents, reserved through ReserveAmerica; 7-night limit."}
FEES_SRC = ("https://www.pa.gov/agencies/dcnr/recreation/what-to-do/stay-overnight/overnight-prices-and-policies.html "
            "(state forest motorized roadside campsites, effective 2022-11-03)")
BOOKING = {"reservable": True, "platform": "reserveamerica", "fcfs": "never", "window_opens_days": 330,
           "reserve_until": {"relative_to": "arrival", "at": "12:00"}, "max_stay_nights": 7}
BOOKING_SRC = ("https://www.pa.gov/agencies/dcnr/recreation/what-to-do/stay-overnight/motorized-roadside-camping "
               "('Most campsites in Pennsylvania state forests can be reserved 11 months in advance to noon of the "
               "day of arrival' through the Pennsylvania State Park and Forest Reservation System; 'A camping permit "
               "will be valid for no more than seven consecutive nights'); ReserveAmerica site pages list each "
               "site as Site-Specific reservable")


def slug(forest):
    return re.sub(r"[^a-z]+", "-", forest.lower()).strip("-") + "-state-forest"


def main():
    dry = "--dry-run" in sys.argv
    cands = json.load(open(os.path.join(HERE, "candidates.json")))
    wf = json.load(open(os.path.join(HERE, "waterfront.json")))
    path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(path))
    fam = os.path.join(ROOT, "trip_data", "family.json")
    next_id = max(r["id"] for r in rows + (json.load(open(fam)) if os.path.exists(fam) else [])) + 1
    names = [c["name"] for c in cands]
    added = []
    for c in cands:
        key = c["site_ids"][0]
        name = c["name"]
        if names.count(name) > 1:     # two clusters in one named area (Medix Run)
            name = f"{name[:-1]}, sites {', '.join(c['labels'])})"
        n = len(c["site_ids"])
        site_urls = [f"{RA}/campsiteDetails.do?contractCode=PA&parkId={c['park_id']}&siteId={s}" for s in c["site_ids"]]
        if n <= 3:
            website = "\n".join(f"https://www.reserveamerica.com/explore/{slug(c['forest'])}/PA/{c['park_id']}/{s}/campsite-booking"
                                for s in c["site_ids"])
        else:
            website = f"{RA}/campgroundDetails.do?contractCode=PA&parkId={c['park_id']}"
        lo, hi = min(c["max_len"]), max(c["max_len"])
        length = f"{hi} ft" if lo == hi else f"{lo}-{hi} ft"
        sites_word = "site" if n == 1 else f"{n} sites"
        caveats = "".join(f" {x[0].upper()}{x[1:]}." for x in c["caveats"])
        area = " / ".join(dict.fromkeys(re.sub(r"^.*?\(|\)$", "", c["name"]).split(" / ")))
        note = (f"Reservable {c['forest']} State Forest drive-in campsite{'' if n == 1 else 's'} "
                f"{', '.join(c['labels'])} ({area}): max vehicle length {length}, "
                f"{'/'.join(s.lower() for s in c['surfaces'])} driveway, one camping unit per site. "
                f"Primitive: no hookups, no dump station; bring water and pack out trash. "
                f"State forest roads are not plowed in winter.{caveats} --Claude")
        w = wf.get(key)
        if w is None:
            # Clusters with no satellite call: no water within 150 m (USGS NHD).
            # A stream 150-300 m off through closed forest can earn neither
            # on-water (~50 m bound) nor a view; ponds in that band were looked at.
            if c.get("water_m") is not None and c["water_m"] <= 150:
                raise SystemExit(f"{name}: water {c['water_m']} m away but no satellite call")
            w = {"waterfront": "not waterfront",
                 "evidence": (f"USGS NHD 2026-10-10: no stream, river or lake within 300 m of the {sites_word}; "
                              f"inland state forest site, default down" if c.get("water_m") is None else
                              f"USGS NHD 2026-10-10: nearest mapped water is {c['water']} {c['water_m']} m from the "
                              f"{sites_word}, through closed forest - beyond any on-water or view distance; default down")}
        entry = {
            "id": next_id, "kind": "campground", "name": name, "location": c["location"],
            "elevation_meters": c["elevation_meters"], "state": "PA", "ownership": "state",
            "waterfront": w["waterfront"], "waterfront_evidence": w["evidence"],
            "inclusion_evidence": (
                f"ReserveAmerica campsiteDetails ({c['forest']} SF parkId {c['park_id']}; siteId "
                f"{', '.join(c['site_ids'])}; read {CHECKED}): Type Roadside/State Forest Rustic, Site Access Drive-In, "
                f"Looking For Category includes RV/Trailer, Max Vehicle Length {length}, status "
                f"{'; '.join(s.replace(' Season Dates', '').rstrip('.') for s in c['status'])} -> a 23-ft rig fits"),
            "website": website, "phone": "888-727-2757", "note": note, "policy_ref": "none",
        }
        ra_src = f"ReserveAmerica campsiteDetails, {c['forest']} SF siteId {', '.join(c['site_ids'])}"
        groups = {
            "fees": FEES, "booking": BOOKING,
            "hookups": {"electric": 0, "water": False, "sewer": False},
            "facilities": {"dump": False},
            "sites": {"count": n, "max_rig_ft": hi, **({"pull_through": True} if c["pull_through"] else {})},
        }
        prov = {"fees": {"source": FEES_SRC, "checked": "2026-10-09"},
                "booking": {"source": BOOKING_SRC, "checked": CHECKED},
                "hookups": {"source": ra_src + " ('There are no electric, water, sewer hook-ups, or dump stations "
                                               "on state forest land')", "checked": CHECKED},
                "facilities": {"source": ra_src + " ('no ... dump stations on state forest land')", "checked": CHECKED},
                "sites": {"source": ra_src + " (Max Vehicle Length, Driveway Entry)", "checked": CHECKED}}
        if all(s.startswith("Open year round") for s in c["status"]) and not any("Dec 15" in x for x in c["caveats"]):
            groups["season"] = {"year_round": True}
            prov["season"] = {"source": ra_src + " (Status: 'Open year round')", "checked": CHECKED}
        cs.apply_update(entry, {**groups, cs.PROVENANCE: prov})
        cs.validate_row(entry, name)
        added.append(entry)
        next_id += 1
    print(f"{len(added)} entries, ids {added[0]['id']}-{added[-1]['id']}")
    if dry:
        print(json.dumps(added[0], indent=2, ensure_ascii=False))
        return
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(rows + added, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


if __name__ == "__main__":
    main()
