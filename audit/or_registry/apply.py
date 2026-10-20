#!/usr/bin/env python3
"""Oregon Parks and Recreation (OPRD) in the policy registry (2026-10-20).

    python3 -I audit/or_registry/apply.py [--apply]

Oregon's 56 `state` entries are 51 OPRD parks, four Oregon Department of Forestry campgrounds
(Tillamook and Clatsop State Forests) and one ODFW wildlife area. `state:OR` is the OPRD row,
reached by ownership+state; the ODF and ODFW entries get `policy_ref: none`, because they are
other agencies and would otherwise inherit OPRD's 25% non-resident rate and reservation fee.
Each of them is first-come and already says so, and each carries its own price.

Every OPRD entry carries its own price, so the row has no nightly figures. The non-resident
rate IS a row field: it is a multiplier on whatever the entry's own rate is, and it applies at
every OPRD campground. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
OPRD = "https://stateparks.oregon.gov/index.cfm?do="
NOT_OPRD = {10614: "ODF, Tillamook State Forest", 10630: "ODF, Tillamook State Forest",
            10643: "ODF, Clatsop State Forest", 10647: "ODF, Tillamook State Forest",
            10646: "ODFW wildlife area"}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://oregonstateparks.reserveamerica.com/",
        "window_opens_days": 180,
        "fcfs": "always",
        "max_stay_nights": 14,
        "note": "Oregon State Parks on ReserveAmerica, or 800-452-5687. 'New reservations are accepted starting the same day as arrival through six months in advance. New sites come online at 6 a.m. daily' (on 2026-10-20 the site read 'Now accepting reservations for arrival October 20, 2026 to April 19, 2027', so window_opens_days carries 180). Same-day online booking has been statewide since 2024-01-01, so there is no cutoff: 'At campgrounds that accept reservations, any available sites can be booked the same day through an online reservation, which can be made from home or at the park via a digital device or a park ranger' - turning up works wherever a site is free, which is why fcfs is always. 'Reservations are not required to camp' anywhere. Campgrounds that take no reservations use a booth or self-registration envelopes; OPRD lists Jackson Kimball, Goose Lake, Bates, Cascara (Fall Creek), Catherine Creek, Hilgard Junction, Jasper Point (Prineville Reservoir), Minam, Red Bridge and Ukiah-Dale, plus Cottonwood Canyon November-March and mixed walk-up loops at The Cove Palisades (spring and fall), Emigrant Springs, Farewell Bend and Lake Owyhee (all reservable in summer); those entries say first-come themselves. STAY LIMIT (OAR 736-010-0020): 'The maximum length of stay for campers is 14 consecutive nights in a 17 night span. After three nights out of the park, campers may return to start a new stay.' No minimum stay is published. Eight people and one RV per site (OAR 736-010-0050); quiet hours 10 p.m.-7 a.m.; 'All vehicles, including towed vehicles, must be able to fit into the paved driveway space' (driveway lengths are on ReserveAmerica). Cancel online or by phone up to the day before arrival (on the day, call the park); changes and cancellations carry a transaction fee.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 10,
        "nonresident": {"type": "multiplier", "factor": 1.25, "applies_to": "total"},
        "checked": "2026",
        "note": "Each entry carries its own 2026 price. OPRD's rate ranges, effective May 1, 2026, tax included (resident, peak): full hookup $30-42, electric with water $28-40, tent $20-27, primitive $0-15, extra vehicle $10. 'Oregon Parks and Recreation Department charges out-of-state residents 25% more' (full hookup $38-53 non-resident). At the 29 busiest parks the rate is the top of the range May 1-September 30 and on every Friday, Saturday and Sunday night; from October 1 to April 30 weekdays are cheaper than weekends. The $10 reservation fee is per site, by phone or online, 'unless it's a same-day reservation, in which case the $10 fee is waived'. No entrance fee for campers: a registered camper displaying the overnight receipt is exempt from the day-use parking permit (OAR 736-015-0030(5)(d)), which otherwise costs $5 a day or $60 ($75 out of state) for 12 months at the parks that charge it. Veterans with a service-connected disability and active-duty military on leave camp free, up to ten nights a calendar month, with no reservation deposit (OAR 736-015-0035); State Parks Day (first Saturday in June) is free for everyone.",
    },
    "provenance": {
        "booking": {"source": f"{OPRD}reserve.make, {OPRD}reserve.first-come, OAR 736-010-0020 and 736-010-0050 (oregon.public.law)", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{OPRD}reserve.rates (rates effective May 1, 2026), {OPRD}visit.faq (2026 fee changes), OAR 736-015-0030 and 736-015-0035", "checked": CHECKED, "method": "manual"},
    },
}

reg = json.load(open(REG, encoding="utf-8"))
cg = json.load(open(CG, encoding="utf-8"))
print("state:OR", "replaces an existing row" if "state:OR" in reg else "is new")
changed = []
for e in cg:
    if e["id"] in NOT_OPRD:
        assert e["state"] == "OR" and e["ownership"] == "state", e["id"]
        if e.get("policy_ref") != "none":
            e["policy_ref"] = "none"
            changed.append((e["id"], e["name"], NOT_OPRD[e["id"]]))
print("policy_ref none:", changed)
if "--apply" in sys.argv:
    reg["state:OR"] = ROW
    with open(REG, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(CG, "w", encoding="utf-8") as f:
        json.dump(cg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("written")
