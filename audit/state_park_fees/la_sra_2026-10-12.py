"""Sabine River Authority of Louisiana parks on Toledo Bend: fees and the standing minimum stay.
    python3 -I la_sra_2026-10-12.py FEES_OUT.json [--apply-min-stay]

Source: the authority's 'Parks Fee Schedule', 'Effective May 1, 2025' (la_sra_fee_page_2026-10-12.txt, from
https://srala-toledo.com/park/): RV spurs per night, Standard / Waterfront-Pull-thru - Cypress Bend $40 / $50, Oak Ridge
$25 / $50, San Miguel $35 / $45, Pleasure Point $35 / $50. Every spur has water and 20/30/50-amp electric (and sewer
at all but some Pleasure Point sites), so the standard spur is the base and the waterfront / pull-through spur a
premium site. 'Senior Citizens (62+) and Disabled Veterans may receive a 20% discount on all overnight rental fees';
a one-night deposit secures a reservation.

Minimum stay, same page: 'There is a 2-night minimum stay for reservations made from March through September on
weekends, and a 3-night minimum stay for Easter, Memorial Day, 4th of July, Labor Day, and Major Events.' A standing
minimum is kept and marked (booking.min_stay + a dated MINIMUM STAY note line), as for every other standing minimum."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import campground_schema as cs  # noqa: E402
D = "2026-10-12"
PAGE = "https://srala-toledo.com/park/"
RATES = {674: ("Cypress Bend", 40, 50), 6883: ("Oak Ridge Park", 25, 50), 6924: ("San Miguel", 35, 45),
         6884: ("Pleasure Point", 35, 50)}
MIN = [{"nights": 2, "applies": "weekend", "season": "reservations from March through September"},
       {"nights": 3, "applies": "holiday", "season": "Easter, Memorial Day, 4th of July, Labor Day and major events"}]
out = []
for eid, (name, std, wf) in RATES.items():
    fees = {"nightly_low": std, "nightly_high": std, "currency": "USD", "surcharges": {"premium_site": wf - std, "weekend": 0},
            "checked": "2025",
            "note": (f"${std} a night for a standard RV spur, ${wf} for a waterfront or pull-through spur, every spur with "
                     "water and 20/30/50-amp electric. Seniors (62+) and disabled veterans get 20% off. Sabine River "
                     f"Authority's fee schedule effective May 1, 2025, read {D}.")}
    out.append({"id": eid, "name": name, "fees": fees,
                "source": f"{PAGE} ('Parks Fee Schedule', 'Effective May 1, 2025': {name} ${std:.2f} / ${wf:.2f} a night "
                          f"Standard / Waterfront-Pull-thru), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "SRA fee findings")
if "--apply-min-stay" in sys.argv:
    cg_path = os.path.join(ROOT, "campgrounds.json")
    rows = json.load(open(cg_path, encoding="utf-8"))
    by = {e["id"]: e for e in rows}
    for eid in RATES:
        e = by[eid]
        assert not (e.get("booking") or {}).get("min_stay") and "MINIMUM STAY" not in (e.get("note") or ""), eid
        prov = dict(e.get(cs.PROVENANCE) or {})
        prov["booking"] = {"source": f"{PAGE} ('There is a 2-night minimum stay for reservations made from March through "
                                     "September on weekends, and a 3-night minimum stay for Easter, Memorial Day, 4th of "
                                     f"July, Labor Day, and Major Events'), read {D}", "checked": D}
        cs.apply_update(e, {"booking": {"min_stay": MIN}, cs.PROVENANCE: prov})
        e["note"] = (e.get("note") or "").rstrip() + (
            "  MINIMUM STAY: 2 nights on weekend reservations from March through September, 3 on Easter, Memorial Day, "
            f"July 4th, Labor Day and major-event weekends (Sabine River Authority fee schedule, {D}). --Claude")
        cs.validate_row(e, label=e["name"])
        print(eid, e["name"], json.dumps(e["booking"], ensure_ascii=False)[:200])
    tmp = cg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, cg_path)
    print("min stays written")
