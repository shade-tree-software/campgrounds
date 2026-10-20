#!/usr/bin/env python3
"""Saskatchewan Provincial Parks in the policy registry (2026-10-20).

    python3 -I audit/sk_registry/apply.py [--apply]

48 of SK's 51 `provincial` entries are Sask Parks campgrounds and recreation sites; Borden
Bridge, Michel Point and Nesslin Lake are private leaseholds on provincial land with their own
booking and no Sask Parks reservation fee, so they get `policy_ref: none`. Every entry carries
its own 2026 price, and the park entry permit is on each entry that needs one (recreation sites
charge none), so the row's fee group holds only the $12 reservation fee. Like Manitoba, Sask
Parks has no rolling window: the whole season opens on April launch days, so window_opens_days
is absent. Devil Lake and Lac la Plonge had no booking record; the 2026-10-12 fee research
found both self-registration, which is recorded here so they don't inherit "reservable".
Dry run unless --apply; safe to rerun.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "campground_policies.json")
CG = os.path.join(ROOT, "campgrounds.json")
CHECKED = "2026-10-20"
GUIDE = "https://saskparks.tourismsaskatchewan.com/media/media-library/pdfs/sask-parks-camping-season-guide.pdf (Sask Parks Camping Season 2026)"
NOT_SKPARKS = {9292: "Borden Bridge, leased", 9303: "Michel Point, private", 9304: "Nesslin Lake, leased"}
SELF_REG = (9180, 9185)

ROW = {
    "booking": {
        "reservable": True,
        "platform": "reserveamerica",
        "url": "https://parks.saskatchewan.ca/",
        "reserve_until": {"relative_to": "arrival", "at": "23:00"},
        "note": "Sask Parks reservation system (parks.saskatchewan.ca) or the call centre, 1-833-775-7275, or by calling the park. There is no rolling window: nightly sites for the whole season (May 14-September 30 in 2026) open on staggered launch days at 7 a.m. CST (2026: April 14 Candle Lake, Good Spirit Lake, Lac La Ronge, Meadow Lake, Rowan's Ravine, Saskatchewan Landing; April 15 Blackstrap, Bronson Forest, Buffalo Pound, Duck Mountain, Moose Mountain, Porcupine Hills; April 16 Crooked Lake, Cypress Hills, Danielson, Great Blue Heron, Greenwater Lake, The Battlefords; April 17 Douglas, Echo Valley, Fort Carlton, Makwa Lake, Narrow Hills, Pike Lake). 'Same-day bookings are allowed until 11 p.m. CST on the day of arrival.' Spring camping before the season cannot be reserved online. NO STAY LIMIT: 'Campers can book nightly camping for as long as they would like on the same campsite provided there is availability', and no minimum stay for campsites (yurts only). Seasonal sites unsold by May 14 become nightly sites. Check-in after 2 p.m., out by noon CST; a site is held 24 hours past check-in, and a no-show can cost up to four nights. Change and cancellation fees depend on the site type and come on top of the non-refundable reservation fee. Several northern campgrounds and the recreation sites are self-registration only; those entries say first-come.",
    },
    "fees": {
        "currency": "CAD",
        "reservation_fee": 12,
        "checked": "2026",
        "note": "Each entry carries its own 2026 price; Sask Parks' 2026 nightly rates (May 14-September 30), taxes included: full service $49, electric $35, non-electric $20, economy $18, the same every night. The $12 reservation fee is per campsite, plus $2 through the call centre, non-refundable. Every vehicle in a provincial park needs an entry permit ($11 a day, $42 a week, $82 a year; free for Saskatchewan residents 65 and older), carried on the entries that need it; the recreation sites charge none.",
    },
    "provenance": {
        "booking": {"source": GUIDE, "checked": CHECKED, "method": "manual"},
        "fees": {"source": GUIDE, "checked": CHECKED, "method": "manual"},
    },
}

if __name__ == "__main__":
    reg = json.load(open(REG, encoding="utf-8"))
    cg = json.load(open(CG, encoding="utf-8"))
    print("provincial:SK", "replaces an existing row" if "provincial:SK" in reg else "is new")
    for e in cg:
        if e["id"] in NOT_SKPARKS:
            assert e["state"] == "SK" and e["ownership"] == "provincial", e["id"]
            print("policy_ref none:", e["id"], e["name"])
            e["policy_ref"] = "none"
        elif e["id"] in SELF_REG:
            assert not e.get("booking"), e["id"]
            print("self-registration:", e["id"], e["name"])
            e["booking"] = {"reservable": False, "fcfs": "always"}
            e.setdefault("provenance", {})["booking"] = {
                "source": "fee research 2026-10-12 (Sask Parks lists it as self-registration, first come, first served)",
                "checked": "2026-10-12", "method": "manual"}
    if "--apply" in sys.argv:
        reg["provincial:SK"] = ROW
        for path, data in ((REG, reg), (CG, cg)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("written")
