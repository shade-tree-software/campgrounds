"""Oklahoma State Parks findings: okstateparks.reserveamerica.com, every park's sites (ra_list.py ->
ok_sites_2026-10-12.json) and each loop and site type's price for Tue 2027-06-15 and Sat 2027-06-19, with the site
page's hookups and max vehicle length (ra_loop_types.py -> ok_booking_rates_2026-10-12.jsonl), read 2026-10-12.

    python3 -I ok_build.py OUT

Oklahoma publishes no camping rate table; the booking site is the source. Every RV site there has electricity (a
'Semi Modern' site has water and electric, 'Modern' adds sewer, 'Premium' sites are dearer ones of either kind), so an
entry's base is its cheapest non-premium RV site a 23-ft rig fits; nightly_low / nightly_high span those across its
loops. Full hookups and premium sites are add-ons on that base, and Saturday's difference is the weekend add-on.
TravelOK's reservation guidelines: 'A 3% service fee will be applied when paying by credit card or debit card'; 'One
parking pass to this state park is included with a completed reservation'; seniors 62+ and military get 10% off the
base rate. No reservation fee. Overflow, group, equestrian, tent and cabin types are left out."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TUE, SAT = "6/15/2027", "6/19/2027"
GUIDE = "https://www.travelok.com/state-parks/reservation-guidelines"
# entry -> (parkId, loops or None for the whole park)
PARK = {
    6609: ("1260032", ("Deer Run", "Eagles Nest", "Blackjack")),
    6597: ("1260041", ("Buzzard Roost",)), 6603: ("1260041", ("Cedar Cove",)), 6592: ("1260041", ("Marietta Landing",)),
    6596: ("1260041", ("Martins Landing",)), 6595: ("1260041", ("Rock Tower",)), 6610: ("1260041", ("Tipps Point",)),
    6575: ("1260041", ("Elephant Rock",)), 673: ("1260041", None),
    6600: ("1260047", ("Victor Landing",)), 6602: ("1260047", ("Wards",)), 6622: ("1260047", ("Quarry Island",)),
    6608: ("1260054", ("Buster",)), 6599: ("1260054", ("Potapo",)),
    6579: ("1260011", ("Cherokee", "Choctaw", "Seminole")),
    6606: ("1260011", ("Sequoyah Bay Attakullakulla", "Sequoyah Bay Hulbutta Micco", "Sequoyah Bay Payamataha")),
    6588: ("1260052", ("Dog Wood",)), 6577: ("1260052", None), 6581: ("1260038", None),
}
NOT_PARK_LOOPS = ("ATV Area",)         # Lake Murray's off-highway-vehicle camp is not one of the lake campgrounds
recs = [json.loads(l) for l in open(os.path.join(HERE, "ok_booking_rates_2026-10-12.jsonl"), encoding="utf-8")]


def price(r):
    # '$28.00 Per Night , $196.00 Per Week', or on some nights 'Sat Jun 19 2027 : $46.00'
    m = re.search(r"\$([\d,]+\.\d\d)", r.get("price") or "")
    return float(m.group(1).replace(",", "")) if m else None


def length(r):
    v = r.get("Max Vehicle Length") or ""
    m = re.match(r"(\d+)", v) or re.match(r"(\d+)", (r.get("cells") or ["", "", "", ""])[3] if len(r.get("cells") or []) > 3 else "")
    return int(m.group(1)) if m else None


def kind(r):
    # Every Oklahoma RV site type has electricity ('Semi Modern' = water and electric, 'Modern' adds sewer); a few
    # site pages leave the electricity field empty (Robbers Cave), so only sewer decides.
    return "fhu" if r.get("Sewer Hookup") == "Y" else "e"


def money(v):
    return f"${v:g}"


by_pid = collections.defaultdict(list)
for e in rows.values():
    if e.get("state") == "OK" and e.get("ownership") == "state" and not e.get("fees"):
        m = re.search(r"parkId=(\d+)", e.get("website") or "")
        if e["id"] in PARK:
            by_pid[PARK[e["id"]][0]].append(e)
        elif m:
            by_pid[m.group(1)].append(e)
out, flags = [], []
for pid, ents in sorted(by_pid.items()):
    for e in ents:
        loops = PARK.get(e["id"], (pid, None))[1]
        sel = [r for r in recs if r["parkId"] == pid and price(r) is not None and not re.search(r"(?i)overflow", r["type"])
               and r["loop"] not in NOT_PARK_LOOPS and (loops is None or r["loop"] in loops)
               and (length(r) is None or length(r) >= 23)]
        tue = [r for r in sel if r["date"] == TUE]
        if not tue:
            flags.append((e["id"], e["name"], f"no priced RV site at park {pid} loops {loops}")); continue
        groups = collections.defaultdict(list)          # (kind, premium) -> Tuesday prices
        for r in tue:
            groups[(kind(r), "Premium" in r["type"])].append(price(r))
        base_keys = ([k for k in (("e", False), ("ne", False)) if k in groups] or [k for k in groups if not k[1]]
                     or list(groups))
        base_vals = [v for k in base_keys for v in groups[k]]
        lo, hi = min(base_vals), max(base_vals)
        sur = {}
        fhu = groups.get(("fhu", False)) or (groups.get(("fhu", True)) if ("fhu", False) not in groups else None)
        if fhu and ("fhu", False) not in base_keys and ("fhu", True) not in base_keys:
            sur["full_hookup"] = round(min(fhu) - lo, 2)
        main = base_keys[0][0]
        prem = groups.get((main, True)) if not base_keys[0][1] else None
        if prem and min(prem) > lo:
            sur["premium_site"] = round(min(prem) - lo, 2)
        diffs = []
        for r in sel:
            if r["date"] == SAT:
                t = next((price(x) for x in tue if x["site"] == r["site"]), None)
                if t is not None:
                    diffs.append(round(price(r) - t, 2))
        base_diffs = []
        for r in sel:
            if r["date"] == SAT and (kind(r), "Premium" in r["type"]) in base_keys:
                t = next((price(x) for x in tue if x["site"] == r["site"]), None)
                if t is not None:
                    base_diffs.append(round(price(r) - t, 2))
        if base_diffs and len(set(base_diffs)) == 1:
            sur["weekend"] = base_diffs[0]           # the base site's Saturday; other types' are in the note
        words = {("e", False): "water and electric", ("ne", False): "no hookups", ("fhu", False): "full hookups",
                 ("e", True): "premium water and electric", ("fhu", True): "premium full hookups",
                 ("ne", True): "premium, no hookups"}
        parts = []
        for k in (("ne", False), ("e", False), ("fhu", False), ("e", True), ("fhu", True), ("ne", True)):
            if k in groups:
                vs = sorted(set(groups[k]))
                parts.append(f"{words[k]} {money(vs[0]) if len(vs) == 1 else money(vs[0]) + '-' + format(vs[-1], 'g')}")
        wk = (f" Saturday +{money(diffs[0])}." if diffs and len(set(diffs)) == 1 and diffs[0] else
              " The same on a Saturday." if diffs and set(diffs) == {0} else
              (" Saturday " + ", ".join(sorted({f"+{money(x)}" for x in diffs})) + " depending on the site." if diffs else ""))
        text = ("A night (weekdays): " + "; ".join(parts) + "." + wk +
                " Plus tax and a 3% card service fee; no reservation fee, and the reservation includes one vehicle's "
                "parking pass. Seniors 62+ and military get 10% off the base rate. Oklahoma State Parks' booking site "
                f"(June 2027 nights), read {D}.")
        fees = {"nightly_low": lo, "nightly_high": hi, "currency": "USD", "surcharges": sur, "checked": "2026",
                "note": text}
        for k in ("nightly_low", "nightly_high"):
            fees[k] = int(fees[k]) if float(fees[k]).is_integer() else fees[k]
        out.append({"id": e["id"], "name": e["name"], "fees": fees,
                    "source": f"okstateparks.reserveamerica.com parkId {pid}" + (f" ({', '.join(loops)})" if loops else "") +
                              f": each loop and RV site type's 1-night price for {TUE} and {SAT} with the site pages' "
                              f"hookups (ok_booking_rates_2026-10-12.jsonl) + {GUIDE}, read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "OK findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:44], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
