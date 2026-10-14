"""Nightly prices for the entries that had only RV Life's $ tier and link to CampLife (2026-10-14: after the RoverPass
entries, the next group by website link).

    python3 -I camplife_tier_build.py --ids 1,2,3 [--out FINDINGS.json] [--fields FIELDS.json]
    python3 -I apply.py FINDINGS.json [--apply]

Reads camplife_tier_2026-10-14.jsonl, written by ../private_gap_browser/camplife_api.py.

The stored range is the site rate before tax, one night from each date read, over every RV site a 23-ft rig fits. An
RV site is one whose type isn't a non-RV or long-stay product by name (the Campspot pass's SKIP, or a picnic shelter)
and whose site record takes an RV (a travel trailer, fifth wheel, motorhome...) or names no equipment; it fits when
its longest rig is 23 ft or more, or not given. CampLife's one-night quote (resSubTotal) can hold a charge made once
a stay with no label of its own, and the two-night quote on the same site gives it: one night twice, less two nights.
$3.50 is what CampLife charges a park for each online reservation (Mineola TX's council item of 2023-12-18: '$3.50'
per online reservation on its Standard and Premium plans), and a park passing that on is the platform's charge, not
the park's: it is taken off the rate, never stored, and the note names it. Any other flat once-a-stay amount is the
park's own, stored as reservation_fee as Artillery Ridge PA's $17.50 was (family_stays_build.py), and flagged PARK
FEE for a look by hand (East Fork WV names its $6 in its cancellation policy: 'full refund minus reservation fee');
OVERRIDE "stay" settles one the pair can't.

--fields writes the groups the same reads settle, in clean_notes.py's "set"/"provenance" shape: booking (reservable,
platform "operator" - CampLife is booking software the park runs as its own reservation system, the schema's rule for
software outside the enum) and hookups (the fitting sites' amenities: the highest of 50/30/20/15-Amp, water and sewer
from "Water", "Sewer" or "Full Hook Up"). Each is written when absent, or over a group made from note prose that it
contradicts or that is silent; a value CampLife doesn't state is never read as "no"."""
import collections, datetime, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from campspot_tier_build import SKIP, num, cash, span, and_list  # noqa: E402

D = "2026-10-14"
DATA = os.path.join(HERE, "camplife_tier_2026-10-14.jsonl")
PLATFORM_STAY = 3.5
RVEQ = r"(?i)trailer|5th|fifth|motor ?home|\brv\b|camper|class [abc]\b|toy ?hauler|\bbus\b|coach|\bvan\b"
# CampLife parks also sell picnic shelters as "sites", taking any equipment (Mozingo Lake MO 1980: $35-75 a day)
SKIP_CL = r"(?i)\bshelter\b"
CANADA = {"ON", "QC", "BC", "AB", "SK", "MB", "NB", "NS", "PE", "NL", "YT", "NT", "NU"}
LATER = (r"(?i)not (yet )?(open|available|accepting)|begin(s)? accepting|accepting reservations|reservations? (open|will "
         r"open|begin|start)|too far|in advance|booking window|cannot be made more than|opens? for (booking|reserv)")
CLOSED = r"(?i)\bclosed\b|\bis open\b|\bopen (from|between|april|may|june|march)|\bseason\b|re-?open"
# per park, by hand: "skip" a regex of type or site names to leave out, "keep" one to count though SKIP leaves it out,
# "stay": "park" | "platform" | a number (a once-a-stay charge the pair can't settle), "fee_text" for the note,
# "dates_text" to add a sentence about the dates, "no_dates" to drop the sentences made from the dates CampLife refused
# (when dates_text says it better), "wrong" naming the park the entry's CampLife link really books (nothing is read
# from that record: Timberlake MO 1977 linked Timberlake Campground, Brandon MS; Sunny Sites MO 2064 linked Sunny's
# Campground, Wauseon OH)
OVERRIDE = {
    1227: {"dates_text": "The campground is open April 1 to October 31, and CampLife took no 2027 dates when read.",
           "no_dates": True},
    1476: {"skip": r"(?i)destination trailer|park model", "stay": "platform"},
    1759: {"dates_text": "The campground is open April through October, and CampLife took no 2027 dates when read.",
           "no_dates": True},
    1977: {"wrong": "Timberlake Campground, 143 Timberlake Dr., Brandon MS (Barnett Reservoir)"},
    2064: {"wrong": "Sunny's Campground, 12399 County Road 13, Wauseon OH"},
}


def load(ids=None):
    recs = {}
    for l in open(DATA, encoding="utf-8"):
        r = json.loads(l)
        if ids is None or r["id"] in ids:
            recs[r["id"]] = r
    return recs


def tname(r, sid):
    return (((r.get("siteMap") or {}).get(str(sid)) or [None, ""])[1] or "").strip()


def sname(r, sid):
    return ((r.get("siteMap") or {}).get(str(sid)) or [str(sid)])[0] or str(sid)


def srec(r, sid):
    return (r.get("sites") or {}).get(str(sid)) or {}


def is_rv(r, sid, ov):
    t, nm = tname(r, sid), sname(r, sid)
    both = t + " | " + nm
    if ov.get("skip") and re.search(ov["skip"], both):
        return False
    if not (ov.get("keep") and re.search(ov["keep"], both)) and (re.search(SKIP, t) or re.search(SKIP_CL, t)):
        return False
    eq = [(r.get("config") or {}).get("equip", {}).get(str(x), "") for x in srec(r, sid).get("equipTypeIds") or []]
    return not eq or any(re.search(RVEQ, x) for x in eq)


def fits(r, sid):
    ml = srec(r, sid).get("maxLength")
    return not ml or ml >= 23


def stay_charge(r, ov):
    """-> (amount, kind, pairs): the once-a-stay part of the quotes, from the one/two-night pairs on the same site."""
    q1 = {(q["date"], q["site"]): q["sub"] for q in r.get("quotes") or [] if q.get("nights") == 1 and q.get("sub") is not None}
    pairs = []
    for q in r.get("quotes") or []:
        if q.get("nights") == 2 and q.get("sub") is not None and (q["date"], q["site"]) in q1:
            one = q1[(q["date"], q["site"])]
            pairs.append((round(2 * one - q["sub"], 2), one, q["sub"]))
    amounts = sorted({p[0] for p in pairs})
    if "stay" in ov:
        v = ov["stay"]
        if isinstance(v, (int, float)):
            return float(v), "platform" if v == PLATFORM_STAY else "park", pairs
        return (amounts[0] if amounts else 0.0), v, pairs
    if not pairs:
        return None, "no pair", pairs
    if len(amounts) > 1:
        return None, "uneven %s" % amounts, pairs
    a = amounts[0]
    if abs(a) < 0.005:
        return 0.0, "none", pairs
    if abs(a - PLATFORM_STAY) < 0.005:
        return a, "platform", pairs
    if a > 0:       # a flat amount of the park's own, like Artillery Ridge PA's $17.50 (family_stays_build.py)
        return a, "park", pairs
    return None, "other %s" % a, pairs


def classify(msgs):
    t = " ".join(msgs)
    if re.search(LATER, t):
        return "later"
    if re.search(CLOSED, t):
        return "closed"
    return "other"


def verdict(e, r):
    """-> (finding or None, report dict)."""
    rep = {"id": e["id"], "name": e["name"], "state": e.get("state"), "cg": r.get("cg")}
    if r.get("error"):
        rep["flag"] = ["GONE: " + str(r.get("error"))]
        return None, rep
    ov = OVERRIDE.get(e["id"], {})
    if ov.get("wrong"):
        rep["flag"] = ["WRONG PARK: the CampLife link books " + ov["wrong"]]
        return None, rep
    cur = "CAD" if (e.get("state") in CANADA or (r.get("currency") or "").upper() == "CAD") else "USD"
    days = r.get("dates") or {}
    flags = []
    stay, kind, pairs = stay_charge(r, ov)
    rep["stay"] = [stay, kind, pairs]
    if stay is None:
        flags.append("STAY %s %s" % (kind, pairs))
    price, short, other, types = {}, set(), set(), {}
    for q in r.get("quotes") or []:
        if q.get("nights") != 1 or q.get("sub") is None:
            continue
        sid = q["site"]
        if not is_rv(r, sid, ov):
            other.add(tname(r, sid) or sname(r, sid))
            continue
        if not fits(r, sid):
            short.add(tname(r, sid) or sname(r, sid))
            continue
        price[(sid, q["date"])] = round(q["sub"] - (stay or 0), 2)
        types[sid] = tname(r, sid) or sname(r, sid)
    rep["left_out"] = sorted(other)
    if not price:
        rep["flag"] = flags + ["NO RV QUOTES"]
        rep["dates"] = {d: (len(v["open"]) if v["open"] else " ".join(v.get("errors") or []) or v.get("status"))
                        for d, v in days.items()}
        return None, rep
    if any(f.startswith("STAY") for f in flags):
        rep["flag"] = flags
        rep["range"] = span(list(price.values()), cur)
        return None, rep
    used = sorted({d for _, d in price})
    if r.get("fallback"):
        flags.append("FALLBACK DATES")
    vals = list(price.values())
    lo, hi = min(vals), max(vals)
    new = {"nightly_low": num(lo), "nightly_high": num(hi), "currency": cur}
    if kind == "park" and stay:
        new["reservation_fee"] = num(stay)
        flags.append("PARK FEE %s" % num(stay))
    if hi > 3 * lo:
        flags.append("WIDE %s-%s" % (num(lo), num(hi)))
    if lo < 15 or hi > 150:
        flags.append("ODD %s-%s" % (num(lo), num(hi)))
    if cur == "CAD":
        flags.append("CAD")
    # the note
    tnames = list(dict.fromkeys(types[s] for s, _ in sorted(price, key=lambda k: (price[k], types[k[0]]))))
    shown = tnames if len(tnames) <= 6 else tnames[:5] + [f"{len(tnames) - 5} more"]
    by_month = collections.OrderedDict()
    for d in used:
        dd = datetime.date.fromisoformat(d)
        by_month.setdefault(f"{dd:%B %Y}", []).append((dd, [v for (s, y), v in price.items() if y == d]))
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
    text = (f"Read on CampLife: one night, site rate before tax, every RV site a 23-ft rig fits ({and_list(shown)}). "
            f"{seasons}")
    if ov.get("dates_text"):
        text += " " + ov["dates_text"]
    mname = lambda ms: and_list(f"{datetime.date.fromisoformat(m + '-01'):%B %Y}" for m in ms)
    used_m = {d[:7] for d in used}
    shut = collections.defaultdict(set)
    for d, v in days.items():
        if d[:7] in used_m:
            continue
        if v["open"]:
            shut["no RV site"].add(d[:7])
        elif v.get("errors"):
            c = classify(v["errors"])
            shut[c].add(d[:7])
            if c == "other":
                flags.append(f"DATE {d}: {' '.join(v['errors'])[:200]}")
        else:
            shut["no RV site"].add(d[:7])
    closed_m = sorted(shut["closed"])
    later_m = sorted(shut["later"] - shut["closed"])
    empty_m = sorted((shut["no RV site"] | shut["other"]) - shut["closed"] - shut["later"])
    if ov.get("no_dates"):
        closed_m = later_m = empty_m = []
        flags = [f for f in flags if not f.startswith("DATE ")]
    if closed_m:
        text += f" CampLife takes no booking in {mname(closed_m)}, when the park is closed."
    if later_m:
        text += f" {mname(later_m)} {'isn' if len(later_m) == 1 else 'aren'}'t open for booking yet."
    if empty_m:
        text += f" CampLife offers no RV site in {mname(empty_m)}."
    if short:
        text += f" Left out: {and_list(sorted(short))} (sites under 23 ft)."
    if kind == "platform" and stay:
        text += f" An online booking adds {cash(stay, cur)} once a stay."
    elif kind == "park" and stay:
        text += f" Each stay also carries a flat {cash(stay, cur)}, which CampLife's quote includes."
    if ov.get("fee_text"):
        text += " " + ov["fee_text"]
    text += f" Read {r.get('read') or D}."
    new.update(checked="2026", note=text)
    link = next((u for u in (e.get("website") or "").split("\n") if "camplife" in u.lower()),
                f"https://www.camplife.com/{r['cg']}/reservation/step1")
    book = f"https://www.camplife.com/{r['cg']}/reservation/step1"
    pair = [p for p in pairs if p[0] == stay] if stay is not None else []
    finding = {"id": e["id"], "fees": new,
               "source": f"{book} (CampLife's quotes for {len(price)} site-nights, one night from "
                         + ", ".join(sorted(days)) + (f"; one night ${pair[0][1]:.2f} and two nights ${pair[0][2]:.2f} on "
                                                      f"the same site for the once-a-stay charge" if pair else "")
                         + f"; camplife_tier_2026-10-14.jsonl), read {r.get('read') or D}"
                         + ("" if link == book else f"; the entry's link {link}")}
    rep.update(range=span(vals, cur), sites=len(types), used=used, flag=flags)
    return finding, rep


HOOK_W = r"(?i)^(water|water hook ?-?ups?)$|full hook|\bfhu\b|water\s*(&|and|/)\s*(electric|sewer)|^w/e"
HOOK_S = r"(?i)^(sewer|sewer hook ?-?ups?)$|full hook|\bfhu\b|sewer\s*(&|and|/)"


def fields(e, r):
    """Groups the same reads settle: booking, hookups."""
    if r.get("error"):
        return {}, {}
    ov = OVERRIDE.get(e["id"], {})
    if ov.get("wrong"):
        return {}, {}
    use = sorted({q["site"] for q in r.get("quotes") or [] if q.get("nights") == 1 and q.get("sub") is not None
                  and is_rv(r, q["site"], ov) and fits(r, q["site"])})
    if not use:
        return {}, {}
    read = r.get("read") or D
    book = f"https://www.camplife.com/{r['cg']}/reservation/step1"
    src = f"{book} (CampLife booking page and RV sites), read {read}"
    prov = e.get("provenance") or {}
    made = lambda grp: str((prov.get(grp) or {}).get("source", "")).startswith("note prose")
    st, pv = {}, {}
    ob = e.get("booking") or {}
    if not ob:
        st["booking"] = {"reservable": True, "platform": "operator"}
        pv["booking"] = {"source": src, "checked": read}
    elif made("booking") and (ob.get("platform") != "operator" or ob.get("reservable") is not True):
        st["booking"] = dict(ob, reservable=True, platform="operator")
        repl = {k: ob[k] for k in ("reservable", "platform") if k in ob and ob[k] != st["booking"][k]}
        kept = {k: v for k, v in ob.items() if k not in ("reservable", "platform")}
        bits = [src] + (["kept from the note: " + json.dumps(kept)] if kept else []) + (
            ["replaces the note's " + json.dumps(repl)] if repl else [])
        pv["booking"] = {"source": "; ".join(bits), "checked": read}
    names = (r.get("config") or {}).get("amenities") or {}
    am = sorted({names.get(str(a), str(a)).strip() for sid in use for a in srec(r, sid).get("amenityIds") or []})
    h = {}
    amps = [a for a in (50, 30, 20, 15) if any(re.search(r"(?i)\b%d[- ]?amps?\b" % a, x) for x in am)]
    if amps:
        h["electric"] = amps[0]
    if any(re.search(HOOK_W, x) for x in am):
        h["water"] = True
    if any(re.search(HOOK_S, x) for x in am):
        h["sewer"] = True
    old = e.get("hookups") or {}
    hsrc = src.replace("booking page and RV sites", "RV sites' amenities: " + ", ".join(
        x for x in am if re.search(r"(?i)amp|water|sewer|electric|hook", x) and not re.search(r"(?i)front|view", x)))
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
