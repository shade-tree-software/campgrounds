"""Nightly prices for the entries that had only RV Life's $ tier and link to RoverPass (2026-10-14: after the Campspot
entries, the next group by website link).

    python3 -I roverpass_tier_build.py --ids 1,2,3 [--out FINDINGS.json] [--fields FIELDS.json]
    python3 -I apply.py FINDINGS.json [--apply]

Reads roverpass_tier_2026-10-14.jsonl, written by ../private_gap_browser/roverpass_api.py. Only a park that takes
bookings through RoverPass (isBookable) is priced here. The rest are directory listings nobody has claimed ("Claim my
Campground"), whose rate tables are not the operator's (.claude/memory/feedback_note_rate_sourcing.md): they are
reported NOT BOOKABLE and priced, if at all, from the operator's own page.

The stored range is the site rate before tax for every RV rate a 23-ft rig fits, one night from each date read:
RoverPass's night price for that date, plus any fee of the park's own that the cart charges every night. An RV rate is
one sold under an RV site type (roverpass_api.RVISH) whose name isn't a long-stay or non-RV product (the Campspot
pass's SKIP), that most of its open sites fit (each site's longest rig 23 ft or more, or none given), or whose own
longest rig is unset or 23 ft or more where RoverPass lists no sites (a request-to-book park has no site inventory).
A rate that needs a few more nights on a date (2 to 7) is priced there too and the minimum is said; one that needs 8 or
more is a long-stay product and left out, and so is a rate sold only to a group (military, first responders, members:
RESTRICT), which is a discount. The park's own fees come from the carts (items with isFee), fitted by
campspot_tier_build.fit_fee: a flat fee once a stay that every quoted rate carries goes in reservation_fee; a flat fee a
night is folded into the nightly price; anything else is said in the note. RoverPass's platform fee, its processing fee
and tax are the platform's and the state's: the note names the platform fee, nothing stores them.

A closed date lists no rates (RoverPass, unlike Campspot, prices nothing inside a closure), so there is nothing to set
aside: the note names the months the park is closed and those that offer no RV rate. A request-to-book park (isRequest:
the operator confirms each booking) is said so. --fields writes the groups the same reads settle: booking, hookups (the
fitting rates' amenities) and season (closeSeasonDates), in clean_notes.py's "set"/"provenance" shape."""
import collections, datetime, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "private_gap_browser"))
from campspot_tier_build import SKIP, num, cash, span, and_list, fit_fee, pct_text, TREAT  # noqa: E402
from roverpass_api import RVISH  # noqa: E402

D = "2026-10-14"
DATA = os.path.join(HERE, "roverpass_tier_2026-10-14.jsonl")
LONG = 8          # a rate needing this many nights or more is a long-stay product, not a nightly one
# a rate sold only to a group (military, first responders, members) is a discount, not the price: left out and flagged
RESTRICT = (r"(?i)\b(military|veterans?|police|firefighters?|first responders?|rescue workers?|seniors?|good sam|"
            r"passport america|escapees|members? only)\b")
# per park, by hand: "skip" a regex of rate names to leave out, "keep" one of names to count though SKIP leaves them out,
# "fee_text" for a fee the fit can't settle, "mins_text" to replace the minimum-stay sentence, "dates_text" to add one,
# "no_season" to keep fields() from writing a season (the park's own page gives other dates, or RoverPass's closures
# are its booking calendar's rather than the campground's)
OVERRIDE = {
    1278: {"no_season": "the park's own page gives its season as May 1 - October 25, 2026; RoverPass stops on October 18"},
    2661: {"no_season": "camp sites are also first come, first served, and the city's page names no closing; the "
                        "closures are RoverPass's booking calendar"},
    4090: {"no_season": "the park's own page gives April 10 - October 25, 2026; RoverPass books April 16 - October 14"},
}


def load(ids=None):
    recs = {}
    for line in open(DATA, encoding="utf-8"):
        r = json.loads(line)
        if ids is None or r["id"] in ids:
            recs[r["id"]] = r                 # the last read of a park wins
    return recs


def label(rt):
    return (rt.get("siteTypeName") or "").split(" - ")[0]


def nm_(name):
    return " ".join((name or "").split())


def site_lengths(r, rid):
    s = (r.get("sites") or {}).get(rid) or {}
    out = []
    for x in s.get("sites") or []:
        ls = [int(v) for v in x.get("maxLength") or [] if str(v).isdigit()]
        out.append(max(ls) if ls else 0)
    return out


def fits(r, rt):
    """Most of the rate's open sites take 23 ft or give no length; with no site list, the rate's own longest rig."""
    ls = site_lengths(r, rt["id"])
    if ls:
        return sum(1 for x in ls if x == 0 or x >= 23) * 2 >= len(ls)
    own = [int(v) for v in rt.get("maxLength") or [] if str(v).isdigit()]
    return not own or 0 in own or max(own) >= 23


def rv(rt, ov):
    name = rt.get("name") or ""
    skipped = re.search(SKIP, name) and not (ov.get("keep") and re.search(ov["keep"], name))
    return (label(rt) in RVISH and not skipped and not (ov.get("skip") and re.search(ov["skip"], name))
            and not re.search(RESTRICT, name))


def verdict(e, r):
    """-> (finding or None, report dict)."""
    rep = {"id": e["id"], "name": e["name"], "state": e.get("state")}
    g = r.get("info") or {}
    if r.get("error") or not g:
        rep["flag"] = ["GONE: " + str(r.get("error"))]
        return None, rep
    if not g.get("isBookable"):
        rep["flag"] = ["NOT BOOKABLE (%s)" % g.get("systemType")]
        return None, rep
    ov = OVERRIDE.get(e["id"], {})
    cur = "CAD" if ((g.get("currency") or {}).get("code") or "").upper() == "CAD" else "USD"
    days = r.get("dates") or {}
    flags = []
    price, mins, rates, short = {}, {}, {}, set()     # (rate, date) -> night price; date -> nights; id -> rate
    restricted = sorted({nm_(rt["name"]) for v in days.values() for rt in v.get("ratesAvailableDuring") or []
                         if label(rt) in RVISH and re.search(RESTRICT, rt.get("name") or "")})
    if restricted:
        flags.append("RESTRICTED (left out) %s" % restricted)
    for d, v in days.items():
        one_night = False
        for rt in v.get("ratesAvailableDuring") or []:
            if rv(rt, ov):
                if fits(r, rt):
                    rates[rt["id"]] = rt
                    price[(rt["id"], d)] = rt["nightPrice"]["amount"]
                    one_night = True
                else:
                    short.add(nm_(rt["name"]))
        # a rate that needs 2-7 nights on that date is still on sale; when no fitting rate sells one night, the least
        # any of them asks is the date's minimum
        need = []
        for rt in v.get("unavailableRatesMinNightsList") or []:
            n = int(rt.get("minNightsRequired") or 0)
            if rv(rt, ov) and fits(r, rt) and 1 < n < LONG:
                rates[rt["id"]] = rt
                price.setdefault((rt["id"], d), rt["nightPrice"]["amount"])
                need.append(n)
        if need and not one_night:
            mins[d] = min(need)
    price = {k: v for k, v in price.items() if v}
    if not price:
        rep["flag"] = ["NO RV RATES (%s, %s)" % (g.get("systemType"), "request" if g.get("isRequest") else "instant")]
        rep["dates"] = {d: (v.get("availability") or {}).get("message") or len(v.get("ratesAvailableDuring") or [])
                        for d, v in days.items()}
        return None, rep
    used = sorted({d for _, d in price})
    if r.get("fallback"):
        flags.append("FALLBACK DATES")
    # the park's own fees, from the carts
    carts = [p for p in r.get("pricing") or [] if p.get("resp")]
    fee_pts = collections.defaultdict(list)
    plat, proc = [], []
    for p in carts:
        res = (p["resp"].get("reservations") or [{}])[0]
        items = (res.get("pricing") or {}).get("items") or []
        site = sum(i["base"]["amount"] for i in items if not i.get("isFee"))
        exp = price.get((p["rate"], p["from"]))
        if exp is not None and abs(site - exp * p["nights"]) > 0.011:
            flags.append(f"CART {p['name']} {p['from']} x{p['nights']}: site ${site} vs ${exp} a night")
        for i in items:
            if i.get("isFee"):
                fee_pts[i["name"]].append((p["nights"], site, i["base"]["amount"], p))
        if not re.search(RESTRICT, p.get("name") or ""):
            plat.append((p["nights"], site, (p["resp"].get("platformFeeTotal") or {}).get("display")))
        proc.append((p["resp"].get("processingFeeTotal") or {}).get("amount") or 0)
    fees = {}
    for nm, pts in fee_pts.items():
        fitsx = fit_fee([x[:3] for x in pts])
        ambiguous = len({TREAT[m] for m, _ in fitsx}) > 1
        carriers = {x[3]["rate"] for x in pts}
        quoted = {p["rate"] for p in carts}
        fees[nm] = {"model": None if ambiguous else (fitsx[0] if fitsx else None),
                    "every": carriers >= quoted, "amounts": sorted({x[2] for x in pts})}
        if not fitsx or ambiguous:
            if "fee_text" not in ov:
                flags.append(f"FEE '{nm}' {'ambiguous ' + str([m for m, _ in fitsx]) if ambiguous else 'irregular'} "
                             f"{fees[nm]['amounts'][:6]}")
    if any(f.startswith("FEE") for f in flags) and "fee_text" not in ov:
        rep["flag"] = flags
        return None, rep
    night_add = sum(f["model"][1]["B"] for f in fees.values()
                    if f["model"] and f["model"][0] in ("night", "stay+night") and f["every"])
    vals = [round(v + night_add, 2) for v in price.values()]
    lo, hi = min(vals), max(vals)
    new = {"nightly_low": num(lo), "nightly_high": num(hi), "currency": cur}
    stay = [(nm, f["model"][1]["A"]) for nm, f in fees.items()
            if f["model"] and f["model"][0] in ("stay", "stay+night", "stay+pct") and f["every"]]
    if stay:
        new["reservation_fee"] = num(round(sum(a for _, a in stay), 2))
    if hi > 3 * lo:
        flags.append("WIDE %s-%s" % (num(lo), num(hi)))
    if lo < 15 or hi > 150:
        flags.append("ODD %s-%s" % (num(lo), num(hi)))
    if cur == "CAD":
        flags.append("CAD")
    weekdays = [d for d in used if datetime.date.fromisoformat(d).weekday() < 4]
    if mins:
        flags.append("MINIMUM %s" % mins)
    # the note
    order = sorted(rates, key=lambda i: (min(v for (x, _), v in price.items() if x == i), nm_(rates[i]["name"])))
    tnames = list(dict.fromkeys(nm_(rates[i]["name"]) for i in order))
    shown = tnames if len(tnames) <= 6 else tnames[:5] + [f"{len(tnames) - 5} more"]
    by_month = collections.OrderedDict()
    for d in used:
        dd = datetime.date.fromisoformat(d)
        by_month.setdefault(f"{dd:%B %Y}", []).append((dd, [round(v + night_add, 2) for (x, y), v in price.items()
                                                             if y == d]))
    parts = []
    for month, ds in by_month.items():
        ds = sorted(ds, key=lambda x: x[0].weekday())
        if len(ds) > 1 and len({span(v, cur) for _, v in ds}) == 1:
            parts.append((month, f"{span(ds[0][1], cur)}, " + " and ".join(f"{dd:%A}" for dd, _ in ds) + " alike"))
        else:
            parts.append((month, "; ".join(f"{span(v, cur)} on a {dd:%A}" for dd, v in ds)))
    merged = collections.OrderedDict()
    for month, t in parts:
        merged.setdefault(t, []).append(month)
    seasons = " ".join(f"{(', '.join(m[:-1]) + ' and ' + m[-1]) if len(m) > 1 else m[0]}: {t}."
                       for t, m in merged.items())
    text = (f"Read on RoverPass: one night, site rate before tax, every RV rate a 23-ft rig fits ({and_list(shown)}). "
            f"{seasons}")
    if ov.get("dates_text"):
        text += " " + ov["dates_text"]
    mname = lambda ms: and_list(f"{datetime.date.fromisoformat(m + '-01'):%B %Y}" for m in ms)
    used_m = {d[:7] for d in used}
    msg = {d: ((v.get("availability") or {}).get("message") or "") for d, v in days.items()
           if not (v.get("availability") or {}).get("isAvailable")}
    closed_m = sorted({d[:7] for d, m in msg.items() if re.search(r"(?i)is closed", m)} - used_m)
    later_m = sorted({d[:7] for d, m in msg.items() if re.search(r"(?i)this far in advance", m)} - used_m
                     - set(closed_m))
    for d, m in msg.items():
        if not re.search(r"(?i)is closed|this far in advance", m):
            flags.append(f"DATE {d}: {m}")
    empty_m = sorted({d[:7] for d in days} - used_m - set(closed_m) - set(later_m))
    if closed_m:
        text += f" RoverPass shows the park closed in {mname(closed_m)}."
    if later_m:
        text += f" {mname(later_m)} {'isn' if len(later_m) == 1 else 'aren'}'t open for booking yet."
    if empty_m:
        text += f" RoverPass offers no RV site in {mname(empty_m)}."
    if short:
        text += f" Left out: {and_list(sorted(short))} (sites under 23 ft)."
    feebits = []
    for nm, f in fees.items():
        lab = f"'{nm}'" if re.search(r"(?i)\b(fee|fees|charge|surcharge)$", nm) else f"'{nm}' fee"
        only = "" if f["every"] else " on some rates"
        if f["model"] is None:
            continue
        m, prm = f["model"]
        if m == "stay":
            feebits.append(f"Plus the park's {cash(prm['A'], cur)} {lab}, once per stay{only}.")
        elif m == "night":
            feebits.append(f"Those include the park's {cash(prm['B'], cur)}-a-night {lab}{only}.")
        elif m == "pct":
            feebits.append(f"The park adds {pct_text(prm['P'])} of the site charge as a {lab}{only}.")
        elif m == "stay+night":
            feebits.append(f"Those include the park's {cash(prm['B'], cur)}-a-night {lab}, which also adds "
                           f"{cash(prm['A'], cur)} once per stay{only}.")
        elif m == "stay+pct":
            feebits.append(f"Plus the park's {lab}: {cash(prm['A'], cur)} once per stay and {pct_text(prm['P'])} of "
                           f"the site charge{only}.")
    if ov.get("fee_text"):
        feebits.append(ov["fee_text"])
    text += (" " + " ".join(feebits)) if feebits else ""
    if "mins_text" in ov:
        text += (" " + ov["mins_text"]) if ov["mins_text"] else ""
    elif mins:
        for n in sorted(set(mins.values())):
            ds = [datetime.date.fromisoformat(d) for d in sorted(mins) if mins[d] == n]
            when = " and ".join(f"{x:%A, %B} {x.day}, {x.year}" for x in ds)
            text += f" Every RV rate asks for at least {n} nights from {when}."
    if g.get("isRequest"):
        text += " Bookings are requests the park confirms."
    one = sorted({x for x in plat if x[0] == 1 and x[2] and x[2] != "$0.00"}, key=lambda x: x[1])
    if one:
        pf = {x[2] for x in plat if x[2]}
        if len(pf) == 1:
            text += f" RoverPass adds its own {next(iter(pf)).replace('.00', '')} platform fee at checkout"
        else:
            text += (f" RoverPass adds its own platform fee at checkout ({one[0][2].replace('.00', '')} on one "
                     f"{cash(one[0][1], cur)} night)")
        text += (", and a card processing fee." if any(proc) else ".")
    text += f" Read {r.get('read') or D}."
    new.update(checked="2026", note=text)
    link = next((u for u in (e.get("website") or "").split("\n") if "roverpass.com/c/" in u),
                f"https://www.roverpass.com/c/{r['slug']}/")
    dates_read = ", ".join(sorted(days))
    cart_from = sorted({p["from"] for p in carts})
    finding = {"id": e["id"], "fees": new,
               "source": f"{link} (RoverPass's pricing for each RV rate, one night from {dates_read}"
                         + (f"; carts for one and two nights from {and_list(cart_from)} for the park's fees" if carts else "")
                         + f"; roverpass_tier_2026-10-14.jsonl), read {r.get('read') or D}"}
    rep.update(range=span(vals, cur), fees={k: v["model"] for k, v in fees.items()}, rates=len(rates), used=used,
               flag=flags, request=bool(g.get("isRequest")))
    return finding, rep


def fields(e, r):
    """Groups the same reads settle. booking: written when absent, or given the platform when a note-made group lacks
    one. hookups: written when absent; a note-made group takes what the fitting RV rates' amenities state where it
    differs or is silent (AWH: trust the booking channel over the sweep notes), and a value RoverPass doesn't state is
    never read as "no". season: from the park's closures on RoverPass - this year's closing (the start of the coming
    winter's closure) and next year's opening (its end) - when the closure after that starts within a day of the same
    date; written when absent or over a note-made season that disagrees."""
    g = r.get("info") or {}
    if not g.get("isBookable"):
        return {}, {}
    ov = OVERRIDE.get(e["id"], {})
    use = {}
    for v in (r.get("dates") or {}).values():
        for rt in (v.get("ratesAvailableDuring") or []) + [x for x in v.get("unavailableRatesMinNightsList") or []
                                                          if 1 < int(x.get("minNightsRequired") or 0) < LONG]:
            if rv(rt, ov) and fits(r, rt) and (rt.get("nightPrice") or {}).get("amount"):
                use[rt["id"]] = rt
    if not use:
        return {}, {}
    read = r.get("read") or D
    link = next((u for u in (e.get("website") or "").split("\n") if "roverpass.com/c/" in u),
                f"https://www.roverpass.com/c/{r['slug']}/")
    src = f"{link} (RoverPass park record and RV rates), read {read}"
    prov = e.get("provenance") or {}
    made = lambda grp: str((prov.get(grp) or {}).get("source", "")).startswith("note prose")
    st, pv = {}, {}
    ob = e.get("booking") or {}
    if not ob:
        st["booking"] = {"reservable": True, "platform": "roverpass"}
        pv["booking"] = {"source": src, "checked": read}
    elif made("booking") and ob.get("platform") != "roverpass":
        st["booking"] = dict(ob, reservable=True, platform="roverpass")
        repl = {k: ob[k] for k in ("reservable", "platform") if k in ob and ob[k] != st["booking"][k]}
        kept = {k: v for k, v in ob.items() if k not in ("reservable", "platform")}
        bits = [src] + (["kept from the note: " + json.dumps(kept)] if kept else []) + (
            ["replaces the note's " + json.dumps(repl)] if repl else [])
        pv["booking"] = {"source": "; ".join(bits), "checked": read}
    am = {a for rt in use.values() for a in rt.get("amenities") or []}
    h = {}
    amps = [a for a in (50, 30, 20, 15) if f"amps_{a}" in am]
    if amps:
        h["electric"] = amps[0]
    if am & {"water", "water_hookups"}:       # an RRS rate's code, a CRS rate's code
        h["water"] = True
    if am & {"sewer", "sewer_hookups"}:
        h["sewer"] = True
    old = e.get("hookups") or {}
    hsrc = src.replace("park record and RV rates", "RV rates' amenities: "
                       + ", ".join(sorted(a for a in am if re.search(r"amps|water|sewer|electric", a))))
    if h and not old:
        st["hookups"] = h
        pv["hookups"] = {"source": hsrc, "checked": read}
    elif h and made("hookups") and any(old.get(k) != v for k, v in h.items()):
        st["hookups"] = dict(old, **h)
        bits = [hsrc]
        kept = {k: v for k, v in old.items() if k not in h}
        if kept:
            bits.append("kept from the note: " + json.dumps(kept))
        repl = {k: old[k] for k, v in h.items() if k in old and old[k] != v}
        if repl:
            bits.append("replaces the note scan's " + json.dumps(repl))
        pv["hookups"] = {"source": "; ".join(bits), "checked": read}
    cl = sorted((datetime.date.fromisoformat(c["from"]), datetime.date.fromisoformat(c["to"]))
                for c in g.get("closeSeasonDates") or []) if not ov.get("no_season") else []
    now = [c for c in cl if c[1] >= datetime.date.fromisoformat(read)]
    if len(now) >= 2:
        a, b = now[0], now[1]
        closes, opens, closes2 = a[0] - datetime.timedelta(1), a[1] + datetime.timedelta(1), b[0] - datetime.timedelta(1)
        day = lambda x: datetime.date(2024, x.month, x.day)
        if abs((day(closes) - day(closes2)).days) <= 1 and 2 <= opens.month <= 7 and 8 <= closes.month <= 12:
            sea = {"year_round": False, "opens": opens.strftime("%m-%d"), "closes": closes.strftime("%m-%d")}
            said = f"closed {a[0]} to {a[1]} and from {b[0]}"
            ssrc = src.replace("park record and RV rates", f"park record: {said}")
            old_s = e.get("season") or {}

            def off(o, n):
                dd = lambda s: datetime.date.fromisoformat("2024-" + s)
                return {k for k, v in n.items() if o.get(k) != v and not (
                    k in ("opens", "closes") and o.get(k) and abs((dd(o[k]) - dd(v)).days) <= 1)}
            if not old_s:
                st["season"], pv["season"] = sea, {"source": ssrc, "checked": read}
            elif made("season") and off(old_s, sea):
                st["season"] = dict(old_s, **sea)
                repl = {k: old_s[k] for k in sea if k in old_s and old_s[k] != sea[k]}
                pv["season"] = {"source": ssrc + ("; replaces the note scan's " + json.dumps(repl) if repl else ""),
                                "checked": read}
            elif not made("season") and off(old_s, sea) & set(old_s):
                print(f"SEASON {e['id']}: the entry's {json.dumps(old_s)} is not from a note; RoverPass gives "
                      f"{json.dumps(sea)}")
        else:
            print(f"SEASON {e['id']}: RoverPass's closures {a} and {b} give no plain season")
    return st, pv


if __name__ == "__main__":
    args = sys.argv[1:]
    ids = {int(x) for x in args[args.index("--ids") + 1].split(",")} if "--ids" in args else None
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
