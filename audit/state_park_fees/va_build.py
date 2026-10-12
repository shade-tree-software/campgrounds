"""VA findings: DCR's camping fee table + the booking site's site types, read 2026-10-12.

    python3 -I va_build.py OUT

va_fee_table_2026-10-12.json is https://www.dcr.virginia.gov/state-parks/camping-fees ('Effective 5/12/2025'): each park's
site types with a Virginia-resident and a non-resident nightly price. Which of those types an RV can use comes from
reservevaparks.com's place search (rdr_place.py -> va_place_types_2026-10-12.json: each campground's site types and the
longest vehicle each takes): at several parks DCR's 'Standard' row is the booking site's 'Tent Only-No Hookups'. The
booking site's own prices (rdr_rates.py -> va_booking_rates_2026-10-12.jsonl, 20 parks before its host started answering
403) are the check: every sampled price must be on the park's table, and a Saturday cost the same as a Tuesday everywhere.
The base is the cheapest site EKKO fits (23 ft): a no-hookup type whose longest site is shorter goes in the note.
The $5 transaction fee is the state:VA registry row's."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
TABLE = json.load(open(os.path.join(HERE, 'va_fee_table_2026-10-12.json'), encoding='utf-8'))["parks"]
PLACES = json.load(open(os.path.join(HERE, 'va_place_types_2026-10-12.json'), encoding='utf-8'))
SAMPLE = [json.loads(l) for l in open(os.path.join(HERE, 'va_booking_rates_2026-10-12.jsonl')) if '"error"' not in l]
D = "2026-10-12"
FEES = "https://www.dcr.virginia.gov/state-parks/camping-fees"
# id: (PlaceId, campground name filter or None)
M = {243: (26, None), 251: (34, None), 252: (1, None), 253: (13, None), 257: (8, None), 529: (11, None), 537: (19, None),
     539: (5, None), 552: (22, "Lovers Leap"), 820: (22, "Cove View"), 591: (25, None), 617: (2, None), 618: (16, None),
     625: (24, None), 626: (35, None), 639: (10, None), 647: (7, None), 668: (28, None), 669: (17, None), 694: (14, None),
     818: (6, None), 819: (15, None), 821: (30, None), 822: (33, None)}
FIT = 23


def type_kind(t):
    if re.search(r"(?i)tent|horse|group|yurt|bunk|cabin", t):
        return None
    if re.search(r"(?i)sewer", t):
        return "fhu"
    if re.search(r"(?i)electric", t):
        return "e"
    if re.search(r"(?i)no hookups", t):
        return "std"
    return None


def row_kind(label):
    if re.search(r"(?i)group|buddy|equest|primitive|stall|paddle", label):   # 'Group Camping (Standard per site ...)'
        return None
    if re.search(r"(?i)sewer", label):
        return "fhu"
    if re.search(r"(?i)electric and water", label):
        return "e"
    if re.search(r"(?i)standard", label):
        return "std"
    return None


def money(v):
    return int(v) if float(v).is_integer() else v


def rng(vals):
    lo, hi = min(vals), max(vals)
    return f"${money(lo)}" if lo == hi else f"${money(lo)}-{money(hi)}"


WORD = {"std": "without hookups", "e": "with electric and water", "fhu": "with full hookups"}
out = []
for eid, (pid, fac) in sorted(M.items()):
    place = PLACES[str(pid)]
    park = place["name"]
    table = TABLE[park]
    kinds, short = {}, {}
    for f in place["facilities"].values():
        if fac and fac.lower() not in f["name"].lower():
            continue
        for t, (ln, _) in f["units"].items():
            k = type_kind(t)
            if k:
                kinds.setdefault(k, []).append(ln or 0)
    if "std" in kinds and 0 < max(kinds["std"]) < FIT:
        short["std"] = max(kinds.pop("std"))
    res, nonres = {}, {}
    for label, r, n in table:
        k = row_kind(label)
        if k:
            res.setdefault(k, set()).add(float(r.strip("$")))
            nonres.setdefault(k, set()).add(float(n.strip("$")))
    sampled = {}
    for s in SAMPLE:
        if s["placeId"] == pid and (not fac or fac.lower() in s["facility"].lower()):
            k = type_kind(s["unitType"])
            if k and s.get("rate"):
                sampled.setdefault(k, set()).add(float(s["rate"]))
    for k, v in sampled.items():           # the booking site's price must be on the park's table
        if k in res and not v <= res[k] and not (k == "e" and v <= res.get("fhu", set())):
            raise SystemExit(f"{eid} {park}: booking {k} {sorted(v)} not on the table {sorted(res[k])}")
    price = {}
    for k in kinds:
        if k in res:
            price[k] = res[k]
        elif k in sampled:            # Kiptopeke's electric-and-water sites: not a row of their own on the table
            price[k] = sampled[k]
    if not price:
        print("no RV price", eid, park, kinds, table)
        continue
    base_kind = next(k for k in ("std", "e", "fhu") if k in price)
    base = min(price[base_kind])
    s = {}
    if base_kind == "std" and "e" in price:
        s["electric"] = money(min(price["e"]) - base)
    if "fhu" in price and base_kind != "fhu":
        s["full_hookup"] = money(min(price["fhu"]) - base)
    s["weekend"] = 0
    parts = [f"{rng(price[k])} a night for a site {WORD[k]}" if i == 0 else f"{rng(price[k])} {WORD[k]}"
             for i, k in enumerate(k for k in ("std", "e", "fhu") if k in price)]
    text = "; ".join(parts) + " (Virginia residents)"
    have = [k for k in ("std", "e", "fhu") if k in price]
    nr = [k for k in have if k in nonres]
    if nr == have:
        text += "; non-residents " + " / ".join(rng(nonres[k]) for k in nr) + "."
    elif nr:
        text += "; non-residents " + ", ".join(f"{rng(nonres[k])} {WORD[k]}" for k in nr) + "."
    else:
        text += "."
    only = [re.search(r"\((site[^)]*only)\)", label) for label, _, _ in table]
    only = [m.group(1) for m in only if m]
    if only:
        text += f" The full-hookup price is for {only[0]}." if "fhu" in price else ""
    if "e" in price and "e" not in res:
        text += " (DCR's table gives no separate electric-and-water price here; the booking site charges $43, the full-hookup price.)"
    if "std" in short:
        text += (f" Sites without hookups are {rng(res['std'])} but take rigs only to {short['std']} ft." if "std" in res else "")
    tent = res.get("std") if "std" not in kinds and "std" not in short else None
    if tent:
        text += f" The {rng(tent)} sites without hookups are tent-only."
    text += f" The same price every night of the week. Plus tax and a $5 transaction fee. DCR's fee table (effective 2025-05-12), read {D}."
    nr_amt = None
    if base_kind in nonres:
        nr_amt = min(nonres[base_kind]) - base
    elif base_kind == "e" and "fhu" in nonres:
        nr_amt = min(nonres["fhu"]) - base
    fees = {"nightly_low": money(base), "nightly_high": money(base), "currency": "USD"}
    if nr_amt:
        fees["nonresident"] = {"type": "surcharge", "amount": money(nr_amt), "per": "night"}
    fees["surcharges"] = s
    fees["checked"] = "2026"
    fees["note"] = text
    out.append({"id": eid, "name": rows[eid]["name"], "fees": fees,
                "source": f"{FEES} ({park}, effective 5/12/2025, read {D}) + reservevaparks.com PlaceId {pid} (site types per "
                          f"campground; sampled prices for 2027-06-15 and 2027-06-19 where its host answered, read {D})"})
# Breaks Interstate Park: the Virginia-Kentucky commission's, not DCR's (its own Firefly booking; policy_ref "none" in
# corrections_2026-10-12.json). Its page's rates replaced 2024's $22 / $31 / $37 by the 2026-07-10 Wayback copy.
out.append({"id": 1104, "name": rows[1104]["name"], "fees": {
    "nightly_low": 27, "nightly_high": 27, "currency": "USD", "surcharges": {"electric": 10, "full_hookup": 14},
    "checked": "2026",
    "note": ("$27 a night for a primitive site, $37 with electric and water, $41 with electric, water and sewer, plus tax; "
             "group sites $134. A cancelled reservation costs $10 a site. The park's campground page, read " + D +
             " (the same rates were on it by July 2026; 2024's were $22, $31 and $37).")},
    "source": ("https://www.breakspark.com/campground ('Primitive Sites Nightly: $27.00 plus tax', 'Electric and Water Sites "
               "Nightly: $37.00', 'Electric Service, Water, and Sewer sites Nightly: $41.00', read " + D + "; Wayback "
               "20260710134807 shows the same, 20240727221449 showed $22 / $31 / $37)")})
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(out), "VA findings")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:30], f["nightly_low"], f.get("nonresident", {}).get("amount"), f["surcharges"], "|", f["note"][:200])
