"""Ontario Parks findings: the 2026 camping fee table (https://www.ontarioparks.ca/fees/camping/2026, 'Fees effective
from April 1, 2026 to March 31, 2027': four fee levels AA / A / B / C, electrical and non-electrical, base fee before
13% HST) and every park's campsite fee schedules on reservations.ontarioparks.ca (GoingToCamp), with each schedule's
sites' service type and allowed equipment, Tue 2026-07-14, Sat 2026-07-18 and Tue 2027-07-13 (gtc_probe.py ->
on_booking_fees_2026-10-12.json). Internet reservation fee $9.74 + HST = $11.00
(https://www.ontarioparks.ca/fees/reservation/2026).

    python3 -I on_build.py OUT

A park's sites carry different fee levels (a premium or waterfront loop sits a level up), so an entry's nightly_low /
nightly_high are its cheapest and dearest non-electrical sites that take a 23-ft rig ('Trailer or RV up to 25ft' or
longer), and the electric surcharge is its cheapest such electrical site less its cheapest non-electrical one. Where
every RV-length site has electricity the electric sites are the base. An entry whose sites all stop at 18 ft is not
priced and is listed for AWH (the 23-ft gate). The 2027 nights still answer with the 2026 fees. Saturday = Tuesday."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
TUE, SAT, NEXT = "2026-07-14", "2026-07-18", "2027-07-13"
FIT = ("Trailer or RV up to 25ft (7.6m)", "Trailer or RV up to 32ft (9.7m)", "Trailer or RV over 32ft (9.7m)")
# entry -> (booking-site park, map-name filter or None)
PARK = {
    8183: ("Algonquin - Mew Lake Campground", None), 8189: ("Algonquin - Lake Of Two Rivers Campground", None),
    8191: ("Algonquin - Canisbay Lake Campground", None), 8192: ("Algonquin - Pog Lake and Kearney Lake Campground", None),
    8204: ("Algonquin - Rock Lake et Raccoon Lake", ("Somogneche", "Tanakiwin")), 8205: ("Algonquin - Tea Lake Campground", None),
    8222: ("Algonquin - Achray Campground / Sand Lake Gate", "Achray"), 8238: ("Algonquin - Kiosk Campground", None),
    8239: ("Algonquin - Brent Campground", None), 8170: ("Bronte Creek Provincial Park - Campground Area", None),
    8194: ("Parc Provincial McRae Point", None), 8206: ("Parc Provincial Presqu'ile", None),
    8225: ("Lake Superior Provincial Park", "Agawa"), 8226: ("Lake Superior Provincial Park", "Rabbit Blanket"),
    8230: ("Killarney Provincial Park", "George Lake"), 8245: ("Quetico Provincial Park", "Dawson Trail"),
    8251: ("Sleeping Giant Provincial Park", "Marie Louise"), 8252: ("Rainbow Falls Provincial Park", "Rossport"),
    8253: ("Rainbow Falls Provincial Park", "Whitesand"), 8259: ("Missinaibi Provincial Park (Lake)", None),
    8257: ("Rene Brunelle Provincial Park", None),
}
probe = json.load(open(os.path.join(HERE, "on_booking_fees_2026-10-12.json"), encoding="utf-8"))
parks = {p["park"]: p for p in probe["parks"]}


def money(v):
    return f"${v:.2f}"


def nightly(s, d):
    fees = s["fees"].get(d) or []
    return min(f[0] for f in fees) if fees and not isinstance(fees, dict) else None


out, flags = [], []
for eid in sorted(e["id"] for e in rows.values() if e.get("state") == "ON" and e.get("ownership") == "provincial"
                  and "ontarioparks.ca" in (e.get("website") or "")):
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    pname, mapf = PARK.get(eid, (e["name"].replace("Provincial Park", "Provincial Park").strip(), None))
    p = parks.get(pname)
    if p is None:
        flags.append((eid, e["name"], "no park on the booking site")); continue
    mapfs = (mapf,) if isinstance(mapf, str) else mapf       # Algonquin's loops now carry Anishinaabe names
    sched = [s for s in p["schedules"] if not mapfs or any(f.lower() in m.lower() for f in mapfs for m in s["maps"])]
    elec, plain = [], []
    for s in sched:
        if not any(x in s["equipment"] for x in FIT):
            continue
        v, sat, nxt = nightly(s, TUE), nightly(s, SAT), nightly(s, NEXT)
        if v is None:
            continue
        assert v == sat, (eid, s["feeScheduleId"], v, sat)
        kind = max(s["services"], key=s["services"].get)
        (elec if "Service Type=Electric" in kind else plain).append((v, s["n"], s["maps"]))
    if not elec and not plain:
        flags.append((eid, e["name"], "no site takes a 23-ft rig: " + "; ".join(
            f"{s['n']} sites up to {max(s['equipment'])}" for s in sched)))
        continue
    base = plain or elec
    lo, hi = min(v for v, _, _ in base), max(v for v, _, _ in base)
    sur = {}
    if plain and elec and min(v for v, _, _ in elec) > lo:     # Restoule's electric sites sit a fee level lower
        sur["electric"] = round(min(v for v, _, _ in elec) - lo, 2)
    sur["weekend"] = 0

    def levels(lst):
        return " / ".join(money(v) for v in sorted({v for v, _, _ in lst}))
    text = (f"{levels(plain)} a night for a non-electrical site" if plain else "") + \
           (("; electrical " if plain else "") + f"{levels(elec)}" + (" a night for an electrical site (every RV-length site here has electricity)" if not plain else "") if elec else "")
    text += (", the same every night, before 13% HST. A second vehicle pays a daily additional-vehicle fee. $11 online reservation fee (incl. HST). Ontario "
             f"residents 65+ pay 20% less. Ontario Parks' 2026 fees and its booking site, read {D}.")
    fees = {"nightly_low": lo, "nightly_high": hi, "currency": "CAD", "reservation_fee": 11, "surcharges": sur,
            "checked": "2026", "note": text}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"https://www.ontarioparks.ca/fees/camping/2026 (2026 fee levels, before HST) + "
                          f"reservations.ontarioparks.ca/api/resource/feeDetails ({pname}" + (f", {' / '.join(mapfs)} sites" if mapfs else "") +
                          f", {TUE} / {SAT} / {NEXT}) + https://www.ontarioparks.ca/fees/reservation/2026 "
                          f"(internet reservation fee $11.00), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "ON findings;", len(flags), "flagged")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:40], f["nightly_low"], f["nightly_high"], f["surcharges"])
for fl in flags:
    print("FLAG", *fl)
