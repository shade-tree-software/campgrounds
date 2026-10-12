"""IN findings: the booking site's per-site prices, Tue 2027-06-15 (Sun-Wed rate) and Sat 2027-06-19
(Thu-Sat rate), read 2026-10-12 (in_booking_sample_2026-10-12.jsonl, sites taken across each park's list).

    python3 -I in_build.py SAMPLE OUT

Indiana's rate page gives only statewide ranges by site type (full hookup $40-52, electric $33-45,
non-electric $20-22, primitive $14-16 on Sun-Wed; more Thu-Sat), so each park's own prices come from the
booking site. No non-resident camping rate: the $7 / $15 entrance fee (Indiana / other plates, once per
stay for campers) is the registry row's. The base is the cheapest drive-in site: non-electric or primitive
where the park has one, else the electric site; youth, backpack, tent-only, rent-a-camp and building
loops are left out."""
import collections, json, os, re, sys
sample, out_path = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))
D = "2026-10-12"
RATES = "https://www.in.gov/dnr/state-parks/rates-and-fees/camping-fees"
SKIP = re.compile(r"(?i)youth|backpack|tent|rent.a|recreati|lodge|building|cabin|group|shelter|horse|equest")
park = collections.defaultdict(lambda: {"ne": [], "e": [], "fhu": [], "e_sat": [], "ne_sat": [], "fhu_sat": [], "loops": set()})
for line in open(sample):
    try:
        r = json.loads(line)
    except ValueError:
        continue
    if "error" in r or not r.get("price") or SKIP.search(r.get("loop") or "") or SKIP.search(r.get("Type") or ""):
        continue
    p = float(re.search(r"\$([\d.]+)", r["price"]).group(1))
    if p <= 0:
        continue
    kind = "fhu" if r.get("Sewer Hookup") else ("e" if r.get("Electricity Hookup") else "ne")
    key = kind + ("_sat" if r["date"] == "6/19/2027" else "")
    park[r["parkId"]][key].append(p)
    park[r["parkId"]]["loops"].add(r["loop"])
by_pid = collections.defaultdict(list)
for e in rows:
    if e.get("state") == "IN" and e.get("ownership") == "state":
        m = re.search(r"contractCode=IN&parkId=(\d+)", e.get("website") or "")
        if m:
            by_pid[m.group(1)].append(e)
out = []
for pid, ents in sorted(by_pid.items()):
    d = park.get(pid)
    if not d or not (d["e"] or d["ne"] or d["fhu"]):
        print("no prices", pid, [e["name"] for e in ents])
        continue
    ne, e, fhu = (min(d[k]) if d[k] else None for k in ("ne", "e", "fhu"))
    base = ne if ne is not None else (e if e is not None else fhu)
    s, parts = {}, []
    erng = (f"${e:g}" + (f"-{max(d['e']):g}" if max(d['e']) > e else "")) if e is not None else None
    if ne is not None:
        parts.append(f"${ne:g} a night for a site without electric" + (" (a primitive site)" if ne < 20 else ""))
        if e is not None:
            parts.append(f"electric {erng}")
            s["electric"] = round(e - base, 2)
    elif e is not None:
        parts.append(f"Every sampled RV site has electric: {erng} a night")
    if fhu is not None:
        parts.append(f"full hookups ${fhu:g}")
        s["full_hookup"] = round(fhu - base, 2)
    if e is not None and d["e_sat"]:
        wk = round(min(d["e_sat"]) - e, 2)
    elif d["ne_sat"] and ne is not None:
        wk = round(min(d["ne_sat"]) - ne, 2)
    else:
        wk = None
    if wk:
        s["weekend"] = wk
    text = "; ".join(parts) + " (Sunday-Wednesday nights)."
    if wk:
        text += f" Thursday-Saturday +${wk:g}."
    text += (" No out-of-state camping rate (the park entrance fee differs by plates). Indiana's rate page gives only "
             f"statewide ranges; these are the booking site's prices for 2027 nights, read {D}.")
    fees = {"nightly_low": base, "nightly_high": base, "currency": "USD"}
    if s:
        fees["surcharges"] = s
    fees["checked"] = "2026"
    fees["note"] = text
    for ent in ents:
        out.append({"id": ent["id"], "name": ent["name"], "fees": dict(fees),
                    "source": f"{RATES} (statewide ranges, read {D}) + indianastateparks.reserveamerica.com parkId {pid} "
                              f"(sampled sites' prices for 2027-06-15 and 2027-06-19, read {D})"})
json.dump(out, open(out_path, 'w'), indent=1, ensure_ascii=False)
print(len(out), 'IN findings')
for x in out:
    print(x['id'], x['name'][:38], x['fees']['nightly_low'], x['fees'].get('surcharges'), '|', x['fees']['note'][:130])
