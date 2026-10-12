"""FL state parks and Greenway campgrounds: each park's campsite fee + Florida's $7 nightly utility fee for RVs, read 2026-10-12.

    python3 -I fl_parks_build.py OUT

Two sources, read through the one-browser driver (floridastateparks.org refuses plain fetches):
- each park's Hours & Fees page (fl_park_fee_text_2026-10-12.json: its camping lines, e.g. '$24 per night plus tax,
  plus a nonrefundable $6.70 reservation fee and a $7 nightly utility fee for RV ... units');
- Reserve Florida's place search (rdr_place.py, fl_rdr_rates_2026-10-12.json): each campground loop's 'Starting at $N'
  line, which is the same campsite fee without the utility fee. It is the only source for the parks whose page gives no
  camping fee (Rainbow Springs, St. Joseph Peninsula, Rodman, Ross Prairie, Gilchrist Blue Springs, Santos), and the check
  on the rest: a page fee that is not among its park's rate lines stops the build.
https://www.floridastateparks.org/fees: 'Effective July 27, 2021: All new reservations for RV, boat, bungalow, cabin and yurt
units at all parks will be assessed a $7 nightly utility fee. This fee does not apply to tent camping', the $6.70 reservation
fee is 'per reservation, not per night', and 'Campsite/cabin stays in Monroe County include a Monroe County surcharge of
$2.50 per night'. So an RV's nightly price is the campsite fee + $7; Florida has no out-of-state rate (its 50% discount is
for Florida residents 65 and over)."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
PAGES = json.load(open(os.path.join(HERE, 'fl_park_fee_text_2026-10-12.json'), encoding='utf-8'))
RDR = json.load(open(os.path.join(HERE, 'fl_rdr_rates_2026-10-12.json'), encoding='utf-8'))
D = "2026-10-12"
STATEWIDE = "https://www.floridastateparks.org/fees"
# id: Reserve Florida PlaceId (the #!park/<id> in the entry's booking link)
PLACE = {149: 75, 150: 9, 151: 46, 152: 53, 153: 54, 154: 57, 156: 58, 157: 37, 158: 51, 159: 14, 160: 39, 161: 1, 162: 38,
         163: 27, 164: 34, 197: 73, 370: 31, 371: 4, 372: 19, 373: 32, 374: 72, 389: 13, 390: 6, 391: 26, 392: 64, 393: 65,
         394: 61, 395: 25, 396: 16, 555: 35, 586: 24, 588: 28, 633: 42, 634: 40, 635: 41, 636: 15, 642: 2, 643: 21, 723: 71,
         4700: 69, 4701: 63, 4702: 45, 4703: 20, 4704: 49, 4705: 8, 4706: 17, 4707: 23, 4708: 48, 4709: 74, 4710: 59,
         4711: 60, 4725: 47}
# The campground loops whose rate line is the campsite fee, where the page gives none.
BOOKING_ONLY = {153: ["LOOP A", "LOOP B", "LOOP C"], 154: ["Campground"], 156: ["Loop A", "Loop B", "Loop C", "Loop P",
                "Ross Prairie Trailhead and Campground"], 393: ["Loop SP"], 4710: ["Ruth B. Kirby Gilchrist Blue Springs State Park"],
                4711: ["Santos Trailhead and Campground"]}
MONROE = {370, 371, 636}
EXTRA = {151: " The park's page lists $20 and does not mention the utility fee, which Florida's fee page applies at all parks.",
         197: " Its tent sites are $24 (no utility fee).",
         4709: " The Weeping Ridge campground's full-facility sites."}


def rates(pid):
    out = {}
    for f in (RDR[str(pid)].get("facilities") or {}).values():
        m = re.match(r"Starting at \$([\d.]+)", f.get("rate") or "")
        if m and float(m.group(1)) > 0:
            out[f["name"].strip()] = float(m.group(1))
    return out


out = []
for eid, pid in sorted(PLACE.items()):
    r = rates(pid)
    if eid in BOOKING_ONLY:
        vals = {r[n] for n in BOOKING_ONLY[eid]}
        assert len(vals) == 1, (eid, vals)
        base, how = int(vals.pop()), "booking"
    else:
        text = re.sub(r"\s+", " ", " // ".join(PAGES[str(eid)]["camping"]))     # the pages use no-break spaces
        m = re.search(r"RV campsites \$(\d+) per night", text) or re.search(r"\$(\d+)(?: standard campsite)? per night", text)
        base, how = int(m.group(1)), "page"
        assert base in set(r.values()), (eid, base, r)          # the page agrees with the booking site
    rv = base + 7
    tent = "" if eid == 197 else f" (tent campers pay ${base})"
    text = (f"${rv} a night for an RV: the ${base} campsite fee plus Florida's $7 nightly utility fee for RVs{tent}, "
            f"plus tax and a $6.70 reservation fee per reservation." + EXTRA.get(eid, ""))
    if eid in MONROE:
        text += " Monroe County stays also carry a $2.50 nightly county surcharge."
    text += (" No out-of-state rate; Florida residents 65 and over get half off the campsite fee. "
             + ("The park's Hours & Fees page" if how == "page" else "Reserve Florida's rate line for the campground")
             + f" and Florida's fee page, read {D}.")
    src = (f"{PAGES[str(eid)]['url']} (camping fee, read {D}) + Reserve Florida PlaceId {pid} (each loop's 'Starting at' rate, "
           f"read {D}) + {STATEWIDE} ($7 nightly RV utility fee at all parks)") if how == "page" else \
          (f"Reserve Florida PlaceId {pid} (rdr/search/place: the campground's 'Starting at ${base}.00' rate line, read {D}; "
           f"its park page gives no camping fee) + {STATEWIDE} ($7 nightly RV utility fee at all parks)")
    out.append({"id": eid, "name": rows[eid]["name"], "fees": {
        "nightly_low": rv, "nightly_high": rv, "currency": "USD", "reservation_fee": 6.7, "checked": "2026", "note": text},
        "source": src})
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(out), 'FL park findings')
for x in out:
    print(x['id'], x['name'][:38], x['fees']['nightly_low'], '|', x['fees']['note'][:150])
