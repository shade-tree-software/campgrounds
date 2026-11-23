# 5729 Palisades State Park: split Queen Campground from King Campground (2026-11-22)

## Decision
SPLIT. Queen Campground becomes its own entry (`new_palisades_queen.json`, one entry). The id stays on King
Campground: the stored pin (43.6827,-96.525) was already in King, 31 m from its RV-site centroid, and King is the
larger campground. `parent_5729.json` re-cuts the kept entry and moves the pin to that centroid.

`trips.campground_references(5729)` returned `[]`, so no trip references the entry.

**facID:** 44 is right for both campgrounds. `kit/sd/gfp_facids.txt` maps 44 to 'Palisades State Park' and 57 to
'Sandy Shore Recreation Area'. The engine page for facID=44 reads facilityName 'Palisades State Park'. The stored
website and booking.url already carried facID=44 (the p3-568 fix was applied). No entry still links facID=57 for
Palisades; 5758 Sandy Shore rightly keeps 57. No wrong link remains.

## Why it passes the split rule
- **Distance (measured):** haversine over the engine's per-unit coordinates, using web-bookable RV sites only
  (no hosts, tents or cabins).
  - King (loop 201): 70 sites, centroid 43.68243,-96.52512 (10 m from 18E).
  - Queen (loop 125): 22 sites, centroid 43.69014,-96.51400 (19 m from 85E).
  - Centroid to centroid: **1,238 m**. Nearest RV sites across the two (2E and 108E-ADA): **964 m**. Nearest
    units of any kind (cabin C4 and tent site 78): 658 m.
  - The verifier's hint for Queen (43.6904,-96.5147) is 85 m from the RV centroid.
- **Separate places, each with its own road:**
  - King's loops hang off the entrance road from the new entrance at 48422 256th St, at the south of the park.
  - That road runs north about 1 km to the day-use area by the creek. There it meets the old east road (255th St
    line) from 485th Ave.
  - Queen's own road leaves the day-use area and runs north about 650 m along the creek past cabins C5-C7 to the
    Queen loop. Read off imagery, not measured on a route.
  - Correction to the hint: Queen is not on its own road off 485th Ave. Its road starts at the day-use junction,
    where the old 485th Ave road also comes in. GFP now says "Please be sure to use the entrance at 48422 256th
    Street". Whether the old east road is still open to the public is not stated.
  - The day-use area, an inholding of farm buildings and fields lie between the two.
  - GFP: "Park Size: 2 campgrounds"; separate King and Queen campground maps; separate engine loops.
  - Same pattern as the Angostura split (5714): each campground on its own loop or spur off a shared park road, more
    than 1 km apart.

## Sources (all read 2026-11-22, plain curl, UA Mozilla/5.0, no bot walls)
- **GFP park page**, https://gfp.sd.gov/parks/detail/palisades-state-park/:
  - Rates: electrical $30, non-electrical $16 (tent only), cabins $60.
  - "Open: Year-round. Between Oct. 1 and April 30, showers, flush toilets and other water systems may be closed
    ... Vault toilets usually remain open."
  - "2 campgrounds, 111 campsites, 10 camping cabins and a group lodge".
  - The new-entrance notice; the 2024 expansion text (77 new campsites, new dump station, 4 cabins).
  - Phone 605.773.6245; reservations 1.800.710.2267; amenities list; "Bolting is not allowed".
- **GFP maps**, each rendered and read:
  - Overview https://gfp.sd.gov/userdocs/palisades_overview.pdf (2025-01-16).
  - King https://gfp.sd.gov/userdocs/palisades_king_cg.pdf (2024-07-12): sites 1-77, cabins 1-4, restroom/shower by
    57E, dump station on the entrance road.
  - Queen https://gfp.sd.gov/userdocs/palisades_queen_cg.pdf (2024-05-24): sites 78-111, cabins 5-10,
    restroom/shower by 85E, no dump station.
- **Go Outdoors SD engine**, https://reservations.gooutdoorssouthdakota.com/FacilityDetails.aspx?facID=44. Parsed
  `var sitesHashMap`.
  - **Loop 201 (King):**
    - 2E-71E: all back-ins, Amp Service "20,30, 50", $30.
    - MaxEquipLength 80 on all but 34E (30). Not written as max_rig_ft: the uniform 80 reads as a default, and p3-568
      judged the same. The stored 84 was Queen's.
    - Also: tent sites 72-77 ($16, MaxEquipLength 60 on tent sites, which is nonsense), cabins C1-C4, and host V1
      (not online).
  - **Loop 125 (Queen):**
    - Back-ins 85E-89E, 92E, 93E, 95E, 103E-111E: lengths 62-84.
    - Pull-offs 98E-102E: 25 ft.
    - Amp Service 50 (85E: 20,30,50), $30.
    - Also: 12 tent sites ($16), cabins C5-C10, and host V2 (not online).
  - **Loop 192:** the lodge, pad L1, the group camps and shelters. None of them is an RV campground.
  - No blackout ranges on any unit.
- **Open-Meteo elevation:** King centroid 434 m, Queen centroid 443 m, old pin 436 m. The 90 m DEM is too coarse to
  resolve the creek valley.

## Imagery
Every frame rendered. Files deleted after use.
- **Esri World_Imagery** via `audit/verify/kit/mn/tools/satpts.py` with the unit points plotted. Source per the
  metadata service: Minnehaha County orthos, 2023-04-01.
  - **1,100 m half-width:** the whole park, both campgrounds and the road network.
  - **500 m half-width:** the entrance road from King north to the day-use junction, the old east road to 485th Ave,
    and Queen's road north from the junction.
  - **380 m half-width (0.84 m/px):** the Queen loop.
  - **130 m half-width (0.29 m/px):** Queen's north end and the creek.
    - 93E is about 60 m from the bank and 95E about 75 m, with the loop road, tent site 94 and bank trees between.
    - The creek is about 20-32 m wide there.
  - **170 m half-width (0.38 m/px):** King's west row.
    - The pads of 32E-36E end about 110-120 m from Split Rock Creek, across open prairie. A narrow side slough lies
      about 55 m out.
    - The creek measured 29-40 m wide (a pixel run along 6 rows) in this April frame, during the 2023 snowmelt.
- **Esri Wayback** release 2023-08-10 (tile 17632, z18, 0.43 m/px; the metadata says Minnehaha 2020, but the frame
  is green-season with King's pads in place). Read at King's west row:
  - The creek bed is about 24-28 m wide, mostly riffle.
  - The pads are about 119 m from the bed's east edge.

## Waterfront calls
- **King: not waterfront** (stored value kept; evidence re-measured, because the old line measured from
  43.6760,-96.5265, south of the loops). No site is near the water. Split Rock Creek reads as a creek (under or
  about 30 m at normal flow), which has no view value.
- **Queen: not waterfront.** The nearest RV sites (93E, 95E) are 60-75 m back behind the loop road, a tent site and
  bank trees. The sites nearer the water are tents and cabins.

## Groups
- **Kept entry (King):**
  - sites: 70, pull_through false, no max_rig_ft (default suspected).
  - hookups: 50.
  - facilities: showers, flush toilets, vault toilets, water and dump all true.
  - season: year_round, now sourced to GFP (it had been derived from the note).
  - booking: unchanged, with provenance.
  - fees and rating: left as stored.
- **Queen:**
  - sites: 22, max 84 (111E). Pull-offs and tent sites in sites.note. pull_through omitted: pull-offs are neither
    back-in nor drive-through.
  - hookups: 50.
  - facilities: no dump key, since the park's station is at King (the Angostura Cascade precedent).
  - season, booking and fees: same as King, with fees sourced (GFP $30 electric = $23 + $7).
  - No rating: RV Life rates the park as a whole.

## For AWH
- Split Rock Creek at King is borderline on the 30 m river rule. It is about 24-28 m in the green-season frame and
  29-40 m in the April 2023 snowmelt frame.
- King's west row (32E-36E) looks across about 115 m of open prairie at it, with no screen.
- If AWH counts the creek as a river there, King would be `riverview`. I kept `not waterfront` under the
  default-down rule.
