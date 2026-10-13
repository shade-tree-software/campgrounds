"""Nightly prices for the entries that had only RV Life's $ tier and link to Campspot (AWH 2026-10-13: "do the 421
entries that link to Campspot").

    python3 -I campspot_tier_build.py --ids 1,2,3 [--out FINDINGS.json] [--fields FIELDS.json]
    python3 -I apply.py FINDINGS.json [--apply]

Reads campspot_tier_2026-10-13.jsonl, written by ../private_gap_browser/campspot_api.py: per park, Campspot's own
pricing for the RV site types a 23-ft rig fits that set the range (the cheapest, any within 10% of it, and the
dearest), one night from a Tuesday and from a Saturday in October 2026, January 2027 and June 2027 (and any --extra
dates), and two nights from the first date on which the park adds a fee of its own. The first records were written by
a fuller first version of the reader, which also read November 2026 and priced every RV type.

The stored range is the site rate before tax: the site charge after any automatic discount, plus any fee the park
charges every night. The park's other fees are worked out from the quotes themselves rather than from a hand-written
model (the 2026-10-13 re-check of 25 parks needed one per park; 421 can't): each fee is fitted, to the cent and across
every quote, as a flat amount once per stay, a flat amount per night, a share of the site charge, or a flat amount
plus one of the others, simplest first. A flat per-stay fee every RV type carries goes in reservation_fee; a share of
the bill, or a fee only some types carry, is said in the note. A fee no rule reproduces, or one two rules reproduce
in different ways (on $40 nights alone, 4% of the site charge and $1.60 a night are the same quotes), is reported,
not landed: OVERRIDE says what it is, as campspot_recheck_build.py's SPEC did.

Dates on which every RV type is closed for the season (RESORT_CLOSED_RULE) are set aside whenever another date is
open - a closed date still shows a price, and not always the season's (Myron WI, 2026-10-13). A type that lists no
campsites and never offers one is left out of that test (see verdict()). A Tuesday on which every
RV type asks for more than one night is flagged; ../private_gap_browser/campspot_dates.py on more dates tells a standing
minimum (booking.min_stay, written by hand; .claude/memory/feedback_minimum_stay.md) from a run of dates (OVERRIDE's
"mins_text").
--fields writes the groups the same reads settle (booking and hookups; see fields()), in
clean_notes.py's "set"/"provenance" shape."""
import collections, datetime, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
D = "2026-10-13"
WINTER = "2027-01-26"       # the January Tuesday campspot_api.py reads; its closure is the coming winter's
LAST_WINTER = "2026-01-26"  # and the same day a year before, whose closure ended this year's opening
LATE_WINTER = "2026-02-15"  # or a closure begun in February (BrightSky KY, new on Campspot from 2026-02-01)
NEXT_WINTER = "2028-01-26"  # the winter after the coming one, set by a few parks already
PREV_WINTER = "2025-01-26"  # the winter before last, for a park that hasn't set the coming winter yet
DATA = os.path.join(HERE, "campspot_tier_2026-10-13.jsonl")
# site types that are not a nightly RV site, by name; the reader (campspot_api.py) carries the same list - keep the
# two in step, or the reader leaves unpriced a type the builder counts
SKIP = (r"(?i)\bgroup\b|horse|equestrian|\brally\b|^(?!.*\b(rv|camper|trailer)\b).*\btent\b|cabin|lodge|bunkhouse|"
        r"double site|buddy|pavilion|day use|day pass|^(?!.*\b(rv|camper|trailer)\b).*\b(boat slip|dock|slip)\b|"
        r"storage|glamp|yurt|tipi|teepee|cottage|motel|\broom\b|accessible|\bada\b|handicap|"
        # a long-stay product, unless the name also sells it by the night ('50 Amp Daily, Weekly RV Site', Sullivan
        # County IN)
        r"^(?!.*\b(daily|nightly|night|overnight|transient)\b).*(season|monthly|long[- ]term|\bweekly\b|annual|"
        r"yearly|winter stay)")
# per park, by hand: "fee_text" for a fee the fit can't settle, "fee_model" {name: [model, params]} for one that a
# further quote settled, "skip" a regex of type names to leave out, "mins_text" to replace the minimum-stay sentence
# (empty when booking.min_stay carries it)
OVERRIDE = {
    # $35 a night on every type and date, so a share of the charge and a flat sum per night give the same cents; the
    # name says card processing, which parks charge as a share
    1331: {"fee_text": "The park adds 3% of the site charge as a 'Processing Fee' ($1.05 on a $35 night), on every "
                       "type but Equine North 30 Amp."},
    1342: {"fee_text": "The park adds 4% of the site charge as a 'Credit Card Processing Fee' and 2% as a 'Lake "
                       "Maintenance Fee' ($1.60 and $0.80 on a $40 night)."},
    # the 2-night minimum of May-September is marked in booking.min_stay, so the note needn't repeat it
    970: {"mins_text": ""},
    # a run of autumn dates, not a standing minimum (campspot_dates.py on four more dates)
    1165: {"mins_text": "Campspot asked for at least 2 nights on every RV type for check-in on October 20, 21 and 27 "
                        "and November 3, 2026, but sold single nights on October 17 and November 10 and 14."},
    # one quote only (the season is over); campspot_dates.py for two nights from 2026-10-20 averaged $53.50, which
    # is ($49 x 2 + $9) / 2
    1518: {"fee_model": {"Booking Fee": ["stay", {"A": 9.0}]}},
    # one fee per type, each 4% of its rate: $1.16 on $29 and $1.72 on $43 quoted, and the list's prices for the
    # other types ($35, $37) carry 4% as well
    1732: {"fee_text": "The park adds 4% of the site charge as a 'Transaction Fee' ($1.16 on a $29 night)."},
    # $30 on every type and date, so a share and a flat sum per night give the same cents; the name says card
    # processing, which parks charge as a share
    1748: {"fee_text": "The park adds 3.2% of the site charge as a 'Processing Fee' ($0.96 on a $30 night)."},
    # batch 3. One price everywhere ($44, $35), and the name says card processing:
    3226: {"fee_text": "The park adds 4% of the site charge as a 'Processing Fee' ($1.76 on a $44 night)."},
    3581: {"fee_text": "The park adds 3% of the site charge as a 'Processing Fee' ($1.05 on a $35 night)."},
    # two nights tell them apart to the cent: 3.5% of $90 is $3.15 and of $86 is $3.01, where a flat sum a night would
    # double the one-night $1.58 and $1.50
    3383: {"fee_model": {"Credit Card Transaction Fee": ["pct", {"P": 0.035}]}},
    3568: {"fee_model": {"Credit Card Surcharge": ["pct", {"P": 0.035}]}},
    # the City of Ashland's other park, Kreher, charges the same-named fee as 3% on types of different prices
    3454: {"fee_model": {"Convenience Fee": ["pct", {"P": 0.03}]}},
    # the name gives the share
    3505: {"fee_model": {"Credit Card Surcharge - 3.5%": ["pct", {"P": 0.035}]}},
    3506: {"fee_model": {"Credit card surcharge 3.5%": ["pct", {"P": 0.035}]}},
    # advance reservations need 2 nights all season, marked in booking.min_stay
    3585: {"mins_text": ""},
}


def num(v):
    return int(v) if float(v).is_integer() else round(v, 2)


def cash(v, cur="USD"):
    s = f"${num(v)}" if float(v).is_integer() else f"${v:.2f}"
    return ("C" + s) if cur == "CAD" else s


def span(vals, cur):
    lo, hi = min(vals), max(vals)
    return cash(lo, cur) if lo == hi else f"{cash(lo, cur)}-{cash(hi, cur).lstrip('C$')}"


def load(ids=None):
    recs = {}
    for line in open(DATA, encoding="utf-8"):
        r = json.loads(line)
        if ids is None or r["id"] in ids:
            recs[r["id"]] = r                 # the last read of a park wins
    return recs


def countable(t, extra_skip=None):
    """An RV site type a 23-ft rig fits: most of its sites take 23 ft or give no length."""
    name = t.get("name") or ""
    if t.get("code") != "rv" or re.search(SKIP, name) or (extra_skip and re.search(extra_skip, name)):
        return False
    return not t.get("max_len") or t["fit_sites"] * 2 >= max(t["sites"], 1)


def nm_(name):
    return " ".join((name or "").split()).rstrip(" #")


def and_list(xs):
    """'A, B and C'; 'A; B; and C' when a name holds a comma itself ('30/50 AMP, Riverfront, Water, Electric')."""
    xs = list(xs)
    if len(xs) == 1:
        return xs[0]
    if any("," in x for x in xs):
        return "; ".join(xs[:-1]) + "; and " + xs[-1]
    return ", ".join(xs[:-1]) + " and " + xs[-1]


def charge(q):
    """The site charge for the stay after any discount, before fees and tax."""
    return round(q["net_avg"] * q["nights"], 2)


def fit_fee(points):
    """points = [(nights, charge, amount)] -> [(model, params), ...] for every rule that gives each amount to the
    cent, simplest first (empty if none). Models: stay A; night B; pct P; stay+night A + B*n; stay+pct A + P*c."""
    ok = lambda f: all(abs(a - round(f(n, c), 2)) < 0.011 for n, c, a in points)
    fits = []
    a0 = points[0][2]
    if ok(lambda n, c: a0):
        fits.append(("stay", {"A": a0}))
    b = points[0][2] / points[0][0]
    if ok(lambda n, c: b * n):
        fits.append(("night", {"B": round(b, 2)}))
    big = max(points, key=lambda p: p[1])
    if big[1]:
        p = round(big[2] / big[1], 4)
        if ok(lambda n, c: p * c):
            fits.append(("pct", {"P": p}))
    # a two-part rule only where neither of its parts fits alone: the cent of slack ok() allows would otherwise fit a
    # plain 3.75% as 1 cent per stay + 3.73% (Stony Mountain PA)
    simple = {m for m, _ in fits}
    ones = [x for x in points if x[0] == 1]
    twos = [x for x in points if x[0] == 2]
    if ones and twos and not simple & {"stay", "night"}:
        bb = round(twos[0][2] - ones[0][2], 2)
        aa = round(ones[0][2] - bb, 2)
        if bb > 0 and aa > 0 and ok(lambda n, c: aa + bb * n):
            fits.append(("stay+night", {"A": aa, "B": bb}))
    cs = sorted({(c, a) for n, c, a in points})
    if len(cs) >= 2 and cs[-1][0] != cs[0][0] and not simple & {"stay", "pct"}:
        p = (cs[-1][1] - cs[0][1]) / (cs[-1][0] - cs[0][0])
        for pr in sorted({round(p, 4), round(p * 400) / 400, round(p, 3)}):
            aa = round(cs[0][1] - pr * cs[0][0], 2)
            if aa > 0 and pr > 0 and ok(lambda n, c: aa + pr * c):
                fits.append(("stay+pct", {"A": aa, "P": pr}))
                break
    return fits


# how each rule is recorded: once per stay -> reservation_fee, per night -> in the nightly price, a share -> the note
TREAT = {"stay": "stay", "night": "night", "pct": "pct", "stay+night": "stay+night", "stay+pct": "stay+pct"}


def pct_text(p):
    return f"{num(round(p * 100, 2))}%"


def verdict(e, r):
    """-> (finding or None, report dict)."""
    rep = {"id": e["id"], "name": e["name"], "state": e.get("state")}
    if r.get("error"):
        rep["flag"] = ["ERROR " + json.dumps(r["error"])[:120]]
        return None, rep
    ov = OVERRIDE.get(e["id"], {})
    cur = "CAD" if (r.get("currency") or "").upper() == "CAD" else "USD"
    types = r.get("types") or {}
    use = {tid for tid, t in types.items() if countable(t, ov.get("skip"))}
    left_short = sorted({nm_(t["name"]) for tid, t in types.items() if t.get("code") == "rv" and tid not in use
                         and t.get("max_len") and t["fit_sites"] * 2 < max(t["sites"], 1)
                         and not re.search(SKIP, t.get("name") or "")})
    # A type that listed no campsites when first read and offered none on any date (Fairgrounds RV Park WI's "50 Amp
    # Grass Special Event Site", Fire Lake OH's "30/50 Amp/ Sewer/ Back In") answers "no campsites available" on the
    # dates every other type answers "closed": it has no site for the closure to name. Counted, it kept those dates
    # open and put their prices in the note, so it is left out of the closed-date and minimum tests. Its price stays:
    # "no sites listed" is not "no sites" (Scottville MI's types list none on a closed date and sell 48 in June).
    raw_lists = {d: rows for d, rows in (r.get("lists") or {}).items() if isinstance(rows, list)}
    ghost = {tid for tid in use if not types[tid].get("sites")
             and not any(x[0] == tid and x[2] for rows in raw_lists.values() for x in rows)
             and not any(q["type"] == tid and q.get("availability") == "AVAILABLE" for q in r.get("quotes") or [])}
    real = lambda rows: [x for x in rows if x[0] not in ghost] or rows
    qs = [q for q in r.get("quotes") or [] if q["type"] in use and not q.get("error") and q.get("net_avg") is not None]
    flags = []
    if not qs:
        rep["flag"] = ["NO QUOTES (%d types, %d rv)" % (len(types), sum(t.get("code") == "rv" for t in types.values()))]
        return None, rep
    one = [q for q in qs if q["nights"] == 1]
    dates = sorted({q["date"] for q in one})
    lists = {d: [x for x in rows if x[0] in use] for d, rows in (r.get("lists") or {}).items() if isinstance(rows, list)}

    def rows_of(d):           # every fitting type the park listed that day, quoted or not
        return lists.get(d) or [[q["type"], None, 0, q["fail"]] for q in one if q["date"] == d]
    shut_d = {d for d in dates if all(any("RESORT_CLOSED_RULE" in f for f in x[3]) for x in real(rows_of(d)))}
    used = [d for d in dates if d not in shut_d] or dates
    shut = not [d for d in dates if d not in shut_d]
    if shut:
        flags.append("CLOSED DATES ONLY")
    if r.get("fallback"):
        flags.append("FALLBACK DATES")
    # the park's own fees
    names = sorted({f[0] for q in qs for f in q["fees"]})
    fees = {}
    for nm in names:
        pts = [(q["nights"], charge(q), sum(f[2] for f in q["fees"] if f[0] == nm), q) for q in qs
               if any(f[0] == nm for f in q["fees"])]
        carriers = {q["type"] for *_, q in pts}
        lacking = {q["type"] for q in qs if not any(f[0] == nm for f in q["fees"])}
        fee_dates = {q["date"] for *_, q in pts}
        fits = fit_fee([p[:3] for p in pts])
        model = fits[0] if fits else None
        # two rules that both fit but are recorded differently (no two-night quote, or one price everywhere) can't
        # be told apart from these quotes
        ambiguous = len({TREAT[m] for m, _ in fits}) > 1
        if nm in ov.get("fee_model", {}):
            model, ambiguous = tuple(ov["fee_model"][nm]), False
        fees[nm] = {"model": model, "types": None if not (lacking - carriers) and not (lacking & carriers) else carriers,
                    "partial_dates": bool(lacking & carriers), "dates": fee_dates,
                    "amounts": sorted({p[2] for p in pts}), "ambiguous": [m for m, _ in fits] if ambiguous else None}
        if model is None or fees[nm]["partial_dates"] or ambiguous:
            if "fee_text" not in ov:
                why = "ambiguous %s" % fees[nm]["ambiguous"] if ambiguous and model else "irregular"
                flags.append(f"FEE '{nm}' {why} {fees[nm]['amounts'][:6]}")
            if ambiguous:              # no rule chosen: the override's text, or no finding
                fees[nm]["model"] = None
        elif fees[nm]["types"] is not None:
            flags.append(f"FEE '{nm}' on some types only")
    if any(f.startswith("FEE") and ("irregular" in f or "ambiguous" in f) for f in flags) and "fee_text" not in ov:
        rep["flag"] = flags
        rep["fees"] = {k: {"model": v["model"], "amounts": v["amounts"]} for k, v in fees.items()}
        return None, rep
    night_add = collections.defaultdict(float)          # type -> flat per-night fee included in the nightly price
    for nm, f in fees.items():
        if f["model"] and f["model"][0] in ("night", "stay+night"):
            for tid in (f["types"] or use):
                night_add[tid] += f["model"][1]["B"]
    price = {}                                           # (type, date) -> nightly site rate
    for q in one:
        if q["date"] in used:
            price[(q["type"], q["date"])] = round(q["net_avg"] + night_add[q["type"]], 2)
    vals = list(price.values())
    lo, hi = min(vals), max(vals)
    new = {"nightly_low": num(lo), "nightly_high": num(hi), "currency": cur}
    stay = [(nm, f["model"][1]["A"]) for nm, f in fees.items()
            if f["model"] and f["model"][0] in ("stay", "stay+night", "stay+pct") and f["types"] is None]
    if stay:
        new["reservation_fee"] = num(round(sum(a for _, a in stay), 2))
    # standing minimum: every RV type on an open Tuesday asks for more nights
    mins = collections.Counter()
    for d in used:
        if datetime.date.fromisoformat(d).weekday() >= 4:
            continue
        rd = real(rows_of(d))
        got = [re.search(r"(\d+) night minimum", " ".join(x[3])) for x in rd]
        if rd and all(got):
            mins[d] = max(int(m.group(1)) for m in got)
    weekdays = [d for d in used if datetime.date.fromisoformat(d).weekday() < 4]
    if mins and set(mins) == set(weekdays) and len({d[:7] for d in weekdays}) > 1:
        flags.append("STANDING MINIMUM %s" % dict(mins))
    elif mins:
        flags.append("WEEKDAY MINIMUM ON SOME DATES %s" % dict(mins))
    if hi > 3 * lo:
        flags.append("WIDE %s-%s" % (num(lo), num(hi)))
    if lo < 15 or hi > 150:
        flags.append("ODD %s-%s" % (num(lo), num(hi)))
    if cur == "CAD":
        flags.append("CAD")
    # the note
    avg_of = collections.defaultdict(list)
    for d in used:
        for tid, avg, *_ in rows_of(d):
            avg_of[tid].append(avg if avg is not None else price.get((tid, d), 1e9))
    tnames = list(dict.fromkeys(nm_(types[t]["name"]) for t in sorted(avg_of, key=lambda t: (min(avg_of[t]),
                                                                                             types[t]["name"]))))
    shown = tnames if len(tnames) <= 6 else tnames[:5] + [f"{len(tnames) - 5} more"]
    tlist = and_list(shown)
    by_month = collections.OrderedDict()
    for d in used:
        dd = datetime.date.fromisoformat(d)
        key = f"{dd:%B %Y}"
        by_month.setdefault(key, []).append((dd, [v for (t, x), v in price.items() if x == d]))
    parts = []
    for month, days in by_month.items():
        days = [(dd, v) for dd, v in sorted(days, key=lambda x: x[0].weekday()) if v]
        if len(days) > 1 and len({span(v, cur) for _, v in days}) == 1:
            parts.append((month, f"{span(days[0][1], cur)}, " + " and ".join(f"{dd:%A}" for dd, _ in days) + " alike"))
            continue
        bits = [f"{span(v, cur)} on a {dd:%A}" for dd, v in days]
        parts.append((month, "; ".join(bits) if len(bits) < 3 else ", ".join(bits)))
    merged = collections.OrderedDict()
    for month, text in parts:
        merged.setdefault(text, []).append(month)
    seasons = " ".join(f"{(', '.join(m[:-1]) + ' and ' + m[-1]) if len(m) > 1 else m[0]}: {t}."
                       for t, m in merged.items())
    where = "the Campspot marketplace" if "/park/" in (e.get("website") or "") + " " + str((e.get("booking") or {}).get("url")) else "Campspot"
    text = (f"Read on {where}: one night for 2 adults, site rate before tax, every RV site type a 23-ft rig fits "
            f"({tlist}). {seasons}")
    raw = {d: rows for d, rows in (r.get("lists") or {}).items() if isinstance(rows, list)}
    open_d = sorted(d for d, rows in raw.items() if rows)
    closed_d = {d for d, rows in lists.items()
                if rows and all(any("RESORT_CLOSED_RULE" in f for f in x[3]) for x in real(rows))}
    closed_d |= shut_d
    # nothing listed on a date earlier than one that lists sites: no sites sold then (not "not open yet")
    empty_d = {d for d, rows in raw.items() if not rows and open_d and d < open_d[-1]}
    used_m = {d[:7] for d in used}
    closed_m = sorted({d[:7] for d in closed_d} - used_m)
    empty_m = sorted({d[:7] for d in empty_d} - used_m - set(closed_m))
    if shut:
        text += " The park is closed for the season on those dates; Campspot still shows its rates."
    elif r.get("fallback"):
        text += " Later dates show no sites: the season has ended and next year's isn't open for booking yet."
    else:
        mname = lambda ms: and_list(f"{datetime.date.fromisoformat(m + '-01'):%B %Y}" for m in ms)
        if closed_m:
            text += f" Campspot shows the park closed in {mname(closed_m)}."
        if empty_m:
            text += f" Campspot offers no sites in {mname(empty_m)}."
        if not any(d.startswith("2027-06") for d in raw if raw[d]) and "2027-06" not in closed_m + empty_m:
            text += " June 2027 isn't open for booking yet."
    if left_short:
        text += f" Left out: {', '.join(left_short)} (sites under 23 ft)."
    inc, stays, pcts = [], [], []
    for nm, f in fees.items():
        label = ("campground fee" if nm.lower() in ("campground fee", "campground fees")
                 else f"'{nm}'" if re.search(r"(?i)\b(fee|fees|charge|surcharge|tax)$", nm) else f"'{nm}' fee")
        only = ""
        if f["types"] is not None:
            on = sorted({nm_(types[t]["name"]) for t in f["types"]})
            off = sorted({nm_(types[q["type"]]["name"]) for q in qs if q["type"] not in f["types"]} - set(on))
            only = (f" on every type but {and_list(off)}" if off and len(off) < len(on)
                    else f" on {and_list(on)} only")
        if ov.get("fee_text") and (f["model"] is None or f["partial_dates"]):
            continue
        m, prm = f["model"]
        if m == "stay":
            stays.append((f"{cash(prm['A'], cur)} {label}", only))
        elif m == "night":
            inc.append(f"Those include the park's {cash(prm['B'], cur)}-a-night {label}{only}.")
        elif m == "pct":
            pcts.append(f"The park adds {pct_text(prm['P'])} of the site charge as a {label}{only}.")
        elif m == "stay+night":
            inc.append(f"Those include the park's {cash(prm['B'], cur)}-a-night {label}, which also adds "
                       f"{cash(prm['A'], cur)} once per stay{only}.")
        elif m == "stay+pct":
            pcts.append(f"Plus the park's {label}: {cash(prm['A'], cur)} once per stay and {pct_text(prm['P'])} of "
                        f"the site charge{only}.")
    feebits = inc
    for only in dict.fromkeys(o for _, o in stays):
        these = [x for x, o in stays if o == only]
        if len(these) == 1:
            feebits.append(f"Plus the park's {these[0]}, once per stay{only}.")
        else:
            feebits.append(f"Plus the park's {and_list(these)}, each once per stay{only}.")
    feebits += pcts
    if ov.get("fee_text"):
        feebits.append(ov["fee_text"])
    text += (" " + " ".join(feebits)) if feebits else ""
    disc = collections.Counter()
    for q in one:
        if q["date"] in used and q["base"] is not None and round(q["base"] - charge(q), 2) > 0:
            disc[(tuple(sorted(str(x.get("name") or x.get("title") or x) for x in q["discounts"])) or ("a discount",),
                  f"{q['date'][:7]}")] += 1
    for (dn, month), _ in sorted(disc.items()):
        mm = f"{datetime.date.fromisoformat(month + '-01'):%B %Y}"
        text += f" The {mm} prices are after the park's automatic {' / '.join(dn)}."
    if "mins_text" in ov:
        text += (" " + ov["mins_text"]) if ov["mins_text"] else ""
    elif mins:
        for n in sorted(set(mins.values())):
            ds = [datetime.date.fromisoformat(d) for d in sorted(mins) if mins[d] == n]
            when = " and ".join(f"{d:%A, %B} {d.day}, {d.year}" for d in ds)
            text += f" Every RV type asks for at least {n} nights from {when}."
    if any(x[1] == "CAMPSPOT_BOOKING_FEE" and x[2] for q in qs for x in q["external"]):
        text += " Campspot adds its own booking fee at checkout (3%, at least $3)."
    text += f" Read {D}."
    new.update(checked="2026", note=text)
    link = next((u for u in re.findall(r"https?://(?:www\.)?campspot\.com/\S+", (e.get("website") or "") + " "
                                       + str((e.get("booking") or {}).get("url") or "")) if "/park/" in u or "/book/" in u),
                f"https://www.campspot.com/book/{r.get('engine_slug')}")
    dates_read = ", ".join(sorted({q["date"] for q in one}))
    finding = {"id": e["id"], "fees": new,
               "source": f"{link} (Campspot's pricing for each RV site type, one night from {dates_read}, 2 adults"
                         + ("; two nights from each Tuesday for the park's fees" if fees else "")
                         + f"; campspot_tier_2026-10-13.jsonl), read {D}"}
    rep.update(range=f"{span(vals, cur)}", fees={k: (v["model"], sorted(v["types"]) if v["types"] else None)
                                                  for k, v in fees.items()},
               types=len(use), used=used, flag=flags, mins=dict(mins))
    return finding, rep


def fields(e, r):
    """Groups the same reads settle. booking: written when absent, or given the platform when a note-made group
    lacks one. hookups: written when absent; a note-made group takes what Campspot's RV site types state where it
    differs or is silent (AWH: trust the booking channel over the sweep notes), and a value Campspot doesn't state is
    never read as "no". season: from the park's own closures on Campspot, last winter's and the coming one, written
    when absent or over a note-made season that disagrees. Nothing when Campspot
    sells no RV site type a 23-ft rig fits (Soaring Eagle PA: lodge rooms only), since then Campspot says nothing about
    the RV sites."""
    if r.get("error") or not r.get("types"):
        return {}, {}
    use = [t for t in r["types"].values() if countable(t)]
    if not use:
        return {}, {}
    link = next((u for u in re.findall(r"https?://(?:www\.)?campspot\.com/\S+", e.get("website") or "")), None)
    src = f"{link or 'https://www.campspot.com/book/' + str(r.get('engine_slug'))} (Campspot park record and site types), read {D}"
    prov = e.get("provenance") or {}
    made = lambda g: str((prov.get(g) or {}).get("source", "")).startswith("note prose")
    st, pv = {}, {}
    ob = e.get("booking") or {}
    if not ob:
        st["booking"] = {"reservable": True, "platform": "campspot"}
        pv["booking"] = {"source": src, "checked": D}
    elif made("booking") and not ob.get("platform"):
        st["booking"] = dict(ob, platform="campspot")
        pv["booking"] = {"source": f"{src}; kept from the note: {json.dumps(ob)}", "checked": D}
    am = {a for t in use for a in t["amenities"]}
    h = {}
    amps = [a for a in (50, 30, 20, 15) if f"{a}-Amp" in am or f"{a} Amp" in am]
    if amps:
        h["electric"] = amps[0]
    # Campspot's amenity names; "Water View", "Water Front" and "Water Accessible" are not a hookup
    if any(re.search(r"(?i)^water hook-?up", a) for a in am):
        h["water"] = True
    if any(re.search(r"(?i)^sewer hook-?up", a) for a in am):
        h["sewer"] = True
    old = e.get("hookups") or {}
    hsrc = src.replace("site types", "RV site types' amenities: "
                       + ", ".join(sorted(a for a in am if re.search(r"(?i)amp|water|sewer", a))))
    if h and not old:
        st["hookups"] = h
        pv["hookups"] = {"source": hsrc, "checked": D}
    elif h and made("hookups") and any(old.get(k) != v for k, v in h.items()):
        st["hookups"] = dict(old, **h)
        bits = [hsrc]      # provenance holds only source/checked/method, so what came from where is said here
        kept = {k: v for k, v in old.items() if k not in h}
        if kept:
            bits.append("kept from the note: " + json.dumps(kept))
        repl = {k: old[k] for k, v in h.items() if k in old and old[k] != v}
        if repl:
            bits.append("replaces the note scan's " + json.dumps(repl))
        pv["hookups"] = {"source": "; ".join(bits), "checked": D}
    # The park record's closedDates give the first and the last closed day (Tumble Hill NY's 2026-11-01 to 2027-04-30
    # is its posted "May 1st through October 31st"). The season is read from two of them: the opening from the closure
    # that spanned last January, so it is the opening that happened (Prairie Creek IN opened April 1 in 2025 and 2026
    # as its county posts, while its 2027 closure runs to April 30 for now), and the closing from the one that spans
    # the January read (Pastime OH's runs to the year 3000 until the park sets 2027). Without both, nothing is written,
    # with two exceptions. A park with no closure on record last winter that has set the next two alike (Ag Park NE:
    # November 1 to April 14 in both) has its season in them. A park that hasn't set the coming winter yet but began
    # the last two on the same day (McMullen WI: December 1 in 2024 and 2025) closes the day before. Alike is within a
    # day, as below: Fairgrounds RV Park WI closes from the Monday after the third weekend of October, which was the
    # 19th in 2026 and is the 18th in 2027. A note-made season that disagrees is replaced, as hookups are (AWH: trust
    # the booking channel over sweep notes).
    def closure(day):
        return next(((datetime.date.fromisoformat(c["startDateInParkTimeZone"]),
                      datetime.date.fromisoformat(c["endDateInParkTimeZone"]))
                     for c in r.get("closed_dates") or []
                     if c["startDateInParkTimeZone"] <= day <= c["endDateInParkTimeZone"]), None)
    # A date a day away is the same date: a closing day is named either as the last night or as the morning after
    # (Turkey Swamp NJ posts April 1 to November 15, and Campspot closes it from November 15).
    def off(old, new):
        day = lambda s: datetime.date.fromisoformat("2024-" + s)
        return {k for k, v in new.items() if old.get(k) != v and not (
            k in ("opens", "closes") and old.get(k) and abs((day(old[k]) - day(v)).days) <= 1)}
    last, nxt, after = closure(LAST_WINTER) or closure(LATE_WINTER), closure(WINTER), closure(NEXT_WINTER)
    prev = closure(PREV_WINTER)
    near = lambda a, b: abs((datetime.date.fromisoformat(a.strftime("2024-%m-%d"))
                             - datetime.date.fromisoformat(b.strftime("2024-%m-%d"))).days) <= 1
    said = f"closed {last[0]} to {last[1]} and from {nxt[0]}" if last and nxt else ""
    if not last and nxt and after and near(nxt[0], after[0]) and near(nxt[1], after[1]):
        last, said = nxt, f"closed {nxt[0]} to {nxt[1]} and {after[0]} to {after[1]}"
    elif last and not nxt and prev and prev != last and near(prev[0], last[0]):
        nxt, said = last, f"closed {prev[0]} to {prev[1]} and {last[0]} to {last[1]}; the coming winter not set yet"
    if last and nxt:
        opens, closes = last[1] + datetime.timedelta(1), nxt[0] - datetime.timedelta(1)
        old_s = e.get("season") or {}
        if 2 <= opens.month <= 7 and 8 <= closes.month <= 12:
            sea = {"year_round": False, "opens": opens.strftime("%m-%d"), "closes": closes.strftime("%m-%d")}
            ssrc = src.replace("park record and site types", f"park record: {said}")
            if not old_s:
                st["season"], pv["season"] = sea, {"source": ssrc, "checked": D}
            elif made("season") and off(old_s, sea):
                st["season"] = dict(old_s, **sea)
                repl = {k: old_s[k] for k in sea if k in old_s and old_s[k] != sea[k]}
                pv["season"] = {"source": ssrc + ("; replaces the note scan's " + json.dumps(repl) if repl else ""),
                                "checked": D}
            elif not made("season") and off(old_s, sea) & set(old_s):
                print(f"SEASON {e['id']}: the entry's {json.dumps(old_s)} is not from a note; Campspot gives "
                      f"{json.dumps(sea)}")
        else:
            print(f"SEASON {e['id']}: Campspot's closures {last} and {nxt} give no plain season")
    return st, pv


if __name__ == "__main__":
    args = sys.argv[1:]
    ids = None
    if "--ids" in args:
        ids = {int(x) for x in args[args.index("--ids") + 1].split(",")}
    out_path = args[args.index("--out") + 1] if "--out" in args else None
    fields_path = args[args.index("--fields") + 1] if "--fields" in args else None
    by = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
    recs = load(ids)
    out, fl = [], []
    for eid in sorted(recs):
        f, rep = verdict(by[eid], recs[eid])
        print(json.dumps(rep, ensure_ascii=False))
        if f:
            out.append(f)
            print("   ", f["fees"]["note"])
        st, pv = fields(by[eid], recs[eid])
        if st:
            fl.append({"id": eid, "set": st, "provenance": pv})
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print(len(out), "findings written")
    if fields_path:
        with open(fields_path, "w", encoding="utf-8") as fh:
            json.dump(fl, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print(len(fl), "field sets written")
