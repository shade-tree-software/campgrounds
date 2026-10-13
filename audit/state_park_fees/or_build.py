"""Oregon findings: Oregon State Parks and four Department of Forestry campgrounds, read 2026-10-12 (page texts in
or_fee_pages_2026-10-12.txt).

    python3 -I or_build.py OUT

Oregon State Parks' booking site (oregonstateparks.reserveamerica.com, classic ReserveAmerica, contract OR) lists every
site of each park (or_sites_2026-10-12.json, ra_sites.py); ra_sample.py quoted up to four sites of each loop and type
for Tue 2027-06-15 (or_booking_rates_2026-10-12.jsonl): one price per park and type ('Residents Pay' and 'Non-Residents
Pay', 25% more, rounded, e.g. $62 / $78), 'Reservation Fees $10.00'. One site of each park and type costs the same on
Sat 2027-06-19 (or_booking_rates_saturday_2026-10-12.jsonl). Tent and primitive sites are 'Looking For Category: Tent
Site' (or_site_details_2026-10-12.jsonl), so the base is the cheapest water-and-electric ('STANDARD') or full-hookup site
a 23-ft rig fits (the listing's lengths; blank = unknown), full hookups an add-on over it; Cottonwood Canyon, whose only
sites are its primitive drive-in sites, is the exception. The rates page ('Rates Effective May 1, 2026'): resident
ranges full $31-60, electric $29-55, tent $20-33, primitive $0-17; 'charges out-of-state residents 25% more'; 'from
October 1 to April 30, weekday rates at a lower price than weekends'. OPRD's 2025-08-01 notice: primitive camping 'from
about $10 to at least $15 per night' from May 1, 2026.

First-come parks (OPRD's first-come list; not on the booking site) get the rates page's range for their site type (the
park page's 'tent sites with water nearby' / 'primitive sites'): tent $20-33, primitive $15 (the notice's floor) to $17,
water and electric $29-55 (Jasper Point). No reservation fee there.

Department of Forestry campgrounds (Tillamook State Forest): 'Drive-in campsite: $20 per night (includes two vehicles)',
'Campgrounds are first come, first served, except' group campsites at Jones Creek and Nehalem Falls. Oregon has no
registry row, so each entry carries its own reservation fee and non-resident rule."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
RATES = "https://stateparks.oregon.gov/index.cfm?do=reserve.rates"
FCFS_PAGE = "https://stateparks.oregon.gov/index.cfm?do=reserve.first-come"
NOTICE = "https://apps.oregon.gov/oregon-newsroom/OR/OPRD/Posts/Post/Fee-updates-to-Oregon-State-Parks"
ODF = "https://www.oregon.gov/odf/recreation/pages/camp.aspx"
NR = {"type": "multiplier", "factor": 1.25, "applies_to": "total"}
OFF = " From October to April, weekday nights cost less than weekends."
# RA entries: entry -> (parkId, loops regex or None)
RA = {292: ("402146", None), 10595: ("402398", None), 10597: ("402486", None), 10598: ("405331", None),
      10599: ("405326", None), 10600: ("402294", None), 10601: ("409402", None), 10602: ("402488", None),
      10604: ("402382", None), 10605: ("402446", r"^(A|C) Loop"), 10606: ("402446", r"^(B|E) Loop"),
      10607: ("402241", None), 10610: ("402284", None), 10612: ("402348", None), 10613: ("402334", None),
      10615: ("402363", None), 10616: ("402178", None), 10617: ("409502", None), 10618: ("405413", None),
      10619: ("405408", None), 10622: ("402479", None), 10623: ("402346", None), 10624: ("402478", None),
      10625: ("402130", None), 10627: ("402267", None), 10628: ("405422", None), 10629: ("402191", None),
      10631: ("405213", None), 10632: ("402126", None), 10633: ("402165", None), 10634: ("405415", None),
      10636: ("402385", None), 10637: ("402388", None), 10640: ("402461", None), 10645: ("402235", None),
      10650: ("405428", None), 10651: ("402155", None), 10652: ("409102", None), 10653: ("402465", None),
      10654: ("402343", None), 11141: ("402499", None)}
# First-come OPRD parks: entry -> (park page id, site type, what the park page says)
FCFS = {10596: (109, "prim", "28 primitive sites for tents or self-contained RVs"),
        10603: (166, "prim", "10 primitive sites without water"),
        10609: (19, "prim", "22 primitive sites with water"),
        10611: (176, "prim", "Cascara Campground: 39 primitive campsites"),
        10635: (9, "prim", "18 primitive campsites"),
        10620: (13, "tent", "18 tent sites with water nearby"),
        10621: (14, "tent", "10 tent sites that can accommodate self-contained RVs"),
        10648: (15, "tent", "27 tent sites with water nearby"),
        10649: (11, "tent", "20 tent sites with water nearby"),
        10639: (25, "e", "Jasper Point: 27 first-come campsites with electricity and water hook ups")}
RANGE = {"prim": (15, 17), "tent": (20, 33), "e": (29, 55)}
RWORD = {"prim": "primitive sites", "tent": "tent sites", "e": "water-and-electric sites"}
ODFS = {10614: "Gales Creek", 10630: "Nehalem Falls", 10643: "Henry Rierson Spruce Run", 10647: "Jones Creek"}
KIND = {"STANDARD": "e", "ADA STANDARD": "e", "STANDARD - FULL": "fhu", "ADA Standard Full": "fhu",
        "PRIMITIVE": "prim", "ADA Primitive": "prim", "TENT SITE": "tent", "ADA TENT": "tent"}
WORD = {"prim": "primitive", "tent": "tent", "e": "water and electric", "fhu": "full hookups"}
sites = json.load(open(os.path.join(HERE, "or_sites_2026-10-12.json"), encoding="utf-8"))
quotes = collections.defaultdict(list)
for line in open(os.path.join(HERE, "or_booking_rates_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    quotes[r["park"][3:-5]].append(r)


def money(p):
    m = re.search(r"\$([\d,]+\.\d\d)", p or "")
    return float(m.group(1).replace(",", "")) if m else None


def num(v):
    return int(v) if float(v).is_integer() else v


out, flags = [], []
for eid, (pid, loops) in sorted(RA.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    price = collections.defaultdict(list)
    for r in quotes[pid]:
        k = KIND.get(r.get("Type"))
        q = money(r.get("price"))
        if k and q and (not loops or re.search(loops, r.get("loop") or "")):
            price[k].append(q)
    fits = collections.defaultdict(bool)
    for s in sites[pid]["sites"]:
        c = s["cells"]
        k = KIND.get(c[1] if len(c) > 1 else "")
        if k and (not loops or re.search(loops, c[0])):
            m = re.match(r"(\d+)", c[3] if len(c) > 3 else "")
            fits[k] |= m is None or int(m.group(1)) >= 23
    rv = ["e", "fhu"] if pid != "409102" else ["prim"]   # Cottonwood Canyon: drive-in primitive sites only
    kinds = [k for k in rv if price.get(k) and fits[k]]
    if not kinds:
        flags.append((eid, e["name"], dict(price), dict(fits)))
        continue
    base_k = min(kinds, key=lambda k: min(price[k]))
    base, hi = min(price[base_k]), max(price[base_k])
    sur = {"weekend": 0}
    if base_k == "e" and "fhu" in kinds:
        sur["full_hookup"] = num(min(price["fhu"]) - base)
    shown = [k for k in ("prim", "tent", "e", "fhu") if price.get(k)]
    parts = "; ".join(f"{WORD[k]} ${num(min(price[k]))}" + (f"-{num(max(price[k]))}" if max(price[k]) != min(price[k])
                                                            else "") for k in shown)
    short = [WORD[k] for k in rv if price.get(k) and not fits[k]]
    text = (f"June nights for Oregon residents: {parts} (non-residents pay 25% more), the same on a Saturday." +
            ((" Tent and primitive sites are" if {"tent", "prim"} <= set(shown) else " Tent sites are" if "tent" in shown
              else " Primitive sites are") + " for tents only (the booking site)." if {"tent", "prim"} & set(shown) - {base_k}
             else "") +
            (f" (The {' and '.join(short)} sites here are too short for a 23-ft rig.)" if short else "") + OFF +
            f" Plus the $10 reservation fee. Oregon State Parks' booking site (June 2027 quotes) and rates page, read {D}.")
    names = sorted({r.get("loop") for r in quotes[pid] if not loops or re.search(loops, r.get("loop") or "")})
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": num(base), "nightly_high": num(hi), "currency": "USD", "nonresident": NR, "reservation_fee": 10,
        "surcharges": sur, "checked": "2026", "note": text},
        "source": f"oregonstateparks.reserveamerica.com parkId {pid}" + (f" ({', '.join(names)})" if loops else "") +
                  f": resident and non-resident 1-night quotes for 2027-06-15 and 2027-06-19 with 'Reservation Fees "
                  f"$10.00' (or_booking_rates_2026-10-12.jsonl) + {RATES} (25% out-of-state, weekday rule), read {D}"})
for eid, (park, k, what) in sorted(FCFS.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    lo, hi = RANGE[k]
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": lo, "nightly_high": hi, "currency": "USD", "nonresident": NR, "reservation_fee": 0,
        "checked": "2026",
        "note": (f"{what} (the park page), first come, first served; the rate is posted at the park. Oregon State Parks "
                 f"publishes only ranges: {RWORD[k]} ${lo}-{hi} a night for residents" +
                 (" (at least $15 since May 2026)" if k == "prim" else "") + f", non-residents 25% more. Read {D}.")},
        "source": f"https://stateparks.oregon.gov/index.cfm?do=park.profile&parkId={park} (site type) + {FCFS_PAGE} + "
                  f"{RATES} ('Rates Effective May 1, 2026')" + (f" + {NOTICE} ('at least $15 per night')"
                                                                 if k == "prim" else "") + f", read {D}"})
for eid, nm in sorted(ODFS.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": 20, "nightly_high": 20, "currency": "USD", "reservation_fee": 0, "surcharges": {"weekend": 0},
        "checked": "2026",
        "note": (f"Oregon Department of Forestry: drive-in campsites $20 a night (two vehicles included), first come, "
                 f"first served" + (" (only the group site is reservable)" if eid in (10630, 10647) else "") +
                 f". ODF's camping page, read {D}.")},
        "source": f"{ODF} ('Drive-in campsite: $20 per night (includes two vehicles)'; 'Campgrounds are first come, first "
                  f"served, except' the group sites at Jones Creek and Nehalem Falls), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "OR findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f["nightly_high"], f.get("surcharges"), f.get("reservation_fee"))
for fl in flags:
    print("FLAG", *fl)
