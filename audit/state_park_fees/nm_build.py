"""New Mexico State Parks findings, read 2026-10-12.

    python3 -I nm_build.py OUT

The fee schedule in force since 2025-01-01 (emnrd.nm.gov/spd 'Fees & Permits' page and its 'Parks Fee Changes' flier):
camping 'Per Vehicle, Walk-In, or Bicycle Per Night', New Mexico residents $10 at a primitive site and $15 at a
developed one, non-residents $15 and $20; 'Water Hook-Up - Per Day (only at sites with water) $5', 'Electric Hook-Up
... $10', 'Sewer Hook-Up ... $5', charged 'for sites with utilities available, regardless of whether the utility is
used' (the FAQ: 'Sites that share utilities would not be charged utility fees'). ReserveAmerica's reservation fee is
'$3.50 per night, $10.00 max. per reservation' ('These fees are separate and do not go to New Mexico State Parks').

The booking site (newmexicostateparks.reserveamerica.com, classic ReserveAmerica, contract NM) lists every site of each
park (nm_sites_2026-10-12.json, ra_sites.py), and ra_sample.py read every one for Tue 2027-06-15
(nm_booking_rates_2026-10-12.jsonl): a reservable site quotes the resident price and the non-resident one, $5 more, and
both are the schedule's sums ($15 developed, $20 with water, $25 with electric, $30 with both, $35 full hookups); a
first-come site prints 'No pricing information available' and pays the same schedule. A Saturday sample, one site per
loop on 2027-06-19 (nm_booking_rates_saturday_2026-10-12.jsonl), prices the same as the Tuesday.

Each entry: base = the cheapest kind of site in its loops that a 23-ft rig fits (Max Vehicle Length; blank = unknown),
priced from the schedule by the site's hookups; water, electric and sewer add-ons where its sites have them;
non-residents +$5 a night on the base; reservation fee $3.50 (a night, at most $10; none where every site is first come,
first served). The park-wide 'Primitive Camping' listing ($10: shore and beach camping, no sites) and group sites are
left out. No entrance fee is recorded: camping is charged per vehicle, and nothing says a camping vehicle also pays the
$5 / $10 day-use fee."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
FEES = "https://www.emnrd.nm.gov/spd/fees-permits/"
NR = {"type": "surcharge", "amount": 5, "per": "night", "applies_to": "base"}
SKIP_LOOP = re.compile(r"(?i)group|shelter|corral|day use")
# entry -> (parkId, its loops (regex) or None for the whole park)
ENTRY = {
    7931: ("430002", None), 7932: ("430039", None), 7933: ("430026", None), 7934: ("430037", None),
    7935: ("430005", None), 7937: ("430010", r"^LIONS BEACH"), 7938: ("430003", r"(?i)^(Appaloosa|STALLION)"),
    7939: ("430027", r"(?i)^Rocky Point"), 7940: ("430032", None), 7941: ("430016", None), 7942: ("430001", None),
    7943: ("430027", r"(?i)^Juniper"), 7944: ("430021", None), 7945: ("430030", None), 7947: ("430012", None),
    7948: ("430006", None), 7949: ("430031", None), 7950: ("430038", None), 7952: ("430022", None),
    7953: ("430010", r"^SOUTH MONTICELLO"), 7954: ("430034", None), 7956: ("430020", r"^PINE "),
    7957: ("430015", None), 7958: ("430020", r"^COTTONWOOD"), 7959: ("430018", None), 7960: ("430013", None),
    7962: ("430007", None), 7963: ("430010", r"^DESERT COVE"), 7964: ("430008", None),
    7965: ("430023", r"^(MAVERICK|PONDEROSA)"), 7966: ("430009", None), 7969: ("430010", r"^QUAIL RUN"),
    7970: ("430011", None), 7973: ("430014", None), 7978: ("430010", r"^LOWER RIDGE ROAD"),
    7980: ("431500", r"(?i)^Mora"), 7982: ("430020", r"^CRUSHER HOLE"), 7986: ("431500", r"(?i)^Terrero"),
}
WORD = {(0, 0, 0): "developed", (0, 1, 0): "water", (1, 0, 0): "electric", (1, 1, 0): "water and electric",
        (1, 1, 1): "full hookups", (0, 1, 1): "water and sewer", (1, 0, 1): "electric and sewer", (0, 0, 1): "sewer"}


def money(p):
    m = re.search(r"\$([\d,]+\.\d\d)", p or "")
    return float(m.group(1).replace(",", "")) if m else None


def num(v):
    return int(v) if float(v).is_integer() else v


sites = {}   # (parkId, site) -> record; a later read of the same site replaces an earlier one
for line in open(os.path.join(HERE, "nm_booking_rates_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    sites[(r["park"].split("_")[1].split(".")[0], r["site"])] = r
sat = {}
for line in open(os.path.join(HERE, "nm_booking_rates_saturday_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    sat[(r["park"].split("_")[1].split(".")[0], r["site"])] = r
sat_diff = {round(money(r["price"]) - money(sites[k]["price"]), 2) for k, r in sat.items()
            if money(r.get("price")) is not None and money((sites.get(k) or {}).get("price")) is not None}
primitive = {p for (p, _), r in sites.items() if r.get("Type") == "Primitive Camping" and money(r.get("price")) == 10}
# Per-entry facts the booking site alone doesn't give (the park pages, read 2026-10-12).
EXTRA = {
    7943: " First come, first served: the park's page lists Juniper's sites among its 'Non-Reservation Sites', and the "
          "booking site shows them 'Not available online'.",
    7964: " The booking site lists all 19 Lakeview sites with 20/30/50-amp electric and charges the electric fee; the park's "
          "own page still says 'No hook-ups'.",
    7980: " The booking site lists Mora's 10 sites but takes no booking for them ('Not available online'), while the "
          "park's page says 'Mora by Reservation only'; Terrero's sites, with no hookups either, are quoted at $15.",
    7986: " The booking site lists no hookups at Terrero's sites, and the park's page counts them among its 33 primitive "
          "sites.",
}
out, flags, odd = [], [], []
for eid, (pid, loops) in sorted(ENTRY.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    mine = [r for (p, _), r in sites.items() if p == pid and r.get("Type") == "Camping" and
            not SKIP_LOOP.search(r.get("loop") or "") and not SKIP_LOOP.search(r.get("site") or "") and
            (not loops or re.search(loops, r.get("loop") or ""))]
    if not mine:
        flags.append((eid, e["name"], f"no sites in {pid} {loops}"))
        continue
    groups = {}   # the site's hookups -> what it pays for, sites, quoted sites, fits, prices, water shared
    for r in mine:
        k = (int(bool(r.get("Electricity Hookup"))), int(r.get("Water Hookup") == "Y"), int(r.get("Sewer Hookup") == "Y"))
        sched = 15 + 10 * k[0] + 5 * k[1] + 5 * k[2]
        q = money(r.get("price"))
        charged, shared = k, False
        if q is not None and q != sched:
            if k[1] and q == sched - 5:     # a shared spigot: 'Sites that share utilities would not be charged'
                charged, shared = (k[0], 0, k[2]), True
            else:
                odd.append((eid, r["site"], r.get("loop"), k, q))
        g = groups.setdefault(k, {"charged": charged, "n": 0, "quoted": 0, "fits": False, "prices": set(), "shared": False})
        g["n"] += 1
        g["quoted"] += q is not None
        g["prices"].add(q if q is not None else sched)
        g["shared"] |= shared
        if shared:
            g["charged"] = charged
        ln = r.get("Max Vehicle Length")
        g["fits"] |= ln in (None, "") or (ln.isdigit() and int(ln) >= 23)
    # A kind of site counts when it is reservable or there are 3 or more of it (Juniper's 2 first-come water and
    # electric sites include the park's one accessible hookup site).
    counted = {k: g for k, g in groups.items() if g["fits"] and (g["quoted"] or g["n"] >= 3)}
    if not counted:
        flags.append((eid, e["name"], f"no site a 23-ft rig fits: { {k: g['n'] for k, g in groups.items()} }"))
        continue
    base = min(counted, key=lambda k: min(counted[k]["prices"]))
    price = min(counted[base]["prices"])
    bc = counted[base]["charged"]
    sur = {"weekend": 0} if sat_diff == {0} else {}
    for i, key, amt in ((0, "electric", 10), (1, "water", 5), (2, "sewer", 5)):
        if not bc[i] and any(g["charged"][i] for g in counted.values()):
            sur[key] = amt
    for k, g in counted.items():
        want = price + sum(sur.get(key, 0) for i, key in enumerate(("electric", "water", "sewer"))
                           if g["charged"][i] and not bc[i])
        if g["prices"] != {want}:
            flags.append((eid, e["name"], f"{WORD[k]} sites priced {sorted(g['prices'])}, the add-ons give {want}"))
    reservable = any(g["quoted"] for g in groups.values())
    order = sorted(counted, key=lambda k: min(counted[k]["prices"]))
    short = [WORD[k] for k in sorted(groups) if not groups[k]["fits"]]
    text = ("June nights for New Mexico residents: " +
            "; ".join(f"{WORD[k]} ${num(min(counted[k]['prices']))}" for k in order) + "." +
            (" The hookup sites share water, so they pay no water fee." if any(g["shared"] for g in counted.values())
             else "") + " Non-residents pay $5 more." +
            (f" (The {' and '.join(short)} sites here are too short for a 23-ft rig.)" if short else "") +
            (" Primitive shore camping in the park is $10 ($15 non-residents)." if pid in primitive and not loops else "") +
            (" Reservations add ReserveAmerica's $3.50 a night, at most $10." if reservable else "") +
            EXTRA.get(eid, "") +
            " New Mexico State Parks' fee schedule ($15 a developed site, plus $5 for water, $10 electric and $5 sewer "
            f"where a site has them) and its booking site's quotes for June 2027, read {D}.")
    fees = {"nightly_low": num(price), "nightly_high": num(price), "currency": "USD", "nonresident": NR,
            "surcharges": sur, "checked": "2026", "note": text}
    if reservable:
        fees["reservation_fee"] = 3.5
    names = sorted({r.get("loop") or "" for r in mine} - {""})
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{FEES} (fee schedule) + newmexicostateparks.reserveamerica.com parkId {pid} "
                          f"({', '.join(names) or 'all loops'}): every site's hookups, length and 1-night quote for "
                          f"2027-06-15 (nm_booking_rates_2026-10-12.jsonl), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NM findings;", len(flags), "flagged; Saturday-Tuesday differences:", sorted(sat_diff))
print("quotes off the schedule:", odd)
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:50], f["nightly_low"], f["surcharges"], f.get("reservation_fee"))
for fl in flags:
    print("FLAG", *fl)
