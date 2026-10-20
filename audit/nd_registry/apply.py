#!/usr/bin/env python3
"""North Dakota Parks and Recreation in the policy registry (2026-10-20).

    python3 -I audit/nd_registry/apply.py [--apply]

15 of ND's 18 `state` entries are ND Parks and Recreation parks booked on reserveNDparks.com, a
US eDirect site. The row is NDPRD's FAQ and camping page. The FAQ prices the reservation fee at
$5.80 online and $9 by phone; the booking site itself charged $6 a site when the entries' fees
were read (2026-10-12), so the row records what checkout charges and the note gives both.

Not covered (`policy_ref: none`): Fort Buford (5891, State Historical Society of North Dakota)
and the ND Forest Service's Strawberry Lake (5900) and Hahn's Bay (13959), all first come with
their own fees. Seven entries lose a note-derived `platform: operator`. Every entry keeps its own
price and vehicle permit. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
FAQ = "https://www.parkrec.nd.gov/faq"
CAMP = "https://www.parkrec.nd.gov/stay/camping"
NONE = {5891, 5900, 13959}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "usedirect",
        "url": "https://www.reservendparks.com/",
        "window_opens_days": 95,
        "max_stay_nights": 14,
        "note": "reserveNDparks.com or 800-807-4723 (7 a.m.-8 p.m. Central). Campsites can be booked 95 days ahead; on the first day a date opens, not before 7 a.m. Central. STAY LIMIT: 14 nights in any 30 days. Check-in 4 p.m., check-out 3 p.m. Every vehicle needs a park entrance permit, campers included. Changes online or by phone, $5, but the arrival date can't be changed. CANCELLING: more than 7 days before arrival, a $10 fee; 7 days or less, one night; no refund once the arrival date passes without cancelling.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 6,
        "checked": "2026",
        "note": "Each entry carries its own price and vehicle entrance permit. The reservation fee is per site and non-refundable: $6 at checkout on the booking site; NDPRD's FAQ says $5.80 online or in person and $9 by phone. A change costs $5.",
    },
    "provenance": {
        "booking": {"source": f"{FAQ}; {CAMP}", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{FAQ}; the reserveNDparks.com checkout as recorded on the entries (read 2026-10-12)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:ND", "replaces an existing row" if "state:ND" in reg else "is new")
    seen = set(); n = 0
    for e in cg:
        if e["id"] in NONE:
            assert e["state"] == "ND" and e["ownership"] == "state", e["id"]
            e["policy_ref"] = "none"; seen.add(e["id"])
            print("policy_ref none:", e["id"], e["name"])
        elif e.get("state") == "ND" and e.get("ownership") == "state":
            b = e.get("booking") or {}
            if b.get("platform") == "operator":
                assert e["provenance"]["booking"]["method"] == "derived", e["id"]
                del b["platform"]; n += 1
    assert seen == NONE
    print("operator platform removed from", n)
    if "--apply" in sys.argv:
        reg["state:ND"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
