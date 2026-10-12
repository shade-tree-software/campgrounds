"""St. Lawrence Parks Commission (Parks of the St. Lawrence) findings: its 2026 fee table (slpc_fee_page_2026-10-12.txt,
from https://www.stlawrenceparks.com/fees/, 'All fees in CAD plus HST') and every campsite fee schedule on its
booking site reservations.parks.on.ca (GoingToCamp), with each schedule's service type and allowed trailer length,
Tue 2026-07-14, Sat 2026-07-18 and Tue 2026-09-15 (gtc_probe.py -> slpc_booking_fees_2026-10-12.json). The booking
site's prices are the table's, the same on every date.

    python3 -I slpc_build.py OUT

The commission is a provincial agency apart from Ontario Parks, so these entries also get policy_ref none and its own
booking channel (slpc_policy.py). Base = the cheapest unserviced site that takes a 23-ft trailer ('Trailer up to 25ft'
or longer): Ivy Lea's $47.32 basic sites take trailers up to 20 ft, so its base is the $55.30 waterfront site.
Add-ons are the table's categories less the base: waterfront, premium waterfront, electric (the cheapest hookup site),
full hookups (Farran Park's 3-service sites; the table also names the Bird Sanctuary, whose booking site has none)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
PARK = {8207: "Farran Park", 8208: "Upper Canada Migratory Bird Sanctuary", 8218: "Woodlands Campground",
        8220: "Mille Roches Campground", 8307: "Riverside-Cedar Campground", 12658: "Glengarry Campground",
        12669: "McLaren Campground", 12683: "Ivy Lea Campground"}
UNSERVICED = {39.99: "basic", 47.32: "basic", 51.54: "waterfront", 55.30: "waterfront", 63.08: "premium waterfront"}
probe = {p["park"]: p for p in json.load(open(os.path.join(HERE, "slpc_booking_fees_2026-10-12.json"), encoding="utf-8"))["parks"]}


def fits(equipment):
    return any((m := re.search(r"Trailer up to (\d+)ft", x)) and int(m.group(1)) >= 25 for x in equipment)


def money(v):
    return f"${v:.2f}"


out = []
for eid, park in PARK.items():
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    plain, hook, short = {}, {}, set()
    for s in probe[park]["schedules"]:
        vals = {f[0] for fees in s["fees"].values() for f in fees}
        assert len(vals) == 1, (park, s["feeScheduleId"], vals)
        v = vals.pop()
        kind = max(s["services"], key=s["services"].get)
        if "Service Type=Unserviced" in kind or "Service Type=Water" in kind:
            if not fits(s["equipment"]):
                short.add(v); continue
            plain[v] = UNSERVICED[v]
        elif fits(s["equipment"]):
            amps = re.search(r"Electric Service=(\d+) amps", kind)
            label = ("full hookups" if "Sewer" in kind else "electric and water" if "Water" in kind else "electric") + \
                    (f" ({amps.group(1)} amp)" if amps else "")
            hook.setdefault(v, label)
    base = min(plain)
    sur = {}
    if hook:
        sur["electric"] = round(min(hook) - base, 2)
    fh = [v for v, l in hook.items() if l.startswith("full")]
    if fh:
        sur["full_hookup"] = round(min(fh) - base, 2)
    wf = [v for v, l in plain.items() if l == "waterfront" and v > base]
    if wf:
        sur["waterfront"] = round(min(wf) - base, 2)
    pr = [v for v, l in plain.items() if l == "premium waterfront" and v > base]
    if pr:
        sur["premium_site"] = round(min(pr) - base, 2)
    sur["weekend"] = 0
    parts = [f"{money(v)} a night for a {l} site" if i == 0 else f"{l} {money(v)}"
             for i, (v, l) in enumerate(sorted(plain.items()))]
    parts += [f"{l} {money(v)}" for v, l in sorted(hook.items())]
    text = "; ".join(parts) + ", the same every night, plus HST."
    cheaper = sorted(v for v in short if v < base)     # a shorter site that would otherwise have been the base
    if cheaper:
        text += " The " + "/".join(money(v) for v in cheaper) + " basic sites here take trailers up to 20 ft."
    text += (" $13.25 + HST reservation fee per booking. Seniors get 20% off basic and 15-amp sites and the military 20% "
             f"off every site, at check-in. St. Lawrence Parks' 2026 fees and its booking site, read {D}.")
    fees = {"nightly_low": base, "nightly_high": base, "currency": "CAD", "reservation_fee": 13.25, "surcharges": sur,
            "checked": "2026", "note": text}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"https://www.stlawrenceparks.com/fees/ (2026 fees, 'All fees in CAD plus HST') + "
                          f"https://www.stlawrenceparks.com/reservations/ (Reservation Fee $13.25) + "
                          f"reservations.parks.on.ca/api/resource/feeDetails ({park}, 2026-07-14 / 2026-07-18 / 2026-09-15), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "SLPC findings")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:36], f["nightly_low"], f["surcharges"], "|", f["note"][:260])
