"""Re-check of the 25 Campspot prices landed 2026-10-10 (AWH 2026-10-13: "Check the 25 campspot entries again").

    python3 -I campspot_recheck_build.py [OUT.json]          # prints each park's verdict
    python3 -I ../state_park_fees/replace_fees.py OUT.json [--apply]

campspot_prices.py (2026-10-10) priced each park from the availability API's averagePricePerNight. That figure is the
Site Total less tax, so it folds in the park's own 'Campground Fees' and Campspot's 'Booking Fee' (3%, at least $3)
wherever a park charges them. This re-check reads each RV type's price breakdown instead (campspot_batch.py: one night
from a Tuesday and from a Saturday - 2026-11-10/14, 2027-06-15/19 where June is open, late October 2026 for parks
already closed in November, January 2027 for the Florida resorts), a 2-night quote wherever the park adds a flat fee,
and hand reads of the parks that sell only through the Campspot marketplace (no /book/ engine). All of it is in
campspot_recheck_2026-10-13.jsonl, in campspot_site.py's line format.

A date pair on which every RV type is closed for the season (RESORT_CLOSED_RULE) is set aside whenever the park has an
open pair: a closed date still shows a price, but Myron's November $35 is not what June charges ($30). A park's own
'Campground Fees' line is recorded the way it is charged, which SPEC states and the 2-night quote proves: a flat amount
once per stay -> reservation_fee; every night -> added to the nightly price; a share of the site charge -> the note
only, as Campspot's booking fee is. The types each 2026-10-10 range left out (group, horse, tent-only, double sites)
stay out. A finding is written only where the nightly range or the per-stay fee differs from the entry."""
import collections, datetime, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
D = "2026-10-13"
DATA = os.path.join(HERE, "campspot_recheck_2026-10-13.jsonl")
SKIP = r"(?i)\bgroup\b|horse|equestrian|\brally\b|\btent\b(?!.*\brv\b)|cabin|lodge|bunkhouse|double site|buddy|private site"

# Per park, how its 'Campground Fees' line is made up - each part proven by the 2-night quote: stay = a flat amount
# once per stay (-> reservation_fee); night = a flat amount every night (added to the nightly price; a dict keyed by
# date prefix when it is seasonal); pct = a share of the site charge (note only); types = the site types that carry
# it, when not all do; fee_text = a sentence instead, for a fee no simple rule reproduces (no check).
# skip = more type names left out; also = [(rate, phrase)] published rates no Campspot date reaches, added to the
# range, with also_text; extra = one more sentence; source = a page added to the provenance; market = marketplace.
SPEC = {
    3450: {"stay": 4, "types": r"(?i)^standard", "types_text": "standard sites only; the premium ones carry none"},
    3471: {"stay": 3.5, "pct": 0.03},
    14515: {"stay": 5},
    14563: {"stay": 3.5},
    14566: {"pct": 0.03},
    14571: {"fee_text": "The park adds a campground fee that grows with the bill ($1.88-2.24 for one night, $3.32 for "
                        "two). Its own page still says $45 a night (10% off Monday-Thursday), $265 a week and $629 a "
                        "month."},
    14644: {"stay": 5, "night": 2},
    14666: {"stay": 3.5},
    14871: {"stay": 3, "also": [(83.35, "summer")],
            "also_text": "The resort's rate card charges the November prices in November and April, the January "
                         "ones December through March, and $83.35 a night for every site May to October.",
            "source": "https://www.gulfwatersrvresortfl.com/services-1 (rate card: 'Summer' May 1 - October 31, "
                      "'Shoulder' November and April, 'Peak' December - March; tax not included)"},
    14881: {"night": {"2026-11": 10},
            "night_text": "November's prices include the park's $10-a-night campground fee; January and June have none."},
    15176: {"stay": 5},
    # marketplace-only parks (campspot_market.py)
    3010: {"market": True, "stay": 2},
    4941: {"market": True, "stay": 10, "skip": r"(?i)with trailer"},
    7839: {"market": True, "stay": 5},
    13358: {"market": True, "stay": 5, "skip": r"(?i)^seasonal",
            "extra": "The county's own fee page: $35 a day or $200 a week for a transient site; the 2026 season ran "
                     "May 1 to October 12.",
            "source": "https://onoville.com/season-fees ('Daily $35.00 Day', 'Weekly $200.00 Week') and "
                      "https://onoville.com/docks-campsites (2026 season May 1 - October 12)"},
    13398: {"market": True, "stay": 5, "pct": 0.05},
    13409: {"market": True, "stay": 5, "pct": 0.03,
            "extra": "Longer stays cost less a night: the city's 2026 rate table has one night at $60 without sewer "
                     "or $70 with it, 2 nights $110 / $130, 3 nights $155 / $195 and a week $330 / $400, and a "
                     "2-night quote here took $10 off.",
            "source": "https://www.colonail.com/scottpark (RV short-term camping rates, 2026 Rules & Regulations "
                      "v1.7)"},
    13433: {"market": True, "stay": 10},
    13450: {"market": True, "pct": 0.03},
    14212: {"market": True, "stay": 5, "skip": r"(?i)rustic",
            "extra": "Rustic tent sites that take an RV, with no hookups, are $25 in October and November and $35 "
                     "in June; they are left out of the range."},
    14217: {"market": True, "pct": 0.03},
}


def num(v):
    return int(v) if float(v).is_integer() else round(v, 2)


def cash(v, cur="USD"):
    s = f"${num(v)}" if float(v).is_integer() else f"${v:.2f}"
    return ("C" + s) if cur == "CAD" else s


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def parse_lines(lines):
    """campspot_site.py lines -> [(type name, site rate per night, nights, {fee line: amount})]."""
    out = []
    for x in lines:
        m = re.match(r"^\d+ (.*?): (?:[A-Z]{1,3})?\$([\d,.]+) x (\d+) nights? \| (?:[A-Z]{1,3})?\$[\d,.]+ \| (.*)$", x)
        if m:
            parts = m.group(4).split(" | ")
            extras = {parts[i]: float(re.sub(r"^(-?)[A-Z]*\$", r"\1", parts[i + 1]).replace(",", ""))
                      for i in range(0, len(parts) - 1, 2)}
            out.append((m.group(1), float(m.group(2).replace(",", "")), int(m.group(3)), extras))
    return out


def closed(r):
    """The park is closed for the season on the record's dates."""
    if r.get("market"):
        return bool(r.get("closed"))
    rv = r.get("rv") or []      # no site free, and the park says closed (a lone booked-out site can say UNAVAILABLE)
    return (bool(rv) and all(not t["free"] for t in rv)
            and any(any("RESORT_CLOSED_RULE" in x for x in t["failure"]) for t in rv))


def load():
    """-> {id: {(d1, d2): record}} for one-night quotes, {id: [parsed lines]} for multi-night quotes."""
    recs, two = collections.defaultdict(dict), collections.defaultdict(list)
    for line in open(DATA, encoding="utf-8"):
        r = json.loads(line)
        if "two_night" in r:
            two[r["id"]] += [x + (r["dates"][0],) for x in parse_lines(r["two_night"])]
        elif any(parse_lines(v) for v in (r.get("breakdown") or {}).values()):
            recs[r["id"]][tuple(r["dates"])] = r          # the last record for those dates wins
    return recs, two


def joined(names):
    names = sorted(f"'{n}'" if "," in n else n for n in names)      # Onoville's "Transient, East Campsite"
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def per_night(spec, d):
    n = spec.get("night", 0)
    return next((v for k, v in n.items() if d.startswith(k)), 0) if isinstance(n, dict) else n


def carries(spec, name):
    return not spec.get("types") or bool(re.search(spec["types"], name))


def fee_check(eid, spec, lines):
    """Every quote's 'Campground Fees' must be what SPEC says the park charges."""
    for name, rate, nights, extras, d in lines:
        want = 0
        if carries(spec, name):                  # a share is of the site charge after any discount line
            charge = rate * nights + sum(v for v in extras.values() if v < 0)
            want = spec.get("stay", 0) + per_night(spec, d) * nights + spec.get("pct", 0) * charge
        got = extras.get("Campground Fees", 0.0)
        assert abs(got - round(want, 2)) < 0.015, (eid, name, d, nights, got, round(want, 2))


def verdicts(entries, strict=True):
    recs, two = load()
    out, report = [], []
    for eid, e in entries.items():
        spec = SPEC.get(eid, {})
        cur = (e.get("fees") or {}).get("currency", "USD")
        pairs = sorted(recs.get(eid, {}))
        open_pairs = [p for p in pairs if not closed(recs[eid][p])]
        shut = not open_pairs and bool(pairs)
        pairs = open_pairs or pairs[:1]               # closed everywhere: the date nearest the season is enough
        rates = collections.defaultdict(dict)          # type -> {date: site rate, net of any discount line}
        lines, booking, discounts, discount_months = [], False, collections.Counter(), set()
        for pair in pairs:
            for d in pair:
                for name, rate, nights, extras in parse_lines(recs[eid][pair]["breakdown"].get(d, [])):
                    if re.search(SKIP, name) or (spec.get("skip") and re.search(spec["skip"], name)):
                        continue
                    off = {k: -v for k, v in extras.items() if v < 0}
                    for k, v in off.items():
                        discounts[(k, num(round(100 * v / (rate * nights))))] += 1
                        discount_months.add(f"{datetime.date.fromisoformat(d):%B %Y}")
                    name = re.sub(r"\s*\*\*.*?\*\*", "", name)
                    add = per_night(spec, d) if carries(spec, name) else 0
                    rates[name][d] = round(rate - sum(off.values()) / nights + add, 2)
                    lines.append((name, rate, nights, extras, d))
                    booking |= "Booking Fee" in extras
        if not rates:
            report.append((eid, "NO DATA"))
            continue
        if any(spec.get(k) for k in ("stay", "night", "pct")):
            if spec.get("stay") or spec.get("night"):
                assert any(x[2] >= 2 for x in two[eid]), (eid, "no 2-night quote")
            fee_check(eid, spec, lines + [x for x in two[eid] if not re.search(SKIP, x[0])])
        elif any(x[3].get("Campground Fees") for x in lines) and not spec.get("fee_text"):
            if strict:
                raise SystemExit(f"{eid}: a 'Campground Fees' line with no SPEC to say how it is charged")
            report.append((eid, "NEEDS SPEC", sorted({(x[0][:30], x[3].get("Campground Fees"), x[4]) for x in lines})[:6]))
            continue
        allv = [v for by in rates.values() for v in by.values()] + [r for r, _ in spec.get("also", [])]
        new = {"nightly_low": num(min(allv)), "nightly_high": num(max(allv)), "currency": cur}
        if spec.get("stay"):
            new["reservation_fee"] = num(spec["stay"])
        old = e.get("fees") or {}
        same = all(old.get(k) == new.get(k) for k in ("nightly_low", "nightly_high", "reservation_fee"))

        def clause(pair):
            d1, d2 = pair
            groups = collections.defaultdict(list)
            for name, by in rates.items():
                if d1 in by or d2 in by:
                    groups[(by.get(d1), by.get(d2))].append(name)
            parts = []
            for (a, b), names in sorted(groups.items(), key=lambda kv: (kv[0][0] or kv[0][1], kv[0][1] or 0)):
                if a is not None and b is not None and a != b:
                    parts.append(f"{joined(names)} {cash(a, cur)} ({cash(b, cur)} on the Saturday)")
                elif a is None:
                    parts.append(f"{joined(names)} {cash(b, cur)} (Saturday only)")
                else:
                    parts.append(f"{joined(names)} {cash(a, cur)}")
            return "; ".join(parts)

        where = "The Campspot marketplace" if spec.get("market") else "Campspot"
        days = lambda p: [datetime.date.fromisoformat(d) for d in p]
        if len(pairs) == 1:
            t, s = days(pairs[0])
            text = (f"{where}, one night for 2 adults from a {t:%A} ({pairs[0][0]}) and from a {s:%A} ({pairs[0][1]}), "
                    f"site rate before tax: {clause(pairs[0])}.")
        else:                                         # months that charged the same are said once
            same_as = collections.defaultdict(list)
            for p in pairs:
                same_as[clause(p)].append(f"{days(p)[0]:%B %Y} ({ordinal(days(p)[0].day)} and {ordinal(days(p)[1].day)})")
            text = f"{where}, one night for 2 adults from a Tuesday and from a Saturday, site rate before tax - " + " ".join(
                f"{', '.join(when[:-1]) + ' and ' + when[-1] if len(when) > 1 else when[0]}: {c}."
                for c, when in same_as.items())
        if shut:
            text += " The park is closed for the season by then; Campspot still shows its rates."
        if not spec.get("market") and not any(p[0].startswith("2027-06") for p in pairs):
            text += " June 2027 isn't open for booking yet."
        if spec.get("also_text"):
            text += " " + spec["also_text"]
        stay, night, pct = spec.get("stay"), spec.get("night"), spec.get("pct")
        share = f"{num(round(pct * 100, 1))}% of the site charge" if pct else ""
        only = f" ({spec['types_text']})" if spec.get("types_text") else ""
        if spec.get("fee_text"):
            text += " " + spec["fee_text"]
        elif night and not isinstance(night, dict):
            text += (f" Those include the park's {cash(night, cur)}-a-night campground fee"
                     + (f", which also adds {cash(stay, cur)} once per stay" if stay else "") + f"{only}.")
        elif night:
            text += " " + spec["night_text"]
        elif stay and pct:
            text += f" Plus the park's campground fee: {cash(stay, cur)} once per stay and {share}{only}."
        elif stay:
            text += f" Plus the park's {cash(stay, cur)} campground fee, once per stay{only}."
        elif pct:
            text += f" The park adds {share} as a campground fee{only}."
        for (k, p), n in sorted(discounts.items()):
            months = sorted(discount_months, key=lambda m: datetime.datetime.strptime(m, "%B %Y"))
            whose = "Those" if len(months) == len(pairs) else f"The {' and '.join(months)} prices"
            text += f" {whose} are after the park's '{k}' discount ({p}% off)."
        if spec.get("extra"):
            text += " " + spec["extra"]
        if booking:
            text += " Campspot adds its own booking fee at checkout (3%, at least $3)."
        text += f" Read {D}."
        new.update(checked="2026", note=text)
        report.append((eid, "confirmed" if same else "CHANGED",
                       {k: old.get(k) for k in ("nightly_low", "nightly_high", "reservation_fee")},
                       {k: new.get(k) for k in ("nightly_low", "nightly_high", "reservation_fee")},
                       "closed season only" if shut else "", "booking fee" if booking else ""))
        if not same:
            slug = recs[eid][pairs[0]]["slug"]
            url = f"https://www.campspot.com/{'park' if spec.get('market') else 'book'}/{slug}"
            dates = ", ".join(d for p in pairs for d in p)
            out.append({"id": eid, "fees": new,
                        "source": f"{url} (each RV site type's price breakdown for one night from {dates}, 2 adults"
                                  + ("; a 2-night quote for the campground fee" if spec.get("stay") or spec.get("night") else "")
                                  + f"; campspot_recheck_2026-10-13.jsonl)"
                                  + (f" + {spec['source']}" if spec.get("source") else "") + f", read {D}"})
    return out, report


if __name__ == "__main__":
    F = json.load(open(os.path.join(HERE, "campspot_findings.json"), encoding="utf-8"))
    by = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
    out, report = verdicts({f["id"]: by[f["id"]] for f in F}, strict=len(sys.argv) > 1)
    for x in report:
        print(*x)
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print(len(out), "findings written")
