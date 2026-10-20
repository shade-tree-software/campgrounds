#!/usr/bin/env python3
"""PEI Provincial Parks in the policy registry (2026-10-20).

    python3 -I audit/pe_registry/apply.py [--apply]

8 of PE's 9 `provincial` entries are PEI Provincial Parks campgrounds, booked on
peiprovincialparks.ca, a ReserveAmerica (Aspira) site. The row is the "Fees and Cancellation
Policies" and "Booking Window" blocks every park's campgroundDetails page carries (read on
Panmure Island's). The season opens for booking on one April date, not on a rolling window, and no
stay limit is published, so the row carries neither. The 60+ / disabled discount is from the
province's 2026 rate table as recorded on the entries (2026-10-12).

Green Park (14939) is run by a leaseholder (KW Green Park Campground) on Campspot with its own
terms: `policy_ref: none`. Seven entries lose a note-derived `platform: operator`. Every entry keeps
its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
PAGE = "https://www.peiprovincialparks.ca/camping/panmure-island-provincial-park/r/campgroundDetails.do?contractCode=PE&parkId=320027 (Booking Window; Fees and Cancellation Policies)"
NONE = {14939}

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://www.peiprovincialparks.ca/",
        "note": "peiprovincialparks.ca (ReserveAmerica) or 1-877-445-4938. The whole season opens for booking on one spring date (April 15, 2026, 9 a.m. Atlantic, for arrivals June 5 to September 26). Check-in 2 p.m. CANCELLING: 72 hours or more before 2 p.m. on the arrival date, everything back but the transaction fees; later, one night is kept as well; a no-show forfeits it all. No refunds for leaving early, except under a severe weather warning.",
    },
    "fees": {
        "currency": "CAD",
        "reservation_fee": 6,
        "checked": "2026",
        "note": "Each entry carries its own price, plus 15% HST. Transaction fees: $6 a reservation, $2.75 a change, $2.75 a cancellation. Seniors 60 and over and persons with disabilities get 10% off.",
    },
    "provenance": {
        "booking": {"source": PAGE, "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{PAGE}; the entries' fee notes (PEI Provincial Parks' 2026 rate table, read 2026-10-12)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("provincial:PE", "replaces an existing row" if "provincial:PE" in reg else "is new")
    seen = set(); n = 0
    for e in cg:
        if e["id"] in NONE:
            assert e["state"] == "PE" and e["ownership"] == "provincial", e["id"]
            e["policy_ref"] = "none"; seen.add(e["id"])
            print("policy_ref none:", e["id"], e["name"])
        elif e.get("state") == "PE" and e.get("ownership") == "provincial":
            b = e.get("booking") or {}
            if b.get("platform") == "operator":
                assert e["provenance"]["booking"]["method"] == "derived", e["id"]
                del b["platform"]; n += 1
    assert seen == NONE
    print("operator platform removed from", n)
    if "--apply" in sys.argv:
        reg["provincial:PE"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
