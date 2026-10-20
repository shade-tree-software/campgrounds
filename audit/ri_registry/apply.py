#!/usr/bin/env python3
"""Rhode Island State Parks (RIDEM) in the policy registry (2026-10-20).

    python3 -I audit/ri_registry/apply.py [--apply]

All 4 RI `state` entries are RIDEM campgrounds booked on ReserveAmerica. Sources: the "Alerts and
Important Information" block every park's ReserveAmerica page carries, and the regulations
250-RICR-100-00-1 §1.x (camping: the two-week limit, Charlestown Breachway's seven nights) and
250-RICR-100-00-8 §8.6 (permits, party size, check-in). riparks.ri.gov sits behind a Cloudflare
challenge and was not read, so RIDEM's full policy (which holds the peak-season minimum stays) is
not in the row: `min_stay` stays unknown rather than guessed.

Charlestown Breachway (4170) takes a 7-night limit. §8.6(K) still says its permits are issued
first come, first served, but ReserveAmerica sells its sites on the same 12-month window as the
others, so the entry stays reservable. Two entries lose a note-derived `platform: reserveamerica`
the row now supplies. Every entry keeps its own price. Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
RA = "https://rhodeislandstateparks.reserveamerica.com/camping/burlingame-state-campground/r/campgroundDetails.do?contractCode=RI&parkId=252711 (Booking Window; Alerts and Important Information)"
R1 = "https://rules.sos.ri.gov/regulations/Part/250-100-00-1"
R8 = "https://rules.sos.ri.gov/regulations/Part/250-100-00-8"
BREACHWAY = 4170

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://rhodeislandstateparks.reserveamerica.com/",
        "window_opens_days": 365,
        "max_stay_nights": 14,
        "note": "ReserveAmerica, up to 12 months ahead and for the same day. As of October 2026, 2027 reservations are on hold while RIDEM picks a new reservation provider, so the channel and rules may change. Unreserved sites are let first come at the parks. STAY LIMIT: 14 nights in any 21 days in peak season (the Thursday before Memorial Day through Labor Day weekend), then 7 nights away; 21 nights in 28 the rest of the year. RIDEM's full policy also sets peak-season minimum stays, not recorded here. Check-in 1-10 p.m. (no later, reserved or not), check-out 11 a.m.; the permit holder is 18 and stays on the site; one family, or six people, a site; two vehicles. The site must be occupied the first night or it is resold with no refund. CANCELLING: 8 days or more before arrival, everything back but the reservation fee and an $8.75 cancellation fee; 2 to 7 days, one night is kept as well; under 2 days, no refund. No refunds for weather or leaving early.",
    },
    "fees": {
        "currency": "USD",
        "reservation_fee": 8.75,
        "checked": "2026",
        "note": "Each entry carries its own resident and non-resident price (by the customer's state of residence). $8.75 reservation fee, non-refundable, and $8.75 to cancel; a second vehicle pass is $12. Rhode Island's senior and disability waivers cover park entry, not camping.",
    },
    "provenance": {
        "booking": {"source": f"{RA}; {R1}; {R8} (8.6)", "checked": CHECKED, "method": "manual"},
        "fees": {"source": f"{RA}; {R8} (8.13-8.15)", "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("state:RI", "replaces an existing row" if "state:RI" in reg else "is new")
    for e in cg:
        if e.get("state") != "RI" or e.get("ownership") != "state":
            continue
        b = e.get("booking") or {}
        if b.get("platform") == "reserveamerica" and e["provenance"]["booking"]["method"] == "derived":
            del b["platform"]
            print("derived platform removed:", e["id"], e["name"])
        if e["id"] == BREACHWAY:
            assert e["name"].startswith("Charlestown Breachway")
            b["max_stay_nights"] = 7
            # An entry's own note hides the row's, so it carries the whole row note with the
            # stay limit swapped for Breachway's.
            peak = "14 nights in any 21 days in peak season (the Thursday before Memorial Day through Labor Day weekend), then 7 nights away"
            assert peak in ROW["booking"]["note"]
            b["note"] = "Fully self-contained RVs only. " + ROW["booking"]["note"].replace(peak, "7 nights in any 21 days in peak season (the Thursday before Memorial Day through Labor Day weekend), then 14 nights away")
            e.setdefault("provenance", {})["booking"] = {"source": f"https://rhodeislandstateparks.reserveamerica.com/camping/charlestown-breachway-campground/r/campgroundDetails.do?contractCode=RI&parkId=252741; {R1}", "checked": CHECKED, "method": "manual"}
            print(e["id"], e["name"], b)
        e["booking"] = b
    if "--apply" in sys.argv:
        reg["state:RI"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
