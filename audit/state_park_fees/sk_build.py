"""Saskatchewan Provincial Parks findings: the 2026-27 Provincial Parks Rates and Fees table (text in
sk_rates_and_fees_2026-27.txt; 'Rates are set as of April 1, 2026, and until further notice'; 'Fees include all
applicable taxes unless otherwise noted'), checked on the booking site parks.saskatchewan.ca (classic ReserveAmerica,
contract SKPP): ra_list.py listed every site of each park (sk_sites_2026-10-12.json) and ra_rate_card.py read the
posted 'Price Rate' of up to two sites of each loop and site type for 2027-06-15 (sk_rate_card_2026-10-12.jsonl).

    python3 -I sk_build.py OUT

The table's nightly camping fees are the same in every park: Fully Serviced $49, Electrical $35, Non-Electrical $20,
Economy $18; 'A reduced service fee discount of $4 per night will be applied beginning October 1 to March 31 to Nightly
Electric and Nightly Non-Electric sites' (the fees page); reservation fee $12 online or in park, $14 through the call
centre, 'applied to each separate reservation'; vehicle entry permit $11 a day, $42 a week, $82 a year, free for
Saskatchewan residents 65 and older. An entry's base is its cheapest site type a 23-ft rig fits (a site's maximum
equipment length; a blank one is unknown, not short), and electric and full service are add-ons on it. Walk-in,
hike-in, group, seasonal, double, yurt and other non-campsite types are left out."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TABLE = "https://parks.saskatchewan.ca/resource/contracts/skpp/Parks_Rates_and_Fees_Table-2026-27.pdf"
FEES = "https://saskparks.tourismsaskatchewan.com/fees"
PRICE = {"economy": 18, "ne": 20, "e": 35, "fhu": 49}
WORD = {"economy": "economy", "ne": "non-electric", "e": "electric", "fhu": "full service"}
KIND = {"Nightly Economy": "economy", "Nightly Non-Electric": "ne", "Nightly Electric": "e",
        "Accessible - Nightly Electric": "e", "Nightly Full Service": "fhu", "Accessible - Nightly Full Service": "fhu"}
NOT_DRIVE_IN = re.compile(r"(?i)walk-in|hike-in|group")
NR = re.compile(r"-\s*NR$")
# entry -> (parkId, its loops (regex) or None for the whole park)
ENTRY = {
    9158: ("290401", r"^Anderson Point"), 9178: ("290401", r"Murray Point"),
    9159: ("290515", None), 9161: ("290310", None), 9163: ("290510", r"^Little Fishing Lake"), 9164: ("290170", None),
    9165: ("290405", r"^Minowukaw$"), 9166: ("290405", r"^Sandy Bay"),
    9167: ("290320", r"^Coldwell"), 9173: ("290320", r"^(?!Coldwell)"),
    9169: ("290245", None), 9170: ("290125", r"^Meadows$"), 9171: ("290125", r"^Rainbow$"), 9172: ("290125", r"^Terrace$"),
    9174: ("290325", None), 9175: ("290275", None), 9176: ("290180", None), 9177: ("290285", None), 9179: ("290290", None),
    9181: ("290375", r"^Missinipe$"), 9182: ("290375", r"^Nemeiben"), 9183: ("290375", r"^Nut Point"),
    9184: ("290375", r"^Wadin"), 9186: ("290500", None),
    9187: ("290460", r"^Greig Lake"), 9188: ("290460", r"^Kimball Lake"), 9189: ("290460", r"^Matheson Lake"),
    9190: ("290460", r"^Mistohay"), 9191: ("290460", r"^Waterhen"), 9192: ("290460", r"^Murray Doell"),
    9193: ("290460", r"^Sandy Beach"), 9194: ("290250", None),
    9195: ("290415", r"^Baldy Lake$"), 9196: ("290415", r"^Ispuchaw$"), 9197: ("290415", r"^Lower Fishing Lake$"),
    9198: ("290415", r"^Zeden Lake$"), 9199: ("290291", r"^Parr Hill$"), 9201: ("290291", r"^Townsend Lake$"),
    9200: ("290340", None), 9204: ("290215", None), 9205: ("290135", None),
}
sites = json.load(open(os.path.join(HERE, "sk_sites_2026-10-12.json"), encoding="utf-8"))
card = [json.loads(l) for l in open(os.path.join(HERE, "sk_rate_card_2026-10-12.jsonl"), encoding="utf-8")]
RES = " the $12 reservation fee ($14 through the call centre) and"
OCT = " $4 a night less from October 1 on electric and non-electric sites."
TAIL = (" Taxes included.{oct} Plus{res} a vehicle entry permit, $11 a day ($42 a week, $82 a year; free for Saskatchewan "
        f"residents 65 and older). Sask Parks' 2026-27 rates and fees table, matched on its booking site, read {D}.")


def rate(r):
    m = re.search(r"\$([\d,]+\.\d\d) Per Night", r.get("rate") or "")
    return float(m.group(1).replace(",", "")) if m else None


out, flags = [], []
for eid, (pid, loops) in sorted(ENTRY.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    mine = [s for s in sites[pid]["sites"] if len(s["cells"]) > 1 and s["cells"][1] in KIND
            and not NOT_DRIVE_IN.search(s["cells"][0]) and (loops is None or re.search(loops, s["cells"][0]))]
    if not mine:
        flags.append((eid, e["name"], f"no campsites in park {pid} loops {loops}")); continue
    count, fits, names, nr = collections.Counter(), collections.defaultdict(bool), set(), collections.Counter()
    reservable = any(not NR.search(s["cells"][0]) for s in mine)   # '- NR' / '-NR' loops: first come, first served
    for s in mine:
        k = KIND[s["cells"][1]]
        count[k] += 1
        ln = s["cells"][3] if len(s["cells"]) > 3 else ""
        fits[k] |= not ln.strip().isdigit() or int(ln) >= 23
        names.add(s["cells"][0])
        if NR.search(s["cells"][0]):
            nr[k] += 1
    # each type's price is the booking site's posted rate (the '- NR' sites post none: the table's), which must be
    # the table's or the table's less the $4 reduced-services discount (Bronson Forest's electric sites, $31)
    posted = collections.defaultdict(set)
    for c in card:
        if c["parkId"] == pid and c["loop"] in names and c["type"] in KIND and rate(c) is not None:
            posted[KIND[c["type"]]].add(rate(c))
    price, reduced, bad = {}, set(), []
    for k in count:
        v = posted.get(k) or {PRICE[k]}
        if len(v) > 1 or next(iter(v)) not in (PRICE[k], PRICE[k] - 4):
            bad.append((k, sorted(v)))
            continue
        price[k] = int(next(iter(v)))
        if price[k] != PRICE[k]:
            reduced.add(k)
    if bad:
        flags.append((eid, e["name"], f"booking site differs from the table: {bad}")); continue
    kinds = [k for k in ("economy", "ne", "e", "fhu") if count[k] and fits[k]]
    if not kinds:
        flags.append((eid, e["name"], f"no site type a 23-ft rig fits ({dict(count)})")); continue
    base = kinds[0]
    sur = {"weekend": 0}
    if base in ("economy", "ne") and "e" in kinds:
        sur["electric"] = price["e"] - price[base]
    if base != "fhu" and "fhu" in kinds:
        sur["full_hookup"] = price["fhu"] - price[base]
    def how(k):
        said = []
        if k in reduced:
            said.append(f"the table's ${PRICE[k]} less the $4 reduced-services discount")
        if nr[k] == count[k]:
            said.append("first come, first served")
        elif nr[k]:
            said.append(f"{count[k] - nr[k]} reservable, the other {nr[k]} first come, first served")
        return f" ({'; '.join(said)})" if said else ""
    parts = [f"{WORD[k]} ${price[k]}{how(k)}" for k in kinds]
    short = [WORD[k] for k in ("economy", "ne", "e", "fhu") if count[k] and not fits[k]]
    text = ("Any night of the week: " + "; ".join(parts) + "." +
            (f" (The {' and '.join(short)} sites here are too short for a 23-ft rig.)" if short else "") +
            TAIL.format(res=RES if reservable else "", oct=OCT if any(k in ("e", "ne") and k not in reduced for k in kinds) else ""))
    fees = {"nightly_low": price[base], "nightly_high": price[base], "currency": "CAD", "reservation_fee": 12,
            "entrance": {"resident": 11, "nonresident": 11, "per": "vehicle_day"}, "surcharges": sur, "checked": "2026",
            "note": text}
    if not reservable:
        del fees["reservation_fee"]
    out.append({"id": eid, "name": e["name"], "fees": fees,
        "source": f"{TABLE} (2026-27 rates, from 2026-04-01) + {FEES} (reduced-services discount) + parks.saskatchewan.ca "
                  f"parkId {pid} ({sites[pid]['name']}; {', '.join(sorted(names))}): each loop and site type's posted "
                  f"'Price Rate' for 2027-06-15 (sk_rate_card_2026-10-12.jsonl) and every site's type and maximum "
                  f"equipment length (sk_sites_2026-10-12.json), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "SK findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:48], f["nightly_low"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
