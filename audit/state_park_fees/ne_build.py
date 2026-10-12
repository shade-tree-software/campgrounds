"""Nebraska Game and Parks findings: the statewide camping rates grid (outdoornebraska.gov/parks/park-pricing/ ->
'2025-Camping-Rates-Grid.pdf', still the one the page links on 2026-10-12; transcribed from its rendered page into GRID
below, because the dots marking each area's site types are graphics), checked on nebraskastateparks.reserveamerica.com
(Branched Oak, Lake McConaughy and Lake Ogallala priced for Tue 2027-06-15 and Sat 2027-06-19, ne_booking_check_*.jsonl;
every price on the grid; $8.50 reservation fee on the quote).

    python3 -I ne_build.py OUT

'Nebraska's state parks, state historical parks and state recreation areas offer five levels of camping ... These rates
are consistent across all parks throughout the state, with the exception of Lake McConaughy State Recreation Area': Full
Hookup $35, Electric Plus $30 (a 20/30-amp site with its own water hookup, or a 50-amp site), Electric $25, Basic $15,
Primitive $10 a night; 'Camping rates during the off-season are $5 less per night for all site types, except primitive
rates that remain $10/night year-round' (modern facilities close mid-October through April); equestrian sites +$5.
Lake McConaughy and Lake Ogallala: May 21 - September 12 Thursday-Saturday $40 / $35 / $20 / beach $25, Sunday-Wednesday
$35 / $30 / $15 / beach $20, September 13 - May 20 $30 / $25 / $10 / beach $15 (full / electric plus / basic / beach).

An entry's base is its area's Basic site where it has one (else Primitive, else the cheapest hookup site); nightly_low / nightly_high are the
off-season and in-season prices; electric (the cheaper of Electric and Electric Plus) and full hookups are in-season
add-ons. The park entry permit ($7 a day for a Nebraska vehicle, $14 otherwise) and the reservation fee are the state:NE
registry row's."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
GRIDPDF = "https://outdoornebraska.gov/wp-content/uploads/2025/01/2025-Camping-Rates-Grid.pdf"
PRICE = {"F": 35, "EP": 30, "E": 25, "B": 15, "P": 10}
WORD = {"F": "full hookup", "EP": "electric plus", "E": "electric", "B": "basic", "P": "primitive"}
# area -> site types ('q' = regular and equestrian sites, equestrian +$5)
GRID = {
    "Alexandria": "EP E B", "Bluestem": "B", "Box Butte": "EP B", "Branched Oak": "F EPq E Bq", "Bridgeport": "B",
    "Buffalo Bill": "EP E B", "Calamus": "EP B", "Chadron": "EP B", "Cheyenne": "EP B", "Conestoga": "EP E B",
    "Cottonwood": "B", "Danish Alps": "EPq B", "Dead Timber": "E P", "Enders": "EP B P", "Eugene T. Mahoney": "F EP E",
    "Fort Kearny": "EP E B", "Fort Robinson": "F EP B", "Fremont": "EP E B P", "Gallagher Canyon": "B P",
    "Indian Cave": "EP E Bq", "Johnson Lake": "EP E B", "Keller Park": "EP B P", "Lake Maloney": "EP B",
    "Lake Minatare": "EP B P", "Lewis and Clark": "F EP E Bq", "Long Pine": "B", "Louisville": "F EP E B",
    "Medicine Creek": "EP E B", "Memphis": "EP B P", "Merritt": "EP B", "Mormon Island": "EP E B",
    "Niobrara": "EP Bq", "North Loup": "P", "Olive Creek": "B", "Pawnee": "EP E Bq", "Pelican Point": "B",
    "Platte River": "F", "Ponca": "EP E B", "Red Willow": "EP E B", "Riverview Marina": "E B", "Rock Creek Lake": "B",
    "Rock Creek Station": "E Bq", "Rockford Lake": "EP E B", "Sandy Channel": "B P", "Sherman Reservoir": "EP B P",
    "Smith Falls": "B", "Stagecoach": "EP E B", "Summit Lake": "EP E B", "Sutherland": "EP B P",
    "Swanson Lake": "EP B P", "Two Rivers": "F EP E Bq", "Union Pacific": "P", "Verdon Lake": "B",
    "Victoria Springs": "EP B", "Wagon Train": "EP E B", "Walgren Lake": "P", "War Axe": "P", "Wildcat Hills": "B",
    "Willow Creek": "EPq E Bq", "Windmill": "EP E B",
}
AREA = {
    2669: "Alexandria", 2673: "Lewis and Clark", 2674: "Bluestem", 2676: "Box Butte", 2677: "Branched Oak",
    2678: "Bridgeport", 2679: "Buffalo Bill", 2680: "Calamus", 2681: "Calamus", 2683: "Chadron", 2685: "Cheyenne",
    2686: "Conestoga", 2687: "Cottonwood", 2690: "Danish Alps", 2691: "Dead Timber", 2692: "Enders",
    2693: "Eugene T. Mahoney", 2694: "Fort Kearny", 2695: "Fort Robinson", 2696: "Fremont", 2697: "Gallagher Canyon",
    2700: "Indian Cave", 2701: "Johnson Lake", 2702: "Keller Park", 2703: "Lake Maloney", 2704: "Lake Minatare",
    2707: "Lewis and Clark", 2711: "Long Pine", 2712: "Louisville", 2714: "Medicine Creek", 2715: "Memphis",
    2716: "Merritt", 2717: "Merritt", 2718: "Mormon Island", 2719: "Niobrara", 2720: "North Loup", 2722: "Olive Creek",
    2726: "Pawnee", 2727: "Pelican Point", 2728: "Platte River", 2729: "Ponca", 2731: "Red Willow",
    2732: "Riverview Marina", 2733: "Rock Creek Station", 2734: "Rockford Lake", 2736: "Sandy Channel",
    2737: "Sherman Reservoir", 2739: "Stagecoach", 2740: "Summit Lake", 2741: "Swanson Lake", 2742: "Swanson Lake",
    2743: "Two Rivers", 2744: "Union Pacific", 2745: "Verdon Lake", 2746: "Victoria Springs", 2747: "Wagon Train",
    2748: "Walgren Lake", 2749: "War Axe", 2750: "Lewis and Clark", 2751: "Wildcat Hills", 2752: "Willow Creek",
    2753: "Windmill",
}
# Lake McConaughy / Ogallala campgrounds: their site types on the booking site (beach = the beach camping areas, not on
# it); prices (off-season, Sunday-Wednesday, Thursday-Saturday)
MAC = {"F": (30, 35, 40), "EP": (25, 30, 35), "B": (10, 15, 20), "beach": (15, 20, 25)}
MAC_ENTRY = {2682: ("Cedar View", "B EP"), 2708: ("Little Thunder", "EP F"), 2709: ("Lone Eagle", "F"),
             2713: ("Martin Bay", "B F"), 2735: ("Sandy Beach", "B"), 2721: ("North Shore", "beach"),
             2724: ("Omaha Beach", "beach"), 2725: ("Otter Creek", "beach"), 2738: ("Spring Park", "beach"),
             2705: ("Lake Ogallala East", "EP")}
TAIL = (" Plus tax, the $8.50 reservation fee when booked online, and a park entry permit ($7 a day for a Nebraska "
        "vehicle, $14 otherwise; $35 / $70 a year). Nebraska Game and Parks' camping rates grid ('These rates are "
        f"consistent across all parks'), matched on its booking site for June 2027 nights, read {D}.")
out, flags = [], []
for eid, e in sorted(rows.items()):
    if e.get("state") != "NE" or e.get("ownership") != "state" or e.get("fees"):
        continue
    if eid in MAC_ENTRY:
        name, kinds = MAC_ENTRY[eid]
        ks = kinds.split()
        base = next(k for k in ("beach", "B", "EP", "F") if k in ks)
        lo, mid, hi = MAC[base]
        sur = {"weekend": 5}
        if base in ("B", "beach") and "EP" in ks:
            sur["electric"] = MAC["EP"][1] - mid
        if base != "F" and "F" in ks:
            sur["full_hookup"] = MAC["F"][1] - mid
        word = {"beach": "beach camping", "B": "basic", "EP": "electric plus", "F": "full hookup"}
        text = ("Lake McConaughy / Ogallala rates: " + "; ".join(
            f"{word[k]} ${MAC[k][1]} Sunday-Wednesday, ${MAC[k][2]} Thursday-Saturday (May 21 - September 12), "
            f"${MAC[k][0]} the rest of the year" for k in ks) + "." + TAIL)
        out.append({"id": eid, "name": e["name"], "fees": {
            "nightly_low": lo, "nightly_high": mid, "currency": "USD", "surcharges": sur, "checked": "2026", "note": text},
            "source": f"{GRIDPDF} (Lake McConaughy and Lake Ogallala seasonal rates) + nebraskastateparks.reserveamerica.com "
                      f"({name} site types; June 2027 quotes), read {D}"})
        continue
    if eid not in AREA:
        flags.append((eid, e["name"], "not on the camping rates grid")); continue
    kinds = GRID[AREA[eid]].split()
    ks = [k.rstrip("q") for k in kinds]
    base = next(k for k in ("B", "P", "E", "EP", "F") if k in ks)     # basic, else primitive, else the cheapest hookup
    hi = PRICE[base]
    lo = hi if base == "P" else hi - 5
    sur = {"weekend": 0}
    elec = [PRICE[k] for k in ("E", "EP") if k in ks and k != base]
    if base in ("B", "P") and elec:
        sur["electric"] = min(elec) - hi
    if "F" in ks and base != "F":
        sur["full_hookup"] = PRICE["F"] - hi
    parts = [f"{WORD[k]} ${PRICE[k]}" for k in ("B", "E", "EP", "F", "P") if k in ks]
    text = ("In season: " + ", ".join(parts) + " a night; $5 less mid-October through April" +
            (" (primitive $10 all year)" if "P" in ks else "") + "." +
            (" Equestrian sites $5 more." if any(k.endswith("q") for k in kinds) else "") + TAIL)
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": lo, "nightly_high": hi, "currency": "USD", "surcharges": sur, "checked": "2026", "note": text},
        "source": f"{GRIDPDF} (row '{AREA[eid]}', linked from https://outdoornebraska.gov/parks/park-pricing/) + "
                  f"nebraskastateparks.reserveamerica.com (June 2027 quotes at Branched Oak and Lake McConaughy match it), "
                  f"read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NE findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:44], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
