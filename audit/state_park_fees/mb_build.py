"""Manitoba Parks findings: every park's campsite fee schedules on manitoba.goingtocamp.com for Tue 2027-07-13 and
Sat 2027-07-17 (gtc_probe.py -> mb_booking_fees_2026-10-12.json), with each schedule's sites' service type and the
longest unit its sites allow, read 2026-10-12; plus the province's park fees page
(https://www.gov.mb.ca/nrnd/parks/park-fees/index.html): 'Nightly Camping Fees: Basic Services $11.55 to $23.65,
Electrical Services $17.85 to $29.95, Electrical/Water Services $21.00 to $31.00, Full Service $25.20 to $27.30', the
'2026 Park Vehicle Permit Fees Includes GST': 'Daily $9.50', 'Casual $16.50 (valid for three consecutive days)', 'Annual
$44.50', and 'Parks Reservation Service: Reservation Fee $10.00'.

    python3 -I mb_build.py OUT

The booking site's prices are the table's (they include 5% GST: $12.60 = $12 x 1.05). The base is the cheapest Basic
(no-hookup) site whose units go to 25 ft or longer, else the cheapest electric site; electric, electric/water and full
service are surcharges on it (electric = the cheaper of electric and electric/water; water = electric/water over
electric alone). Seasonal, group, backcountry and
$0 (host) schedules are left out. A Saturday costs the same everywhere. St. Ambroise Beach is run by a commercial
operator (Surfside Beach; 'Provincial park vehicle permits are not required') and is not priced here."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TUE, SAT = "2027-07-13", "2027-07-17"
FEES = "https://www.gov.mb.ca/nrnd/parks/park-fees/index.html"
PARK = {
    9319: "Terrain de camping Asessippi", 9320: "Terrain de camping de Bakers Narrows", 9323: "Birch Point Campground",
    9324: "Terrain de camping de Birds Hill", 9325: "Terrain de camping de Camp Morton",
    9326: "Clearwater Provincial Park - Campers Cove Campground",
    9327: "Parc provincial du lac Clearwater - Terrain de camping de la baie Pioneer",
    9328: "Parc provincial de Duck Mountain - Terrain de camping des lacs Blue",
    9329: "Parc provincial de Duck Mountain - Terrain de camping de lac Childs",
    9330: "Parc provincial de Duck Mountain - Terrain de camping du lac Wellman",
    9333: "Terrain de camping de Grand Beach", 9337: "Terrain de camping d'Hecla Gull Harbour",
    9338: "Hnausa Beach Campground", 9340: "Terrain de camping de la plage Lundar",
    9341: "Terrain de camping de Manipogo", 9342: "Moose Lake Campground",
    9343: "Parc provincial Nopiming - Terrain de camping du lac Beresford",
    9344: "Parc provincial Nopiming - Terrain de camping du lac Bird",
    9345: "Nopiming Provincial Park - Tulabi Falls Campground", 9347: "Terrain de camping du lac Paint",
    9348: "Terrain de camping de la plage Rainbow", 9349: "Terrain de camping de Rivers",
    9350: "Spruce Woods Provincial Park - Kiche Manitou Campground", 9352: "Terrain de camping de Saint-Malo",
    9353: "Terrain de camping de Stephenfield",
    9354: "Parc provincial de Turtle Mountain - Terrain de camping du lac Adam",
    9356: "Terrain de camping deWatchorn", 9357: "Terrain de camping des chutes Wekusko",
    9359: "Whiteshell Provincial Park - Betula Lake Campground",
    9360: "Parc provincial du Whiteshell - Terrain de camping de Big Whiteshell",
    9361: "Parc provincial du Whiteshell - Terrain de camping du lac Brereton",
    9362: "Parc provincial du Whiteshell - Terrain de camping du lac Caddy",
    9364: "Whiteshell Provincial Park - Nutimik Lake Campground",
    9365: "Parc provincial du Whiteshell - Terrain de camping d'Opapiskaw",
    9366: "Parc provincial du Whiteshell - Terrain de camping des chutes Otter",
    9367: "Parc provincial du Whiteshell - Terrain de camping du lac White",
    9368: "Parc provincial du Whiteshell - Terrain de camping de Falcon Beach",
    9369: "Whiteshell Provincial Park - Falcon Lakeshore Campground",
    9370: "Parc provincial du Whiteshell - Terrain de camping du lac West Hawk",
    9371: "Parc  provincial de Turtle Mountain - Terrain de camping du lac William",
    9372: "Terrain de camping de la plage Winnipeg",
}
probe = json.load(open(os.path.join(HERE, "mb_booking_fees_2026-10-12.json"), encoding="utf-8"))
parks = {p["park"]: p for p in probe["parks"]}
WORD = {"ne": "basic (no hookups)", "e": "electric", "ew": "electric and water", "fhu": "full service"}


def longest(eq):
    v = [int(m.group(1)) for x in eq if (m := re.match(r"(\d+)ft$", x))]
    return 41 if any(x.startswith("Over") for x in eq) else max(v, default=0)


def kind(services):
    k = max(services, key=services.get)
    t = (re.search(r"Service Type=([\w/]+)", k) or [None, "Basic"])[1]
    return {"Basic": "ne", "Electric": "e", "Electric/Water": "ew", "Full": "fhu"}.get(t)


def nightly(s, d):
    f = s["fees"].get(d)
    return sum(x[0] for x in f) if isinstance(f, list) and f else None


def money(v):
    return f"${v:.2f}"


out, flags = [], []
for eid in sorted(i for i, e in rows.items() if e.get("state") == "MB" and e.get("ownership") == "provincial"):
    e = rows[eid]
    if e.get("fees"):
        continue
    if eid not in PARK:
        flags.append((eid, e["name"], "not on the booking site")); continue
    p = parks[PARK[eid]]
    got = {}
    for s in p["schedules"]:
        if s["category"] != "Campsite":
            continue
        v, sat = nightly(s, TUE), nightly(s, SAT)
        if not v:                                   # $0: a host's site
            continue
        assert v == sat, (eid, s["feeScheduleId"], v, sat)
        k = kind(s["services"])
        if k is None:
            continue
        got.setdefault(k, []).append((v, s["n"], longest(s["equipment"])))
    fit = {k: [x for x in xs if x[2] >= 25] for k, xs in got.items()}
    fit = {k: xs for k, xs in fit.items() if xs}
    if not fit:
        flags.append((eid, e["name"], f"no schedule takes a 23-ft rig: {got}")); continue
    base_k = next(k for k in ("ne", "e", "ew", "fhu") if k in fit)
    base = min(v for v, _, _ in fit[base_k])
    hi = max(v for v, _, _ in fit[base_k])
    sur = {}
    elec = [v for k in ("e", "ew") for v, _, _ in fit.get(k, []) if k != base_k]
    if base_k == "ne" and elec:
        sur["electric"] = round(min(elec) - base, 2)
    e_only, ew = [v for v, _, _ in fit.get("e", [])], [v for v, _, _ in fit.get("ew", [])]
    if e_only and ew and base_k in ("ne", "e") and min(ew) > min(e_only):
        sur["water"] = round(min(ew) - min(e_only), 2)       # electric/water over electric alone
    if "fhu" in fit and base_k != "fhu":
        sur["full_hookup"] = round(min(v for v, _, _ in fit["fhu"]) - base, 2)
    sur["weekend"] = 0
    parts = []
    for k in ("ne", "e", "ew", "fhu"):
        if k in fit:
            vals = sorted({v for v, _, _ in fit[k]})
            parts.append(f"{WORD[k]} {' / '.join(money(v) for v in vals)}")
    text = ("A night: " + "; ".join(parts) + ", GST included, the same every night of the week." +
            (" (The basic sites here take smaller units only.)" if "ne" in got and base_k != "ne" else "") +
            " Plus a $10 reservation fee per booking, and each vehicle needs a provincial park vehicle permit ($9.50 a "
            f"day, $16.50 for three days, $44.50 a year). Manitoba Parks' booking site (July 2027 nights) and 2026 fees, "
            f"read {D}.")
    fees = {"nightly_low": base, "nightly_high": hi, "currency": "CAD", "reservation_fee": 10,
            "entrance": {"resident": 9.5, "nonresident": 9.5, "per": "vehicle_day"}, "surcharges": sur,
            "checked": "2026", "note": text}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"manitoba.goingtocamp.com/api/resource/feeDetails ({p['park']}, every campsite fee schedule, "
                          f"{TUE} and {SAT}) + {FEES} (2026 nightly camping fee ranges, vehicle permits, $10.00 reservation "
                          f"fee), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "MB findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:42], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
