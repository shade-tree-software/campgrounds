"""North Dakota Parks and Recreation findings: ReserveND (the US eDirect/Tyler engine, API
ndparksrdr.usedirect.com/rdr/rdr/), read 2026-10-12. rdr_place.py lists each park's campgrounds and site types with
their longest vehicle length (nd_places_2026-10-12.json); rdr_rates.py found sampled sites of each type for late
October and rdr_reprice.py priced those sites for Tue 2027-06-15 and Sat 2027-06-19 (nd_booking_rates_june_*.jsonl).

    python3 -I nd_build.py OUT

The 2026 State Parks Guide defines the site levels - 'Primitive: no utilities; Standard: electricity; Modern:
electricity and water; Premium: electricity, water and sewer' - and the vehicle permit, 'Daily Permit: $7 | Annual
Permit: $35 | Family Annual Permit: $61.25', needed in addition to camping fees ('All vehicles entering a state park
must have a valid daily or annual vehicle entrance permit. This includes overnight stays', the FAQ). The prices are the
same in every park: primitive $15 every night, standard and modern $25 ($30 on a Saturday), premium $30 ($35).

The base is an entry's cheapest primitive site a 23-ft rig fits (a type whose length is blank is unknown, not short),
else its cheapest hookup site; standard / modern (electric) and premium (full hookups) are add-ons on it; water is
modern over standard where a park has both; weekend is the base site's Saturday difference, and the other types'
Saturday prices are in the note. Every sampled site carries a $6.00 'Fee', the engine's reservation fee (Ohio's
engine puts its $6.50 reservation fee in the same field); the FAQ still says '$5.80' online and '$9.00' by phone,
'charged per campsite'. Tent, group, horse, cabin and yurt sites are left out."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TUE, SAT = "2027-06-15", "2027-06-19"
GUIDE = "https://www.parkrec.nd.gov/sites/www/files/documents/Stay/2026%20State%20Parks%20Guide-WEB.pdf"
FAQ = "https://www.parkrec.nd.gov/faq"
PLACE = {5880: 53, 5881: 56, 5882: 60, 5883: 63, 5884: 64, 5885: 59, 5886: 55, 5887: 57, 5888: 58, 5889: 61,
         5890: 54, 5893: 52, 5894: 52, 5896: 51}
FAC = {5893: r"^Primitive Campground", 5894: r"^Sanger"}
KIND = {"Primitive Campsite": "ne", "Standard Campsite": "e", "Modern Campsite": "ew", "Premium Campsite": "fhu"}
WORD = {"ne": "primitive", "e": "standard (electric)", "ew": "modern (electric and water)", "fhu": "premium (full hookups)"}
places = json.load(open(os.path.join(HERE, "nd_places_2026-10-12.json"), encoding="utf-8"))
tue = collections.defaultdict(lambda: collections.defaultdict(list))
tue_unit, sat = {}, collections.defaultdict(dict)
for line in open(os.path.join(HERE, "nd_booking_rates_june_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    k = KIND.get(r.get("unitType"))
    if "error" in r or not r.get("rate") or not k:
        continue
    key, p = (r["placeId"], r["facility"].strip()), float(r["rate"])
    if r["date"] == SAT:
        sat[key][(k, r["unitId"])] = p
    else:
        tue[key][k].append(p)
        tue_unit[(key, k, r["unitId"])] = p


def money(v):
    return f"${v:g}"


def num(v):
    return int(v) if float(v).is_integer() else v


out, flags = [], []
for eid, pid in sorted(PLACE.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    p = places[str(pid)]
    facs = [f for f in p["facilities"].values() if eid not in FAC or re.search(FAC[eid], f["name"].strip())]
    keys = [k for k in tue if k[0] == pid and k[1] in {f["name"].strip() for f in facs}]
    vals = collections.defaultdict(list)
    for k in keys:
        for kk, v in tue[k].items():
            vals[kk] += v
    fits = collections.defaultdict(bool)            # a blank length (0) is unknown, not short
    for f in facs:
        for t, (ln, _a) in f["units"].items():
            if t in KIND:
                fits[KIND[t]] |= not ln or ln >= 23
    fit = [k for k in ("ne", "e", "ew", "fhu") if vals.get(k) and (fits[k] or k != "ne")]
    if not fit:
        flags.append((eid, e["name"], f"no priced RV site ({dict(vals)})")); continue
    base_k = fit[0]
    lo, hi = min(vals[base_k]), max(vals[base_k])
    sur = {}
    elec = [v for k in ("e", "ew") if k != base_k and k in fit for v in vals[k]]
    if base_k == "ne" and elec:
        sur["electric"] = num(round(min(elec) - lo, 2))
    if "e" in fit and "ew" in fit and base_k in ("ne", "e"):
        sur["water"] = num(round(min(vals["ew"]) - min(vals["e"]), 2))
    if "fhu" in fit and base_k != "fhu":
        sur["full_hookup"] = num(round(min(vals["fhu"]) - lo, 2))
    sat_by = collections.defaultdict(set)           # site type -> Saturday minus Tuesday, per sampled site
    for k in keys:
        for (kk, uid), v in sat.get(k, {}).items():
            if (k, kk, uid) in tue_unit:
                sat_by[kk].add(round(v - tue_unit[(k, kk, uid)], 2))
    if len(sat_by.get(base_k, ())) == 1:
        sur["weekend"] = num(next(iter(sat_by[base_k])))

    def price(k):
        lo_k, hi_k = min(vals[k]), max(vals[k])
        txt = money(lo_k) if lo_k == hi_k else f"{money(lo_k)}-{hi_k:g}"
        d = sat_by.get(k, set())
        if d == {0}:
            return txt + " every night"
        if len(d) == 1 and lo_k == hi_k:
            return f"{txt}, {money(lo_k + next(iter(d)))} on a Saturday"
        return txt
    text = ("A night: " + "; ".join(f"{WORD[k]} {price(k)}" for k in ("ne", "e", "ew", "fhu") if k in fit) + "." +
            (" (The primitive sites here are too short for a 23-ft rig.)" if vals.get("ne") and "ne" not in fit else "") +
            " Plus a $6 reservation fee per site (the booking site's figure; the FAQ says $5.80 online, $9 by phone) and "
            "a vehicle permit ($7 a day, $35 a year). North Dakota Parks' booking site (June 2027 nights) and 2026 guide, "
            f"read {D}.")
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": num(lo), "nightly_high": num(hi), "currency": "USD",
        "reservation_fee": 6, "entrance": {"resident": 7, "nonresident": 7, "per": "vehicle_day"}, "surcharges": sur,
        "checked": "2026",
        "note": text},
        "source": f"ReserveND PlaceId {pid} ({p['name']}; {', '.join(sorted(k[1] for k in keys))}): each site type's "
                  f"nightly rate from rdr/search/details for sampled sites, {TUE} and {SAT} "
                  f"(nd_booking_rates_june_2026-10-12.jsonl; reservation fee: each site's 'Fee') + {GUIDE} (site levels, vehicle "
                  f"permit) + {FAQ} (reservation fee, permit with a camping reservation), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "ND findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:40], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
