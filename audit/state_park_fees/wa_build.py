"""Washington State Parks findings: every park's campsite fee schedules on washington.goingtocamp.com for Tue 2027-06-15
and Sat 2027-06-19 (gtc_probe.py -> wa_booking_fees_2026-10-12.json), with each schedule's sites' service type, maps
and the longest unit its sites allow, read 2026-10-12; plus the agency's fees page (wa_fee_pages_2026-10-12.txt):
peak season (May 15 - Sept. 15) 'Standard campsites $31 - $43', 'Partial utility campsites $41 - $51', 'Full-utility
campsites $46 - $56'; shoulder (April 1 - May 14 and Sept. 16 - Oct. 31) $23-35 / $35-46 / $41-51; winter $23 / $35 /
$41; 'Sales and lodging tax (where applicable) are included in all fees listed.'

    python3 -I wa_build.py OUT

The booking site prices each site in one of three tiers ($31 / $37 / $43 standard, $41 / $46 / $51 with water and
electric, $46 / $51 / $56 full hookups), the same on a Saturday. The base is the cheapest primitive drive-in or standard
(no-hookup) site whose units go to 25 ft or longer, else the cheapest hookup site; nightly_high is the dearest of that kind; electric
(water and electric, or electric alone), water (electric and water over electric alone) and full hookups are add-ons
on the base. Walk-in and hiker/biker sites, schedules whose sites take no RV or trailer, and schedules on
the overflow or host-site maps alone are left out. An entry named for one campground of a park takes only the
schedules on its map. The reservation fee and the non-resident fee are on the state:WA registry row."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TUE, SAT = "2027-06-15", "2027-06-19"
FEES = "https://parks.wa.gov/passes-permits/fees"
# entry -> (booking-site park, the entry's maps or None for the whole park)
PARK = {
    294: ("Deception Pass State Park", None), 10369: ("Cape Disappointment State Park", None),
    10370: ("Seaquest State Park", None), 10371: ("Paradise Point State Park", None),
    10372: ("Battle Ground Lake State Park", None),
    10373: ("Beacon Rock State Park", {"Woodard Creek Campground"}), 10374: ("Maryhill State Park", None),
    10375: ("Brooks Memorial State Park", None), 10376: ("Columbia Hills State Park", None),
    10377: ("Lewis and Clark Trail State Park (SE Washington)", None), 10378: ("Fields Spring State Park", None),
    10379: ("Grayland Beach State Park", None), 10380: ("Pacific Beach State Park", None),
    10381: ("Ocean City State Park", None), 10382: ("Schafer State Park", None), 10383: ("Twin Harbors State Park", None),
    10384: ("Lake Sylvia State Park", None), 10385: ("Ike Kinswa State Park", None),
    10386: ("Millersylvania State Park", None), 10387: ("Lewis and Clark State Park (SW Washington)", None),
    10389: ("Rainbow Falls State Park", None), 10391: ("Joemma Beach", None),
    10392: ("Yakima Sportsman State Park", None), 10393: ("Lake Easton State Park", None),
    10397: ("Wanapum State Park", None), 10398: ("Potholes State Park", None), 10400: ("Bogachiel State Park", None),
    10402: ("Fort Worden State Park", {"Beach Campground"}), 10403: ("Dosewallips State Park", None),
    10404: ("Dash Point State Park", None), 10405: ("Fort Casey State Park", None), 10406: ("Belfair State Park", None),
    10407: ("Manchester State Park", None), 10408: ("Fort Flagler State Park", None),
    10409: ("Fort Worden State Park", {"Upper Forest Campground"}), 10410: ("Kanaskat-Palmer State Park", None),
    10411: ("Sequim Bay State Park", None), 10412: ("Kitsap Memorial State Park", None),
    10414: ("Scenic Beach State Park", None), 10415: ("Potlatch State Park", None), 10416: ("Illahee State Park", None),
    10417: ("Fort Townsend State Park", None), 10418: ("Jarrell Cove State Park", None),
    10419: ("Twanoh State Park", None), 10420: ("Camano Island State Park", None),
    10421: ("Penrose Point State Park", None), 10422: ("Wenatchee Confluence State Park", None),
    10423: ("Lincoln Rock State Park", None), 10424: ("Lake Wenatchee State Park", None),
    10425: ("Daroga State Park", None), 10426: ("Lake Chelan State Park", None),
    10428: ("Twenty-Five Mile Creek State Park", None),
    10429: ("Steamboat Rock State Park", {"Bay Loop Campground", "Cove Loop Campground", "Dune Loop Campground",
                                          "Sage Loop Campground"}),
    10431: ("Sun Lakes State Park", None), 10432: ("Bridgeport State Park", None), 10433: ("Alta Lake State Park", None),
    10437: ("Riverside State Park - Bowl and Pitcher", None), 10438: ("Mount Spokane State Park", None),
    10439: ("Bay View State Park", None), 10440: ("Rasar State Park", None), 10441: ("Birch Bay State Park", None),
    10442: ("Larrabee State Park", None), 10443: ("Fort Ebey State Park", None), 10444: ("Moran State Park", None),
    10445: ("Spencer Spit State Park", None), 10446: ("Pearrygin Lake State Park", None),
    10447: ("Curlew Lake State Park", None), 10448: ("Conconully State Park", None),
}
probe = json.load(open(os.path.join(HERE, "wa_booking_fees_2026-10-12.json"), encoding="utf-8"))
parks = {p["park"]: p for p in probe["parks"]}
KIND = {"Primitive With Vehicle": "pv", "Standard - No Hook-ups": "ne", "Electric Hook-ups": "e", "Electrical Water Hook-up": "ew",
        "Electrical Water Sewer Hook-up": "fhu"}
WORD = {"pv": "primitive drive-in (no flush toilets)", "ne": "standard (no hookups)", "e": "electric", "ew": "water and electric", "fhu": "full hookups"}
SIDE = {"Overflow", "Host Sites", "?"}


def longest(eq):
    v = [int(m.group(1)) for x in eq if (m := re.search(r"RV/Trailer up to (\d+)", x))]
    return 41 if any(re.search(r"RV/Trailer over 40", x) for x in eq) else max(v, default=0)


def kind(services):
    k = max(services, key=services.get)
    t = (re.search(r"Service Type=([^,]+)", k) or [None, ""])[1].strip()
    return KIND.get(t)


def nightly(s, d):
    f = s["fees"].get(d)
    return sum(x[0] for x in f) if isinstance(f, list) and f else None


def num(v):
    return int(v) if float(v).is_integer() else v


def span(vs):
    lo, hi = min(vs), max(vs)
    return f"${num(lo)}" if lo == hi else f"${num(lo)}-{num(hi)}"


out, flags = [], []
for eid, (pname, maps) in sorted(PARK.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    p = parks[pname]
    got, short = {}, set()
    for s in p["schedules"]:
        if s["category"] != "Campsite":
            continue
        ms = set(s["maps"])
        if ms <= SIDE:                                  # overflow or host sites only
            continue
        if maps and not ms & maps:
            continue
        v, sat = nightly(s, TUE), nightly(s, SAT)
        if not v:
            continue
        assert v == sat, (eid, s["feeScheduleId"], v, sat)
        k = kind(s["services"])
        if k is None:
            continue
        if longest(s["equipment"]) < 25:
            if longest(s["equipment"]):
                short.add(k)
            continue
        got.setdefault(k, []).append(v)
    if not got:
        flags.append((eid, e["name"], "no schedule takes a 23-ft rig")); continue
    base_k = next(k for k in ("pv", "ne", "e", "ew", "fhu") if k in got)
    base, hi = min(got[base_k]), max(got[base_k])
    sur = {}
    elec = [v for k in ("e", "ew") if k != base_k for v in got.get(k, [])]
    if base_k in ("pv", "ne") and elec:
        sur["electric"] = num(min(elec) - base)
    if got.get("e") and got.get("ew") and base_k in ("pv", "ne", "e") and min(got["ew"]) > min(got["e"]):
        sur["water"] = num(min(got["ew"]) - min(got["e"]))
    if "fhu" in got and base_k != "fhu":
        sur["full_hookup"] = num(min(got["fhu"]) - base)
    sur["weekend"] = 0
    parts = [f"{WORD[k]} {span(got[k])}" for k in ("pv", "ne", "e", "ew", "fhu") if k in got]
    too_short = [WORD[k] for k in ("ne", "e", "ew", "fhu") if k in short and k not in got]
    text = ("June nights on the booking site: " + "; ".join(parts) + ", the same on a Saturday" +
            (f" ({' and '.join(too_short)} sites here take nothing over 20 ft)" if too_short else "") +
            (". Primitive sites cost the same in every season." if set(got) == {"pv"} else
             ". Peak-season rates (May 15 - Sept. 15); shoulder-season and winter rates are lower.") +
            f" Tax included. Washington State Parks' booking site and fees page, read {D}.")
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": num(base), "nightly_high": num(hi), "currency": "USD", "surcharges": sur, "checked": "2026",
        "note": text},
        "source": f"washington.goingtocamp.com, {pname}" + (f" ({', '.join(sorted(maps))})" if maps else "") +
                  f": campsite fee schedules for {TUE} and {SAT} with their sites' service types and allowed equipment "
                  f"(wa_booking_fees_2026-10-12.json) + {FEES} (season table, tax included), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "WA findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:45], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
