"""Prince Edward Island findings: PEI Provincial Parks' 2026 rate table (pe_fee_page_2026-10-12.txt, from
https://www.peiprovincialparks.ca/articles/camping/pei-provincial-parks-fees-and-operating-dates) and every
nightly site of each park on its booking site, with its service type and equipment length (ra_list.py ->
pe_sites_2026-10-12.json). The booking site prices nothing between seasons (2027 opens to bookings in the spring).

    python3 -I pe_build.py OUT

'The following Rates apply to all of the Provincial Park Campgrounds. HST (15%) and Transaction Fees are applicable
to all reservations': Unserviced $38, Two-way Service (electricity and water) $45, Three-way Service (electricity,
water and sewer) $50; '$6.00 + HST reservation'; seniors 60+ and disabled persons 10% off the daily rate. The base
is the unserviced site where one takes a 23-ft rig; Cedar Dunes' unserviced sites are 21 ft or tent pads, so its
base is the two-way site, as for Virginia's short no-hookup sites."""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
PAGE = "https://www.peiprovincialparks.ca/articles/camping/pei-provincial-parks-fees-and-operating-dates"
RATE = {"No Service": 38, "2 way": 45, "3 way": 50}
WORD = {"No Service": "an unserviced site", "2 way": "two-way (electric and water)", "3 way": "three-way (full hookups)"}
PARK = {13002: "320025", 13003: "320021", 13004: "320022", 13005: "320023", 13006: "320024", 13007: "320026",
        13008: "320027", 13009: "320028"}
sites = {p["parkId"]: p["sites"] for p in json.load(open(os.path.join(HERE, "pe_sites_2026-10-12.json")))["parks"]}
out = []
for eid, pid in PARK.items():
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    fit = collections.Counter()
    for s in sites[pid]:
        c = s["cells"]
        if len(c) > 3 and c[1] in RATE and c[3].isdigit() and int(c[3]) >= 23:
            fit[c[1]] += 1
    kinds = [k for k in RATE if fit[k]]
    base = RATE[kinds[0]]
    sur = {}
    if kinds[0] == "No Service" and "2 way" in kinds:
        sur["electric"] = RATE["2 way"] - base
    if "3 way" in kinds:
        sur["full_hookup"] = RATE["3 way"] - base
    sur["weekend"] = 0
    parts = [f"${RATE[k]} a night for {WORD[k]}" if i == 0 else f"{WORD[k]} ${RATE[k]}" for i, k in enumerate(kinds)]
    text = "; ".join(parts) + ", the same every night"
    if kinds[0] != "No Service":
        text += " (the unserviced sites here are 21 ft or shorter)"
    elif fit["No Service"] == 1:
        text += " (only one unserviced site here is long enough for a 23-ft rig)"
    text += (". Plus 15% HST, and a $6 + HST reservation fee per booking. Seniors 60+ and disabled persons get 10% off. "
             f"PEI Provincial Parks' 2026 rate table, which applies to every provincial campground, and the park's sites on "
             f"its booking site, read {D}.")
    fees = {"nightly_low": base, "nightly_high": base, "currency": "CAD", "reservation_fee": 6, "surcharges": sur,
            "checked": "2026", "note": text}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{PAGE} ('CAMPGROUND SERVICE RATES 2026': Unserviced $38.00, Two-way Service $45.00, Three-way "
                          f"Service $50.00; '$6.00 + HST reservation') + www.peiprovincialparks.ca parkId {pid} site list "
                          f"(RV-length sites by service type: {dict(fit)}), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "PE findings")
for x in out:
    print(x["id"], x["name"][:34], x["fees"]["nightly_low"], x["fees"]["surcharges"], "|", x["source"][-80:])
