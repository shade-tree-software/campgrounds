"""Wyoming State Parks findings, read 2026-10-12 (page text in wy_pages_2026-10-12.json).

    python3 -I wy_build.py OUT

The '2026 Wyo Parks Fee Schedule' (wyoparks.wyo.gov permits-fees): 'The base rate for camping is $10 for residents and
$18 for non-residents. Fees for camping per vehicle are calculated as follows: base camping fee + day use fee + sales &
lodging tax'; 'Electric Site Fee: $10 per night'; day use 'Parks $7 per day, per vehicle' (residents) / '$12' (non-
residents), 'Historic Sites $4 per day, per adult' / '$8'. The booking site, now US eDirect at reserve.wyoming.gov (API
wyordr.usedirect.com/wyomingrdr/rdr/; the old wyomingstateparks.reserveamerica.com no longer resolves), lists each
park's campgrounds with their electric and non-electric sites (wy_places_2026-10-12.json) and prices every site at the
$10 base, Tuesday and Saturday alike; the electric fee, day use and tax are added in the cart. Connor Battlefield's page
posts its taxed totals: 'Daily use is free! Nightly Non-Resident camping fees are $20.34 Nightly Wyoming Resident camping
fees are $11.30'. The Wyoming State Fair's RV park (state-owned, not a state park) prices its own sites.

Each entry: nightly_low/high the resident base, non-residents +$8, electric +$10 where the campground has electric
sites, the day-use fee as entrance (not at Connor Battlefield, free; Medicine Lodge's is not stated, so not recorded).
wy_links_2026-10-12.py replaces the dead ReserveAmerica links."""
import json, sys
D = "2026-10-12"
FEES = "https://wyoparks.wyo.gov/index.php/permits-reservations/permits-fees"
TAX = " Plus sales and lodging tax (Connor Battlefield's posted $10 / $18 nights are $11.30 / $20.34)."
NR = {"type": "surcharge", "amount": 8, "per": "night"}
PARK_ENTRY = {"resident": 7, "nonresident": 12, "per": "vehicle_day"}
# entry -> (PlaceId, campground on the booking site, has electric sites)
PARK = {6349: (7, "North Fork", True), 6350: (8, "Aspen Grove", False), 6351: (12, "Pat's Point", False),
        6352: (10, "Two Moon", True), 6353: (11, "Sandy Beach", True), 6354: (6, "Tamarask", False),
        6359: (15, "Popo Agie and Sawmill", False), 6360: (14, "North Red Hills", True),
        6361: (13, "Lower, Middle and Upper", True)}
NAME = {6349: "Buffalo Bill State Park (North Fork Campground)", 6350: "Curt Gowdy State Park (Aspen Grove Campground)",
        6351: "Keyhole State Park (Pat's Point Campground)", 6352: "Glendo State Park (Two Moon Campground)",
        6353: "Guernsey State Park (Sandy Beach Campground)", 6354: "Boysen State Park (Tamarask Campground)",
        6359: "Sinks Canyon State Park (Popo Agie/Sawmill Campgrounds)", 6360: "Seminoe State Park (North Red Hills Campground)",
        6361: "Medicine Lodge State Archaeological Site"}
out = []
for eid, (pid, cg, elec) in sorted(PARK.items()):
    sur = {"weekend": 0}
    if elec:
        sur["electric"] = 10
    day = ("plus that day's day-use fee" if eid == 6361 else
           "plus the day-use fee, $7 a vehicle for residents and $12 for others")
    text = (f"$10 a night for Wyoming residents, $18 for others{', +$10 at an electric site' if elec else ''}, {day}." + TAX +
            f" Wyoming State Parks' 2026 fee schedule; the booking site prices the {cg} sites at the $10 base, read {D}.")
    fees = {"nightly_low": 10, "nightly_high": 10, "currency": "USD", "nonresident": NR, "surcharges": sur,
            "checked": "2026", "note": text}
    if eid != 6361:
        fees["entrance"] = PARK_ENTRY
    out.append({"id": eid, "name": NAME[eid], "fees": fees,
                "source": f"{FEES} ('2026 Wyo Parks Fee Schedule') + reserve.wyoming.gov PlaceId {pid} ({cg}: site types; "
                          f"rdr/search/details 'Rate' $10.00 for 2026-10-20 and 2026-10-24), read {D}"})
out.append({"id": 6370, "name": "Hawk Springs State Recreation Area", "fees": {
    "nightly_low": 10, "nightly_high": 10, "currency": "USD", "nonresident": NR, "entrance": PARK_ENTRY,
    "surcharges": {"weekend": 0}, "checked": "2026",
    "note": ("$10 a night for Wyoming residents, $18 for others, plus the day-use fee ($7 / $12 a vehicle)." + TAX +
             f" 24 primitive walk-up sites. Wyoming State Parks' 2026 fee schedule, read {D}.")},
    "source": f"{FEES} ('2026 Wyo Parks Fee Schedule'), read {D}"})
out.append({"id": 6356, "name": "Connor Battlefield State Historic Site", "fees": {
    "nightly_low": 10, "nightly_high": 10, "currency": "USD", "nonresident": NR, "surcharges": {"weekend": 0},
    "checked": "2026",
    "note": ("'Daily use is free! Nightly Non-Resident camping fees are $20.34 Nightly Wyoming Resident camping fees are "
             "$11.30' - the $10 / $18 base with sales and lodging tax. First come, first served; fees posted at the "
             f"entrance, cash or check. Its page and Wyoming State Parks' 2026 fee schedule, read {D}.")},
    "source": f"https://wyoparks.wyo.gov/index.php/places-to-go/connor-battlefield (Fees) + {FEES}, read {D}"})
out.append({"id": 6549, "name": "Wyoming State Fairgrounds & Events Complex RV Park", "fees": {
    "nightly_low": 30, "nightly_high": 40, "currency": "USD", "checked": "2026",
    "note": ("'Non-Fairtime Camping: Daily RV-$30 Monthly RV-$650 Weekly RV-$175'; 'Fairtime Camping: Daily RV-$40'; "
             "dry tent camping $20. 30/50-amp hookups, water and sewer. The Wyoming State Fair's event complex page, "
             f"read {D}.")},
    "source": f"https://wystatefair.com/event-complex/ (RV Park & Campground), read {D}"})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "WY findings")
