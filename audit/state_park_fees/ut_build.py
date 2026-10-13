"""Utah State Parks findings, read 2026-10-12.

    python3 -I ut_build.py OUT

Each park's fee page (stateparks.utah.gov/parks/<park>/park-fees/, texts in ut_fee_pages_2026-10-12.txt) lists its
camping fees by campground and site type; camping covers one vehicle ('Includes 1 vehicle', 'Covers 1 vehicle'), so no
entrance is recorded, and 'Campsite Reservation Fee Per reservation $8' (Huntington, Millsite, Scofield; the booking
site's quotes add the same '$8.00'). The booking site (utahstateparks.reserveamerica.com, classic ReserveAmerica,
contract UT) lists every site (ut_sites_2026-10-12.json, ra_sites.py), and ra_sample.py read every one for Tue
2027-06-15 (ut_booking_rates_2026-10-12.jsonl); one site of each loop, type and price on Sat 2027-06-19
(ut_booking_rates_saturday_2026-10-12.jsonl) costs the same (only East Canyon's glamping wagon and trailer differ), and
ra_rate_card.py read two sites' details per loop and type (ut_site_details_2026-10-12.jsonl: 'Looking For Category'),
which marks the tent-only loops.

The booking site's June 2027 quotes match the fee pages except at three parks, where the page is used and the note
gives the quote: Bear Lake (the page's summer and resident / non-resident rates; the booking site quotes one price for
June-August 2027 and none for May or September), East Canyon (the booking site quotes $5-10 less for every month of its
2027 season) and Green River (the page's $45; the booking site quotes $45 for November 2026 and $50 from January 2027),
ut_booking_months_2026-10-12.txt. Red Fleet's fee page lists no camping and Utahraptor's lists only Fossil Flats, so
their prices are the booking site's.

Each entry: base = the cheapest site type a 23-ft rig can use in its campground (Max Vehicle Length; blank = unknown;
doubles, group, tent-only and lodging sites left out); hookup sites as add-ons on it ('electric' = electric, or water
and electric, over the base; 'water' over electric alone; 'full_hookup' over the base); weekend 0; reservation fee $8
where the sites are on the booking site; non-residents +$5 a night at Bear Lake, the only park with a residency split;
off-season rates in the note."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
PAGE = "https://stateparks.utah.gov/parks/{}/park-fees/"
NR = {"type": "surcharge", "amount": 5, "per": "night", "applies_to": "base"}
# entry -> (fee page slug, RA parkId or None, loops regex or None, base, high, add-ons, what the booking site must
#           show (kind -> cheapest single-site price) or None where the page is used, note)
E = {
    10094: ("coral-pink", "345131", None, 28, 28, {"electric": 17}, {"ne": 28, "ew": 45},
            "Old Campground (sites 1-22, no hookups) $28 a night, double sites $60; New Campground (sites 23-34, water "
            "and electric) $45."),
    10095: ("sand-hollow", "345761", r"^Westside", 50, 50, {}, {"fhu": 50},
            "Westside Campground: full hookups $50 a night."),
    10096: ("goosenecks", None, None, 10, 10, {}, None,
            "$10 a night, 'First-come, first-served sites only (no reservations)'; extra vehicle $5."),
    10097: ("quail-creek", "345711", None, 28, 28, {"electric": 12}, {"ne": 28, "ew": 40},
            "Primitive sites $28 a night; sites with power and water $40."),
    10098: ("snow-canyon", "345781", None, 40, 40, {"electric": 5}, {"ne": 40, "ew": 45},
            "Non-hookup sites $40 a night; water and electric $45."),
    10099: ("gunlock", "346810", None, 45, 45, {}, {"ew": 45},
            "Hookup sites (water and electric) $45 a night."),
    10100: ("kodachrome-basin", "345501", r"^Basin", 35, 35, {"full_hookup": 10}, {"ne": 35, "fhu": 45},
            "Basin Campground: standard sites (no hookups) $35 a night; full hookups $45 (13 sites)."),
    10101: ("escalante-petrified-forest", "345221", None, 30, 30, {"electric": 10, "full_hookup": 30},
            {"ne": 30, "e": 40, "fhu": 60},
            "Loop A: standard sites $30 a night, water and electric $40; Loops B and C: full hookups $60."),
    10102: ("otter-creek", "345611", None, 40, 40, {"electric": 5}, None,
            "Pull-through sites without hookups $40 a night (the booking site lists them but quotes no 2027 price); "
            "beachfront sites with electric and water $45; tent sites $30."),
    10103: ("dead-horse", "344161", r"^Wingate", 60, 60, {}, {"e": 60},
            "Wingate's RV sites (20/30/50-amp electric; no water fill) $60 a night in March-June and September-October, "
            "$50 the rest of the year."),
    10104: ("fremont-indian", "345271", r"^CASTLE ROCK", 20, 20, {}, {"ne": 20},
            "Castle Rock: sites without hookups $20 a night, double sites $40."),
    10105: ("goblin-valley", "344291", None, 45, 45, {}, {"ne": 45},
            "Main campground (no hookups) $45 a night; extra vehicle $20."),
    10106: ("fremont-indian", "345271", r"^Sam Stowe", 35, 35, {}, {"fhu": 35},
            "Sam Stowe: full-hookup RV sites (50/30-amp, water, sewer) $35 a night."),
    10107: ("utahraptor", "351951", r"^Loop \d", 50, 50, {}, {"ew": 50},
            "Gastonia Campground: water and 20/30/50-amp electric, $50 a night on the booking site (the fee page lists "
            "only Fossil Flats' primitive sites, $30)."),
    10108: ("green-river", "344341", None, 45, 45, {}, None,
            "Main Campground $45 a night, every site with electric and water (the fee page); the booking site quotes $45 "
            "for November 2026 and $50 from January 2027."),
    10109: ("millsite", "344551", None, 25, 25, {"water": 5}, {"e": 25, "ew": 30},
            "Sites 11-20 (electric only) $25 a night; sites 1-10 (electric and water) $30."),
    10110: ("palisade", "344641", None, 35, 35, {"electric": 5, "full_hookup": 10}, {"ne": 35, "ew": 40, "fhu": 45},
            "Sites without hookups $35 a night (doubles $70); electric sites $40; full hookups (Sanpitch, Wakara) $45 "
            "(doubles $90)."),
    10111: ("huntington", "344391", None, 30, 30, {"full_hookup": 3}, {"ew": 30, "fhu": 33},
            "Partial hookups (electric and water) $30 a night; full hookups $33."),
    10112: ("yuba", "343961", r"^Painted Rocks", 45, 45, {}, {"ew": 45},
            "Painted Rocks: electric sites $45 a night, doubles $90."),
    10113: ("yuba", "343961", r"^OASIS", 40, 40, {"electric": 5}, {"ne": 40, "e": 45},
            "Oasis: non-electric sites (#20-28) $40 a night; electric sites (#1-19) $45."),
    10114: ("scofield", "344771", r"^MOUN", 20, 20, {"full_hookup": 15}, {"ne": 20, "fhu": 35},
            "Mountain View: standard sites (no services) $20 a night; one full-hookup site $35."),
    10115: ("scofield", "344771", r"^MADS", 20, 20, {"electric": 10, "full_hookup": 15}, {"ne": 20, "ew": 30, "fhu": 35},
            "Madsen Bay: standard sites $20 a night, electric and water $30, full hookups $35."),
    10116: ("starvation", "342801", r"^MOUN", 40, 40, {}, {"ew": 40, "fhu": 40},
            "Mountain View Campground: $40 a night in the busy season, partial (water and electric) or full hookups "
            "alike; $20 in winter."),
    10117: ("utah-lake", "343871", None, 50, 50, {}, {"ew": 50},
            "Lakeshore Campground (water and 30-amp electric) $50 a night."),
    10118: ("deer-creek", "342171", None, 40, 40, {"full_hookup": 10}, {"ne": 40, "fhu": 50},
            "Great Horned Owl (no hookups) $40 a night; Chokecherry full hookups $50 ($60 at its 50-amp sites); Fox Den "
            "full hookups (50-amp) $60."),
    10120: ("steinaker", "342811", None, 30, 30, {"electric": 10, "full_hookup": 20}, {"ne": 30, "e": 40, "fhu": 50},
            "Summer: dry sites $30 a night, electric only $40, full hookups $50; winter $25 / $25 / $35."),
    10121: ("wasatch-mountain", "342921", None, 45, 45, {"full_hookup": 5}, {"ew": 45, "fhu": 50},
            "Cottonwood loop water and electric $45 a night; full hookups $50 (Cottonwood, Mahogany), $60 at Soldier "
            "Hollow and Chalet. Oak Hollow's hookup sites are tent sites on the booking site; Little Deer Creek's "
            "primitive sites (not on the booking site) are $25."),
    10122: ("red-fleet", "342741", None, 50, 50, {"full_hookup": 10}, {"ew": 50, "fhu": 60},
            "Water and 30-amp electric $50 a night; full hookups $60 (the booking site; the park's fee page lists no "
            "camping)."),
    10123: ("great-salt-lake", "346808", r"^GSL", 40, 40, {"full_hookup": 20}, {"ew": 40, "fhu": 60},
            "Water and electric $40 a night; full hookups $60 (one site); walk-in tent sites $20."),
    10124: ("rockport", "342751", None, 35, 35, {"electric": 10}, {"ne": 35, "ew": 45},
            "Cottonwood, Crandall Cove, Riverside and Twin Coves (no hookups) $35 a night, doubles $45; Juniper (water "
            "and electric) $45, doubles $70."),
    10125: ("east-canyon", "342191", None, 40, 40, {"electric": 10, "full_hookup": 15}, None,
            "Big Rock (no hookups) $40 a night, doubles $70; Dixie Creek partial hookups $50, full hookups $55, doubles "
            "$80 / $90 (the fee page). The booking site quotes less for summer 2027: Big Rock $35, Dixie Creek $40 "
            "partial and $45 full."),
    10126: ("echo", "349750", r"^Dry Hollow", 40, 40, {}, {"ew": 40},
            "Dry Hollow: 50-amp electric and water $40 a night, double sites $70."),
    10127: ("antelope-island", "343031", r"^White Rock", 40, 40, {}, {"ne": 40},
            "White Rock Bay: standard sites $40 a night (covers 2 vehicles; vault toilets)."),
    10128: ("antelope-island", "343031", r"^Bridger Bay", 30, 30, {"electric": 10}, {"ne": 30, "ew": 40},
            "Bridger Bay: standard sites (no hookups) $30 a night; water and electric $40."),
    10129: ("willard-bay", "343941", r"^South Marina", 60, 60, {}, {"fhu": 60},
            "South Marina: full hookups $60 a night."),
    10130: ("willard-bay", "343941", r"^Cottonwood", 60, 60, {}, {"fhu": 60},
            "Cottonwood: full hookups $60 a night."),
    10131: ("willard-bay", "343941", r"^Willow Creek", 60, 60, {}, {"ew": 60},
            "Willow Creek: water and electric $60 a night."),
    10132: ("hyrum", "343401", None, 40, 40, {"electric": 10}, {"ne": 40, "ew": 50},
            "Dry sites $40 a night; water and power $50."),
    10133: ("bear-lake", "343061", r"^(BIG CREEK|BIRCH)", 55, 55, {}, None,
            "Rendezvous Beach full hookups: summer $55 a night for Utah residents, $60 for others; the rest of the year "
            "$40 / $45 (the fee page). The booking site quotes $45 for June-August 2027."),
    10134: ("bear-lake", "343061", r"^SOUTH EDEN", 35, 35, {}, None,
            "South Eden partial hookups: summer $35 a night for Utah residents, $40 for others; the rest of the year "
            "$25 / $30 (the fee page). The booking site quotes $40 for June-August 2027."),
    10135: ("bear-lake", None, None, 30, 30, {}, None,
            "Cisco Beach primitive sites: summer $30 a night for Utah residents, $35 for others; the rest of the year "
            "$20 / $25. First come, first served."),
    10136: ("bear-lake", "343061", r"^NORTH EDEN", 45, 45, {}, None,
            "North Eden partial hookups: summer $45 a night for Utah residents, $50 for others; the rest of the year "
            "$30 / $35 (the fee page). The booking site quotes $40 for June-August 2027."),
    10189: ("echo", "349750", r"^Red Rock", 50, 50, {}, {"fhu": 50},
            "Red Rock Marina Campground: full hookups $50 a night."),
}
SKIP_TYPE = re.compile(r"(?i)hammock|camper trailer|wagon|teepee|pit house|bunkhouse|tent only|group|cabin|yurt")


def money(p):
    m = re.search(r"\$([\d,]+\.\d\d)", p or "")
    return float(m.group(1).replace(",", "")) if m else None


tent = collections.defaultdict(list)    # (parkId, loop, type) -> each sampled site allows only tents
for line in open(os.path.join(HERE, "ut_site_details_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    cat = r.get("Looking For Category") or ""
    tent[(r["parkId"], r["loop"], r["type"])].append(bool(cat) and not re.search(r"RV|Trailer", cat))
TENT = {k for k, v in tent.items() if all(v)}
quotes = collections.defaultdict(list)  # parkId -> site records
for line in open(os.path.join(HERE, "ut_booking_rates_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    quotes[r["park"][3:-5]].append(r)


def kind(r):
    e = (r.get("Electricity Hookup") or "").strip() not in ("", "N")
    w = (r.get("Water Hookup") or "") in ("Y", "Yes")
    s = (r.get("Sewer Hookup") or "") in ("Y", "Yes")
    return "fhu" if e and w and s else "ew" if e and w else "e" if e else "ne"


out, flags = [], []
for eid, (slug, pid, loops, base, hi, sur, want, what) in sorted(E.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    seen = {}
    if pid:
        for r in quotes[pid]:
            if SKIP_TYPE.search(r.get("Type") or "") or (pid, r.get("loop"), r.get("Type")) in TENT:
                continue
            if loops and not re.search(loops, r.get("loop") or ""):
                continue
            ln = r.get("Max Vehicle Length")
            q = money(r.get("price"))
            if q is None or (ln and ln.isdigit() and int(ln) < 23):
                continue
            k = kind(r)
            seen[k] = min(seen.get(k, q), q)
        got = {k: int(v) if float(v).is_integer() else v for k, v in seen.items()}
        # Every declared kind as declared; another kind (electric-only sites beside water-and-electric ones) only at a
        # declared price, never below the base.
        odd = {k: v for k, v in got.items() if k not in (want or {}) and (v < base or v not in (want or {}).values())}
        if want is not None and ({k: got.get(k) for k in want} != want or odd):
            flags.append((eid, e["name"], f"booking site {got} vs declared {want}"))
        elif want is None:
            print("page used:", eid, e["name"][:40], "booking site", got)
    fees = {"nightly_low": base, "nightly_high": hi, "currency": "USD", "surcharges": {**sur, "weekend": 0},
            "checked": "2026"}
    if slug == "bear-lake":
        fees["nonresident"] = NR
    if pid:
        fees["reservation_fee"] = 8
    fees["note"] = (what + (" Plus the $8 reservation fee." if pid else "") + " Camping covers one vehicle. Utah State "
                    "Parks' fee page" + (" and its booking site's June 2027 quotes (a Saturday the same)" if pid else "") +
                    f", read {D}.")
    src = PAGE.format(slug) + " (camping fees)"
    if pid:
        names = sorted({r.get("loop") for r in quotes[pid] if not loops or re.search(loops, r.get("loop") or "")})
        src += (f" + utahstateparks.reserveamerica.com parkId {pid}" + (f" ({', '.join(names)})" if loops else "") +
                f": every site's 1-night quote for 2027-06-15 with 'Reservation Fees $8.00' "
                f"(ut_booking_rates_2026-10-12.jsonl) and one per loop, type and price for 2027-06-19")
    out.append({"id": eid, "name": e["name"], "fees": fees, "source": src + f", read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "UT findings;", len(flags), "flagged; tent-only loops:", sorted(k for k in TENT if k[0] in
      {v[1] for v in E.values()}))
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f["surcharges"], f.get("reservation_fee"), f.get("nonresident"))
for fl in flags:
    print("FLAG", *fl)
