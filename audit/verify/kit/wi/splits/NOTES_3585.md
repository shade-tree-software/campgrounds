# Split: 3585 Sidie Hollow County Park (Vernon County, WI), 2026-11-17

## Decision: PARTIAL SPLIT
- Boat Landing Campground (101-125) becomes a new entry: `new_sidie_hollow_boat_landing.json`.
- 3585 keeps the Main Campground Area (201-230) and Upper Ridge Campground (301-330): `parent_3585.json`.
- Upper Ridge has its own road, but its centroid is only ~0.8 km from Main's, so it stays inside 3585. It is the part closest to the rule's edge, so AWH may want to decide it.

## Sources (all read 2026-11-17 unless dated otherwise)
- County page: https://www.vernoncountywi.gov/departments/land_and_water_conservation/parks_and_forests/sidie_hollow.php
  - "85 campsites".
  - "a nice mix of rustic tent sites with no utilities, electric sites, and full hookup RV sites ~ advance reservations require a two night minimum".
  - "camp hosts at site #9 of the boat landing campground area".
  - The caretaker's office is in the main campground area.
- 2026 rates PDF: https://cms8.revize.com/revize/vernoncountywi/2026%20Sidie_Hollow_Rates%20and%20Rules.pdf
  - Rustic $20, Electric $30, Electric & Water $40, Full Hookup $55 a night.
  - Weekly rate charges 6 nights; month $300-825; full season (Apr 15 - Oct 15) $2,000 on full hookup only.
  - $8 reservation/processing fee.
  - Online booking closes 3 days out; Wednesday FCFS for that weekend.
- County "Park Overview & Detailed Camping" PDF (2 pages, rendered and read): https://cms8.revize.com/revize/vernoncountywi/Park%20Overview%20&%20Detailed%20Camping.pdf
  - Page 1, per-site symbols:
    - Main Campground Area, E6051 County Road XX: rustic 201-208 and 219-224 (14); electric 209-218 and 226-230 (15); full hookup 225 (1).
    - Upper Ridge Campground, S5001 Campsite Road: rustic 301-302 and 317-330 (16); electric & water 303-316 (14).
    - Boat Landing Campground, S5184 Boat Landing Road: rustic 101-105 (5); full hookup 106-122 (17); electric & water 123-125 (3).
    - Totals: 35 rustic, 15 E, 17 E+W, 18 FHU = 85. This matches the Campspot type counts exactly.
  - Page 2, facility icons:
    - Main: dump station, showers, fresh water, restrooms, park office.
    - Upper Ridge: restrooms, fresh water, wifi; no showers and no dump.
    - Boat Landing: fresh water, restrooms, showers, playground, shelter, boat landing; no dump.
- Campspot: the earlier capture `audit/price_research/campspot_tier_2026-10-13.jsonl` gives type counts, amperage per type (Electric type 30-Amp only; E+W and FHU types 30 and 50), RV types to 40 ft, and primitive sites to 30 ft with 1 of 35 at 23 ft or more.
  - **campspot.com refused a plain curl today (CloudFront 403 on /api/gator-core/v2/parks/slug/sidie-hollow-park).** I did not retry it by any route, including the browser. Per-site lengths, amperage and whether host site 109 / site 225 are bookable are therefore unverified at site level.
- Open-Meteo elevation (DEM):
  - Main pin 43.5470,-90.9605: 296 m.
  - Boat Landing pin 43.5381,-90.9500: 288 m.
  - Upper Ridge 43.5411,-90.9649: 366 m.
  - Lake samples: 281-290 m.

## Imagery (Esri World_Imagery export, my own lat/lng-grid overlay; every frame rendered)
- 43.5425,-90.9560 hw 1300 m: the whole park. Lake, all three areas and the dam at the west end located.
- 43.5455,-90.9605 hw 260 and 43.5470,-90.9590 hw 230: the Main area.
  - The 226-230 diagonal spurs are at ~43.5481,-90.9604.
  - The electric row runs east of the road from ~43.5462 to 43.5477.
  - The day-use turnaround and parking are at 43.5450, where the old pin sat.
  - The lake starts at ~43.5440.
- 43.5468,-90.9603 hw 100: close-up of the electric row (creekside evidence below).
- 43.5410,-90.9650 hw 300 and 43.5412,-90.9655 hw 140: Upper Ridge.
  - The road runs N-S at -90.9650..-90.9645 from 43.5424 to 43.5404 with spurs on both sides, then curves SW to a turnaround at ~43.5397,-90.9670.
- 43.5445,-90.9630 hw 330 and 43.5480,-90.9665 hw 400: Upper Ridge's access.
  - Campsite Road leaves the N-S Sidie Hollow Road at ~43.5492,-90.9688 and runs SE along the ridge to Upper Ridge.
  - No road links it to County Road XX or the Main area; there are only trails.
- 43.5390,-90.9500 hw 250 and 43.5382,-90.9502 hw 130: the Boat Landing loop.
  - North row 117-125 is at ~43.5382-43.5384; south row 106-116 at ~43.5379-43.5380; RVs are visible.
- 43.5384,-90.9525 hw 140: the lake's east tip, marsh and boat-launch lot west of Boat Landing.

## Measured distances
These are approximate site centroids read from the county map placed on imagery, measured with haversine.
- Main (all 30 sites) 43.5472,-90.9598. Main RV sites only: 43.5473,-90.9605.
- Upper Ridge 43.5411,-90.9649.
- Boat Landing 43.5381,-90.9500.
- Main to Boat Landing: **1.29 km** (1.33 km from the Main RV sites). Each has its own road and address (County Road XX vs Boat Landing Road). **Meets the rule.**
- Main to Upper Ridge: **0.80 km** (0.78 km from the Main RV sites). Nearest sites, 224 to 301: ~0.50 km. It has its own road (Campsite Road off Sidie Hollow Road) and a separate address. **It fails the ~1 km test, so it stays with Main, which is the part it adjoins.**
- Upper Ridge to Boat Landing: 1.25 km.
- The old pin (43.5451,-90.9604) is ~245 m from the Main RV-site centroid, at the day-use turnaround.

## Waterfront
- **3585, Main + Upper Ridge: CREEKSIDE (sites 214-218).**
  - On the 43.5468,-90.9603 close-up, two trailers stand on the 214-218 row at ~43.5464-43.5466,-90.9604, on open mown grass.
  - Coe Hollow Creek, a few metres wide, is ~20-25 m east of them. No road, lot or tree screen lies between.
  - The county map draws the creek beside 209-218. I did not claim 209-213: they are among scattered trees and I could not resolve their pads.
  - No lake value: the lake is ~250 m south, past the day-use lot.
  - Upper Ridge: a wooded ridge ~75-85 m above the lake, ~160 m through continuous forest. No water value.
  - Not a below-dam case: the Main area is at the inflow, upstream of the dam at the west end.
  - This raises the stored "not waterfront". p3-503 had logged a creekside lead for these sites.
- **Boat Landing: NOT WATERFRONT.**
  - The south row backs onto a continuous treeline ~20-30 m south. Sidie Hollow Creek runs under that canopy; it is on the county map but not visible on imagery.
  - The lake tip and marsh are ~160 m west, past the boat-launch lot.

## Field notes
- `rating` (RV Life 3.5*/$$$) stays on 3585 only; the park has one RV Life record.
- `hookups`, 3585: electric 50, water true, sewer true.
  - The 50 A comes from Upper Ridge's E+W type and site 225's FHU type; the Main area's electric type is 30 A only.
  - Sewer rests on the lone full-hookup site 225. The engine's 18 FHU sites equal 106-122 plus 225, so 225 is in the public inventory. Site-level bookability is unverified (Campspot refused).
- `facilities.dump` is true on Boat Landing, following the MN Lake Bronson precedent: it is the same park, and the station is in the Main area. A group note says where it is.
- `season` and `booking` values are unchanged; I re-read both sources today.
- I did not set `pull_through`: the engine lists both Back-In and Pull-Through at type level.

## If AWH wants Upper Ridge as its own entry
Ready values:
- Name: "Sidie Hollow County Park, Upper Ridge Campground".
- Pin 43.5411,-90.9649; elevation 366 m.
- 30 sites: 14 E+W (303-316) and 16 rustic.
- Hookups: 50 A, water, no sewer. Fees $40 E+W, rustic $20.
- Facilities: restrooms and fresh water; showers and dump are in the Main area.
- Not waterfront.
- 3585 would then become Main only: 30 sites; electric 50 via 225 (the electric type is 30 A); water and sewer via 225; fees $30-55.

## Not done / refused
- campspot.com (CloudFront 403 to curl): not retried by any route.
- No other site refused. No browser was started.
