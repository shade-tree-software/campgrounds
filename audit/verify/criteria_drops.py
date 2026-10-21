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
    14397: ("2026-10-21", "over the US$50 price gate, no exception", "Operator's 'Current prices' page, read 2026-10-21: $65/night (50-amp full hookup). Homosassa: no gateway within 40 km (gateways.py); no Good Sam park, no --AWH note, no stays."),
    14414: ("2026-10-21", "over the US$50 price gate, no exception (and possibly 55+)", "Newbook, read 2026-10-21: RV Standard $71/night. Arcadia: no gateway; Good Sam false; no --AWH note, no stays. The operator's home page also says 'we are 55+ community' (its FAQ says all-age)."),
    14431: ("2026-10-21", "long-stay park with no nights visibly for sale (long-stay test 2)", "buckheadridgeresort.com, read 2026-10-21: annual leases (August-July), 'Residents', contact form only; no nightly rate and no booking site."),
    4766: ("2026-10-21", "no live presence (private presence rule)", "2026-10-21: buddyslakesidepark.com NXDOMAIN; bigbassvillagecampground.com an unconnected Wix domain; no operator page found by name or phone 352-447-3474. The only listing (CampLinq aggregator) gives monthly prices only."),
    4724: ("2026-10-21", "camping prohibited by the agency", "FWC Escribano Point WMA regulations summary, July 1 2026 - June 30 2027: 'Camping: Prohibited.' The WMA pages list no camping; the WebReserv booking page is gone ('Page Not Found'); The Dyrt lists it CLOSED. Read 2026-10-21."),
    4797: ("2026-10-21", "long-stay test 5: sells homes (home community)", "hammondellcampsites.com, read 2026-10-21: 'primarily a 55+ community', 'Mobile Homes for Sale' and 'Lot Information' pages, $665/month mobile-home sites; the RV section is part of a mobile-home community."),
    4751: ("2026-10-21", "no live presence (private presence rule)", "2026-10-21: no website of its own (Facebook only, unreadable) and no booking listing; the Google place at the pin has 10 reviews (rule needs 25)."),
    4804: ("2026-10-21", "no price indicator (private presence rule)", "2026-10-21: no posted rate, no working booking page (RoverPass listing unclaimed, not bookable), no RV Life price tier; the stored $50-65 were other parks' prices from RoverPass's 'nearby' panel. Only presence: a 2009-era http site (the https domain serves an unrelated acupuncture clinic)."),
    4806: ("2026-10-21", "over the US$50 price gate, no exception", "masonicparkflorida.com, read 2026-10-21: $60/night (weekly $360, monthly $550), booking by request form + deposit. No gateway, not Good Sam, no --AWH note, no stays."),
    14425: ("2026-10-21", "over the US$50 price gate, no exception (and a 55+ home community)", "oakhavenrvpark.com rates effective 2026-05-01: $70-80/night. A 55+ senior park for mobile-home and park-model owners with properties for sale. No gateway, Good Sam false, no stays."),
    4811: ("2026-10-21", "over the US$50 price gate, no exception", "leestravelpark.com rates dated 2026-10-01: $85/$90/night. Largo: no gateway within 40 km; Good Sam false; no --AWH note, no stays."),
    14394: ("2026-10-21", "long-stay test 5: sells homes (55+ home community)", "woodsnwatertrails.com, read 2026-10-21: '55+ RV Community' for 'full-time, seasonal, and short-term stays', a Homes for Sale page, seasonal and annual residencies full with a waitlist."),
    14422: ("2026-10-21", "long-stay test 2: no nights visibly for sale", "woodysrvresort.com, read 2026-10-21: no posted rate anywhere; daily stays only 'Restrictions Apply, please call for details'; park rules are a Florida Statute 723 mobile-home community's (rent due on the 1st, year-round units anchored and skirted, units sold in the park). The price rests on RV Life's $$ alone, which test 2 does not accept."),
    14409: ("2026-10-21", "long-stay park: AWH 2026-10-21 (55+ resident community with units for sale)", "ridgemanorcampground.com + its RoverPass page, read 2026-10-21 (p3-31): 55+, 'units for sale', a resident application for stays of 6+ months, seasonal/yearly lots, no daily rates on sale for January 2027. Dropped by AWH."),
    14395: ("2026-10-21", "over the US$50 price gate, no exception (mostly long-stay 55+)", "Campspot, read 2026-10-21: $55/night for October 2026 and January 2027 nights (site: 'Starting at $50 Daily'). Lake Panasoffkee: nearest gateway Walt Disney World 68 km; Good Sam false; no --AWH note, no stays. A 55+ park mostly selling seasons and permanent residency."),
    4758: ("2026-10-21", "over the US$50 price gate, no exception (and mostly long-stay)", "ResNexus, read 2026-10-21: $69.00/night before tax (Nov 2026, Feb 2027), one-night searches offered only as '2 nights or more'; 16-18 of its 18 sites occupied on ordinary Tuesdays in Nov, Feb and Jun. Gulf Breeze: no gateway within 40 km; Good Sam not listed; no --AWH note, no stays."),
    4771: ("2026-10-21", "over the US$50 price gate, no exception", "Campspot, read 2026-10-21: $55/night for the 30-amp waterfront sites and $60 deluxe full hookup (Jan 2027, Nov 2026), plus a $2.50 resort fee and 3% processing; the operator's page says 'Nightly Stays $50-55'. Nearest gateway Orlando 91 km; Good Sam false; no --AWH note, no stays. Mixed manufactured-home and RV community. Same reading as Countryside 14395."),
    14407: ("2026-10-21", "over the US$50 price gate, no exception (and mostly seasonal 55+)", "Newbook, read 2026-10-21: Basic $72.95 to Premium $77.95 daily. No gateway within 40 km (Tampa 51 km, Walt Disney World 61 km); Good Sam not listed; no --AWH note, no stays. Calls itself a '55+ community', rates lead with monthly/6-month/yearly packages."),
    14418: ("2026-10-21", "park admits only rigs 24 ft or longer (EKKO is 23 ft)", "Oak Grove RV Resort park rules, read 2026-10-21: 'Self-contained 24\\' or longer motorhomes, fifth wheels, travel trailers and park models'. Also mostly seasonal/residential (full-time sites, 1-year park-model leases) with no posted rate ('Call us for Rates!')."),
    14386: ("2026-10-21", "long-stay test 2: background checks, mostly monthly", "pellicercreekcampground.com, read 2026-10-21: 'We are mainly a long-term park offering monthly reservations. We do offer short-term rentals when we have availability'; 'Majority of our sites are reserved for monthly reservations only'; background checks on all occupants, rent due on the 1st, 30-day move-out notice. (Price $65 would have passed on the St. Augustine gateway.)"),
    4755: ("2026-10-21", "monthly rentals only (long-stay test 3)", "sunsetisle operator site, read 2026-10-21: 'Monthly and long term rentals only beginning 1/1/2022'; a 'Florida residential community' with lots for sale; no rates posted; 10 RV sites."),
    4768: ("2026-10-21", "over the US$50 price gate, no exception (and primarily 55+)", "Operator's rates, read 2026-10-21: $60/night tax included for 2. Nearest gateway Jacksonville 149 km; no Good Sam discount, no --AWH note, no stays. FAQ: 'primarily a 55+ community', children up to two weeks."),
    4767: ("2026-10-21", "over the US$50 price gate, no exception", "CampLife quotes Oct 2026-Jun 2027, read 2026-10-21: cheapest RV site $57/night plus a $3 per-stay fee, before 10% tax. Nearest gateway Jacksonville 153 km; no --AWH note, no stays."),
    4744: ("2026-10-21", "long-stay park: no nightly rate posted, park models for sale (tests 2 and 5)", "thegladesresort.com, read 2026-10-21: rules address 'annual residents' and 'Lessee', rent and electric due on the 1st, park models for sale; RV Sites page says call 863-983-8070 for rates (only RV Life's $$ stands in, which test 2 does not accept)."),
    4789: ("2026-10-21", "long-stay park: no nightly rate posted (test 2)", "tampasouthrvresort.com, read 2026-10-21: the Rates page says only 'Call For Summer Specials'; pages speak to 'residents' and 'tenants' returning 'year after year', park models on some sites; the RoverPass listing is unbookable. Only RV Life's $$ stands in, which test 2 does not accept."),
    14403: ("2026-10-21", "over the US$50 price gate, no exception", "Newbook, read 2026-10-21: $57.56/night base. Nearest gateway Walt Disney World 66 km; not a Good Sam Park; no --AWH note, no stays. A 55+ community."),
    4780: ("2026-10-21", "no live presence (private presence rule)", "2026-10-21: campsitesarrowhead.com serves an Indonesian gambling spam page (also on 2026-10-15/16); no other operator site found. A mobile-home park with full-time residents; nightly stays rest on one Nov-2025 review."),
    4763: ("2026-10-21", "no live presence (private presence rule)", "2026-10-21: only a Facebook page, no rates or booking (the pattern AWH dropped 2026-10-11); its newest post (~2026-10-19) says 'A lot of clean up ahead of us ... We'll be back soon'."),
    4802: ("2026-10-21", "no live presence (private presence rule)", "2026-10-21: cedarslakervpark.com no longer resolves; the only link is an unclaimed, unbookable RoverPass listing; no operator-posted rate. Directories call it 'Cedars Lake MH & RV Park'."),
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
