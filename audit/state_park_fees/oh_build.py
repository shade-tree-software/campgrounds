"""OH findings: ReserveOhio's nightly rate per site type (rdr_rates.py -> oh_booking_rates_2026-10-12.jsonl), sampled for
Tue 2027-06-15 and Sat 2027-06-19, read 2026-10-12; plus Camp Perry RV Park from its own page.

    python3 -I oh_build.py RATES OUT

Ohio publishes no camping rate table; the booking site prices each site type per park (the call its page makes when a
site is clicked returns {"Rate": "41.00", "Fee": "6.50"}). The base is the cheapest site an RV can use: non-electric
where the park has it, else electric; electric and full hookups are surcharges on it, premium sites go in the note.
The $6.50 reservation fee and 'no non-resident rate difference' are the state:OH registry row's (ohiodnr.gov reservation
policy). Tent-only, walk-in, cabin, 'Cabent' and group types are left out by rdr_rates.py or here."""
import collections, json, os, re, sys
rates_path, out_path = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))
D = "2026-10-12"
SAT = "2027-06-19"


# Malabar Farm's campground: ReserveOhio types every site 'Campsite Equestrian Non-Electric', but ODNR's page says its
# 'Non-electric campsites ... can accommodate equestrian campers' - a general campground that also takes horses.
EQUESTRIAN_OK = {361}


def kind(t, pid=None):
    if pid in EQUESTRIAN_OK and re.search(r"(?i)equestrian non.?electric", t):
        return "ne"
    if re.search(r"(?i)cabent|cabin|tent|group|walk|equest|horse", t):
        return None
    prem = "prem_" if re.search(r"(?i)premium", t) else ""
    if re.search(r"(?i)non.?electric", t):
        return prem + "ne"
    if re.search(r"(?i)full hookup", t):
        return prem + "fhu"
    if re.search(r"(?i)electric", t):
        return prem + "e"
    return None


park = collections.defaultdict(lambda: collections.defaultdict(list))
sat = collections.defaultdict(dict)
names = {}
for line in open(rates_path):
    r = json.loads(line)
    if "error" in r or not r.get("rate"):
        continue
    k = kind(r["unitType"], r["placeId"])
    if k is None:
        continue
    p = float(r["rate"])
    names[r["placeId"]] = r["park"]
    if r["date"] == SAT:
        sat[r["placeId"]][(k, r["unitId"])] = p
    else:
        park[r["placeId"]][k].append(p)
        park[r["placeId"]]["tue:" + k + ":" + str(r["unitId"])].append(p)


def rng(vals):
    lo, hi = min(vals), max(vals)
    return f"${lo:g}" if lo == hi else f"${lo:g}-{hi:g}"


by_pid = collections.defaultdict(list)
for e in rows:
    if e.get("state") == "OH" and e.get("ownership") == "state" and not e.get("fees"):
        m = re.search(r"#!park/(\d+)", e.get("website") or "")
        if m:
            by_pid[int(m.group(1))].append(e)
out = []
for pid, ents in sorted(by_pid.items()):
    d = park.get(pid)
    if not d or not any(d.get(k) for k in ("ne", "e", "fhu", "prem_ne", "prem_e", "prem_fhu")):
        print("no prices", pid, [e["name"] for e in ents])
        continue
    ne = d.get("ne") or []
    e_ = d.get("e") or []
    fhu = d.get("fhu") or []
    prem = {k: d[k] for k in ("prem_ne", "prem_e", "prem_fhu") if d.get(k)}
    if ne:
        base = min(ne)
    elif e_:
        base = min(e_)
    elif fhu:
        base = min(fhu)
    else:
        base = min(min(v) for v in prem.values())
    s, parts = {}, []
    if ne:
        parts.append(f"{rng(ne)} a night for a site without electric")
        if e_:
            parts.append(f"electric {rng(e_)}")
            s["electric"] = round(min(e_) - base, 2)
    elif e_:
        parts.append(f"Every RV site has electric: {rng(e_)} a night")
    if fhu:
        parts.append(f"full hookups {rng(fhu)}")
        s["full_hookup"] = round(min(fhu) - base, 2)
    if not ne and not e_ and fhu:
        parts[-1] = f"Every RV site has full hookups: {rng(fhu)} a night"
        s.pop("full_hookup", None)
    label = {"prem_ne": "premium sites without electric", "prem_e": "premium electric sites", "prem_fhu": "premium full-hookup sites"}
    for k, v in prem.items():
        parts.append(f"{label[k]} {rng(v)}")
    # weekend: a Saturday that costs more than the same unit's Tuesday
    diffs = []
    for (k, uid), p in sat.get(pid, {}).items():
        t = d.get(f"tue:{k}:{uid}")
        if t:
            diffs.append(round(p - t[0], 2))
    wk = min((x for x in diffs if x > 0), default=0) if diffs and all(x > 0 for x in diffs) else 0
    text = "; ".join(parts) + "."
    if wk:
        s["weekend"] = wk
        text += f" Saturday +${wk:g}."
    elif diffs and all(x == 0 for x in diffs):
        text += " The same on a Saturday."
    elif diffs:
        text += " Some sites cost more on a Saturday (" + ", ".join(f"+${x:g}" for x in sorted(set(diffs)) if x) + ")."
    if pid in EQUESTRIAN_OK:
        text += " ReserveOhio lists every site as an equestrian non-electric campsite; ODNR says they also take other campers."
    text += (f" Plus tax and a $6.50 reservation fee per reservation; no out-of-state rate. ReserveOhio's prices for "
             f"June 2027 nights, read {D}.")
    fees = {"nightly_low": base if base % 1 else int(base), "nightly_high": base if base % 1 else int(base), "currency": "USD"}
    if s:
        fees["surcharges"] = {k: (v if v % 1 else int(v)) for k, v in s.items()}
    fees["checked"] = "2026"
    fees["note"] = text
    for ent in ents:
        out.append({"id": ent["id"], "name": ent["name"], "fees": dict(fees),
                    "source": f"ReserveOhio PlaceId {pid} ({names[pid]}): each campsite type's nightly rate from "
                              f"rdr/search/details for sampled sites, 2027-06-15 and 2027-06-19, read {D} "
                              f"(oh_booking_rates_2026-10-12.jsonl)"})
# Strouds Run: its campground is not on ReserveOhio (only the shelters are); the park's concession runs it first come
out.append({"id": 1028, "name": "Strouds Run State Park", "fees": {
    "nightly_low": 15, "nightly_high": 20, "currency": "USD", "checked": "2026",
    "note": ("$20 a night April 1 to the first Sunday in December, $15 the rest of the year (sites 19 and 20, with a shelter, "
             "$25 / $20). First come, first served with self-registration envelopes; the park's concession, Strouds Run "
             f"Rentals, runs the campground. Read {D}.")},
    "source": f"https://www.stroudsrunrentals.com/campground ('In-Season Rates ... Campsites: $20/night', 'Off-Season Rates ... "
              f"Campsites: $15/night', read {D}; ODNR's park page sends campers there)"})
# Camp Perry RV Park: the Ohio National Guard's RV park, not on ReserveOhio; its page gives only a range
out.append({"id": 14313, "name": "Camp Perry RV Park", "fees": {
    "nightly_low": 35, "nightly_high": 53.94, "currency": "USD", "checked": "2026",
    "note": ("$35.00-$53.94 a night, $800 a month; the RV park's page gives only the range. Every site has 30/50-amp "
             f"electric, water and sewer. Read {D}.")},
    "source": f"https://cplcc.com/recreational-vehicle-camp/ ('$35.00-$53.94 $800/monthly', read {D})"})
json.dump(out, open(out_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(out), 'OH findings')
for x in out:
    f = x['fees']
    print(x['id'], x['name'][:34], f['nightly_low'], f.get('surcharges'), '|', f['note'][:170])
