# 9205 Saskatchewan Landing Provincial Park: split decision (2026-11-19)

**Decision: SPLIT into three.**
- **9205 keeps Bearpaw A/B + Sagebrush.** It has 240 sites. Its pin stays at 50.6772,-107.948.
- **New entry: Riverside + Nighthawk.** It has 60 sites. Pin on R12, 50.6878,-107.9253.
- **New entry: Bison Hollow.** It has 24 sites. Pin on BH9, 50.6631,-108.0161.

Prairie Meadow's 4 group areas and the Equestrian campground's 9 non-electric horse sites are not counted in any entry, as before. Landing View is a private campground and is not part of this.

## Sources (all read 2026-11-19 unless dated)

**parks.saskatchewan.ca, SKPP parkId 290135 (Sask Parks booking site)**
- campsitePaging.do: the whole park, 337 rows. It needs a cookie jar and is slow, about 20-45 s per page.
- campsiteDetails.do: 132 pages, which give GIS lat/lng, amps, length, access and reserve type.
  - Every Riverside (34), Nighthawk (26) and Bison Hollow (24) site.
  - 30 Bearpaw/Sagebrush sites.
  - Some Prairie Meadow pages.
- The campgroundDetails.do park page: the services list and the reduced-services rate table.

**Park maps, published 2026-06-19**
- PDF: saskparks.tourismsaskatchewan.com `.../saskatchewan-landing/saskatchewan-landing-all.pdf`.
- All 6 pages were rendered and viewed: core area, Bearpaw, Sagebrush, Nighthawk/Riverside, Bison Hollow/Prairie Meadow, and Equestrian.

**Tourism Saskatchewan data: `parks.csv` and `listings.csv`**
- Phone 306-375-5525.
- Fall camping runs in October.
- The winter listing reads "Closed for the Season".

**Other sources**
- The Sask Parks camping season guide PDF.
- audit/state_park_fees/sk_rate_card_2026-10-12.jsonl: $35 for every loop.
- SKPP site photos: `webphotos/SKPP/pid290135/sid<id>/0/540x360.jpg`.
  - Riverside: R28, R29, R31, R32, R33, R36, R38-R41, plus 6395 and 6408.
  - Bison Hollow: BH19-BH24.
  - Sagebrush: S27-S34.
  - Bearpaw: B41, B42, B80-B82, B106.
- Open-Meteo elevation API.
- OSRM (router.project-osrm.org): road distances.

**Not used**
- No source refused me during this task.
- No headless browser was started.

## Measurements (haversine, from SKPP GIS site points)

**Bearpaw/Sagebrush centroid**
- The loop centroids are weighted by site count: Bearpaw A 107, Bearpaw B 80, Sagebrush 53.
- Result: 50.6771,-107.9479, about 15 m from the stored pin.

**Riverside + Nighthawk centroid**
- Taken from all 60 points: 50.6885,-107.9267.
- It is **1.96 km** from Bearpaw/Sagebrush.
- The nearest pair of sites is S30 to R1, 1.21 km apart.
- By road it is 2.4 km, along Hwy 261, using its own junction off the highway.

**Bison Hollow centroid**
- Taken from all 24 points: 50.6631,-108.0163.
- It is **5.07 km** from Bearpaw/Sagebrush.
- The nearest pair of sites is B1 to BH1, 4.49 km apart.
- By road it is 12.5 km: Hwy 261, then Hwy 4, then its own road west of Hwy 4.

**Loops kept together**
- Riverside to Nighthawk: 0.34 km centroid to centroid (0.25 km between nearest sites), off one junction. They stay one entry.
- Bearpaw A to Bearpaw B: 0.49 km.
- Bearpaw B to Sagebrush: 0.40 km.
- Bearpaw and Sagebrush share one Campground Access Road, so they stay one entry.

**Elevations (Open-Meteo)**
- 9205 pin: 571.
- R12: 565.
- BH9: 562.

## Per-loop data (paging table)

| Loop | Sites | Length (ft) | Amps | Notes |
|---|---|---|---|---|
| Bearpaw A | 105 + 2 double | 25-50 | 15/30/50 on B66, B69, B71, B72, B78-B89 (15 sites) | Pull-Thru: B80 |
| Bearpaw B | 80 | 25-52 | 15/30 | Pull-Thru: B91; B135 blank |
| Sagebrush | 52 + 1 accessible | 32-82 | 15/30 | S6 is 82 ft; S17 blank |
| Riverside | 34 | 25-65 | 15/30/50 on R1-R12, R14-R20 (19 sites) | All Back-In. Not booked: R13, R30, R42 |
| Nighthawk | 26 | 32-70 | 15/30 | N19 is 70 ft. Back-In, except N22 and N27, which are Roadside |
| Bison Hollow | 24 | 32-50 | 15/30 | Access is printed only on BH19 and BH20 (Back-In), so pull_through is omitted |

- Every row reads "Near Water - no" and "Full Hookup - no".
- The park has no water or sewer hookups.

## Imagery: Esri World_Imagery tiles, SKPP GIS points plotted. Every frame rendered and was viewed.

Lake Diefenbaker is a reservoir and was drawn down in this imagery. High water is placed at the treeline, or at the sand line in front of it. The SKPP photos were taken at high water and show the water at the grass edge there.

**z18, 3x3 tiles over Riverside, plus a 3x crop with a 10 m bar and 50 m rings**
- The shore row sits inside a continuous belt of trees and shrubs. Distances to that edge:
  - R28: about 15 m.
  - R29: about 19 m.
  - R31-R33: about 25 m.
  - R36-R41: about 30-45 m.

**z18 over Bison Hollow, plus a 1.5x crop with rings**
- The south-west row (BH21-BH24) is about 30-50 m from the inner edge of the sand band.
- Between them are the loop's perimeter track and a strip of shrubs and trees.

**z18 over Bearpaw A by B80, with rings**
- B80 is about 50 m inside dense woods from the treeline.

**z17 over Bearpaw and over Sagebrush, and z16 over the whole north shore**
- Bearpaw is under continuous canopy.
- Sagebrush's south-east sites S30-S34 are about 110-150 m from the high-water edge. Between them are the boundary track and an open grass slope.

## Waterfront calls

**Bearpaw + Sagebrush (9205): lakeview.**
- Photos of S32, S33 and S34 (site ids 6439-6441) show the lake through trees. The ids are in sequence; S30 = 6437 was confirmed by its detail page.
- The Bearpaw photos show only woods.

**Riverside + Nighthawk: lakeview.** This matches p3-526.

**Bison Hollow: lakeview.**
- Photos of BH19 and BH20 show the lake in the distance past trees.
- BH21 shows it faintly.

## For AWH

**Riverside R28, and perhaps R29 and R40, is the closest call.**
- In the official site photos:
  - R28 sits on open grass under scattered tall trees, with the lake beyond a tall-grass fringe, about 15 m off.
  - R40 shows open grass to a reed band, with the water beyond.
- The imagery cannot see under the canopy.
- The photos are undated.
- The booking data says "Near Water - no" on every row.
- So the call stayed down. If AWH accepts the photos as clear open ground, Riverside could be lakefront with a caveat naming R28 (and R29).

**Leads, not investigated or added**
- The Nighthawk/Riverside map marks "Cactus Blume Private Campground" between the loops.
- The same map has a "To Glamping Resorts" arrow on Hwy 261.

**Showers, laundry and groceries**
- They are drawn only on the Bearpaw page.
- The Riverside/Nighthawk and Bison Hollow pages show an accessible service centre and washrooms, but no shower symbol.
- So the new entries omit showers and flush_toilets (left unknown) rather than claim them.
