"""The 25 NY State Parks campgrounds priced 2026-10-09 from each park's posted range: rebuilt 2026-10-12.

    python3 -I ny25_build.py OUT

Their range (Watkins Glen '$18-$30') spans site types and weekends, so beside it NY State Parks' statewide add-ons
(weekend +$4, electric +$7, ...) were counted twice (AWH 2026-10-12, on Hither Hills). Rebuilt the way ny_build.py priced
the other 52: each park's sites on the booking site for Tuesday 2027-06-15 and Saturday 2027-06-19
(ny25_booking_sample_2026-10-12.jsonl, sites taken across the whole list with their hookups). The base is the cheapest
site an RV can use; electric and full hookups are add-ons on it; a Saturday's difference is the weekend add-on; other
price steps (waterfront, premium) are named in the note. Non-residents +$5 a night (registry row state:NY); $7.25
reservation fee."""
import collections, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
rows = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'campgrounds.json'), encoding='utf-8'))}
D = "2026-10-12"
SCHED = "https://parks.ny.gov/camping/fees-policies"
RA = "newyorkstateparks.reserveamerica.com"
IDS = [1389, 1391, 1392, 1393, 1394, 1395, 1396, 1397, 1399, 1400, 1401, 1404, 1405, 1406, 1408, 1411, 1412, 1413, 1414,
       1415, 1417, 1418, 1420, 1421, 1428]
SKIP = re.compile(r"(?i)cabin|cottage|lean|yurt|group|boat|walk|hike|tent only|tent site|pavilion|shelter|day use|rv only")


def kind(r):
    amps = r.get("Electricity Hookup")
    if r.get("Sewer Hookup") and amps:
        return "fhu"
    return "e" if amps else "ne"


tue, sat = collections.defaultdict(dict), collections.defaultdict(dict)
for line in open(os.path.join(HERE, "ny25_booking_sample_2026-10-12.jsonl")):
    r = json.loads(line)
    if "error" in r or SKIP.search(r.get("loop") or "") or SKIP.search(r.get("Type") or ""):
        continue
    m = re.search(r"\$([\d.]+) Per Night", r.get("price") or "")
    if not m:
        continue
    p = float(m.group(1))
    (sat if r["date"] == "6/19/2027" else tue)[r["parkId"]][r["site"]] = (kind(r), p, r.get("Electricity Hookup"),
                                                                          r.get("loop"))
out = []
for eid in IDS:
    e = rows[eid]
    pid = re.search(r"parkId=(\d+)", e["website"]).group(1)
    t = tue.get(pid) or {}
    if not t:
        print("NO SAMPLE", eid, e["name"], pid)
        continue
    by = collections.defaultdict(list)
    for site, (k, p, amps, loop) in t.items():
        by[k].append(p)
    base_kind = "ne" if by.get("ne") else ("e" if by.get("e") else "fhu")
    base = min(by[base_kind])
    s = {}
    if base_kind == "ne" and by.get("e"):
        s["electric"] = int(min(by["e"]) - base)
    if by.get("fhu") and base_kind != "fhu":
        s["full_hookup"] = int(min(by["fhu"]) - base)
    wk = sorted({round(sat[pid][x][1] - t[x][1], 2) for x in sat.get(pid, {}) if x in t})
    if wk and wk[0] > 0:
        s["weekend"] = int(wk[0])
    elif wk == [0]:
        s["weekend"] = 0
    steps = sorted({p - min(by[k]) for k in by for p in by[k] if p - min(by[k]) > 0})
    word = {"ne": "a site without hookups", "e": "a site with electric", "fhu": "a full-hookup site"}
    parts = [f"${int(base)} a night for {word[base_kind]}"]
    if "electric" in s:
        parts.append(f"electric +${s['electric']}")
    if "full_hookup" in s:
        parts.append(f"full hookups +${s['full_hookup']}")
    text = "; ".join(parts) + "."
    if steps:
        text += " Some sites cost " + " or ".join(f"${int(x)}" for x in steps) + " more (waterfront, 50-amp or premium sites)."
    if s.get("weekend"):
        text += f" Friday, Saturday and the night before a holiday +${s['weekend']}."
    elif "weekend" in s:
        text += " The same on a Saturday."
    text += (" Non-residents +$5 a night; $7.25 reservation fee. NY State Parks' booking site, sampled sites for a Tuesday "
             f"and a Saturday in June 2027, read {D} (this replaces the park's posted range, which spanned site types and "
             "weekends).")
    fees = {"nightly_low": int(base), "nightly_high": int(base), "currency": "USD", "reservation_fee": 7.25,
            "nonresident": {"type": "surcharge", "amount": 5, "per": "night"}}
    fees["surcharges"] = s
    fees["checked"] = "2026"
    fees["note"] = text
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"{RA} parkId {pid} (sampled sites' prices and hookups for 2027-06-15 and 2027-06-19, read {D}) + "
                          f"{SCHED} (statewide schedule)"})
    print(eid, e["name"][:34], "| was", e["fees"].get("nightly_low"), "-", e["fees"].get("nightly_high"), "| now", int(base),
          s, "| kinds", {k: sorted(set(v)) for k, v in by.items()}, "| sat", wk)
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NY findings")
