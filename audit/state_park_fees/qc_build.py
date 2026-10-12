"""Quebec (SEPAQ) findings: every campsite of each entry's campground(s) on sepaq.com's booking search for four 2027
nights - Tue 2027-06-08 and Tue 2027-09-07 (low season), Tue 2027-07-13 and Sat 2027-07-17 (high season #2) - read
2026-10-12 through the one-browser driver (qc_sites_2026-10-12.json; 2027 bookings open 2026-11-08, but the search
already prices every site), plus site detail pages for their eligible equipment, up to four per loop, type and price until one takes a 23-ft rig
(qc_site_details_2026-10-12.json).

    python3 -I qc_build.py OUT

SEPAQ prices a site by its type, its campground's rate level and the night: low season (to June 10 and from September
6 in 2027), high season #1 (June 11 - July 8, August 15 - September 5) and #2 (July 9 - August 14), Sunday-Thursday or
Friday-Saturday ('2027 season' table on https://www.sepaq.com/camping/emplacement/tente.dot, 'Taxes not included.
National park entry fees not included.'). The base is the cheapest site with no hookups (rustic or semi-serviced)
whose eligible equipment takes a 23-ft trailer or motorhome; where none does, the cheapest hookup site that does.
nightly_low is its low-season Tuesday price, nightly_high its high-season #2 Tuesday price, weekend the Saturday
difference; electric and full_hookup are the high-season #2 Tuesday differences to the cheapest fitting electric and
3-service sites. National parks add the daily entry fee, $10.30 an adult, children free, taxes included
(https://www.sepaq.com/pq/tarification-parcs-nationaux.dot: 'For a stay, the entry fee is in addition to the
accommodation fee'); wildlife reserves and the two tourist centres charge none."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
LOW, LOW2, TUE, SAT = "2027-06-08", "2027-09-07", "2027-07-13", "2027-07-17"
CLASS = {"Rustic campsite": "R", "Semi-serviced campsite": "S", "Campsite furnished with 1 service (water)": "W",
         "Campsite furnished with 1 service (electricity)": "E",
         "Campsite furnished with 2 services (water, electricity)": "EW",
         "Campsite furnished with 2 services (water, sewer hookup)": "WS",
         "Campsite furnished with 3 services (water, electricity, sewer hookup)": "EWS"}
WORD = {"R": "a rustic site", "S": "a semi-serviced site", "W": "water", "E": "electric", "EW": "electric and water",
        "WS": "water and sewer", "EWS": "3 services (electric, water, sewer)"}
NOHOOK = ("R", "S", "W")
ev = json.load(open(os.path.join(HERE, "qc_sites_2026-10-12.json"), encoding="utf-8"))
details = json.load(open(os.path.join(HERE, "qc_site_details_2026-10-12.json"), encoding="utf-8"))
sites = []                      # one record per site and night, as read
for eid, li, ti, name, slug, *prices in ev["sites"]:
    leaf = ev["leaves"][li]
    for date, price in zip(ev["dates"], prices):
        sites.append({"eid": eid, "leaf": leaf, "type": ev["types"][ti], "name": name, "date": date,
                      "price": price, "href": f"/en/reservation/camping/{leaf}/{slug}"})


def fits(href):
    """True when the site's eligible equipment takes a 23-ft trailer or motorhome (None when not read)."""
    d = details.get(href)
    if d is None:
        return None
    for x in d.get("Eligible Equipment", []):
        if re.search(r"(?i)tent trailer", x) or not re.search(r"(?i)\b(trailers?|recreation(al)? vehicles?)\b", x):
            continue
        if re.search(r"(?i)all types", x):              # 'All types of trailers', 'All types of recreational vehicles'
            return True
        m = re.search(r"\((\d+) feet\)", x)            # 'Trailer under 8 meters (25 feet)'
        if m and int(m.group(1)) > 23:
            return True
    return False


NATIONAL = re.compile(r"(?i)parc national")
out, flags = [], []
by_entry = collections.defaultdict(list)
for s in sites:
    if s["type"] in CLASS:
        by_entry[s["eid"]].append(s)
for eid in sorted(by_entry):
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    groups = collections.defaultdict(lambda: {"dates": collections.defaultdict(list), "href": None, "n": set()})
    tue_price = {(s["leaf"], s["href"]): s["price"] for s in by_entry[eid] if s["date"] == TUE}
    for s in by_entry[eid]:
        key = (s["leaf"], CLASS[s["type"]], tue_price.get((s["leaf"], s["href"])))
        g = groups[key]
        if s["price"] is not None:          # no price: the campground is closed that night
            g["dates"][s["date"]].append(s["price"])
        g["n"].add(s["href"])
        g["href"] = g["href"] or s["href"]
    # a group (loop, type, high-season price) counts when ANY site read in it takes a 23-ft rig: limits differ
    # site by site inside one loop (Arthabaska's rustic sites run from 15-ft to 40-ft trailers)
    fit = {k: g for k, g in groups.items() if k[2] is not None and any(fits(h) for h in g["n"])}   # priced in high season
    unread = [k for k, g in groups.items() if not any(h in details for h in g["n"])]
    if unread:
        flags.append((eid, e["name"], f"{len(unread)} groups without a detail read")); continue

    def best(classes, date):
        vals = [min(v) for k, g in fit.items() if k[1] in classes for d, v in g["dates"].items() if d == date and v and min(v)]
        return min(vals) if vals else None
    kinds = sorted({k[1] for k in fit}, key=list(CLASS.values()).index)
    if not kinds:
        flags.append((eid, e["name"], "no site takes a 23-ft rig")); continue
    base_cls = [c for c in ("R", "S") if c in kinds] or [kinds[0]]
    lows = [x for x in (best(base_cls, LOW), best(base_cls, LOW2)) if x]
    hi, sat = best(base_cls, TUE), best(base_cls, SAT)
    if hi is None or sat is None:
        flags.append((eid, e["name"], f"no high-season price for {base_cls}: {sorted(k[1:] for k in fit)}")); continue
    lo = min(lows) if lows else hi          # closed on both low-season nights read (June 8, September 7)
    sur = {}
    if base_cls[0] in NOHOOK:
        el = best(("E", "EW", "EWS"), TUE)
        if el:
            sur["electric"] = round(el - hi, 2)
        fh = best(("EWS",), TUE)
        if fh:
            sur["full_hookup"] = round(fh - hi, 2)
    elif base_cls[0] in ("E", "EW"):
        fh = best(("EWS",), TUE)
        if fh:
            sur["full_hookup"] = round(fh - hi, 2)
    sur["weekend"] = round(sat - hi, 2)
    parts = []
    for c in kinds:
        a = [x for x in (best((c,), LOW), best((c,), LOW2)) if x]
        b = best((c,), TUE)
        parts.append(f"{WORD[c]} ${min(a):.2f}-{b:.2f}" if a else f"{WORD[c]} ${b:.2f}")
    national = bool(NATIONAL.search(e["name"]))
    text = ((f"${lo:.2f} a night in low season to ${hi:.2f} on a high-season weeknight" if lows else
             f"${hi:.2f} on a high-season weeknight (no low-season price on June 8 or September 7, 2027)") +
            f" for the cheapest site that takes a 23-ft rig ({WORD[base_cls[0]]}); Friday and Saturday "
            f"${sur['weekend']:.2f} more. By site type (low-season Tuesday - high-season Tuesday): " + "; ".join(parts) +
            ". Plus taxes" +
            (" and the national park's daily entry fee ($10.30 an adult, taxes included; children free)" if national else "") +
            f". SEPAQ's booking site, 2027 nights, read {D}.")
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD", "surcharges": sur, "checked": "2027", "note": text}
    if national:
        fees["entrance"] = {"resident": 10.3, "nonresident": 10.3, "per": "person_day"}
    leaves = sorted({k[0] for k in groups})
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": "https://www.sepaq.com/en/reservation/search (every campsite of " + ", ".join(leaves[:4]) +
                          (f" and {len(leaves) - 4} more loops" if len(leaves) > 4 else "") +
                          f"; 2027-06-08, 2027-07-13, 2027-07-17, 2027-09-07) + each loop's site detail pages (eligible "
                          f"equipment), read {D}" + (" + https://www.sepaq.com/pq/tarification-parcs-nationaux.dot "
                                                      "(daily access $10.30 an adult)" if national else "")})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "QC findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:44], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
