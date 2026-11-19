# Split 9161 - Blackstrap Provincial Park (SK) - 2026-11-19

## Decision: SPLIT

Hazelnut Grove (sites 100-118) is a separate place. It sits about 5 km north on its own lakeshore spur by the Highway 211 park entrance, while Kevin Misfeldt and Sunset Ridge share their own road at the south end of the lake. It also runs the park's winter camping. Kevin Misfeldt and Sunset Ridge are 0.44 km apart on one road, so they stay together under id 9161, which is the larger part (125 sites).

- `parent_9161.json`: 9161 is renamed "Blackstrap Provincial Park - Kevin Misfeldt and Sunset Ridge Campgrounds" and re-pinned 51.7460,-106.4615 (on site 200; Open-Meteo 538 m). The old pin, 51.7462,-106.4593, sat on a track in the grass gap between the loops. Sites become 125 (max 50). Hookups are unchanged (50 A, water and sewer on Sunset Ridge FS 317-326 and KM 264A). The season now closes 10-31 and loses the winter camping. Fees and facilities are left unchanged.
- `new_blackstrap_hazelnut_grove.json`: "Blackstrap Provincial Park - Hazelnut Grove Campground", 51.7872,-106.4234 (the GIS centroid of the 19 sites; Open-Meteo 535 m, the same as the lake surface DEM). It has 19 sites, 15/30 A, max_rig_ft 35, season 05-14 to 03-14. Fees are $35 CAD plus the carried reservation fee of 12 and the entrance fee {11,11,vehicle_day}.

## Measurements (haversine, SKPP GIS site points)

| | lat,lng | points |
|---|---|---|
| Hazelnut Grove centroid | 51.78715,-106.42338 | all 19 |
| Kevin Misfeldt centroid | 51.74574,-106.46267 | 12 sampled (200, 204, 205, 226, 227, 229, 241, 254-257, 261) |
| Sunset Ridge centroid | 51.74707,-106.45663 | 8 sampled (301, 307, 313, 317, 329A, 343, 352, 362) |

- Hazelnut to Kevin Misfeldt: **5.34 km**. Hazelnut to Sunset Ridge: **5.01 km**. The nearest sampled pair (117 to 301) is **4.79 km**. The verifier's hint of ~4.6 km was a little short.
- Kevin Misfeldt to Sunset Ridge: 0.44 km, one road.
- Old pin to the KM and SR centroids: 237 m and 207 m. Old pin to Hazelnut: 5.18 km.

## Site data (parks.saskatchewan.ca SKPP parkId 290310, read 2026-11-19)

- **Paging table, all 147 rows; every row reads "Near Water - no".**
  - Hazelnut Grove: 19 Nightly Electric, 100-118.
  - Kevin Misfeldt: 31 NE, 30 NNE (221-224 are walk-ins with no length), 1 Accessible FS (264A), and 2 Camp-Easy yurts (217-218).
  - Sunset Ridge: 45 NE, 1 Accessible NE (329A), 10 FS (317-326, 15/30/50), and 7 Seasonal Electric (305-310, 314).
  - The pavilion is listed separately.
  - The total of 144 (19 + 62 + 63) matches the stored count.
- **Detail pages:** all 19 Hazelnut sites, plus 20 sampled main sites. siteIds 6833 and 6838 return "Page Not Found"; they are gaps, not sites.
  - Hazelnut "Maximum Equipment Length (ft)": 40 on 103, 111 and 112; 35 on 100, 101 and 104-108; 25 on the rest.
  - Hazelnut "Allowed Equipment": up to the 19-25 ft class on 17 sites. Only site 100 adds 26-32 and 33-40. Sites 102 and 106 take "Single Tent, Van/Truck Camper" only.
  - Hazelnut area notes: "Sites are small and better suited for small campers under 25 feet." and "In hot weather, algae bloom tends to occur on lake, sometimes creating a strong odor in campground, particularly lakefront sites."
- **Park page:**
  - Winter Camping text: Nov 1, 2026 - Mar 14, 2027, "pit toilets (available in the Hazelnut campground)"; water, showers and dump unavailable.
  - Rate table "General Season Nov 19 2026 - Nov 19 2027": Nightly Electric $31.00, FS $45.00, NE $16.00. These are the reduced-services rates; the summer electric rate is $35 (rate card jsonl 2026-10-12).
- **Tourism SK listings.csv:**
  - Fall: "Contact the park ... to book a campsite in October" (no loop named).
  - Winter: "Winter camping available in Hazelnut campground ...".
  - parks.csv phone: 1-306-492-5676.
- **Park map PDF (blackstrap-all.pdf, Campgrounds page 2026-04-10):**
  - The Hazelnut inset shows sites 100-119, two potable water symbols, a washroom, garbage, wood and parking. It shows no sani dump or shower building.
  - The core page shows Hazelnut by the park entrance; KM and SR are at the south end on their own road.

## Waterfront

The water here is Blackstrap Lake, a reservoir. On the reservoir the vegetated edge is the high-water line.

- **Hazelnut: lakeview.**
  - The lake-side row is 100-101, 103-105, 108-110, 112 and 114-117. These sites are about 10-25 m from the open water, behind a continuous band of willow, shrubs and trees.
  - Pixel profiles put the vegetation-to-water edge about 12-22 m from sites 109, 110 and 117.
  - Site photos show the lake through or over shrubs from 100, 101, 103, 104, 108, 109, 116 and 117.
  - No site is on open ground to the water. The operator's "lakefront sites" wording was re-audited and does not change the call.
- **Main: lakeview.**
  - KM open-grass sites 254-257 are 42-51 m from the water (flood-fill mask plus profiles), across about 10 m of mown grass and then a continuous shoreline shrub band.
  - Photos show the lake over the shrubs from 253-256 and 259-261, and through trees from 251. No lake is visible from 204-206, 227-229, 239, 250, 252 or 257.
  - 204 and 205 are in trees, about 35 m+ from the water.
  - Sunset Ridge is up the hill, 300 m+ from the shore, and inland.

## Imagery frames read (all rendered)

- Esri World_Imagery:
  - hz17 (z17)
  - hz18 (z18, 0.369 m/px) and its water mask
  - hz18x2 (2x crop of z18)
  - main16 (z16)
  - main17 (z17, 0.739 m/px, main GIS points + old pin)
  - km18 (z18, 0.37 m/px, KM points) and its water mask
- z19 returned "Map data not yet available" tiles and was discarded.
- SKPP site photo contact sheets: sh1-sh4 (Hazelnut, every site) and km1-km4 (KM 204-206, 227-229, 239, 250-261).
- Park map PDF pages rendered to PNG: the core area, the Hazelnut inset and the legend.

## For AWH

- **Hazelnut site sizes:** online booking caps 17 of the 19 Hazelnut sites at a 25-ft unit, despite posted maximums of 35-40. A 23-ft rig fits. Only site 100 books larger (max_rig_ft 35).
- **Hazelnut waterfront:** the operator calls some Hazelnut sites "lakefront". On imagery the lake-side row is only 10-25 m from the water, but behind a continuous shrub band. I called it **lakeview** under the default-down rule.
- **October camping:** the listing does not name the loop. I followed the hint and closed the main entry at 10-31; Hazelnut's 05-14 to 03-14 season spans October either way.
- **Site 119:** the park map shows it in Hazelnut, but it is not on the booking site.
- **Old note:** it said the main loops were on the "southeast shore" and Hazelnut "about 4.5 km". Both are replaced: the main loops are at the south end of the lake, and the measured distance is about 5 km.
