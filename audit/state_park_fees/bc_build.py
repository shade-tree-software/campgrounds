"""British Columbia findings, read 2026-10-12: BC Parks campgrounds, Recreation Sites and Trails BC sites and four
heritage-site campgrounds (page texts in bc_fee_pages_2026-10-12.txt).

    python3 -I bc_build.py OUT

BC Parks: the recreation user fee schedule (bc_fee_schedule_2026-10-12.txt) gives every park's frontcountry camping fee
'per party per night' for the summer (peak) season, June 15 to Labour Day, and the shoulder and winter seasons, by
campground where a park has several. The booking site (camping.bcparks.ca, GoingToCamp; gtc_probe.py ->
bc_booking_fees_2026-10-12.json, Tue 2027-06-15 and Sat 2027-06-19, peak season) answers the same fee for each fee
schedule, the same on a Saturday, and adds the electrical hook-up as its own line ('Additional Service Plus fees apply
for full-service electrical hook-ups'). Each entry: base = the booking site's fee for a non-electric site taking a
'Trailer or RV' over 18 ft in the entry's campground (else its electric site's fee plus the hook-up), checked against
the schedule's peak fee, or the schedule's peak fee where the entry is not on the booking site (first come, first
served: reservation fee 0); electric = the cheapest such electric site's hook-up line; weekend 0; shoulder and winter
fees in the note. The registry row (provincial:BC, bc_registry_2026-10-12.py) carries the $20 non-resident fee 'per
party per campground' and the $6 a night reservation fee (at most $18).

Recreation sites: each site's record (bc_rec_sites_2026-10-12.json, the sitesandtrailsbc.ca API) lists its overnight
fee with the dates it applies; no fee listed = free. Barkerville's Lowhee and Forest Rose, Kilby and Historic Hat Creek
Ranch: the operators' own rates. These are outside BC Parks' fees, so they get policy_ref none (bc_corrections)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
SCHED = "https://nrs.objectstore.gov.bc.ca/kuwyyf/recreation_user_fee_schedule_503f64b014.pdf"
FEESPAGE = "https://bcparks.ca/reservations/camping-fees/"
RSTAPI = "https://dj2qs6gf0wkg3.cloudfront.net/api/v1/recreation-resource/"


def fee_rows(path):
    """The schedule's frontcountry camping rows: park, area, [peak, shoulder, winter]; a name can wrap onto the lines
    above and below the row."""
    L = open(path, encoding="utf-8").read().split("\n")
    out = []
    for i, ln in enumerate(L):
        m = re.search(r"Frontcountry camping", ln)
        if not m or "SERVICE" in ln:
            continue
        cells = re.findall(r"\$\d+(?:\.\d+)?|(?<=\s)-(?=\s)", ln[m.end():])
        pre = [p for p in re.split(r"\s{2,}", ln[:m.start()].strip()) if p]
        park, area = (pre + ["", ""])[:2]
        if not park:
            up = [p for p in re.split(r"\s{2,}", L[i - 1].strip()) if p]
            dn = [p for p in re.split(r"\s{2,}", L[i + 1].strip()) if p]
            park = " ".join(x[0] for x in (up, dn) if x and "$" not in x[0] and "camping" not in " ".join(x).lower())
        out.append({"park": park, "area": area, "fees": cells, "line": i + 1})
    return out


STOP = {"provincial", "park", "parks", "campground", "the", "site", "of", "recreation", "area", "marine", "and", "south",
        "north", "memorial", "a", "k", "aka"}


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower().replace("'", "")) if w not in STOP}


def money(c):
    return float(c[1:]) if c and c.startswith("$") else None


def num(v):
    return int(v) if float(v).is_integer() else v


def amt(v):
    return f"${num(v)}" if v is not None else None


def cad(v):
    return f"${v:.2f}" if not float(v).is_integer() else f"${int(v)}"


SCHEDULE = fee_rows(os.path.join(HERE, "bc_fee_schedule_2026-10-12.txt"))
# Entries whose schedule row the name match cannot find (special characters, an unlabelled row, a misspelt area).
ROW = {8411: ("E.C. Manning Park", "Lightning Lakes Campground", ["$51", "$35"]),
       8396: ("Sx̱ótsaqel/Chilliwack Lake Park", "", ["$32", "$22"]),
       8547: ("Tā Ch'ilā Park [a.k.a. Boya Lake Park]", "", ["$29", "$20"]),
       8528: ("Nisg̱a'a Memorial Lava Bed Park", "", ["$20", "$20"]),
       8406: ("Skagit Valley Park", "Silver Tip", ["$18", "$18"]),
       8551: ("Stone Mountain Park", "", ["$20", "$20"])}
# Campground maps on the booking site for entries named for one campground of a park.
MAPS = {8391: r"Gold Creek", 8395: r"Maple Bay", 8411: r"Lightning Lake", 8415: r"Mule Deer", 8417: r"Coldspring", 8393: r"Delta Grove",
        8397: r"Entrance Bay", 8401: r"Clear Creek", 8398: r"Alouette", 8402: r"North Beach", 8405: r"Ross Lake",
        8390: r"Hicks", 8407: r"Lakeside|Deer Lake", 8408: r"Bench", 8441: r"Buttle Lake", 8445: r"Ralph River",
        8467: r"Davis Creek|Cove Loop", 8472: r"Lost Ledge", 8474: r"Packrat Point", 8519: r"Robson Meadows",
        8520: r"Robson River", 8523: r"Lucerne", 8521: r"Clearwater Lake", 8522: r"Falls Creek", 8509: r"Mahood Lake",
        8549: r"Strawberry Flats", 8550: r"MacDonald", 8421: r"Hampton", 8468: r"Alces", 8469: r"White River",
        8470: r"Inlet Creek", 8471: r"Home Basin", 8505: r"Pyramid", 8406: r"Silver ?[Tt]ip", 8496: r"Shelter Bay",
        8511: r"Atnarko", 8512: r"Fisheries", 8498: r"Sunset View", 8499: r"Emerald Bay", 8502: r"Arrowhead",
        8492: r"Bush Creek"}
FREE = {8532: "'No camping fee is charged at this park.' (its page)",
        8533: "'No camping fee currently charged at this park and no services are provided; it is user maintained.' (its "
              "page)",
        8538: "'There is presently no fee for camping.' (its page)"}
UNPRICED = {8448: "first come, first served; 'For camping fee rates, contact the park caretaker' (no published rate)",
            8461: "no fee published, and its page says the area 'is best suited to truck and camper units as opposed to "
                  "trailers or motor homes' (an inclusion question)",
            8506: "no fee published (not in the fee schedule; the page lists only '~20 sites')",
            8403: "the operator now books Riverside as a group site 'by phone call only', and the recreation sites record "
                  "lists it Closed (its $17 fee ran 2023-2025) - an inclusion question"}
probe = {str(p["id"]): p for p in json.load(open(os.path.join(HERE, "bc_booking_fees_2026-10-12.json"),
                                                 encoding="utf-8"))["parks"]}
rst = json.load(open(os.path.join(HERE, "bc_rec_sites_2026-10-12.json"), encoding="utf-8"))
RV = re.compile(r"Trailer or RV")


def schedule_row(eid, e):
    if eid in ROW:
        park, area, fees = ROW[eid]
        return {"park": park, "area": area, "fees": fees}
    ew = words(e["name"])
    cands = [r for r in SCHEDULE if words(r["park"]) and words(r["park"]) <= ew]
    if cands:
        best = max(len(words(r["park"])) for r in cands)
        cands = [r for r in cands if len(words(r["park"])) == best]
    if len(cands) > 1:
        sel = [r for r in cands if r["area"] and words(r["area"]) <= ew]
        cands = sel or [r for r in cands if not r["area"]] or cands
    return cands[0] if len({tuple(r["fees"]) for r in cands}) == 1 and cands else None


# Campgrounds priced from their own pages: Cedar Point (a BC Parks page, not in the schedule) and the heritage sites
# (outside BC Parks' fees).
OWN = {
    8516: (25, 25, {"weekend": 0}, None,
           "'Vehicle-accessible camping fee: $25 per party per night' and 'A $20 fee is added for anyone who is not a B.C. "
           "resident' (its BC Parks page); sites are reservable through the park, and campers arriving when staff are away "
           "choose a site and pay later.",
           "https://bcparks.ca/cedar-point-park/ (page data: frontcountry camping description), read " + D),
    8515: (27, 27, {"electric": 10, "full_hookup": 30, "weekend": 0}, 5,
           "Lowhee Campground (Barkerville), June 18 - September 28, 2026: unserviced $27 a night, 30-amp power $37, full "
           "service $57, plus 5% GST; reservable sites a $5 booking fee; no out-of-province fee.",
           "https://barkerville.ca/plan/campgrounds/ (Lowhee rates, GST, booking fee), read " + D),
    8596: (27, 27, {"electric": 10, "weekend": 0}, 5,
           "Forest Rose Campground (Barkerville), May 14 - September 14, 2026: unserviced $27 a night, 30-amp power $37, "
           "plus 5% GST; reservable sites a $5 booking fee; no out-of-province fee.",
           "https://barkerville.ca/plan/campgrounds/ (Forest Rose rates, GST, booking fee), read " + D),
    8392: (40, 45, {"weekend": 0}, 7,
           "Kilby's 2026 rates: May 1 - September 30 $40 a night on the bush side, $45 on the beach side; March, April and "
           "October $30; November - February $20 (eight first-come sites). Reservation fee $7 for one night, $12 for two, "
           "$18 for three or more ($5 more by phone).",
           "https://kilby.ca/campground/ (2026 nightly rates, reservation fees), read " + D),
    8682: (43, 43, {"electric": 10, "weekend": 0}, None,
           "Non-serviced RV sites C$43 a night, serviced (water and 30-amp electric) C$53 on the ranch's Campspot booking "
           "page (read for a closed-season date); open from May 1 in 2026.",
           "https://www.campspot.com/book/historic-hat-creek-ranch (availability API: Non-Serviced RV Site C$43.00, "
           "Serviced RV Site C$53.00) + https://hatcreek.ca/stay, read " + D),
}
out, flags = [], []
for eid in sorted(i for i, e in rows.items() if e["state"] == "BC" and e.get("ownership") == "provincial"):
    e = rows[eid]
    if e.get("fees") or eid in UNPRICED or eid in OWN:
        continue
    w = e.get("website") or ""
    if eid in FREE:
        out.append({"id": eid, "name": e["name"], "fees": {
            "nightly_low": 0, "nightly_high": 0, "currency": "CAD", "reservation_fee": 0, "checked": "2026",
            "note": f"Free: {FREE[eid]} First come, first served. Read {D}."},
            "source": f"{w.split()[0]} (page data: camping description), read {D}"})
        continue
    if str(eid) in rst:
        r = rst[str(eid)]
        f = r["overnight_fees"]
        if f:
            x = f[0]
            v, start, end = x["fee_amount"], x["fee_start_date"][:10], (x.get("fee_end_date") or "")[:10]
            text = (f"${num(v)} a night (the recreation sites record: overnight camping fee for {start} to {end})" +
                    (", the 2025 season's; the same operator's Maple Grove is $20 for 2026" if end.startswith("2025") else
                     "") + ".")
        else:
            v, text = 0, "Free: the recreation sites record lists no overnight fee."
        res = (r.get("reservation") or {}).get("reservation_website")
        text += (f" Reservations through the operator ({res})." if res else " First come, first served.") + \
            f" Recreation Sites and Trails BC, read {D}."
        out.append({"id": eid, "name": e["name"], "fees": {
            "nightly_low": v, "nightly_high": v, "currency": "CAD", "surcharges": {"weekend": 0}, "checked": "2026",
            "note": text, **({} if res else {"reservation_fee": 0})},
            "source": f"{RSTAPI}{r['rec']} (overnight_fees: amount, dates, every day of the week) via sitesandtrailsbc.ca, "
                      f"read {D}"})
        continue
    row = schedule_row(eid, e)
    m = re.search(r"resourceLocationId=(-?\d+)", w)
    p = probe.get(m.group(1)) if m else None
    if p is None and row:       # not linked: the park by name, if it is on the booking site
        pw = words(row["park"])
        p = next((q for q in probe.values() if words(q["park"]) == pw), None)
    ne, el = [], []                 # non-electric fees; (total, hook-up) of electric sites
    if p:
        pat = MAPS.get(eid, "")
        for s in p["schedules"]:
            if pat and not any(re.search(pat, x) for x in s["maps"]):
                continue
            if not any(RV.search(x) for x in s["equipment"]):
                continue
            f = s["fees"].get("2027-06-15")
            sat = s["fees"].get("2027-06-19")
            if not isinstance(f, list) or not f:
                continue
            assert f == sat, (eid, s["feeScheduleId"])
            elec = any("Serviced" in k for k in s["services"])
            if elec and len(f) > 1:
                el.append((f[0][0] + f[1][0], f[1][0]))
            else:
                ne.append(f[0][0])
    peak = money(row["fees"][0]) if row and row["fees"] else None
    hi = None
    if ne:
        base, hi = min(ne), max(ne)
    elif el:
        base = min(t for t, _ in el)
    elif peak is not None:
        base = peak
    else:
        flags.append((eid, e["name"], "no fee found", row, bool(p)))
        continue
    if ne and peak is not None and base != peak:
        flags.append((eid, e["name"], f"booking site {base} vs schedule peak {peak}"))
    sur = {"weekend": 0}
    if ne and el:
        sur["electric"] = num(min(t for t, _ in el) - base)
    shoulder = money(row["fees"][1]) if row and len(row["fees"]) > 1 else None
    winter = money(row["fees"][2]) if row and len(row["fees"]) > 2 else None
    on_site = bool(m) or bool(ne or el)    # linked, or its campground found on the booking site
    only_el = bool(el) and not ne
    hook = min(h for _, h in el) if el else None
    text = (f"Summer (June 15 to Labour Day) {cad(base)}" + (f"-{cad(hi)[1:]}" if hi and hi != base else "") +
            " a night per party" +
            (f": the camping fee {cad(base - hook)} plus the {cad(hook)} electric hook-up (every site here has one)"
             if only_el else f"; electric sites {cad(min(t for t, _ in el))}" if el else "") +
            (f"; shoulder season {cad(shoulder)}" + (" plus the hook-up" if only_el else "")
             if shoulder is not None and (shoulder != base - (hook if only_el else 0)) else
             "; the same in the shoulder season" if shoulder is not None else "") +
            (f", winter {cad(winter)}" if winter is not None else "") + ". " +
            ("Reservable on camping.bcparks.ca." if on_site else "First come, first served.") +
            f" BC Parks' 2026 fee schedule" + (" and booking site" if p and (ne or el) else "") + f", read {D}.")
    fees = {"nightly_low": num(base), "nightly_high": num(hi or base), "currency": "CAD", "surcharges": sur, "checked": "2026",
            "note": text}
    if not on_site:
        fees["reservation_fee"] = 0
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{SCHED} ({row['park'] if row else '?'}{', ' + row['area'] if row and row['area'] else ''}: "
                          f"frontcountry camping {', '.join(row['fees']) if row else '?'} per party per night)" +
                          (f" + camping.bcparks.ca, {p['park']} (fee schedules for 2027-06-15 and 2027-06-19, "
                           f"bc_booking_fees_2026-10-12.json)" if p and (ne or el) else "") + f", read {D}"})
for eid, (lo, hi, sur, rf, text, src) in OWN.items():
    e = rows[eid]
    if e.get("fees"):
        continue
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD", "surcharges": sur, "checked": "2026",
            "note": text + f" Read {D}."}
    if rf is not None:
        fees["reservation_fee"] = rf
    out.append({"id": eid, "name": e["name"], "fees": fees, "source": src})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "BC findings;", len(flags), "flagged; unpriced:", sorted(UNPRICED))
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f.get("surcharges"), f.get("reservation_fee"))
for fl in flags:
    print("FLAG", *fl)
