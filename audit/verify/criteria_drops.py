#!/usr/bin/env python3
"""Entries dropped on phase-7 criteria follow-ups (criteria_followups.md), under the standing
rules I may apply and report: the private presence rule (AWH 2026-10-14: a working website with
a phone, or Google Maps open with 25+ reviews and a phone) and the long-stay rule's test 2
(nights really for sale: a posted nightly rate + phone, or a booking site).

    python3 -I audit/verify/criteria_drops.py [--apply]

Logged to removals.json beside this script. No trip references any of them (asserted).
Dry run unless --apply; safe to rerun.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CG = os.path.join(ROOT, "campgrounds.json")
LOG = os.path.join(HERE, "removals.json")

DROPS = {
    1168: ("2026-10-21", "long-stay park with no nights visibly for sale (long-stay test 2)",
           "lakebonin.com, read 2026-10-21: 'With our focus on seasonal sites, we also have non-seasonal sites available'; "
           "'Daily, weekly and seasonal rates are available. Call or email us to book' - no rate posted anywhere on the site, no booking site."),
    13118: ("2026-10-21", "no live presence (private presence rule)",
            "Operator domain parked and booking host NXDOMAIN (2026-10-20); Google Maps has no listing at the pin "
            "(searches by name, address and phone 570-448-2268 find only other businesses), read 2026-10-21."),
    1164: ("2026-10-21", "no live presence (private presence rule)",
           "Only a Facebook page; Google Maps listing (286 Firehouse Ln, 4.7 over 32 reviews) carries no phone or website; "
           "no posted rate. Read 2026-10-21."),
    1188: ("2026-10-21", "no live presence (private presence rule)",
           "woodhavenacres.com, read 2026-10-21: one page with an email form, no phone, rates or booking; "
           "Google Maps 'Woodhaven Campgrounds' has 5 reviews (under 25)."),
    13095: ("2026-10-21", "no live presence (private presence rule)",
            "Ivanhoe Civic League's only page is a login-walled Facebook page; no operator page posts a rate; "
            "Google Maps 'Ivanhoe Jubilee Park Show Grounds' (4.7 over 43 reviews, open) carries no phone or website - "
            "the only phone is on Campendium. Horse-only question also unverifiable. Read 2026-10-21."),
    13090: ("2026-10-21", "no live presence (private presence rule)",
            "No operator website (only a login-walled Facebook page and tourism-directory listings); "
            "Google Maps 'Lonesome Pine RV Park & Campground' has a phone but 16 reviews (under 25); "
            "no posted rate, and RV Life's $ rests on a placeholder ~$1 average. Read 2026-10-21."),
    520: ("2026-10-21", "4WD recommended on the access road (AWH 4WD rule, Rapidan 2026-10-21)", "DWR Long Run Road (Forest Rd 72) page, read 2026-10-21: 'The road is unpaved, winding, and remote. It is recommended only for 4-wheel drive vehicles with high clearance.' FR 72 is the only road to the site; EKKO is not 4WD (AWH's own note: 'road may require 4WD')."),
    519: ("2026-10-21", "4WD recommended on the access road (AWH 4WD rule, Rapidan 2026-10-21)", "DWR Long Run Road (Forest Rd 72) page, read 2026-10-21: 'The road is unpaved, winding, and remote. It is recommended only for 4-wheel drive vehicles with high clearance.' FR 72 is the only road to the site; EKKO is not 4WD (AWH's own note: 'road may require 4WD')."),
    522: ("2026-10-21", "4WD recommended on the access road (AWH 4WD rule, Rapidan 2026-10-21)", "DWR Long Run Road (Forest Rd 72) page, read 2026-10-21: 'The road is unpaved, winding, and remote. It is recommended only for 4-wheel drive vehicles with high clearance.' FR 72 is the only road to the site; EKKO is not 4WD (AWH's own note: 'road may require 4WD')."),
    521: ("2026-10-21", "4WD recommended on the access road (AWH 4WD rule, Rapidan 2026-10-21)", "DWR Long Run Road (Forest Rd 72) page, read 2026-10-21: 'It is recommended only for 4-wheel drive vehicles with high clearance.' The site is 0.5 mi up FR 72C, which leaves FR 72 8.7 mi in from Hopkins Gap; FR 72 is the only way in. EKKO is not 4WD."),
    123: ("2026-10-21", "WMA camping lot is a boat-ramp lot (AWH 2026-10-21: drop WMA lots that are waterfront or near a ramp)", "DWR, https://dwr.virginia.gov/camping-on-wmas/: 'It is unlawful to camp within 300 feet of any lake or facility (building, boat ramp, etc.)'. The Kelly's Ford lot is the Rappahannock access/boat-ramp lot."),
    124: ("2026-10-21", "WMA camping lot is a boat-ramp lot (AWH 2026-10-21: drop WMA lots that are waterfront or near a ramp)", "DWR, https://dwr.virginia.gov/camping-on-wmas/: 'It is unlawful to camp within 300 feet of any lake or facility (building, boat ramp, etc.)'. The Rogers Ford lot is the Rappahannock access/boat-ramp lot."),
    247: ("2026-10-21", "WMA camping areas are waterfront (AWH 2026-10-21: drop WMA lots that are waterfront or near a ramp)", "DWR, https://dwr.virginia.gov/camping-on-wmas/: 'It is unlawful to camp within 300 feet of any lake or facility (building, boat ramp, etc.)'. The Carlisle Tract's camping areas are along the fishing beach, and its boat ramp is its one named facility."),
    248: ("2026-10-21", "WMA camping spot is waterfront (AWH 2026-10-21: drop WMA lots that are waterfront or near a ramp)", "DWR, https://dwr.virginia.gov/camping-on-wmas/: 'It is unlawful to camp within 300 feet of any lake or facility (building, boat ramp, etc.)'. The entry's one camping/parking spot is on the Chickahominy River."),
    254: ("2026-10-21", "WMA camping areas are on the lakeshore (AWH 2026-10-21: drop WMA lots that are waterfront or near a ramp)", "DWR, https://dwr.virginia.gov/camping-on-wmas/: 'It is unlawful to camp within 300 feet of any lake or facility (building, boat ramp, etc.)'. AWH's note: 'multiple camping/parking areas at the lakeshore' of Briery Creek Lake."),
    482: ("2026-10-21", "WMA camping areas are on the lake (AWH 2026-10-21: drop WMA lots that are waterfront or near a ramp)", "DWR, https://dwr.virginia.gov/camping-on-wmas/: 'It is unlawful to camp within 300 feet of any lake or facility (building, boat ramp, etc.)'. AWH's note: 'Two parking/camping areas right on the lakefront.'"),
    406: ("2026-10-21", "access appears to need 4WD (AWH 2026-10-21)", "DWR Flagpole Knob page (https://dwr.virginia.gov/vbwt/sites/flagpole-knob/): FR 85 toward the summit is 'remote, narrow, very steep, deeply rutted, and rocky. Only experienced overlanding/off-roading drivers should attempt this road.' AWH 2026-10-21: reached the three westernmost sites (55, 402, 403) in 2WD; the sites beyond appear to need 4WD."),
    404: ("2026-10-21", "access appears to need 4WD (AWH 2026-10-21)", "DWR Flagpole Knob page (https://dwr.virginia.gov/vbwt/sites/flagpole-knob/): FR 85 toward the summit is 'remote, narrow, very steep, deeply rutted, and rocky. Only experienced overlanding/off-roading drivers should attempt this road.' AWH 2026-10-21: reached the three westernmost sites (55, 402, 403) in 2WD; the sites beyond appear to need 4WD."),
    405: ("2026-10-21", "access appears to need 4WD (AWH 2026-10-21)", "DWR Flagpole Knob page (https://dwr.virginia.gov/vbwt/sites/flagpole-knob/): FR 85 toward the summit is 'remote, narrow, very steep, deeply rutted, and rocky. Only experienced overlanding/off-roading drivers should attempt this road.' AWH 2026-10-21: reached the three westernmost sites (55, 402, 403) in 2WD; the sites beyond appear to need 4WD."),
    970: ("2026-10-21", "Sun Outdoors brand (AWH 2026-10-21: drop)", "AWH: 'drop Sun Outdoors Ocean City'. Sun Outdoors parks are pre-skipped by the curation passes; base $91-328/night (operator page/Campspot, p3-26)."),
    64: ("2026-10-21", "OHV staging camp (AWH 2026-10-02 off-road rule)", "DNR Savage River SF recreation page (https://dnr.maryland.gov/forests/Pages/publiclands/SavageRiver/recreation-trails.aspx), read 2026-10-21: the campsites are listed under the St. John's Rock ORV Trail - '13-mile off-road vehicle trail system ... 200-foot rock crawl ... Eight campsites ... Pricing varies by number of ORVs. A Maryland DNR Off-Road Vehicle permit is required.' The booking site's directions end at 'the ORV trail entrance'."),
    87: ("2026-10-21", "off-road park (AWH 2026-10-02 off-road rule)", "Wolf Den Run State Park is Maryland's ORV state park; DNR's camping page (https://dnr.maryland.gov/publiclands/Pages/western/WolfDenRun/Camping.aspx), read 2026-10-21, lets ORVs ride from the campground to Huckleberry Rocks (riding inside the campground banned) - a riders' camp. Also: 'A four-wheel drive vehicle may be necessary to access the campsite' in winter."),
    438: ("2026-10-21", "4WD recommended on the access road (AWH 2026-10-21: drop)", "DWR Rapidan WMA page, read 2026-10-21: roads beyond the state-maintained portion 'are narrow and not maintained to VDOT standards and can be rough. A four-wheel drive vehicle recommended.' EKKO is not 4WD. 438 is reached up the dirt road beyond SR 642 (Taylor Mountain Rd)."),
    440: ("2026-10-21", "4WD recommended on the access road (AWH 2026-10-21: drop)", "DWR Rapidan WMA page, read 2026-10-21: roads beyond the state-maintained portion 'are narrow and not maintained to VDOT standards and can be rough. A four-wheel drive vehicle recommended.' EKKO is not 4WD."),
}

if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    import trips
    cg = json.load(open(CG, encoding="utf-8"))
    by = {e["id"]: e for e in cg}
    log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
    logged = {r["id"] for r in log}
    gone = []
    for i, (day, reason, evidence) in DROPS.items():
        e = by.get(i)
        if e is None:
            assert i in logged, i
            continue
        assert not trips.campground_references(i), i
        gone.append(i)
        log.append({"id": i, "state": e["state"], "name": e["name"], "ownership": e["ownership"],
                    "location": e["location"], "reason": reason, "evidence": evidence, "checked": day})
        print(f"  drop {i} {e['state']} {e['name']}: {reason}")
    print(len(gone), "to drop")
    if "--apply" in sys.argv and gone:
        cg = [e for e in cg if e["id"] not in gone]
        with open(CG, "w", encoding="utf-8") as f:
            json.dump(cg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        with open(LOG, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("written")
