"""NY findings, read 2026-10-12.

    python3 -I ny_build.py OUT

State Parks (OPRHP) campgrounds: the statewide rate schedule at parks.ny.gov/camping/fees-policies
(base $17, flagship campgrounds $3 more; electric 15/20/30 amp +$7, 50 amp +$9; full hookups +$13 /
+$15; waterfront +$6; Friday, Saturday and the night before a holiday +$4; non-residents +$5 a night;
$7.25 reservation fee), applied to what each park's sites cost on the booking site for Tuesday
2027-06-15 and Saturday 2027-06-19 (ny_booking_sample_2026-10-12.jsonl: sites taken across the whole
site list, with each one's electric/water/sewer hookups).

DEC campgrounds: DEC's 2026 Summer Recreation Campground Summary (revised 1/12/26), one flat
nightly fee per campground, non-residents +$5 a night; five of them were checked on the booking site
for the same two nights and charged exactly the summary's fee, with no weekend difference."""
import json, os, sys
out_path = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
SCHED = "https://parks.ny.gov/camping/fees-policies"
DEC = "https://dec.ny.gov/sites/default/files/2025-04/summerreccampgroundsummary.pdf"
RA = "newyorkstateparks.reserveamerica.com"
# OPRHP: id: (parkId, low, high, surcharges, flagship, sentence)
# low/high = the plain site; when every sampled RV site had electric, the electric site IS the plain site.
P = {
    143: (232, 24, 24, {}, False, "Every RV site has 20/30-amp electric: $24 a night."),
    214: (375, 27, 29, {}, True, "Every sampled site has electric: $27 a night with 30 amp, $29 with 50 amp."),
    310: (427, 20, 20, {"electric": 7, "waterfront": 6}, True, "$20 a night; electric (30 amp) +$7; waterfront +$6."),
    311: (361, 20, 20, {"electric": 7, "waterfront": 6}, True, "$20 a night; electric (30 amp) +$7; waterfront +$6."),
    312: (456, 17, 17, {}, False, "$17 a night (no electric site came up in the sample)."),
    313: (459, 20, 20, {"electric": 7, "waterfront": 6}, True, "$20 a night; electric (30 amp) +$7; waterfront +$6."),
    314: (452, 17, 17, {"electric": 7, "waterfront": 6}, False, "$17 a night; electric (15 amp) +$7; waterfront +$6."),
    316: (240, 20, 20, {"electric": 7, "waterfront": 6, "full_hookup": 13}, True,
          "$20 a night; electric +$7 (20/30 amp) or +$9 (50 amp); waterfront +$6; full hookups +$13 (+$15 with 50 amp)."),
    317: (447, 17, 17, {"electric": 7, "waterfront": 6}, False, "$17 a night; electric (30 amp) +$7; waterfront +$6."),
    318: (474, 20, 20, {"electric": 7, "waterfront": 6, "full_hookup": 13}, True,
          "$20 a night; electric (30 amp) +$7; waterfront +$6; full hookups +$13 (+$15 with 50 amp)."),
    319: (175, 20, 20, {"electric": 7}, True, "$20 a night; electric +$7 (30 amp) or +$9 (50 amp)."),
    321: (336, 20, 20, {"electric": 7, "waterfront": 6}, True, "$20 a night; electric +$7 (30 amp) or +$9 (50 amp); waterfront +$6."),
    322: (302, 17, 17, {"electric": 7, "waterfront": 6}, False, "$17 a night; electric +$7 (20/30 amp) or +$9 (50 amp); waterfront +$6."),
    323: (433, 17, 17, {"electric": 7, "waterfront": 6}, False, "$17 a night; electric (30 amp) +$7; waterfront +$6."),
    324: (19, 17, 17, {}, False, "$17 a night; no electric sites."),
    325: (82, 24, 26, {}, False, "Every sampled site has electric: $24 a night with 30 amp, $26 with 50 amp."),
    326: (72, 17, 17, {}, False, "$17 a night; no electric or water at the sites."),
    327: (64, 17, 17, {"electric": 7}, False, "$17 a night; electric +$7 (30 amp) or +$9 (50 amp)."),
    328: (78, 14, 14, {"electric": 10}, False, "$14 a night for a primitive site; electric (30 amp) sites $24."),
    329: (56, 24, 24, {"waterfront": 6}, False, "Every site has electric: $24 a night (30 amp); waterfront +$6 ($32 with 50 amp)."),
    330: (44, 17, 17, {"electric": 7}, False, "$17 a night; electric +$7 (30 amp) or +$9 (50 amp)."),
    331: (165, 20, 20, {"electric": 7, "full_hookup": 15}, True, "$20 a night; electric (30 amp) +$7; full hookups (50 amp) +$15."),
    332: (368, 17, 17, {"electric": 9}, False, "$17 a night; electric (50 amp) +$9."),
    333: (170, 27, 29, {}, True, "Every sampled site has electric: $27 a night with 30 amp, $29 with 50 amp."),
    335: (347, 20, 20, {"electric": 7, "waterfront": 6, "full_hookup": 13}, True,
          "$20 a night; electric (30 amp) +$7; waterfront +$6; full hookups +$13."),
    336: (343, 17, 17, {"electric": 7, "waterfront": 6}, False,
          "$17 a night (the schedule's low end for this park; the sampled non-electric site was a $23 waterfront one); electric (30 amp) +$7; waterfront +$6."),
    338: (468, 20, 20, {"electric": 7}, True, "$20 a night; electric (15/20/30 amp) +$7."),
    339: (280, 24, 26, {}, False, "Every sampled site has electric: $24 a night with 30 amp, $26 with 50 amp."),
    340: (317, 17, 17, {"electric": 7, "waterfront": 6}, False,
          "$17 a night; electric +$7 (30 amp) or +$9 (50 amp), these sites with water; waterfront +$6."),
    349: (439, 17, 17, {"electric": 7}, False, "$17 a night; electric (15 amp) +$7."),
    466: (409, 17, 17, {}, False, "$17 a night; no hookups."),
    641: (288, 20, 20, {"full_hookup": 13}, True, "$20 a night ($23 for some sites); full hookups +$13."),
}
TAIL = (" Friday, Saturday and the night before a holiday +$4; non-residents +$5 a night; $7.25 reservation fee."
        "{flag} NY State Parks' rate schedule, read {d}; the booking site charged these for 2027 nights.")
out = []
for eid, (pid, low, high, s, flag, text) in sorted(P.items()):
    surch = dict(s)
    surch["weekend"] = 4
    fees = {"nightly_low": low, "nightly_high": high, "currency": "USD", "reservation_fee": 7.25,
            "nonresident": {"type": "surcharge", "amount": 5, "per": "night"}, "surcharges": surch,
            "checked": "2026",
            "note": text + TAIL.format(flag=" A flagship campground: $3 more than the $17 base." if flag else "", d=D)}
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees,
                "source": f"{SCHED} (statewide rates and this park's range, read {D}) + {RA} parkId {pid} (sampled sites' "
                          f"prices and hookups for 2027-06-15 and 2027-06-19, read {D})"})
# DEC: one fee per campground (2026 summary); parkIds checked on the booking site marked.
DECF = {287: ("Cranberry Lake", 20, None), 309: ("Lake George Battleground", 22, 122), 341: ("Lake Harris", 18, None),
        342: ("Wilmington Notch", 18, None), 343: ("Meadowbrook", 18, None), 345: ("Scaroon Manor", 25, 3386),
        346: ("Putnam Pond", 18, None), 348: ("Lake Eaton", 20, None), 350: ("Nicks Lake", 22, None),
        351: ("Moffitt Beach", 22, 673), 353: ("Lewey Lake", 20, None), 354: ("Lake Durant", 20, None),
        355: ("Golden Beach", 20, None), 356: ("Eighth Lake", 22, None), 357: ("Meacham Lake", 20, None),
        358: ("Fish Creek", 22, 574), 363: ("Crown Point", 18, 573), 364: ("Northampton Beach", 22, None),
        365: ("Buck Pond", 20, None), 366: ("Rollins Pond", 20, None)}
for eid, (nm, fee, pid) in sorted(DECF.items()):
    note = (f"${fee} a night; non-residents +$5 a night; $7.25 reservation fee. No hookups. DEC's 2026 campground "
            f"summary, read {D}" + ("; the booking site charged the same for 2027 nights, weekend or not." if pid else
                                    "; five other DEC campgrounds charged exactly their summary fee on the booking site for 2027 nights."))
    if eid == 345:
        note = note.replace("$25 a night;", "$25 a night ($20 for some sites);")
    fees = {"nightly_low": fee, "nightly_high": fee, "currency": "USD", "reservation_fee": 7.25,
            "nonresident": {"type": "surcharge", "amount": 5, "per": "night"}, "checked": "2026", "note": note}
    src = f"{DEC} (DEC 2026 Summer Recreation Campground Summary, revised 1/12/26: '{nm}' ${fee}.00; '* Non-New York State residents will be charged an additional $5/night', read {D})"
    if pid:
        src += f" + {RA} parkId {pid} (sampled sites' prices for 2027-06-15 and 2027-06-19, read {D})"
    out.append({"id": eid, "name": rows[eid]['name'], "fees": fees, "source": src})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'NY findings')
