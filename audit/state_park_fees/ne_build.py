"""NH, VT, RI, CT and NJ findings, read 2026-10-12.

    python3 -I ne_build.py OUTDIR

Each state's published table, checked against its booking site (per-site 1-night prices in
ne_booking_checks_2026-10-12.log; Vermont's sampled sites in vt_booking_sample_2026-10-12.jsonl;
New Jersey's site list in nj_sites_2026-10-12.json). Writes OUTDIR/<st>_fees_2026-10-12.json."""
import json, os, sys
outdir = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"


def money(x):
    return f"${x:g}" if x == int(x) else f"${x:.2f}"


def finding(eid, low, high, note, source, res_fee=None, nonres=None, surcharges=None):
    fees = {"nightly_low": low, "nightly_high": high, "currency": "USD"}
    if res_fee is not None:
        fees["reservation_fee"] = res_fee
    if nonres:
        fees["nonresident"] = {"type": "surcharge", "amount": nonres, "per": "night"}
    if surcharges:
        fees["surcharges"] = surcharges
    fees["checked"] = "2026"
    fees["note"] = note
    return {"id": eid, "name": rows[eid]['name'], "fees": fees, "source": source}


# --- New Hampshire: statewide table by site type; the booking site charged the same for 2027 nights.
NH_T = "https://www.nhstateparks.org/fees-reservations/camping-rates-reservations"
NH_RA = "newhampshirestateparks.reserveamerica.com"
NH_TAIL = (" $7 reservation fee. The rate covers two adults and up to four children; each extra adult $10 a night, "
           "each extra child $5. No out-of-state surcharge; New Hampshire residents 65+ get $5 off a night "
           "(not on holidays{x}). NH State Parks' camping rate table, read {d}; the booking site charged the same for "
           "{when}.")
# id: (parkId, base, (surcharge key, amount) or None, what the base is, extra words, booking dates)
NH = {
    4103: (270003, 35, None, "a standard campsite", "", "2027 nights"),
    4113: (270011, 35, None, "a standard campsite", "", "2027 nights"),
    4107: (270015, 35, None, "a standard campsite", "", "2027 nights"),
    207: (270021, 60, None, "every RV site (waterfront, full hookups, 30 amp)", "", "2027 nights"),
    4101: (270027, 35, None, "a standard campsite", "", "2027 nights"),
    4106: (270044, 35, None, "a standard or platform campsite", "", "2027 nights"),
    4114: (270045, 35, ("electric", 10), "a standard campsite",
           " The 20-amp sites with water and electric are $45.", "2027 nights"),
    4112: (270050, 29, None, "a primitive campsite", "", "2027 nights"),
    4100: (270051, 35, ("electric", 10), "a standard or platform campsite",
           " The five RV/Trailer sites, which have 30-amp electric on the booking site, are $45.", "2027 nights"),
    4109: (270053, 35, None, "a standard campsite", "", "2027 nights"),
    4102: (270061, 35, None, "a standard campsite", "", "2027 nights"),
    4104: (270065, 29, None, "a primitive campsite", "", "2027 nights"),
    4111: (270082, 45, None, "every drive-in site (water and electric, 20/30 amp)",
           " The remote sites are priced separately.", "2027 nights"),
    4105: (270097, 35, None, "a standard campsite", "", "2027 nights"),
    4108: (270121, 50, None, "every site (full hookups, 30 amp)",
           " Off season, with electric only, the table's rate is $35.", "2027 nights"),
    4110: (270950, 35, ("full_hookup", 25), "a standard campsite",
           " The 19 RV sites with full 50-amp hookups are $60.", "2027 nights"),
    804: (270029, 70, None, "every RV site (full hookups)",
          " The table's Hampton dry-camping rate is $40.", "October 2026 nights (no 2027 night was open yet)"),
}
nh = []
for eid, (pid, base, sur, what, extra, when) in sorted(NH.items()):
    x = "; Hampton Beach and Ellacoya excluded" if eid in (207, 804) else ""
    note = f"{money(base)} a night for {what}." + extra + NH_TAIL.format(x=x, d=D, when=when)
    nh.append(finding(eid, base, base, note,
                      f"{NH_T} (statewide rates by site type, read {D}) + {NH_RA} parkId {pid} (per-site prices, "
                      f"{'2026-10-15 and 2026-10-17' if eid == 804 else '2027-06-15 and 2027-06-19'}, read {D})",
                      res_fee=7, surcharges=dict([sur]) if sur else None))

# --- Vermont: statewide, effective 2025-07-01; every sampled site on the booking site matched.
VT_T = "https://vtstateparks.com/camping"
VT_PRIME = {4072, 297, 4070, 4074, 4071, 4075, 4078, 299, 4073, 298, 204, 344, 4081, 362, 360, 4079, 675}
VT_PID = {4076: 1280011, 300: 1280013, 615: 1280014, 4072: 1280015, 301: 1280016, 297: 1280018, 4069: 1280019,
          4070: 1280021, 4074: 1280022, 4068: 1280024, 4071: 1280031, 4075: 1280032, 4078: 1280033, 4077: 1280034,
          299: 1280035, 4073: 1280036, 298: 1280039, 204: 1280042, 344: 1280053, 4082: 1280057, 4080: 1280071,
          4081: 1280073, 362: 1280075, 360: 1280078, 359: 1280081, 4079: 1280082, 675: 1280085}
vt = []
for eid, pid in sorted(VT_PID.items()):
    prime = eid in VT_PRIME
    note = ("$20 a night for a Vermont resident, $38 for a non-resident (tent/RV site, up to 4 people; $8 for each "
            "extra person, 8 at most)" + ("; prime sites $2 more" if prime else "") +
            ". Pets $3 each a night. $8 non-refundable reservation fee per site. No hookups. Vermont State Parks' "
            f"camping fees (in effect since 2025-07-01), read {D}; the booking site charged the same for 2027 nights.")
    s = {"pet": 3}
    if prime:
        s["premium_site"] = 2
    vt.append(finding(eid, 20, 20, note,
                      f"{VT_T} (Camping Fees: 'Updated prices in effect starting July 1, 2025', read {D}) + "
                      f"vtstateparks-visit.com parkId {pid} (sampled sites' resident / non-resident prices for "
                      f"2027-06-15, read {D})", res_fee=8, nonres=18, surcharges=s))

# --- Rhode Island: the fee regulation's three tiers; the booking site's October 2026 prices.
RI_T = ("https://rules.sos.ri.gov/regulations/Part/250-100-00-8 (250-RICR-100-00-8, 'Camping - Daily Site "
        "Reservations' tiers, read 2026-10-12)")
RI_TAIL = (" $8.75 reservation fee. 2027 reservations are on hold while Rhode Island DEM picks a new reservation "
           f"provider (riparks.ri.gov, {D}). Rhode Island's fee regulation, read {D}; the booking site charged the "
           "same for October 2026 nights.")
ri = []
for eid, pid, extra in [(205, 253123, ""), (206, 252711, ""),
                        (4170, 252741, " Self-contained RVs only.")]:
    ri.append(finding(eid, 18, 18, "$18 a night for a Rhode Island resident, $36 for a non-resident (tier 3)." + extra + RI_TAIL,
                      f"{RI_T} + rhodeislandstateparks.reserveamerica.com parkId {pid} (per-site prices for 2026-10-20 and "
                      f"2026-10-24, read {D})", res_fee=8.75, nonres=18))
ri.append(finding(4171, 24, 28,
                  "Every RV site has hookups: water and electric (30 amp) $24 a night for a Rhode Island resident, $45 "
                  "for a non-resident (tier 2, area 4); water, electric and sewer $28, non-resident $55 (tier 1, areas 1 "
                  "and 2)." + RI_TAIL,
                  f"{RI_T} + rhodeislandstateparks.reserveamerica.com parkId 252611 (15 sampled sites' prices and hookups "
                  f"for 2026-10-20, read {D})", res_fee=8.75, nonres=21))

# --- Connecticut: DEEP's parking and camping fee table; the booking site charged the same for 2027 nights.
CT_T = "https://portal.ct.gov/DEEP/State-Parks/Parking-and-Camping-Fees---CT-State-Parks-and-Forests"
CT_TAIL = (" $9 reservation fee. DEEP's camping fee table (content last updated October 2024), read {d}; the booking "
           "site charged the same resident rates for 2027 nights.")
# id: (parkId, base, nonres amount, surcharges, sentence)
CT = {
    211: (100102, 17, 10, {"electric": 10}, "$17 a night for a Connecticut resident, $27 for a non-resident; electric sites $27."),
    212: (100101, 20, 10, {"electric": 15}, "$20 a night for a Connecticut resident, $30 for a non-resident; electric sites $35 ($45 non-resident)."),
    4051: (100107, 20, 10, None, "$20 a night for a Connecticut resident, $30 for a non-resident."),
    4052: (100104, 14, 10, None, "$14 a night for a Connecticut resident, $24 for a non-resident."),
    4053: (100802, 17, 10, None, "$17 a night for a Connecticut resident, $27 for a non-resident."),
    4054: (100800, 17, 10, None, "$17 a night for a Connecticut resident, $27 for a non-resident."),
    4055: (100100, 17, 10, {"electric": 10}, "$17 a night for a Connecticut resident, $27 for a non-resident; electric sites $27."),
    4056: (100128, 33, 12, {"electric": 4, "full_hookup": 7},
           "$33 a night for a Connecticut resident, $45 for a non-resident; water and electric (30 amp) $37 ($48 "
           "non-resident); full hookups (50 amp) $40 ($52 non-resident)."),
    4057: (100110, 17, 10, None, "$17 a night for a Connecticut resident, $27 for a non-resident."),
    4058: (100105, 14, 10, None, "$14 a night for a Connecticut resident, $24 for a non-resident."),
    4059: (100108, 17, 10, None, "$17 a night for a Connecticut resident, $27 for a non-resident."),
    4060: (100106, 14, 10, None, "$14 a night for a Connecticut resident, $24 for a non-resident. The loop's one "
           "water/electric site (20) is $29."),
    4061: (100106, 14, 10, None, "$14 a night for a Connecticut resident, $24 for a non-resident."),
    4062: (100103, 17, 10, None, "$17 a night for a Connecticut resident, $27 for a non-resident."),
}
ct = []
for eid, (pid, base, nr, s, text) in sorted(CT.items()):
    ct.append(finding(eid, base, base, text + CT_TAIL.format(d=D),
                      f"{CT_T} (this park's camping line, read {D}) + connecticutstateparks.reserveamerica.com parkId {pid} "
                      f"(per-site prices for 2027-06-15 and 2027-06-19, read {D})", res_fee=9, nonres=nr, surcharges=s))

# --- New Jersey: NJ Outdoors lists every site with its resident / non-resident cost.
NJ_TAIL = f" Every site's cost as listed on NJ Outdoors, the state's booking site, read {D}."
NJ = {616: (12, True), 1807: (2, False), 1808: (3, False), 1809: (4, True), 1810: (5, False), 1811: (6, False),
      1812: (20, False), 1813: (10, False), 1814: (15, False), 1815: (16, False), 1816: (13, False),
      1817: (8, False), 1820: (19, False)}
nj = []
for eid, (loc, we) in sorted(NJ.items()):
    text = "$20 a night for a New Jersey resident, $25 for a non-resident (tent/trailer site, up to 6 people)"
    if we:
        text += "; sites with water and electric hookups $30 ($35 non-resident)"
    if eid == 1820:
        text += ". The forest's primitive camping areas are $3 a person ($5 non-resident)"
    nj.append(finding(eid, 20, 20, text + "." + NJ_TAIL,
                      f"https://www.njportal.com/DEP/NJOutdoors/Park/Details?locationId={loc} (each site's cost, read {D})",
                      nonres=5, surcharges={"electric": 10} if we else None))

for st, data in (("nh", nh), ("vt", vt), ("ri", ri), ("ct", ct), ("nj", nj)):
    json.dump(data, open(os.path.join(outdir, f"{st}_fees_{D}.json"), "w"), indent=1, ensure_ascii=False)
    print(st, len(data))
