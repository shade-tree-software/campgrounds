# 5742 Roy Lake State Park: split the West Unit from the East Unit (2026-11-22)

## Decision
SPLIT. The West Unit becomes its own entry (`new_roy_lake_west.json`, one entry). The id stays on the East Unit:
the stored pin (45.69941,-97.41938) was already inside it, 94 m from its RV-site centroid. `parent_5742.json`
re-cuts the kept entry and moves the pin to that centroid.

`trips.campground_references(5742)` returned `[]`, so no trip references the entry. The id can stay on either
campground; it stays on the one the pin marks.

## Why it passes the split rule
- **Distance (measured):** haversine over the engine's per-unit coordinates, using web-bookable RV sites only
  (no hosts, tents or cabins).
  - East Unit (loop 89): 37 sites, centroid 45.69857,-97.41941.
  - West Unit (loop 90): 49 sites, centroid 45.70625,-97.45430.
  - Centroid to centroid: **2,841 m**. The nearest pair of sites across the two (57E and 51E) is **2,602 m** apart.
  - The verifier's hint (45.70602,-97.45460) was a little off the West centroid. It probably included cabins.
- **Separate places, each with its own road:**
  - The two units sit on opposite shores of Roy Lake's NE arm.
  - The West Unit is on the peninsula at the park's main entrance: the entrance booth, dump station and day-use
    area off 438th Ave / Northside Dr.
  - The East Unit has its own access road running south from the shore road, about 2.3 km from the West entrance
    in a straight line (read off imagery). It has its own swim beach, boat ramp and dump station (GFP overview map).
  - The GFP campground map draws them as "WEST UNIT" and an "EAST UNIT" inset. GFP's park page says "2
    campgrounds".
- Both units are on one engine facility (facID=55) but in separate loops (89 East, 90 West). The rec.gov exception
  is not needed: the distance rule alone is met.

## Sources (all read 2026-11-22, plain curl with UA Mozilla/5.0, no bot walls)
- **GFP park page**, https://gfp.sd.gov/parks/detail/roy-lake-state-park/:
  - Rates: electric $30, non-electric $16, camping cabins $60.
  - "Open: Year-round. Between Oct. 1 and April 30, showers, flush toilets and other water systems may be closed
    ... Vault toilets usually remain open."
  - "2 campgrounds with 101 campsites, 3 camping cabins, 6 modern cabins, and 6 suites"
  - "3 miles southwest of Lake City off SD Hwy 10"; phone 605.910.4521.
  - Amenities list, plus the on-site convenience store.
  - Lodging text: "The nearest campsites are located at West Unit campground."
- **GFP maps:**
  - Campground map https://gfp.sd.gov/userdocs/roy_cg.pdf: ArcGIS Pro, created 2025-11-17, modified 2026-03-31.
    Rendered and read. It shows site numbering, restroom/showers, vault toilets, water, host sites (V1, V2 West;
    V3 East), tent sites and the C-Store.
  - Overview map https://gfp.sd.gov/userdocs/roy_overview.pdf: rendered and read. Both units, the dump stations,
    beaches and ramps.
- **Go Outdoors SD engine**, https://reservations.gooutdoorssouthdakota.com/FacilityDetails.aspx?facID=55. Parsed
  `var sitesHashMap`: 131 units, 118 active.
  - Engine alert: "New campsites have been added to the East Unit. East Unit Campsite Numbers Have Changed."
  - **Loop 89 (East):**
    - 54E-87E and 88-90: all "Back-In Campsite", Amp Service 20/30, $30.
    - MaxEquipLength runs 45-80. 80 ft at 58E, 61E and 68E. 75 ft at 69E, 84E, 87E and 88-90 looks like the engine
      default and was not used.
    - Two units disagree with their own Online Content: 65E (55 vs 67) and 70E (65 vs 35).
    - Also: T6-T9 tent ($16), cabins C1-C2 ($60), and host V3 (20/30/50, not reservable online).
  - **Loop 90 (West):**
    - 1E-52E: 15E and 17E are absent, and 8E is "Tent Only - Electric" at $23, which leaves 49 RV sites.
    - Pull-thrus are 42E, 44E and 46E. Amp Service 20/30/50, $30.
    - MaxEquipLength runs 42-82, with 82 at 44E. Online Content disagrees for 18E (84 vs 50) and 2E (85 vs 70);
      not used.
    - Also: T1-T5 tent ($16), cabins C3/C10/C11, modern cabins C4-C9, suites S12-S17, group shelter PSW, and hosts
      V1 (not online) and V2.
  - No unit carries a closed-season blackout range.
- **Open-Meteo elevation:** West centroid 553 m, East centroid 561 m, old pin 560 m, open lake 545 m.

## Imagery (Esri World_Imagery export via audit/verify/kit/mn/tools/satpts.py, unit points plotted)
Every frame rendered. Files deleted after use.
- **Overview, 2,100 m half-width:** both units on opposite shores of the arm, each with its own road.
- **East Unit:**
  - 500 m frame: the own access road south from the shore road, and the pads at the unit points.
  - 110 m frames:
    - West shore row (56E-65E): pad ends about 30-35 m from the lake, behind a continuous tree belt.
    - South cul-de-sac (66E-70E): about 25-40 m from the lake, behind a continuous tree fringe.
- **West Unit:**
  - 600 m frame: the peninsula loop reached through the day-use area from the entrance booth.
  - 120 m frames (the SE one also enlarged 2x):
    - SE rows: 28E and 29E about 13 m from the lake, 22E about 20 m, 20E about 20-25 m. A continuous tree and shrub
      fringe runs along the whole shore.
    - NW side (3E-9E): about 25 m to a shallow, weedy bay, behind a tree belt and reed fringe.
- Esri returned HTTP 500 for 60 m and 90 m half-widths at 900 px, so 110-120 m was the finest frame.

## Waterfront calls
- **East Unit: lakeview** (unchanged). Shore sites 56E-70E have a filtered view through a continuous tree belt. No
  site has open ground to the water.
- **West Unit: lakeview.** SE sites 20E-29E look at the lake through a continuous fringe 13-25 m deep. Nothing has
  open ground to the water.

## Re-cuts on the kept entry (parent_5742.json)
- **Name:** "Roy Lake State Park (East Unit)".
- **Location:** moved 94 m to the RV-site centroid. **Elevation:** 561 m.
- **Rewritten for the East Unit alone:** waterfront_evidence, inclusion_evidence and note.
- **Hookups:** electric 50 becomes **30**. Every sold East site is 20/30; the 50 A came from the West Unit and host V3.
- **Sites:** 86/82 ft/pull_through true becomes **37/80 ft/pull_through false**. Every East unit is a back-in; the
  pull-thrus are the West Unit's.
- **Facilities:** values unchanged, but now sourced from the East Unit inset of the campground map.
- **Unchanged:** website, phone, rating, season, booking (provenance updated) and fees.

## New entry (new_roy_lake_west.json)
- "Roy Lake State Park (West Unit)", pinned at 45.70625,-97.45430, elevation 553 m, ownership state.
- 49 RV sites, 82 ft max, pull-thrus, 50 A, camp_store true (the C-Store is in the unit).
- Season, booking and fees copied from 5742, since they are the same park-wide GFP schedule and facility.
  - Fees are 23 + $7 electric = the $30 every RV unit prices at.
  - RV Life rating not copied: the listing is park-level and was not looked up for this unit. Absent means unknown.

## For AWH
- The engine sells **V2 online at $37**, but the GFP campground map marks V2 as a host site. It is excluded from the
  West count.
- The rating on 5742 (RV Life 5*/$$) is the park's single listing. It now sits on the East Unit only.
- The engine says the East Unit was renumbered when new sites were added. The stored counts use the current
  numbering (54E-90).
