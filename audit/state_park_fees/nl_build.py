"""Newfoundland and Labrador findings: ParksNL's fee page (https://www.parksnl.ca/reservations/, read 2026-10-12) and
its booking site (www.nlcamping.ca, a GoingToCamp host), every park's short-stay fee schedules for Tue 2027-07-13 and
three Saturdays at Dildo Run and Butter Pot (gtc_probe.py -> nl_booking_fees_2026-10-12.json).

    python3 -I nl_build.py OUT

The fee page: 'Nightly campsite' $20.15 unserviced ('Unserviced campsites are available in all 13 campgrounds') and
$30.90 serviced ('15-50 amp electrical service ... Campsite water service is also available at some campgrounds';
'Serviced campsites can be found at Dildo Run, Frenchman's Cove, J.T. Cheeseman, La Manche, Lockston Path, and Notre
Dame'). 'Nightly Vehicle Pass: Vehicle entry for a night of camping, $7' (day pass $10, seasonal pass to all
provincial parks $50); 'a reservation fee of $7.00 (incl. tax) is applied ... for each call and/or online
transaction'; residents 65+ get 35% off campsite and vehicle entry fees. The booking site answers $20.15 and $30.90
(plus the weekly $123.59 / $190.76) for exactly those parks, the same on Saturdays. No out-of-province rate."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
PAGE = "https://www.parksnl.ca/reservations/"
UNSERVICED, SERVICED = 20.15, 30.90
probe = json.load(open(os.path.join(HERE, "nl_booking_fees_2026-10-12.json"), encoding="utf-8"))
nightly = {}
for p in probe["parks"]:
    vals = set()
    for s in p["schedules"]:
        for fees in s["fees"].values():
            vals.add(min(f[0] for f in fees))          # the nightly fee; the other is the weekly one
    nightly[p["park"]] = vals
out = []
for eid in sorted(e["id"] for e in rows.values() if e.get("state") == "NL" and e.get("ownership") == "provincial"):
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    park = [n for n in nightly if n.lower().replace("'", "") == e["name"].lower().replace("’", "").replace("'", "")]
    assert park, e["name"]
    vals = nightly[park[0]]
    assert vals <= {UNSERVICED, SERVICED} and UNSERVICED in vals, (eid, vals)
    serviced = SERVICED in vals
    fees = {"nightly_low": UNSERVICED, "nightly_high": UNSERVICED, "currency": "CAD", "reservation_fee": 7,
            "entrance": {"resident": 7, "nonresident": 7, "per": "vehicle_day"},
            "surcharges": ({"electric": round(SERVICED - UNSERVICED, 2)} if serviced else {}) | {"weekend": 0},
            "checked": "2026",
            "note": ("$20.15 a night for an unserviced site" + ("; serviced sites (electric, water at some) $30.90" if serviced
                     else "; no serviced sites here") + ". The same every night of the week, and no out-of-province rate. "
                     "Each vehicle also needs the $7 nightly vehicle pass (or a $50 seasonal pass to all provincial parks), "
                     "and each booking carries a $7.00 reservation fee (incl. tax). Residents of the province aged 65+ get "
                     f"35% off. ParksNL's fee page and booking site (2027 nights), read {D}.")}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{PAGE} ('Nightly campsite' $20.15 unserviced / $30.90 serviced; 'Nightly Vehicle Pass ... $7'; "
                          f"reservation fee $7.00 incl. tax) + www.nlcamping.ca/api/resource/feeDetails ({park[0]}: "
                          f"{', '.join(f'${v:.2f}' for v in sorted(vals))} a night, 2027-07-13), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NL findings")
for x in out:
    print(x["id"], x["name"][:40], x["fees"]["nightly_low"], x["fees"]["surcharges"])
