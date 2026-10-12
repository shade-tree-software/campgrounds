"""GA findings, read 2026-10-12.

    python3 -I ga_build.py OUT

- State parks: gastateparks.reserveamerica.com, sampled sites for Tue 2027-06-15 and Sat 2027-06-19 (ra_quick.py ->
  ga_booking_sample_2026-10-12.jsonl). Georgia prices site by site (a park's sites differ by a few dollars) and publishes
  no table (registry row state:GA), so each entry carries the range of its sampled RV sites. Every RV site sampled has
  electric and water; full hookups are named in the note. The park pass ($10 a vehicle) is the registry row's. Entry ->
  park id: ga_park_ids_2026-10-12.json (the booking site's park directory, matched by name).
- The lodge parks book campsites through their concession's iqwebbook engine (ga_lodges/: Tue 2027-01-12 and Sat
  2027-01-16): Amicalola Falls, Unicoi, Georgia Veterans (Lake Blackshear Resort). Little Ocmulgee's engine says
  'PLEASE CALL HOTEL' for every campsite, so it stays unpriced.
- Wildlife Resources Division campgrounds: Go Outdoors Georgia's site lists (reservations.gooutdoorsgeorgia.com, read in
  the browser 2026-10-12) and Rocky Mountain's campground rules PDF.
- Stone Mountain Park: Campspot (ga_stone_mountain_campspot_2026-10-12.jsonl)."""
import collections, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
IDS = json.load(open(os.path.join(HERE, 'ga_park_ids_2026-10-12.json')))
D = "2026-10-12"
SKIP = re.compile(r"(?i)hike|canoe|backpack|backcountry|equest|horse|primitive|group|paddle|walk|boat|cabin|yurt|cottage|"
                  r"pioneer|shelter|lodge|platform|squirrel|glamp|adirondack|event")
ew, fhu, sat, tue = (collections.defaultdict(set) for _ in range(4))
for line in open(os.path.join(HERE, "ga_booking_sample_2026-10-12.jsonl")):
    r = json.loads(line)
    if "error" in r or SKIP.search(r.get("loop") or "") or SKIP.search(r.get("Type") or ""):
        continue
    if "Electric" not in (r.get("Type") or ""):
        continue
    m = re.search(r"\$([\d.]+) Per Night", r.get("price") or "")
    if not m:
        continue
    p = float(m.group(1))
    (fhu if r.get("Sewer Hookup") else ew)[r["parkId"]].add(p)
    (sat if r["date"] == "6/19/2027" else tue)[r["parkId"]].add((r["site"], p))


def money(x):
    return f"${int(x)}" if float(x).is_integer() else f"${x:.2f}"


def rng(v):
    lo, hi = min(v), max(v)
    return money(lo) if lo == hi else f"{money(lo)}-{money(hi)[1:]}"


out = []
for sid, (name, cur, pid, dname) in sorted(IDS.items(), key=lambda x: int(x[0])):
    eid = int(sid)
    if not pid or pid not in tue and pid not in ew:
        continue
    vals = ew[pid] | fhu[pid]
    if not vals:
        print("no RV prices", eid, name, pid); continue
    t = dict(tue[pid]); s = dict(sat[pid])
    up = sorted({round(s[k] - t[k], 2) for k in s if k in t and s[k] != t[k]})
    parts = [f"{rng(ew[pid])} a night for a site with electric and water" if ew[pid] else ""]
    if fhu[pid]:
        parts.append(f"full hookups {rng(fhu[pid])}" if ew[pid] else f"{rng(fhu[pid])} a night for a site with full hookups")
    text = "; ".join(p for p in parts if p) + "."
    text += (" A Saturday costs " + " or ".join(f"${int(x)}" for x in up) + " more at some sites." if up
             else " The same on a Saturday.")
    text += (" Georgia prices site by site; these are sampled sites' prices for a Tuesday and a Saturday in June 2027 on "
             f"Georgia State Parks' booking site, read {D}. Vehicles need the $10 ParkPass.")
    if dname and dname.startswith("Okefenokee"):
        text += " The park is now called Okefenokee State Park."
    lo, hi = min(vals), max(vals)          # both dates' prices are in vals
    out.append({"id": eid, "name": rows[eid]["name"], "fees": {
        "nightly_low": int(lo) if lo.is_integer() else lo, "nightly_high": int(hi) if float(hi).is_integer() else hi,
        "currency": "USD", "checked": "2026", "note": text},
        "source": f"gastateparks.reserveamerica.com parkId {pid} ({dname}; sampled sites' 1-night price for 2027-06-15 and "
                  f"2027-06-19, read {D})"})
# The lodge parks (concession engines, ga_lodges/), the Wildlife Resources campgrounds and Stone Mountain
OTHER = {
    4516: (49, 59, "$49 a night for a campsite with power and water on a weeknight, $59 on a Saturday (January 2027). The "
           "campground books through the lodge's own reservation system, not the state parks' site. Vehicles need the "
           "$10 ParkPass.", "https://us01.iqwebbook.com/TLAAFGA683/ (Amicalola Falls Lodge's booking engine: every "
           "'Campsite ... Power/Water' $49.00 on 2027-01-12, $59.00 on 2027-01-16; ga_lodges/)"),
    4546: (45, 60, "$45-50 a night for a site with power and water, $55 with full hookups on a weeknight; on a Saturday "
           "$50-54 and $60 (January 2027). Walk-in tent site $20. The campground books through the lodge's own "
           "reservation system. Vehicles need the $10 ParkPass.", "https://us01.iqwebbook.com/ULGA340/ (Unicoi Lodge's "
           "booking engine, campsites for 2027-01-12 and 2027-01-16; ga_lodges/)"),
    4529: (55, 70, "$55 a night for a 30-amp site away from the water, $60 for 50-amp or full hookups, $65-70 on the "
           "waterfront, the same on a Saturday (January 2027). The campground books through Lake Blackshear Resort, the "
           "park's concession. Vehicles need the $10 ParkPass.", "https://us01.iqwebbook.com/LBRGCGA690/ (Lake Blackshear "
           "Resort's booking engine, campsites for 2027-01-12 and 2027-01-16; ga_lodges/)"),
    4639: (30, 30, "$30 a night for a site with 50-amp electric and water (the two double sites $60); primitive tent sites "
           "$12. Every vehicle needs a $5 daily parking permit (one per campsite at night). Booked on Go Outdoors Georgia.",
           "https://reservations.gooutdoorsgeorgia.com/FacilityDetails.aspx?facID=8 (site list: RV sites $30.00, sites B-I "
           "$12.00, read 2026-10-12) + Rocky Mountain PFA campground rules PDF ('SITES 2-7, 9-36 ... $30 PER NIGHT', $5 daily "
           "parking permit)"),
    4551: (40, 40, "$40 a night for a full-facility site (electric, water, sewer); tent-only sites $20. Booked on Go Outdoors "
           "Georgia.", "https://reservations.gooutdoorsgeorgia.com/FacilityDetails.aspx?facID=1 (site list: 'Full Facility' "
           "$40.00, 'Tent Only' $20.00, read 2026-10-12)"),
    4679: (35, 40, "$35 a night for an RV/tent site with electric and water, $40 for a full-facility site (sewer, pull-through); "
           "tent-only sites $20. Booked on Go Outdoors Georgia.", "https://reservations.gooutdoorsgeorgia.com/FacilityDetails.aspx"
           "?facID=2 (site list: 'RV/Tent Combo' $35.00, 'Full Facility' $40.00, 'Tent Only' $20.00, read 2026-10-12)"),
    13372: (61.7, 66.87, "$61.70 a night for an RV site with water and electric, $66.87 with full hookups, on a weeknight in "
            "May or June 2027; a Saturday $5.17 more. Lakeside, cable and premium sites $72.04-97.89, a super site $145.66; "
            "tent and pop-up sites $51.36. Booked on Campspot.", "https://www.campspot.com/park/stone-mountain-campground-stone-"
            "mountain-ga (the availability the park page fetches, one-night stays 2027-05-11, 2027-06-15 and 2027-06-19, read "
            "2026-10-12; ga_stone_mountain_campspot_2026-10-12.jsonl)"),
}
for eid, (lo, hi, note, src) in OTHER.items():
    out.append({"id": eid, "name": rows[eid]["name"], "fees": {"nightly_low": lo, "nightly_high": hi, "currency": "USD",
                "checked": "2026", "note": note + f" Read {D}."}, "source": src})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "GA findings")
for x in out:
    print(x["id"], x["name"][:34], x["fees"]["nightly_low"], x["fees"]["nightly_high"], "|", x["fees"]["note"][:140])
