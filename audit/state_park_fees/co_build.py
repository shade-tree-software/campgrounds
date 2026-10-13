"""Colorado Parks and Wildlife findings: its booking site cpwshop.com (ReserveAmerica's 'CUI' .page platform), read
2026-10-12. cui_sites.py listed every site of each campground the parks' pages link to (co_sites_2026-10-12.jsonl: loop,
site type, maximum vehicle length; five parks drawn on an SVG map give neither loop nor length, so their every site was
read), and cui_rates.py priced sites of each loop and type for Tue 2027-06-15 and Sat 2027-06-19
(co_booking_rates_2026-10-12.jsonl; 'Camping Fees (1 Night)').

    python3 -I co_build.py OUT

CPW's camping page gives each type's range across parks and seasons ('Backcountry ... $13 - $18', 'Basic ... $22 -
$28', 'Electric ... $27 - $36', 'Full Hook-up ... $32 - $41 Per Night'); the booking site's June nights are the top of
each. An entry's base is its cheapest site type a 23-ft rig fits (maximum vehicle length; a blank one is unknown, not
short, but CPW's 0 is a site for no vehicle); electric and full hookups are add-ons on it, and weekend is the base
site's Saturday difference. The daily vehicle pass is the state:CO row's. CPW's reservation fee is not recorded: no
current CPW page states it (its old reservation FAQ said $10, non-refundable). Tent, cabin, yurt, group, walk-in and
backcountry sites are left out."""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TUE, SAT = "06/15/2027", "06/19/2027"
CAMPING = "https://cpw.state.co.us/camping"
KIND = {"Primitive": "prim", "Basic": "basic", "Basic - ADA": "basic", "Electric": "e", "Electric - ADA": "e",
        "Full Hookup": "fhu", "Full Hookup - ADA": "fhu"}
WORD = {"prim": "primitive", "basic": "basic", "e": "electric", "fhu": "full hookups"}
NOT_DRIVE_IN = re.compile(r"(?i)walk-in|backcountry|hike-in|group|cabin|yurt")
# entry -> (parkID, its loops (regex) or None for the whole campground)
ENTRY = {
    408: ("50081", None), 409: ("50022", None), 2240: ("50020", None),
    2241: ("50028", r"^(Pelican|Cove)$"), 2242: ("50028", r"^Lakeside$"), 2244: ("50065", r"^Elks Campground$"),
    2246: ("50021", None), 2247: ("50025", r"^Reverends Ridge [A-E] Loop$"), 2248: ("50032", None),
    2249: ("50024", r"^Rocky Ridge"), 2250: ("50024", r"^North Shore"), 2253: ("50024", r"^Witchers Cove$"),
    2254: ("50024", r"^Lazy Boy$"), 2256: ("50024", r"^Rocking Chair$"),
    2257: ("50036", r"^(Yucca Flats|Prairie Ridge|Kettle Creek|Eagle View)$"), 2258: ("50036", r"^Arkansas Point$"),
    2259: ("50029", r"^Pinon"), 2260: ("50029", r"^Yucca$"), 2261: ("50044", r"^Carpios Ridge$"),
    2262: ("50072", r"^Lake Hasty$"),
    2263: ("50067", r"^Hecla Junction$"), 2264: ("50067", r"^Rincon$"), 2265: ("50067", r"^Ruby Mountain$"),
    2266: ("50067", r"^Railroad Bridge$"),
    2269: ("50040", r"^Pinnacle City$"), 2270: ("50040", r"^Junction City$"), 2271: ("50040", r"^McKindley$"),
    2272: ("50040", r"^Harding Spur$"),
    2273: ("50041", r"^(Arnica|Harebell|Larkspur|Lupine|Rosecrown|Yarrow)$"), 2274: ("50041", r"^(Wheeler|Bridge Island)$"),
    2275: ("50035", None), 2276: ("50070", r"^Headquarters$"),
    2277: ("52700", r"^Pronghorn"), 2278: ("52700", r"^Bears Ears"),
    2279: ("50042", r"(?i)bockman"), 2280: ("50042", r"(?i)north michigan"), 2281: ("50042", r"(?i)ranger lakes"),
    2282: ("50026", None), 2283: ("50027", None), 2284: ("50069", r"^Main$"),
    2285: ("50045", r"^Early Settlers$"), 2286: ("50045", r"^Aspen Grove$"), 2287: ("50045", r"^Oak Point$"),
    2288: ("50038", r"^(Cottonwood|Cedar)$"), 2289: ("50038", r"^Lakeview$"), 2290: ("50038", r"^(Sage|Pinon)$"),
    2294: ("50039", r"^Dakota Terraces"), 2295: ("50039", r"^Elk Ridge"), 2296: ("50039", r"^Pa-Co-Chu-Puk [FG] Loop$"),
    2297: ("50023", r"^Clear Fork$"), 2298: ("50023", r"^Iron Creek$"), 2300: ("50031", r"^(Main|West Side)$"),
    2301: ("50033", r"(?i)rosa"), 2302: ("50033", r"(?i)carracas"),
}
parks = {}
for line in open(os.path.join(HERE, "co_sites_2026-10-12.jsonl"), encoding="utf-8"):
    p = json.loads(line)
    parks[p["parkId"]] = p
rates = [json.loads(l) for l in open(os.path.join(HERE, "co_booking_rates_2026-10-12.jsonl"), encoding="utf-8")]
read = {(r["parkId"], r["siteId"]): r for r in rates if r["date"] == TUE and r.get("price")}


def price(r):
    m = re.search(r"\$([\d,]+\.\d\d)", r.get("price") or "")
    return float(m.group(1).replace(",", "")) if m else None


def num(v):
    return int(v) if float(v).is_integer() else v


out, flags = [], []
for eid, (pid, loops) in sorted(ENTRY.items()):
    e = rows[eid]
    if e.get("fees"):
        continue
    park = parks[pid]
    mine = []
    for s in park["sites"]:
        r = read.get((pid, s["siteId"])) or {}
        loop = s.get("loop") or r.get("loop") or ""
        if s.get("type") not in KIND or NOT_DRIVE_IN.search(loop) or (loops and not re.search(loops, loop)):
            continue
        mine.append((s, loop, s.get("maxlen") if s.get("maxlen") is not None else r.get("Maximum Vehicle Length")))
    if not mine:
        flags.append((eid, e["name"], f"no campsites in {pid} loops {loops}")); continue
    names = {loop for _, loop, _ in mine}
    ids = {s["siteId"] for s, _, _ in mine}
    fits = collections.defaultdict(bool)
    for s, loop, ln in mine:
        fits[KIND[s["type"]]] |= ln in (None, "") or (str(ln).isdigit() and int(ln) >= 23)
    tue, sat, sat_diff = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(set)
    tue_of = {}
    zero = collections.defaultdict(lambda: True)   # every listed length of the type is CPW's 0
    for s, loop, ln in mine:
        zero[KIND[s["type"]]] &= str(ln) == "0"
    for r in rates:
        if r["parkId"] != pid or r["siteId"] not in ids or r.get("type") not in KIND or price(r) is None:
            continue
        if r["date"] == TUE:
            tue[KIND[r["type"]]].append(price(r))
            tue_of[r["siteId"]] = price(r)
    for r in rates:
        if r["parkId"] == pid and r["date"] == SAT and r.get("type") in KIND and r["siteId"] in tue_of and price(r) is not None:
            sat[KIND[r["type"]]].append(price(r))
            sat_diff[KIND[r["type"]]].add(round(price(r) - tue_of[r["siteId"]], 2))
    kinds = sorted((k for k in tue if fits[k]), key=lambda k: min(tue[k]))
    if not kinds:
        flags.append((eid, e["name"], f"no priced site a 23-ft rig fits ({ {k: sorted(set(v)) for k, v in tue.items()} })"))
        continue
    base = kinds[0]
    lo, hi = min(tue[base]), max(tue[base])
    sur = {}
    if len(sat_diff.get(base, ())) == 1:
        sur["weekend"] = num(next(iter(sat_diff[base])))
    if base in ("prim", "basic") and "e" in kinds:
        sur["electric"] = num(min(tue["e"]) - lo)
    if base != "fhu" and "fhu" in kinds:
        sur["full_hookup"] = num(min(tue["fhu"]) - lo)

    def money(k, night=tue):
        a, b = min(night[k]), max(night[k])
        return f"${a:g}" if a == b else f"${a:g}-{b:g}"
    order = [k for k in ("prim", "basic", "e", "fhu") if k in kinds]
    same = all(sat_diff.get(k) == {0} for k in order)
    short = [k for k in ("prim", "basic", "e", "fhu") if tue.get(k) and not fits[k]]
    none = [WORD[k] for k in short if zero[k]]
    short = [WORD[k] for k in short if not zero[k]]
    text = ("June nights: " + "; ".join(f"{WORD[k]} {money(k)}" for k in order) + "." +
            (" The same on a Saturday." if same else
             " Saturday: " + "; ".join(f"{WORD[k]} {money(k, sat)}" for k in order if sat.get(k)) + ".") +
            (f" (The {' and '.join(short)} sites here are too short for a 23-ft rig.)" if short else "") +
            (f" (CPW gives the {' and '.join(none)} sites here no room for a vehicle.)" if none else "") +
            " Plus tax and the daily vehicle pass. CPW's camping page puts basic sites at $22-28, electric $27-36 and "
            f"full hookups $32-41 by park and season. Colorado Parks and Wildlife's booking site, read {D}.")
    out.append({"id": eid, "name": e["name"], "fees": {
        "nightly_low": num(lo), "nightly_high": num(hi), "currency": "USD", "surcharges": sur, "checked": "2026",
        "note": text},
        "source": f"cpwshop.com parkID {pid} ({park.get('name')}; {', '.join(sorted(names))}): each loop and site type's "
                  f"1-night price for 2027-06-15 and 2027-06-19 (co_booking_rates_2026-10-12.jsonl) and every site's type "
                  f"and maximum vehicle length (co_sites_2026-10-12.jsonl) + {CAMPING} (type ranges), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "CO findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:50], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
