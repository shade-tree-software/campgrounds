"""Findings for apply.py from pa_parks.json (PA DCNR statewide table + each park's site types)."""
import json, sys
src = json.load(open(sys.argv[1])); out_path = sys.argv[2]
TABLE = "https://www.pa.gov/agencies/dcnr/recreation/where-to-go/state-parks/state-park-prices/camping.html"
CHECKED = ("the booking site charged exactly these for 2027 nights at Gifford Pinchot, Cherry Springs, "
           "Poe Paddy and Cook Forest (2026-10-12)")
def build(eid, name, loops, amen, pid, fcfs=False):
    modern = bool({'modern', 'modern-rustic'} & set(loops)); rustic = 'rustic' in loops
    lo, hi = (16 if rustic else 20), (20 if modern else 16)
    s = {"weekend": 4}
    if 'electric' in amen: s["electric"] = 7
    if 'full' in amen: s["full_hookup"] = 21
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "USD", "reservation_fee": 6.5,
            "nonresident": {"type": "surcharge", "amount": 5, "per": "night"}, "surcharges": s, "checked": "2026"}
    if modern and rustic:
        base = ("$16 a night for a Pennsylvania resident in the rustic loop, $20 in the modern loop (showers), "
                "$4 more on Friday, Saturday and holiday nights")
    elif modern:
        base = "$20 a night for a Pennsylvania resident (modern campground, showers), $24 on Friday, Saturday and holiday nights"
    else:
        base = "$16 a night for a Pennsylvania resident (rustic campground, no showers), $20 on Friday, Saturday and holiday nights"
    if 'electric' in amen: base += "; electric +$7"
    if 'full' in amen: base += "; full hookup +$21"
    parts = [base + "."]
    if amen and 'none' not in amen:
        parts.append(f"Every RV site has electric, so ${lo + 7}" + (f"-{hi + 7}" if hi != lo else "") + " on a weeknight.")
    parts.append("Non-residents +$5 a night; $6.50 transaction fee per reservation or registration; designated pet sites +$2.")
    if fcfs: parts.append("First come, first served: register and pay at the park.")
    parts.append("DCNR's statewide price table, read 2026-10-12; the booking site charged the same for 2027 nights.")
    fees["note"] = " ".join(parts)
    where = f"this park's site types on pennsylvaniastateparks.reserveamerica.com (parkId {pid})" if pid else \
            "our entry's site description (rustic, no hookups; not on the booking site)"
    return {"id": eid, "name": name, "fees": fees,
            "source": f"{TABLE} (statewide table, read 2026-10-12) + {where}; {CHECKED}"}
findings = [build(p['id'], p['name'], p['loops'], [a for a in p['amen']], p['parkId']) for p in src['parks']]
findings.append(build(1060, "Colton Point State Park", ['rustic'], ['none'], None, fcfs=True))
json.dump(findings, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(findings), 'PA findings'); print(json.dumps(findings[0], ensure_ascii=False, indent=1)[:1600])
print(json.dumps([f for f in findings if f['id'] == 860][0]['fees'], ensure_ascii=False)[:900])
