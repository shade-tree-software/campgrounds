"""Iowa state parks and forests findings: the DNR's 'Camping Rates' sheet, updated February 15, 2026
(ia_rate_sheet_2026-10-12.txt: peak season May 1 - October 15 and off-season October 16 - April 30, per park and site
type, 'Rates are per night and include sales tax'), checked against iowastateparks.reserveamerica.com: sampled sites'
1-night prices for Wed 2026-10-14 (peak) and Tue 2026-10-20 (off-season) (ra_quick.py -> ia_booking_sample_*.jsonl),
and every site of each park with its type and equipment length (ra_list.py -> ia_sites_2026-10-12.json).

    python3 -I ia_build.py OUT

The base is the non-electric site where the park's site list has one that takes a 23-ft rig, else the electric site. A
site's max vehicle length is the number in its driveway column; a drive-in non-electric site with no number posted counts
as fitting, since the ones read (ia_ne_site_details_2026-10-12.jsonl: Lacey-Keosauqua, Backbone, Springbrook, Rock Creek,
Elk Rock) are typed 'RV Site, Tent Site, Trailer Site' with 26-100 ft sites;
nightly_low / nightly_high are its off-season and peak prices; electric and full hookups are peak differences. 'A
$4-$5/night fee applies to holiday weekend stays during Memorial Day, Labor Day and 4th of July holiday weekends.' The
booking site adds a $4.50 reservation fee to each reservation (every sampled quote's breakdown).

Where the booking site charges something else for a site type it is what the entry carries, with the sheet's figure in
the note (as for Maryland's Wolf Den Run): Brushy Creek's Beach Campground still charges $25 electric / $35 full hookups
against the sheet's $26 / $38, and Beeds Lake, Bellevue and Dolliver sell full-hookup sites (electric + $12) the sheet
has no column for (Backbone's two are its camp hosts'). Host sites and two-family 'Buddy' sites are left out. Shimek's
White Oak sites are all typed 'Tent Only' ('Looking For Category: Tent Site', one 'can accommodate a pop up camper'):
priced, and flagged."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
SHEET = "https://www.iowadnr.gov/media/6743/download"
t = open(os.path.join(HERE, "ia_rate_sheet_2026-10-12.txt"), encoding="utf-8").read()


def parse(seg):
    out = {}
    for line in seg.splitlines():
        m = re.match(r"^\s{0,3}([A-Z][A-Za-z&.' -]+?)\s{2,}((?:(?:\$\d+|--)\s*){5})\s*$", line)
        if m:
            out[m.group(1).strip()] = [int(v[1:]) if v != "--" else None for v in re.findall(r"\$\d+|--", m.group(2))]
    return out


PEAK = parse(t[t.find("PEAK SEASON RATES"):t.find("OFF-SEASON RATES")])
OFF = parse(t[t.find("OFF-SEASON RATES"):t.find("Group Camp Rates")])
COLS = ("fhu", "ew", "e", "ne")                 # sewer-water-electric, water-electric, electric, nonelectric (youth group dropped)
WORD = {"fhu": "full hookups", "ew": "water and electric", "e": "electric", "ne": "non-electric"}
SPECIAL = {2888: "AA Call", 2893: "Brushy Creek Nonequestrian", 2897: "Elk Rock Nonequestrian", 2906: "Honey Creek",
           2912: "Lake Macbride North Modern", 2915: "Lake of Three Fires Nonequestrian", 2921: "Nine Eagles Nonequestrian",
           2930: "Shimek Forest Nonequestrian", 2932: "Stephens Forest Nonequestrian", 2936: "Volga River Nonequestrian",
           2939: "Waubonsie Nonequestrian", 2942: "Yellow River Forest Nonequestrian"}
SKIP = {2905: "Honey Creek Resort: not on the DNR sheet; its own site no longer lists RV sites",
        3129: "Sharon Bluffs: run by Appanoose County Conservation, first come, no published fee"}
sites = json.load(open(os.path.join(HERE, "ia_sites_2026-10-12.json"), encoding="utf-8"))
TYPE = {"Standard Non-Electric": "ne", "Standard Electric": "e", "Standard Electric with Water": "ew",
        "Standard Full Hook-Up": "fhu"}
BOOK = {}                       # parkId -> kind -> date -> [prices]
for line in open(os.path.join(HERE, "ia_booking_sample_2026-10-12.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    m = re.match(r"\$([\d.]+) Per Night", r.get("price") or "")
    k = TYPE.get(r.get("Type"))
    if not m or not k or "Host" in (r.get("site") or "") or r.get("loop") == "Primitive Campground-South":
        continue                # Lake Macbride's primitive south loop is not the entry's modern campground
    BOOK.setdefault(r["parkId"], {}).setdefault(k, {}).setdefault(r["date"], []).append(float(m.group(1)))


def booked(pid, k, date):
    vals = (BOOK.get(pid, {}).get(k) or {}).get(date)
    return max(set(vals), key=vals.count) if vals else None


def row_name(e):
    if e["id"] in SPECIAL:
        return SPECIAL[e["id"]]
    n = re.sub(r"\s*\(IA\)|\s+-\s+.*$", "", e["name"])
    n = re.sub(r"\s+(State Park|State Recreation Area|State Forest)$", "", n)
    return n


out, flags = [], []
for eid, e in sorted(rows.items()):
    if e.get("kind") != "campground" or e.get("state") != "IA" or e.get("ownership") != "state" or e.get("fees"):
        continue
    if eid in SKIP:
        flags.append((eid, e["name"], SKIP[eid])); continue
    name = row_name(e)
    if name not in PEAK:
        flags.append((eid, e["name"], f"no sheet row '{name}'")); continue
    pk, of = dict(zip(COLS, PEAK[name])), dict(zip(COLS, OFF[name]))
    pid = (re.search(r"parkId=(\d+)", e.get("website") or "") or [None, None])[1]
    differ = []
    for k in COLS:
        for prices, date in ((pk, "10/14/2026"), (of, "10/20/2026")):
            b = booked(pid, k, date)
            if b is not None and b != prices[k]:
                differ.append(f"{WORD[k]} {'peak' if prices is pk else 'off-season'} ${b:g} (" +
                              (f"the sheet says ${prices[k]}" if prices[k] else "not on the sheet") + ")")
                prices[k] = int(b) if float(b).is_integer() else b
    lst = sites.get(pid, {}).get("sites", [])
    # cells: [loop, type, people, "48 Back-In" | "Back-In" | "Hike-In" | ...]: the number is the site's max vehicle
    # length; a drive-in site with none posted is typed 'RV Site, Tent Site, Trailer Site' (ia_ne_site_details_*.jsonl)
    ne_fit = any(len(s["cells"]) > 3 and s["cells"][1] == "Standard Non-Electric" and "Host" not in s["site"]
                 and (m := re.match(r"(\d+ ?)?(Back-In|Pull-Through|Parallel)?$", s["cells"][3]))
                 and (not m.group(1) or int(m.group(1)) >= 23) for s in lst)
    if pk["ne"] and not ne_fit and lst and not any(pk[k] for k in ("e", "ew", "fhu")):
        # Shimek's White Oak: every site is typed 'Tent Only' ('Looking For Category: Tent Site', 'Site can accommodate
        # a pop up camper', 45-ft gravel pads) - priced, and left for AWH
        flags.append((eid, e["name"], "no non-electric site the booking site types for RVs; priced from the sheet"))
    base = "ne" if pk["ne"] and (ne_fit or not lst or not any(pk[k] for k in ("e", "ew", "fhu"))) else \
        next(k for k in ("e", "ew", "fhu") if pk[k])
    sur = {}
    if base == "ne" and (pk["e"] or pk["ew"]):
        sur["electric"] = min(v for v in (pk["e"], pk["ew"]) if v) - pk["ne"]
    if pk["fhu"] and base != "fhu":
        sur["full_hookup"] = pk["fhu"] - pk[base]
    sur["weekend"] = 0
    parts = [(f"{WORD[k]} ${of[k]:g} / ${pk[k]:g}" if of[k] else f"{WORD[k]} ${pk[k]:g} (peak)") for k in ("ne", "e", "ew", "fhu") if pk[k]]
    note = ("Off-season (October 16 - April 30) / peak (May 1 - October 15) prices, sales tax included: " + "; ".join(parts) +
            "." + (" The non-electric sites here are too short for a 23-ft rig or tent sites." if pk["ne"] and base != "ne" else "") +
            (" (Non-electric site lengths not checked: the park lists no sites online.)" if base == "ne" and not lst else "") +
            (" The booking site charges " + "; ".join(differ) + "." if differ else "") +
            " Plus $4-5 a night on Memorial Day, July 4th and Labor Day weekends. Iowa DNR's camping rates (updated February "
            f"15, 2026), matched on its booking site, read {D}.")
    fees = {"nightly_low": of[base], "nightly_high": pk[base], "currency": "USD", "reservation_fee": 4.5, "surcharges": sur,
            "checked": "2026", "note": note}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{SHEET} ('Camping Rates', updated February 15, 2026, row '{name}': peak and off-season, 'include sales "
                          f"tax') + iowastateparks.reserveamerica.com parkId {pid} (site list; sampled sites priced 2026-10-14 and "
                          f"2026-10-20), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "IA findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:36], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
