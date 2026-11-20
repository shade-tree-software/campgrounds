# 6359 Sinks Canyon State Park: split Sawmill from Popo Agie (2026-11-20)

## Decision
SPLIT. Sawmill becomes its own entry (`new_sinks_sawmill.json`, one entry). The id stays on Popo Agie, because the
stored pin already marks it (42.74150,-108.82260 is 13 m from Popo Agie's RV-site centroid). `parent_6359.json`
re-cuts the kept entry.

## Why it passes the split rule
- **Separate engine facilities:** reserve.wyoming.gov PlaceId 15 has FacilityId 384 "Popo Agie" (21 units incl. HOST)
  and FacilityId 385 "Sawmill" (6 units: 26-29, TE25, shelter SAWS), each with its own facility point.
- **Distance (measured, haversine on the engine's unit MapInfo points):** RV-site centroid to centroid
  is 2,561 m (Popo Agie 42.74146,-108.82245 from 12 RV units; Sawmill 42.75709,-108.79942 from 4 RV units). The facility
  points are 2,560 m apart. The nearest units across the two campgrounds are TE23 to 29, 2,358 m apart.
- **Entrances:** Esri imagery shows each campground as its own paved loop connecting directly to WY-131 (Sinks Canyon
  Rd), about 2.4 km apart along the highway. They share nothing but the state highway.

## Sources
- reserve.wyoming.gov US eDirect API (wyordr.usedirect.com/wyomingrdr/rdr/): `search/grid` for 384 and 385
  (2027-06-15, 2027-04-27, 2027-09-27, 2026-12-10 windows) and `search/details` for every unit (2027-07-14; Sawmill 27/28
  also Saturday 2027-07-17). Reservation season 2027-05-01..09-30 in both, and walk-in counts in December
  (21 at Popo Agie, 6 at Sawmill). MaximumStay is 14 and every Rate is 10.00.
- Sawmill units: 26 is 20 ft, gravel, back-in; 27 is 24 ft, paved, back-in. 28 and 29 are 40 ft, paved, "Angle to Road:
  Parallel", "Pull Through RV Site", "Will not accommodate RV slide-outs." TE25 is a tent site. SAWS is a $40 day-use
  shelter. Every unit has a vault toilet. A 23-ft rig fits 27, 28 and 29.
- Popo Agie has 12 RV units: 01 (45 ft), 03 (36), 04 (40), 05 (30), 09 (36), 10 (36), 11 (30), 13 (18), 17 (30, "not
  recommended for RV's over 30ft"), 18 (30), 19 (30) and 24 (35x16). All are Back In. There are 8 tent sites, and
  HOST is not web-bookable. Sites 06 and 08 are absent; 12 and 15 are first-come.
- wyoparks.wyo.gov refuses with an F5 challenge, so it was not fetched. I used the repo capture
  `audit/state_park_fees/wy_pages_2026-10-12.json` (the Sinks Canyon page and the fee schedule) and search-result text
  (2026-11-20):
  - 'Campsites for RVs': "Popo Agie campground offers 24 sites for tents and small trailers/campers. There is very
    limited availability for large trailers." and "Sawmill Campground offers 5 campsites with an accessible site, 2
    roadside trailer/camper sites and 2 pull in/tent sites."
  - Hiking page: "no day use fee charged at Sinks Canyon State Park".
- The Dyrt Sawmill page (read 2026-11-20) describes Sawmill as mainly a day-use area.
  - Listing: "around six sites running directly alongside the river" and "RVs are limited to 24 feet" (an aggregator
    figure; the engine's 40-ft sites outrank it).
  - Reviews: 2018 "right on the drive and next to a cascade in a deep canyon" and "Clean vault toilet, potable water";
    2023 "Waterpump available".
  - Alert: water shut off for the off-season.
- Campflare (search-result text only) shows "Water: No" for Sawmill.
- Open-Meteo elevation: Sawmill 42.7571,-108.7994 is 1882 m; Popo Agie's pin is 2038 m (unchanged).

## Imagery (all frames rendered; files deleted after use)
- Sawmill: Esri World_Imagery at 90 m half-width (800 px, 0.225 m/px) and 450 m (1.125 m/px), plus USGS NAIP at 90 m in
  the same EPSG:3857 frame and a USGS 3DEP DEM (rendered as hillshade with 1-m contours). Every unit point is plotted.
- Popo Agie: Esri at 200 m half-width with every unit point. The loop and pads match the points, the river is open
  along the south side, and there are entrances off WY-131.
- Esri export returns HTTP 500 at 1000 px for these small extents. 800 px works.

## Waterfront calls
- **Sawmill: riverview.** The Middle Fork Popo Agie is a 12-18 m boulder cascade (NAIP), so it is creek-size.
  - Sites 28 and 29 are on a paved roadside lane at the bank. The whitewater is 8-12 m from their unit points, and the
    bank drops about 2 m.
  - Both imagery vintages show a continuous band of riparian trees, about 8-10 m deep, between the lane and the water.
    Esri crowns overhang the lane, and RGB transects run green for 8-12 m. I found no open gap.
  - That is not open ground, so the gate defaults down. The view of the cascade from 27-29 is supported by The Dyrt
    text and by the engine's 'Waterfront Setting: River' tag on 27-29. Site 27 is about 20 m away; 26 is 'Short Walk'.
  - Lead: this becomes creekside if a site photo shows open ground from 28/29 to the water. Popo Agie's 03-05 passed
    through a low willow fringe.
- **Popo Agie: creekside** (unchanged; its evidence already describes Popo Agie only). The new note names pads 03-05 per
  the few-sites rule.

## Re-cuts on the kept entry and fixes found
- Name: "Sinks Canyon State Park (Popo Agie Campground)". The inclusion_evidence, note and sites are rewritten for Popo
  Agie only: count 24, max 45, and pull_through dropped because it came from Sawmill's 28/29.
- Water shut-off moved from the note to facilities.note.
- **Season note was wrong:** "In winter only Popo Agie sites 12 and 15 stay open". The park page and the engine both show
  every campsite first-come from Oct 1 to Apr 30. Corrected.
- **Fees note contradicted entrance 0:** it said "plus the day-use fee, $7 ... $12". Sinks Canyon charges no day-use fee
  (wyoparks text), so entrance 0 stands and the note is corrected.
- Booking: season 05-01..09-30 added. In the note, "Popo Agie sites 12 and 15" becomes "sites 12 and 15".
- Unchanged: location, elevation, waterfront, waterfront_evidence, website, phone, rating and hookups.

## For AWH
- Sawmill's potable_water is written true, resting on the 2018 and 2023 Dyrt reviews plus the listing's hand pump.
  Campflare says no water, and the engine's shelter says no water at the structure.
- Unit pages show "Fees range from 12/21", while the rate is $10. This was already flagged in p3-546.
- Sawmill has no RV Life rating on the new entry (not looked up). An absent rating is unknown.
