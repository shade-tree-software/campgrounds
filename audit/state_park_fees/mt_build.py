"""Montana findings: state parks and one fishing access site, read 2026-10-12 (texts in mt_fee_pages_2026-10-12.txt).

    python3 -I mt_build.py OUT

FWP's state park fee schedule (the '2020 Montana State Parks Schedule', the scanned PDF its fees page links as the
'Montana State Parks Fee Schedule') is still in force: its figures are the 'CURRENT' column of FWP's 2026-06-24 fee
schedule justifications, which propose raising them no earlier than 2027. Peak season (third Friday in May to third
Sunday in September), a campsite without electricity: resident $18, nonresident $28 'includes daily entrance fee',
nonresident with the Entrance Pass $18; with electricity '$18 + $6 electricity fee = $24' ($34 nonresident);
backcountry/rustic $12 ($20 nonresident); off season (third Monday in September to third Thursday in May) $14 / $24,
electric $20 / $30, rustic the same; 'Montana accommodation tax ... is included'; reservation fee $10 an individual
campsite. FWP's fees page lists rustic campsites only at Thompson Chain of Lakes and Makoshika, and every park page puts
'Campsite fees' at '$4-$34 per night', which leaves no room for the schedule's +$5 premium campsite. The booking site
(montanastateparks.reserveamerica.com, classic ReserveAmerica, contract MT) gives each park's site types and lengths
(mt_sites_2026-10-12.json, ra_sites.py; two sites' details per loop and type in mt_site_details_2026-10-12.jsonl,
ra_rate_card.py) but quotes nothing in October: the reservation season and the three-month window are both closed
('Not available online' on every date tried).

Each park entry: base = the cheapest type a 23-ft rig fits (equipment length; blank = unknown; a loop whose sampled
sites allow only tents is left out); electric +$6 where the park has 3 or more electric sites a rig fits (a lone
electric site can be an accessible or host site); non-residents +$10 a night, which includes their daily entrance fee,
so no entrance is recorded (residents pay theirs with their vehicle registration); reservation fee $10 where the sites
are on the booking site; weekend 0 (one rate every night); off-season rates in the note. Ackley Lake, Lost Creek and
Medicine Rocks are first come, first served and not on the booking site: the standard rate (FWP's 2024 notice for
Ackley Lake: residents '$18/night', non-residents '$28/night'). Ennis fishing access site: the 2026 FAS fee table's
$12 a night with a Montana fishing license, $18 without, which its FishMT page lists."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
SCHEDULE = "https://fwp.mt.gov/binaries/content/assets/fwp/stateparks/fees-and-regulations/fee-schedule-2020-2021-final-.pdf"
JUSTIFY = ("https://fwp.mt.gov/binaries/content/assets/fwp/aboutfwp/public-comments/public-use-fees/"
           "2026-06-24-fee-schedule-justifications.pdf")
FEES = "https://fwp.mt.gov/stateparks/fees-and-general-information"
NR = {"type": "surcharge", "amount": 10, "per": "night", "applies_to": "base"}
KIND = {"Campsite": "standard", "Campsite Electric": "electric", "Rustic Campsite": "rustic"}
PRICE = {"rustic": 12, "standard": 18, "electric": 24}
PROPOSAL = (" FWP proposed in June 2026 to raise the standard site to $24 ($38 non-residents) and electric to $32 ($46), "
            "no earlier than 2027.")
listing = json.load(open(os.path.join(HERE, "mt_sites_2026-10-12.json"), encoding="utf-8"))
sampled = {}   # (parkId, siteId) -> the site's page allows only tents
for line in open(os.path.join(HERE, "mt_site_details_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    eq = " ".join(str(r.get(k) or "") for k in ("Allowed Equipment", "Looking For Category"))
    sampled[(r["parkId"], r["siteId"])] = bool(eq.strip()) and not re.search(r"(?i)rv|trailer|camper|motor|pop", eq)
# A loop and type whose sampled sites all allow only tents and that lists no length for any site is tent sites; elsewhere
# a sampled tent site is left out and the rest go by their length.
groups = collections.defaultdict(list)
for pid, park in listing.items():
    for s in park["sites"]:
        c = s["cells"]
        groups[(pid, c[0], c[1] if len(c) > 1 else "")].append(s)
tent_only = {k for k, members in groups.items()
             if any((k[0], s["siteId"]) in sampled for s in members)
             and all(sampled.get((k[0], s["siteId"]), True) for s in members if (k[0], s["siteId"]) in sampled)
             and not any(re.match(r"\d", s["cells"][3] if len(s["cells"]) > 3 else "") for s in members)}


def money_text(kinds, base):
    order = [k for k in ("rustic", "standard", "electric") if k in kinds]
    peak = "; ".join(f"{k} ${PRICE[k]}" for k in order)
    off = "; ".join(f"{k} ${PRICE[k] if k == 'rustic' else PRICE[k] - 4}" for k in order)
    return (f"Peak season (third Friday in May to third Sunday in September): {peak} a night for Montana residents; "
            f"non-residents $10 more, which includes their daily entrance fee (the resident rate with the $50 Nonresident "
            f"Entrance Pass). Off season: {off} (non-residents $10 more).")


out, flags = [], []
for pid, park in sorted(listing.items()):
    for eid in park["entry_ids"]:
        e = rows[eid]
        if e.get("fees"):
            continue
        n, fits = collections.Counter(), collections.defaultdict(bool)
        for s in park["sites"]:
            cells = s["cells"]
            t = cells[1] if len(cells) > 1 else ""
            if t not in KIND or (pid, cells[0], t) in tent_only or sampled.get((pid, s["siteId"])):
                continue
            m = re.match(r"(\d+)", cells[3] if len(cells) > 3 else "")
            n[KIND[t]] += 1
            fits[KIND[t]] |= m is None or int(m.group(1)) >= 23
        kinds = [k for k in n if fits[k] and n[k] >= 3]
        if not kinds:
            flags.append((eid, e["name"], dict(n)))
            continue
        base = min(kinds, key=PRICE.get)
        sur = {"weekend": 0}
        if base != "electric" and "electric" in kinds:
            sur["electric"] = 6
        short = [k for k in ("standard", "electric") if n[k] >= 3 and not fits[k]]
        text = (money_text(kinds, base) +
                (f" (The {' and '.join(short)} sites here are too short for a 23-ft rig.)" if short else "") +
                " Plus the $10 reservation fee. Montana accommodation tax included." + PROPOSAL +
                f" FWP's fee schedule (in force since 2020) and its booking site's site types, read {D}.")
        out.append({"id": eid, "name": e["name"], "fees": {
            "nightly_low": PRICE[base], "nightly_high": PRICE[base], "currency": "USD", "nonresident": NR,
            "reservation_fee": 10, "surcharges": sur, "checked": "2026", "note": text},
            "source": f"{SCHEDULE} ('2020 Montana State Parks Schedule': campsite fees by season and residency, "
                      f"reservation fee) + {JUSTIFY} (the same figures as 'CURRENT') + montanastateparks.reserveamerica.com "
                      f"parkId {pid} (site types and lengths, mt_sites_2026-10-12.json), read {D}"})
FCFS = {6090: ("Ackley Lake has 26 first-come first-served, rustic (no electricity, water or dump services) campsites' "
               "(its page); FWP's 2024 notice charged them the standard rate.",
               "https://www.lewistownnews.com/camping-fees-apply-at-ackley-lake-state-park/"
               "article_e3ed2c30-f825-11ee-a5b0-a35ccd876167.html (FWP's notice, 2024-04-10: peak season MT Resident "
               "$18/night, Non-Resident $28/night; off season $14 / $24) + https://fwp.mt.gov/stateparks/ackley-lake"),
        6091: ("8 campsites, first come, first served (its page).", "https://fwp.mt.gov/stateparks/medicine-rocks"),
        6093: ("25 campsites, first come, first served; RV/trailer length limited to 23 feet (its page).",
               "https://fwp.mt.gov/stateparks/lost-creek")}
for eid, (what, src) in FCFS.items():
    e = rows[eid]
    if e.get("fees"):
        continue
    text = ((what[:1].upper() + what[1:] if eid != 6090 else "'" + what) + " " + money_text(["standard"], "standard") +
            " Montana accommodation tax included." + PROPOSAL +
            f" FWP's fee schedule (in force since 2020; FWP lists rustic campsites only at Thompson Chain of Lakes and "
            f"Makoshika), read {D}.")
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": 18, "nightly_high": 18, "currency": "USD", "nonresident": NR, "surcharges": {"weekend": 0},
        "checked": "2026", "note": text},
        "source": f"{SCHEDULE} + {JUSTIFY} + {FEES} (rustic campsites only at Thompson Chain of Lakes and Makoshika) + "
                  f"{src}, read {D}"})
out.append({"id": 6217, "name": rows[6217]["name"], "fees": {
    "nightly_low": 12, "nightly_high": 18, "currency": "USD", "checked": "2026",
    "note": "Camping fee: $12/night with a Montana fishing license, $18 without; MT residents 62+, disabled or veterans "
            "$5 / $7.50."},
    "source": "https://fwp.mt.gov/binaries/content/assets/fwp/fish/fas/2026-fas-fee-table_adopted.pdf (2026 FAS use fee "
              "table: camping $12.00/night Montana fishing license holders, $18.00 non-Montana license holders; "
              "$5.00/$7.50 for MT residents 62+, disabled or veterans); fee site per "
              "https://myfwp.mt.gov/fishMT/fas/39753534 ('Facilities & Fees': FAS Camping With Valid Fishing License 12.0, "
              f"Without Valid Fishing License 18.0), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "MT findings;", len(flags), "flagged; tent-only loops:", sorted(tent_only))
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:50], f["nightly_low"], f["nightly_high"], f.get("surcharges"), f.get("reservation_fee"))
for fl in flags:
    print("FLAG", *fl)
