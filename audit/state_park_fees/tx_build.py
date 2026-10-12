"""Texas state parks findings: each park's own campsite and entrance fee pages on tpwd.texas.gov, read 2026-10-12
(tx_pages.py -> tx_park_pages_2026-10-12.json).

    python3 -I tx_build.py OUT

Texas publishes its fees park by park: every campsite type with its nightly fee ('Plus daily entrance fee'), and the
park's daily entrance fee per person 13 and older. A type counts for an RV unless its name or description makes it a
tent, walk-in, hike-in, equestrian, group, overflow or cabin site, bars RVs ('No motor homes, trailers, or pop-ups
allowed'), or caps them under 23 ft ('trailers and motor homes 20 feet or less'); a water-only or primitive type counts
only where its page says RVs, trailers or motor homes may use it, or calls it drive-in. The base is the cheapest such
type with the fewest hookups (primitive, then water, then electric, then full hookups); nightly_low / nightly_high span
that kind's types (a park's bayfront or premium loop costs more); water, electric and full hookups are add-ons on it.
The entrance fee is recorded per person and day (the registry row has the per-person shape without an amount)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
pages = json.load(open(os.path.join(HERE, "tx_park_pages_2026-10-12.json"), encoding="utf-8"))
UNIT = {7027: r"Doctor", 7028: r"South Sulphur", 7058: r"Birch Creek", 7059: r"Nails Creek", 7079: r"Johnson Branch",
        7080: r"Isle du Bois", 7013: r"River District"}
# The type's NAME says what kind of site it is; its description can only bar RVs outright. (Amenity lines such as
# 'Shade shelter', 'Good for RV groups' or 'Excess vehicles must park in an overflow area' are not exclusions, and a
# description naming a few tent-only sites among RV ones - Balmorhea's 'Sites 12-17: Tent only' - is not either.)
NAME_EXCL = re.compile(r"(?i)tents? only|tent-only|walk-in|walk in|hike-in|hike in|backpack|paddle|boat-in|floating|"
                       r"equest|group|overflow|cabin|shelter|lodg|screened")
TEXT_EXCL = re.compile(r"(?i)no (?:motor homes|recreational vehicles|rvs|trailers)|these are tent-only sites|"
                       r"(?:these|all) sites are (?:for )?tents? only|(?:motor homes|trailers|rvs)[^.]{0,40}(?:are )?"
                       r"not (?:permitted|allowed)|vehicles are not allowed|must reserve at least \d+ campsites")
RVOK = re.compile(r"(?i)\brvs?\b|trailer|motor home|pop-up|camper|drive-in|pull-through|back-in")
LIMIT = re.compile(r"(?i)(\d+) feet or less|under (\d+) feet|maximum (?:vehicle |rv |trailer )?length (?:is )?(\d+)|"
                   r"(\d+)[- ]f(?:oo|ee)t (?:maximum|max)")


def kind(t, text):
    n = t["name"]
    if re.search(r"(?i)full hookup", n) or any(l.lower() == "sewer hookup" for l in t["listing"]):
        return "fhu"
    if re.search(r"(?i)electric|\bamp\b", n):
        return "e"
    if re.search(r"(?i)water", n):
        return "w"
    if re.search(r"(?i)primitive", n):
        return "ne"
    return None


def usable(t):
    if not t.get("name"):          # Martin Dies Jr.'s type headings are not links: take the listing's first line
        t["name"] = next((l for l in t["listing"][1:3] if "Photos" not in l and l != 'js-more">'), None)
    if not t.get("name") or t.get("nightly") is None:
        return None, "no name or fee"
    text = " ".join(l for l in t["listing"] if l not in ("More »",))
    k = kind(t, text)
    if k is None:
        return None, "not a campsite type"
    if NAME_EXCL.search(t["name"]):
        return None, "tent / walk-in / equestrian / group / cabin type"
    if TEXT_EXCL.search(text):
        return None, "its description bars RVs"
    lim = [int(x) for m in LIMIT.finditer(text) for x in m.groups() if x]
    if lim and min(lim) < 23:
        return None, f"RVs limited to {min(lim)} ft"
    if k in ("w", "ne") and not RVOK.search(text):
        return None, "water-only or primitive type not said to take RVs"
    return k, None


def entrance(lines):
    i = next((j for j, l in enumerate(lines) if re.search(r"(?i)13 years|adult", l)), None)
    v = next((l for l in lines[i:i + 6] if re.match(r"^\$\d|^Free", l)), None) if i is not None else None
    if v is None:
        return None
    if v.startswith("Free"):
        return 0
    return float(re.match(r"\$(\d+(?:\.\d+)?)", v).group(1))


def money(v):
    return f"${v:g}"


WORD = {"ne": "primitive", "w": "water only", "e": "water and electric", "fhu": "full hookups"}
out, flags = [], []
for eid, e in sorted(rows.items()):
    if e.get("state") != "TX" or e.get("ownership") != "state" or e.get("fees"):
        continue
    m = re.search(r"tpwd\.texas\.gov/state-parks/([a-z0-9-]+)", e.get("website") or "")
    if not m:
        continue
    p = pages.get(m.group(1))
    if not p or not p.get("types"):
        flags.append((eid, e["name"], f"no fee page ({m.group(1)})")); continue
    got = {}
    skipped = []
    for t in p["types"]:
        if eid in UNIT and not re.search(UNIT[eid], t.get("name") or ""):
            continue
        k, why = usable(t)
        if k is None:
            if t.get("name"):
                skipped.append(f"{t['name']} ({why})")
            continue
        got.setdefault(k, []).append((t["nightly"], t["name"]))
    if not got:
        flags.append((eid, e["name"], "no RV site type: " + "; ".join(skipped)[:300])); continue
    base_k = next(k for k in ("ne", "w", "e", "fhu") if k in got)
    lo = min(v for v, _ in got[base_k])
    hi = max(v for v, _ in got[base_k])
    sur = {}
    if base_k == "ne" and "w" in got:
        sur["water"] = round(min(v for v, _ in got["w"]) - lo, 2)
    if base_k in ("ne", "w") and "e" in got:
        sur["electric"] = round(min(v for v, _ in got["e"]) - lo, 2)
    if base_k != "fhu" and "fhu" in got:
        sur["full_hookup"] = round(min(v for v, _ in got["fhu"]) - lo, 2)
    parts = []
    for k in ("ne", "w", "e", "fhu"):
        if k in got:
            vs = sorted({v for v, _ in got[k]})
            parts.append(f"{WORD[k]} {money(vs[0]) if len(vs) == 1 else money(vs[0]) + '-' + format(vs[-1], 'g')}")
    ent = entrance(p.get("entrance") or [])
    text = ("A night: " + "; ".join(parts) + "." +
            (f" Plus the park's daily entrance fee, ${ent:g} a person 13 and older (12 and under free)." if ent else
             " Plus the park's daily entrance fee." if ent is None else " No entrance fee.") +
            f" Texas State Parks' fee pages for the park, read {D}.")
    fees = {"nightly_low": int(lo) if lo % 1 == 0 else lo, "nightly_high": int(hi) if hi % 1 == 0 else hi,
            "currency": "USD"}
    if ent is not None:
        fees["entrance"] = {"resident": ent if ent % 1 else int(ent), "nonresident": ent if ent % 1 else int(ent),
                            "per": "person_day"}
    if sur:
        fees["surcharges"] = {k: (int(v) if v % 1 == 0 else v) for k, v in sur.items()}
    fees["checked"] = "2026"
    fees["note"] = text
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"https://tpwd.texas.gov/state-parks/{m.group(1)}/fees-facilities/campsites" +
                          (f" ({UNIT[eid]} types)" if eid in UNIT else "") +
                          f" and .../entrance-fees, read {D} (tx_park_pages_2026-10-12.json)"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "TX findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:40], f["nightly_low"], f["nightly_high"], f.get("surcharges"), (f.get("entrance") or {}).get("resident"))
for fl in flags:
    print("FLAG", *fl)
