"""MD findings: each park's published campsite rate (dnr.maryland.gov service-charges page) as
charged by the booking site (parkreservations.maryland.gov) for 2027 nights, read 2026-10-12."""
import os, json, sys
out_path = sys.argv[1]
OC = "https://dnr.maryland.gov/publiclands/Pages/oc.aspx"
# id: (plain, electric, electric+water+sewer, parkId, extra note)
P = {63: (18.5, 27.5, None, 380118, ""), 82: (21.5, 27.5, None, 380107, ""),
     88: (10, None, None, 380102, "Primitive sites."), 89: (10, None, None, 380102, "Primitive sites."),
     423: (21.5, 27.5, None, 380134, ""), 424: (18.5, 24.5, None, 380117, ""),
     533: (15, None, None, 380109, ""), 550: (27.5, 38.5, None, 380101, ""),
     648: (21.5, 27.5, None, 380125, ""), 650: (21.5, 33.5, 38.5, 380123, ""),
     651: (18.5, 24.5, None, 380110, ""), 652: (21.5, 27.5, None, 380112, ""),
     653: (21.5, 27.5, None, 380105, ""), 654: (21.5, 27.5, None, 380105, ""),
     659: (21.5, 27.5, 36.5, 380108, ""), 824: (18.5, 24.5, None, 380120, ""),
     828: (21.5, 27.5, 32.5, 380133, "The electric sites include water."),
     681: (21.5, 27.5, None, 380116, ""), 825: (21.5, 27.5, None, 380121, ""),
     829: (18.5, 24.5, None, 380121, ""), 826: (None, 27.5, None, 380131, ""),
     827: (21.5, 27.5, None, 380132, ""), 830: (18.5, 24.5, None, 380104, ""),
     87: (10, None, None, 380136, "Primitive sites.")}
rows = {e['id']: e for e in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'campgrounds.json'), encoding='utf-8'))}
def m(x): return f"${x:.2f}"
out = []
for eid, (plain, elec, ews, pid, extra) in sorted(P.items()):
    fees = {"currency": "USD", "reservation_fee": 6.25, "checked": "2026"}
    s = {"weekend": 1}
    if plain is not None:
        fees["nightly_low"] = fees["nightly_high"] = plain
        if elec: s["electric"] = round(elec - plain, 2)
        if ews: s["full_hookup"] = round(ews - plain, 2)
        text = f"{m(plain)} a night" + (f", {m(elec)} with electric" if elec else "") + \
               (f", {m(ews)} with electric, water and sewer" if ews else "")
    else:
        fees["nightly_low"] = fees["nightly_high"] = elec
        text = f"Every campsite has electric: {m(elec)} a night"
    fees["surcharges"] = s
    text += "; $1 more on Friday and Saturday nights. " + (extra + " " if extra else "")
    text += ("$6.25 transaction fee per reservation; no out-of-state camping surcharge. Maryland Park Service's "
             "published rate for this park, read 2026-10-12; the booking site charged the same for 2027 nights.")
    fees["note"] = text
    fees = {k: fees[k] for k in ("nightly_low", "nightly_high", "currency", "reservation_fee", "nonresident",
                                 "surcharges", "checked", "note") if k in fees}
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees,
                "source": f"{OC} (this park's camping charges, read 2026-10-12) + parkreservations.maryland.gov parkId {pid} "
                          f"(per-site prices for 2027-06-15 and 2027-06-19, read 2026-10-12)"})
# Wolf Den Run: the booking site charged $10-11 where the service-charges page says $15.
w = next(x for x in out if x['id'] == 87)
w['fees']['nightly_high'] = 11
w['fees']['note'] = ("$10-11 a night on the booking site (2026-27 nights; Maryland's service-charges page lists $15); "
                     "$1 more on Friday and Saturday nights. Primitive sites. $6.25 transaction fee per reservation; "
                     "no out-of-state camping surcharge. Read 2026-10-12.")
w['source'] = w['source'].replace('2027-06-15 and 2027-06-19', '2026-11-10, 2027-06-15 and 2027-06-19')
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'MD findings'); print(out[0]['fees'])
