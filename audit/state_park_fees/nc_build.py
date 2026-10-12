"""NC findings: NC State Parks' booking site (northcarolinastateparks.reserveamerica.com), sampled sites for Tue
2027-06-15 and Sat 2027-06-19, read 2026-10-12 (ra_quick.py -> nc_booking_sample_2026-10-12.jsonl), plus every Kerr Lake
site's campground and type (ra_list.py -> nc_kerr_sites_2026-10-12.json) for its seven campground entries.

    python3 -I nc_build.py OUT

Each site's nightly rate is shown before 'Reservation Fees $3.00 Per Night'; NC's statewide rate page quotes the sum
('Tent, trailer, or RV site with no hookups $30', electric only $35, electric and water $40, full hookups $45), so the
entries carry the sum too. Umstead's sites run $3 above the statewide table. A Saturday costs the same; no non-resident
rate (registry row state:NC). Jordan Lake's electric loop at Poplar Point is walk-up only ('Not available online'), so
its price is the statewide table's."""
import collections, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
RATES = "https://www.ncparks.gov/about-us/state-parks-reservation-rates-and-activity-fees"
FEE = 3
SKIP = re.compile(r"(?i)hike|canoe|backpack|equest|horse|primitive|group|paddle|walk|boat|cabin|yurt|class|audit|shelter")
KERR = {102: "Nutbush Campground", 103: "County Line Campground", 104: "Bullocksville Campground",
        105: "Kimball Point Campground", 106: "J.C. Cooper Campground", 107: "Hibernia Campground",
        108: "Henderson Point Campground"}
STATEWIDE = {"ne": 27, "e": 32, "ew": 37, "fhu": 42}     # before the $3 a night


def kind(r):
    t = r.get("Type") or ""
    if "Non-Electric" in t:
        return "ne"
    if "Electric" in t:
        return "fhu" if r.get("Sewer Hookup") else ("ew" if r.get("Water Hookup") else "e")
    return None


price = collections.defaultdict(lambda: collections.defaultdict(set))
seen = collections.defaultdict(set)
for line in open(os.path.join(HERE, "nc_booking_sample_2026-10-12.jsonl")):
    r = json.loads(line)
    if "error" in r or SKIP.search(r.get("loop") or "") or SKIP.search(r.get("Type") or ""):
        continue
    k = kind(r)
    if not k:
        continue
    seen[r["parkId"]].add(k)
    m = re.search(r"\$([\d.]+) Per Night", r.get("price") or "")
    if m:
        assert "Reservation Fees / $3.00 Per Night" in (r.get("breakdown") or ""), r
        price[r["parkId"]][k].add(float(m.group(1)))
kerr = collections.defaultdict(set)
for s in json.load(open(os.path.join(HERE, "nc_kerr_sites_2026-10-12.json")))["sites"]:
    loop, typ = (s["cells"] + ["", ""])[:2]
    k = "ne" if "Non-Electric" in typ else ("ew" if "Electric" in typ else None)   # Kerr Lake's electric sites have water
    for eid, name in KERR.items():
        if k and loop.startswith(name):
            kerr[eid].add(k)
WORD = {"ne": "a site without hookups", "e": "electric only", "ew": "electric and water", "fhu": "full hookups"}
out = []
for eid in sorted(e["id"] for e in rows.values() if e.get("state") == "NC" and e.get("ownership") == "state"
                  and not e.get("fees")):
    m = re.search(r"parkId=(\d+)", rows[eid].get("website") or "")
    if not m:
        print("no parkId", eid); continue
    pid = m.group(1)
    kinds = kerr[eid] if eid in KERR else seen[pid]
    p, walkup = {}, []
    for k in kinds:
        if price[pid].get(k):
            p[k] = sorted(price[pid][k])
        else:
            p[k] = [STATEWIDE[k]]
            walkup.append(k)
    if not p:
        print("no prices", eid, pid); continue
    order = [k for k in ("ne", "e", "ew", "fhu") if k in p]
    base = min(p[order[0]]) + FEE
    s = {}
    if order[0] == "ne":
        el = [min(p[k]) for k in ("e", "ew") if k in p]
        if el:
            s["electric"] = int(min(el) + FEE - base)
    if "fhu" in p and order[0] != "fhu":
        s["full_hookup"] = int(min(p["fhu"]) + FEE - base)
    parts = []
    for i, k in enumerate(order):
        amt = "/".join(f"${int(v + FEE)}" for v in p[k])
        parts.append(f"{amt} a night for {WORD[k]}" if i == 0 else f"{WORD[k]} {amt}")
    text = "; ".join(parts) + (", each including the $3-a-night reservation fee." if len(parts) > 1
                               else ", including the $3-a-night reservation fee.")
    if walkup:
        text += (" The electric sites here are walk-up only (not bookable online); their price is NC's statewide rate.")
    if pid == "552839":
        text += " Umstead's sites cost $3 more than NC's statewide rates."
    text += f" The same on a Saturday; no out-of-state rate. NC State Parks' booking site, June 2027 nights, read {D}."
    fees = {"nightly_low": int(base), "nightly_high": int(base), "currency": "USD"}
    if s:
        fees["surcharges"] = s
    fees["checked"] = "2026"
    fees["note"] = text
    out.append({"id": eid, "name": rows[eid]["name"], "fees": fees,
                "source": f"northcarolinastateparks.reserveamerica.com parkId {pid} (sampled sites' rate + 'Reservation Fees $3.00 "
                          f"Per Night' for 2027-06-15 and 2027-06-19, read {D})" + (" + every Kerr Lake site's campground and "
                          "type" if eid in KERR else "") + (f" + {RATES} (statewide rates)" if walkup else "")})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NC findings")
for x in out:
    print(x["id"], x["name"][:34], x["fees"]["nightly_low"], x["fees"].get("surcharges"), "|", x["fees"]["note"][:150])
