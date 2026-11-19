# Split 9159: The Battlefords Provincial Park (SK), 2026-11-19

## Decision

**Split.** 9159 keeps the core area (Centre + North + Spruce Meadow, 213 sites), renamed
"The Battlefords Provincial Park - Core Area Campgrounds", pin unchanged. The South campground
(sites 301-421) becomes a new entry, "The Battlefords Provincial Park - South Campground"
(`new_battlefords_south.json`). Hilltop Campground (603-617) is in neither entry (see below).

## Measurements (SKPP GIS point of every site, haversine)

| Group | Sites with GIS point | Centroid |
|---|---|---|
| Center | 79/79 | 53.12783,-108.39492 |
| North | 114/114 | 53.13109,-108.38874 |
| Spruce Meadow | 20/20 | 53.13175,-108.39351 |
| Core (all three) | 213 | 53.12994,-108.39148 (falls on the main road between loops) |
| South | 121/121 | 53.11514,-108.37800 |

- South to core centroid: **1,879 m**. South to Center 1,810 m, to North 1,916 m, to Spruce Meadow 2,120 m.
- Nearest pair of sites: South 314 to Center 272, **1,319 m**.
- Kept pin 53.1278,-108.395: 6 m from Center's centroid, on Centre's sites. It is no longer on the golf
  resort's RV loops; that resort (Jackfish Lodge, 99 seasonal sites, not Sask Parks) is the block of RVs
  south-east of Centre on imagery. New South pin 53.1151,-108.3780 sits among the loops by the service centre.
- Center to North centroids are about 550 m apart: adjacent loops of the core, so they stay one entry.
- Open-Meteo elevation: 542.0 m at both pins.
- Own entrance: the park map (PDF p.1/p.3, published 16-17/03/2025) draws South on its own spur road off the
  main park road, beside the "Entry Gate", with "Core Area" to the north. Separate place: **passes** (own road,
  over 1 km apart).

## Site data (parks.saskatchewan.ca parkId 290515: paging table + every site's detail page, read 2026-11-19)

- **South (loop 290859):** 121 Nightly Electric, all 15/30 A. Max equipment: 40 ft x7, 32 x39, 25 x65,
  18 x10 (303, 325, 331, 375, 376, 380, 383, 392, 408, 409); 111 take a 19-25 ft unit. Access:
  96 back-in, 5 pull-through (302, 316, 326, 400, 402), 20 roadside. Gravel pads mostly. Every site:
  "Near Water - no", "Access To = Beach, Service Centre, Wood Pile". Site 302 posted rate $35.00/night
  for 6/15/2027 (rate card captured 2026-10-12).
- **Core:** Center 79 (53 Nightly Electric, 26 Nightly Non-Electric; seven sites at 50 ft: 211, 238-240, 249,
  253, 272; pull-through 257, 266), North 114 (59 Nightly Electric + 3 Accessible, 52 Seasonal Electric;
  50 A on nightly 31, 106, 110 and seasonal 79-105, 107-109), Spruce Meadow 20 Nightly Non-Electric.
  213 sites, 161 nightly (115 electric); 152 nightly take a 19-25 ft unit. Max 50 ft and 50 A both stay with the core.
- Group Areas (8) are not counted in either entry. Aspen, Maple and Willow sit on South's road; Poplar, Lakeview,
  Clearview and Keeway near the core; Robinson is farther south.

## Waterfront

- **South: not waterfront (stored) -> lakeview.** SKPP campsite photos (three per site, read 2026-11-19 for
  330, 332, 333, 334, 335, 354, 355; contact sheets rendered and viewed): 332 (open grass) shows Jackfish Lake
  over a band of shrubs; 333, 334 and 335 show it through a thin line of aspen; 330, 354 and 355 show no lake.
  On Esri World_Imagery z17 (0.72 m/px, frame s17 and a 2x crop of it, both rendered), a colour profile from each
  GIS point toward the shore reaches open water at about 45-55 m for 330-335. A strip of trees and shrubs and the
  Lakeside Trail lie between, so this is a view, not on the water (sk_head: a shoreline trail or trees between =
  a view). 329 and 353-358 sit 60-100 m back in trees; the rest are inland. Esri z18 returned "Map data not yet
  available" here; that frame was discarded.
- **Core: not waterfront, unchanged.** On imagery frame k17 (z17, rendered), Centre's lakeward sites (225, 227,
  253-261) are about 200-300 m from open water. The day-use beach, its parking lots, the Lakeview group camp
  and shoreline woods lie between. Spruce Meadow is farther back; North is inland, east of the main road.
  Every core site reads "Near Water - no".

## Facilities, season, fees

- **Core:** the facilities keep the stored values (showers, laundry, store, dump, flush toilets, potable water).
  Sources: the park page's Services and Amenities, the core-area map's "Shower and Laundry" and "Sani Dump"
  symbols, and the Beachside Store on the main beach.
- **South:** dump and potable water are recorded (sani dump and potable water symbols on the South map).
  The South map also has "Service Centre Accessible", "Washrooms" and "Accessible Washroom" symbols, and every
  South site lists "Service Centre = Y". Its legend has no shower or laundry symbol, however, and no source says
  what the South service centre holds. Showers and flush toilets are therefore **left absent** (unknown), not
  inferred.
- **Season:** both entries run 05-14 to 09-30 (2026). Tourism SK listings.csv: "Not Available in Fall",
  winter "Closed for the Season". The park is not on the SKPP winter-camping list (Blackstrap, Buffalo Pound,
  Cypress Hills, Duck Mountain, Echo Valley, Good Spirit, Moose Mountain, Rowan's Ravine, Pike Lake).
  The parent's season is unchanged.
- **Fees:**
  - South: nightly $35 CAD, weekend surcharge 0. Per the task, I wrote no reservation_fee or entrance; both
    are on the provincial:SK row.
  - **AWH should see:** that row's note says the entry permit is "carried on the entries that need it", and
    every other SK provincial entry stores `entrance` and `reservation_fee`. South would be the only one without
    them. Add them on apply if the map should print the permit.
  - Parent: fees unchanged ($20 non-electric, +$15 electric). Its fees note still carries the reservation-fee
    and permit boilerplate, which this split did not touch.

## Hilltop Campground (603-617)

- Drawn on park map p.2 east of North, by the Clearview and Keeway group camps, on their road near the
  Campground Permit Office and Park Entry.
- Not on the SKPP reservation system: no loop and no site rows 603-617 among the 343.
- No Tourism SK listing, and no web result mentions it.
- On imagery (hill17, z17, rendered) it is an open field at about 53.1282,-108.3764, with tents and vehicles,
  just north of the Clearview (53.12765,-108.37769) and Keeway (53.12743,-108.37647) group camps, sharing
  their access road.
- Distances: about 885 m from North's centroid and 1,026 m from the core centroid.
- **How its sites are sold (first-come, overflow, seasonal or group) is unknown.** It is left out of both
  entries and needs AWH or a call to the park office (306-386-2212) to settle.

## Other flags for AWH

- The SKPP park page's "GPS Info" (53.12147,-108.3812) sits on the golf course; don't pin from it.
- The core's RV Life rating (park-level) stays on 9159; South gets none.

## Sources

- https://parks.saskatchewan.ca/camping/the-battlefords-provincial-park/r/campgroundDetails.do?contractCode=SKPP&parkId=290515
  (park page, campsitePaging.do for all 343 rows, campsiteDetails.do for every site, site photos), read 2026-11-19
- https://saskparks.tourismsaskatchewan.com/media/media-library/pdfs/park-downloads/the-battlefords/the-battlefords-all.pdf
  (maps published 16-17/03/2025)
- https://saskparks.tourismsaskatchewan.com/the-battlefords (data: /media/databases/parks.csv: Phone Number Primary
  1-306-386-2212; listings.csv)
- audit/state_park_fees/sk_rate_card_2026-10-12.jsonl (South 302 $35.00 per night)
- Esri World_Imagery tiles, z15 (ov15), z17 (s17, k17, hill17), all rendered and viewed; z18 unavailable
- Open-Meteo /v1/elevation
- gov.sk.ca news (2014: "electrical expansion in the South Campground")
