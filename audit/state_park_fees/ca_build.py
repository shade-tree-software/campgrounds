"""California findings: California State Parks on ReserveCalifornia, three CAL FIRE demonstration state forests and the
Dixon May Fair, read 2026-10-12 (page texts in ca_fee_pages_2026-10-12.txt).

    python3 -I ca_build.py OUT

ReserveCalifornia is US eDirect (Tyler) RDR (config.json: rdrApiUrl
https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/). Each entry was matched to its park
(fd/citypark: name, then distance) and its campground facilities (search/place, ca_places_2026-10-12.json; the map is
ca_facility_map_2026-10-12.json). rdr_units.py read each facility's units on 2027-04-06 (inside the six-month window)
and priced the longest unit of every site type for Tue 2027-06-15 and Sat 2027-06-19 (ca_units_2026-10-12.jsonl);
every quote adds the $8.25 reservation fee (on the state:CA registry row). Site types: 'Campsite', 'Premium Campsite',
'Primitive Campsite' and the like have no hookups; 'Hook Up (E )' electric; 'Hook Up (E/W)' (or an unlabelled 'Hook Up')
electric and water; 'Hook Up (E/W/S)' full hookups; tent, hike/bike, group, cabin and equestrian types are left out
(a 'Tent Campsite' counts only where it is a campground's only type). Base = the cheapest site type with no hookups
whose longest unit takes a 23-ft rig (a length of 0 = unknown), else the cheapest hookup type; nightly_high the dearest
of that kind; hookups as add-ons; weekend = the Saturday difference.

CAL FIRE (14 CCR § 1401.1, operative 2021-04-01): 'Designated Camping Area (including two vehicles)' $25 per day at
Jackson and Boggs Mountain, $30 at Mountain Home, paid on arrival, first come, first served. Dixon May Fair: 'Space
rental fee $45 per day (beginning January 1, 2026 – $50 per day)', first come, first served. These four are outside
California State Parks (policy_ref none, ca_corrections_2026-10-12.json)."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TUE, SAT = "2027-06-15", "2027-06-19"
API = "https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/"
fmap = json.load(open(os.path.join(HERE, "ca_facility_map_2026-10-12.json"), encoding="utf-8"))
places = json.load(open(os.path.join(HERE, "ca_places_2026-10-12.json"), encoding="utf-8"))
units = collections.defaultdict(list)
for line in open(os.path.join(HERE, "ca_units_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    if "unitTypeId" in r:
        units[str(r["facilityId"])].append(r)
SKIP = re.compile(r"(?i)hike|bike|group|cabin|yurt|cottage|equest|horse|floating|dorm|hogan|lodge")
WORD = {"ne": "campsites", "e": "electric", "ew": "electric and water", "fhu": "full hookups"}
UNPRICED = {11609: "Benicia SRA's en route sites", 11614: "Bow Willow (Anza-Borrego)", 11616: "Butano",
            11664: "Manchester", 11676: "Navarro Beach", 11677: "Paul M. Dimmick", 11683: "Picacho",
            11697: "Saddleback Butte", 11715: "Woodson Bridge", 13967: "Turlock Lake"}
OWN = {
    11611: (25, "Calso Camp", "Boggs Mountain"), 11653: (25, "Camp 1", "Jackson"), 11675: (30, "Frazier Mill",
                                                                                           "Mountain Home")}


def kind(t):
    t = t or ""
    if re.search(r"(?i)E/W/S|Double Hook Up", t):
        return "fhu"
    if re.search(r"(?i)Hook Up \(E/W|Hook Up Campsite", t):
        return "ew"
    if re.search(r"(?i)Hook Up \(E", t):
        return "e"
    if re.search(r"(?i)tent", t):
        return "tent"
    if re.search(r"(?i)en ?route", t):
        return "enroute"
    return "ne"


def num(v):
    return int(v) if float(v).is_integer() else v


def cash(v):
    return f"${num(v)}" if float(v).is_integer() else f"${v:.2f}"


def span(vs):
    return cash(min(vs)) + (f"-{cash(max(vs))[1:]}" if max(vs) != min(vs) else "")


out, flags, too_short = [], [], []
for k, v in sorted(fmap.items(), key=lambda kv: int(kv[0])):
    eid = int(k)
    e = rows[eid]
    if e.get("fees") or eid in UNPRICED or eid in OWN or not v["facilities"]:
        continue
    got = collections.defaultdict(list)       # kind -> [(tue, sat, type, facility, length)]
    for fid in v["facilities"]:
        for r in units.get(fid, []):
            t = r.get("unitType") or ""
            if SKIP.search(t):
                continue
            tue = (r["rates"].get(TUE) or {}).get("rate")
            sat = (r["rates"].get(SAT) or {}).get("rate")
            if not tue or float(tue) == 0:
                continue
            got[kind(t)].append((float(tue), float(sat) if sat else None, t, r["facility"], r.get("maxLength") or 0))
    fit = {kk: [x for x in xs if x[4] == 0 or x[4] >= 23] for kk, xs in got.items()}
    fit = {kk: xs for kk, xs in fit.items() if xs}
    enroute = fit.pop("enroute", None)          # en route sites (overnight travellers): named, not the base
    if not any(kk in fit for kk in ("ne", "e", "ew", "fhu")) and (enroute or "tent" in fit):
        fit = {"ne": enroute or fit["tent"]}     # a campground whose only type is en route or 'Tent Campsite'
        enroute = None
    fit.pop("tent", None)
    longest = None
    if not fit:   # no site takes a 23-ft rig: price the campground anyway, say so, and list it for AWH
        fit = {kk: xs for kk, xs in got.items() if kk != "tent"} or ({"ne": got["tent"]} if "tent" in got else {})
        if not fit:
            flags.append((eid, e["name"], "no priced site"))
            continue
        longest = max(x[4] for xs in fit.values() for x in xs)
        too_short.append((eid, e["name"], longest))
    base_k = next(kk for kk in ("ne", "e", "ew", "fhu") if kk in fit)
    lo, hi = min(x[0] for x in fit[base_k]), max(x[0] for x in fit[base_k])
    sur = {}
    if base_k == "ne" and (fit.get("e") or fit.get("ew")):
        sur["electric"] = num(min(x[0] for x in fit.get("e", []) + fit.get("ew", [])) - lo)
    if fit.get("e") and fit.get("ew") and min(x[0] for x in fit["ew"]) > min(x[0] for x in fit["e"]):
        sur["water"] = num(min(x[0] for x in fit["ew"]) - min(x[0] for x in fit["e"]))
    if "fhu" in fit and base_k != "fhu":
        sur["full_hookup"] = num(min(x[0] for x in fit["fhu"]) - lo)
    wk = {round(x[1] - x[0], 2) for xs in fit.values() for x in xs if x[1] is not None}
    if wk == {0}:
        sur["weekend"] = 0
    elif len(wk) == 1:
        sur["weekend"] = num(wk.pop())
    else:
        flags.append((eid, e["name"], f"Saturday differences {sorted(wk)}"))
    short = sorted({WORD[kind(x[2])] for xs in got.values() for x in xs if 0 < x[4] < 23 and kind(x[2]) in WORD}
                   - {WORD[kk] for kk in fit})
    parts = "; ".join(f"{WORD[kk]} {span([x[0] for x in fit[kk]])}" for kk in ("ne", "e", "ew", "fhu") if kk in fit)
    text = (f"June 2027 nights on ReserveCalifornia: {parts}" +
            (", the same on a Saturday" if sur.get("weekend") == 0 else
             f", ${sur['weekend']} more on a Saturday" if sur.get("weekend") else "") + "." +
            (f" (The {' and '.join(short)} sites here are too short for a 23-ft rig.)" if short and not longest else "") +
            (f" The booking site lists no site here for a vehicle over {longest} ft." if longest else "") +
            (f" En route sites {span([x[0] for x in enroute])}." if enroute else "") +
            " Plus the $8.25 reservation fee. California State Parks' booking site, read " + D + ".")
    fees = {"nightly_low": num(lo), "nightly_high": num(hi), "currency": "USD", "surcharges": sur, "checked": "2026",
            "note": text}
    facs = sorted({x[3] for xs in fit.values() for x in xs})
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{API} (ReserveCalifornia), {places[str(v['place'])]['name']}: {', '.join(facs)} - one unit of "
                          f"each site type priced for {TUE} and {SAT} (search/details; ca_units_2026-10-12.jsonl), read {D}"})
for eid, (fee, camp, forest) in OWN.items():
    e = rows[eid]
    if e.get("fees"):
        continue
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": fee, "nightly_high": fee, "currency": "USD", "reservation_fee": 0, "surcharges": {"weekend": 0},
        "checked": "2026",
        "note": (f"CAL FIRE's fee at {forest} Demonstration State Forest: ${fee} a day for a designated camping area, two "
                 f"vehicles included, paid on arrival; first come, first served (14 CCR § 1401.1, operative 2021-04-01; "
                 f"read {D}).")},
        "source": f"https://www.law.cornell.edu/regulations/california/14-CCR-1401.1 (subsection {'(b)' if fee == 30 else '(a)'}: "
                  f"'Designated Camping Area (including two vehicles)' ${fee} per day; history: amended 12-7-2020, operative "
                  f"4-1-2021), read {D}"})
e = rows[12426]
if not e.get("fees"):
    out.append({"id": 12426, "name": e["name"], "fees": {
        "nightly_low": 50, "nightly_high": 50, "currency": "USD", "reservation_fee": 0, "surcharges": {"weekend": 0},
        "checked": "2026",
        "note": ("'Space rental fee $45 per day (beginning January 1, 2026 – $50 per day)'; first come, first served; at most 14 "
                 "days, and closed to campers during fair events (the fair's rentals page lists the 2026 dates). Read "
                 f"{D}.")},
        "source": f"https://dixonmayfair.com/rentals/ ('Space rental fee $45 per day (beginning January 1, 2026 – $50 per "
                  f"day)'; 'first-come, first-serve'), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "CA findings;", len(flags), "flagged; unpriced:", sorted(UNPRICED))
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f["nightly_high"], f.get("surcharges"), f.get("reservation_fee"))
for fl in flags:
    print("FLAG", *fl)
for t in too_short:
    print("SHORT", *t)
