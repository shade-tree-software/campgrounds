"""Nova Scotia findings: Nova Scotia Parks' 2026 price table (ns_fee_page_2026-10-12.txt, from
https://parks.novascotia.ca/camping-fees) and its booking site (novascotia.goingtocamp.com), every park's unserviced
and serviced campsite fee schedules for Tue 2027-07-13 and Sat 2027-07-17 (gtc_probe.py ->
ns_booking_fees_2026-10-12.json).

    python3 -I ns_build.py OUT

'All prices include applicable taxes': Unserviced Campsite $26.50 per night, Serviced Campsite $35.30 per night
(Mira River's page: 'two way hook up (30 amp electrical service and drinking water)'), Reservation Fee $8.95,
additional vehicle $8.25 per night, senior (65+) and veteran discounts $2.35 per night. The booking site charges
exactly those two prices at every park, Saturday the same. Laurie and Thomas Raddall each list ONE serviced site
(Laurie's site 19, Thomas Raddall's 'H1') while their park pages list unserviced sites only, so they get no electric
surcharge (a lone hookup site
may be the host's, as in recgov_hookups.py)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
PAGE = "https://parks.novascotia.ca/camping-fees"
UNS, SER = 26.5, 35.3
probe = json.load(open(os.path.join(HERE, "ns_booking_fees_2026-10-12.json"), encoding="utf-8"))
parks = {}
for p in probe["parks"]:
    k = {}
    for s in p["schedules"]:
        vals = {f[0] for fees in s["fees"].values() for f in fees}
        k.setdefault(s["category"], [0, set()])
        k[s["category"]][0] += s["n"]
        k[s["category"]][1] |= vals
    parks[p["park"].lower().replace("-", " ").replace(" island", "")] = k


def norm(n):
    return n.lower().replace("-", " ").replace(" island", "")


out = []
for eid in sorted(e["id"] for e in rows.values() if e.get("state") == "NS" and e.get("ownership") == "provincial"):
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    k = parks[norm(e["name"])]
    assert k["Unserviced Campsite"][1] == {UNS}, (eid, k)
    nser = k.get("Serviced Campsite", [0, set()])
    if nser[0]:
        assert nser[1] == {SER}, (eid, k)
    serviced = nser[0] > 1
    fees = {"nightly_low": UNS, "nightly_high": UNS, "currency": "CAD", "reservation_fee": 8.95,
            "surcharges": ({"electric": round(SER - UNS, 2)} if serviced else {}) | {"weekend": 0}, "checked": "2026",
            "note": ("$26.50 a night for an unserviced site" + ("; serviced sites (electric hookup) $35.30" if serviced else "")
                     + ", taxes included, the same every night; no out-of-province rate. $8.95 reservation fee per booking; "
                     "an extra vehicle is $8.25 a night. Seniors 65+ and veterans get $2.35 a night off. Nova Scotia Parks' "
                     f"2026 prices and its booking site (2027 nights), read {D}.")}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{PAGE} ('2026 Prices ... All prices include applicable taxes': Unserviced Campsite $26.50, Serviced "
                          f"Campsite $35.30, Reservation Fee $8.95) + novascotia.goingtocamp.com/api/resource/feeDetails "
                          f"({nser[0] if serviced else 0} serviced / {k['Unserviced Campsite'][0]} unserviced sites, 2027-07-13 "
                          f"and 2027-07-17), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NS findings")
for x in out:
    print(x["id"], x["name"][:36], x["fees"]["nightly_low"], x["fees"]["surcharges"], "|", x["source"][-75:])
