#!/usr/bin/env python3
"""SEPAQ (Quebec parcs nationaux and réserves fauniques) in the policy registry (2026-10-20).

    python3 -I audit/qc_registry/apply.py [--apply]

43 of the 45 QC `provincial` entries book through SEPAQ. The row is SEPAQ's published reservation
terms for campsites ("Modalités de réservation — Emplacement de camping"). That page answers 403 to
plain HTTP and SEPAQ's site terms forbid automated readers, so it was held; AWH approved ONE read
with the headless driver on 2026-10-20 (its text is kept beside this script, sepaq_camping_modalites_2026-10-20.txt).

The page publishes no booking window and no reservation fee, so the row carries neither. It says a
minimum number of nights "may be required according to the park and the season" without giving
one, so `min_stay` stays unknown; the 14-night maximum is stated. Not for seasonal sites, which run
on a lease.

The two réserve faunique campgrounds in Lacs-Albanel-Mistassini-et-Waconichi (12520 Baie
Pénicouane, 12521 Lac Albanel) are run and booked by the Cree corporation Nibiischii, not SEPAQ, so
they take `policy_ref: none`. Every entry keeps its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
POL = "https://www.sepaq.com/reservation/modalites/camping.dot"
NIBIISCHII = (12520, 12521)

ROW = {
    "booking": {
        "reservable": True,
        "platform": "sepaq",
        "url": "https://www.sepaq.com/reservation/",
        "max_stay_nights": 14,
        "note": "sepaq.com or 1-800-665-6527. The whole stay is paid when booking (instalments without interest for stays more than 90 days out costing $500 or more). Check-in 3 p.m. Six people a site, at most four of them adults; children are not admitted over that. A minimum number of nights may be required depending on the park and the season; at most 14 consecutive nights. CHANGES (same kind of site, same season): up to 5 days before arrival, free if the value is the same or higher, $7 plus tax if lower; within 4 days, and on arrival day before 3 p.m., one change only, at 50% of any decrease (minimum $14). CANCELLING: up to 5 days before arrival, refunded less $7 plus tax; within 4 days, no refund. The terms always follow the original booking, even after a change of dates.",
    },
    "fees": {
        "currency": "CAD",
        "checked": "2026",
        "note": "Each entry carries its own price, plus taxes. A change or a timely cancellation costs $7 plus tax per reservation.",
    },
    "provenance": {
        "booking": {"source": f"{POL} ('Modalités de réservation — Emplacement de camping'), read once with the headless driver on AWH's OK", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{POL} ('Modification et annulation')", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("provincial:QC", "replaces an existing row" if "provincial:QC" in reg else "is new")
    qc = [e for e in cg if e.get("state") == "QC" and e.get("ownership") == "provincial"]
    for e in qc:
        if e["id"] in NIBIISCHII:
            assert "nibiischii" in (e.get("website") or ""), e["id"]
            e["policy_ref"] = "none"
            print("  policy_ref none:", e["id"], e["name"])
    print(len(qc) - len(NIBIISCHII), "entries take the row")
    if "--apply" in sys.argv:
        reg["provincial:QC"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
