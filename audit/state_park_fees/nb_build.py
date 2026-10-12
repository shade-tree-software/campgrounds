"""New Brunswick findings: each park's 'Dates & Rates' tab on parcsnbparks.ca (nb_park_rates_2026-10-12.json) and the
booking site (reservations.parcsnbparks.ca, a GoingToCamp host): every campsite fee schedule with its sites' hookups,
for Tue 2026-06-09 (low season), Tue 2026-07-14 and Sat 2026-07-18 (high season) (gtc_probe.py ->
nb_booking_fees_2026-10-12.json). 2027 nights price at the high-season rate on every date so far, so the 2026 nights
are the ones that show both seasons.

    python3 -I nb_build.py OUT

'2026 High Season rates are in effect from May 15 to May 18 and from June 19 to September 7, 2026'; low season 'from
May 19 to June 18 and from September 8 until end of 2026 season'; 'all prices are posted before tax'. The about-us
page's policies: 'A non-refundable reservation fee of $10.00 will be charged for each reservation made.' The booking
site's prices equal the pages' for every site type the pages list, Saturday the same as Tuesday. Only sites that allow
a trailer of 25 ft or longer count: Sugarloaf's, New River Beach's, The Anchorage's and République's unserviced sites
are tent, van or small-trailer (18 ft) sites, so their base is the cheapest hookup site. The Anchorage has one price
all season, before tax $35.65 electric / $41.74 full hookups ($41 / $48 with HST; its page still shows
2024 rates). At
République (every site) and Sugarloaf (all but its full-hookup sites) the booking site adds a further charge of 4% and
3.5% of the nightly fee; the page doesn't name it, so the note just states it."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
rows = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "campgrounds.json"), encoding="utf-8"))}
D = "2026-10-12"
LOW, HIGH, SAT = "2026-06-09", "2026-07-14", "2026-07-18"
RV = ("Trailer up to 7.6 m (25 ft.)", "Lg. trailer/motorhome 5.5 m (18 ft.) to 9.7 m (32 ft.)",
      "XL trailer/motorhome 9.7 m (32 ft.) +")
PARK = {12892: "The Anchorage Provincial Park", 12893: "Herring Cove Provincial Park", 12894: "Mactaquac Provincial Park",
        12895: "Mount Carleton Provincial Park", 12896: "Murray Beach Provincial Park",
        12897: "New River Beach Provincial Park", 12898: "Parlee Beach Provincial Park",
        12899: "République Provincial Park", 12900: "Sugarloaf Provincial Park"}
PAGE = {12892: "12/the-anchorage-provincial-park", 12893: "6/herring-cove-provincial-park",
        12894: "10/mactaquac-provincial-park", 12895: "7/mount-carleton-provincial-park",
        12896: "11/murray-beach-provincial-park", 12897: "13/new-river-beach-provincial-park",
        12898: "5/parlee-beach-provincial-park", 12899: "8/republique-provincial-park", 12900: "9/sugarloaf-provincial-park"}
probe = {p["park"]: p for p in json.load(open(os.path.join(HERE, "nb_booking_fees_2026-10-12.json"), encoding="utf-8"))["parks"]}


def kind(services):
    """(order, label) for a schedule from its majority hookup combination."""
    combo = max(services, key=services.get)
    f = dict(x.split("=", 1) for x in combo.split(", ") if "=" in x)
    amps = f.get("Electrical Service", "").replace(" Amps", " amp")
    if f.get("Service Type") == "Unserviced":
        return 0, "an unserviced site"
    if f.get("Sewer Service") == "Yes":
        return 3, f"full hookups ({amps})"
    if f.get("Water Service") == "Yes":
        return 2, f"electric and water ({amps})"
    return 1, f"electric ({amps})"


def money(v):
    return f"${v:.2f}"


out = []
for eid, park in PARK.items():
    e = rows[eid]
    if e.get("fees"):
        print("has fees", eid); continue
    types = []
    for s in probe[park]["schedules"]:
        if not any(x in s["equipment"] for x in RV):
            continue
        night = {d: s["fees"][d][0][0] if s["fees"][d][0][0] < 500 else s["fees"][d][1][0] for d in (LOW, HIGH, SAT)}
        assert night[HIGH] == night[SAT], (park, s["feeScheduleId"])
        extra = s["fees"][HIGH][2][0] if len(s["fees"][HIGH]) > 2 else None
        o, label = kind(s["services"])
        types.append((night[HIGH], o, label, night[LOW], extra))
    types = sorted(set(types))
    base_high, base_o, base_label, base_low, _ = types[0]
    seasonal = any(t[3] != t[0] for t in types)
    sur = {}
    el = [t for t in types if t[1] in (1, 2) and t[1] > base_o]
    if base_o == 0 and el:
        sur["electric"] = round(el[0][0] - base_high, 2)
    fh = [t for t in types if t[1] == 3]
    if fh and base_o < 3:
        sur["full_hookup"] = round(fh[0][0] - base_high, 2)
    sur["weekend"] = 0
    parts = []
    for i, (hi, o, label, lo, extra) in enumerate(types):
        amt = f"{money(lo)} / {money(hi)}" if seasonal else money(hi)
        parts.append(f"{amt} a night for {label}" if i == 0 else f"{label} {amt}")
    text = ("; ".join(parts) + (" (low season, May 19 - June 18 and from September 8 / high season, May 15-18 and June 19 - "
            "September 7, in 2026)" if seasonal else ", one price all season") + ", the same every night of the week.")
    extras = sorted({round(t[4] / t[0] * 100, 1) for t in types if t[4]})
    if extras:
        text += f" The booking site adds a further {extras[0]:g}% of the nightly fee on " + \
                ("every site." if all(t[4] for t in types) else "its sites without full hookups.")
    text += (" Plus 15% HST, and a $10 reservation fee per booking. NB Parks' 2026 rates on the park's page and its "
             f"booking site (2026 nights), read {D}.")
    if eid == 12892:
        with_tax = " / ".join(f"${t[0] * 1.15:.0f}" for t in types)
        text = text.replace("Plus 15% HST", f"Plus 15% HST ({with_tax} with tax; the park page still shows 2024 rates)")
    fees = {"nightly_low": base_low, "nightly_high": base_high, "currency": "CAD", "reservation_fee": 10,
            "surcharges": sur, "checked": "2026", "note": text}
    out.append({"id": eid, "name": e["name"], "fees": fees,
                "source": f"https://www.parcsnbparks.ca/en/parks/{PAGE[eid]}/dates (2026 rates, 'posted before tax') + "
                          f"reservations.parcsnbparks.ca/api/resource/feeDetails ({park}, {LOW}, {HIGH} and {SAT}) + "
                          f"https://www.parcsnbparks.ca/en/about-us ('A non-refundable reservation fee of $10.00'), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "NB findings")
for x in out:
    f = x["fees"]
    print(x["id"], x["name"][:30], f["nightly_low"], f["nightly_high"], f["surcharges"], "|", f["note"])
