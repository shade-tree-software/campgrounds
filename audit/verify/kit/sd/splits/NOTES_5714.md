# 5714 Angostura Recreation Area: split into three entries (2026-11-22)

## Decision
SPLIT into three:
- **5714 (kept): Angostura Recreation Area (Cheyenne Campground).** The stored pin (43.3395,-103.4143) was already
  in Cheyenne, 61 m from its RV-site centroid. `parent_5714.json` re-cuts the entry and moves the pin to that
  centroid.
- **New: Angostura Recreation Area (Cascade Campground)**, the first entry in `new_angostura_south.json`.
- **New: Angostura Recreation Area (Hat Creek and Horsehead Campgrounds)**, the second entry. Hat Creek and
  Horsehead are each on their own spur, but they fail the ~1 km bar (720 m apart). They also share the south entrance
  and the day-use area between them, so they stay together.

`trips.campground_references(5714)` returned `[]`. No trip references the entry.

## Measurements
All distances are haversine over the engine's per-unit coordinates. Only web-bookable RV sites count (no hosts,
tents, cabins or shelters).

**RV-site centroids**

| Campground | Engine loop | Sites | Centroid | Elevation (Open-Meteo) |
|---|---|---|---|---|
| Cheyenne | 2 | 16 | 43.33983,-103.41490 | 996 m |
| Cascade | 1 | 63 | 43.31906,-103.41131 | 976 m |
| Hat Creek | 4 | 23 | 43.30146,-103.40016 | 974 m |
| Horsehead | 5 | 51 | 43.29794,-103.39269 | 976 m |
| Hat Creek + Horsehead | 4 + 5 | 74 | 43.29903,-103.39502 | 972 m |

The combined Hat Creek + Horsehead centroid falls 23 m from 127E, so it is on sites and serves as the pin.

**Distances, centroid to centroid (nearest pair of sites in brackets)**

| Pair | Distance |
|---|---|
| Cheyenne to Cascade | **2,328 m** (17E to 26E: 2,045 m) |
| Cascade to Hat Creek | **2,154 m** (48E to 90E: 1,918 m) |
| Cascade to Horsehead | 2,790 m |
| Cascade to Hat Creek + Horsehead | 2,588 m |
| Cheyenne to Hat Creek + Horsehead | 4,813 m |
| Cheyenne to Hat Creek | 4,430 m |
| Cheyenne to Horsehead | 4,992 m |
| Hat Creek to Horsehead | **720 m** (101E to 127E: 424 m), below the ~1 km bar |

**Entrances**

| From | To | Distance |
|---|---|---|
| Cheyenne centroid | GFP North Entrance (43.34587,-103.422) | 883 m |
| Horsehead centroid | GFP South Entrance (43.29235,-103.3817) | 1,085 m |
| Hat Creek centroid | GFP South Entrance | 1,806 m |

**Roads (from the GFP overview map and Esri imagery)**
- The park road runs down the west shore from the north entrance booth on US-385 to the south entrance.
- Each campground sits on its own loop or spur off that road.
- Cascade is on its own loop road, with a swim beach at its north end.
- Hat Creek and Horsehead branch off separately on either side of day-use area #3 (ramp, pier, fish cleaning,
  shelter). The dump station is on the road in from the south entrance.
- One engine facility (facID=3) sells all four, so the rec.gov exception does not apply. Distance alone decides.

## Sources (all read 2026-11-22; plain curl, UA Mozilla/5.0, no bot walls)

**GFP park page**, https://gfp.sd.gov/parks/detail/angostura-recreation-area/:
- Rates: electric $30, non-electric $16, cabins $60.
- Season: "Open: Year-round. Between Oct. 1 and April 30, showers, flush toilets and other water systems may be
  closed ... Vault toilets usually remain open."
- Size: "4 campgrounds with 171 campsites and 14 camping cabins".
- Phone 605.773.2886.
- The amenities list.
- North and South Entrance GPS points.

**GFP maps.** Both are ArcGIS Pro, created and modified 2023-05-23, and both were rendered and read.
- https://gfp.sd.gov/userdocs/angostura_campgrounds.pdf: site numbering, host sites (V1-V3, V4/V5, V6, V7) and
  restroom/shower, vault toilet, water and dump symbols.
- https://gfp.sd.gov/userdocs/angostura_overview.pdf: the park road, the four campgrounds, the day-use areas, and
  the dump stations at Cheyenne and on the south entrance road.

**Go Outdoors SD engine**, https://reservations.gooutdoorssouthdakota.com/FacilityDetails.aspx?facID=3.

Parsed `var sitesHashMap`: 221 units. Every RV site is $30 with 20/30/50 A, and no unit has a blackout range.

The engine shows two alerts:
- "Double up camping is no longer allowed ..."
- "For stays from October 1 to April 30 please contact the park office for comfort station status."

| Loop | Campground | RV sites | Max length | Other units |
|---|---|---|---|---|
| 2 | Cheyenne | 1E-14E, 17E, 18E, all back-in | 35-65 ft. 3E's 75 is the engine default, not used | Tent-only 15, 16, 19-22 ($16); cabins C5, C6, C9, C14; hosts V1-V3 ($37, "Campground Host") |
| 1 | Cascade | 26E-89E (no 57E) | Back-ins 36-70 ft. 58E/61E show 75, not used. Pull-thru 71E is 140 ft | Cabins C1, C2, C10, C15; hosts V4/V5 |
| 4 | Hat Creek | 90E-112E, all back-in | 32-68 ft | Cabins C3, C4, C11-C13; host V6 |
| 5 | Horsehead | 113E-163E, all back-in | 45-74 ft. 144E's 75 not used | Cabins C7, C8; hosts V7/V8 (130-ft pull-thrus) |

Loop 3 holds group shelters PSH1-4. Loop 6 (301-330) and 142 are inactive.

**Reservoir level (Reclamation)**
- Top of conservation pool: 3,187.2 ft (971.5 m). Reclamation's 2004 sedimentation survey says "at conservation pool
  elevation 3,187.2, the surface area was 4,612 acres".
- Current conditions: 48% of capacity in July 2026. Search-result text from usbr.gov/gp/hydromet.

## Imagery
Esri World_Imagery export, served 2026-11-22; the vintage is unpublished and it is a drawdown year. Unit points
were plotted on every frame, and all frames rendered.

| Frame | Half-width | Coverage |
|---|---|---|
| ov | 2,900 m | Whole west shore |
| south | 650 m | Hat Creek and Horsehead |
| chey_w | 480 m | Cheyenne |
| chey | 200 m | Cheyenne |
| chey_17 | 130 m | Cheyenne 17E/18E |
| casc | 330 m | Cascade |
| casc_w | 130 m | Cascade west row |
| hat | 130 m | Hat Creek |
| hh_w | 130 m | Horsehead west |
| hh_s | 150 m | Horsehead south |

**Engine site photos.** These are undated and taken at a high pool. All rendered.
- Cheyenne: 17E, 18E.
- Cascade: 27E, 29E, 31E, 33E, 35E, 38E, 40E, 42E, 44E, 71E.
- Hat Creek: 94E, 96E, 98E, 99E, 100E, 101E.
- Horsehead: 125E, 126E, 127E, 128E, 137E, 139E, 142E, 144E, 146E.

## Waterfront calls
**Cheyenne: lakeview -> not waterfront (DOWN).**
- The main loop is in pines more than 300 m from the water.
- 17E is ~93 m from the cove through pine clumps.
- The 17E and 18E photos show no water.
- Only tent-only 15 and 16 are by the water.

**Cascade: lakeview.**
- The west row 26E-44E sits in a continuous shore tree belt.
- Today ~120-140 m of sand flat separates it from the water.
- The high-pool photos show the lake through the trees. At 29E and 31E the water is at the tree line ~30-40 m off.

**Hat Creek + Horsehead: lakeview.**
- Hat Creek: 98E, 100E and 101E are ~10-25 m from the grass/sand line and ~75-90 m from today's water over open
  sand.
- The high-pool photos show water directly behind 96E, 98E, 100E and 101E across open grass.
- Horsehead: 127E is ~70 m and 142E ~75 m from today's water through a tree belt. The photos show only glimpses
  (128E, 142E, 144E).
- Held down under the drawdown lessons (p3-551: full-pool distance alone doesn't make lakefront; p3-572: measure to
  the water). This matches the p3-564 verifier's call.

**Lakefront lead for AWH:** Hat Creek 96E, 98E, 100E and 101E would meet the open-ground ~50 m test if Angostura is
read at full pool.

## For AWH
- Cheyenne goes down from lakeview to not waterfront.
- Hat Creek 96E/98E/100E/101E are a full-pool lakefront lead (see above).
- The RV Life `rating` (4.5) is a park-level listing. It is left on 5714 and not copied to the new entries.
- GFP's maps are dated 2023-05-23.
- Cascade has no dump station of its own, so `dump` is absent on it. The park's dump stations are at Cheyenne and on
  the south entrance road.
