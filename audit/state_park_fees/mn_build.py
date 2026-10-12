"""MN findings: Minnesota state parks and recreation areas from ReserveMN, state forest campgrounds from the DNR's fee
page, read 2026-10-12.

    python3 -I mn_build.py PLACES RATES OUT

PLACES = rdr_place.py's facilities and unit types per park (each type's longest vehicle length); RATES = the nightly
rate of sampled sites of each campground and type: rdr_rates.py found them for Tue 2026-10-20 / Sat 2026-10-24
(mn_booking_rates_2026-10-12.jsonl), and rdr_reprice.py priced the same sites for Tue 2027-06-15 / Sat 2027-06-19
(mn_booking_rates_june_2026-10-12.jsonl) - the in-season prices, since late-October nights price a full-hookup site
as electric once the water is off (Lake Shetek's $42 on Oct 20, $34 on Oct 24).
The DNR's fee page (dnr.state.mn.us/state_parks/fees.html) gives only ranges for state parks - 'Drive-in campsites
$20-$35/night', 'Electric hookup (where available) add $10/night', 'Water and sewer hookup (where available) add
$8/night', 'tax is additional' - so each park's own price comes from the booking site. The base is the cheapest drive-in
site without electric where the campground has one a 23-ft rig fits, else its electric site (nightly_low / nightly_high
span an entry's campgrounds); electric and full hookups are surcharges on it, measured within a campground. Cart-in, walk-in, backpack, double, equestrian, group and cabin sites are left out. The $8 online
reservation fee ('No fee for same-day reservations') and the $7 vehicle permit are the state:MN registry row's.

State forest campgrounds are a separate system (first come, pay at the campground): 'In state forests (taxes are
included): Drive-in campsites $17/night; Equestrian campsites $22/night'. They are not state parks, so they get
`policy_ref: none` (they inherited the parks' vehicle permit, reservation rules and fee)."""
import collections, json, os, re, sys
places_path, rates_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
rows = json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))
reg = json.load(open(os.path.join(ROOT, "campground_policies.json"), encoding="utf-8"))
D = "2026-10-12"
TUE, SAT = "2027-06-15", "2027-06-19"
FEES = "https://www.dnr.state.mn.us/state_parks/fees.html"

# An entry that is one campground of a park with several: which ReserveMN facilities it is.
FAC = {5408: r"Paint Rock", 5412: r"Riverview", 5398: r"Beatrice", 5399: r"Side Lake", 5419: r"^Lower",
       5420: r"^Upper", 5418: r"Shipwreck", 5410: r"Sherlock", 5409: r"Portsmouth", 5421: r"Baptism",
       5364: r"Meadowbrook", 285: r"Savanna Portage Campground"}


def kind(t):
    if re.search(r"(?i)equest|double|triple|cart|walk|backpack|canoe|boat|group|cabin|yurt|tent|lodg|house", t):
        return None
    if re.search(r"(?i)^drive-in electric/water/sewer$", t):
        return "fhu"
    if re.search(r"(?i)^drive-in electric$", t):
        return "e"
    if re.search(r"(?i)^drive-in$", t):
        return "ne"
    return None


places = json.load(open(places_path, encoding="utf-8"))
tue = collections.defaultdict(lambda: collections.defaultdict(list))   # (pid, facility) -> kind -> [rate]
sat = collections.defaultdict(dict)                                     # (pid, facility) -> (kind, unit) -> rate
tue_unit = {}
for line in open(rates_path, encoding="utf-8"):
    r = json.loads(line)
    if "error" in r or not r.get("rate"):
        continue
    k = kind(r["unitType"])
    if k is None:
        continue
    key = (r["placeId"], r["facility"])
    p = float(r["rate"])
    if r["date"] == SAT:
        sat[key][(k, r["unitId"])] = p
    else:
        tue[key][k].append(p)
        tue_unit[(key, k, r["unitId"])] = p


def money(v):
    return f"${v:g}" if v % 1 else f"${int(v)}"


def rng(vals):
    lo, hi = min(vals), max(vals)
    return money(lo) if lo == hi else f"{money(lo)}-{hi:g}"


def as_num(v):
    return v if v % 1 else int(v)


out, flags = [], []
for e in rows:
    if e.get("kind") != "campground" or e.get("state") != "MN" or e.get("ownership") != "state" or e.get("fees"):
        continue
    if (cs.resolve(e, reg).get("fees") or {}).get("values", {}).get("nightly_low") is not None:
        continue
    m = re.search(r"#!park/(\d+)", e.get("website") or "")
    forest = "State Forest" in e["name"]
    if forest:
        horse = "Horse Camp" in e["name"]
        note = ("Minnesota state forest campground: drive-in campsites $17 a night, taxes included" +
                (" (the equestrian sites $22)" if horse else "") + "; first come, first served, paid at the campground. "
                f"DNR fee page, read {D}.")
        out.append({"id": e["id"], "name": e["name"], "policy_ref": "none",
                    "fees": {"nightly_low": 17, "nightly_high": 17, "currency": "USD", "surcharges": {"weekend": 0},
                             "checked": "2026", "note": note},
                    "source": f"{FEES} ('In state forests (taxes are included): Drive-in campsites $17/night ... Equestrian "
                              f"campsites $22/night'), read {D}"})
        continue
    if not m:
        flags.append((e["id"], e["name"], "no ReserveMN link"))
        continue
    pid = int(m.group(1))
    p = places.get(str(pid)) or {}
    facs = [f for f in (p.get("facilities") or {}).values()
            if (e["id"] not in FAC or re.search(FAC[e["id"]], f["name"].strip()))]
    fnames = {f["name"].strip() for f in facs}
    keys = [k for k in tue if k[0] == pid and k[1].strip() in fnames]
    vals = collections.defaultdict(list)
    for k in keys:
        for kk, v in tue[k].items():
            vals[kk] += v
    if not vals:
        flags.append((e["id"], e["name"], f"no RV site prices at place {pid} ({sorted(fnames)})"))
        continue
    maxlen = collections.defaultdict(int)          # kind -> longest vehicle length of any facility's unit type
    for f in facs:
        for t, (ln, _avail) in (f.get("units") or {}).items():
            k = kind(t)
            if k:
                maxlen[k] = max(maxlen[k], ln or 0)
    ne_fit = bool(vals.get("ne")) and maxlen["ne"] >= 23
    if vals.get("ne") and not ne_fit:
        flags.append((e["id"], e["name"], f"non-electric sites top out at {maxlen['ne']} ft; base is electric"))
    base_k = "ne" if ne_fit else ("e" if vals.get("e") else "fhu")
    base = min(vals[base_k])

    def step(lo_k, hi_k):
        """The add-on from lo_k to hi_k inside one campground (the cheapest such difference), else across the entry."""
        d = [min(tue[k][hi_k]) - min(tue[k][lo_k]) for k in keys if tue[k].get(lo_k) and tue[k].get(hi_k)]
        return as_num(round(min(d) if d else min(vals[hi_k]) - base, 2))
    s, parts = {}, []
    if base_k == "ne":
        parts.append(f"{rng(vals['ne'])} a night for a drive-in site without electric")
        if vals.get("e"):
            parts.append(f"electric {rng(vals['e'])}")
            s["electric"] = step("ne", "e")
    elif base_k == "e":
        parts.append(f"{rng(vals['e'])} a night for an electric site" +
                     (" (the sites without electric are too short for a 23-ft rig)" if vals.get("ne") else
                      " (every drive-in site has electric)"))
    if vals.get("fhu"):
        if base_k == "fhu":
            parts.append(f"every drive-in site has full hookups: {rng(vals['fhu'])} a night")
        else:
            parts.append(f"full hookups {rng(vals['fhu'])}")
            s["full_hookup"] = step(base_k, "fhu") if any(tue[k].get(base_k) and tue[k].get("fhu") for k in keys) \
                else as_num(round(min(vals["fhu"]) - base, 2))
    diffs = []
    for k in keys:
        for (kk, uid), v in sat.get(k, {}).items():
            t = tue_unit.get((k, kk, uid))
            if t is not None:
                diffs.append(round(v - t, 2))
    text = "; ".join(parts) + "."
    if diffs and all(x == 0 for x in diffs):
        s["weekend"] = 0
        text += " The same on a Saturday."
    elif diffs and all(x > 0 for x in diffs):
        s["weekend"] = as_num(min(diffs))
        text += f" Saturday +{money(min(diffs))}."
    elif diffs:
        text += " Some sites cost more or less on a Saturday (" + ", ".join(
            f"{'+' if x > 0 else '-'}{money(abs(x))}" for x in sorted(set(diffs)) if x) + ")."
    text += (" Plus tax and the $8 online reservation fee (none for a same-day reservation), and a state park vehicle "
             f"permit. ReserveMN's prices for June 2027 nights, read {D}.")
    fees = {"nightly_low": as_num(base), "nightly_high": as_num(max(vals[base_k])), "currency": "USD", "surcharges": s,
            "checked": "2026", "note": text}
    out.append({"id": e["id"], "name": e["name"], "fees": fees,
                "source": f"ReserveMN PlaceId {pid} ({p.get('name')}; {', '.join(sorted(k[1].strip() for k in keys))}): "
                          f"each campsite type's nightly rate from rdr/search/details for sampled sites, {TUE} and {SAT}, "
                          f"read {D} (mn_booking_rates_june_2026-10-12.jsonl); {FEES}"})
json.dump(out, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "MN findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:40], f["nightly_low"], f.get("surcharges"), x.get("policy_ref", ""))
for fl in flags:
    print("FLAG", *fl)
