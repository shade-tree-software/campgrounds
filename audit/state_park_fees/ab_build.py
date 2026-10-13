"""Alberta Parks findings: each campground's page on albertaparks.ca, read 2026-10-12 (ab_campground_pages_2026-10-12.json).

    python3 -I ab_build.py OUT

Each campground page has a 'Camping' table: site type, campsites, power (amps), '$/Night', reservable dates ('-' where
the sites are first come, first served) and the season, plus an 'Updated:' date; the Kananaskis and Bow Valley pages add
'A Kananaskis Conservation Pass is required to park your vehicle in Kananaskis and the Bow Valley'. The fee guidelines
(albertaparks.ca/.../camping-in-alberta-parks/fee-guidelines/): 'Each campground's fees are based on market demand and
the services available at that site (within the approved range)', 'Fees are inclusive of the federal Goods and Services
Tax (GST)', basic campsites '$8 - $31/night' plus '$8/night' each for water, electric and sewer hook-ups, 'Non-refundable
$12 reservation fee per reservation' (on the provincial:AB registry row), and the Conservation Pass 'Day pass - $15
(registers one vehicle)'. Campgrounds run by the Friends of the Eastern Slopes Association list 'FOESA Membership' as
the rate: 'A nightly fee is not charged; however, campers are encouraged to purchase an annual membership'.

Each entry: base = the cheapest of unserviced, power, power/water and power/water/sewer sites (walk-in tenting,
equestrian and seasonal sites left out); add-ons over it ('electric' = the cheaper power site, 'water' = power/water over
power alone, 'full_hookup' = power/water/sewer); weekend 0 (one price a night); reservation fee 0 where no site is
reservable; the Conservation Pass as the entrance where the page requires it. Mount Kidd RV Park, a concessionaire's
park in Kananaskis Country with its own booking site, is priced from its rates page."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
GUIDE = "https://www.albertaparks.ca/albertaparks-ca/visit-our-parks/camping-in-alberta-parks/fee-guidelines/"
KCP = {"resident": 15, "nonresident": 15, "per": "vehicle_day", "name": "Kananaskis Conservation Pass"}
KIND = {"Unserviced": "ne", "Power": "e", "Power (Premium)": "e", "Power/Water": "ew", "Power/Water/Sewer": "fhu"}
WORD = {"ne": "unserviced", "e": "power", "ew": "power and water", "fhu": "power, water and sewer"}
pages = json.load(open(os.path.join(HERE, "ab_campground_pages_2026-10-12.json"), encoding="utf-8"))


def price(v):
    if v == "FOESA Membership":
        return 0
    m = re.fullmatch(r"\$(\d+(?:\.\d\d)?)", v or "")
    return float(m.group(1)) if m else None


def num(v):
    return int(v) if float(v).is_integer() else v


def amps(p):
    a = [x for x in re.split(r"\s*/\s*", p or "") if x.isdigit()]
    return "/".join(a) + "-amp" if a else ""


out, flags = [], []
for k, rec in sorted(pages.items(), key=lambda kv: int(kv[0])):
    eid = int(k)
    e = rows[eid]
    if e.get("fees") or not rec["pages"]:
        if not rec["pages"] and eid != 12809:
            flags.append((eid, e["name"], "no campground page"))
        continue
    got, parts, reservable, seasons, dates, kcp, foesa = {}, {}, False, [], [], False, False
    for pg in rec["pages"]:
        kcp |= pg["kcp"]
        if pg.get("season"):
            seasons.append(pg["season"])
        if pg.get("updated"):
            dates.append(pg["updated"])
        for c in pg["rows"]:
            k2 = KIND.get(c.get("Site Type"))
            v = price(c.get("$/Night"))
            if k2 is None or v is None:
                continue
            foesa |= c.get("$/Night") == "FOESA Membership"
            got.setdefault(k2, []).append(v)
            reservable |= (c.get("Reservations") or "-") != "-"
            label = (f"{WORD[k2]}{' (' + amps(c.get('Power')) + ')' if amps(c.get('Power')) else ''} "
                     f"{'free' if v == 0 else '$' + str(num(v))}")
            parts[label] = parts.get(label, 0) + (int(c["Campsites"]) if c.get("Campsites", "").isdigit() else 0)
    if not got:
        flags.append((eid, e["name"], "no priced RV site"))
        continue
    base_k = next(x for x in ("ne", "e", "ew", "fhu") if x in got)
    base, hi = min(got[base_k]), max(got[base_k])
    sur = {}
    if base_k == "ne" and (got.get("e") or got.get("ew")):
        sur["electric"] = num(min(got.get("e", []) + got.get("ew", [])) - base)
    if got.get("e") and got.get("ew") and min(got["ew"]) > min(got["e"]):
        sur["water"] = num(min(got["ew"]) - min(got["e"]))
    if "fhu" in got and base_k != "fhu":
        sur["full_hookup"] = num(min(got["fhu"]) - base)
    sur["weekend"] = 0
    fees = {"nightly_low": num(base), "nightly_high": num(hi), "currency": "CAD", "surcharges": sur, "checked": "2026"}
    if not reservable:
        fees["reservation_fee"] = 0
    if kcp:
        fees["entrance"] = KCP
    season = "; ".join(dict.fromkeys(seasons))
    text = ("No nightly fee: the Friends of the Eastern Slopes Association runs it and asks campers to buy an annual "
            "membership. " if foesa else "") + \
        ("A night: " + "; ".join(f"{lab} ({n} sites)" if n else lab for lab, n in parts.items()) + ". "
         if not foesa else "") + \
        (f"Season {season}. " if season and season != "Year-round" else "Open year-round. " if season else "") + \
        ("Reservable in season." if reservable else "First come, first served.") + \
        (" A Kananaskis Conservation Pass ($15 a vehicle a day) is required to park." if kcp else "") + \
        (" GST included." if not foesa else "") + \
        f" The campground's Alberta Parks page (updated {', '.join(dict.fromkeys(dates)) or 'undated'}), read {D}."
    fees["note"] = text
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": " + ".join(pg["url"] for pg in rec["pages"]) + " (the 'Camping' table" +
                          (", the Conservation Pass line" if kcp else "") + f") + {GUIDE} (GST included, $12 reservation "
                          f"fee" + (", $15 day pass" if kcp else "") + f"), read {D}"})
# Mount Kidd RV Park: the concessionaire's own rates page (taxes and its $14 reservation fee extra).
out.append({"id": 12809, "name": rows[12809]["name"], "fees": {
    "nightly_low": 40.29, "nightly_high": 40.29, "currency": "CAD", "reservation_fee": 14, "entrance": KCP,
    "surcharges": {"electric": 10.57, "water": 5.33, "full_hookup": 19.23, "weekend": 0}, "checked": "2026",
    "note": ("No services $40.29 a night (Loop F), power only $50.86, power and water $56.19, full service $59.52 (summer "
             "loops A, B and E 1-11; power only in spring, autumn and winter), before tax; plus its $14 reservation fee "
             "per campsite. Rates last verified 2026-08-05 on the park's rates page. Alberta requires a Kananaskis "
             "Conservation Pass ($15 a vehicle a day) to park in Kananaskis Country. Read 2026-10-12.")},
    "source": "https://www.mountkiddrv.com/rates-fees ('Rates last verified 2026-08-05': rates by service class and loop, "
              f"'$14.00 per campsite' reservation fee) + https://www.alberta.ca/kananaskis-conservation-pass, read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "AB findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f["nightly_high"], f["surcharges"], f.get("reservation_fee"),
          "KCP" if f.get("entrance") else "")
for fl in flags:
    print("FLAG", *fl)
